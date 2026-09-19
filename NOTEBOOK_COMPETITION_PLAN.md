# The Perfect Molecule That Wasn't — molab notebook working plan

Updated 17 September 2026. This records the discussion, the evidence already collected, the ideas considered, and the current plan. It is a working research plan, not a claim that the final notebook or Galactica experiment already exists.

## The whole story in plain language

**Question:** When an ADMET predictor calls some molecules the winners, how much of that promise survives actual measurements?

We have real molecules for which both model predictions and laboratory measurements are available. We rank those molecules by the *predicted* combination of LogD and solubility, choose the supposed top candidates, then reveal how those same molecules *measured*. The visitor can see whether selecting more aggressively helps, where the model overpromises, and which actual structures account for the result.

Galactica-based Chemlactica then proposes a few new analogs of promising **training-set** molecules. These are proposals with no measured ADMET labels. The first experiment teaches why we should inspect evidence before calling a generated proposal a winner. The scientific claim comes from the measured-data experiment; the Galactica scene shows the next design step and its uncertainty.

One possible visitor journey: move the control to the top 2% of predicted molecules (43 in the current eligible set); see their predicted and measured positions side by side; click one to inspect the structure, prediction errors, and nearest measured training analog; then look at a small gallery of Galactica proposals labeled **measured ADMET unknown**.

The three states must remain visibly distinct throughout the notebook:

1. **Prediction:** a number supplied by a model.
2. **Measurement:** the actual released experimental result for that exact molecule.
3. **Proposal:** a new generated molecule with no experimental result yet.

## Why this is the chosen competition idea

