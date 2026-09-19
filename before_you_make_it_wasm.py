# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["altair==6.0.0", "marimo==0.24.2", "numpy==2.4.3", "pandas==2.3.3"]
# ///
"""Browser-native companion to Before You Make It.

This version deliberately uses a compact, audited evidence payload rather than
native cheminformatics libraries, so GitHub/molab's WebAssembly preview remains
interactive. Exact SMILES are shown as the portable structure representation.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="Before You Make It")


@app.cell
def _():
    import json
    from pathlib import Path

    local_bundle = Path(__file__).resolve().parent / "data" / "molab_bundle.json"
    if local_bundle.is_file():
        bundle_text = local_bundle.read_text()
    else:
        # The GitHub preview is a one-file WASM app. raw.githubusercontent.com
        # permits CORS, allowing this audited companion payload to load there.
        from pyodide.http import open_url

        bundle_text = open_url(
            "https://raw.githubusercontent.com/MenuaB/marimo-comp3/main/data/molab_bundle.json"
        ).read()
    evidence_bundle = json.loads(bundle_text)
    return (evidence_bundle,)


@app.cell
def _():
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd

    alt.data_transformers.disable_max_rows()
    return alt, mo, np, pd


@app.cell
def _(mo):
    mo.md("""
    # Before You Make It

    ## An enormous search. A few experiments. One next decision.

    This browser-native edition keeps the same pinned evidence and nine actions
    as the full notebook. It uses exact SMILES rather than native 2D depictions
    so it can run entirely in your browser.
    """)
    return


@app.cell
def _(evidence_bundle, mo):
    scale_control = mo.ui.radio(
        options={"Pull back": "pull", "Skip motion": "reduced"},
        value="Pull back",
        label="1. Begin the scale view",
    )
    mo.vstack([mo.md("## 1. Start close enough to understand one possibility"), scale_control])
    return (scale_control,)


@app.cell
def _(alt, evidence_bundle, mo, np, pd, scale_control):
    scale_table = pd.DataFrame(evidence_bundle["scale_landmarks"])
    scale_table["log10_count"] = np.log10(scale_table["count"])
    scale_plot = alt.Chart(scale_table).mark_circle(color="#38598b", opacity=0.82).encode(
        x=alt.X("log10_count:Q", title="Orders of magnitude (log₁₀ possibilities)", axis=alt.Axis(values=[0, 3, 6, 9, 11.22])),
        y=alt.Y("marks:Q", title=None, axis=None),
        size=alt.Size("marks:Q", legend=None, scale=alt.Scale(range=[100, 2300])),
        tooltip=[alt.Tooltip("count:Q", format=","), "label:N"],
    ).properties(height=190, title="Schematic compression: every mark is an aggregate landmark")
    final_scale = scale_table.iloc[-1]
    transition_copy = "All landmarks are immediately visible." if scale_control.value == "reduced" else "One pull-back compresses intervening orders of magnitude schematically."
    mo.vstack([
        mo.md(f"""{transition_copy}

        GDB-17 enumerates about **{int(final_scale['count']):,}** molecules with up to 17 atoms of C, N, O, S and halogens. At one hypothetical inspection per second, without stopping, that is about **{final_scale['hypothetical_years_at_one_per_second']:,.0f} years**. This is a scale comparison, not laboratory time."""),
        mo.ui.altair_chart(scale_plot),
        mo.callout("Now enter one real collection that people measured. ExpansionRx is not a subset of GDB-17.", kind="info"),
    ])
    return


@app.cell
def _(evidence_bundle, mo):
    seed_labels = {
        f"{seed['seed_id']} · benchmark cluster {seed['cluster']}": seed["seed_id"]
        for seed in evidence_bundle["seeds"]
    }
    seed_control = mo.ui.dropdown(
        options=seed_labels,
        value=next(iter(seed_labels)),
        label="2. Choose a real training seed / family",
    )
    mo.vstack([mo.md("## 2. Enter one measured collection"), seed_control])
    return (seed_control,)


@app.cell
def _(alt, evidence_bundle, mo, np, pd, seed_control):
    selected_seed = next(
        seed for seed in evidence_bundle["seeds"] if seed["seed_id"] == seed_control.value
    )
    training_table = pd.DataFrame(evidence_bundle["training_context"])
    seed_record = training_table.loc[training_table.molecule_id == selected_seed["seed_id"]].iloc[0]
    accounting = evidence_bundle["assay_accounting"]
    endpoint_table = pd.DataFrame({
        "endpoint": accounting["endpoint_columns"],
        "recorded value": [seed_record[column] for column in accounting["endpoint_columns"]],
    })
    endpoint_table["evidence"] = np.where(
        endpoint_table["recorded value"].notna(), "recorded numeric value", "unknown / not numeric"
    )
    coverage_table = pd.DataFrame({
        "endpoint": accounting["endpoint_columns"],
        "recorded values": [accounting["per_endpoint"][column] for column in accounting["endpoint_columns"]],
    })
    coverage_table["missing or non-numeric"] = accounting["records"] - coverage_table["recorded values"]
    coverage_long = coverage_table.melt(id_vars="endpoint", var_name="evidence", value_name="molecule-endpoint cells")
    coverage_plot = alt.Chart(coverage_long).mark_bar().encode(
        y=alt.Y("endpoint:N", title=None, sort="-x"),
        x=alt.X("molecule-endpoint cells:Q", title="Released molecules"),
        color=alt.Color("evidence:N", scale=alt.Scale(domain=["recorded values", "missing or non-numeric"], range=["#2a9d8f", "#d9e2ec"])),
    ).properties(height=235, title="The original record expands into uneven evidence coverage")
    mo.vstack([
        mo.md(f"""**{selected_seed['seed_id']}** is a real training molecule. Its exact structure is:

        `{selected_seed['smiles']}`

        Measured LogD: **{selected_seed['measured_LogD']:.1f}**; kinetic solubility: **{selected_seed['measured_KSOL_uM']:.1f} µM**."""),
        mo.ui.table(endpoint_table, pagination=False),
        mo.ui.altair_chart(coverage_plot),
        mo.md(f"These nine columns contain **{accounting['recorded_values']:,} recorded numeric assay values** across **{accounting['records']:,} released molecules**. **{accounting['missing_or_non_numeric']:,}** of **{accounting['possible_cells']:,}** possible cells lack numeric ML-ready values."),
    ])
    return selected_seed, training_table


@app.cell
def _(evidence_bundle, selected_seed):
    candidate_table = pd.DataFrame(evidence_bundle["candidates"])
    seed_candidates = candidate_table.loc[candidate_table.seed_id == selected_seed["seed_id"]].sort_values("candidate_id", kind="stable")
    return (seed_candidates,)


@app.cell
def _(evidence_bundle, mo, seed_candidates):
    proposal_options = {
        f"{row.candidate_id} · prompt-seed similarity {row.similarity_to_seed:.2f}": row.candidate_id
        for row in seed_candidates.itertuples(index=False)
    }
    proposal_control = mo.ui.dropdown(
        options=proposal_options,
        value=next(iter(proposal_options)),
        label="3. Choose one recorded AI proposal",
    )
    generation_counts = evidence_bundle["generation_manifest"]["counts"]
    mo.vstack([
        mo.md(f"""## 3. Let AI suggest possibilities

        Cached outputs from the pinned ChemLlama-1B run: **{generation_counts['raw']} raw samples**, **{generation_counts['valid_unique']} unique valid**, **{generation_counts['invalid']} invalid**, **{generation_counts['duplicate']} duplicates**. These are seed-prompt outputs, not live inference."""),
        proposal_control,
        mo.ui.table(seed_candidates[["candidate_id", "smiles", "similarity_to_seed", "nearest_training_id", "nearest_training_similarity"]], pagination=True),
    ])
    return (proposal_control,)


@app.cell
def _(mo, proposal_control, seed_candidates):
    selected_candidate = seed_candidates.loc[seed_candidates.candidate_id == proposal_control.value].iloc[0]
    descriptor_table = pd.DataFrame(list(selected_candidate.computed_descriptors.items()), columns=["computed descriptor", "value"])
    mo.vstack([
        mo.md(f"""### Your proposal: `{selected_candidate.candidate_id}`

        Exact structure: `{selected_candidate.smiles}`

        Known: computed descriptors and nearest-training context `{selected_candidate.nearest_training_id}` (Morgan similarity {selected_candidate.nearest_training_similarity:.3f}). Unknown: this proposal's experimental LogD, kinetic solubility, Caco-2, and wider assay profile."""),
        mo.ui.table(descriptor_table, pagination=False),
    ])
    return (selected_candidate,)


