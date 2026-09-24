"""Chemistry, commitment, and portable-analysis regression tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski

from scripts.story_analysis import (
    active_fit_summary,
    caco_shortlist_summary,
    measured_shortlist_summary,
    resolve_committed_ids,
    selected_molecule_context,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload():
    return json.loads((ROOT / "data" / "molab_bundle.json").read_text())


def state_for(payload, kind, index=0, *, revealed=False, caco=False, inspected=None):
    key = payload["nominations"]["fit_keys"][index]
    ids = payload["nominations"]["ensemble_ids"] if kind == "ensemble" else payload["nominations"]["nominations"][key]
    return {
        "active_fit_index": index,
        "active_fit_key": key,
        "inspected_molecule_id": inspected or payload["retrospective"]["unanimous_id"],
        "selection_kind": kind,
        "committed_fit_key": None if kind == "ensemble" else key,
        "committed_ids": list(ids),
        "measurements_revealed": revealed,
        "caco_revealed": caco,
    }


def test_generated_chemistry_audit_excludes_neutral_halides_and_preserves_raw(payload):
    audit = {row["candidate_id"]: row for row in payload["candidate_audit"]}
    c0033 = audit["C-0033"]
    assert c0033["raw_smiles"].endswith(".Cl")
    assert c0033["parsed"] and c0033["sanitized"]
    assert not c0033["presentation_eligible"]
    assert c0033["chemistry_status"] == "parse_valid_multicomponent_unresolved"
    assert any("neutral standalone halogen" in warning for warning in c0033["chemistry_warnings"])
    featured = {candidate["candidate_id"] for candidate in payload["candidates"]}
    assert "C-0033" not in featured
    assert payload["generation"]["default_candidate_id"] in featured
    counts = payload["generation"]["chemistry_audit_counts"]
    assert counts == {"raw_samples": 96, "rdkit_parseable_samples": 27, "single_component_candidates": 23, "unresolved_multicomponent_candidates": 4, "presentation_eligible_candidates": 23, "featured_candidates": 23}


def test_featured_structures_are_single_sanitized_and_descriptor_consistent(payload):
    eligible = [row for row in payload["candidate_audit"] if row["presentation_eligible"]]
    assert len({row["depiction_smiles"] for row in eligible}) == len(eligible)
    for row in eligible:
        assert row["sanitized"] and row["fragment_count"] == 1
        assert row["depiction_smiles"] == row["descriptor_smiles"]
        molecule = Chem.MolFromSmiles(row["descriptor_smiles"])
        descriptors = row["computed_descriptors"]
        assert descriptors["molecular_weight_Da"] == pytest.approx(Descriptors.MolWt(molecule), abs=1e-4)
        assert descriptors["rdkit_clogp"] == pytest.approx(Crippen.MolLogP(molecule), abs=1e-4)
        assert descriptors["tpsa_A2"] == pytest.approx(Descriptors.TPSA(molecule), abs=1e-4)
        assert descriptors["hbd"] == Lipinski.NumHDonors(molecule)
        assert descriptors["hba"] == Lipinski.NumHAcceptors(molecule)
    assert "NaN" not in json.dumps(payload, allow_nan=False)


def test_all_saved_fit_and_ensemble_commitments_flow_through_measurement_and_caco(payload):
    results = []
    for index in range(25):
        state = state_for(payload, "active_fit", index, revealed=True, caco=True)
        ids = resolve_committed_ids(payload, state)
        assert ids == payload["nominations"]["nominations"][state["committed_fit_key"]]
        assert len(ids) == 50
        measured = measured_shortlist_summary(payload, ids)
        caco = caco_shortlist_summary(payload, ids)
        assert measured["measured_target_passes"] == payload["retrospective"]["fit_target_passes"][state["committed_fit_key"]]
        assert caco["paired_numeric_count"] + caco["missing_or_bounded_count"] == 50
        results.append(measured["measured_target_passes"])
    assert (min(results), max(results)) == (31, 42)
    ensemble = state_for(payload, "ensemble", revealed=True, caco=True)
    ids = resolve_committed_ids(payload, ensemble)
    assert measured_shortlist_summary(payload, ids)["measured_target_passes"] == 41
    assert caco_shortlist_summary(payload, ids)["paired_numeric_count"] == 38
    assert caco_shortlist_summary(payload, ids)["paired_numeric_among_initial_passes"] == 33


def test_analysis_withholds_outcomes_and_rejects_malformed_commits(payload):
    state = state_for(payload, "active_fit", 12)
    active = active_fit_summary(payload, state)
    assert active["overlap_with_ensemble"] + active["active_only_count"] == 50
    context = selected_molecule_context(payload, payload["retrospective"]["unanimous_id"], state)
    assert "measurement_summary" not in context
    state["committed_ids"] = state["committed_ids"][:-1]
    with pytest.raises(ValueError, match="exactly fifty"):
        resolve_committed_ids(payload, state)
    state = state_for(payload, "ensemble")
    state["committed_fit_key"] = payload["nominations"]["fit_keys"][0]
    with pytest.raises(ValueError, match="ensemble"):
        resolve_committed_ids(payload, state)
