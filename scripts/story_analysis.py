"""Small, dependency-free calculations behind the interactive story.

These functions intentionally consume the portable JSON payload rather than
the source dataframes.  They are used as an independent check on browser
state, and are kept simple enough to mirror in the portable notebook.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


CAPACITY = 50


def _state_value(state: Mapping[str, Any], key: str, default: Any = None) -> Any:
    value = state.get(key, default)
    return default if value is None else value


def _fit_key(payload: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    nominations = payload["nominations"]
    keys = nominations["fit_keys"]
    index = _state_value(state, "active_fit_index", 0)
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(keys):
        raise ValueError("active_fit_index is not a saved fit index")
    key = keys[index]
    supplied = state.get("active_fit_key")
    if supplied is not None and supplied != key:
        raise ValueError("active_fit_key does not match active_fit_index")
    return str(key)


def _ids(value: object, *, label: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{label} must be an ordered sequence")
    ids = [str(item) for item in value]
    if len(ids) != CAPACITY or len(set(ids)) != CAPACITY:
        raise ValueError(f"{label} must contain exactly fifty unique IDs")
    return ids


def resolve_committed_ids(payload: Mapping[str, Any], story_state: Mapping[str, Any]) -> list[str]:
    """Validate a commitment and return its canonical, source-derived order.

    A browser-provided list is evidence of the visitor's action, never the
    authority for the shortlist.  It must exactly match the saved fit or
    ensemble nomination list.
    """
    selection_kind = story_state.get("selection_kind")
    if selection_kind is None:
        if story_state.get("committed_ids", []) not in ([], None):
            raise ValueError("uncommitted state cannot include molecule IDs")
        return []
    nominations = payload["nominations"]
    if selection_kind == "active_fit":
        key = story_state.get("committed_fit_key")
        if key not in nominations["nominations"]:
            raise ValueError("active-fit commitment has an unknown fit key")
        expected = _ids(nominations["nominations"][key], label="saved fit nomination")
    elif selection_kind == "ensemble":
        if story_state.get("committed_fit_key") is not None:
            raise ValueError("ensemble commitment cannot have a fit key")
        expected = _ids(nominations["ensemble_ids"], label="ensemble nomination")
    else:
        raise ValueError("selection_kind must be active_fit, ensemble, or None")
    supplied = _ids(story_state.get("committed_ids"), label="committed_ids")
    if supplied != expected:
        raise ValueError("committed_ids do not match the selected source list")
    return expected


def active_fit_summary(payload: Mapping[str, Any], story_state: Mapping[str, Any]) -> dict[str, Any]:
    """Return prediction-only active-fit facts; no measurement fields are read."""
    nominations = payload["nominations"]
    key = _fit_key(payload, story_state)
    active_ids = _ids(nominations["nominations"][key], label="active fit nomination")
    ensemble_ids = _ids(nominations["ensemble_ids"], label="ensemble nomination")
    active_set, ensemble_set = set(active_ids), set(ensemble_ids)
    metadata = next(item for item in nominations["fit_metadata"] if item["fit_key"] == key)
    inspected = story_state.get("inspected_molecule_id")
    return {
        "fit_key": key,
        "fit_label": metadata["label"],
        "active_ids": active_ids,
        "overlap_with_ensemble": len(active_set & ensemble_set),
        "active_only_count": len(active_set - ensemble_set),
        "ensemble_only_count": len(ensemble_set - active_set),
        "inspected_id": inspected,
        "inspected_inclusion_frequency": int(
            nominations["inclusion_counts"].get(inspected, 0)
        ),
    }


def _record(payload: Mapping[str, Any], molecule_id: str) -> Mapping[str, Any]:
    try:
        return payload["evidence_records"][molecule_id]
    except KeyError as exc:
        raise ValueError(f"unknown molecule ID: {molecule_id}") from exc


def measured_shortlist_summary(payload: Mapping[str, Any], committed_ids: Sequence[str]) -> dict[str, Any]:
    """Count LogD/KSOL outcomes only from the exact committed IDs."""
    ids = _ids(committed_ids, label="committed_ids")
    outcomes = [_record(payload, molecule_id).get("measurement_summary") for molecule_id in ids]
    if any(outcome is None for outcome in outcomes):
        raise ValueError("committed shortlist lacks a measurement record")
    passes = sum(bool(outcome["target_pass"]) for outcome in outcomes)
    retrospective = payload["retrospective"]
    return {
        "selected_count": len(ids),
        "measured_target_passes": passes,
        "ensemble_measured_target_passes": int(retrospective["ensemble_target_passes"]),
        "fit_range": dict(retrospective["fit_target_passes_summary"]),
        "random_expected_passes": float(retrospective["random_reference"]["random_expected_passes"]),
    }


def caco_shortlist_summary(payload: Mapping[str, Any], committed_ids: Sequence[str]) -> dict[str, Any]:
    """Count numeric paired Caco-2 evidence and preserve missing/bounded status."""
    ids = _ids(committed_ids, label="committed_ids")
    paired: list[str] = []
    paired_initial_passes = 0
    for molecule_id in ids:
        record = _record(payload, molecule_id)
        endpoints = {endpoint["key"]: endpoint for endpoint in record["endpoints"]}
        papp = endpoints["Caco-2 Permeability Papp A>B"]
        efflux = endpoints["Caco-2 Permeability Efflux"]
        numeric = (
            papp["status"] == "measured" and efflux["status"] == "measured"
            and papp["value"] is not None and efflux["value"] is not None
        )
        if numeric:
            paired.append(molecule_id)
            paired_initial_passes += bool(record["measurement_summary"]["target_pass"])
    # A committed contrast is deterministic: prefer the lexicographically first
    # paired initial target miss; otherwise use the first paired record.
    misses = [
        molecule_id for molecule_id in paired
        if not _record(payload, molecule_id)["measurement_summary"]["target_pass"]
    ]
    contrast = sorted(misses or paired)[0] if paired else None
    return {
        "selected_count": len(ids),
        "paired_numeric_count": len(paired),
        "paired_numeric_among_initial_passes": paired_initial_passes,
        "missing_or_bounded_count": len(ids) - len(paired),
        "contrast_id": contrast,
    }


def selected_molecule_context(
    payload: Mapping[str, Any], molecule_id: str, story_state: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Return a selected record without leaking outcomes before disclosure."""
    record = _record(payload, molecule_id)
    context: dict[str, Any] = {
        "molecule_id": molecule_id,
        "role": record["role"],
        "inclusion_frequency": int(payload["nominations"]["inclusion_counts"].get(molecule_id, 0)),
        "ensemble_prediction": record.get("ensemble_prediction"),
    }
    revealed = bool(story_state and story_state.get("measurements_revealed"))
    if revealed:
        context["measurement_summary"] = record.get("measurement_summary")
    if story_state and story_state.get("caco_revealed"):
        context["caco_endpoints"] = [
            endpoint for endpoint in record["endpoints"]
            if endpoint["key"].startswith("Caco-2")
        ]
    return context
