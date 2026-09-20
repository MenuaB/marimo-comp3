"""Anywidget bridges for the counted scale and molecule evidence lens."""

from __future__ import annotations

from pathlib import Path

import anywidget
import traitlets

ASSETS = Path(__file__).resolve().parent


def initial_story_state(payload: dict[str, object]) -> dict[str, object]:
    nominations = payload["nominations"]
    unanimous_id = payload["retrospective"]["unanimous_id"]
    first_seed = payload["seeds"][0]["seed_id"]
    return {
        "seed_id": first_seed,
        "candidate_id": None,
        "active_fit_index": 0,
        "active_fit_key": nominations["fit_keys"][0],
        "inspected_molecule_id": unanimous_id,
        "selection_kind": None,
        "committed_ids": [],
        "evidence_stage": "nomination",
        "measurements_revealed": False,
        "caco_revealed": False,
        "returned_to_proposal": False,
        "next_assay": None,
        "event_sequence": 0,
    }


class ScaleJourney(anywidget.AnyWidget):
    """Counted, skippable scale transition into recorded evidence."""

    _esm = (ASSETS / "scale_journey.js").read_text()
    _css = (ASSETS / "scale_journey.css").read_text()

    payload = traitlets.Dict().tag(sync=True)
    state = traitlets.Dict(
        default_value={
            "started": False,
            "complete": False,
            "reduced_motion": False,
            "event_sequence": 0,
        }
    ).tag(sync=True)


class MoleculeEvidenceLens(anywidget.AnyWidget):
    """Preserve molecule identity while the source of evidence changes."""

    _esm = (ASSETS / "molecule_evidence.js").read_text()
    _css = (ASSETS / "molecule_evidence.css").read_text()

    payload = traitlets.Dict().tag(sync=True)
    state = traitlets.Dict().tag(sync=True)

    def __init__(self, *, payload: dict[str, object], **kwargs: object) -> None:
        if payload.get("schema_version") != "before-you-make-it-visual-v3":
            raise ValueError("MoleculeEvidenceLens requires visual payload schema v3")
        super().__init__(payload=payload, state=initial_story_state(payload), **kwargs)
