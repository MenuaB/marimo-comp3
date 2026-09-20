# Before You Make It — restore the experience and the sense of scale

Corrective execution instructions, 18 September 2026.

**Superseded for story and UI execution by [CUSTOM_VISUAL_STORY_EXECUTION.md](CUSTOM_VISUAL_STORY_EXECUTION.md), 20 September 2026.** Read that brief first. Retain the scientific and provenance safeguards below where compatible; the newer brief specifies the model-fit interaction, custom components, and deployment parity.

Read this before continuing implementation. It refines and takes precedence over the narrative, ordering, and presentation instructions in `AGENT_EXECUTION_PLAN.md`. Its data-integrity, H100-only, provenance, testing, and publishing boundaries remain in force.

## 1. What you are fixing

The current notebook implements useful analysis, but it has not delivered the agreed experience. It begins with scoring/data accounting, appends ChemLlama at the end, has no persistent visitor-selected seed/proposal, and lacks the vastness/human-effort opening and earned hopeful ending. The Caco-2 section appears with the first reveal instead of creating a second discovery. Some selectable tables do not drive anything downstream. The final instruction to choose an assay has no corresponding control.

Preserve the actual scientific work and model outputs. Rework their orchestration and presentation so a visitor can experience the reasoning. Do not respond by only improving prose, adding section headings, changing colors, or writing a more impressive summary than the notebook supports.

The user wants the visitor to leave thinking:

> I had not understood how enormous the possibilities are, how much work sits behind each measured point, and how much judgment is needed to turn an AI suggestion into a useful next experiment.

Make the notebook deliver that realization through scale, continuity, consequential interactions, and evidence. Do not claim a guaranteed competition win.

## 2. Preserve what is already real

- Keep the audited sources, existing baseline regressions, Caco-2/stability calculations, and corrected cache/analog behavior unless verification finds an actual defect.
- Preserve ChemLlama main run `chemllama-271948`, its raw log, manifest, and candidates. Current summary: 96 raw samples, 27 unique valid candidates, 69 invalid records, zero duplicates. Preserve smoke/failed-run history as documented.
- These generation counts are pipeline results under the recorded prompt/parser/config. They do not establish the checkpoint's general validity rate. The current config describes a raw-SMILES continuation probe with undocumented conditioning semantics; do not silently promote it to proven seed-conditioned analog generation.
- Verify the run's candidate relationships and parsing before making visual claims about generated neighbors. Log any necessary parser reprocessing as a new derived artifact; never silently overwrite original raw evidence.
- Do not rerun generation to find prettier examples. If a technical defect genuinely requires another run, use the existing authorized H100-only workflow and preserve all attempts. A6000 remains prohibited.
- Pin the approved run in notebook configuration and verify its manifest/artifact hashes. Do not select whichever candidates file has the newest modification time.

## 3. Creative direction: one journey with objects that persist

Working title remains **Before You Make It**. Suggested subtitle: **An enormous search. A few experiments. One next decision.**

Build one guided journey through a chemical decision. Keep a selected structure, its identity, and its evidence recognizable as the visitor moves between views. The visitor should develop a stake in one real proposed molecule, then return to it with better judgment.

Use these emotional transitions deliberately:

1. **Awe:** this small drawing belongs to a staggering range of possibilities.
2. **Respect:** experimental knowledge is accumulated by people, compound by compound and assay by assay.
3. **Temptation:** AI can propose many more things to try.
4. **Commitment:** a limited experimental budget forces a choice.
5. **Surprise:** real measurements change some of those expectations.
6. **Reconsideration:** even an accurate answer can answer too narrow a question.
7. **Hope:** some measured profiles are encouraging, and we can choose a better next experiment.

Use a concise piece of copy beside each discovery. Put technical derivations, lengthy disclaimers, and implementation commentary in optional methods. Keep the scientific distinctions visible without covering the main screen in caveats.

## 4. The opening must make scale felt

Implement a short, skippable powers-of-scale sequence with meaningful labels. A static star field, rotating molecule, or an enormous exponent printed on a slide is insufficient.

