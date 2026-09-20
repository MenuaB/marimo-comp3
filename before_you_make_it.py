# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["altair==6.0.0", "duckdb==1.4.4", "marimo==0.24.2", "marimo-chem-utils==0.2.4", "numpy==2.4.3", "pandas==2.3.3", "rdkit==2025.9.6"]
# ///
"""Before You Make It — an enormous search, a few experiments, one decision.

This viewing-time notebook only consumes cached ChemLlama artifacts. It never
loads a model; saved ADMET predictions remain confined to released test data.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="full", app_title="Before You Make It")


@app.cell
def _():
    """Make the GitHub preview self-sufficient without changing local use.

    molab opens a single notebook file from GitHub.  The local project has
    helper modules, audited metadata, and a pinned generation artifact beside
    that file, so a preview needs to materialize those small project files on
    first run.  The larger audited source data remain downloaded by
    ``ensure_sources()`` with their recorded SHA-256 checks.
    """
    import sys
    import tempfile
    from pathlib import Path
    from urllib.request import urlopen

    local_root = Path(__file__).resolve().parent
    if (local_root / "scripts" / "notebook_data.py").is_file():
        project_root = local_root
    else:
        project_root = Path(tempfile.gettempdir()) / "marimo-comp3-github-main"
        github_root = "https://raw.githubusercontent.com/MenuaB/marimo-comp3/main"
        required_files = [
            "scripts/notebook_data.py",
            "scripts/experience_data.py",
            "config/notebook_analysis.json",
            "config/notebook_experience.json",
            "outputs/audit.json",
            "outputs/chemllama/chemllama-271948/manifest.json",
            "outputs/chemllama/chemllama-271948/candidates.json",
            "outputs/chemllama/chemllama-271948/raw_generation.jsonl",
        ]
        for relative_path in required_files:
            destination = project_root / relative_path
            if destination.is_file():
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(destination.suffix + ".tmp")
            with urlopen(f"{github_root}/{relative_path}") as response:
                temporary.write_bytes(response.read())
            temporary.replace(destination)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    from rdkit import Chem
    from rdkit.Chem import Draw
    from marimo_chem_utils import draw_molecule_grid
    from scripts.experience_data import active_budget_reference, evidence_accounting, load_pinned_generation, scale_landmarks
    from scripts.notebook_data import DATA, prepare, shortlist
    alt.data_transformers.disable_max_rows()
    return (
        Chem,
        DATA,
        Draw,
        active_budget_reference,
        alt,
        draw_molecule_grid,
        evidence_accounting,
        load_pinned_generation,
        mo,
        np,
        pd,
        prepare,
        scale_landmarks,
        shortlist,
    )


@app.cell
def _(mo):
    mo.md("""
    # Before You Make It

    ## An enormous search. A few experiments. One next decision.

    ### The idea, in plain language

    There are far too many possible molecules to test one by one. We first pick
    one molecule that scientists have already measured. Then we pick one **AI
    suggestion** based on it. That suggestion is only an idea — nobody has
    measured it yet.

    Next, we practice making a decision in a separate collection where the
    laboratory answers are already known. We let a model choose 50 molecules it
    thinks look good, then reveal what the lab actually measured. Finally, we
    return to *your* AI suggestion and choose the most useful next experiment.

    In short: **start with evidence → consider an AI idea → check how similar
    decisions held up in the lab → decide what to test next.**

    The numbered controls are the path. Three labels matter throughout:

    - **Computed** means calculated from a structure.
    - **Predicted** means a model's estimate.
    - **Measured** means a laboratory result.

    The laboratory results revealed in the middle belong to the separate
    practice collection, never to your unmeasured AI suggestion.
    """)
    return


@app.cell
def _(load_pinned_generation, prepare, scale_landmarks):
    cohort, pressure_metrics, preparation_manifest = prepare()
    candidates, generation_manifest, seed_records = load_pinned_generation()
    scale_steps = scale_landmarks()
    return (
        candidates,
        cohort,
        generation_manifest,
        preparation_manifest,
        scale_steps,
        seed_records,
    )


@app.cell
def _(mo):
    scale_action = mo.ui.radio(options={"Pull back": "pull", "Skip motion": "reduced"}, value="Pull back", label="1. Begin the scale view")
    mo.md("## 1. Start close enough to understand one possibility")
    scale_action
    return (scale_action,)


@app.cell
def _(alt, mo, np, pd, scale_action, scale_steps):
    scale_frame = pd.DataFrame(scale_steps)
    scale_frame["log10_count"] = np.log10(scale_frame["count"])
    scale_chart = alt.Chart(scale_frame).mark_circle(color="#38598b", opacity=0.82).encode(
        x=alt.X("log10_count:Q", title="Orders of magnitude (log₁₀ possibilities)", axis=alt.Axis(values=[0, 3, 6, 9, 11.22])),
        y=alt.Y("marks:Q", title=None, axis=None), size=alt.Size("marks:Q", legend=None, scale=alt.Scale(range=[100, 2300])),
        tooltip=[alt.Tooltip("count:Q", format=","), "label:N"],
    ).properties(height=190, title="Schematic compression: every mark is an aggregate landmark, never one molecule")
    final_landmark = scale_frame.iloc[-1]
    motion_copy = "The same landmarks are shown without animation." if scale_action.value == "reduced" else "One pull-back compresses the intervening orders of magnitude schematically."
    animation_mode = "scale-pullback" if scale_action.value == "pull" else "scale-still"
    landmark_markup = "".join(f"<span class='landmark l{index}'><b>{row['count']:,}</b><small>{row['label']}</small></span>" for index, row in scale_frame.iterrows())
    scale_motion = mo.Html(f"""<style>.scale-journey{{height:128px;position:relative;overflow:hidden;border:1px solid #d9e2ec;border-radius:12px;background:linear-gradient(90deg,#f7fbff,#edf6f5)}}.scale-journey .landmark{{position:absolute;top:37px;display:grid;gap:5px;text-align:center;color:#183153;opacity:1}}.scale-journey small{{width:130px;font-size:11px;color:#52616b}}.scale-journey b{{font-size:16px}}.scale-pullback .landmark{{animation:landmark 10s ease-in-out both}}.scale-pullback .l0{{left:4%;animation-delay:0s}}.scale-pullback .l1{{left:24%;animation-delay:1.8s}}.scale-pullback .l2{{left:44%;animation-delay:3.6s}}.scale-pullback .l3{{left:64%;animation-delay:5.4s}}.scale-pullback .l4{{left:80%;animation-delay:7.2s}}.scale-still .l0{{left:4%}}.scale-still .l1{{left:24%}}.scale-still .l2{{left:44%}}.scale-still .l3{{left:64%}}.scale-still .l4{{left:80%}}@keyframes landmark{{0%{{transform:scale(.35);opacity:0}}18%,100%{{transform:scale(1);opacity:1}}}}</style><div class='scale-journey {animation_mode}' aria-label='Scale landmarks from one schematic possibility to 166 billion GDB-17 molecules'>{landmark_markup}</div>""")
    mo.vstack([mo.md(f"""{motion_copy}

    GDB-17 enumerates about **{int(final_landmark['count']):,}** molecules with up to 17 atoms of C, N, O, S and halogens. At a hypothetical inspection rate of one molecule per second, without stopping, that is about **{final_landmark['hypothetical_years_at_one_per_second']:,.0f} years**. This is a scale comparison, not a claim about laboratory research time. [Source: GDB](https://gdb.unibe.ch/downloads/)."""), scale_motion, mo.ui.altair_chart(scale_chart), mo.callout("Now enter one real collection that people measured. ExpansionRx is not a highlighted subset of GDB-17.", kind="info")])
    return


@app.cell
def _(evidence_accounting):
    assay_accounting = evidence_accounting()
    return (assay_accounting,)


@app.cell
def _(mo, seed_records):
    seed_options = {f"{seed['seed_id']} · benchmark cluster {seed['cluster']}": seed["seed_id"] for seed in seed_records}
    seed_control = mo.ui.dropdown(options=seed_options, value=next(iter(seed_options)), label="2. Choose a real training seed / family")
    mo.md("## 2. Enter one measured collection")
    seed_control
    return (seed_control,)


@app.cell
def _(
    Chem,
    DATA,
    Draw,
    alt,
    assay_accounting,
    mo,
    np,
    pd,
    seed_control,
    seed_records,
):
    selected_seed = next(seed for seed in seed_records if seed["seed_id"] == seed_control.value)
    all_training = pd.read_csv(DATA / "expansion_data_train.csv").rename(columns={"Molecule Name": "molecule_id"})
    seed_row = all_training.loc[all_training.molecule_id == selected_seed["seed_id"]].iloc[0]
    strip = pd.DataFrame({"endpoint": assay_accounting["endpoint_columns"], "recorded value": [seed_row[column] for column in assay_accounting["endpoint_columns"]]})
    strip["evidence"] = np.where(strip["recorded value"].notna(), "recorded numeric value", "unknown / not numeric in ML-ready table")
    seed_image = Draw.MolToImage(Chem.MolFromSmiles(seed_row.SMILES), size=(360, 235))
    evidence_matrix = pd.DataFrame({"endpoint": assay_accounting["endpoint_columns"], "recorded values": [assay_accounting["per_endpoint"][column] for column in assay_accounting["endpoint_columns"]]})
    evidence_matrix["missing or non-numeric"] = assay_accounting["records"] - evidence_matrix["recorded values"]
    evidence_matrix_long = evidence_matrix.melt(id_vars="endpoint", var_name="evidence", value_name="molecule-endpoint cells")
    evidence_chart = alt.Chart(evidence_matrix_long).mark_bar().encode(y=alt.Y("endpoint:N", title=None, sort="-x"), x=alt.X("molecule-endpoint cells:Q", title="Released molecules"), color=alt.Color("evidence:N", scale=alt.Scale(domain=["recorded values", "missing or non-numeric"], range=["#2a9d8f", "#d9e2ec"]))).properties(height=235, title="The original record expands into uneven evidence coverage")
    mo.vstack([mo.md(f"""**{selected_seed['seed_id']}** is a real training molecule. Its measured LogD is **{selected_seed['measured_LogD']:.1f}** and kinetic solubility is **{selected_seed['measured_KSOL_uM']:.1f} µM**.

    Design → make → purify → measure → interpret is explanatory context, not a reconstruction of this molecule's history."""), mo.hstack([seed_image, mo.ui.table(strip, pagination=False)], widths=[0.42, 0.58]), mo.ui.altair_chart(evidence_chart), mo.md(f"Across both released splits, these nine challenge columns contain **{assay_accounting['recorded_values']:,} recorded numeric assay values** across **{assay_accounting['records']:,} molecules**. Of **{assay_accounting['possible_cells']:,} possible cells**, **{assay_accounting['missing_or_non_numeric']:,}** lack numeric ML-ready values; that includes unavailable evidence and excluded out-of-range values. Each filled cell is a piece of experimental evidence. A structure alone cannot fill the rest.")])
    return all_training, selected_seed


@app.cell
def _(candidates, selected_seed):
    seed_candidates = candidates.loc[candidates.seed_id == selected_seed["seed_id"]].sort_values("candidate_id", kind="stable").copy()
    return (seed_candidates,)


@app.cell
def _(draw_molecule_grid, generation_manifest, mo, seed_candidates):
    candidate_options = {f"{row.candidate_id} · prompt-seed similarity {row.similarity_to_seed:.2f}": row.candidate_id for row in seed_candidates.itertuples(index=False)}
    candidate_control = mo.ui.dropdown(options=candidate_options, value=next(iter(candidate_options)), label="3. Choose one recorded AI proposal")
    run_counts = generation_manifest["counts"]
    mo.vstack([mo.md(f"""## 3. Let AI suggest possibilities

    These are cached outputs from this seed prompt in the pinned ChemLlama-1B run, not live inference and not a claim of proven seed-conditioning semantics. The run recorded **{run_counts['raw']} raw samples**: **{run_counts['valid_unique']} unique valid**, **{run_counts['invalid']} invalid**, and **{run_counts['duplicate']} duplicates** after the recorded parser."""), candidate_control, draw_molecule_grid(seed_candidates, legend_column="candidate_id", max_to_show=8, image_size=(175, 140)), mo.ui.table(seed_candidates[["candidate_id", "similarity_to_seed", "nearest_training_id", "nearest_training_similarity", "evidence_status"]], pagination=True)])
    return (candidate_control,)


@app.cell
def _(Chem, Draw, candidate_control, mo, pd, seed_candidates):
    selected_candidate = seed_candidates.loc[seed_candidates.candidate_id == candidate_control.value].iloc[0]
    proposal_image = Draw.MolToImage(Chem.MolFromSmiles(selected_candidate.smiles), size=(360, 235))
    descriptor_rows = pd.DataFrame(list(selected_candidate.computed_descriptors.items()), columns=["computed descriptor", "value"])
    mo.vstack([mo.md(f"""### Your proposal: `{selected_candidate.candidate_id}`

    Known: RDKit-computed descriptors and nearest-training context (`{selected_candidate.nearest_training_id}`, Morgan similarity {selected_candidate.nearest_training_similarity:.3f}). Unknown: this exact proposal's experimental LogD, kinetic solubility, Caco-2, and wider assay profile."""), mo.hstack([proposal_image, mo.ui.table(descriptor_rows, pagination=False)], widths=[0.48, 0.52])])
    return (selected_candidate,)


@app.cell
def _(mo):
    retrospective_commit = mo.ui.button(label="4. Commit fifty retrospective choices", kind="success")
    mo.md("## Before deciding what to make, inspect a collection where experimental answers already exist")
    retrospective_commit
    return (retrospective_commit,)


@app.cell
def _(cohort, retrospective_commit, shortlist):
    committed = bool(retrospective_commit.value)
    active_shortlist = shortlist(cohort, 50)
    return active_shortlist, committed


@app.cell
def _(
    active_budget_reference,
    active_shortlist,
    alt,
    cohort,
    committed,
    mo,
    pd,
    preparation_manifest,
):
    if committed:
        commitment_comparator = active_budget_reference(cohort, 50)
        commitment_constants = preparation_manifest["constants"]
        points = alt.Chart(active_shortlist).mark_circle(size=62, opacity=0.74, color="#377eb8").encode(x=alt.X("pred_LogD:Q", title="Predicted LogD", scale=alt.Scale(domain=[-1.5, 5.5])), y=alt.Y("pred_KSOL_uM:Q", title="Predicted kinetic solubility (µM)", scale=alt.Scale(type="log", domain=[1, 2000])), tooltip=["molecule_id:N", alt.Tooltip("pred_LogD:Q", format=".2f"), alt.Tooltip("pred_KSOL_uM:Q", format=".1f")])
        target = alt.Chart(pd.DataFrame({"x1": [commitment_constants["logd_low"]], "x2": [commitment_constants["logd_high"]], "y1": [commitment_constants["ksol_median_um"]], "y2": [2000]})).mark_rect(opacity=0.13, color="#2a9d8f").encode(x="x1:Q", x2="x2:Q", y="y1:Q", y2="y2:Q")
        commit_view = mo.vstack([mo.md(f"""## 4. A limited budget forces a choice

    This separate held-out cohort has 2,160 paired released molecules. The fixed fifty are ranked by saved Morgan + LightGBM predictions only. The shaded region is the training-derived illustrative LogD/KSOL target — not a probability of drug success."""), mo.ui.altair_chart((target + points).properties(height=315, title="Prediction-only positions for the same 50 identities")), mo.md(f"The equal-budget random reference is ready: **{commitment_comparator['random_expected_passes']:.2f}** expected target passes in fifty. Observed outcomes remain hidden.")])
    else:
        commit_view = mo.callout("Commit the fixed fifty to enter the prediction-only retrospective cohort. Held-out outcomes remain hidden.", kind="info")
    commit_view
    return


@app.cell
def _(committed, mo):
    measurement_reveal = mo.ui.button(label="5. Reveal what the laboratory said", kind="warn")
    measurement_trigger_view = measurement_reveal if committed else mo.md("Commit the retrospective choices before revealing laboratory measurements.")
    measurement_trigger_view
    return (measurement_reveal,)


@app.cell
def _(
    active_budget_reference,
    active_shortlist,
    alt,
    cohort,
    committed,
    measurement_reveal,
    mo,
    pd,
    preparation_manifest,
):
    measurements_revealed = committed and bool(measurement_reveal.value)
    if measurements_revealed:
        reveal_comparator = active_budget_reference(cohort, 50)
        reveal_rows = pd.concat([
            active_shortlist[["molecule_id", "pred_LogD", "pred_KSOL_uM"]].rename(columns={"pred_LogD": "LogD", "pred_KSOL_uM": "KSOL_uM"}).assign(evidence="prediction"),
            active_shortlist[["molecule_id", "obs_LogD", "obs_KSOL_uM"]].rename(columns={"obs_LogD": "LogD", "obs_KSOL_uM": "KSOL_uM"}).assign(evidence="measurement"),
        ], ignore_index=True)
        reveal_target = pd.DataFrame({"evidence": ["prediction", "measurement"], "x1": [preparation_manifest["constants"]["logd_low"]] * 2, "x2": [preparation_manifest["constants"]["logd_high"]] * 2, "y1": [preparation_manifest["constants"]["ksol_median_um"]] * 2, "y2": [2000] * 2})
        reveal_points = alt.Chart(reveal_rows).mark_circle(size=45, opacity=0.68, color="#377eb8").encode(x=alt.X("LogD:Q", title="LogD", scale=alt.Scale(domain=[-2.5, 5.5])), y=alt.Y("KSOL_uM:Q", title="Kinetic solubility (µM)", scale=alt.Scale(type="log", domain=[1, 2000])), tooltip=["molecule_id:N", "evidence:N", alt.Tooltip("LogD:Q", format=".2f"), alt.Tooltip("KSOL_uM:Q", format=".1f")])
        reveal_region = alt.Chart(reveal_target).mark_rect(opacity=0.13, color="#2a9d8f").encode(x="x1:Q", x2="x2:Q", y="y1:Q", y2="y2:Q")
        reveal_chart = (reveal_region + reveal_points).facet(column=alt.Column("evidence:N", title=None, sort=["prediction", "measurement"])).properties(title="Same 50 IDs: predicted and released LogD/KSOL positions")
        measurement_view = mo.vstack([mo.md(f"""## 5. What did the laboratory say?

    The same fifty move from predicted to measured positions. **{reveal_comparator['selected_passes']}/50** meet the illustrative measured profile, versus **{reveal_comparator['random_expected_passes']:.2f}** expected for equal-size random selection (95% simulated range {reveal_comparator['random_low_95']:.0f}–{reveal_comparator['random_high_95']:.0f}). The selection is useful: mean illustrative score is **{active_shortlist.pred_score.mean():.3f}** predicted and **{active_shortlist.obs_score.mean():.3f}** measured. Random-shortlist variation is not assay uncertainty."""), mo.ui.altair_chart(reveal_chart)])
    else:
        measurement_view = mo.md("Laboratory outcomes remain hidden until the reveal; the shortlist was not retuned using them.")
    measurement_view
    return (measurements_revealed,)


@app.cell
def _(measurements_revealed, mo):
    caco_reveal = mo.ui.button(label="6. What else matters? Show Caco-2 evidence")
    caco_trigger_view = caco_reveal if measurements_revealed else mo.md("The second evidence reveal follows the laboratory reveal.")
    caco_trigger_view
    return (caco_reveal,)


@app.cell
def _(active_shortlist, alt, caco_reveal, measurements_revealed, mo, np):
    caco_revealed = measurements_revealed and bool(caco_reveal.value)
    caco_columns = ["Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux"]
    if caco_revealed:
        paired_caco = active_shortlist.dropna(subset=caco_columns).copy()
        target_passes = active_shortlist.loc[active_shortlist.measured_threshold_pass]
        paired_target_passes = target_passes.dropna(subset=caco_columns)
        paired_caco["initial_profile"] = np.where(paired_caco.measured_threshold_pass, "meets initial two-target profile", "misses initial profile")
        caco_chart = alt.Chart(paired_caco).mark_circle(size=72, opacity=0.78).encode(x=alt.X("Caco-2 Permeability Papp A>B:Q", title="Caco-2 Papp A>B (10⁻⁶ cm/s)"), y=alt.Y("Caco-2 Permeability Efflux:Q", title="Caco-2 efflux ratio"), color=alt.Color("initial_profile:N", title="Initial LogD/KSOL profile"), tooltip=["molecule_id:N", "initial_profile:N", alt.Tooltip("Caco-2 Permeability Papp A>B:Q", format=".2f"), alt.Tooltip("Caco-2 Permeability Efflux:Q", format=".2f")]).properties(height=310, title="Additional evidence for the unchanged original fifty")
        caco_view = mo.vstack([mo.md(f"""## 6. The answer can be right and the question incomplete

    **{len(paired_caco)}/50** have paired numeric Caco-2 values. Among **{len(target_passes)}** initial target passes, **{len(paired_target_passes)}** have paired Caco-2 evidence; the others are unknown, not failures. It met the two goals we gave it. Those were not all the questions we needed to ask."""), mo.ui.altair_chart(caco_chart), mo.ui.table(active_shortlist[["molecule_id", "measured_threshold_pass", *caco_columns]].fillna("unknown / unavailable"), pagination=True)])
    else:
        caco_view = mo.md("Caco-2 is deliberately a second discovery; do not infer it from the LogD/KSOL reveal.")
    caco_view
    return (caco_revealed,)


@app.cell
def _(active_shortlist, caco_revealed, mo):
    inspect_options = {f"{row.molecule_id} · predicted score {row.pred_score:.3f}": row.molecule_id for row in active_shortlist.itertuples(index=False)}
    inspect_default = next(label for label, molecule_id in inspect_options.items() if molecule_id == "E-0023839")
    inspect_control = mo.ui.dropdown(options=inspect_options, value=inspect_default, label="7. Inspect one retrospective example")
    inspect_trigger_view = inspect_control if caco_revealed else mo.md("Choose an example after the Caco-2 discovery.")
    inspect_trigger_view
    return (inspect_control,)


@app.cell
def _(
    Chem,
    Draw,
    active_shortlist,
    all_training,
    caco_revealed,
    inspect_control,
    mo,
    pd,
):
    inspected = active_shortlist.loc[active_shortlist.molecule_id == inspect_control.value].iloc[0]
    analog = all_training.loc[all_training.molecule_id == inspected.nearest_training_id].iloc[0]
    profile = pd.DataFrame([{"record": inspected.molecule_id, "role": "held-out example", "LogD": inspected.obs_LogD, "KSOL (µM)": inspected.obs_KSOL_uM, "Caco-2 Papp A>B": inspected["Caco-2 Permeability Papp A>B"], "Caco-2 efflux": inspected["Caco-2 Permeability Efflux"]}, {"record": analog.molecule_id, "role": "nearest training context", "LogD": analog.LogD, "KSOL (µM)": analog.KSOL, "Caco-2 Papp A>B": analog["Caco-2 Permeability Papp A>B"], "Caco-2 efflux": analog["Caco-2 Permeability Efflux"]}]).fillna("unknown / unavailable")
    inspection_view = mo.vstack([mo.md(f"""## 7. Inspect evidence behind a choice

    `{inspected.molecule_id}`: predicted LogD **{inspected.pred_LogD:.2f}**, measured LogD **{inspected.obs_LogD:.2f}**, and measured KSOL **{inspected.obs_KSOL_uM:.1f} µM**. Its nearest training context is `{analog.molecule_id}` at Morgan Tanimoto **{inspected.nearest_training_similarity:.3f}**; this is not transferred measurement evidence. Cluster {int(inspected.cluster)}; top-fifty inclusion **{int(inspected.selection_stability_count)}/25** saved fits (selection stability, not success probability)."""), mo.hstack([Draw.MolToImage(Chem.MolFromSmiles(inspected.SMILES), size=(310, 210)), Draw.MolToImage(Chem.MolFromSmiles(analog.SMILES), size=(310, 210))], widths=[0.5, 0.5]), mo.ui.table(profile, pagination=False)]) if caco_revealed else mo.md("Inspection opens after both evidence discoveries so one molecule can stay coherent across endpoints.")
    inspection_view
    return


@app.cell
def _(caco_revealed, mo):
    return_to_proposal = mo.ui.button(label="8. Return to my proposal", kind="success")
    return_trigger_view = return_to_proposal if caco_revealed else mo.md("Return becomes available after the additional evidence view.")
    return_trigger_view
    return (return_to_proposal,)


@app.cell
def _(
    Chem,
    Draw,
    active_shortlist,
    caco_revealed,
    mo,
    return_to_proposal,
    selected_candidate,
    selected_seed,
):
    returning = caco_revealed and bool(return_to_proposal.value)
    encouraging_examples = active_shortlist.loc[active_shortlist.molecule_id.isin(["E-0021738", "E-0024328"]), ["molecule_id", "obs_LogD", "obs_KSOL_uM", "Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux"]]
    return_view = mo.vstack([mo.md(f"""## 8. Return with better judgment

    You started from seed `{selected_seed['seed_id']}` and chose `{selected_candidate.candidate_id}`. It remains an unmeasured proposal: the retrospective measurements do not belong to it. The real examples beside it offer property-specific reasons for hope, not clinical claims."""), mo.hstack([Draw.MolToImage(Chem.MolFromSmiles(selected_candidate.smiles), size=(350, 225)), mo.ui.table(encouraging_examples, pagination=False)], widths=[0.48, 0.52])]) if returning else mo.md("Return restores your exact seed and candidate after the separate retrospective evidence journey.")
    return_view
    return (returning,)


@app.cell
def _(mo, returning):
    assay_control = mo.ui.radio(options={"Caco-2 permeability and efflux": "Caco-2 permeability and efflux", "Kinetic solubility": "Kinetic solubility", "HLM intrinsic clearance": "HLM intrinsic clearance"}, value="Caco-2 permeability and efflux", label="9. Choose the next question to test")
    assay_trigger_view = assay_control if returning else mo.md("Choose the next question after returning to your proposal.")
    assay_trigger_view
    return (assay_control,)


@app.cell
def _(assay_control, mo, pd, returning, selected_candidate):
    reasons = {"Caco-2 permeability and efflux": "It can expose transport-related evidence outside the original LogD/KSOL objective.", "Kinetic solubility": "It would replace a computed context cue with an experiment for this exact proposal.", "HLM intrinsic clearance": "It asks a metabolism-related question omitted by the original two-property objective."}
    decision_view = mo.vstack([mo.md("## 9. Make the next experiment count"), mo.ui.table(pd.DataFrame([{"Candidate": selected_candidate.candidate_id, "Known": "computed RDKit descriptors; recorded seed-prompt and nearest-training context", "Unknown": "this candidate's experimental LogD, KSOL, Caco-2, clearance, and wider profile", "Next question": assay_control.value, "Why it could change the decision": reasons[assay_control.value]}]), pagination=False), mo.md("We cannot explore everything. We can make the next experiment count. Choosing this question does not commission an assay or predict its outcome.")]) if returning else mo.md("The final decision record appears only after returning to your original proposal.")
    decision_view
    return


@app.cell
def _(mo, preparation_manifest):
    methods_constants = preparation_manifest["constants"]
    mo.accordion({"Methods and evidence boundaries": mo.md(f"The retrospective cohort contains 2,160 released test molecules with numeric LogD and KSOL. The illustrative training-derived target is LogD {methods_constants['logd_low']:.1f}–{methods_constants['logd_high']:.1f}, KSOL at least {methods_constants['ksol_median_um']:.1f} µM. Saved predictions test only released molecules; ChemLlama proposals retain unknown experimental fields.")})
    return


if __name__ == "__main__":
    app.run()
