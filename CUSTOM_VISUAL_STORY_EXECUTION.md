# Before You Make It: revised story and custom visual implementation

Execution brief, 20 September 2026.

## 1. Assignment and precedence

Execute this brief in the existing workspace. Deliver the working notebook and its portable viewing path, not another plan, standalone mockup, or collection of charts. The user wants a distinctive marimo competition entry that makes molecular vastness, accumulated human effort, imperfect prediction, and earned hope tangible in at most ten required interactions.

This is the current authoritative implementation brief for story, custom visuals, state flow, deployment parity, and acceptance. It supersedes conflicting narrative/UI instructions in `AGENT_EXECUTION_PLAN.md`, `STORY_EXPERIENCE_REWORK.md`, `COMPETITION_DESIGN_REVIEW.md`, and older proposals. Their source audits, H100-only restrictions, scientific safeguards, and existing authorization remain applicable. `COMPETITION_DESIGN_REVIEW.md` explains the rationale and source-code lessons; use it as supporting context.

Preserve the established title **Before You Make It**. Use the working subtitle **Fifty experiments. Twenty-five maps. One next decision.** Explain that fifty is an illustrative capacity limit and the twenty-five maps are saved repeat/fold fits of the benchmark predictor, not independent experts or twenty-five generated molecules.

The focused question is:

> How do we choose a few molecules to investigate when our maps of what looks promising disagree—and when measurements can change even their shared recommendation?

The emotional sequence is: vast possibility → respect for accumulated evidence → a personal AI proposal → scarce experimental attention → changing model nominations → experimental surprise and useful enrichment → broader ADMET questions → a better next experiment.

Do not reduce this to “AI fails.” Do not claim most research fails or that these results establish generated-molecule success rates. Winning is an objective, not a promise.

## 2. Authorization, scope, and preservation

You may edit the notebooks, scientific helpers when necessary, widget code, configuration, dependency manifests, bundle builder, relevant tests, and documentation. Install needed local development/browser dependencies and run local validation. Do not ask again for permission to perform this already-authorized work.

Preserve the approved ChemLlama run `chemllama-271948`, its raw records, candidates, and manifest. The pilot has 96 raw samples, 27 unique valid candidates, 69 invalid records, and zero duplicates. Keep the actual seed-prompt relationships and recorded prompting limitations. This revision requires no new model inference. If a demonstrated technical defect requires another run, the existing authorization permits H100-only Slurm inference; A6000 remains prohibited, including smoke tests and fallback. Viewing the notebook must never load weights or submit jobs.

Inspect applicable repository instructions and current filesystem/git state. Protect current work with version control or a dated, non-overwriting backup before substantial edits. Preserve historical audits, raw data, inference records, and existing pilot results. Do not clear global caches, stop unrelated services, or overwrite others' work.

The repository now references a public GitHub/molab entry point. Its existence is not permission to push or publish new changes. Prepare all local code, bundles, tests, and handoff artifacts. Use any existing explicitly authorized private molab execution route; otherwise report the exact remaining molab test gap. No public upload, submission, account creation, organizer contact, or paid service use is required by this brief.

## 3. Read and inspect before editing

Read these files once, then follow actual dependencies rather than repeatedly rereading plans:

- `before_you_make_it.py` and `before_you_make_it_wasm.py`.
- `scripts/notebook_data.py`, `scripts/experience_data.py`, and `scripts/build_molab_bundle.py`.
- `DATA_CONTRACT.md`, `DATA_AUDIT.md`, `outputs/audit.json`, and the current preparation manifest.
- `config/notebook_analysis.json`, `config/notebook_experience.json`, and `config/chemllama_generation.json`.
- `tests/test_analysis.py`, `tests/test_experience_data.py`, `tests/test_generation_contract.py`, and `tests/test_molab_bundle.py`.
- `scripts/validate_story_browser.py`, `IMPLEMENTATION_STATUS.md`, `README.md`, and both walkthrough/state documents.
- `outputs/notebook_validation/competition-review-20260920.json` and `COMPETITION_DESIGN_REVIEW.md`.

