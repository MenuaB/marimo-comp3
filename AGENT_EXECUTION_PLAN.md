# Before You Make It — competition notebook execution instructions

Updated 18 September 2026 after the user's approval of the revised ADMET story and H100 inference.

**Read [CUSTOM_VISUAL_STORY_EXECUTION.md](CUSTOM_VISUAL_STORY_EXECUTION.md) first.** The 20 September brief governs the revised story, custom widgets, state flow, native/portable parity, and acceptance tests. It supersedes conflicting narrative/UI instructions here and in `STORY_EXPERIENCE_REWORK.md`; the scientific, H100-only, provenance, and publishing requirements below remain in force.

Workspace: `/home/mbedrosian/code/marimo`, currently resolving to `/mnt/weka/mbedrosian/code/marimo`. Use `pwd -P` and paths accessible from compute nodes.

## 1. Assignment and explicit authorization

Complete the existing `before_you_make_it.py` as a polished, scientifically rigorous, native marimo notebook for the OpenADMET × marimo competition. The objective is a distinctive submission with a credible chance of winning: a compelling story whose discoveries come from inspectable chemistry and real ADMET evidence. Passing unit tests or making an animation alone is not completion.

The user explicitly authorizes you to:

- Edit the existing notebook, helpers, configuration, tests, and documentation.
- Build environments and install notebook, inference, testing, and browser-verification dependencies.
- Download the exact selected generator, **`yerevann/ChemLlama-1B`**.
- Submit and monitor Slurm jobs for actual inference on **H100 GPUs only**.
- Produce and integrate real cached generation outputs.
- Verify the full experience, start an authenticated local server, and prepare a portable submission bundle.

**A6000 devices are off limits, including for smoke tests, model loading, quantization, and fallback. Never use the `rtx` partition or `ap-rtx` node.** An idle A6000 is not permission to use it. If H100 resources queue, continue independent work and wait or report the actual scheduling blocker.

This brief supersedes the older measured-only stopping point, the Galactica-only model choice, and instructions to avoid inference dependencies or stop before generation. The previous plan is preserved in `docs/archive/AGENT_EXECUTION_PLAN_measured_only_2026-09-18.md`. Do not substitute `chemlactica-1.3b`, Chemma, CheMeleon, or another generator for ChemLlama-1B.

Do not request permission again for the authorized work above. Do not publish or submit the notebook, make a public repository, contact organizers, create accounts, or incur paid external-service charges. Prepare the concrete deliverable before any later publishing decision. Use an existing authorized private molab route if available; otherwise test the portable bundle locally and report the actual molab-verification gap.

Continue through real generation, implementation, scientific checks, browser interaction testing, and handoff. A plan, mockup, standalone HTML page, static export, empty candidate gallery, or seed-only handoff is not completion. If an external prerequisite blocks a required gate, finish independent work and state exactly what remains unverified.

## 2. Read first and preserve the foundation

Read applicable `AGENTS.md` instructions and inspect filesystem/git status. This directory was not a Git repository during the previous review; verify rather than assuming git is available. Read:

1. This brief, `before_you_make_it.py`, `scripts/notebook_data.py`, and `tests/test_analysis.py`.
2. `DATA_AUDIT.md`, `DATA_CONTRACT.md`, `outputs/audit.json`, and `scripts/first_experiment.py`.
3. `README.md`, `IMPLEMENTATION_STATUS.md`, and `CHEMLACTICA_HANDOFF.md` as descriptions of the earlier implementation, not current scope limits.
4. Older story/proposal files for background only; this brief governs conflicts.
5. The competition page/rubric and primary documentation for the selected checkpoint, endpoint definitions, and installed APIs.

Preserve the current notebook before substantial edits. Use version control if available, otherwise a dated non-overwriting backup. Preserve historical audits, scripts, pilot outputs, and source hashes. Do not delete untracked files, use broad resets, clear global caches, recreate a working environment without cause, or kill unrelated processes.

Prefer local changes, readable Python helpers, and thin launchers. Scientific settings, generation budgets, RNG settings, fingerprint definitions, and cache identity belong in small explicit config files. Avoid a new application framework or elaborate abstraction layer.

## 3. Thesis and scientific distinctions

Title: **Before You Make It**.

Central question: **When AI gives us a promising molecule, what evidence could change our decision to make or test it?**

Emotional arc: vast possibility → human effort → AI-generated possibilities → predicted promise → experimental investigation → earned hope → the next experiment.

Distinguish three things throughout:

- **Prediction error:** the measured property differs from its prediction.
- **Incomplete objective:** the molecule meets the selected targets, but another measured property changes the interpretation.
- **Missing evidence:** an unmeasured property remains unknown.

