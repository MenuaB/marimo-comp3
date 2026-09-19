"""Small verified data views for the guided notebook experience."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.notebook_data import DATA, ROOT, shortlist, training_seeds

EXPERIENCE_CONFIG = ROOT / "config" / "notebook_experience.json"


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
        "random_expected_passes": float(samples.mean()),
        "random_low_95": float(np.quantile(samples, 0.025)),
        "random_high_95": float(np.quantile(samples, 0.975)),
    }