Check the current competition page/rubric and the primary API documentation for the installed marimo/anywidget versions. Do not assume the latest online example is compatible with the pinned environment. The project already lists anywidget and traitlets in `requirements-notebook.in`, but the notebook script dependency headers currently omit them; correct the actual viewing paths and locks together.

Useful primary references:

- Competition: https://marimo.io/pages/events/notebook-competition-3
- Rubric: https://docs.google.com/spreadsheets/d/1xEd-njH43jTWQfr-2wjXULhiGKXl6zEvmKIobWOO8Ks/edit?gid=620363524
- marimo widget integration: https://docs.marimo.io/api/inputs/anywidget/
- Widget lifecycle: https://anywidget.dev/en/afm/
- Bounded chemical-space source: https://gdb.unibe.ch/downloads/

Do not add unrelated models, datasets, an arbitrary molecular editor, or a new web application framework. The distinctive discovery already exists in the saved predictions.

## 4. Scientific facts and claims to preserve

Recompute these reference values from the pinned inputs; never use the review JSON as a replacement scientific source:

| Quantity | Expected result |
| --- | ---: |
| Released train + test records | 7,608 |
| Endpoint columns | 9 |
| Populated numeric endpoint values in the current ML-ready tables | 36,003 |
| Possible molecule–endpoint cells | 68,472 |
| Cells lacking numeric values there | 32,469 |
| Paired held-out LogD/solubility cohort | 2,160 |
| Saved prediction fits per endpoint | 25 |
| Nomination capacity per fit | 50 |
| Union of the fit-specific top-fifty lists | 256 |
| Intersection of all those lists | 1 |
| Ensemble fifty meeting the measured two-property target | 41 |
| Cohort molecules meeting that target | 905 |
| Exact expected passes for a random fifty | 50 × 905 / 2,160 = 20.949074074… |
| Paired numeric Caco-2 evidence among the ensemble fifty | 38 |
| Paired numeric Caco-2 evidence among the 41 target passes | 33 |

Targets remain the existing illustrative LogD interval 1.4–2.9 and KSOL ≥125.5 µM. Preserve the established desirability score, inclusive boundaries, endpoint transform, cohort exclusions, and deterministic ordering. Do not select targets to engineer failure.

The unanimous nomination is **E-0024329**, second in the ensemble ranking. Ensemble-predicted LogD is 1.9990820203, measured LogD is 0.70; predicted KSOL is 317.811799 µM, measured KSOL is 269.0 µM. Across fits, its predicted LogD spans approximately 1.678215–2.260510. It misses the illustrative measured LogD goal despite consistent nomination.

Select this illustrative record using the prediction-only rule “present in every fit's top-fifty list,” and disclose that the surprising example was noticed retrospectively. Do not describe it as prospectively preregistered. If recomputation changes the intersection, stop and investigate provenance/ranking instead of forcing the expected ID.

Each fit's overlap with the ensemble fifty is 21–36, median 29. Fit-specific measured target passes range from 31 to 42, median 38. These fits share methods and overlapping training data. Treat fit disagreement as selection sensitivity; it is not calibrated experimental uncertainty, an independent ensemble of expert opinions, or a time sequence.

Keep computed descriptors, predictions, measurements, censored bounds, and missing values distinct. Unknown is not failure or zero. A similarity neighbor's assay result does not belong to the selected molecule. Favorable ADMET values do not establish efficacy or clinical success.

## 5. The nine-action experience

Count actual required clicks/gestures, including navigation. Do not add Continue buttons between substantive actions. Scrolling through a long page of boilerplate is not an acceptable substitute for a guided layout. Optional inspection may remain available without being required for the main argument.

| Action | Visitor does | Required observable consequence |
| --- | --- | --- |
| 1 | Pull back, or skip motion | Experiences a counted scale transition and enters the real evidence collection. |
| 2 | Select one training seed | Sees its real profile, structural context, and compatible recorded proposals. |
| 3 | Select a ChemLlama proposal | Retains that exact candidate in a persistent tray, with experimental unknowns. |
| 4 | Scrub saved model fits | Changes nominations, structure inspection, and Python-derived fit statistics; discovers the unanimous record. |
| 5 | Commit the ensemble fifty | Freezes the explicitly labeled ensemble shortlist for the retrospective investigation. |
| 6 | Reveal measurements | Sees same-ID movement, the unanimous record's target miss, and the full useful enrichment result. |
| 7 | Expand the ADMET question | Reveals Caco-2 for the same fifty, preserving favorable earlier results and showing missing evidence. |
| 8 | Return to my proposal | Restores the original seed/candidate next to encouraging measured examples. |
| 9 | Choose the next assay | Updates an actual candidate-specific decision record in Python. |