Do not call all three "AI failure." Do not claim most research or most AI suggestions fail. The current data show useful selection together with optimism, omitted properties, and uncertainty.

The chemical-space opening is brief motivation. A bounded reference such as GDB-17 can illustrate scale, with source and scope. Do not treat a 2D embedding as a literal map of molecular space, imply ExpansionRx is a subset of GDB-17, or turn an arbitrary ratio into humanity's measured coverage. Move quickly into a local lead-optimization setting with real compounds.

Keep model roles explicit: ChemLlama generates proposals; the existing Morgan + LightGBM table supplies saved ADMET predictions for released test molecules. Those measurements test those ADMET predictions, not new ChemLlama structures. Generated structures need their own experiments before claims of experimental success or failure.

## 4. Experience: seven main interactions, at most ten required actions

Aim for a complete guided path in roughly three minutes, with optional deeper exploration. Count actual required clicks/gestures, including navigation; do not disguise five sub-clicks as one interaction. Combine a meaningful action with advancing the story. Avoid mandatory quizzes, free-form setup, and repetitive molecule picking.

### Opening — automatic, short, and skippable

- Start with one molecular structure, pull back through a sourced sense of scale, then enter the real ExpansionRx collection.
- Keep this to roughly 10–15 seconds at most; offer immediate skip and reduced-motion access.
- Explain ADMET once and clarify that the chosen assays cover selected ADME properties, not potency or comprehensive toxicity/safety.
- Make experimental effort tangible through a short design–make–purify–measure–interpret schematic. Do not invent compound histories, synthesis times, labor hours, or costs.

### Interaction 1: Look inside one neighborhood

- Let the visitor select one of a few real training families/seeds. Update a structure grid, property view, and the seed's measured profile together.
- Explain SMILES, LogD, kinetic solubility, and units beside a real structure, without a long lecture.
- Use training observations here; keep held-out outcomes hidden until the relevant reveal.
- Treat benchmark clusters as algorithmic groupings, not automatically a shared scaffold or an actual optimization chronology.
- Carry the chosen seed through the proposal scene and final decision.

### Interaction 2: Let AI suggest the next steps

- Show genuine ChemLlama-1B proposals for the selected seed from the recorded run.
- Required default: cached outputs. Label the action "Explore AI proposals" or "Show recorded generation"; do not imply cached results are live inference.
- Show the seed and a small, inspectable page of generated neighbors together. Keep the whole valid set accessible.
- Report raw, invalid, duplicate, and unique-valid counts. Zero failures is an acceptable outcome; do not manufacture defects for drama.
- Display verified computed descriptors and independently checked conditioning only. Experimental values remain unknown.

### Interaction 3: Which fifty would we spend experiments on?

- Explicitly transition to the retrospective ExpansionRx cohort with saved predictions and real measurements.
- Default to **50 compounds**, not an unexplained top 2%/43. Optional deeper count budgets are 10 and 100.
- Use the fixed 2,160 paired test molecules and prediction-only ranking. The visitor commits to this shortlist.
- Show an understandable target region, selected structures, count, and predicted summary. Raw endpoints accompany the composite score.
- Keep the default training-derived rule fixed; do not retune it using revealed test outcomes.

### Interaction 4: What did the laboratory say?

- Move the same selected IDs from predicted to measured positions on fixed, readable axes. Preserve identity and selection through the transition.
- Show measured target passes, predicted/measured score, and equal-budget random-selection reference with correctly labeled variation.
- Keep misses and successes visible. Recompute the expected 41/50 target passes rather than hard-coding the story.
- Use a custom AnyWidget integrated with native marimo state and Python-derived downstream chemistry views.

### Interaction 5: Did we ask enough questions?

- Reveal measured Caco-2 permeability and efflux for the **same original shortlist**, with no reranking or silent denominator change.
- Expected paired numeric Caco-2 coverage: 38/50; among the 41 two-target passes, 33 have Caco-2 results. Distinguish numeric absence, raw censoring, and true unavailable evidence where possible.
- Show endpoint values and distributions with training context. Use a linked scatter/profile strip or similarly legible view, with units and missingness. Avoid radar charts that conceal scale and unknowns.
- Added cutoffs need an explicit project-specific or illustrative rationale. Label this new secondary analysis exploratory; do not select thresholds to produce a dramatic attrition rate.
- The lesson is that the original objective left properties out, not that a LogD/KSOL predictor was supposed to predict efflux.

### Interaction 6: Inspect evidence behind a choice

