"""Small verified data views for the guided notebook experience."""
from __future__ import annotations

import hashlib
import json
import base64
import gzip
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

from scripts.notebook_data import (
    DATA,
    ROOT,
    analysis_config,
    build_fit_nomination_data,
    ensure_sources,
    prepare,
    shortlist,
    training_seeds,
)

EXPERIENCE_CONFIG = ROOT / "config" / "notebook_experience.json"
VISUAL_SCHEMA_VERSION = "before-you-make-it-visual-v3"

ENDPOINT_DEFINITIONS = [
    {"key": "LogD", "label": "LogD", "short_label": "LogD", "unit": "dimensionless"},
    {"key": "KSOL", "label": "Kinetic solubility", "short_label": "KSOL", "unit": "µM"},
    {"key": "HLM CLint", "label": "Human liver microsomal CLint", "short_label": "HLM", "unit": "mL/min/kg"},
    {"key": "MLM CLint", "label": "Mouse liver microsomal CLint", "short_label": "MLM", "unit": "mL/min/kg"},
    {"key": "Caco-2 Permeability Papp A>B", "label": "Caco-2 Papp A>B", "short_label": "Papp", "unit": "10^-6 cm/s"},
    {"key": "Caco-2 Permeability Efflux", "label": "Caco-2 efflux ratio", "short_label": "Efflux", "unit": "ratio"},
    {"key": "MPPB", "label": "Mouse plasma protein binding", "short_label": "MPPB", "unit": "% unbound"},
    {"key": "MBPB", "label": "Mouse brain protein binding", "short_label": "MBPB", "unit": "% unbound"},
    {"key": "MGMB", "label": "Mouse muscle binding", "short_label": "MGMB", "unit": "% unbound"},
]