Action 4 is one exploration gesture, not 25 clicks. Supply keyboard equivalents and a concise summary without requiring traversal of all fits. The visitor explores individual fits, then explicitly commits the ensemble list. Never silently commit the last individual fit while reporting ensemble outcomes.

Expose the three seed options and a small first set of proposal cards as direct one-click choices. Use direct assay choices at the end. A dropdown that must be opened and then selected adds actions; do not count that as one click. Additional proposals and detailed search may be optional. Selecting a card should also perform the corresponding story transition without a separate confirmation button.

Do not require a separate selection click to understand the unanimous example: focus it automatically by the transparent prediction-only rule. Optional clicks can inspect other molecules. Defaults must be useful and reversible; a selected default is not evidence the visitor actively chose it.

## 6. Opening: counted scale and accumulated effort

Build a small custom scale component. Start with one schematic possibility and pull back through grouped counts: one, thousands, millions, billions, and approximately 166 billion in GDB-17. Verify the source's exact scope before finalizing captions.

The transition must preserve understandable units: show what one tile or group represents at each level. Use deterministic aggregation and geometric zoom/level-of-detail changes, not a row of labels fading in or increasingly large bubbles. Clearly label schematic/logarithmic compression. Do not attempt to render billions of marks or imply that you did.

Keep animation roughly 8–12 seconds maximum, skippable immediately, without forced waiting. Reduced motion shows the same count hierarchy and comparison. The one-per-second arithmetic yields approximately 5,260 years; “about 5,300 years” is appropriate. Label this hypothetical inspection, never laboratory throughput or time required to discover a drug.

Explicitly change context to ExpansionRx. It is not a highlighted subset of GDB-17, and their ratio is not humanity's coverage of molecular space. Do not place a real ExpansionRx molecule into the enumeration unless membership is actually established.

Then expand a real training molecule's nine-slot evidence strip into the recorded collection. At close range, show actual endpoint records; at wider scales, aggregate counts by family/endpoint with meaningful units. Preserve the selected training record as an anchor. Full-dataset coverage counts may appear, but held-out property outcomes must remain hidden before the retrospective reveal. Use training records for individually inspectable early profiles.

Show that recorded assay values represent accumulated evidence, while gaps remain. A brief design → make → purify → measure → interpret sequence may explain laboratory work, clearly labeled as schematic rather than the molecule's documented history. Do not invent elapsed years, staff, costs, failed syntheses, or chronological optimization trails. Missing ML-ready values can include censored/excluded observations; preserve that distinction.

## 7. Main component: MoleculeEvidenceLens

Implement one reusable anywidget with a small number of modes. This is a proposed local component, not an existing package. Its purpose is to preserve molecule identity while changing the displayed source of evidence.

Keep three stable visual areas:

1. A primary exploration viewport and its active control.
2. A molecule card with readable RDKit depiction, ID, nine-slot evidence strip, and exact values.
3. A compact fifty-slot selection tray and caption identifying the population, model, and evidence state.

The early generated proposal stays in a distinct retained-candidate tray. Do not let selecting a retrospective molecule overwrite the user's generated-candidate ID.

### Nomination mode

- Display the 256-molecule union as a fixed-order mosaic or matrix. A compact overview can aggregate at low zoom, with readable records on selection. Caption it as a nomination layout, not chemical geometry.
- Use deterministic order, for example inclusion frequency descending, ensemble score descending, ID ascending. Confirm the order uses no outcomes.
- Scrubbing a discrete fit index changes which fifty records are nominated. Their locations stay fixed so membership changes are visible. The tray, active repeat/fold label, overlaps, and molecule details update together.
- Show the union/intersection counts for the full 25-fit collection. If a counter tracks only fits visited so far, label that separate quantity accurately.
- Mark the unanimous candidate consistently without giving it a “certain success” badge. Make its 25/25 nomination count inspectable.
- Do not interpolate fictitious model fits. Animation between fit selections is a display transition; numerical predictions come from an actual selected fit.
- Keep the chosen generated proposal separate from this held-out cohort and its published ADMET predictor.

