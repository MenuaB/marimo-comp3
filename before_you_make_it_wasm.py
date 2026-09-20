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
    import json
    from pathlib import Path

    local_bundle = Path(__file__).resolve().parent / "data" / "molab_bundle.json"
    if not local_bundle.is_file():
        raise RuntimeError(
            "The visual-v3 portable bundle is not beside this notebook. "
            "Run scripts/build_molab_bundle.py locally. The unpublished bundle "
            "is intentionally not fetched from a mutable GitHub branch."
        )
    visual_payload = json.loads(local_bundle.read_text())
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
            "selection_kind": None,
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
    import marimo as mo
    import pandas as pd

    return mo, pd


@app.cell
def _(mo):
    mo.md("""
    # Before You Make It

    ## Fifty experiments. Twenty-five maps. One next decision.

    **How do we choose a few molecules to investigate when our maps of what
    looks promising disagree—and when measurements can change even their
    shared recommendation?**

    This portable edition uses the same verified payload, RDKit SVG
    depictions, custom renderer, and state contract as the native notebook.
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
def _(evidence_lens, mo, pd, visual_payload):
    story_state = evidence_lens.value.get("state", evidence_lens.state)
    fit_index = int(story_state.get("active_fit_index", 0))
    fit_key = visual_payload["nominations"]["fit_keys"][fit_index]
    fit_label = visual_payload["nominations"]["fit_metadata"][fit_index]["label"]
    fit_ids = visual_payload["nominations"]["nominations"][fit_key]
    ensemble_ids = visual_payload["nominations"]["ensemble_ids"]
    candidate_id = story_state.get("candidate_id")
    assay = story_state.get("next_assay")
    state_rows = [
        {"Python-owned value": "Active saved fit", "Current value": f"{fit_label} · {len(set(fit_ids) & set(ensemble_ids))}/50 overlap with ensemble"},
        {"Python-owned value": "Retained proposal", "Current value": candidate_id or "not chosen"},
        {"Python-owned value": "Inspected retrospective ID", "Current value": story_state.get("inspected_molecule_id") or "none"},
        {"Python-owned value": "Evidence stage", "Current value": story_state.get("evidence_stage", "nomination")},
    ]
    if assay and candidate_id:
        state_rows.append({"Python-owned value": "Candidate-specific decision", "Current value": f"{candidate_id} → {assay}"})
    mo.accordion(
        {
            "Live portable Python state": mo.ui.table(
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
