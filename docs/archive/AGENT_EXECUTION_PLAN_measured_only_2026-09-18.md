# Before You Make It — agent execution instructions

Prepared 18 September 2026. Workspace: `/Users/menuab/Documents/ChatGPT/marimo`.

## Assignment and stopping point

Implement, launch, and verify a native marimo notebook for the OpenADMET notebook competition. Build the complete measured-data experience: a beginner-friendly data introduction, chemical structure tooltips and linked molecule grids, prediction-based shortlist selection, an interactive prediction-to-measurement reveal, selection-pressure analysis, and inspection of chemical families and nearest training analogs.

Finish with a short, honest transition to the user's Galactica-based Chemlactica work and prepare its future input/output contract. **Stop before downloading model weights, installing a model-inference stack, loading a checkpoint, generating molecules, or running any Chemlactica inference.** No new ADMET training or inference is needed either: use the published predictions already available.

This is an implementation assignment. Continue through all stages below; the earlier proposal's “first implementation assignment” was a smaller milestone, not the completion boundary for this task. Do not stop after producing a scaffold, static HTML preview, or introductory chart. Do not publish or submit the notebook, create accounts, or spend money. Routine reversible local implementation, environment setup, data retrieval from the recorded public sources, and verification are part of the assignment.

The intended deliverable is a running notebook the user can inspect, supported by reproducible data preparation, meaningful validation, and a precise account of what remains for Chemlactica.

## Read first and preserve existing work

Read applicable `AGENTS.md` instructions, inspect the current working tree, then read these workspace files in order:

1. This execution plan.
2. `COMPETITION_STORY_PROPOSAL.md` for the scientific question and visitor journey.
3. `DATA_AUDIT.md` and `outputs/audit.json` for checked provenance and transformations.
4. `scripts/first_experiment.py` and `outputs/first_pressure_data.csv` for the actual calculation.
5. `NOTEBOOK_COMPETITION_PLAN.md` for prior decisions, model boundaries, and parked alternatives.

Do not treat every idea in the older documents as required. The latest scope above takes precedence: all measured-data interactions, but no Chemlactica execution. Keep one baseline, Morgan + LightGBM, in the main experience. Do not add CheMeleon, a model leaderboard, docking, PMO-Dock, fine-tuning, or a substitute generator.

Much of this workspace is currently untracked. Untracked does not mean disposable. Preserve the original scripts, data, audit, proposal, and first pilot outputs. Do not overwrite historical outputs to make new results appear consistent. Put new caches and validation artifacts in separate named paths. Never use `git clean` or broad resets.

There is a previous standalone HTML motion study outside the repository. It is not a marimo notebook, has not passed browser interaction verification, and is not an implementation foundation. The new notebook must use real marimo state and chemistry components.

## Product and scientific question

Working title: **Before You Make It — From AI shortlist to molecular evidence**.

Primary question: **When we select molecules predicted to balance LogD and solubility, how much of their predicted advantage survives experimental measurement as we become more selective?**

The audience includes someone unfamiliar with ExpansionRx, SMILES, ADMET, and these assays. The first few interactions must teach enough to understand the question. The experience progresses through: meet one molecule, explore the training collection, make a shortlist, reveal measurements, investigate individual compounds, and consider what evidence a future generated proposal would need.

The plot is not required to show catastrophic model failure. The existing pilot shows useful selection with an optimistic predicted gain. Report the actual result and its limits. The final scientific takeaway must make sense before adding any generated molecules.

The competition explicitly promotes marimo-chem-utils and extensions. Build around structure-aware selection and reactive notebook execution. Pat Walters' published examples favor connecting overview plots to actual structures; his evaluation writing emphasizes dataset quality, statistics, and training/test similarity. These inform the design, without implying endorsement or a guaranteed judging outcome.

## Deliverables

Create these files, adapting names only for a concrete implementation reason:

