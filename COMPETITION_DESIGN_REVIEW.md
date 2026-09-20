# Competition design review: make the uncertainty tangible

20 September 2026. A source-based reassessment of the earlier story brief.

**Implementation handoff:** execute [CUSTOM_VISUAL_STORY_EXECUTION.md](CUSTOM_VISUAL_STORY_EXECUTION.md). It turns this review into the current detailed implementation contract; this document remains supporting design rationale.

## Verdict

The emotional intention is worth keeping. The current execution and the previous brief do not yet establish a distinctive competition submission. They cover the right topics but permit a sequence of conventional charts, explanatory paragraphs, and reveal buttons. A larger opening number and better colors will not fix that.

The improved premise is: **We can propose far more molecules than we can investigate. Even inside a measured collection, choosing the next fifty depends on an imperfect map. What survives when we change the map, consult the measurements, and ask another ADMET question?**

Keep “Before You Make It.” A useful subtitle is **Fifty experiments. Twenty-five maps. One next decision.** Fifty is an illustrative capacity constraint, not a documented project budget. Twenty-five comes from the actual saved benchmark fits, not an invented game length.

This review refines the narrative and visual priorities in `STORY_EXPERIENCE_REWORK.md`. Preserve its provenance, evidence distinctions, accessibility, H100-only inference restrictions, and maximum ten required interactions. The proposal below is not an implementation report. No notebook changes or inference jobs were performed for this review.

## What the competition actually rewards