@app.cell
def _(mo):
    commit_control = mo.ui.button(label="4. Commit fifty retrospective choices", kind="success")
    mo.vstack([mo.md("## Before deciding what to make, inspect a collection where experimental answers already exist"), commit_control])
    return (commit_control,)


@app.cell
def _(evidence_bundle, np, pd):
    browser_shortlist = pd.DataFrame(evidence_bundle["top_fifty"])
    browser_pass_flags = np.asarray(evidence_bundle["cohort_pass_flags"], dtype=bool)
    return browser_pass_flags, browser_shortlist


@app.cell
def _(alt, browser_pass_flags, browser_shortlist, commit_control, evidence_bundle, mo, np, pd):
    committed = bool(commit_control.value)
    if committed:
        constants = evidence_bundle["preparation_manifest"]["constants"]
        commitment_rng = np.random.default_rng(20260918)
        commitment_random_counts = np.array([commitment_rng.choice(browser_pass_flags, size=50, replace=False).sum() for _ in range(2000)])
        target_frame = pd.DataFrame({"x1": [constants["logd_low"]], "x2": [constants["logd_high"]], "y1": [constants["ksol_median_um"]], "y2": [2000]})
        target_plot = alt.Chart(target_frame).mark_rect(opacity=0.13, color="#2a9d8f").encode(x="x1:Q", x2="x2:Q", y="y1:Q", y2="y2:Q")
        points_plot = alt.Chart(browser_shortlist).mark_circle(size=62, opacity=0.74, color="#377eb8").encode(
            x=alt.X("pred_LogD:Q", title="Predicted LogD"),
            y=alt.Y("pred_KSOL_uM:Q", title="Predicted kinetic solubility (µM)", scale=alt.Scale(type="log", domain=[1, 2000])),
            tooltip=["molecule_id:N", alt.Tooltip("pred_LogD:Q", format=".2f"), alt.Tooltip("pred_KSOL_uM:Q", format=".1f")],
        )
        commit_view = mo.vstack([
            mo.md(f"""## 4. A limited budget forces a choice

            This fixed fifty is ranked from saved predictions only. The equal-budget random reference is **{commitment_random_counts.mean():.2f}** expected target passes; outcomes remain hidden."""),
            mo.ui.altair_chart((target_plot + points_plot).properties(height=315, title="Prediction-only positions for the same 50 identities")),
        ])
    else:
        commit_view = mo.callout("Commit the fixed fifty to enter the prediction-only retrospective cohort. Held-out outcomes remain hidden.", kind="info")
    commit_view
    return (committed,)


