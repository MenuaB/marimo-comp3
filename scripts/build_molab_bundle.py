"""Build the small, browser-safe evidence payload for the molab/WASM notebook."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.experience_data import (
    evidence_accounting,
    load_pinned_generation,
    scale_landmarks,
)
from scripts.notebook_data import DATA, prepare, shortlist

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "molab_bundle.json"


def records(frame: pd.DataFrame) -> list[dict[str, object]]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def main() -> None:
    cohort, _, preparation_manifest = prepare()
    candidates, generation_manifest, seeds = load_pinned_generation()
    top_fifty = shortlist(cohort, 50)
    training = pd.read_csv(DATA / "expansion_data_train.csv").rename(
        columns={"Molecule Name": "molecule_id"}
    )
    required_training = set(seed["seed_id"] for seed in seeds) | set(
        top_fifty.nearest_training_id
    )
    payload = {
        "schema_version": 1,
        "scale_landmarks": scale_landmarks(),
        "assay_accounting": evidence_accounting(),
        "seeds": seeds,
        "candidates": records(candidates),
        "generation_manifest": generation_manifest,
        "preparation_manifest": preparation_manifest,
        "top_fifty": records(top_fifty),
        "cohort_pass_flags": cohort.measured_threshold_pass.astype(bool).tolist(),
        "training_context": records(
            training.loc[training.molecule_id.isin(required_training)].copy()
        ),
    }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