- `before_you_make_it.py`: the actual runnable marimo notebook.
- `requirements-notebook.in` and `requirements-notebook.lock.txt`: intentional runtime dependencies and resolved versions for the tested environment.
- `README.md`: exact installation, launch, data-bootstrap, and verification instructions; explain the Chemlactica stopping point.
- `DATA_CONTRACT.md`: columns, units, transforms, identifiers, score, exclusions, source revisions, evidence types, and provenance.
- `tests/test_analysis.py`: focused scientific/data regression tests; use the standard library if sufficient.
- `outputs/notebook_validation/`: checks, screenshots when available, and new derived summaries. Preserve the old pilot files elsewhere in `outputs/`.
- `CHEMLACTICA_HANDOFF.md`: future generation inputs, output contract, and outstanding model decisions. No runnable inference or model download is needed.
- `outputs/chemlactica_preparation/seed_manifest.json`: a small deterministic set of real training seeds with provenance, if seed selection succeeds.
- `IMPLEMENTATION_STATUS.md`: what was built and tested, launch URL/process status, performance observations, and remaining limitations.

Small helpers under `scripts/` or a local module are acceptable when they improve clarity. Prefer a notebook that can bootstrap from pinned public data without importing unshipped local helpers. If helpers are required, provide and test an explicit bundle/launch path; never call a lone `.py` file portable when it depends on hidden workspace files.

Do not manufacture a candidates file with invented outputs. A candidate schema may be documented without any generated records.

## Stage 1 — minimal environment and a running notebook

At planning time, this shell reported Python 3.14.6, and neither `uv` nor `marimo` was on PATH. Recheck rather than assuming that is still true. Inspect any existing `.venv` before changing it.

Use one project-local virtual environment. A compatible installed Python 3.12 or 3.13 is a reasonable first choice if available; otherwise check that the installed Python has binary wheels for the required chemistry packages. Avoid an unplanned RDKit source build. If a compatible interpreter is missing, install a maintained compatible Python through an available trusted package manager and document that decision.

The required runtime capabilities are provided by these packages:

- `marimo`, `marimo-chem-utils`, `altair` for the notebook and linked chemistry views.
- `rdkit`, `pandas`, `numpy` for chemistry and data handling.
- `duckdb` for reading the saved prediction Parquet without requiring a separate PyArrow stack.
- `anywidget`, `traitlets` for the custom reactive reveal.

List directly used packages explicitly even if another package also depends on them. Let the chemistry package's necessary transitive dependencies resolve; “minimal” does not mean bypassing supported dependencies. Avoid torch, transformers, accelerate, CUDA, Jupyter, Docker, Node build systems, and 3D packages for this milestone. Matplotlib is only needed if deliberately running the historical plotting script; the notebook does not need it merely to reproduce the underlying calculation.

Bootstrap commands, after selecting the compatible `python3` executable and creating the runtime requirements file:

```sh
cd /Users/menuab/Documents/ChatGPT/marimo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-notebook.in
.venv/bin/python -m pip check
.venv/bin/python -m pip freeze > requirements-notebook.lock.txt
```

Use the selected interpreter explicitly if it is not `python3`; record it in the README. Reuse a suitable existing environment instead of recreating it. Resolve versions once, smoke-test imports and rendering, then retain the tested lock. Do not blindly install `requirements-audit.txt` as the notebook environment: its historical plotting dependencies are a separate concern. Inspect installed package signatures because upstream examples and their package pins may differ.

Create the notebook with valid `marimo.App`, reactive cells, and an `app.run()` entry point. Add PEP 723 inline metadata listing the tested direct dependencies and supported Python version so future sandbox/molab use is clear. Keep these declarations consistent with the project environment.

Launch early in the existing environment:

```sh
.venv/bin/marimo edit before_you_make_it.py --no-sandbox --watch --headless --host 127.0.0.1 --port 2718
```

Check the installed CLI's help before relying on flags. If the port is occupied, use a free port and record it; do not kill an unrelated process. Keep the local server in a managed background session and use its returned browser URL, including its normal authentication token where applicable. Do not disable authentication or bind publicly to simplify testing. The token is for local access, not something to commit in documentation.

Use one environment for initial development, rather than nesting a sandbox inside `.venv`. The separate `marimo edit --sandbox` route can be verified later if uv is available. Start with a visible heading and a real molecule to prove the notebook is executing; continue building in this running notebook.

**Gate:** Python imports succeed, dependency resolution is recorded, a real RDKit structure renders in marimo, and the notebook is accessible at a local URL.

## Stage 2 — data bootstrap, joins, and cache

Reuse cached files under `data/` after checking their SHA-256 values against `outputs/audit.json` and `scripts/first_experiment.py`. If missing, fetch the same pinned public revisions, validate the digest, and write atomically. An existing checksum mismatch is an error to investigate, not permission to overwrite the file silently.