@app.cell
def _(committed, mo):
    measurement_control = mo.ui.button(label="5. Reveal what the laboratory said", kind="warn")
    (measurement_control if committed else mo.md("Commit the retrospective choices before revealing laboratory measurements."))
    return (measurement_control,)


@app.cell
def _(alt, browser_pass_flags, browser_shortlist, committed, measurement_control, mo, np, pd):
    measurements_revealed = committed and bool(measurement_control.value)
    if measurements_revealed:
        reveal_rng = np.random.default_rng(20260918)
        reveal_random_counts = np.array([reveal_rng.choice(browser_pass_flags, size=50, replace=False).sum() for _ in range(2000)])
        reveal_rows = pd.concat([
            browser_shortlist[["molecule_id", "pred_LogD", "pred_KSOL_uM"]].rename(columns={"pred_LogD": "LogD", "pred_KSOL_uM": "KSOL_uM"}).assign(evidence="prediction"),
            browser_shortlist[["molecule_id", "obs_LogD", "obs_KSOL_uM"]].rename(columns={"obs_LogD": "LogD", "obs_KSOL_uM": "KSOL_uM"}).assign(evidence="measurement"),
        ], ignore_index=True)
        reveal_plot = alt.Chart(reveal_rows).mark_circle(size=45, opacity=0.68, color="#377eb8").encode(
            x=alt.X("LogD:Q", title="LogD"), y=alt.Y("KSOL_uM:Q", title="Kinetic solubility (µM)", scale=alt.Scale(type="log", domain=[1, 2000])), tooltip=["molecule_id:N", "evidence:N", alt.Tooltip("LogD:Q", format=".2f"), alt.Tooltip("KSOL_uM:Q", format=".1f")],
        ).facet(column=alt.Column("evidence:N", title=None, sort=["prediction", "measurement"])).properties(title="Same 50 IDs: predicted and released positions")
        measurement_view = mo.vstack([mo.md(f"""## 5. What did the laboratory say?

        **{int(browser_shortlist.measured_threshold_pass.sum())}/50** meet the illustrative measured profile, versus **{reveal_random_counts.mean():.2f}** expected for equal-size random selection (95% simulated range {np.quantile(reveal_random_counts, .025):.0f}–{np.quantile(reveal_random_counts, .975):.0f})."""), mo.ui.altair_chart(reveal_plot)])
    else:
        measurement_view = mo.md("Laboratory outcomes remain hidden until the reveal.")
    measurement_view
    return (measurements_revealed,)