### Prediction-to-measurement mode

- After ensemble commitment, display all fifty IDs in a LogD/KSOL property plane with numerical axes, units, and the chosen target region.
- On reveal, animate those exact IDs to measured coordinates. Maintain a stable coordinate system during the transition. Show a ghost origin/connector for the selected record and exact before/after values.
- If using logarithmic solubility coordinates, apply the transformation consistently and label it. Handle zero values explicitly; never clamp them silently into a misleading location. Derive a suitable domain from the committed display data or flag out-of-domain values visibly.
- Animation intermediates are not assay observations, molecular conformations, time evolution, or uncertainty bounds. Prefer a short transition with a clear final state and a replay option after disclosure.
- E-0024329 must visibly exit the selected target on LogD, while the aggregate simultaneously shows 41/50 passes and the random reference. Do not use an isolated error example to imply the whole shortlist failed.
- Compute the exact random expectation analytically. Use the existing seeded simulation or an appropriate exact distribution for random-shortlist variation; label what any interval means. A shaded band described in prose must actually be drawn.

### Expanded ADMET mode

- Reveal Caco-2 with its own committed action/state, for the unchanged ensemble fifty.
- Expand the selected molecule's assay strip and provide a coordinated Papp/efflux view with units. Changing property axes must be explicit; do not visually interpolate LogD into a permeability value as if they were commensurate.
- Retain the 38/50 and 33/41 coverage denominators. Records without paired numeric evidence remain selectable in the tray and evidence card.
- Keep initial target success visible when another endpoint is unfavorable or unknown. Do not relabel all missing records as failures.
- Connect every point/table/tray selection to the same inspected ID and card. No selectable chart should be disconnected from the rest of the notebook.

Use E-0023839 as an inspectable broader-profile contrast and E-0021738/E-0024328 as encouraging measured examples, with transparent example-selection rules and the complete shortlist accessible. Preserve units and actual values. Do not invent mechanisms or causal tradeoffs.

## 8. Implementation architecture and functions

Use the existing scientific helpers as the source of truth. Add focused functions where needed, not a new pipeline. Suggested layout is `widgets/molecule_evidence.py`, `widgets/molecule_evidence.js`, `widgets/molecule_evidence.css`, plus a small scale component or shared rendering module. A comparable simpler layout is acceptable; avoid a generic visualization framework.

Implement these responsibilities with explicit inputs/outputs. Names are suggested; scientific behavior is mandatory:

### `build_fit_nomination_data(...)`

- Read the pinned saved predictions, restrict to the existing 2,160 IDs, and retain exactly the selected LGBM LogD/LogS endpoints.
- Validate unique `(molecule_id, repeat, fold, endpoint)` records and the same 25 fit keys for every molecule and endpoint. Pair endpoints by their actual repeat/fold keys before scoring; never pair two independently sorted arrays.
- Reuse the existing score/transform/constants and stable top-k tie-break. Keep ensemble scoring identical to the established path; averaging individual scores need not equal scoring averaged endpoints.
- Return sorted fit keys, each fit's ordered fifty IDs, union order, inclusion counts, intersection IDs, ensemble shortlist, and fit-to-ensemble overlaps.
- Include prediction records needed for all inspectable union molecules, not only the ensemble fifty. Separate prediction-only selection data from subsequently revealed measurements.
- Cache using source hashes, analysis config, cohort identity, tie-break rules, and schema version. Store the 256 × 25 display subset rather than repeatedly querying the full parquet on interaction.

### `build_molecule_evidence_records(...)`

- Join by validated canonical IDs. Include structure identity, provenance role, each endpoint's numeric value/unit/status, and source references as available.
- Use explicit measured, predicted, computed, missing, and censored/bounded representations. JSON null represents absence; forbid NaN/Infinity in serialized output.
- Include nearest-training context for every inspectable record, not just the ensemble fifty. Preserve the analog's own incomplete assays. Keep all-training nearest-neighbor behavior and fingerprint settings unchanged.
- Generate structure SVGs with the existing verified RDKit path. Preserve stereochemistry and depiction metadata. Do not substitute a SMILES text box for the primary molecular depiction in the portable version.