def experience_config() -> dict[str, object]:
    return json.loads(EXPERIENCE_CONFIG.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pinned_generation() -> tuple[pd.DataFrame, dict[str, object], list[dict[str, object]]]:
    """Load only the explicit approved run and validate raw/candidate links."""
    config = experience_config()
    run = ROOT / "outputs" / "chemllama" / str(config["generation_run_id"])
    manifest = json.loads((run / "manifest.json").read_text())
    candidates = pd.read_json(run / "candidates.json")
    raw = [json.loads(line) for line in (run / "raw_generation.jsonl").read_text().splitlines()]
    if manifest["generation_run_id"] != config["generation_run_id"]:
        raise ValueError("Pinned generation run ID mismatch")
    if sha256(run / "candidates.json") != config["generation_candidate_sha256"]:
        raise ValueError("Pinned generation candidate hash mismatch")
    if sha256(run / "raw_generation.jsonl") != manifest["raw_sha256"]:
        raise ValueError("Pinned generation raw-log hash mismatch")
    if sha256(run / "candidates.json") != manifest["candidate_sha256"]:
        raise ValueError("Pinned generation manifest candidate hash mismatch")
    if len(raw) != manifest["counts"]["raw"] or len(candidates) != manifest["counts"]["valid_unique"]:
        raise ValueError("Pinned generation accounting mismatch")
    raw_by_index = {row["raw_sample_index"]: row for row in raw}
    seeds = {seed["seed_id"] for seed in training_seeds()}
    for candidate in candidates.to_dict("records"):
        record = raw_by_index.get(candidate["raw_sample_index"])
        if record is None or record["validation_status"] != "valid_unique":
            raise ValueError("Candidate lacks a valid raw-record link")
        if candidate["seed_id"] not in seeds or record["seed_id"] != candidate["seed_id"]:
            raise ValueError("Candidate seed provenance mismatch")
        if pd.notna(candidate["measured_LogD"]) or pd.notna(candidate["measured_KSOL_uM"]):
            raise ValueError("Proposal carries invented experimental evidence")
    candidates["SMILES"] = candidates["smiles"]
    return candidates, manifest, training_seeds()


def evidence_accounting() -> dict[str, object]:
    config = experience_config()
    columns = list(config["endpoint_columns"])
    all_records = pd.concat(
        [pd.read_csv(DATA / "expansion_data_train.csv"), pd.read_csv(DATA / "expansion_data_test.csv")],
        ignore_index=True,
    )
    numeric = all_records[columns].notna()
    return {
        "endpoint_columns": columns,
        "records": len(all_records),
        "possible_cells": int(numeric.size),
        "recorded_values": int(numeric.to_numpy().sum()),
        "missing_or_non_numeric": int((~numeric).to_numpy().sum()),
        "per_endpoint": {column: int(numeric[column].sum()) for column in columns},
    }


def scale_landmarks() -> list[dict[str, object]]:
    config = experience_config()
    total = int(config["gdb17_molecule_count"])
    seconds = total / int(config["hypothetical_inspection_rate_per_second"])
    return [
        {"count": 1, "label": "one schematic possibility", "marks": 1},
        {"count": 1_000, "label": "a thousand possibilities", "marks": 10},
        {"count": 1_000_000, "label": "a million possibilities", "marks": 30},
        {"count": 1_000_000_000, "label": "a billion possibilities", "marks": 60},
        {"count": total, "label": "GDB-17: about 166 billion", "marks": 100,
         "hypothetical_years_at_one_per_second": seconds / (365.25 * 24 * 3600)},
    ]


def active_budget_reference(cohort: pd.DataFrame, count: int, random_seed: int = 20260918, draws: int = 2000) -> dict[str, float | int]:
    """Same-cohort equal-budget pass-count distribution for the active shortlist."""
    selected = shortlist(cohort, count)
    eligible_pass = cohort.measured_threshold_pass.to_numpy(dtype=bool)
    rng = np.random.default_rng(random_seed)
    samples = np.array([rng.choice(eligible_pass, size=count, replace=False).sum() for _ in range(draws)])
    return {
        "selected_passes": int(selected.measured_threshold_pass.sum()),
        "selected_count": count,
        "cohort_passes": int(eligible_pass.sum()),
        "cohort_count": int(len(eligible_pass)),
        "random_expected_passes": float(count * eligible_pass.sum() / len(eligible_pass)),
        "random_simulation_mean_passes": float(samples.mean()),
        "random_low_95": float(np.quantile(samples, 0.025)),
        "random_high_95": float(np.quantile(samples, 0.975)),
    }


def _json_records(frame: pd.DataFrame) -> list[dict[str, object]]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def _structure_svg(smiles: str, width: int = 300, height: int = 190) -> str:
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError(f"Cannot depict invalid SMILES: {smiles}")
    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    drawer.drawOptions().clearBackground = False
    drawer.drawOptions().addStereoAnnotation = True
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, molecule)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText().replace("svg:", "")
    return svg.replace("<?xml version='1.0' encoding='iso-8859-1'?>", "").strip()


def _endpoint_evidence(
    split_row: pd.Series,
    raw_row: pd.Series | None,
    definition: dict[str, str],
) -> dict[str, object]:
    key = definition["key"]
    value = split_row.get(key)
    if pd.notna(value):
        return {**definition, "status": "measured", "value": float(value), "bound": None}
    raw_value = None if raw_row is None else raw_row.get(key)
    if pd.notna(raw_value):
        text = str(raw_value).strip()
        if text.startswith(("<", ">")):
            return {**definition, "status": "bounded", "value": None, "bound": text}
    return {**definition, "status": "missing", "value": None, "bound": None}


