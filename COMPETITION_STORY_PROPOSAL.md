# Before You Make It

*From AI shortlist to molecular evidence*

Working competition proposal · updated 18 September 2026

The current implementation assignment is in [AGENT_EXECUTION_PLAN.md](AGENT_EXECUTION_PLAN.md). It supersedes this historical proposal with a seven-interaction ADMET story, a second Caco-2 evidence reveal, and authorized real `yerevann/ChemLlama-1B` generation on H100 Slurm resources only. Its scope replaces the earlier no-inference stopping point and Galactica-only model choice below. A6000 devices are off limits.

This is a proposed direction for discussion and implementation. It specifies the story, interactions, scientific boundaries, and delivery plan; it does not claim that the notebook, custom widget, or Chemlactica generation experiment has been built. The original `NOTEBOOK_COMPETITION_PLAN.md` remains the record of prior work. This proposal incorporates the user's later priority: showcase marimo's chemistry tools and reactive execution through a compelling scientific experience.

**The lead pitch**

You are at a molecular design meeting. A model has ranked the candidates, a generator can propose more, and you have a limited testing budget. What evidence would make you spend an experiment on one molecule?

Before You Make It is an interactive investigation built around OpenADMET's ExpansionRx data. Visitors shortlist existing compounds using predicted lipophilicity and solubility, reveal their released experimental measurements, and inspect the chemical families and training analogs behind the results. They then use the same inspection workflow to examine new analogs proposed by our Galactica-based Chemlactica model, where experimental answers are still unknown.

Its signature contribution is a reusable molecular evidence widget: a prediction-to-measurement reveal connected to chemical structures, family selection, and nearest-training-analog inspection through marimo's reactive cells. The visitor ends by choosing a proposal and naming the evidence still needed to evaluate it.

**The question and the payoff**

The primary scientific question is: when we select molecules predicted to balance LogD and solubility, how much of their predicted advantage survives experimental measurement as we become more selective?

The broader story asks: what should we inspect before turning an AI suggestion into the next experiment?

The outcome remains open. A good shortlist can improve on random selection while overestimating its own quality. The current pilot supports that possibility. The notebook must also remain satisfying if uncertainty weakens the apparent gap or some chemical families perform well. Discovery comes from investigating what happened to specific molecules.

Use “Before You Make It” as the proposed title. It accommodates both existing compounds in a retrospective decision exercise and generated proposals for future work. Explain that the first experiments already happened; the reveal is a presentation device, not a prospective trial. Avoid a title that requires the molecules or the model to fail.

**Why this fits the competition**

The competition names marimo-chem-utils and encourages extensions. Its linked rubric assigns 20% each to creativity, interactivity/workflow, presentation/shareability, and customization, plus 10% each to code quality and chemical validity. A strong submission therefore needs a distinct scientific experience, an integrated custom contribution, and a reliable execution path. This proposal is designed against those published criteria; it cannot predict the judges' final choice. [Competition](https://marimo.io/pages/events/notebook-competition-3) · [Linked rubric](https://docs.google.com/spreadsheets/d/1xEd-njH43jTWQfr-2wjXULhiGKXl6zEvmKIobWOO8Ks/edit?gid=620363524)

The intended first-minute impression: changing a selection changes the chemistry you see, the evidence you inspect, and the scientific conclusion you can draw.

**How to account for Pat Walters' published priorities**