- One selection opens structure, nearest training analog, family, prediction error, wider measured profile, and training-fit selection stability together.
- Use a deterministic default example with its retrospective selection rule shown. Keep typical and encouraging examples accessible without mandatory extra steps.
- Show actual structures and similarity. Do not invent causal explanations for prediction errors, efflux mechanisms, or clinical outcomes.
- Show selection frequency across the 25 saved fitted-model variants, labeled **selection stability**, not a success probability or calibrated uncertainty.
- Retain family concentration context: the reference top fifty span 16 benchmark clusters.

### Interaction 7: What would you measure next?

- Restore the visitor's seed and genuine ChemLlama proposals using the same evidence layout.
- Let one action select a candidate or the next assay they would prioritize. Defaults should avoid a multi-step questionnaire.
- Clearly distinguish computed descriptors, predictions if a validated scorer is added, measurements for that exact compound, and unknowns.
- End beside real measured compounds with encouraging profiles. Their successes remain property-specific; novel generated compounds remain proposals.
- Do not imply the visitor commissioned an experiment or experimentally validated ChemLlama.

Optional pressure curves, additional budgets, full tables, methods, and robustness comparisons come after or beside the guided story. The main notebook must run without GPU access or model inference at viewing time and remain understandable without motion or hover.

## 5. Pinned sources and regression anchors

Use source identities and SHA-256 values in `outputs/audit.json`:

- Official ExpansionRx revision: `6b898ccc43d10d25b230fb09e22a6e30c30022b5`.
- Benchmark revision: `06582771d48af8096f6b05a5a247b177189a8fa4`.
- Files: `expansion_data_train.csv`, `expansion_data_test.csv`, `expansion_data_raw.csv`, `expansion_log_scaled.csv`, `predictions_all.parquet`.

Verify checksums before use; fetch absent files atomically from pinned URLs. Investigate mismatches instead of silently replacing files. Recompute the following from those files; these are checks, not permission to force matching outputs:

| Quantity | Reference |
| --- | --- |
| Official train / test molecules | 5,326 / 2,282 |
| Paired training / paired test LogD+KSOL | 4,934 / 2,160 |
| Test records outside paired cohort | 122 |
| Predictions per eligible molecule and endpoint | 25 distinct repeat/fold keys |
| Training-derived LogD window / KSOL midpoint | 1.4–2.9 / 125.5 µM |
| Top 50 predicted / measured mean score | 0.8228211410121915 / 0.7485762984188178 |
| Top 50 measured target passes | 41 |
| Top 10 predicted / measured mean score | 0.8357651396829253 / 0.7652232042260241 |
| Top 10 measured target passes | 8 |
| Whole-cohort target-pass fraction | 0.41898148148148145 |
| Expected random passes in fifty | approximately 20.9491 |
| Top 50 paired numeric Caco-2 coverage | 38 |
| Caco-2 coverage among 41 target passes | 33 |
| Top 50 benchmark clusters | 16 |
| Union of 25 per-fit top-50 lists | 256 molecules |
| Ensemble top-50 inclusion across fits | minimum 4, median 15, maximum 25 out of 25 |
| Ensemble top-50 members in all 25 lists | 1 |
| Per-fit overlap with ensemble top 50 | minimum 21, median 29, maximum 36 |
| Cohort nearest-training similarity | median 0.6363636363636364; 242 at least 0.8 |
| Benchmark clusters spanning train/test | 59 |

For ensemble selection, average endpoint predictions across fits first, then compute the score. Do not average per-fit scores instead. Sort descending score, ascending molecule ID, stably. For selection stability, pair LogD and LogS on the **same repeat/fold keys**, compute that fit's score, and select its fifty. Validate IDs, SMILES, finite predictions, matching `y_true`, and complete distinct keys before aggregation.

Preserve historical top-10%-and-top-2% regression tests although the UI changes to count budgets.

### Score and transforms

Preserve the audited default:

```text
stored_LogS = log10(KSOL_uM + 1) - 6
distance = max(1.4 - LogD, LogD - 2.9, 0)
logd_component = exp(-distance / 0.75)
KSOL_uM = max(10 ** clip(stored_LogS + 6, -6, 8) - 1, 0)
score = sqrt(logd_component * KSOL_uM / (KSOL_uM + 125.5))
```

The measured target-pass diagnostic is `1.4 <= LogD <= 2.9` and `KSOL_uM >= 125.5`. This is an illustrative training-derived profile, not a universal medicinal target or a drug-success probability. Invert mean stored LogS only after averaging; do not call that arithmetic mean predicted solubility. Preserve zero values and explain display transforms.

### Examples to verify

