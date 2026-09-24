# Before You Make It — state and disclosure contract

The default path has nine required actions. Optional point inspection, replay,
additional proposal cards, methods, and restart do not add required navigation.

| Action | Visitor event | Canonical state change | Observable consequence |
| ---: | --- | --- | --- |
| 1 | Show the scale or its immediate summary | `scale.complete = true` | Both routes retain the five scale landmarks, bounded GDB-17 scope, hypothetical inspection-time comparison, one-molecule evidence explanation, and collection coverage. |
| 2 | Choose a measured reference | `seed_id`; incompatible `candidate_id` and `next_assay` clear | The measured example changes and filters which cached generated proposals are offered. It does not change the retrospective shortlist. |
| 3 | Retain an unmeasured proposal | `candidate_id`; `next_assay` clears | The exact cached candidate enters the persistent tray with experimental slots unknown. Copy explicitly transitions to a separate retrospective analysis. |
| 4 | Compare saved model fits | `active_fit_index`, `active_fit_key`, `fit_explored`; initially highlights `E-0024329` | The fixed 256-position nomination layout, fifty-slot tray, fit predictions, and Python overlap update together. A visitor-selected molecule remains selected. |
| 5 | Choose this model's or the averaged-model fifty | `selection_kind = active_fit` with `committed_fit_key`, or `ensemble`; exact canonical `committed_ids` (50); `evidence_stage = prediction` | The chosen fifty enter the prediction-only property plane and remain fixed. |
| 6 | Compare with measurements | `measurements_revealed = true`; `evidence_stage = measured` | The same IDs move to measurements. The panel derives the shortlist's pass count, ensemble comparator, related-fit range, and random expectation. |
| 7 | Ask about permeability and efflux | `caco_revealed = true`; `evidence_stage = caco` | The unchanged fifty enter an explicitly explained Caco-2 Papp/efflux plane; paired, missing, and bounded evidence remain distinct. |
| 8 | Apply the lesson to the proposal | `returned_to_proposal = true`; inspected ID becomes the retained candidate | The exact candidate returns with unknown assays beside clearly separate measured examples. |
| 9 | Choose the next unanswered question | `next_assay` | Python receives a candidate-specific assay question; no assay is commissioned and no result is invented. |

Generation context (`seed_id`, `candidate_id`) is separate from retrospective
state (`active_fit_key`, `inspected_molecule_id`). Commitment owns
`selection_kind`, `committed_fit_key`, and the exact ordered fifty IDs.
Disclosure owns the two booleans. The ending owns
`returned_to_proposal` and `next_assay`.

Changing the seed clears an incompatible proposal and old assay choice but does
not rewrite retrospective evidence. Changing proposal identity never transfers
the previous proposal's data. A visitor can commit the active fit or explicitly
use the ensemble; fit scrubbing cannot replace a committed list.
The first reveal cannot expose Caco-2; the second cannot occur first. “Restart
retrospective” explicitly clears commitment/disclosure while preserving the
retained proposal. Every event ID and fit key is drawn from the versioned
payload.