Suggested construction:

- Begin close enough to understand one schematic molecular possibility.
- One action, **Pull back**, traverses several orders of magnitude, e.g. 1 → 1,000 → 1,000,000 → 1,000,000,000 → approximately 166 billion.
- At each level state what a visible mark represents. Use deterministic aggregate marks; do not imply the browser is drawing billions of individual structures.
- End at a **bounded enumeration**: GDB-17, molecules containing up to 17 atoms of the enumerated non-hydrogen elements. Verify exact scope/count against the primary source before finalizing the caption.
- Offer one understandable arithmetic comparison: **Even at one molecule every second, without stopping, 166 billion would take about 5,300 years.** Label this a hypothetical inspection rate, not the speed or duration of laboratory research. Calculate it reproducibly; do not imply 5,300 years are required to discover a drug.
- The visual scale changes must make it clear that the first screen was a tiny local view. Explicitly indicate any nonlinear/logarithmic scale or schematic compression.
- Keep the whole transition roughly 8–12 seconds with immediate skip. No forced watching, repeated clicking, sound, or continuously looping animation.

Then make an explicit contextual cut: **Now enter one real collection that people measured.** ExpansionRx is a different collection, not a highlighted subset of GDB-17. Do not carry an actual ExpansionRx structure into the enumeration as if membership were established. Do not calculate a global coverage fraction from these unlike collections.

Reduced motion must show the same scale landmarks, mark meanings, and arithmetic without animation. A visitor who skips motion must still understand the scale.

Source: https://gdb.unibe.ch/downloads/

## 5. Make the work behind a measurement tangible

After the scale opening, show one real official-training molecule with a compact nine-endpoint evidence strip. Populate cells from actual source data; preserve unknown/censored states. Explain the two endpoints that drive the main decision, then reveal how much broader experimental profiling can be.

Let that one record expand into the real collection. A progressively aggregated evidence matrix can show the accumulation of recorded values while retaining a connection to the original molecule. It must support a real family/seed selection through marimo rather than becoming a disconnected animation.

Reference counts verified from the current pinned ML-ready train/test tables:

- 7,608 released molecules across both splits.
- Nine challenge endpoint columns.
- 36,003 populated numeric molecule–endpoint values.
- 68,472 possible cells in that nine-column table; 32,469 lack numeric values there.

Recompute these in Python using the explicit nine endpoint columns. Call them **recorded assay values**, not 36,003 independent experiments or 36,003 synthesis attempts. ML-ready absent values include excluded out-of-range measurements as well as unavailable measurements; explain that distinction and preserve raw-source bounds.

Use a short schematic sequence for a record: design → make → purify → measure → interpret. This is explanatory context, not a reconstruction of that molecule's actual history. Do not manufacture time, expense, headcount, number of optimization cycles, or failed synthetic routes.

Suggested copy:

> Each filled cell is a piece of experimental evidence. A structure alone cannot fill the rest.

The visual should convey the scale of accumulated knowledge while exposing its uneven coverage. Avoid making human research feel futile; this evidence is precisely what makes modeling and better decisions possible.

## 6. A concrete nine-action path

The main path may require **at most ten actual user actions**, preferably the nine below. Count clicks/gestures, including Continue/navigation actions. Deeper exploration, replay, and keyboard alternatives are optional, not additional mandatory work. Target approximately three minutes without forcing timing.

| Action | Visitor action | Required consequence |
| --- | --- | --- |
| 1 | Pull back, or skip the motion | Understand bounded chemical-space scale, then arrive at the real measured collection. |
| 2 | Choose one of three training seeds/families | A real structure, its measured profile, family context, and associated recorded generation become the persistent context. |
| 3 | Choose one actual AI proposal | Record the selected candidate, show its verified relation to the seed and unknown experimental profile, and retain that candidate for the ending. |
| 4 | Commit fifty retrospective choices | Enter the separately labeled held-out cohort; show the prediction-only shortlist and fixed target region. |
| 5 | Reveal laboratory measurements | Preserve molecule identities; update measured results, target passes, and the exact equal-budget random reference. |
| 6 | Ask “What else matters?” | Reveal Caco-2 as a distinct second event for the same fifty, exposing omitted properties and missing evidence. |
| 7 | Inspect the example | Connect the selected result to its structure, prediction error, broader profile, training analog, and selection stability. |
| 8 | Return to my proposal | Restore the exact seed and candidate from actions 2–3, beside relevant measured examples. |
| 9 | Choose the next question to test | A real assay-choice control updates a short decision record for that candidate without inventing an assay outcome. |

