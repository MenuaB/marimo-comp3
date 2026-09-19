# Implementation status

This file records the current implementation state as of 18 September 2026.

## Completed stages

1. Created a project-local Python 3.13 virtual environment and resolved direct
   notebook dependencies in `requirements-notebook.lock.txt`.
2. Verified pinned input digests, built the typed fixed 2,160-row joined cohort,
   and wrote regenerable cache artifacts under `data/notebook_cache/`.
3. Reproduced the saved Morgan + LightGBM pilot exactly: top 10% is predicted
   0.7942619913570331 / measured 0.7461249726859417; top 2% is
   0.8248401217273029 / 0.7538348622359935.
4. Reworked the notebook into a nine-action experience: sourced bounded-scale
   opening, real nine-endpoint evidence accumulation, seed-linked cached
   proposals, fixed-fifty commitment, separate evidence reveals, coherent
   inspection, and a restored-proposal assay decision.
5. Added explicit pinned-generation loading and hash/provenance validation in
   `scripts/experience_data.py`; the notebook no longer chooses candidates by
   newest file modification time.
6. Created an isolated Python 3.12 inference environment; tokenizer/config
   preflight and H100-only device guard are recorded under
   `outputs/chemllama_preparation/`.
7. Completed ChemLlama H100 smoke job `271947` and main pilot job `271948` on
   `gpu03` (NVIDIA H100 80GB HBM3). The main pilot has 96 raw samples, 27
   unique valid candidates, 69 invalid samples, and no duplicates. Raw output,
   candidates, and manifest are in `outputs/chemllama/chemllama-271948/`.

## Validation completed

- `marimo check before_you_make_it.py` completed successfully.
- `.venv/bin/python -m pytest` passed 12 scientific, generation, and
  experience-contract tests.
- `marimo export html ...` executed the reworked notebook and produced
  `outputs/notebook_validation/story-rework-final.html`.
- An isolated fresh-cache smoke test regenerated a separate
  `outputs/notebook_validation/clean_cache_smoke/` cache and returned the
  expected 4,934 training complete cases and 2,160 paired test records.
- The local authenticated server was restarted successfully and is running in
  terminal session `89482` at
  `http://127.0.0.1:2718` (its one-time access-token URL is intentionally not
  persisted in this file).

## Performance observations

Warm cached preparation is fast; initial native chemistry tooltip creation for
the deterministic 800-molecule navigation sample took roughly 2–3 seconds in
the export. Nearest-training fingerprints are cached in the joined cohort.
Molecular grids cap rendering at 12 records per view.

## Remaining verification limitation

The static export and executable notebook checks passed. Live authenticated
browser interaction (including widget point-to-card propagation, reduced-motion,
narrow-layout, and fresh-kernel restart) still needs a browser automation route;
it is not claimed complete. Molab execution is also unverified because no
authorized private molab route was available in this workspace.

The installed `marimo-chem-utils` version lacks a package REOS interface and a
validated per-pair MCS depiction API; the notebook documents this instead of
claiming alert or shared-substructure causes.
