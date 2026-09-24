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
    from scripts.story_analysis import (
        active_fit_summary,
        caco_shortlist_summary,
        measured_shortlist_summary,
        resolve_committed_ids,
        selected_molecule_context,
    )
    from widgets.molecule_evidence import MoleculeEvidenceLens, ScaleJourney

    return (MoleculeEvidenceLens, ScaleJourney, active_fit_summary,
            caco_shortlist_summary, load_visual_payload,
            measured_shortlist_summary, mo, pd, resolve_committed_ids,
            selected_molecule_context)


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
def _(active_fit_summary, caco_shortlist_summary, evidence_lens,
      measured_shortlist_summary, mo, pd, resolve_committed_ids,
      selected_molecule_context, visual_payload):
    story_state = evidence_lens.value.get("state", evidence_lens.state)
    active = active_fit_summary(visual_payload, story_state)
    committed_ids = resolve_committed_ids(visual_payload, story_state)
    candidate_id = story_state.get("candidate_id")
    inspected_id = story_state.get("inspected_molecule_id")
    stage = story_state.get("evidence_stage", "nomination")
    assay = story_state.get("next_assay")
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
            {"Live shortlist analysis": "Committed ordered IDs", "Value": str(len(committed_ids)) + "; outcomes withheld"},
        ])
        if story_state.get("measurements_revealed"):
            measured = measured_shortlist_summary(visual_payload, committed_ids)
            selected = selected_molecule_context(visual_payload, inspected_id, story_state)
            state_rows.extend([
                {"Live shortlist analysis": "Measured target passes", "Value": f"{measured['measured_target_passes']}/50; ensemble {measured['ensemble_measured_target_passes']}/50; related-fit range {measured['fit_range']['minimum']}–{measured['fit_range']['maximum']}"},
                {"Live shortlist analysis": "Exact random expectation", "Value": f"{measured['random_expected_passes']:.6f} passes"},
                {"Live shortlist analysis": "Inspected measured record", "Value": str(selected.get("measurement_summary"))},
            ])
        if story_state.get("caco_revealed"):
            caco = caco_shortlist_summary(visual_payload, committed_ids)
            state_rows.append({"Live shortlist analysis": "Paired Caco-2 evidence", "Value": f"{caco['paired_numeric_count']}/50; {caco['paired_numeric_among_initial_passes']} among initial passes; {caco['missing_or_bounded_count']} missing/bounded"})
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
            "Live shortlist analysis": mo.ui.table(
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