His writing identifies dataset quality, appropriate statistics, and training/test similarity as key evaluation concerns. His marimo chemistry examples emphasize moving between summary views and actual structures. Our inference is that an inspectable decision workflow will fit those stated priorities. We cannot infer his private preferences or endorsement. [Evaluation article](https://patwalters.github.io/Just-Because-You-Published-It-Doesnt-Mean-Its-Right/) · [Marimo chemistry examples](https://patwalters.github.io/Practical-Cheminformatics-with-Marimo/)

Express this through the notebook: show source and assay units, preserve the official split, expose nearest-training similarity, inspect representative molecules as well as outliers, and separate observed patterns from chemical explanations. Credit his tools and prediction source naturally. Do not create a fictional Pat persona, invented quotes, or an implied endorsement.

**The dataset and the existing foundation**

Use the official OpenADMET ExpansionRx release, which is one of the competition's suggested datasets. Focus on LogD and kinetic solubility so the main view remains understandable. Attribute the dataset under its published CC-BY-4.0 license. [Dataset](https://huggingface.co/datasets/openadmet/openadmet-expansionrx-challenge-data)

The local audit records 5,326 training and 2,282 test molecules, including 2,160 test molecules with numeric measurements for both endpoints. The primary cohort stays fixed across shortlist sizes. Missing and censored measurements remain accounted for outside that primary cohort.

Use the pinned Morgan + LightGBM prediction files already audited locally. Average the saved predictions per endpoint and molecule before applying the decision rule, matching the pilot. Attribute this baseline to its source; Chemlactica does not supply these predictions. [Saved benchmark source](https://github.com/PatWalters/expansion-ml-comparison)

The existing training-derived desirability rule rewards LogD within 1.4–2.9 and increasing solubility. Its 0–1 output is an illustrative decision score. Present raw properties alongside it. It is neither a drug-success probability nor a generally optimal medicinal chemistry target.

For the top 43 molecules, the audited means are 0.825 predicted and 0.754 measured, compared with 0.581 for expected random selection from the eligible cohort. These descriptive results establish feasibility; they do not establish a universal failure of ADMET prediction. See [DATA_AUDIT.md](/Users/menuab/Documents/ChatGPT/marimo/DATA_AUDIT.md) for provenance and limitations.

**Scene 0 — Meet the molecules and understand the decision**

Begin with the question in one plain-language sentence, then a brief guided orientation. Assume the visitor has never heard of ExpansionRx or ADMET. Explain that these are compounds from drug-discovery programs, with structures and laboratory measurements of properties relevant to how compounds behave. They are not a list of approved drugs, and these two endpoints do not establish therapeutic activity or safety.

Start with one real training-set molecule shown as a structure beside its annotated data record. Explain that SMILES is a text representation of the structure; LogD describes partitioning between lipid-like and aqueous phases under specified conditions, while kinetic solubility measures dissolved concentration under the assay protocol. Show units and retrieve assay conditions from the source documentation before stating them. Explain that LogD has a chosen target range in this exercise, whereas solubility receives increasing credit. Avoid implying either a universal optimal range or that higher LogD is always better.

Then place training molecules in the two-property view, with structure tooltips and a selectable molecular grid. Explain the axes, any logarithmic transformation, and the illustrative target. A visitor can select a region and see the compounds behind it. The scene establishes why balancing two properties creates a selection problem.

Finally explain the split and coverage: 5,326 training compounds supply the illustrative rule and analog context; 2,282 held-out compounds have published baseline predictions; 2,160 have numeric experimental values for both selected endpoints. Account for the other 122 without calling them failures. Use training measurements for the opening property distributions so held-out outcomes can remain hidden until the reveal. The reader now understands a molecule, a measurement, a prediction, and the cohort being evaluated.

Keep this orientation short enough to lead naturally into the question. It is scaffolding for an investigation, not a complete dataset dashboard. Show measured units before introducing the composite score, and explain the score only when ranking requires it.

**Scene 1 — Make the shortlist**

Opening copy: “If we could investigate only a fraction of these compounds, would the model help us choose?”

Select by a visible fraction and show the derived molecule count. A proposed initial state is the top 10% (216 compounds), with 50%, 25%, 5%, and 2% available for comparison. This is a presentation default, not a scientifically privileged budget. The pilot's top 2% gives round(0.02 × 2,160) = 43 compounds. The 43 count has no special experimental meaning and should not anchor the title or premise. Call these shortlisted compounds, not 43 experiments: two endpoints and possible assay replicates prevent that equivalence.

Show predictions, with measured outcomes hidden initially. Let visitors adjust the shortlist budget among the established fractions and select compounds or groups on the property plot. Hovering reveals molecular structures; selecting a group populates a structure grid and property table. The active budget and selection remain visible.

Features demonstrated: marimo controls and reactive execution, marimo-chem-utils structure tooltips and molecular grids, selection-linked tables and charts. This applies the package's documented patterns to a specific decision. [Package](https://github.com/PatWalters/marimo_chem_utils)

The main experience uses the fixed decision rule. If editable scientific thresholds are added later, clearly mark them exploratory and keep them separate from the fixed pilot analysis.

**Scene 2 — Reveal the laboratory results**

Opening copy: “These experiments have already been done. Let's see where your selected molecules landed.”

The custom reveal moves each selected molecule from its predicted to its measured property position. Trails preserve identity, and the visitor can scrub between the two states. The molecules themselves do not change; only their plotted property coordinates change. Intermediate positions are visual interpolation, not measurements or a physical trajectory.

The chemical selection remains connected to the structure grid throughout. Clicking a molecule publishes its ID to Python and updates its evidence view. A stable side-by-side or endpoint view remains available for precise comparison and reduced-motion use.

The reveal reports measured gain over random, the predicted/observed score gap, and raw endpoint values. Add explicit measured threshold-pass counts with a declared illustrative rule. Never call a compound a successful drug based on these two properties.

Features demonstrated: a purpose-built AnyWidget with two-way state, synchronized downstream notebook cells, and the existing chemical rendering tools. The reusable component handles IDs and evidence states; scientific calculations remain readable in Python. [AnyWidget support](https://docs.marimo.io/api/inputs/anywidget/)

**Scene 3 — Inspect the chemistry behind the result**

Opening copy: “Is this an isolated surprise, or part of a chemical family?”

Let visitors choose a family or cluster, inspect its molecular grid, and compare the selected compounds' errors. For an individual molecule, show its nearest training analog, fingerprint similarity, experimental properties, and shared substructure when a chemically meaningful match is available. Identify how the family and similarity were computed; avoid implying that every cluster has a single common scaffold.

The first guided examples should include a typical selected molecule, a strong overprediction, and a case whose promise survived measurement, picked by explicit outcome-based rules and labeled retrospective examples. The complete selected set remains inspectable.

A functional-group review can use SMARTS highlighting and the package's alert-review pattern. Alerts are inspection cues. They cannot establish toxicity, assay interference, or the cause of an error. Shared substructures similarly provide context rather than a causal explanation.

This scene turns the show into a useful chemical tool. A similarity-versus-error view is an exploratory diagnostic; do not promise that familiar compounds will necessarily be more accurate.

**Scene 4 — Bring in our Chemlactica work**

Opening copy: “Now we can propose the next molecules. What evidence comes with them?”

Introduce the generator by name in the opening premise, then give it the closing design task. Use a small set of measured training molecules as seeds for frozen, Galactica-based Chemlactica generation. This preserves a clean separation from the retrospective test evaluation. The released repository documents Galactica-based checkpoints and structured similarity conditioning. Verify the exact model card, checkpoint revision, and prompt format before the run. [Chemlactica](https://github.com/yerevann/chemlactica)

Proposed feasibility budget: three training seeds and 32 sampled outputs per seed. Choose seeds deterministically from distinct training families with suitable measured properties, before inspecting generated outputs. Check validity, deduplicate, record similarity and computed descriptors, and retain an audit of every sampled output and rejection. Select displayed candidates by a declared rule covering similarity and descriptor variation. The exact checkpoint stays undecided until feasibility and hardware needs are checked.

Show a training seed and its proposal family through the same molecular evidence view used in the earlier scenes. Seed measurements are labeled measurements of the seed. Generated candidates show their own computed descriptors and generation provenance; their measured LogD and solubility fields say “unknown.” Similarity and shared substructure help inspection without transferring the seed's assay results to the proposal.

Do not score these candidates using the saved benchmark prediction table: it contains results for existing test compounds and cannot evaluate new structures. Keep cLogP explicitly distinct from experimental LogD. Do not claim the retrospective experiment validates Chemlactica or that a generated molecule is novel to all chemical literature; checks against the bundled dataset establish only dataset overlap.

The visitor's final action is to nominate one candidate for further investigation and identify a next measurement. The nomination is a reasoned hypothesis. The measurable generator results are validity, uniqueness, structural relationships, and computed descriptors.

This makes the user's work central to the notebook's question: what happens when a molecular proposal arrives without the experimental answers that made the earlier audit possible?

**The custom contribution to prioritize**

Build one reusable “molecular evidence view” that joins selected molecule IDs, paired property positions when available, structures, analog relationships, and explicit evidence status. Its distinguishing feature is preserving the same investigation as a visitor moves from a measured compound to a generated proposal with missing experimental evidence.

The native features are the notebook's reactive execution, UI controls, and widget integration. Pat's chemistry package supplies documented rendering and overview/detail patterns. Our contribution is the coordinated evidence workflow and animated paired-property reveal. Automatic structural alignment and more elaborate family views are proposed extensions whose implementation must be verified; they are not claimed as existing package features.

Use marimol only if a specific 3D inspection strengthens the decision. It is a separate community package promoted in marimo's gallery, with atom selection and frame changes available to reactive cells. For this two-property story, it is optional. Any RDKit-generated conformer would be labeled computed geometry, with no suggestion that its appearance explains measured solubility. [Marimol demo](https://molab.marimo.io/gallery/l/molecular-trajectory-animation)

**Scientific evidence and uncertainty**

Keep the fixed shortlist analysis descriptive for this finite cohort. Show a random-shortlist reference distribution obtained by sampling equal-sized subsets without replacement; label its interval as random-selection variation, not uncertainty in an assay measurement. For broader-population estimates, specify the estimand and use a chemical-cluster-aware resampling analysis, rerunning ranking and selection within each resample. Treat this as a sensitivity analysis with explicit assumptions.

If selection stability across the 25 saved fits is useful, pair endpoints by the same repeat/fold and report variability as model-fit stability. These fits share test molecules and do not create independent experimental replications.

The audit found no exact canonical train/test overlap, but substantial related chemistry and shared clusters. Show those facts and restrict generalization accordingly. The pilot has already been inspected; subsequent thresholds, subgroup analyses, and narrative examples are exploratory. A second stored baseline can be a compact robustness check if needed, without expanding the core experience into a leaderboard or adding CheMeleon against the user's stated preference.

**Proposed implementation sequence and completion gates**

1. Lock the question, primary cohort, baseline, units, fixed score, example-selection rules, and source revisions. Reuse the audited preparation code and cached sources. Establish the environment and a native marimo notebook immediately; the user does not need to run a separate model or preparation pipeline manually. Complete the descriptive evidence and uncertainty specification as the data foundation is integrated.
2. Build the newcomer orientation and test the native interaction chain: plot selection updates the molecule grid and property table. Then add the plain prediction/measurement comparison and nearest-training-analog view. It must work in marimo before investing in animation.
3. Implement the reusable evidence widget and reveal. Verify stable molecule identity, Python state updates, missing-evidence behavior, keyboard access, readable labels, and responsiveness.
4. Run the small Chemlactica feasibility batch offline and record checkpoint, prompts, random seeds, decoding, hardware, outputs, and exclusions. Cached proposals make the submitted notebook runnable without downloading model weights. If quality is poor, revise the generation setup transparently; do not silently replace candidates or pretend the model scene succeeded.
5. Write concise scene transitions, attribution, methods, and limitations. Have a chemist inspect highlighted matches, chemical claims, and illustrative thresholds. Test whether a new reader can distinguish prediction, measurement, and proposal.
6. Run the notebook end to end in a fresh molab session using public or bundled assets and pinned dependencies. Check asset permissions/licenses, disclose AI assistance, and prepare the required video and molab link. The published deadline is October 4, 2026, 11:59 PM PST; confirm the submission form's operative deadline before submission. [Entry requirements](https://marimo.io/pages/events/notebook-competition-3)

**Proposed short video sequence**

Briefly introduce one molecule and the two properties, then present the shortlist question. Change the selected fraction once, select a group, and show actual molecular structures updating. Reveal the measurements, click a changed molecule, and inspect its training analog. Switch to a Chemlactica proposal using the same evidence view. End on the experimental fields that remain unknown and the measurement the visitor would request next.

The visual promise is a continuous path from model output to molecular evidence to a new hypothesis. The scientific promise is that every number, structure, and missing result can be inspected. Together these give the project a distinctive contribution, a substantive role for the user's research, and a clear reason to exist as a reactive chemistry notebook.

**First implementation assignment for an agent**

Suggested handoff prompt, for when implementation is authorized:

> Work in /Users/menuab/Documents/ChatGPT/marimo. Read COMPETITION_STORY_PROPOSAL.md, NOTEBOOK_COMPETITION_PLAN.md, DATA_AUDIT.md, and scripts/first_experiment.py. Build the first runnable native marimo notebook for “Before You Make It.” Set up isolated, declared dependencies; verify cached input hashes and the audited molecule joins, and reuse the existing score and saved baseline predictions. Start with a newcomer-friendly explanation of one training molecule, LogD, solubility, and the train/test split. Add a training-data property plot with chemical structure tooltips and selection linked to a molecule grid using marimo-chem-utils. Then add fraction-based shortlist selection and a plain predicted-versus-measured comparison for the fixed held-out cohort. Reproduce the recorded pilot aggregates. The initial fraction may be 10%; derive and display the selected count. Keep expensive data preparation outside reactive selection cells and keep the notebook runnable without undocumented prior commands. Run the notebook in marimo, inspect runtime errors, exercise the selection interaction, and verify a clean restart. This first milestone ends at the working data introduction and measured comparison; defer custom animation, 3D, new model training, and Chemlactica inference to subsequent milestones. Preserve existing artifacts and do not publish or submit.

The authoring loop is: edit the notebook's Python source, execute it in marimo, inspect errors and rendered behavior, and iterate. A code agent can do this directly. marimo's inline dependency metadata and sandbox support help make that environment reproducible. The later Chemlactica generation is a separate offline preparation step with a cached output consumed by the notebook. [Dependency workflow](https://docs.marimo.io/guides/package_management/inlining_dependencies/)
