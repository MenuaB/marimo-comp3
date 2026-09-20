# Implementation status

Current as of 20 September 2026.

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
- Preserved ChemLlama run `chemllama-271948`, its 96 raw records, 27 valid
  candidates, 69 invalid records, zero duplicates, seed links, and prompting
  limitation. No inference was rerun.

## Validation evidence

- `pytest`: 17 scientific, generation, schema, tamper, and portable-parity tests
  pass.
- `marimo check`: both notebooks pass after formatting.
- Native and portable HTML exports execute successfully.
- Live Chromium paths pass for both native and local portable notebooks. Each
  run verifies all nine required actions, rapid fit scrubbing, exact ensemble
  commitment, withheld outcomes before reveal, same-ID measurement state,
  41/50 enrichment, 38/50 and 33/41 Caco-2 coverage, retained candidate
  identity, Python assay decision, replay, explicit restart, a 390-pixel layout
  with zero widget overflow, reduced motion, and a fresh session.
- State-aware screenshots and logs are under
  `outputs/notebook_validation/custom-visual-story-{native,portable}/`.

The final measured startup/interaction timings are recorded in each
`interaction_log.json`; they are environment observations, not performance
claims.

## Publication status

The visual-v3 notebook and bundle are published on `main`. The portable entry
point uses the checked-in bundle when present and an immutable, SHA-256-verified
GitHub bundle fallback when the host loads only the notebook file. Local native
and portable browser paths have passed the complete nine-action checklist.