Do not add mandatory navigation between these actions. Use staged disclosure or a compact guided notebook layout, with completed evidence available to revisit. The deeper analysis must remain part of a real notebook rather than a separate application.

## 7. Bring ChemLlama into the beginning and keep it personal

Currently the notebook first shows proposals at the end. Move the introduction before the retrospective experiment.

- Present the selected training seed beside genuine output structures linked by recorded `seed_id`.
- Preserve the actual relationship: “outputs from this seed prompt” is safe when that is what was recorded; “optimized analogs” or a requested similarity claim needs independent support.
- Show a few candidates initially with all valid candidates available through a compact table/grid.
- Display the run's sample accounting, including invalid output, with concise provenance. Do not show only successes without a denominator.
- Candidate selection must update a real downstream Python-derived evidence card. Keep the chosen ID in persistent marimo state, not just a checkbox in an unused table.
- Show computed descriptors as computed and exact experimental fields as unknown. Never fill them with a neighbor's data or saved predictions for a different compound.
- Label cached generation plainly. No fake streaming, artificial inference delay, or “Generate” button that pretends cached data were newly produced.

The visitor should think, “I have a concrete idea worth investigating.” Avoid claiming the generator has already solved ADMET.

Transition copy can be:

> Before we decide what to make, let's examine a collection where the experimental answers already exist.

Clearly identify the change to the retrospective cohort and its separate published ADMET predictor. The ending returns to the candidate; the intermediate measurements do not belong to it.

## 8. Stage two different discoveries from ADMET evidence

### First discovery: a useful model can still overpromise

Improve the existing reveal:

- Show numeric ticks, raw units or an explicitly explained transformation, a visible target region, and stable molecule IDs.
- Preserve all fifty points before/after; movement is between property predictions and measurements, not molecular geometry.
- Compute the active budget's exact reference. For fifty, the expected random target passes are approximately 20.95 versus 41 actual selected target passes. A historical fractional-budget plot is not a replacement.
- Actually draw any described bands. Label their meaning as random-shortlist variation, not assay uncertainty or calibrated model confidence.
- Hide downstream measured summaries, pressure curves, outcome-selected examples, and Caco-2 until their appropriate reveal states. Scrolling must not spoil the sequence.
- Produce a one-sentence interpretation from the actual active values. Let positive evidence remain positive.

### Second discovery: the answer can be right and the question incomplete

Caco-2 must have its own action/state. It should not appear automatically when the first measurements are revealed.

Use the same molecule as an anchor before and after showing additional endpoints. Verify these actual records:

| Molecule | LogD | KSOL, µM | Caco-2 Papp A>B, 10^-6 cm/s | Efflux ratio |
| --- | ---: | ---: | ---: | ---: |
| E-0023839 | 1.6 | 275 | 0.80 | 31.1 |
| E-0021738 | 2.2 | 288 | 26.72 | 0.92 |
| E-0024328 | 2.2 | 287 | 14.48 | 1.24 |

All three meet the initial chosen LogD/KSOL targets. Their broader profiles differ. These are retrospective illustrative contrasts, not proof of clinical success/failure and not evidence that optimizing solubility caused an efflux problem.

Keep the full fifty visible with correct coverage: 38 have paired numeric Caco-2 data, twelve lack paired numeric evidence; among 41 initial target passes, 33 have paired Caco-2 data. Missing/censored evidence stays visible. Do not choose arbitrary new thresholds to manufacture a dramatic funnel.

Suggested pivotal sentence:

> It met the two goals we gave it. Those were not all the questions we needed to ask.