| Molecule | LogD | KSOL, µM | Caco-2 Papp A>B, 10^-6 cm/s | Efflux ratio | HLM CLint, mL/min/kg |
| --- | ---: | ---: | ---: | ---: | ---: |
| E-0023839 | 1.6 | 275 | 0.80 | 31.1 | 23.6 |
| E-0021738 | 2.2 | 288 | 26.72 | 0.92 | 7.8 |
| E-0024328 | 2.2 | 287 | 14.48 | 1.24 | 15.8 |

These are retrospective illustrations, not drugs proven to succeed/fail. The first meets the initial two targets but differs substantially on other measured endpoints. Explain example selection and retain the full distribution.

`E-0020691` is a reference large score overestimate in the top fifty: predicted LogD approximately 1.869 versus measured -1.8; predicted KSOL approximately 237.8 µM versus measured 308 µM. Use it to distinguish an endpoint prediction error from an omitted-property concern.

## 6. Scientific requirements

1. Keep observations out of ranking and rule fitting. All newly developed analyses are retrospective/exploratory; do not imply preregistration or prospective blinding.
2. Show individual properties alongside scores so readers can see which endpoint changes a decision.
3. Calculate equal-size random-shortlist distributions without replacement from the same eligible cohort. Defaults: seed `20260918`, 2,000 draws; make these explicit config/cache fields. An exact hypergeometric interval for pass counts is also valid if documented and checked.
4. Distinguish random-shortlist variation, variability across training fits, assay uncertainty, and population uncertainty. The 25 fits share test molecules and overlapping training sets; they are not independent assay replications.
5. Default to descriptive fixed-cohort findings plus stability. Any broader bootstrap intervals need a stated estimand, cluster assumptions, resampling unit, and reranking rule; do not assume chemically related molecules are independent.
6. Keep Caco-2 on the original shortlist with explicit coverage and no implicit imputation. Observed-subset results do not automatically describe missing outcomes.
7. Do not restrict the analysis to complete cases across all nine assays: the reference top fifty have none complete across all nine. Preserve assay-specific availability.
8. Audit raw inequality labels. A bound is not an exact measurement; preserve its operator and distinguish censoring from missingness. Do not invent assay ceilings or floors from a numerical pile-up alone.
9. Confirm units and reported conditions from primary sources. Do not invent pH/incubation time. Kinetic solubility is not thermodynamic solubility; cLogP is not experimental LogD; efflux does not by itself establish transporter mechanism or clinical failure.
10. Search nearest neighbors across **all valid official training structures**, including incomplete assay records. Keep their own missing values visible. The diagnostic Morgan bit fingerprints are distinct from the baseline's count-fingerprint model features.
11. Report shared chemical families. No exact canonical overlap does not establish scaffold novelty or broad extrapolation.
12. Detect exact generated-compound matches to the released data using documented stereochemistry-aware identity rules. Report rediscoveries; do not call them novel or treat selected exact matches as an unbiased wet-lab validation of generation. Pretraining overlap remains unknown unless actually audited.

## 7. Repair known defects before expanding the notebook

Verify and fix:

- **Cache reuse:** `FRACTIONS` is a tuple in memory and a list in the JSON manifest, so identity comparison currently misses. Use a canonical JSON-compatible identity; test an actual warm-cache hit. Include analysis/score settings, random draw count, relevant versions, fingerprints, schema, and source hashes. Handle incomplete/corrupt caches and write safely.
- **Analog lookup:** the cache searches all training structures but the card searches complete cases. `E-0022859` can crash because analog `E-0017238` is omitted. Join against all training records and display missing assays.
- **Silent rendering cap:** `data.slice(0,250)` limits drawing/clicking under larger declared counts. Render the whole active set or clearly disclose visual sampling without altering analytic denominators.
- **Missing reference bands:** the pressure plot describes bands it does not draw. Render the reference/interval or correct the presentation.
- **Premature outcomes:** downstream family/evidence views can expose held-out measurements before Reveal. Gate all relevant values and retrospective examples by the presentation state.
- **Disconnected selections:** wire meaningful table/grid selections to the actual evidence card or remove misleading selection controls.
- **Widget cleanup/state:** remove model event listeners and animation callbacks; handle scrubbing, reduced motion, and seed/budget changes without stale selection or duplicate observers.
- **Validation gaps:** replace superficial leakage/cache checks with meaningful behavior checks; validate actual distinct repeat/fold keys rather than only row counts.

## 8. ChemLlama checkpoint, environment, and prompt preflight

### Identity

