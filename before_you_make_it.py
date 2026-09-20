# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["anywidget==0.9.21", "duckdb==1.4.4", "marimo==0.24.2", "numpy==2.4.3", "pandas==2.3.3", "rdkit==2025.9.6", "traitlets==5.14.3"]
# ///
"""Before You Make It — fifty experiments, twenty-five maps, one decision.

The viewing path consumes pinned source data, saved predictions, and the cached
ChemLlama run only. It never loads model weights or submits inference work.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="Before You Make It")


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    from scripts.experience_data import load_visual_payload
    from widgets.molecule_evidence import MoleculeEvidenceLens, ScaleJourney

    return MoleculeEvidenceLens, ScaleJourney, load_visual_payload, mo, pd


@app.cell
def _(mo):
    mo.md("""
    # Before You Make It

    ## Fifty experiments. Twenty-five maps. One next decision.

    **How do we choose a few molecules to investigate when our maps of what
    looks promising disagree—and when measurements can change even their
    shared recommendation?**

    Pull back from molecular possibility, keep one real AI proposal, and
    carry the same retrospective molecules from nomination to measurement.
    """)
    return


@app.cell
def _(load_visual_payload):
    visual_payload = load_visual_payload()
    return (visual_payload,)


@app.cell
def _(ScaleJourney, mo, visual_payload):
    opening_seed = visual_payload["seeds"][0]
    opening_seed_id = opening_seed["seed_id"]
    scale_payload = {
        "scale_landmarks": visual_payload["scale_landmarks"],
        "assay_accounting": visual_payload["assay_accounting"],
        "seed": opening_seed,
        "seed_record": visual_payload["evidence_records"][opening_seed_id],
        "seed_svg_gzip_base64": visual_payload["depictions"]["items"][opening_seed_id],
    }
    scale_journey = mo.ui.anywidget(ScaleJourney(payload=scale_payload))
    scale_journey
    return


@app.cell
def _(MoleculeEvidenceLens, mo, visual_payload):
    evidence_lens = mo.ui.anywidget(MoleculeEvidenceLens(payload=visual_payload))
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
    overlap = len(set(fit_ids) & set(ensemble_ids))
    candidate_id = story_state.get("candidate_id")
    inspected_id = story_state.get("inspected_molecule_id")
    stage = story_state.get("evidence_stage", "nomination")
    assay = story_state.get("next_assay")
    state_rows = [
        {"Python-owned value": "Active saved fit", "Current value": f"{fit_label} · {overlap}/50 overlap with ensemble"},
        {"Python-owned value": "Retained proposal", "Current value": candidate_id or "not chosen"},
        {"Python-owned value": "Inspected retrospective ID", "Current value": inspected_id or "none"},
        {"Python-owned value": "Evidence stage", "Current value": stage},
    ]
    if assay and candidate_id:
        reason = {
            "Caco-2 permeability and efflux": "Could reveal transport behavior outside the original LogD/KSOL question.",
            "Kinetic solubility": "Would replace a computed context cue with a measurement for this exact proposal.",
            "HLM intrinsic clearance": "Would add a human-microsomal metabolism question omitted by the original objective.",
        }[assay]
        state_rows.append(
            {
                "Python-owned value": "Candidate-specific decision",
                "Current value": f"{candidate_id} → {assay}. {reason}",
            }
        )
    mo.accordion(
        {
            "Live Python state (proof of reactive bridge)": mo.ui.table(
                pd.DataFrame(state_rows), pagination=False
            )
        }
    )
    return


@app.cell
def _(mo, visual_payload):
    reference = visual_payload["retrospective"]["random_reference"]
    source_hashes = visual_payload["provenance"]["source_hashes"]
    mo.accordion(
        {
            "Methods, boundaries, and provenance": mo.md(
                f"""
                The retrospective cohort is the **2,160** released test records
                with numeric LogD and KSOL. The illustrative target is LogD
                **{visual_payload['targets']['logd_low']}–{visual_payload['targets']['logd_high']}**
                and KSOL **≥ {visual_payload['targets']['ksol_min_um']} µM**, fixed
                from training records. The analytic random-fifty expectation is
                **50 × {reference['cohort_passes']} / {reference['cohort_count']} =
                {reference['random_expected_passes']:.6f}**; the displayed band
                comes from seeded random shortlists and is not assay uncertainty.

                The 25 saved repeat/fold fits share a method and overlapping
                training data. Their nominations show selection sensitivity,
                not independent expert votes or calibrated uncertainty. The
                unanimous example was noticed retrospectively using the
                prediction-only rule “present in every fit top fifty.”

                ChemLlama proposals are cached raw-SMILES continuation samples
                from run **{visual_payload['generation']['run_id']}**. The run
                recorded **96 raw / 27 unique valid / 69 invalid / 0 duplicate**
                samples. It does not establish conditional analog optimization;
                generated candidates keep experimental fields unknown.

                Source hashes are pinned for all five scientific inputs
                ({len(source_hashes)} verified files). Missing numeric fields can
                include unavailable evidence or bounded observations excluded
                from the ML-ready tables; unknown is never converted to zero or
                failure. Favorable properties do not establish efficacy or
                clinical success.
                """
            )
        }
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    Data: OpenADMET/ExpansionRx (CC BY 4.0) and the pinned Pat Walters
    benchmark prediction revision. Molecular depictions are generated with
    RDKit. Original custom widget code and notebook implementation were
    developed with AI assistance; every scientific result is recomputed from
    pinned released inputs.
    """)
    return


if __name__ == "__main__":
    app.run()