The published weights are creativity 20%, interaction/workflow 20%, presentation/shareability 20%, customization 20%, code 10%, and chemical validity 10%. The customization criterion asks for a purpose-built widget/package integrated into the reactive workflow. Scientific correctness is essential, but accumulating validation checks alone leaves most of the rubric unaddressed. [Rubric](https://docs.google.com/spreadsheets/d/1xEd-njH43jTWQfr-2wjXULhiGKXl6zEvmKIobWOO8Ks/edit?gid=620363524).

The event emphasizes a focused question, intuition, chemical validity, originality, and useful extensions. It explicitly discourages a dataset summary and does not require beating predictive benchmarks. A runnable molab submission remains mandatory. The rubric retains some wording about papers from the earlier format; the current event description establishes the ADMET task. [Competition description](https://marimo.io/pages/events/notebook-competition-3).

Do not infer Pat Walters' private preferences or predict a judging score. Use the published criteria and demonstrate chemically inspectable evidence.

## What the examples teach us

All four distinct notebooks were inspected at source level. The duplicate Dead Salmon link was counted once. The hosted Neural Thickets fork and denoise source were extracted from their public preview HTML; the other two came from the linked gallery repository. Browser rendering could not be verified locally because Chromium failed to launch. These are code/design observations, not a completed live usability comparison or reproduction of their scientific results.

### Neural Thickets

The diamond-search game lets target density alter the experience of searching. The notebook then connects that intuition to model perturbations, task-specific performance, and a sampling-budget extension. The fork defines `PerturbationSamplerWidget` around line 1926, with SVG marks and synchronized traits; its opening game is a separate HTML iframe. [Notebook](https://molab.marimo.io/notebooks/nb_YTBCBe326sVEFSqhhyGoHa), [published source](https://github.com/akashrma/neural-thickets-molab/blob/main/neural_thickets.py).

Transfer: make scarce experimental attention tangible and connect the metaphor to actual data. Do not copy hidden diamonds as invented drug successes, demand dozens of guesses, or treat an isolated game as marimo reactivity.

### Dead Salmons of Interpretability

`FalsePositiveHunter` at line 241 connects a draggable statistical threshold, a histogram, a grid, and a numerical verdict. The same interaction recurs in different investigations. Other widgets compare attribution, probing, and sparse features. [Source](https://github.com/marimo-team/gallery-examples/blob/main/notebooks/jam-2026-Q2/dead-salmon.py).

Transfer: let the visitor operate the assumption that changes the conclusion. For our notebook, changing the saved model fit must visibly change the shortlist and update Python-derived counts. Reuse the interaction instead of introducing a new chart grammar in every section. Do not import its multiple-testing argument as an explanation of our ADMET errors without evidence.

### Geometry of Noise

One dimension control links the apple-peel illustration, shell behavior, posterior calculation, and sampler comparison. `ApplePeelWidget` at line 780 and `PosteriorCollapseWidget` at line 1190 turn mathematical relationships into manipulable geometry. Cached calculations and browser-local rendering support exploration. [Source](https://github.com/marimo-team/gallery-examples/blob/main/notebooks/jam-2026-Q2/geometry-of-noise.py).

Transfer: one governing control should change several coherent views. Preserve molecule identity when moving between model fits and measurements. Use precomputed data for animation. Do not copy dimensional-concentration claims into molecular-space explanations; they are different arguments.

### Predict the Image, Not the Noise / denoise

`ManifoldGameWidget` at line 191 introduces a visual distinction that returns in trained-model experiments and a held-out denoising extension. A noise slider controls a fixed set of example images; `CellTour` supplies a guided route. [Notebook and source preview](https://molab.marimo.io/notebooks/nb_c81Tt2cPsKSPJShRB1bLQD), [gallery description](https://marimo.io/gallery/l/predict-the-image-not-the-noise).

Transfer: introduce a visual object early, then return to it with stronger evidence. Reuse the same molecules throughout. Learn from the design without treating every claim as authoritative: for example, its comparator is labeled Gaussian blur but implemented with average pooling. Our own labels must match our computations.

### Shared principle

Each example gives the visitor something specific to manipulate and a reason to care about the resulting change. Visual polish supports that relationship. Novelty comes from the question and the interaction together. More WebGL, more model parameters, and more charts are not substitutes.

## A stronger discovery already exists in our data

Recomputed directly from the pinned prediction parquet and current 2,160-molecule cohort, using the existing score and deterministic tie-breaking:

| Quantity | Result |
| --- | ---: |
| Saved repeat/fold fits | 25 |
| Molecules selected per fit | 50 |
| Distinct molecules nominated across those lists | 256 |
| Molecules selected by every fit | 1 |
| Overlap of each fit's fifty with the ensemble fifty | 21–36; median 29 |
| Ensemble shortlist meeting the measured two-property target | 41/50 |
| Expected passes for fifty random cohort molecules | 20.9491 |

The unanimous molecule is **E-0024329**, ranked second by the ensemble score:

| Property | Predicted | Measured |
| --- | ---: | ---: |
| LogD | 1.9991 | 0.70 |
| Kinetic solubility, µM | 317.81 | 269.0 |

All 25 LogD predictions are within approximately 1.678–2.261, inside the existing illustrative target 1.4–2.9. Its measured LogD falls outside that target. This is a concrete demonstration that selection stability does not guarantee the selected property profile.

Do not call the fits 25 independent experts or uncertainty samples: they share methodology and overlapping training data. Do not call the molecule a failed drug. Do not extrapolate one example into a population-level calibration conclusion. The illustrative example was noticed retrospectively; identify it transparently by the prediction-only rule “present in every top-fifty list,” with the complete cohort available.

The positive result is equally central. Different fit-specific lists produce 31–42 measured target passes, and the ensemble produces 41. Changing nominations does not imply the model has no practical value. Those outcomes are correlated retrospective results, not 25 independent trials.

Machine-readable review evidence: `outputs/notebook_validation/competition-review-20260920.json`. Original calculation: `selection_stability` in `scripts/notebook_data.py`, with endpoint pairing by `(Name, repeat, fold)` before scoring. Preserve the exact cohort restriction.

## The revised story

### 1. Possibilities expand; experimental knowledge has to be earned

Start with a structure-sized mark and pull back through an explicitly schematic hierarchy of counted possibilities. Use the existing sourced GDB-17 example as a bounded enumeration, with clear scale units and a brief duration. Then explicitly change context to the real ExpansionRx collection; never imply dataset membership in GDB-17 or a global coverage fraction.

Make the human effort visible through an expanding evidence strip: a molecular structure has nine potential assay slots, and only recorded evidence fills them. At collection scale, retain actual counts: 7,608 records and 36,003 populated numeric endpoint values in the current ML-ready tables. Missing/censored records need distinct interpretation. These values do not count independent laboratory operations or person-hours.

The thought to evoke: **Even this small collection contains a great deal of work. Knowing the structure is only the beginning.**

### 2. AI makes more possibilities available

The visitor chooses a real training seed and a genuine cached ChemLlama proposal. The proposal has a readable structure, computed descriptors, seed-prompt provenance, and an unfilled experimental profile. Keep it visible in a small persistent tray.

Generation must not magically fill its assay slots. Maintain the documented prompting limitations and actual batch accounting. Do not claim the generator is an optimized ADMET navigator based on this pilot.

Transition to a separately labeled retrospective investigation: we have existing predictions and measurements for that collection, so we can examine how choices held up. These measurements do not validate the generated candidate or ChemLlama.

### 3. Let the visitor discover that the map changes

A single scrub across the 25 saved fits changes which fifty molecules are nominated. Stable molecule IDs remain in place in a nomination matrix; selected cells illuminate for the active fit. A connected fifty-slot tray and structure card update alongside it. At the end of the gesture, summarize 256 distinct nominations and one unanimous choice.

The user experiences scarcity through a fixed fifty-slot capacity, without making fifty selections. No arbitrary success density, fake laboratory wait, or repeated clicking game is required.

Focus the unanimous molecule using the prediction-only rule before displaying its outcome. Ask the reader to consider whether agreement is sufficient. This can be a short prompt without another mandatory click.

### 4. Reveal measurements with a visible consequence

Commit the explicit ensemble shortlist for the canonical path. Clearly label the distinction between exploring individual-fit nominations and committing the ensemble's list.

Morph each of those same fifty molecules from its predicted LogD/solubility coordinates to its measured coordinates. Keep numerical axes, target region, selected ID, and endpoint values legible. Show ghost origins or connectors for an inspected molecule. This is movement between estimates and observations, not physical molecular motion or an experimental trajectory.

The unanimous molecule visibly leaves the chosen target. Its structure and nine-slot profile remain anchored. Alongside this, show the full 41/50 outcome and exact random expectation, with correctly labeled random-selection variability.

The takeaway is precise: **Agreement can be reassuring. Measurements can still change the decision. And the model can still help us spend our limited attention well.**

### 5. Widen the question without erasing success

Reveal Caco-2 separately for the unchanged fifty. Expand the evidence strip from the first two endpoints to permeability and efflux. Keep favorable two-property results visibly favorable; additional information is a different question.

Show the actual contrasting profiles, including E-0023839 and the encouraging E-0021738/E-0024328 examples. Preserve coverage: 38 of fifty have paired numeric Caco-2 values, including 33 of the 41 initial target passes. Missing evidence must remain an explicit state.

Do not manufacture a survival funnel by adding thresholds until only one molecule remains. Use transparent example-selection rules and avoid suggesting that one property change caused another.

### 6. Return to the original proposal with better judgment

Restore the visitor's exact ChemLlama candidate. Its experimental strip is still unfilled. The measured investigation has changed the visitor's understanding, not the candidate's evidence.

Offer an actual next-assay choice and update a Python-derived decision card explaining what that assay could resolve. Keep the encouraging measured examples nearby. The ending connects scale to agency: we cannot inspect everything, but we can make the next question precise.

## The signature visual instrument

Build one main reusable `MoleculeEvidenceLens` anywidget, supported by a small scale introduction. This name is a proposed component, not an existing package. Its purpose is to preserve molecular identity across nomination, prediction, measurement, and partial profiles—something a stack of independent charts currently does poorly.

Suggested composition:

- A main viewport with the active view and one direct control.
- A persistent molecule card: RDKit depiction, ID, nine-slot evidence strip, and exact values.
- A compact fifty-slot selection tray and a caption stating which population/model/evidence state is shown.

The fit view uses a fixed-order 256-by-25 nomination matrix or aggregated overview with zoom to readable rows. Do not draw 256 overlapping rank ribbons. The outcome view uses a real property plane with units. Transition between those layouts explicitly; do not imply that screen distances in a nomination matrix are chemical distances.

Visual semantics must be consistent: predicted marks have one outline treatment, experimental marks another, missing cells use a visible empty/hatched state, generated proposals carry their own provenance badge. Favor readable molecular structures over decorative atom balls. Censoring must remain distinguishable from absence.

A selected ID, active fit, and committed evidence state must synchronize through `mo.ui.anywidget` to Python. Python computes the shortlist, overlaps, evidence card, and comparison statistics. Keep transient animation frames in the browser, and clean up listeners. Pin payload schemas, ordering, and derived artifacts. [Official marimo integration](https://docs.marimo.io/api/inputs/anywidget/).

Reuse verified RDKit/marimo chemistry rendering. Do not rebuild structure parsing or invent a molecular editor to collect customization points. Avoid smooth interpolated ADMET heatmaps across unknown chemistry: their visual confidence would exceed the evidence.

## Nine actions, with optional depth

| Action | Consequence |
| --- | --- |
| 1. Pull back / skip motion | Understand bounded scale and enter the real evidence collection. |
| 2. Select a training seed | Establish real measured context. |
| 3. Select a cached proposal | Keep this exact unmeasured candidate in the persistent tray. |
| 4. Scrub the model fits | See nominations change; inspect the single unanimous choice. |
| 5. Commit the ensemble fifty | Freeze the explicitly identified retrospective selection. |
| 6. Reveal measurements | Watch same-ID movement; see the unanimous example and full enrichment result. |
| 7. Expand the ADMET question | See Caco-2 contrast and incomplete coverage. |
| 8. Return to my proposal | Restore its unchanged evidence alongside measured reasons for hope. |
| 9. Choose the next assay | Update the candidate's actual decision record. |

Point inspection, all-fit tables, methods, nearest analogs, and alternative budgets are optional depth. Do not add Continue buttons between these actions. A scrub is one exploration gesture, not 25 required clicks. Keyboard access should allow a short equivalent path; count actual navigation requirements in browser testing.

## Specific weaknesses in the current code

- `before_you_make_it.py:89`: the opening explains the entire journey before the visitor experiences it. Reduce this to a question, a promise, and the first visual.
- `before_you_make_it.py:146`: the scale view uses growing circles and CSS-animated labels. The “Pull back” control does not deliver semantic zoom or preserve a counted visual unit across scales.
- `before_you_make_it.py:202`: endpoint coverage is a stacked bar chart. Useful analytically, but it does not deliver the record-to-collection transformation described in the story.
- `before_you_make_it.py:305`: prediction and measurement appear as separate facets. The code says the same fifty move, but the visual does not animate that movement or link a selected point to inspection.
- `before_you_make_it.py:334`: the Caco-2 chart is another independent view. Returned Altair selections are not consumed by the inspection dropdown.
- `before_you_make_it.py:370`: stability is text in a detail view despite containing the strongest newly identified interaction opportunity.
- `scripts/validate_story_browser.py`: several expected labels are stale relative to the current notebook. It does not verify the proposed fit interaction or full selection propagation. Do not treat the presence of this script as browser acceptance evidence.

These observations describe source inspected on 20 September, not a screenshot-based aesthetic review. The implementation has improved its scientific staging since the original six-step summary; the next priority is coherent interaction and presentation.

## Execution priorities

1. Verify and cache the 25-fit nomination matrix, 256-union/one-intersection counts, and unanimous example. Include deterministic ranking and exact cohort IDs. Use exact random expectation `50 * 905 / 2160`; simulations supply variation, not the analytic expectation.
2. Build one working fit-scrub → selected structure → Python result flow. This is the first prototype acceptance gate. It must reveal something without a paragraph explaining what to notice.
3. Extend that same component into the predicted-to-measured reveal, including the positive cohort result. Validate identity conservation.
4. Add the expanded evidence strip and retained ChemLlama proposal. Confirm generated and retrospectively measured objects cannot be confused.
5. Rebuild the opening around actual visual scale and recorded evidence. Keep it short enough that the central experiment remains the main event.
6. Apply a coherent visual system: readable structure size, restrained palette, deliberate typography, generous spacing, one focal view, consistent axes and labels. Test the default view and a narrow window.
7. Finish an actual molab run, live interaction checks, and a concise walkthrough. Preserve the existing limits on external publishing and submission.

Do not start with another inference batch, more datasets, a new predictive architecture, a dozen plots, or a complete general-purpose visualization library. Existing data already contain a distinctive story. A compact reusable widget is enough if it solves the actual presentation problem.

## Acceptance questions

- Can someone describe the nomination disagreement after a single gesture?
- Can they follow the same molecule through the reveal without reading its ID twice?
- Can they explain why unanimous nomination is different from measured success?
- Does the notebook make both human evidence accumulation and missing knowledge visible?
- Is the model's useful enrichment as visible as its mistakes?
- Does the final proposal retain its actual unknowns while giving the visitor a meaningful next choice?
- Would the central interaction be worth sharing even with the introductory prose removed?

Scientific checks and browser tests establish correctness and functionality. A short observed walkthrough with a new reader is still needed to establish whether the intended surprise and clarity actually land. Winning remains uncertain; this direction makes the submission more distinctive and better aligned with the published criteria.