@app.cell
def _(measurements_revealed, mo):
    caco_control = mo.ui.button(label="6. What else matters? Show Caco-2 evidence")
    (caco_control if measurements_revealed else mo.md("The second evidence reveal follows the laboratory reveal."))
    return (caco_control,)


@app.cell
def _(alt, browser_shortlist, caco_control, measurements_revealed, mo, np):
    caco_revealed = measurements_revealed and bool(caco_control.value)
    caco_columns = ["Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux"]
    if caco_revealed:
        paired_caco = browser_shortlist.dropna(subset=caco_columns).copy()
        target_passes = browser_shortlist.loc[browser_shortlist.measured_threshold_pass]
        paired_caco["initial profile"] = np.where(paired_caco.measured_threshold_pass, "meets initial profile", "misses initial profile")
        caco_plot = alt.Chart(paired_caco).mark_circle(size=72, opacity=0.78).encode(x=alt.X("Caco-2 Permeability Papp A>B:Q", title="Caco-2 Papp A>B (10⁻⁶ cm/s)"), y=alt.Y("Caco-2 Permeability Efflux:Q", title="Caco-2 efflux ratio"), color="initial profile:N", tooltip=["molecule_id:N", "initial profile:N", *caco_columns]).properties(height=310, title="Additional evidence for the unchanged original fifty")
        caco_view = mo.vstack([mo.md(f"""## 6. The answer can be right and the question incomplete

        **{len(paired_caco)}/50** have paired numeric Caco-2 values; **{target_passes.dropna(subset=caco_columns).shape[0]}/{len(target_passes)}** initial target passes have paired evidence. The others are unknown, not failures."""), mo.ui.altair_chart(caco_plot), mo.ui.table(browser_shortlist[["molecule_id", "measured_threshold_pass", *caco_columns]].fillna("unknown / unavailable"), pagination=True)])
    else:
        caco_view = mo.md("Caco-2 is deliberately a second discovery.")
    caco_view
    return (caco_revealed,)


@app.cell
def _(browser_shortlist, caco_revealed, mo):
    inspect_options = {f"{row.molecule_id} · predicted score {row.pred_score:.3f}": row.molecule_id for row in browser_shortlist.itertuples(index=False)}
    inspect_default = next(label for label, value in inspect_options.items() if value == "E-0023839")
    inspect_control = mo.ui.dropdown(options=inspect_options, value=inspect_default, label="7. Inspect one retrospective example")
    (inspect_control if caco_revealed else mo.md("Choose an example after the Caco-2 discovery."))
    return (inspect_control,)