def build_molecule_evidence_records(
    cohort: pd.DataFrame,
    nomination_data: dict[str, object],
    candidates: pd.DataFrame,
    seeds: list[dict[str, object]],
) -> dict[str, object]:
    """Join identity, provenance, evidence states, and verified depictions."""
    train = pd.read_csv(DATA / "expansion_data_train.csv").rename(
        columns={"Molecule Name": "molecule_id"}
    )
    test = pd.read_csv(DATA / "expansion_data_test.csv").rename(
        columns={"Molecule Name": "molecule_id"}
    )
    raw = pd.read_csv(DATA / "expansion_data_raw.csv", dtype=str).rename(
        columns={"Molecule Name": "molecule_id"}
    )
    raw_by_id = raw.set_index("molecule_id", drop=False)
    cohort_by_id = cohort.set_index("molecule_id", drop=False)
    union_ids = list(nomination_data["union_order"])
    if not set(union_ids).issubset(cohort_by_id.index):
        raise ValueError("Nomination union contains IDs outside the paired cohort")
    nearest_ids = set(cohort_by_id.loc[union_ids].nearest_training_id.astype(str))
    seed_ids = {str(seed["seed_id"]) for seed in seeds}
    training_ids = nearest_ids | seed_ids
    train_by_id = train.set_index("molecule_id", drop=False)
    if not training_ids.issubset(train_by_id.index):
        raise ValueError("A required training context ID is absent")

    records: dict[str, dict[str, object]] = {}
    depictions: dict[str, str] = {}
    for molecule_id in union_ids:
        cohort_row = cohort_by_id.loc[molecule_id]
        split_row = test.loc[test.molecule_id == molecule_id].iloc[0]
        raw_row = raw_by_id.loc[molecule_id] if molecule_id in raw_by_id.index else None
        records[molecule_id] = {
            "molecule_id": molecule_id,
            "role": "held_out_retrospective",
            "smiles": str(cohort_row.SMILES),
            "canonical_isomeric_smiles": str(cohort_row.canonical_isomeric_smiles),
            "cluster": int(cohort_row.cluster),
            "nearest_training_id": str(cohort_row.nearest_training_id),
            "nearest_training_similarity": float(cohort_row.nearest_training_similarity),
            "ensemble_prediction": {
                "LogD": float(cohort_row.pred_LogD),
                "LogS": float(cohort_row.pred_LogS),
                "KSOL_uM": float(cohort_row.pred_KSOL_uM),
                "score": float(cohort_row.pred_score),
            },
            "measurement_summary": {
                "LogD": float(cohort_row.obs_LogD),
                "KSOL_uM": float(cohort_row.obs_KSOL_uM),
                "score": float(cohort_row.obs_score),
                "target_pass": bool(cohort_row.measured_threshold_pass),
            },
            "endpoints": [
                _endpoint_evidence(split_row, raw_row, definition)
                for definition in ENDPOINT_DEFINITIONS
            ],
            "source": "ExpansionRx released test split",
        }
        depictions[molecule_id] = _structure_svg(str(cohort_row.SMILES))

    for molecule_id in sorted(training_ids):
        split_row = train_by_id.loc[molecule_id]
        raw_row = raw_by_id.loc[molecule_id] if molecule_id in raw_by_id.index else None
        records[molecule_id] = {
            "molecule_id": molecule_id,
            "role": "training_seed" if molecule_id in seed_ids else "nearest_training_context",
            "smiles": str(split_row.SMILES),
            "canonical_isomeric_smiles": Chem.MolToSmiles(
                Chem.MolFromSmiles(str(split_row.SMILES)), isomericSmiles=True
            ),
            "cluster": None,
            "nearest_training_id": None,
            "nearest_training_similarity": None,
            "ensemble_prediction": None,
            "measurement_summary": None,
            "endpoints": [
                _endpoint_evidence(split_row, raw_row, definition)
                for definition in ENDPOINT_DEFINITIONS
            ],
            "source": "ExpansionRx released training split",
        }
        depictions[molecule_id] = _structure_svg(str(split_row.SMILES))

    official_canonical_to_id: dict[str, str] = {}
    for row in pd.concat([train, test], ignore_index=True).itertuples(index=False):
        molecule = Chem.MolFromSmiles(str(row.SMILES))
        official_canonical_to_id[
            Chem.MolToSmiles(molecule, isomericSmiles=True)
        ] = str(row.molecule_id)
    for candidate in candidates.to_dict("records"):
        candidate_id = str(candidate["candidate_id"])
        canonical = str(candidate["canonical_isomeric_smiles"])
        rediscovery_id = official_canonical_to_id.get(canonical)
        records[candidate_id] = {
            "molecule_id": candidate_id,
            "role": "generated_proposal",
            "seed_id": str(candidate["seed_id"]),
            "smiles": str(candidate["smiles"]),
            "canonical_isomeric_smiles": canonical,
            "cluster": None,
            "nearest_training_id": str(candidate["nearest_training_id"]),
            "nearest_training_similarity": float(candidate["nearest_training_similarity"]),
            "ensemble_prediction": None,
            "measurement_summary": None,
            "computed_descriptors": candidate["computed_descriptors"],
            "endpoints": [
                {**definition, "status": "missing", "value": None, "bound": None}
                for definition in ENDPOINT_DEFINITIONS
            ],
            "rediscovery_id": rediscovery_id,
            "source": "Cached ChemLlama seed-prompt output; experiments unknown",
        }
        depictions[candidate_id] = _structure_svg(str(candidate["smiles"]))

    if len(records) != len(set(records)) or set(depictions) != set(records):
        raise ValueError("Evidence-record identity map is inconsistent")
    return {"records": records, "depictions": depictions}