Source revisions currently used:

- OpenADMET data: `6b898ccc43d10d25b230fb09e22a6e30c30022b5`.
- Pat Walters benchmark: `06582771d48af8096f6b05a5a247b177189a8fa4`.

Required inputs are `expansion_data_train.csv`, `expansion_data_test.csv`, `expansion_data_raw.csv`, `expansion_log_scaled.csv`, and `predictions_all.parquet`. The latter is approximately 19 MiB locally. Use the manifest's exact URLs and digests; do not replace them with current branch heads.

Copy or factor the minimal verified loading/scoring logic with attribution. Importing the historical script also imports its plotting dependencies, so avoid doing that merely for one function. Keep numerical behavior identical and verify it against the saved pilot.

Build a typed table using stable molecule IDs. Explicitly distinguish `pred_LogD`, `pred_LogS`, `obs_LogD`, `obs_LogS`, and `obs_KSOL_uM` before merging. Generic `LogD` columns can collide and acquire suffixes; never let prediction/measurement identity depend on implicit suffixes.

Verify these reference facts from the actual files:

- Official training split: 5,326 molecules; test split: 2,282.
- Training complete cases for the two endpoints: 4,934.
- Test numeric LogD: 2,270; numeric KSOL: 2,170; both: 2,160.
- The 122 test molecules excluded from the primary paired analysis are not automatically failures. Preserve the separate missing/censoring accounting.
- Raw data have 7,618 rows; ten are outside the released train/test split. Do not silently add them.
- IDs and structures match the benchmark before joining.
- For `method == 'lgbm'`, there are 25 saved predictions per eligible molecule and endpoint. Validate repeat/fold keys and completeness before averaging.
- Saved `y_true` matches the official measurements after the documented transform.
- The reference audit reports valid parsed structures, no exact canonical train/test duplicates, and 59 benchmark clusters represented in both splits. Verify definitions before reproducing those counts.

Average predictions in their stored endpoint space, per molecule, before computing the predicted joint score. For solubility, the stored quantity is:

```text
LogS = log10(KSOL_uM + 1) - 6
KSOL_uM = max(10 ** (LogS + 6) - 1, 0)
```

This is a transformed kinetic-solubility value. Do not relabel it as unmodified thermodynamic log molar solubility. Preserve the clipping behavior in the original `score()` function for numerical consistency. In particular, inverse-transforming an average log prediction is not the same as averaging inverse-transformed predictions.

Expected table fields include molecule ID, original SMILES, canonical isomeric SMILES, split, benchmark cluster ID, observed properties and availability, mean predicted properties, prediction count, predicted/observed score, and nearest-training ID/similarity. Add derived fields explicitly; never impute absent measured outcomes.

Do expensive joins, fingerprint construction, nearest-neighbor search, random-reference sampling, and depiction work once or in keyed caches. Cache identity must include source hashes, analysis settings, relevant RDKit version, and code/schema version. Changing selection must not download data or recompute all fingerprints.

Use a separate regenerable cache such as `data/notebook_cache/`. This path is ignored already under `data/`; the notebook must be able to regenerate it. Ensure a fresh runtime can fetch and prepare its pinned data without a hidden manual command. Preserve original `outputs/audit.json`.

**Gate:** validated source identity, a unique-ID joined cohort, exact primary counts, finite numerical outputs, and the documented reproducible bootstrap path.

## Stage 3 — exact score and descriptive results

Recompute the rule from the training complete cases. Expected constants: LogD lower quartile 1.4, upper quartile 2.9, median KSOL 125.5 µM.

```text
distance = max(1.4 - LogD, LogD - 2.9, 0)
logd_component = exp(-distance / 0.75)
solubility_component = KSOL_uM / (KSOL_uM + 125.5)
joint_score = sqrt(logd_component * solubility_component)
```

Label it an illustrative training-derived desirability score, not a probability of drug success. Keep raw properties accessible. Do not optimize this rule against held-out outcomes; the pilot has already been seen and later analysis changes are exploratory.

