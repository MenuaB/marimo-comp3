# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["anywidget==0.9.21", "marimo==0.24.2", "pandas==2.3.3", "traitlets==5.14.3"]
# ///
"""Portable browser companion for Before You Make It.

All expensive chemistry, selection, and depiction work is precomputed into the
versioned bundle. Lightweight state remains reactive Python in marimo.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="Before You Make It")


@app.cell
def _():
    import hashlib
    import json
    from pathlib import Path

    local_bundle = Path(__file__).resolve().parent / "data" / "molab_bundle.json"
    bundle_revision = "716a90dc9eeb43b0cfe031dad281326e7e8a46c8"
    local_bundle_sha256 = "46ddd1866adf41c453ebdd167b2a17357633203467552bacc822808008aaadf2"
    published_bundle_sha256 = "46ddd1866adf41c453ebdd167b2a17357633203467552bacc822808008aaadf2"
    if local_bundle.is_file():
        bundle_bytes = local_bundle.read_bytes()
        expected_sha256 = local_bundle_sha256
    else:
        bundle_url = (
            "https://raw.githubusercontent.com/MenuaB/marimo-comp3/"
            f"{bundle_revision}/data/molab_bundle.json"
        )
        try:
            from pyodide.http import open_url
        except ModuleNotFoundError:
            from urllib.request import urlopen

            with urlopen(bundle_url) as response:
                bundle_bytes = response.read()
        else:
            bundle_bytes = open_url(bundle_url).read().encode("utf-8")
        expected_sha256 = published_bundle_sha256
    actual_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"Portable bundle hash mismatch: {actual_sha256}; expected {expected_sha256}"
        )
    visual_payload = json.loads(bundle_bytes)
    if visual_payload.get("schema_version") != "before-you-make-it-visual-v3":
        raise ValueError("Portable bundle schema mismatch; rebuild visual-v3")
    return (visual_payload,)


@app.cell
def _(visual_payload):
    import anywidget
    import traitlets

    def initial_state(payload):
        return {
            "seed_id": payload["seeds"][0]["seed_id"],
            "candidate_id": None,
            "active_fit_index": 0,
            "active_fit_key": payload["nominations"]["fit_keys"][0],
            "inspected_molecule_id": payload["retrospective"]["unanimous_id"],
            "inspected_by_visitor": False,
            "selection_kind": None,
            "committed_fit_key": None,
            "committed_ids": [],
            "evidence_stage": "nomination",
            "measurements_revealed": False,
            "caco_revealed": False,
            "returned_to_proposal": False,
            "next_assay": None,
            "event_sequence": 0,
        }

    class PortableScaleJourney(anywidget.AnyWidget):
        _esm = visual_payload["widget_assets"]["scale_js"]
        _css = visual_payload["widget_assets"]["scale_css"]
        payload = traitlets.Dict().tag(sync=True)
        state = traitlets.Dict(
            default_value={
                "started": False,
                "complete": False,
                "reduced_motion": False,
                "event_sequence": 0,
            }
        ).tag(sync=True)

    class PortableMoleculeEvidenceLens(anywidget.AnyWidget):
        _esm = visual_payload["widget_assets"]["lens_js"]
        _css = visual_payload["widget_assets"]["lens_css"]
        payload = traitlets.Dict().tag(sync=True)
        state = traitlets.Dict().tag(sync=True)

    return PortableMoleculeEvidenceLens, PortableScaleJourney, initial_state


@app.cell
def _():
    # These pure functions deliberately live in the portable notebook: they
    # operate on the JSON bundle and synchronized widget state only.
    def _fifty(ids, label):
        if not isinstance(ids, list) or len(ids) != 50 or len(set(ids)) != 50:
            raise ValueError(f"{label} must be exactly fifty unique ordered IDs")
        return list(ids)

    def resolve_committed_ids(payload, story_state):
        kind = story_state.get("selection_kind")
        if kind is None:
            if story_state.get("committed_ids", []) not in ([], None):
                raise ValueError("uncommitted state cannot contain IDs")
            return []
        nominations = payload["nominations"]
        if kind == "active_fit":
            key = story_state.get("committed_fit_key")
            if key not in nominations["nominations"]:
                raise ValueError("unknown committed fit key")
            expected = _fifty(nominations["nominations"][key], "saved fit")
        elif kind == "ensemble":
            if story_state.get("committed_fit_key") is not None:
                raise ValueError("ensemble cannot have a committed fit key")
            expected = _fifty(nominations["ensemble_ids"], "ensemble")
        else:
            raise ValueError("invalid selection kind")
        if _fifty(story_state.get("committed_ids"), "commit") != expected:
            raise ValueError("widget commitment does not match its saved source")
        return expected

    def active_fit_summary(payload, story_state):
        nominations = payload["nominations"]
        index = story_state.get("active_fit_index", 0)
        if not isinstance(index, int) or not 0 <= index < len(nominations["fit_keys"]):
            raise ValueError("invalid active fit index")
        key = nominations["fit_keys"][index]
        if story_state.get("active_fit_key", key) != key:
            raise ValueError("active fit key/index mismatch")
        active, ensemble = _fifty(nominations["nominations"][key], "active fit"), _fifty(nominations["ensemble_ids"], "ensemble")
        metadata = next(item for item in nominations["fit_metadata"] if item["fit_key"] == key)
        inspected = story_state.get("inspected_molecule_id")
        return {"fit_key": key, "fit_label": metadata["label"], "overlap_with_ensemble": len(set(active) & set(ensemble)), "active_only_count": len(set(active) - set(ensemble)), "ensemble_only_count": len(set(ensemble) - set(active)), "inspected_inclusion_frequency": nominations["inclusion_counts"].get(inspected, 0)}

    def measured_shortlist_summary(payload, committed_ids):
        ids = _fifty(committed_ids, "commit")
        records = payload["evidence_records"]
        outcomes = [records[molecule_id]["measurement_summary"] for molecule_id in ids]
        if any(outcome is None for outcome in outcomes):
            raise ValueError("committed ID lacks measurement evidence")
        retrospective = payload["retrospective"]
        return {"measured_target_passes": sum(item["target_pass"] for item in outcomes), "ensemble_measured_target_passes": retrospective["ensemble_target_passes"], "fit_range": retrospective["fit_target_passes_summary"], "random_expected_passes": retrospective["random_reference"]["random_expected_passes"]}

    def caco_shortlist_summary(payload, committed_ids):
        ids, records = _fifty(committed_ids, "commit"), payload["evidence_records"]
        paired = []
        for molecule_id in ids:
            endpoints = {item["key"]: item for item in records[molecule_id]["endpoints"]}
            if all(endpoints[key]["status"] == "measured" and endpoints[key]["value"] is not None for key in ("Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux")):
                paired.append(molecule_id)
        paired_passes = sum(records[molecule_id]["measurement_summary"]["target_pass"] for molecule_id in paired)
        misses = sorted(molecule_id for molecule_id in paired if not records[molecule_id]["measurement_summary"]["target_pass"])
        return {"paired_numeric_count": len(paired), "paired_numeric_among_initial_passes": paired_passes, "missing_or_bounded_count": 50-len(paired), "contrast_id": (misses or sorted(paired) or [None])[0]}

    def selected_molecule_context(payload, molecule_id, story_state=None):
        record = payload["evidence_records"][molecule_id]
        context = {"molecule_id": molecule_id, "role": record["role"], "ensemble_prediction": record.get("ensemble_prediction"), "inclusion_frequency": payload["nominations"]["inclusion_counts"].get(molecule_id, 0)}
        if story_state and story_state.get("measurements_revealed"):
            context["measurement_summary"] = record.get("measurement_summary")
        if story_state and story_state.get("caco_revealed"):
            context["caco_endpoints"] = [item for item in record["endpoints"] if item["key"].startswith("Caco-2")]
        return context

    return active_fit_summary, caco_shortlist_summary, measured_shortlist_summary, resolve_committed_ids, selected_molecule_context


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    return mo, pd


@app.cell
def _(mo):
    mo.md("""
    <section data-testid="story-introduction">

    # Before You Make It

    ## Imagine you can test only fifty molecules.

    There are far more possible molecules than a laboratory can make and
    measure. Each experiment adds evidence—how much a molecule dissolves,
    where it prefers to distribute, or how readily it crosses a cell-like
    barrier—but that work takes material, assays, and attention.

    Models help decide where to spend that attention. Here, **twenty-five
    saved fits of the same modeling method** each rank a held-out collection.
    Think of each fit as a different map of the same territory: the training
    folds change, so the recommended fifty can change too.

    You will follow one illustrative budget of **fifty experiments**: compare
    the model fits, commit an exact shortlist, reveal its real measurements,
    ask what another ADMET assay adds, and finally decide what evidence an
    unmeasured proposal would need next.

    </section>
    """)
    return


@app.cell
def _(PortableScaleJourney, mo, visual_payload):
    opening_seed = visual_payload["seeds"][0]
    opening_seed_id = opening_seed["seed_id"]
    scale_payload = {
        "scale_landmarks": visual_payload["scale_landmarks"],
        "assay_accounting": visual_payload["assay_accounting"],
        "seed": opening_seed,
        "seed_record": visual_payload["evidence_records"][opening_seed_id],
        "seed_svg_gzip_base64": visual_payload["depictions"]["items"][opening_seed_id],
    }
    scale_journey = mo.ui.anywidget(PortableScaleJourney(payload=scale_payload))
    scale_journey
    return


@app.cell
def _(PortableMoleculeEvidenceLens, initial_state, mo, visual_payload):
    evidence_lens = mo.ui.anywidget(
        PortableMoleculeEvidenceLens(
            payload=visual_payload,
            state=initial_state(visual_payload),
        )
    )
    evidence_lens
    return (evidence_lens,)


@app.cell
def _(active_fit_summary, caco_shortlist_summary, evidence_lens,
      measured_shortlist_summary, mo, pd, resolve_committed_ids,
      selected_molecule_context, visual_payload):
    story_state = evidence_lens.value.get("state", evidence_lens.state)
    active = active_fit_summary(visual_payload, story_state)
    committed_ids = resolve_committed_ids(visual_payload, story_state)
    candidate_id = story_state.get("candidate_id")
    state_rows = [
        {"Live shortlist analysis": "Active saved fit", "Value": active["fit_label"]},
        {"Live shortlist analysis": "Fit / ensemble overlap", "Value": f"{active['overlap_with_ensemble']}/50; {active['active_only_count']} active-only; {active['ensemble_only_count']} ensemble-only"},
        {"Live shortlist analysis": "Inspected nomination frequency", "Value": f"{active['inspected_inclusion_frequency']}/25"},
    ]
    if not committed_ids:
        state_rows.append({"Live shortlist analysis": "Commitment", "Value": "Choose this fit’s fifty or the ensemble fifty; outcomes withheld."})
    else:
        source = "Ensemble shortlist" if story_state["selection_kind"] == "ensemble" else f"{story_state['committed_fit_key']} shortlist"
        state_rows.extend([
            {"Live shortlist analysis": "Committed strategy", "Value": source},
            {"Live shortlist analysis": "Committed ordered IDs", "Value": f"{len(committed_ids)}; outcomes withheld"},
        ])
        if story_state.get("measurements_revealed"):
            measured = measured_shortlist_summary(visual_payload, committed_ids)
            selected = selected_molecule_context(visual_payload, story_state["inspected_molecule_id"], story_state)
            state_rows.extend([
                {"Live shortlist analysis": "Measured target passes", "Value": f"{measured['measured_target_passes']}/50; ensemble {measured['ensemble_measured_target_passes']}/50; related-fit range {measured['fit_range']['minimum']}–{measured['fit_range']['maximum']}"},
                {"Live shortlist analysis": "Exact random expectation", "Value": f"{measured['random_expected_passes']:.6f} passes"},
                {"Live shortlist analysis": "Inspected measured record", "Value": str(selected.get("measurement_summary"))},
            ])
        if story_state.get("caco_revealed"):
            caco = caco_shortlist_summary(visual_payload, committed_ids)
            state_rows.append({"Live shortlist analysis": "Paired Caco-2 evidence", "Value": f"{caco['paired_numeric_count']}/50; {caco['paired_numeric_among_initial_passes']} among initial passes; {caco['missing_or_bounded_count']} missing/bounded"})
    mo.accordion(
        {
            "Live shortlist analysis": mo.ui.table(
                pd.DataFrame(state_rows), pagination=False
            )
        }
    )
    return


@app.cell
def _(mo, visual_payload):
    reference = visual_payload["retrospective"]["random_reference"]
    mo.accordion(
        {
            "Methods and evidence boundaries": mo.md(
                f"""
                Same native/portable schema: `{visual_payload['schema_version']}`.
                The retrospective cohort has 2,160 released paired LogD/KSOL
                records. The exact random-fifty expectation is
                **{reference['random_expected_passes']:.6f}** passes. Saved fits
                are related repeat/fold models, not independent experts or
                calibrated uncertainty. Cached ChemLlama proposals from
                **{visual_payload['generation']['run_id']}** remain experimentally
                unknown; no model weights load during viewing.
                """
            )
        }
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    OpenADMET/ExpansionRx data (CC BY 4.0), pinned benchmark predictions,
    and RDKit depictions. Original custom widget code was developed with AI
    assistance; scientific values are derived from pinned released inputs.
    """)
    return


if __name__ == "__main__":
    app.run()