### `build_visual_payload(...)`

- Assemble versioned records, deterministic array order, fit metadata, nominations, depiction assets, endpoint definitions, target constants, evidence-accounting data, and generation provenance.
- Key records by ID or validate any integer-index map in both directions. Record source and derived-artifact hashes.
- Include the full inspectable union and needed training neighbors, three seeds, and all valid approved generated candidates. Do not limit the payload to twelve gallery entries or only fifty outcomes.
- Keep payload size measured and reasonable. Reuse depiction references; do not repeat a large SVG for every fit. Use selective rendering and caching instead of making hundreds of full-size DOM structure cards at once.

### `active_budget_reference(...)`

- Correct the current semantic mismatch: `random_expected_passes` currently returns the simulation mean, and an existing test expects 20.993. Return the analytic expectation under that name. If retaining the Monte Carlo mean, give it a distinct explicit field.
- Update the meaningful expectation test to 50 × 905 / 2,160. Preserve deterministic variation calculations and all unrelated historical score regressions.

### Widget bridge and rendering

- Use `mo.ui.anywidget(...)` and synchronized traits for meaningful committed state: active fit key, selected retrospective ID, generation seed/candidate IDs, evidence stage, and assay choice as appropriate.
- Send selected IDs and discrete choices to Python; derive downstream tables/captions/cards from those values. Demonstrate real reactive updates, not merely a browser-local text replacement.
- Keep continuous pointer position, zoom interpolation, and animation progress frontend-local. Synchronize a fit selection on pointer release or at a bounded rate; ensure the final displayed fit and Python result agree.
- Use Canvas for dense marks if needed, SVG for axes/labels and the fifty-point transition, and HTML/CSS for cards. Plain JavaScript is sufficient. If adding D3 or another library, pin and package it deliberately; avoid unreliable floating CDN imports.
- Use requestAnimationFrame for movement, responsive sizing, high-DPI Canvas handling, stable keyed marks, and cleanup of listeners/observers/timers on rerender/disposal. Escape text and handle only locally generated trusted SVG markup.
- Do not recompute chemistry, rankings, or nearest neighbors on every animation frame. Do not run model inference during viewing.

## 9. State and disclosure contract

Write a compact state transition table in `docs/story_state_machine.md` and implement it. Suggested state separates:

- Generation context: `seed_id`, `candidate_id`.
- Retrospective exploration: `active_fit_key`, `inspected_molecule_id`.
- Commitment: exact `committed_ids`, selection kind `ensemble`, count 50.
- Disclosure: `measurements_revealed`, `caco_revealed`.
- Ending: `returned_to_proposal`, `next_assay`.

Use one canonical owner for each piece of state. Avoid duplicated frontend/Python states that disagree or a marimo dependency cycle. Validate event IDs/fit keys before using them.

Reset rules:

- Changing seed clears an incompatible generated-candidate selection and old candidate-specific assay decision. It need not invalidate the unrelated retrospective evidence investigation.
- Changing the generated candidate updates the retained tray and final decision record; never transfers the previous candidate's identity or measurements.
- Scrubbing fits before commitment changes exploration only. The commit action explicitly selects the ensemble fifty.
- After commitment, exploratory fit browsing must not silently replace the committed set. An optional explicit restart clears retrospective disclosure state.
- The first reveal cannot expose Caco-2, broader outcome tables, or outcome-selected examples prematurely. The second reveal cannot occur before the first.
- Returning preserves the exact selected proposal. A final assay choice changes a real decision record, never fabricates an assay result or commissions laboratory work.

Disclosure is a teaching device, not a secrecy/security boundary: the dataset is public. Prevent accidental spoilers in visible tooltips, hidden-but-open accordions, counters, and lower cells. There is no need for encryption or access controls around public outcomes.

## 10. ChemLlama continuity and hopeful ending

Keep the approved generation visible early and return to it late. Identify outputs as cached samples from recorded seed prompts. The current raw-SMILES continuation probe does not establish documented conditional analog optimization; retain that limitation in concise provenance.