@app.cell
def _(browser_shortlist, caco_revealed, inspect_control, mo, pd, training_table):
    inspected = browser_shortlist.loc[browser_shortlist.molecule_id == inspect_control.value].iloc[0]
    analog = training_table.loc[training_table.molecule_id == inspected.nearest_training_id].iloc[0]
    inspection_table = pd.DataFrame([{"record": inspected.molecule_id, "role": "held-out example", "SMILES": inspected.SMILES, "LogD": inspected.obs_LogD, "KSOL (µM)": inspected.obs_KSOL_uM, "Caco-2 Papp A>B": inspected["Caco-2 Permeability Papp A>B"], "Caco-2 efflux": inspected["Caco-2 Permeability Efflux"]}, {"record": analog.molecule_id, "role": "nearest training context", "SMILES": analog.SMILES, "LogD": analog.LogD, "KSOL (µM)": analog.KSOL, "Caco-2 Papp A>B": analog["Caco-2 Permeability Papp A>B"], "Caco-2 efflux": analog["Caco-2 Permeability Efflux"]}]).fillna("unknown / unavailable")
    (mo.vstack([mo.md(f"## 7. Inspect evidence behind a choice\n\n`{inspected.molecule_id}`: predicted LogD **{inspected.pred_LogD:.2f}**, measured LogD **{inspected.obs_LogD:.2f}**, measured KSOL **{inspected.obs_KSOL_uM:.1f} µM**. Nearest training context: `{analog.molecule_id}` at Morgan Tanimoto **{inspected.nearest_training_similarity:.3f}**; this is not transferred measurement evidence."), mo.ui.table(inspection_table, pagination=False)]) if caco_revealed else mo.md("Inspection opens after both evidence discoveries."))
    return


@app.cell
def _(caco_revealed, mo):
    return_control = mo.ui.button(label="8. Return to my proposal", kind="success")
    (return_control if caco_revealed else mo.md("Return becomes available after the additional evidence view."))
    return (return_control,)


@app.cell
def _(browser_shortlist, caco_revealed, mo, return_control, selected_candidate, selected_seed):
    returning = caco_revealed and bool(return_control.value)
    encouraging = browser_shortlist.loc[browser_shortlist.molecule_id.isin(["E-0021738", "E-0024328"]), ["molecule_id", "obs_LogD", "obs_KSOL_uM", "Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux"]]
    (mo.vstack([mo.md(f"## 8. Return with better judgment\n\nYou started from `{selected_seed['seed_id']}` and chose `{selected_candidate.candidate_id}`. Its exact structure remains `{selected_candidate.smiles}`. It is still unmeasured; the retrospective values do not belong to it."), mo.ui.table(encouraging, pagination=False)]) if returning else mo.md("Return restores your exact seed and candidate."))
    return (returning,)


@app.cell
def _(mo, returning):
    assay_control = mo.ui.radio(options={"Caco-2 permeability and efflux": "Caco-2 permeability and efflux", "Kinetic solubility": "Kinetic solubility", "HLM intrinsic clearance": "HLM intrinsic clearance"}, value="Caco-2 permeability and efflux", label="9. Choose the next question to test")
    (assay_control if returning else mo.md("Choose the next question after returning to your proposal."))
    return (assay_control,)


@app.cell
def _(assay_control, mo, pd, returning, selected_candidate):
    assay_reasons = {"Caco-2 permeability and efflux": "It can expose transport-related evidence outside the original LogD/KSOL objective.", "Kinetic solubility": "It would replace a computed context cue with an experiment for this exact proposal.", "HLM intrinsic clearance": "It asks a metabolism-related question omitted by the original two-property objective."}
    (mo.vstack([mo.md("## 9. Make the next experiment count"), mo.ui.table(pd.DataFrame([{"Candidate": selected_candidate.candidate_id, "Known": "computed descriptors; recorded seed-prompt and nearest-training context", "Unknown": "this candidate's experimental LogD, KSOL, Caco-2, clearance, and wider profile", "Next question": assay_control.value, "Why it could change the decision": assay_reasons[assay_control.value]}]), pagination=False), mo.md("We cannot explore everything. We can make the next experiment count.")]) if returning else mo.md("The final decision record appears after returning to your original proposal."))
    return


if __name__ == "__main__":
    app.run()
