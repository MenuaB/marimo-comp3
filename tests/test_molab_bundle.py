from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_browser_bundle_preserves_pinned_experience_facts() -> None:
    payload = json.loads((ROOT / "data" / "molab_bundle.json").read_text())

    assert payload["schema_version"] == 1
    assert len(payload["top_fifty"]) == 50
    assert len(payload["cohort_pass_flags"]) == 2160
    assert sum(payload["cohort_pass_flags"]) > 0
    assert payload["generation_manifest"]["generation_run_id"] == "chemllama-271948"
    assert payload["generation_manifest"]["counts"] == {
        "raw": 96,
        "valid_unique": 27,
        "invalid": 69,
        "duplicate": 0,
    }
    assert payload["assay_accounting"]["recorded_values"] == 36_003