def _canonical_json_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _compress_depictions(depictions: dict[str, str]) -> dict[str, object]:
    return {
        "encoding": "gzip+base64",
        "items": {
            molecule_id: base64.b64encode(
                gzip.compress(svg.encode("utf-8"), compresslevel=9, mtime=0)
            ).decode("ascii")
            for molecule_id, svg in depictions.items()
        },
    }


def build_visual_payload(force: bool = False) -> dict[str, object]:
    """Assemble the versioned native/portable payload from one tested path."""
    cohort, _, preparation_manifest = prepare(force=force)
    candidates, generation_manifest, seeds = load_pinned_generation()
    nominations = build_fit_nomination_data(cohort, force=force)
    evidence = build_molecule_evidence_records(cohort, nominations, candidates, seeds)
    ensemble = shortlist(cohort, 50)
    reference = active_budget_reference(cohort, 50)
    fit_passes = {}
    cohort_by_id = cohort.set_index("molecule_id")
    for fit_key, ids in nominations["nominations"].items():
        fit_passes[fit_key] = int(
            cohort_by_id.loc[list(ids)].measured_threshold_pass.sum()
        )
    selected_caco = ensemble.dropna(
        subset=["Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux"]
    )
    candidate_records = candidates[
        [
            "candidate_id",
            "seed_id",
            "similarity_to_seed",
            "nearest_training_id",
            "nearest_training_similarity",
            "raw_sample_index",
        ]
    ].copy()
    payload: dict[str, object] = {
        "schema_version": VISUAL_SCHEMA_VERSION,
        "scale_landmarks": scale_landmarks(),
        "assay_accounting": evidence_accounting(),
        "endpoint_definitions": ENDPOINT_DEFINITIONS,
        "targets": {
            "logd_low": preparation_manifest["constants"]["logd_low"],
            "logd_high": preparation_manifest["constants"]["logd_high"],
            "ksol_min_um": preparation_manifest["constants"]["ksol_median_um"],
        },
        "seeds": seeds,
        "candidates": _json_records(candidate_records),
        "generation": {
            "run_id": generation_manifest["generation_run_id"],
            "counts": generation_manifest["counts"],
            "checkpoint_id": generation_manifest["config"]["checkpoint_id"],
            "checkpoint_revision": generation_manifest["config"]["checkpoint_revision"],
            "prompt_semantics": generation_manifest["config"]["prompt_semantics"],
            "candidate_sha256": generation_manifest["candidate_sha256"],
            "raw_sha256": generation_manifest["raw_sha256"],
        },
        "nominations": nominations,
        "evidence_records": evidence["records"],
        "depictions": _compress_depictions(evidence["depictions"]),
        "retrospective": {
            "ensemble_target_passes": int(ensemble.measured_threshold_pass.sum()),
            "random_reference": reference,
            "fit_target_passes": fit_passes,
            "fit_target_passes_summary": {
                "minimum": min(fit_passes.values()),
                "median": float(np.median(list(fit_passes.values()))),
                "maximum": max(fit_passes.values()),
            },
            "caco_paired": int(len(selected_caco)),
            "caco_paired_among_target_passes": int(
                selected_caco.measured_threshold_pass.sum()
            ),
            "example_rules": {
                "unanimous": "present in every fit-specific top-fifty list",
                "contrast": "preselected inspectable broader-profile contrast",
                "encouraging": "ensemble records with measured target passes and available broader profiles",
            },
            "unanimous_id": "E-0024329",
            "contrast_id": "E-0023839",
            "encouraging_ids": ["E-0021738", "E-0024328"],
        },
        "provenance": {
            "analysis_schema": analysis_config()["schema_version"],
            "source_hashes": preparation_manifest["identity"]["source_hashes"],
            "generation_candidate_sha256": experience_config()[
                "generation_candidate_sha256"
            ],
            "selection_rule": "predictions only; score descending then molecule ID ascending",
        },
        "widget_assets": {
            "lens_js": (ROOT / "widgets" / "molecule_evidence.js").read_text(),
            "lens_css": (ROOT / "widgets" / "molecule_evidence.css").read_text(),
            "scale_js": (ROOT / "widgets" / "scale_journey.js").read_text(),
            "scale_css": (ROOT / "widgets" / "scale_journey.css").read_text(),
        },
    }
    payload["provenance"]["nominations_sha256"] = _canonical_json_hash(nominations)
    payload["provenance"]["records_sha256"] = _canonical_json_hash(
        evidence["records"]
    )
    # Force a strict JSON traversal here so non-finite values fail before a bundle is written.
    json.dumps(payload, allow_nan=False)
    return payload


