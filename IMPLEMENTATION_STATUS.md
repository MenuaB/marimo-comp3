# Implementation status

Current as of 23 September 2026.

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

## Validation evidence

- `pytest`: scientific, generation, schema, chemistry-audit, commitment, and
  portable-analysis tests cover the 23 featured candidates, all 25 saved fits,
  and ensemble parity.
- `marimo check`: both notebooks pass after formatting.
- Native and portable HTML exports execute successfully.
- The browser harness now exercises an active-fit commitment and a separate
  ensemble commitment, their different summaries, and committed-ID Caco-2
  continuity. Re-run it in an environment with Playwright Chromium shared
  libraries available; this environment lacks `libnspr4.so`.
- State-aware screenshots and logs are under
  `outputs/notebook_validation/custom-visual-story-{native,portable}/`.

The final measured startup/interaction timings are recorded in each
`interaction_log.json`; they are environment observations, not performance
claims.

## Publication status

The checked-in visual-v3 notebook and bundle contain the phase 1–3 changes.
The portable entry point verifies the local artifact and its immutable,
SHA-256-verified GitHub fallback at commit `9990392`.