Follow this immediately with inspectable values and chemistry, not a generalized anti-AI message.

## 9. Make inspection a coherent chemical view

One selected molecule must update together:

- Its 2D structure and identity.
- Predicted and measured LogD/solubility, once revealed.
- Its Caco-2 values/unknowns, once separately revealed.
- Its nearest **training** analog, its own measured values, and correctly defined similarity.
- Its benchmark family and family concentration in the shortlist.
- Its top-fifty inclusion frequency across the 25 saved fits, explicitly labeled selection stability.

A chart selection, table selection, and evidence card must agree on the same ID. Do not expose clickable rows without downstream behavior. Handle incomplete training analogs without hiding them or crashing. Use shared-substructure highlighting only if verified and chemically correct; do not invent mechanistic explanations.

Move dense tables and optional pressure/stability details into secondary inspection. Do not require twenty clicks to understand the seven scientific points.

## 10. End with earned hope and a functioning next decision

Return to the **same candidate and seed** selected early. Make this unmistakable through the same IDs, structures, and visual placement.

Show measured examples such as E-0021738 and E-0024328 as property-specific reasons for hope. Use a transparent selection rule and preserve the full shortlist context; do not quietly hand-pick favorable evidence. The previously concerning example should remain inspectable too.

For the proposal, provide a real control for the next experimental question, with a small set of relevant assays and a reasonable default. Selecting an assay updates a concise record such as:

```text
Candidate: [actual selected candidate ID]
Known: [computed descriptors and verified context]
Unknown: [candidate's exact experimental properties]
Next question: [chosen assay]
Why this could change the decision: [carefully scoped explanation]
```

Do not claim an assay was commissioned, a sample was synthesized, or the outcome is known. If an exact dataset rediscovery is present, label it separately and show only that exact compound's matching evidence.

Suggested closing thought:

> We cannot explore everything. We can make the next experiment count.

The hope comes from real useful enrichment, encouraging measured profiles, and a better-informed next question. It must remain visible even if a generated batch or an individual prediction disappoints.

## 11. Native marimo architecture and visual restraint

- Rework the existing notebook; preserve its auditable Python calculations. Do not implement the whole experience in a detached HTML/JavaScript slideshow.
- Native controls own the seed, candidate, budget, assay choice, and committed reveal states. Custom widgets return selected IDs to Python. Python-derived views must visibly react.
- Use explicit state such as selected seed ID, selected candidate ID, active shortlist, first-reveal state, Caco-2-reveal state, inspected molecule ID, and next-assay choice. Implement it with the installed marimo API and a dependency flow that avoids cycles.
- Maintain candidate state when visiting the separate retrospective cohort. Define resets deliberately: changing a seed clears an incompatible candidate; changing a retrospective budget clears relevant measured/inspection state without losing the chosen generation context.
- Do not import inference dependencies, submit jobs, or load weights from ordinary notebook viewing cells.
- Keep rapid animation state frontend-local and synchronize only committed interactions. Clean up every listener/observer and animation frame.
- Use one consistent visual language for evidence states and one main focal area per scene. Large numbers should establish scale or a meaningful comparison, not decorate a dashboard.
- Reuse native chemistry grids/tooltips, Altair/marimo charts, and verified RDKit depictions. Use custom animation where it explains scale, identity, or an evidence transition.
- Prefer readable structures and axes over motion, 3D ornaments, particle effects, or repeated full-width data tables. No stock hero illustration is needed.
- Provide keyboard/table alternatives, readable narrow layouts, reduced motion, and explicit unknowns. Never hide essential information behind hover.

## 12. Specific changes that must be verified

1. Replace the current scoring-first opening with the sourced scale sequence and measured-evidence collection.
2. Add a real training-seed selector and an early proposal gallery linked to it.
3. Retain an actual candidate selection across the measured investigation and restore it at the end.
4. Give Caco-2 a distinct reveal state/action; keep premature outcomes hidden everywhere, including the pressure table.
5. Add numeric tick labels and target regions to the main reveal; compute and render the active count's random comparator.
6. Integrate Caco-2 and stability into the selected molecule's evidence view.
7. Add the measured success examples and functioning final assay-choice control.
8. Load the explicitly approved generation run, not the newest directory by modification time.
9. Replace the existing walkthrough with steps that the actual implementation can perform. Do not mark target behavior as implemented without testing it.