Rank the fixed 2,160-molecule test cohort by predicted score. Preserve the pilot's stable ordering/tie behavior, or document and verify any deliberate tie-break change. For fractions 50%, 25%, 10%, 5%, 2%, compute `max(1, round(N * fraction))`: 1,080, 540, 216, 108, 43. Default the UI to 10%. The 2% point is 43 compounds, not a privileged laboratory budget or 43 experiments. Include the 100% cohort as a reference if helpful.

For each fraction compute on exactly the same selected IDs:

- Mean predicted and measured score.
- Measured gain over the whole-cohort measured mean.
- Predicted-minus-measured score gap.
- Measured count and fraction passing a plainly stated illustrative threshold rule: `1.4 <= LogD <= 2.9` and `KSOL_uM >= 125.5`. These thresholds are an added diagnostic, not the continuous score itself or a clinical standard.
- Optional retrospective best-measured ceiling, labeled unavailable at selection time and hidden before the reveal.

Regression targets for the fixed baseline, before display rounding:

```text
Random-reference mean: 0.5808721599709448
Top 10%, n=216: predicted 0.7942619913570331; measured 0.7461249726859417
Top 2%, n=43:   predicted 0.8248401217273029; measured 0.7538348622359935
```

Compare all fractions with the existing CSV, aiming for absolute tolerance `1e-9` under equivalent computations. Investigate mismatches in aggregation, units, clipping, ordering, or cohort membership. Do not hardcode these means into the live display.

Required uncertainty context: with a fixed documented seed, sample 2,000 random subsets without replacement within each subset, of the same size as each shortlist. Report a central 95% reference interval for random-shortlist means. Repeated draws across subsets are allowed. Label this “variation across random shortlists”; it is not an assay confidence interval or a confidence interval around the selected model's result.

Report the fixed-cohort selected means descriptively. Do not add unsupported error bars. Broader-population cluster-aware bootstrap estimates and 25-fit selection stability are optional follow-up analyses, not blockers for this delivery. If included, define the estimand, chemical-cluster assumptions, and repeated-fit dependence explicitly.

**Gate:** all pilot aggregates reproduced, threshold counts calculated from actual measurements, random-reference sampling reproducible, and labels distinguish each quantity.

## Stage 4 — newcomer orientation using native chemistry components

Build this before the custom animation, but continue afterward through the full assignment.

1. Show the primary question and one real complete-case training molecule. Choose it deterministically by a stated rule; do not invent a chemical name or therapeutic role from its structure.
2. Explain what a molecule record contains: structure, SMILES, measured LogD, measured kinetic solubility, and units. Expand ADMET once, then explain only the relevant endpoints.
3. Verify assay conditions from source documentation before giving a pH, incubation time, or experimental protocol. Omit unverified specifics. State that these compounds are not necessarily approved drugs and these properties do not establish potency or safety.
4. Show the training complete cases in a property plot with meaningful axes, molecular tooltips, and a selection-linked molecular grid. Use marimo-chem-utils functions supported by the installed version.
5. Explain any log transformation visibly. A log1p axis with actual µM tick labels can be used for solubility, including zero, provided the mapping is declared and consistent. Alternatively show the exact stored transform. Do not silently drop zeros on a logarithmic axis.
6. Show the chosen LogD band and explain that the acceptable range is an illustrative decision rule. Provide a small explanation of the training/test split and exclusions before introducing predictions.

Inspect the actual installed `interactive_chart`, `add_image_column`, and `draw_molecule_grid` APIs. The current README and example notebook differ in whether a chart is already wrapped. Determine the return type instead of wrapping a UI element twice. Avoid cross-cell in-place dataframe mutations; assign transformed data to explicit new variables so marimo can track dependencies.

The initial grid should contain a small deterministic sample so the screen is useful before interaction. After a brush selection, show selected structures, count, pagination, and a readable property table. Distinguish “no selection yet” from “selection contains no molecules.” Cap rendered structures per page, not the analytical cohort.

Keep held-out measured values out of this introductory scene. Use training measurements for orientation so the test reveal remains meaningful.

**Gate:** a newcomer can identify a molecule and both axes, and a real plot selection updates a native molecular grid through Python without manually rerunning cells.

## Stage 5 — shortlist and reactive measurement reveal

Build a prediction view of the fixed held-out cohort with the fraction control, selected count, molecule tooltips/grid, and a reveal action. Scientific selection uses predictions only. Measured positions, outcome-based examples, measured metrics, and retrospective ceiling are initially hidden. This is presentation state, not a claim of prospective blinding or a security boundary.