Show actual batch denominators and invalid outputs without framing this pilot as a general model-quality benchmark. Keep computed descriptors clearly labeled. Perform exact rediscovery checks if necessary; if a candidate exactly matches a measured record under the defined identity policy, label that case accurately rather than asserting it is unmeasured.

The ending must include:

- The same seed/candidate structures and IDs chosen earlier.
- Their actual knowns and unknowns.
- Encouraging measured property profiles, with a transparent selection rule and no clinical claims.
- A concise next-assay control whose output includes the candidate ID, question, and how the answer could change a decision.

Do not imply that the retrospective LGBM analysis tests ChemLlama or that the proposed assay is mathematically optimal without a value-of-information model. It is a reasoned next question.

## 11. Visual and editorial requirements

Use a coherent typography, spacing, color, and evidence-state system across the scale component, main widget, and notebook. Keep one main focal area per scene and readable molecular structures. Favor direct manipulation, clear labels, and meaningful motion over particle effects or ornamental 3D.

Reduce the opening prose to a question and a short promise. Explain each discovery after or beside its interaction. Keep detailed derivations and long provenance in optional methods while leaving essential distinctions visible.

Do not bake every conclusion into static text. Generate counts/captions from the actual state and data. Every interactive control must produce an observable consequence. Avoid unused selectable tables, redundant controls, repeated giant tables, and disconnected chart styles.

Provide keyboard selection, visible focus, non-hover access to values, responsive layouts, adequate contrast, and reduced motion. Do not rely on red/green alone. The motion-free route must preserve identity, scale, and discoveries.

A reviewer should be able to share a screenshot of the main widget and identify its question, molecular subject, and evidence state without the entire surrounding essay. A screenshot alone does not establish interactivity.

## 12. Native and portable entry-point parity

The project contains a native notebook and a browser/WASM companion; README links the latter. Treat the user-facing entry point as part of the deliverable. Do not produce a polished local notebook while leaving the shared experience as an older chart sequence or SMILES-only view.

Use the same widget renderer, styles, payload schema, and scientific selection logic in both paths. The bundle builder may precompute RDKit depictions and expensive scientific results so the browser does not need native RDKit/DuckDB. Lightweight Python state/filtering/caption updates should still demonstrate marimo reactivity in the browser path.

Extend `scripts/build_molab_bundle.py` and its tests to include fit nominations, required evidence records, SVG depictions, provenance, and all widget assets. Version the schema and validate compatibility. Keep statistical computations shared or precomputed from one tested source; do not maintain subtly divergent ranking implementations in two notebooks.

Update script dependency headers, requirements, locks, bootstrap file lists, and bundling together. New Python/JS/CSS files must actually travel with the notebook. Prefer a small shared module or a reproducibly generated portable artifact to manually copied widget code.

Pin remote code/assets/data to an immutable revision with integrity checks where used. The current bootstrap references mutable `main`; do not silently reuse stale cached helper files after widget/schema changes. A new unpublished revision cannot be fetched remotely, so validate a local portable bundle first and describe the pending publication step honestly.

Do not assume anywidget works in the actual molab/WASM target merely because native execution succeeds. Test the intended route. If it cannot support the component, pursue a supported native molab route within existing authorization and make the actual intended submission path explicit. Do not claim parity or remove the functioning entry point without a tested replacement.

## 13. Implementation sequence

1. Inspect/back up current work; identify the actual native and portable entry points and dependency versions.
2. Implement and verify nomination/evidence payloads, including the exact random expectation correction.
3. Build the first complete interactive slice: scrub fits → inspect unanimous molecule → commit ensemble → reveal its actual measurement alongside cohort enrichment. Use real data immediately.
4. Validate that slice in a live kernel-backed browser and the intended portable environment. Resolve lifecycle/dependency/state problems before expanding the story.
5. Add coordinated Caco-2 disclosure, evidence strips, generated-candidate persistence, and the final assay decision.
6. Build the counted scale and recorded-evidence opening using the same visual language.
7. Integrate the nine-action guided path, optional methods/exploration, responsive styling, keyboard navigation, and reduced motion.
8. Run scientific, browser, portability, and fresh-cache checks; fix failures. Update status and walkthrough to the tested implementation.