- Exact model: `yerevann/ChemLlama-1B`.
- Observed revision: `f3f7fc0aa3ad48799d4cc89e3ed822c1d016614e`.
- Observed metadata: public/ungated, 1,235,814,400 float32 parameters, `LlamaForCausalLM`, 2,048 configured context length, and no README/model card at that revision.
- Recheck metadata and pin the observed revision when available. If a different revision is necessary, record the reason and exact ID before running; never silently follow `main`.
- Do not infer training corpus, supported tags, license, or conditioning semantics from the family name. Record evidence and missing documentation honestly.

### Environments

- Inspect/reuse the notebook `.venv`, currently Python 3.13 with pinned marimo/RDKit dependencies.
- Create a separate `.venv-inference` with a compatible Python, CUDA PyTorch, Transformers, tokenizer dependencies, and validation chemistry dependencies.
- Inspect config/tokenizer compatibility and authoritative package docs. The export records Transformers 5.x; do not blindly downgrade past supported RoPE/tokenizer fields.
- Record direct dependencies and resolved versions separately for notebook, inference, and tests. Do not install the model stack into the required viewing environment.
- Put weights in an explicit shared-filesystem cache, not the portable bundle. Do CPU metadata/tokenizer checks before expensive allocations.

### Prompt verification

1. Inspect tokenizer settings, generation config, export/training code, and an exact working inference example if present in authorized local/upstream sources.
2. Older Chemlactica `[SIMILAR]`, `[CLOGP]`, and `[START_SMILES]` templates are leads to investigate, not proven ChemLlama compatibility. Token presence alone does not prove trained support.
3. Verify BOS/EOS, prompt framing, stop conditions, padding, input/output lengths, and generated-SMILES extraction. Never parse a seed echoed in the prompt as a new generated candidate.
4. Prefer verified seed/similarity conditioning. Independently compute achieved similarity with the conditioning fingerprint definition; distinguish that from the notebook's diagnostic fingerprint if different.
5. Small, logged prompt probes are allowed. Preserve attempted formats and outputs. If semantics remain unresolved, continue independent notebook work; ask one concise model-specific clarification only after local/upstream evidence and small probes cannot resolve it.
6. Do not invent experimental LogD, KSOL, or Caco-2 tags. Do not assume a base model supports conversational instructions or a chat template.

## 9. Slurm: H100-only execution

Reinspect `sinfo`, partition/account/QOS access, and shared paths before submission. Planning-time configuration advertised `gpu:h100` in several partitions, including `research`, `defq`, and `all`. `rtx`/`ap-rtx` advertises `gpu:rtx_a6000:1` and is forbidden.

Request **one typed H100**, not generic `gpu:1` and not a whole node. Use modest walltime/CPU/memory and increase only after evidence of need. Adapt this template after checking access:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=chemllama-1b-pilot
#SBATCH --partition=research
#SBATCH --gres=gpu:h100:1
#SBATCH --exclude=ap-rtx
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --output=/mnt/weka/mbedrosian/code/marimo/outputs/chemllama/slurm/%x-%j.out
#SBATCH --error=/mnt/weka/mbedrosian/code/marimo/outputs/chemllama/slurm/%x-%j.err
set -euo pipefail
cd /mnt/weka/mbedrosian/code/marimo
srun .venv-inference/bin/python scripts/generate_chemllama.py \
  --config config/chemllama_generation.json \
  --run-id "chemllama-${SLURM_JOB_ID}"
