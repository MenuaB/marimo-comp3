from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.experience_data import load_visual_payload


ROOT = Path(__file__).resolve().parents[1]


def test_browser_bundle_preserves_pinned_experience_facts() -> None:
    payload = json.loads((ROOT / "data" / "molab_bundle.json").read_text())

    assert payload["schema_version"] == "before-you-make-it-visual-v3"
    assert len(payload["nominations"]["ensemble_ids"]) == 50
    assert len(payload["nominations"]["union_order"]) == 256
    assert payload["nominations"]["intersection_ids"] == ["E-0024329"]
    assert payload["generation"]["run_id"] == "chemllama-271948"
    assert payload["generation"]["counts"] == {
        "raw": 96,
        "valid_unique": 27,
        "invalid": 69,
        "duplicate": 0,
    }
    assert payload["assay_accounting"]["recorded_values"] == 36_003
    assert payload["retrospective"]["random_reference"]["random_expected_passes"] == 50 * 905 / 2160
    assert payload["retrospective"]["ensemble_target_passes"] == 41
    assert payload["retrospective"]["caco_paired"] == 38
    assert payload["depictions"]["encoding"] == "gzip+base64"
    assert payload["generation"]["chemistry_audit_counts"]["featured_candidates"] == 23
    assert payload["generation"]["default_candidate_id"] != "C-0033"
    assert len(payload["candidate_audit"]) == 27
    assert payload["provenance"]["candidate_audit_sha256"]
    assert set(payload["depictions"]["items"]) == set(payload["evidence_records"])
    assert set(payload["widget_assets"]) == {"lens_js", "lens_css", "scale_js", "scale_css"}


def test_portable_bundle_same_committed_ids_across_disclosures() -> None:
    payload = json.loads((ROOT / "data" / "molab_bundle.json").read_text())
    committed = payload["nominations"]["ensemble_ids"]
    records = payload["evidence_records"]
    assert len(committed) == len(set(committed)) == 50
    assert all(records[molecule_id]["ensemble_prediction"] is not None for molecule_id in committed)
    assert all(records[molecule_id]["measurement_summary"] is not None for molecule_id in committed)
    assert sum(
        records[molecule_id]["endpoints"][4]["value"] is not None
        and records[molecule_id]["endpoints"][5]["value"] is not None
        for molecule_id in committed
    ) == 38


def test_portable_bundle_contains_newcomer_first_narrative() -> None:
    payload = json.loads((ROOT / "data" / "molab_bundle.json").read_text())
    scale_js = payload["widget_assets"]["scale_js"]
    lens_js = payload["widget_assets"]["lens_js"]

    assert "What are you looking at?" in scale_js
    assert "hypothetical inspection time" in scale_js
    assert "A structure tells us what a molecule is" in scale_js
    assert "Show the summary" in scale_js
    assert "The generated proposal does not enter this analysis" in lens_js
    assert "How sensitive is the shortlist to the fitted model?" in lens_js
    assert "Compare with measurements" in lens_js
    assert "Ask about permeability and efflux" in lens_js
    assert "MoleculeEvidenceLens keeps" not in lens_js
    assert "scrub the saved fits" not in lens_js


def test_native_loader_accepts_bundle_and_rejects_schema_or_hash_tampering(tmp_path) -> None:
    payload = load_visual_payload()
    assert payload["nominations"]["intersection_ids"] == ["E-0024329"]

    malformed = json.loads((ROOT / "data" / "molab_bundle.json").read_text())
    malformed["schema_version"] = "unknown"
    bad_schema = tmp_path / "bad-schema.json"
    bad_schema.write_text(json.dumps(malformed))
    with pytest.raises(ValueError, match="schema mismatch"):
        load_visual_payload(bad_schema)

    malformed = json.loads((ROOT / "data" / "molab_bundle.json").read_text())
    malformed["nominations"]["intersection_ids"] = []
    bad_hash = tmp_path / "bad-hash.json"
    bad_hash.write_text(json.dumps(malformed))
    with pytest.raises(ValueError, match="nomination hash mismatch"):
        load_visual_payload(bad_hash)
