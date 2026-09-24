# Implementation status

Current as of 24 September 2026.

## Complete locally

- Recomputed the 25 repeat/fold nomination sets by pairing LogD/LogS on actual
  `(molecule_id, repeat, fold)` keys. The cached result has 256 union IDs, one
  intersection ID (`E-0024329`), fit/ensemble overlap 21–36 (median 29), and
  exact prediction records for all 256 × 25 display pairs.
- Corrected `random_expected_passes` to the analytic
  `50 × 905 / 2,160 = 20.949074…`; retained the seeded simulation mean as the
  separately named `random_simulation_mean_passes`.
- Built versioned evidence records with measured, predicted, computed, missing,
  and bounded states; all inspectable union molecules, required training
  neighbors, three seeds, and all 27 approved generated candidates have keyed
  compressed RDKit SVG depictions.
- Implemented `MoleculeEvidenceLens` and `ScaleJourney` as original anywidgets.
  The main widget synchronizes seed/candidate, active fit, inspected ID,
  ensemble commitment, disclosure stage, return state, and assay decision to
  Python. Animation progress remains frontend-local.
- Replaced both notebook paths with the same visual schema and renderer. The
  portable bundle is 3.07 MiB and includes its exact JS/CSS assets, scientific
  payload, depictions, source hashes, and derived-artifact hashes.
- Preserved ChemLlama run `chemllama-271948`, its 96 raw records, 27
  RDKit-parseable candidates, 69 invalid records, zero duplicates, seed links,
  and prompting limitation. A deterministic chemistry audit identifies 23
  sanitized single-component featured candidates and four unresolved
  multi-component samples. `C-0033` remains in the audit with raw `.Cl` but is
  not displayed as a proposal. No inference was rerun.
- Replaced ensemble-only commitment with active-fit or ensemble commitment.
  `selection_kind`, `committed_fit_key`, and 50 ordered `committed_ids` flow
  through Python-derived measurement and Caco-2 summaries.
- Rebuilt the introduction around the concrete premise “Imagine you can test
  only fifty molecules.” It now explains experimental evidence and the 25
  model fits before presenting controls. The animated, summary, and
  reduced-motion scale routes all retain the five landmarks, bounded GDB-17
  scope, hypothetical one-per-second comparison, and the transition from one
  measured molecule to collection-wide coverage.
- Replaced visitor-facing component/procedure language with question-led scene
  transitions. Seed selection is explicitly described as filtering cached
  proposal examples; proposal identity is explicitly separated from the
  retrospective shortlist. LogD, kinetic solubility, Papp, and efflux receive
  plain-language introductions before their abbreviated views.

## Validation evidence

- `pytest`: 22 scientific, generation, schema, chemistry-audit, commitment,
  portable-analysis, and narrative-asset tests pass. They cover the 23 featured
  candidates, all 25 saved fits, ensemble parity, and the newcomer-first copy
  embedded in the portable bundle.
- `marimo check`: both notebooks pass after formatting.
- Native and portable HTML exports execute successfully.
- Native and portable HTML exports complete. The portable live server starts
  and serves successfully.
- The browser harness now captures the full introductory page and exercises
  the complete animated scale, immediate summary, reduced motion, active-fit
  and ensemble routes, their different summaries, and committed-ID Caco-2
  continuity. Its current run remains blocked before browser launch because
  this host lacks Chromium shared libraries beginning with `libnspr4.so`; no
  new screenshots are claimed from this host.
- State-aware screenshots and logs are under
  `outputs/notebook_validation/custom-visual-story-{native,portable}/`.

The final measured startup/interaction timings are recorded in each
`interaction_log.json`; they are environment observations, not performance
claims.

## Newcomer reading assessment

The revised default copy answers four questions before or beside the relevant
action: the problem is allocating an illustrative fifty experimental slots;
experiments add behavioral evidence that structures and predictions cannot;
each choice states what it changes and what it does not change; and each result
ends with the question that motivates the next scene. This is an editorial
assessment of the implemented copy, not a substitute for observing a new
reader. A short external newcomer walkthrough remains desirable before final
submission.

## Publication status

The checked-in visual-v3 notebook and bundle contain the phase 1–3 changes.
The portable entry point verifies the local artifact and its immutable,
SHA-256-verified GitHub fallback at commit `9990392`.