```

Create log directories before submission. Add account/QOS only when verified for this user. Keep launcher logic thin; configuration, parsing, generation, guards, and validation belong in Python.

Mandatory preflight **before loading weights onto a device**:

- Require a Slurm allocation for GPU inference; respect the allocation's visible devices.
- Require CUDA and inspect every device to be used. Reject names not identifying H100, explicitly rejecting A6000.
- Record job ID, node, resources, GPU name/UUID, driver, CUDA/PyTorch versions, dtype, and visible-device count.
- Do not override `CUDA_VISIBLE_DEVICES` to escape the allocation or use an unrestricted device map across unintended hardware.
- BF16 is a reasonable H100 starting point subject to compatibility and a real output smoke test. Record precision changes; do not silently quantize.
- Run tensor inference only inside the allocated job; no login-node GPU shortcuts or A6000 fallback.

Use `sbatch --parsable`, save the returned job ID/config, and monitor with bounded `squeue`/`sacct`/log checks. A disappeared queue entry is not success: inspect final exit state and artifacts. Work on the notebook during queue waits. Do not spam-submit duplicates or cancel unrelated jobs. Diagnose failures before retrying this task's jobs and preserve previous logs.

## 10. Generation experiment and output contract

### Budget

- Reuse the three distinct-cluster official-training seeds in the existing preparation manifest after validating their selection. Do not replace them with held-out winners.
- First run 4–8 raw smoke samples total to check framing, extraction, H100 execution, and output recording.
- Then run **3 seeds × 32 raw samples = 96 raw samples** for the main pilot.
- Put seed list, sample count, RNG scheme, temperature, top-p/top-k if used, max tokens, batch size, dtype, and prompt template in configuration.
- Preserve diagnostic attempts. Default total cap: 256 raw samples across smoke/pilot/diagnostics; any increase needs a concrete reason recorded before the larger run. Do not silently reroll until an attractive gallery appears.
- This is a generation feasibility experiment, not ChemLlama fine-tuning or a new optimization benchmark.

### Artifacts and validation

Create a raw append-only generation log, run manifest, valid-candidate table, and rejection/duplicate summary. Retain:

```text
generation_run_id, raw_sample_index, seed_id,
checkpoint_id, checkpoint_revision, exact_prompt,
random_seed_or_rng_state_scheme, decoding_settings,
raw_generated_text, extracted_smiles,
validation_status, rejection_reason,
canonical_isomeric_smiles, duplicate_of,
similarity_to_seed, nearest_training_id, nearest_training_similarity,
computed_descriptors_with_names_units_and_tool_versions,
exact_dataset_match_id_and_split_if_any,
evidence_status
```

- Assign stable IDs and preserve raw-sample provenance after deduplication.
- Document parsing, stereochemistry, salt/fragment, and identity policies. Parseable SMILES do not establish synthesizability or suitability.
- Do not neutralize, remove fragments, or alter tautomers/stereochemistry without recording the change and rationale.
- Use a concise useful descriptor set: molecular weight, RDKit cLogP, TPSA, HBD/HBA, and similarity, for example. Add QED/SA only with correct definitions and a story-specific purpose.
- Novel unmeasured proposals have experimental LogD, KSOL, Caco-2, and other measurements as JSON `null`, never zero or NaN.
- Exact rediscoveries can link to known measurements for that exact structure in a separately labeled state. They are not novel proposals or unbiased validation of the generator.
- Never transfer an analog's measurements or saved test predictions to a generated structure.
- Hash the candidate artifacts and record full provenance, actual runtime, and device use.
- Read the actual records before integration. If outputs are few/invalid, report and diagnose the real result; do not invent compounds or substitute a model to meet a visual quota.

## 11. Optional ADMET scorer and robustness extensions

Required core: published saved ADMET predictions for retrospective molecules; computed descriptors/analog evidence and unknown experimental values for novel proposals.

A stronger extension is permitted if it can be completed without jeopardizing the core: fit a small Morgan + LightGBM ADMET scorer using training-only validation/settings, freeze its recipe, evaluate retrospectively on the official test split, and then apply that same scorer to generated candidates. This is ADMET model fitting, not ChemLlama fine-tuning.

If adding it:

- Record features, transforms, folds, seeds, serialized models, and environment. Keep settings selection within training data and disclose prior test exploration.
- Use the **same callable scorer** in its measured reveal and proposal scoring. Do not attach the published ensemble's reference results to a newly trained model.
- Keep the published-baseline analysis as a reproducibility reference and clearly identify the active model.
- Validate endpoint quality and decision behavior; show all actual results. Candidate outputs remain predictions with applicability context, not measurements or calibrated success probabilities.
- Do not claim measured optimization gains for generated compounds without experimental evidence.

This is optional and must not displace actual ChemLlama inference, Caco-2 analysis, or browser validation. A deeper comparison with already cached Monroe predictions is also optional, to check whether a pattern is specific to the simple baseline. Do not add CheMeleon, docking, PMO-Dock, another generator, a model leaderboard, or ChemLlama fine-tuning.

## 12. Native marimo and visual implementation

- Improve `before_you_make_it.py`; do not replace it with a standalone HTML/React app.
- Native marimo controls own seed, budget, family, and inspection state. Scientific calculations remain in Python cells/helpers. Use supported `marimo-chem-utils` grids/tooltips and RDKit depictions.
- Extend the existing AnyWidget as a reusable evidence reveal with stable IDs, explicit evidence transitions, and selected-ID output to downstream Python cells.
- Keep animation frames in JavaScript. Sync meaningful selections/committed states, not 60 progress updates per second through the reactive graph.
- Prefer upstream controls → immutable payload → selected IDs → downstream evidence. Prove any bidirectional coordination does not loop or reset state unexpectedly.
- Use fixed, data-derived axes for each reveal, readable labels/units, target regions, trails, and endpoint identity. Label interpolated states as visual transitions, not experiments.
- Cache joins, fingerprints, neighbors, generation, and expensive depictions. View changes must not rerun inference or rebuild the scientific cache.
- Paginate structure rendering while calculating over the full declared cohort. Distinguish no selection from an empty subset and disclose any actual visual sampling.
- Align selected IDs across plots, grids, tables, broader profiles, stability, and analog cards. Selection affordances must work.
- Distinguish computed / predicted / measured / unknown with labels as well as color. Missing evidence is not a zero or failure.
- Support keyboard/table access, touch, narrow layouts, reduced motion, replay, and scrubbing. Essential information must not require hover.
- Keep methodological detail accessible in concise expanders and source links. Keep package limitations and implementation commentary in developer docs, not the main narrative.
- Credit Expansion Therapeutics/OpenADMET, benchmark authors, marimo-chem-utils, and AI assistance accurately. Do not imply judge endorsement.

## 13. Deliverables and portability

Use a simple structure, adapting names only for concrete implementation reasons:

```text
before_you_make_it.py
scripts/notebook_data.py
scripts/generate_chemllama.py
scripts/prepare_candidates.py                  # only if separation helps
scripts/run_chemllama_h100.sbatch
config/notebook_analysis.json
config/chemllama_generation.json
requirements-notebook.in / requirements-notebook.lock.txt
requirements-inference.in / requirements-inference.lock.txt
requirements-test.in                          # if needed
tests/test_analysis.py
tests/test_generation_contract.py
outputs/chemllama/<run_id>/...
outputs/chemllama/slurm/...
outputs/notebook_validation/<validation_id>/...
README.md
DATA_CONTRACT.md
CHEMLACTICA_HANDOFF.md                         # update to actual run report
IMPLEMENTATION_STATUS.md
docs/submission_walkthrough.md
```

Do not create modules merely to match this tree. Choose candidate formats the lightweight notebook can load without the inference stack. Keep full raw logs separate from the small presentation table.

Bundle the notebook, required helpers, config, attribution, source manifests, and genuine small candidate artifacts. Resolve data paths relative to the bundle. Include pinned-data bootstrap or permitted bundled inputs; obey licenses. Do not depend on private absolute paths, Slurm, model weights, or a GPU at viewing time. Test the exact bundle, not only the working directory.

Update current docs to remove obsolete no-inference instructions while preserving historical facts as history. Do not state generation or tests succeeded until they actually did.

## 14. Required validation gates

### A. Scientific and data checks

Run **`pytest`** as required by repository instructions. Existing unittest-style tests can be collected by pytest. Add tests for scientific behavior and identified defects, not cosmetic implementation details:

- Source hashes, unique joins, cohorts, label/structure agreement, distinct repeat/fold completeness, finite predictions, and old/new budget regressions.
- Observed-value perturbation through the actual analysis path cannot change prediction ranking or training-derived constants; simply sorting a precomputed score column is not sufficient leakage protection.
- Nested selected IDs, threshold boundaries, zero/transform handling, missing/censored semantics, and consistent denominators.
- Caco-2 coverage/example values and no silent reranking or all-assay complete-case filtering.
- Per-fit top-k selection/stability and mean-endpoint-then-score ensemble definition.
- All-training analog lookup, including incomplete analog `E-0017238`, deterministic ties, and split provenance.
- Canonical cache identity, verified second-call cache hit, and invalidation after relevant config changes.
- Prompt/continuation separation; real raw-log/candidate linkage; invalid/duplicate accounting; exact-match handling; JSON nulls.
- H100 device guard accepts an H100 and rejects A6000/non-H100 **before model loading**, tested with mocks. Do not access an A6000 to test rejection.

### B. Actual generation

- At least one genuine ChemLlama-1B job completes on an allocated H100.
- Manifest contains job ID, exact revision, GPU/runtime details, prompt/config, and full raw-output accounting.
- Validate actual artifacts, not only job exit code. Preserve failed/pending/retried job records honestly.

### C. Notebook execution

Check the installed CLI and run supported equivalents of:

```bash
.venv/bin/python -m pytest
.venv/bin/marimo check before_you_make_it.py
.venv/bin/marimo export html before_you_make_it.py --no-sandbox \
  -o outputs/notebook_validation/VALIDATION_ID/notebook_snapshot.html