Proceed through all steps. The first slice is an internal milestone, not the final deliverable or an automatic request for user approval.

## 14. Validation and acceptance gates

Run the repository-required `pytest` suite and relevant marimo checks for both entry points. Run executable exports and verify a fresh local portable bundle. Preserve historical pilot regressions. Add tests for meaningful scientific/state invariants rather than asserting incidental CSS strings.

Required scientific checks:

- Correct per-ID/per-fit endpoint pairing; duplicate or missing keys fail clearly.
- Reproducible fit nomination union/intersection, unanimous ID, ensemble ranking, and target outcomes.
- Perturbing observed values cannot change nominations, thresholds, layout order derived from predictions, or the unanimous selection rule.
- Exact random expectation and correctly labeled variation calculations.
- Same fifty IDs across prediction, measurement, and Caco-2; correct coverage and missing/censored representations.
- Correct record identity in depiction and training analog context, including incomplete analog assays.
- Pinned generation/provenance and retained proposal identity; no fabricated measurements.
- Native and portable payload/results agree; malformed schemas, non-finite JSON values, unknown IDs, and hash mismatches are handled explicitly.

Live browser verification is mandatory before claiming interactive completion. Repair the stale label selectors in `scripts/validate_story_browser.py`, preferably using stable accessible names/test IDs. A failed Chromium launch is a problem to diagnose; use an isolated compatible runtime/dependencies where possible. Do not equate static HTML export with successful interaction.

Exercise these behaviors with screenshots and a compact machine-readable interaction log:

1. Scale marks/units, skip, and reduced-motion route are understandable and work.
2. Every seed filters compatible proposals; selecting a different candidate propagates to Python and persists later.
3. Fit scrubbing changes actual nominations and Python-derived counts; final pointer/keyboard selection matches the displayed repeat/fold.
4. Selecting a chart/matrix/tray record updates its correct structure and evidence card.
5. Ensemble commitment records exactly the canonical fifty and cannot be confused with a fit-specific fifty.
6. Before disclosure, visible outcomes do not leak; first and second reveals remain distinct.
7. Same-ID transition ends at actual coordinates and preserves the correct selected record, including E-0024329.
8. Positive enrichment, target miss, and missing ADMET evidence remain visually distinct.
9. Returning restores the exact generated candidate; assay selection changes its decision record in Python.
10. Replay, reset, rapid scrubbing, resize, keyboard use, reduced motion, and fresh-kernel restart do not desynchronize state or accumulate duplicate listeners.
11. The same essential interactions and structure depictions work in the actual intended submission environment.

Count required actions on the actual default path. Record startup and interaction timing on the measured environment without inventing performance claims. Record screenshots at scale, fit disagreement, measured reveal, Caco-2, and final candidate states; verify state/IDs as well as images.

If an external restriction prevents an execution gate, finish independent work and report that gate as incomplete with exact evidence. Do not rewrite the walkthrough to pretend the test happened. Do not claim a human usability study unless someone actually performed it.

## 15. Handoff and completion

Update `README.md`, `IMPLEMENTATION_STATUS.md`, `docs/story_state_machine.md`, and `docs/submission_walkthrough.md` to match the implementation. Keep historical source/inference records. Remove outdated current-scope claims or clearly mark them as historical.

Provide:

- The two relevant notebook paths and the actual intended submission entry point.
- Local launch instructions, a private authenticated launch URL where available, and the portable bundle path. Do not persist access tokens in tracked docs or public artifacts.
- A concise description of the custom components and the scientific discoveries they expose.
- The verified required action count and a short walkthrough recording or screenshots.
- Scientific/browser/portable checks performed, results, and exact unresolved limitations.
- A source/AI-assistance acknowledgment appropriate to the competition. Check licensing and attribution before reusing others' actual code or artwork; the preferred approach is original code implementing the learned interaction patterns.

The work is complete when the working notebook makes the audience experience scale, accumulated effort, changing nominations, measured surprise, and informed hope through a coherent custom interaction—with scientific correctness and the viewing route demonstrated. More prose, a passing unit-test list, or a widget that only animates decorative marks does not meet this assignment.