Implement the signature reveal as a small AnyWidget wrapped in `mo.ui.anywidget`, not a detached iframe containing the entire analysis. Use SVG/canvas and lightweight JavaScript inside the widget; avoid adding a frontend build system. Reuse RDKit-generated chemistry depictions.

The proposed interface should have:

- An immutable input payload keyed by molecule ID, containing paired coordinates, scientific property values, and accessible labels.
- Synced traits for selected molecule IDs, active molecule ID, and committed reveal state.
- A local animation progress value with replay and scrubbing. Animation frames should remain in the frontend; publishing 60 updates per second to Python would needlessly rerun cells. Publish committed changes or throttled meaningful events.
- A stable inspection output read in a downstream marimo cell through the wrapped widget's supported state API.

Choose one clear direction of state ownership. The fraction control determines the ranked cohort upstream. Widget selection determines downstream grid/table inspection. An optional table selection determines the active evidence card. Do not write downstream selection back upstream in a reactive cycle. If adding bidirectional coordination, prove it does not loop or reset selection unpredictably.

Interaction requirements:

- The same molecule ID moves between predicted and measured coordinates on a fixed axis scale.
- Trails and endpoint labels make the direction understandable. Motion interpolates properties, not atom coordinates or molecular geometry.
- A reveal changes the display, never the underlying ranking.
- Clicking or selecting a visible molecule updates a downstream molecular grid and evidence card in Python.
- Changing fraction clears stale selection, stops old animation, and resets the reveal to predictions; explicitly label the new shortlist size.
- Scrubbing and replay work repeatedly without duplicated listeners or lingering animation frames. Implement widget cleanup.
- A reduced-motion endpoint view supports the same selection/evidence workflow.
- Keyboard-accessible controls and a selectable table provide alternatives to hover or precise pointing.
- Partial animation states are labeled visual interpolation. Do not report interpolated values as experimental results.

Use real chemistry grid/tooltips from the package elsewhere in the notebook. The custom component should extend the evidence workflow, not replace every native component with a separate dashboard.

**Gate:** an interaction originating inside the custom widget changes at least one downstream Python-derived chemical view; identity and selection persist correctly through the reveal; reduced-motion and repeated use work.

## Stage 6 — pressure curve, molecular families, and analog inspection

After the reveal, expose the selection-pressure analysis with predicted and measured score, random reference, random-shortlist interval, and measured threshold-pass counts. Labels must state the cohort and denominator. A brush or family filter is an inspection subset, not permission to rerank a different cohort silently.

Use benchmark cluster labels already present in `expansion_log_scaled.csv` to organize chemical families. Explain that algorithmic clusters do not necessarily share one exact scaffold. Join IDs explicitly. Let choosing a family update its molecule grid, relevant paired values/errors, and family count. Keep overall results available with a clear reset.

For each inspected test molecule show:

- The molecule and its nearest **training** analog as labeled 2D structures.
- Their identities and split labels.
- The test molecule's predicted and, after reveal, measured properties with units.
- The analog's own measured properties, including missingness where applicable.
- Morgan radius-2, 2,048-bit fingerprint Tanimoto similarity, matching the audit's similarity definition. This bit-fingerprint diagnostic is separate from the baseline model's fingerprint representation.

Compute nearest neighbors against all valid training structures; do not choose a closer held-out molecule. Break equal-similarity ties deterministically by molecule ID and cache the result. Reference audit targets: median nearest-training similarity about 0.6363636; 242 of 2,160 at least 0.8.

Where supported, align depictions and highlight a real shared substructure. Use a bounded MCS calculation or a documented scaffold match, preserve stereochemistry in depictions, and handle no match/timeout honestly. Alignment is optional if it would compromise chemical validity; explicit molecular comparison is required.

Provide three outcome-based example choices after the reveal: a typical selected compound, a large overprediction, and a case whose promise survived measurement. Define deterministic selection rules and tie-breaks, label them retrospective examples, and keep the whole shortlist browsable. Do not invent a structural cause for an error.

Include a compact, secondary functional-group review using the package's REOS/SMARTS pattern if its supported API is practical. Name the rule set and highlight actual matched atoms. Describe matches as review cues, not proof of toxicity, failure, or the cause of a prediction error. If package compatibility prevents this secondary feature, document that specific limitation while completing all core views.