def load_visual_payload(path: Path | None = None) -> dict[str, object]:
    """Load a precomputed payload and reject stale or malformed artifacts."""
    bundle_path = path or (DATA / "molab_bundle.json")
    payload = json.loads(
        bundle_path.read_text(),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"Non-finite JSON constant in visual payload: {value}")
        ),
    )
    if payload.get("schema_version") != VISUAL_SCHEMA_VERSION:
        raise ValueError("Visual payload schema mismatch; rebuild the molab bundle")
    if payload.get("provenance", {}).get("source_hashes") != ensure_sources():
        raise ValueError("Visual payload source hashes do not match pinned inputs")
    if (
        payload.get("provenance", {}).get("generation_candidate_sha256")
        != experience_config()["generation_candidate_sha256"]
    ):
        raise ValueError("Visual payload generation hash mismatch")
    if payload["provenance"].get("nominations_sha256") != _canonical_json_hash(
        payload["nominations"]
    ):
        raise ValueError("Visual payload nomination hash mismatch")
    if payload["provenance"].get("records_sha256") != _canonical_json_hash(
        payload["evidence_records"]
    ):
        raise ValueError("Visual payload evidence-record hash mismatch")
    record_ids = set(payload["evidence_records"])
    if set(payload["depictions"]["items"]) != record_ids:
        raise ValueError("Visual payload depiction/record identity mismatch")
    expected_assets = {
        "lens_js": (ROOT / "widgets" / "molecule_evidence.js").read_text(),
        "lens_css": (ROOT / "widgets" / "molecule_evidence.css").read_text(),
        "scale_js": (ROOT / "widgets" / "scale_journey.js").read_text(),
        "scale_css": (ROOT / "widgets" / "scale_journey.css").read_text(),
    }
    if payload.get("widget_assets") != expected_assets:
        raise ValueError("Visual payload widget assets are stale; rebuild the molab bundle")
    return payload