```

Create a real run directory in place of `VALIDATION_ID`; preserve earlier validation artifacts. Inspect runtime/cell errors and export content rather than only file existence.

### D. Live browser walkthrough

Use browser tools or install an isolated automation runtime where needed. The previous absence of browser tooling does not justify skipping an attempt. Test the **live marimo server and Python kernel**, not only static HTML or a detached widget.

1. Fresh load: understandable first screen, readable real structure, skippable intro, and no prematurely exposed test outcomes.
2. Family/seed: native grid/profile and genuine cached proposal gallery follow the selected training seed.
3. Budget: default 50 and optional 10/100 produce expected IDs/counts and clear stale selections.
4. Reveal: preserved molecule identity, correct Python counts/means, actual reference/bands with accurate labels.
5. Caco-2: same shortlist, correct 38/50 coverage, unknowns visible, and example profiles correct.
6. Point selection: a custom-widget action changes the actual downstream Python evidence card to the same ID. Verify a table/keyboard alternative too.
7. Family/stability/analog: correct memberships/counts; empty subsets and incomplete neighbors do not crash.
8. Return to proposal: selected context retained; experimental fields remain unknown except explicitly labeled exact rediscoveries.
9. Replay, scrub, reduced motion, changes during motion, and repeated interactions do not leak listeners, reset unexpectedly, or trigger inference.
10. Desktop/narrow layout: no clipped structures, overlapping labels, or essential hover-only controls. Count required guided actions: at most ten.
11. Kernel/server restart: key interactions still work without hidden execution order or manual out-of-order execution.

Save screenshots of major evidence transitions and a compact interaction-test log. Screenshots alone do not prove reactivity. If an external access boundary blocks a step, state the exact blocker and mark the gate incomplete.

### E. Clean runtime and bundle

- Test a separate clean cache/bundle copy without deleting the working cache.
- Exercise the documented bootstrap from the bundle directory.
- Verify default startup performs no model inference/download and needs no GPU, Slurm, secrets, or private absolute paths.
- Measure cold start, warm cache reuse, and representative interaction latency on the actual machine. Fix measured bottlenecks without changing cohort denominators.
- Use an available authorized private molab route to test there. If unavailable, report local portability checks separately from unverified molab execution.

## 15. Work order and final handoff

1. Preserve current work; inspect environments and H100 partition/account access.
2. Repair existing defects and establish top-50, Caco-2, stability, and neighbor computations.
3. Verify model/prompt framing; build the inference environment and H100 preflight.
4. Submit the small smoke job, inspect outputs, then run the 96-sample H100 pilot.
5. Build the seven-interaction notebook while jobs queue/run, without depending on invented candidate data.
6. Validate and integrate real candidates and the return-to-proposal ending.
7. Finish scientific tests, live browser walkthrough, restart/clean-bundle checks, and documentation.
8. Consider optional scorer/Monroe work only after core generation and experience succeed; revalidate affected claims.

Handoff must include:

- Notebook, README, evidence contract, generation report, and implementation-status links.
- Actual authenticated local launch URL/process status when available; no access tokens in committed docs.
- Exact model revision, successful H100 Slurm job ID(s), raw/valid/unique counts, and artifact locations.
- Main measured findings and coverage, without implying wet-lab validation of new proposals.
- Which data, browser, clean-runtime, and molab checks passed; precise remaining limitations.
- A short submission-video outline in `docs/submission_walkthrough.md` demonstrating the working story. Do not publish or submit it.

If an external prerequisite blocks a required part, complete independent authorized work and report the blocker. Do not replace real generation with a future-work paragraph or static export with a claim of interaction verification.

## 16. Primary references

- [Competition](https://marimo.io/pages/events/notebook-competition-3)
- [Rubric](https://docs.google.com/spreadsheets/d/1xEd-njH43jTWQfr-2wjXULhiGKXl6zEvmKIobWOO8Ks/edit?gid=620363524)
- [Official data and endpoint definitions](https://huggingface.co/datasets/openadmet/openadmet-expansionrx-challenge-data)
- [Pinned benchmark](https://github.com/PatWalters/expansion-ml-comparison/tree/06582771d48af8096f6b05a5a247b177189a8fa4)
- [Chemistry components](https://github.com/PatWalters/marimo_chem_utils)
- [Overview/detail workflows](https://patwalters.github.io/Practical-Cheminformatics-with-Marimo/)
- [Evaluation concerns](https://patwalters.github.io/Just-Because-You-Published-It-Doesnt-Mean-Its-Right/)
- [Models and experimental allocation](https://patwalters.github.io/Response-to-Peter-Kenny/)
- [Selected generator](https://huggingface.co/yerevann/ChemLlama-1B)
- [Older Chemlactica code — verify compatibility](https://github.com/YerevaNN/ChemLactica)
- [Bounded chemical-space reference](https://gdb.unibe.ch/downloads/)
- [marimo CLI](https://docs.marimo.io/cli/)
- [AnyWidget integration](https://docs.marimo.io/api/inputs/anywidget/)
- [Inline dependencies](https://docs.marimo.io/guides/package_management/inlining_dependencies/)

External documentation supplies scientific/API evidence. It does not override the H100-only restriction or expand publishing authorization.