**Gate:** family filtering, molecule selection, nearest-training provenance, and chemically valid highlighting are inspectable; no display substitutes an analog's measurement for the selected compound's measurement.

## Stage 7 — prepare the Chemlactica boundary without executing it

Finish the current notebook with a concise transition: “We have checked predictions against existing measurements. Next, Chemlactica can propose analogs whose experimental properties still need to be measured.” Make it clear this stage has not run.

Prepare three real complete-case training seeds from distinct available benchmark clusters, selected deterministically by measured training desirability with molecule-ID tie-breaks. These are future proposal seeds, not held-out evaluation winners. Record their IDs, SMILES, cluster, measured properties, score rule, source hashes, and why each was selected. A real training-seed grid is appropriate. If fewer than three eligible distinct families exist under the stated rule, record that fact rather than inventing seeds.

Do not render fake generated structures, empty generated-candidate galleries, a functioning-looking Generate button, or a success banner. The current notebook should feel complete at the end of its measured-data question, followed by this clearly scoped next step.

Document the future candidate record contract:

```text
candidate_id, seed_id, smiles, canonical_isomeric_smiles
checkpoint_id, checkpoint_revision, prompt, random_seed, decoding_settings
generation_run_id, raw_sample_index, validation_status, rejection_reason
similarity_to_seed, nearest_training_id, nearest_training_similarity
computed_descriptors_with_names_units_and_tool_versions
measured_LogD = null, measured_KSOL_uM = null
evidence_status = "proposal_unmeasured"
```

Real future outputs must retain invalid/duplicate sample accounting in a separate raw log. Deduplication does not establish global chemical novelty. A nearest analog gives context only. Saved test prediction tables cannot score new candidates. A computed cLogP is not experimental LogD. Do not add an unsupported LogD conditioning tag.

Prepare `CHEMLACTICA_HANDOFF.md` with this schema, seed selection, proposed 3 × 32 sample feasibility budget, required checkpoint/prompt verification, and the later cached-loading path. Do not fix an unverified checkpoint identifier or install dependencies for it. The notebook's imports and dependency metadata must remain free of the model stack.

**Gate:** training seeds and future schema are ready, the notebook truthfully explains the missing generation step, and no model execution/download has occurred.

## Stage 8 — validation, polish, and restart

Use focused checks that protect scientific meaning and real behavior. Do not spend time on tests that only mirror cosmetic implementation.

Required data/analysis checks:

- Hashes, unique joins, cohort sizes, transformed labels, 25 predictions per endpoint, and all pilot aggregate regressions.
- Changing held-out observed values in an isolated in-memory test must not change the predicted ranking or training-derived constants.
- Selected means and pass counts use the same IDs and denominators; selections are nested as fractions shrink.
- Threshold boundary behavior, score range, zero-solubility handling, and transform round-trip behavior on valid measured examples.
- Nearest analogs are training IDs, similarity is bounded, and known split/similarity checks match.
- Serialization uses JSON null for missing results, never invented zeros or nonstandard NaN.
- Proposal-state handling can be tested using a clearly synthetic test record kept outside the user-facing data; do not display it as a generated compound.

Run the installed CLI's supported equivalents of:

```sh
.venv/bin/marimo check before_you_make_it.py
.venv/bin/python -m unittest discover -s tests
.venv/bin/marimo export html before_you_make_it.py --no-sandbox -o outputs/notebook_validation/notebook_snapshot.html
```

Create the output directory first and preserve prior validation runs when overwriting would obscure evidence. A static export checks execution and records a snapshot; it does not establish interactive Python behavior. Inspect export/runtime logs for failures rather than trusting that a file exists.

Required browser walkthrough of the running notebook:

1. Load from a fresh session and inspect the newcomer explanation and real initial structure.
2. Brush the training plot; confirm molecule-grid and table IDs match the selection.
3. Change fractions through 10%, 2%, and 50%; confirm 216, 43, and 1,080 compounds.
4. Confirm held-out measured information is hidden until reveal; reveal and verify the recorded metrics.
5. Select a custom-widget point; confirm the downstream Python evidence view changes to the same molecule.
6. Replay, scrub, change fraction during/after a reveal, clear selection, and test empty subsets.
7. Inspect a family and a nearest training analog; verify IDs, units, and valid highlights.
8. Check table/keyboard alternatives, reduced motion, and a narrower layout for label collisions or clipped controls.
9. Restart the kernel and notebook process; confirm reproducibility and no manual out-of-order cell execution.
10. Confirm the ending contains only real training seeds and an explicitly future Chemlactica step.