## 13. Validation: prove both science and experience

Run `pytest`, marimo checks, and static execution/export as required by the main brief. Retain all scientific regression checks. Add focused coverage for candidate persistence, separate reveal states, active-budget comparators, and pinned-generation loading where appropriate.

Browser testing is required for the interactive acceptance claim. Use the live marimo server with its Python kernel. Install an isolated browser automation runtime if needed and authorized by the main brief. A static export cannot establish this gate. If an external restriction prevents browser verification, report the exact restriction and keep the gate explicitly incomplete.

Capture the following evidence:

- Scale landmarks have correct labels/mark meanings and match the computed arithmetic. Skip and reduced motion preserve the information.
- Dataset accounting derives from the nine explicit endpoint columns; missing/censored interpretation is accurate.
- Selecting each seed changes the early candidate view correctly. Selecting a candidate updates Python-derived evidence.
- After both retrospective reveals and molecule inspection, returning restores the same chosen seed/candidate.
- Before the first reveal, no held-out measured values/summary are shown; between reveals, Caco-2 outcomes remain hidden.
- The first reveal preserves IDs and shows correct top-fifty counts plus the equal-budget random comparison.
- The second reveal retains the same fifty and correct Caco-2 coverage; the example's structure and values remain connected.
- Point and table selection update the same evidence card; invalid/empty selections and missing analog assays are handled.
- Choosing the next assay changes the actual final decision record without generating fictional outcomes.
- The default path requires at most ten actions, including navigation, and does not require browsing dozens of molecules.
- Replay, budget/seed changes, fresh-kernel restart, reduced motion, keyboard access, and narrow layouts work.

Save a compact interaction log and screenshots at the scale, early proposal, both reveals, inspection, and final-return states. Screenshots alone do not prove Python reactivity; verify actual IDs/state as well. Record measured startup/interaction times and avoid unsupported performance claims.

Perform an editorial pass in addition to automated checks. Use these questions as review prompts, not as claims of a completed human usability study:

- Can a newcomer explain the scale comparison without repeating an unexplained exponent?
- Can they distinguish a structure, a computed descriptor, a prediction, and an experimental result?
- Is the experimental effort visible before the AI appears?
- Does the AI proposal create a concrete question the later evidence helps them reconsider?
- Are the two ADMET discoveries distinguishable and anchored to actual molecules?
- Does the ending offer measured reasons for hope and restore the visitor's original choice?
- Do the controls visibly connect views, demonstrating why this belongs in marimo?

If any answer is no, revise the experience. Do not claim the intended emotional response has been demonstrated merely because the code executes.

## 14. Execution order and handoff

1. Back up the current notebook and record the approved generation run/artifact identity.
2. Define the nine-action path and state transitions in a short working note, then implement them; do not stop at the note.
3. Build the real seed → proposal → retained candidate → return/assay state flow first.
4. Implement the sourced scale/human-evidence opening in the notebook.
5. Stage and link the two ADMET reveals, inspection, active-budget comparator, and measured hope examples.
6. Integrate/polish layout, labels, motion alternatives, and the final decision record.
7. Run scientific and live-browser validation, count actual guided actions, and fix failures.
8. Update `IMPLEMENTATION_STATUS.md`, `README.md`, and `docs/submission_walkthrough.md` to match reality. Preserve the inference reports and historical results.

Final handoff: notebook and launch link, a concise description of what changed, screenshots or a local walkthrough recording, actual main-path action count, scientific/browser checks passed, and exact unresolved limitations. No publishing or competition submission without the user's later instruction.

The task is complete only when the **working notebook** delivers the scale → effort → AI possibility → experimental investigation → informed hope sequence, with the required scientific and interaction evidence. Another list of implemented charts is not sufficient.