The [competition](https://marimo.io/pages/events/notebook-competition-3) asks for one clear question about real drug-discovery data, a runnable marimo notebook, chemical validity, and interactions that teach something. It explicitly accepts curated OpenADMET data and values custom visualization over simply winning a model leaderboard. The selected ExpansionRx data are among its suggested sources. The submission deadline listed on the page is **4 October 2026, 11:59 PM PST**.

The user's intended angle is skeptical and inspectable: **are the apparent winners actually winning?** That also fits the style the user sees in Pat Walters' writing: check the data, splits, structures, and limits of impressive scores. The visualization should carry the explanation: connected predicted/observed plots, a pressure control, and an inspectable molecular evidence card. A decorative chemical-space plot or a model leaderboard by itself is insufficient.

The user's lab work should be visible without making the notebook a model advertisement. The chosen generator family is the user's **Galactica-based Chemlactica**, used as released. No fine-tuning of it is planned. Chemma, PMO-Dock, docking, and CheMeleon are not part of the current submission path.

## Where the idea came from and what changed

The attached *The Perfect Molecule That Wasn't* revised brief proposed the core measured-data experiment, three published benchmark model families, a selection-pressure control, a model-agreement view, and a molecular evidence card. It treated generation as optional and recommended no live training or generation in the submitted notebook. That brief is a source proposal, not an instruction that overrides the later conversation.

Our first local plan followed that idea. The user then asked to emphasize marimo's visualization features, Pat Walters' skeptical approach, and promotion of their own molecular-model work. The user specifically rejected CheMeleon, prefers the Galactica-based Chemlactica model used **without new fine-tuning**, and would rather avoid PMO-Dock and docking for this notebook. The current default therefore uses **one simple published ADMET baseline prediction table** for the measured-data reveal, plus **one Galactica-based generator** for the proposal gallery. The published baseline predictions are required to ask the original question; they are not another generator run in the notebook.

An important correction from our discussion: the cLogP-versus-measured-LogD comparison is **not** a test of Chemlactica. Chemlactica's released general checkpoints document a trained `[CLOGP]` tag, but that does not mean they saw ExpansionRx measured LogD. The paper reports a separate Lipophilicity fine-tuning experiment; that is not evidence that the released general checkpoint predicts this dataset's LogD. We briefly treated a cLogP/LogD comparison as the main story, but withdrew that interpretation after the user rightly challenged it. The original predicted-versus-measured experiment remains the plan.

## What has actually been run and verified

`DATA_AUDIT.md` gives the full provenance, file hashes, transformations, missingness, and structure checks. `scripts/first_experiment.py` reproduces the initial analysis and writes `outputs/first_pressure_plot.png`, `outputs/first_pressure_plot.pdf`, `outputs/first_pressure_data.csv`, and `outputs/audit.json`. These were computed locally from released data and saved predictions, not copied from a website. **No ADMET model was trained or run locally, no Chemlactica checkpoint was run, and no docking was run.**

- Official ExpansionRx split used in this pilot: **5,326 train** and **2,282 test** molecules. Of the test molecules, **2,160** have both numeric measured LogD and kinetic solubility (`KSOL`, µM). No missing test result was imputed.
- Pat Walters' benchmark molecule IDs and SMILES match the official split. Its `LogS` is a transformation of KSOL, `log10(KSOL in µM + 1) - 6`; the actual measurement is KSOL. Each of the three initially inspected model families has 25 saved predictions per eligible test molecule and endpoint. Those fits share one test set and are not 25 independent laboratory replications.
- All train/test structures parsed. No exact canonical structure appeared in both splits. The median nearest-training Morgan similarity among eligible test molecules is **0.636**; **242/2,160** are at least 0.8 similar to a training molecule. This is not a claim of generalization to entirely new scaffolds.
- The pilot used a **train-derived illustrative score**, not a universal definition of a good drug: LogD gets full credit inside the training complete-case interquartile range **1.4–2.9** and falls outside it; solubility gets half credit at the training median **125.5 µM** and rises with KSOL; their joint score is the geometric mean. The default was fixed using training data before inspecting the pilot test curve. UI changes to the score after seeing test results must be marked exploratory.
- At the strictest top **2% (43 molecules)**, the stored Morgan + LightGBM predictions averaged **0.825** on that joint score; those same molecules' measurements averaged **0.754**. Random selection from the same eligible cohort averages **0.581**. Thus selection helped in this pilot, while the predicted gain was larger than the measured gain. The pilot is descriptive and still needs uncertainty intervals, threshold-pass counts, and molecule-level inspection before a final claim.
- For historical context, the initial exploratory plot also included Monroe + TabPFN (**0.824 predicted, 0.811 measured**) and ChemProp + CheMeleon (**0.842 predicted, 0.795 measured**) at top 2%. These are audit results, not a decision to feature CheMeleon. The planned submission defaults to one simple baseline.
- A separate RDKit feasibility check found that cLogP and measured LogD differ substantially in these data: among **2,270** test molecules with numeric LogD, **1,323** differed by at least one log unit. Among **712** with cLogP in 1.4–2.9, **303** had measured LogD outside that range. `scripts/clogp_logd_feasibility.py` reproduces it. This is background about two different properties, **not a result about Chemlactica**, and is not the proposed notebook question.

## The first experiment: predicted winners versus measured winners

**Input:** the official ExpansionRx split and one fixed set of Pat Walters' saved Morgan + LightGBM predictions for LogD and LogS. Use the same **2,160 complete-case test molecules** at every selection level. The measured test labels are used only for evaluation, never to rank or tune the default selection.

**Procedure:** calculate the train-defined joint desirability from each molecule's predicted properties, sort the test molecules by it, and keep the top 50%, 25%, 10%, 5%, and 2%. For each selected group, calculate the mean predicted score, mean score from that *same group's* measurements, the number and fraction that pass explicit measured property thresholds, and uncertainty intervals suitable for the finite set of test molecules. Keep the random-selection reference and a clearly retrospective measured-best ceiling. Inspect individual errors and the nearest training analog rather than explaining an aggregate curve with speculation.

**Possible outcomes:** measured gains may track predictions, lag behind them, flatten, or remain strong even at the strictest selection. We report whichever occurs. A good average error metric alone does not answer this selection question. We must not retune the default score after seeing the held-out curve to force a dramatic result.

The original brief also proposed cross-model overlap and replicate-selection stability. These are useful **optional second lenses** if the single-baseline story needs them. Monroe's stored predictions could supply a comparator; CheMeleon should not be added against the user's preference. If the extra lens complicates the main visual, leave it out.

## Galactica-based Chemlactica's exact role

The [Chemlactica repository](https://github.com/yerevann/chemlactica) documents Galactica-based released checkpoints and structured generation prompts including `[SIMILAR]`, `[CLOGP]`, `[QED]`, and other properties. For this notebook, start with one verified **Galactica-based** checkpoint and a small set of promising **training** molecules as analog seeds. The first feasibility run should use documented similarity conditioning, fixed random seeds, prompt strings, decoding settings, and a small output budget. Compute validity, uniqueness, similarity to seed/nearest measured training analog, and simple RDKit descriptors. Do not add an unsupported `LogD` prompt or pretend cLogP is measured LogD.

Galactica's weights stay frozen. Candidate generation can happen **offline once**; the notebook loads a cached, attributed candidate table and interactively filters and displays it. The visitor does not need a GPU or a live model call. A separate reproducible generation script and exact checkpoint identifier should be included. The competition page allows molab GPU use, but it does not require live inference. A clean molab run must work without hidden files or model downloads.

The gallery is intended, but it has a quality gate: only include it if a tiny test produces valid, interesting analogs and the gallery helps explain the measured-data result. Otherwise the measured-data notebook is complete on its own. Generated compounds have **no measured LogD, KSOL, binding, safety, or synthesis result**. A nearest measured analog is context, not a transferable measurement. Scoring generated molecules with an ADMET predictor would require a separately callable, validated predictor; Pat Walters' saved test predictions cannot score new structures. That extra model work is not part of the simple first build.

## The marimo experience

1. **Hero view:** one selection-pressure control updates a predicted-versus-measured score curve, with selected count and uncertainty visible. The chart says plainly that 0–1 desirability is a chosen decision rule, not a drug probability.
2. **Linked chemical view:** selected molecules appear in predicted and measured LogD/solubility property space. Clicking one highlights the same molecule in both places, its change in position, and its contribution to the aggregate gap.
3. **Evidence card:** show the selected structure beside its nearest **training** analog, measured and predicted values with units, similarity, and limited structural review cues. A structural alert is a reason to inspect, not proof of toxicity or failure.
4. **Galactica proposal gallery:** small, visually separate cards for generated analogs, with validity/similarity/descriptors and a prominent **measured ADMET unknown** label. Do not place them on a measured-outcome plot as though their measurements existed.

The purpose-built interaction is moving from the aggregate curve to a specific structure and its evidence in one or two clicks. Use `marimo-chem-utils` where useful, with a small project-specific linked evidence view. Keep the design clear enough for a chemist to inspect claims and appealing enough to show marimo's reactive controls.

## Doubts, limits, and other ideas discussed

- **Does the Galactica model have to run in the notebook?** No. Cached offline generation plus a reproducible script is the preferred feasible design. An optional live demo should be added only if it proves reliable and quick on molab.
- **Can the model be used as is?** Yes for documented conditional *generation*; the exact checkpoint and prompt syntax still need a real feasibility run. The released general checkpoint is not verified as an ExpansionRx experimental LogD predictor. No user-model fine-tuning is planned.
- **What if the Galactica scene feels bolted on?** Keep it short, as the next proposal after the measured reveal, and omit it if it teaches nothing. Do not claim the measured test experiment validates generated molecules.
- **Could we do docking?** The user's Chemlactica paper reports docking-guided optimization. The lab's [PMO-Dock](https://github.com/YerevaNN/PMO-Dock) paper and code provide another docking and specificity direction. That would be a distinct, larger wildcard notebook involving protein preparation, scoring choices, and computational proxies rather than released ExpansionRx measurements. The user prefers not to use PMO-Dock here; docking is parked.
- **Could cLogP versus LogD be the notebook?** It gives a real descriptive contrast, but Chemlactica has no measured LogD labels for its generated molecules. It cannot establish whether the generator's outputs are experimental ADMET winners, so this is parked as background.
- **Should we use three benchmark models?** The attached brief proposed Morgan + LightGBM, Monroe + TabPFN, and ChemProp + CheMeleon to study disagreement. The user does not want CheMeleon. One simple baseline is the default; a second saved baseline is only a possible later comparison.
- **What does “limited to Galactica” mean in this plan?** Galactica-based Chemlactica is the only molecular generator and the only model checkpoint we would run ourselves. One published ADMET prediction table remains necessary for the original predicted-versus-measured experiment. If “no other model outputs at all” is intended, the scientific question must change, because the released Galactica checkpoint alone has no verified ExpansionRx LogD/KSOL predictions.
- **Which exact model name?** Earlier messages used “ChemBlaXP” and “Kimblef”; these were not verified as checkpoint identifiers. The implementation must record the exact released Galactica-based Chemlactica checkpoint and avoid silently treating those names as CheMeleon, Chemma, or an experimental LogD predictor.
- **Uncertainty and leakage:** the 25 saved fits do not make the test set 25 times larger; confidence intervals need an explicit method. High train/test similarity and shared chemical clusters limit the scope of generalization. Censored/missing test labels are excluded from the primary complete-case analysis. The score window was train-defined, but the pilot test result has already been seen, so later analysis changes must be labeled exploratory.

## Build sequence and gates

1. **Measured-result gate:** reproduce the single-baseline plot; add selected counts, measured threshold-pass rates, intervals, and a few chemically inspected examples. Confirm the conclusion remains honest at each selection pressure.
2. **Visualization gate:** build the marimo pressure control, linked predicted/observed scatterplots, and structure/nearest-analog card. A stranger should understand the result without reading the research brief.
3. **Galactica gate:** identify a released Galactica-based Chemlactica checkpoint, verify the actual prompt format, run a tiny frozen-weight analog-generation batch, and record provenance. Only then choose candidate cards for the notebook; no hand-picked unlogged replacements.
4. **Submission gate:** a fresh molab session runs end to end from public or bundled assets. Check chemistry and units, licenses and attribution, source revisions, AI disclosure, performance, and the short video explanation. The final message should show what the measurements establish and what remains unknown about new proposals.

## References and local artifacts

- [Competition brief and rules](https://marimo.io/pages/events/notebook-competition-3)
- [Official OpenADMET ExpansionRx dataset](https://huggingface.co/datasets/openadmet/openadmet-expansionrx-challenge-data)
- [Pat Walters' saved benchmark predictions](https://github.com/PatWalters/expansion-ml-comparison)
- [Pat Walters on data quality and evaluation](https://patwalters.github.io/Just-Because-You-Published-It-Doesnt-Mean-Its-Right/)
- [Pat Walters' marimo chemistry examples](https://patwalters.github.io/Practical-Cheminformatics-with-Marimo/)
- [Chemlactica paper](https://arxiv.org/html/2407.18897v1) and [repository](https://github.com/yerevann/chemlactica)
- [PMO-Dock repository](https://github.com/YerevaNN/PMO-Dock), considered but parked
- Attached source brief: `/Users/menuab/Downloads/The_Perfect_Molecule_MVP_Project_Brief_revised(1).docx`
- Local audit: `DATA_AUDIT.md`; analysis script: `scripts/first_experiment.py`; first plot: `outputs/first_pressure_plot.png`; cLogP check: `scripts/clogp_logd_feasibility.py`