Use the browser tools available in the execution environment and obey their supported access flow. Do not count a standalone JavaScript animation or an HTML export as a substitute for testing marimo reactivity. If browser access is blocked, continue allowed runtime/data checks and clearly mark the remaining interaction verification as unverified; do not claim completion of that gate.

Record cold-start and warm interaction timings on the actual machine. Aim for responsive selection, lazy/paginated structure rendering, and cached nearest-neighbor work. Measure before adding complexity. Keep scientific metrics in Python; transient animation can stay in JavaScript.

Verify a separate clean runtime or clean notebook cache using the documented bootstrap. Do not delete the user's existing cache to simulate a fresh run. Test molab only if an already authorized path permits it without publishing or sharing the project; otherwise provide the bundle and clearly report that molab execution remains unverified.

## Scientific and presentation rules throughout

- Prediction, measurement, computed descriptor, and future proposal are distinct evidence types in labels and code.
- No train/test leakage in rule fitting or ranking. Shared chemical families limit generalization even without exact duplicates.
- Missing/censored results are not ordinary numerical outcomes. Do not treat inequality strings as exact measurements.
- Do not claim these endpoints establish efficacy, safety, synthesizability, or clinical promise.
- Desirability is a declared decision rule. Similarity is context. Alerts invite inspection. None is a calibrated success probability.
- Statistical bands must say what varies. The 25 fits are not 25 independent laboratory replications.
- Keep presentation centered on one question. Do not build an unrelated EDA dashboard, a t-SNE tour, or a 3D viewer merely to add features.
- Keep methodological detail available through concise expanders, with short plain-language explanations beside the actual decisions.
- Include attribution, pinned source revisions, relevant licenses, and accurate AI assistance disclosure. Distinguish reusing saved predictions from training or running an ADMET model.
- Use the palette, typography, and layout consistently. Important outcomes must remain clear without animation, color discrimination, or hover.

## Definition of done and delivery message

The task is complete when the native notebook runs, all core scenes through molecular investigation work, the baseline numerical checks pass, meaningful reactive interactions have been exercised, a reproducible restart path exists, and the Chemlactica boundary is documented without running it. Secondary optional features do not replace missing core functionality.

Leave a working local notebook server available to the user when the environment supports a persistent process. Record the actual process/session and URL at handoff without promising permanence. Otherwise give the tested launch command and explain the process lifetime.

Your final response should link the notebook and README, provide the local access path, summarize implemented scenes and verification results, identify any unverified browser/molab behavior, and explicitly state that Chemlactica was not downloaded or run. Keep the fuller evidence in `IMPLEMENTATION_STATUS.md`.

## Authoritative references to check during implementation

- [Competition and submission requirements](https://marimo.io/pages/events/notebook-competition-3)
- [Competition's linked rubric](https://docs.google.com/spreadsheets/d/1xEd-njH43jTWQfr-2wjXULhiGKXl6zEvmKIobWOO8Ks/edit?gid=620363524)
- [Official ExpansionRx data](https://huggingface.co/datasets/openadmet/openadmet-expansionrx-challenge-data)
- [Saved benchmark predictions](https://github.com/PatWalters/expansion-ml-comparison)
- [marimo-chem-utils](https://github.com/PatWalters/marimo_chem_utils) and its installed-version examples
- [Chemistry overview/detail tutorial](https://patwalters.github.io/Practical-Cheminformatics-with-Marimo/)
- [Evaluation considerations](https://patwalters.github.io/Just-Because-You-Published-It-Doesnt-Mean-Its-Right/)
- [marimo CLI](https://docs.marimo.io/cli/)
- [Inline dependencies and sandbox environments](https://docs.marimo.io/guides/package_management/inlining_dependencies/)
- [AnyWidget integration and state](https://docs.marimo.io/api/inputs/anywidget/)
- [Chemlactica repository for future model verification](https://github.com/yerevann/chemlactica)

External documentation provides API evidence, not permission to expand this task's scope. Check the installed APIs and keep pinned data revisions stable.
