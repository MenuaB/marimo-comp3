# Before You Make It

**Fifty experiments. Twenty-five maps. One next decision.**

A nine-action marimo story about choosing a small retrospective molecular
shortlist when saved model fits disagree, seeing what measurement changes, and
returning to one unmeasured cached ChemLlama proposal with a better next
question.

## Entry points

- `before_you_make_it.py` — native local notebook. It loads the verified,
  precomputed visual payload and the same custom renderer used by the portable
  path.
- `before_you_make_it_wasm.py` — intended competition/molab entry point. It is
  browser-safe: no RDKit, DuckDB, weights, GPU, or inference is needed while
  viewing.
- `data/molab_bundle.json` — schema
  `before-you-make-it-visual-v3`, containing fit nominations, evidence records,
  compressed RDKit SVG depictions, provenance, and the exact JS/CSS widget
  assets for portable parity.

The public molab URL will be:
[open the portable notebook](https://molab.marimo.io/github/MenuaB/marimo-comp3/blob/main/before_you_make_it_wasm.py).
This workspace is not authorized to push. The revised notebook and v3 bundle
therefore require an explicit publication commit before that public URL can be
claimed as tested. Local portable execution is tested end to end; no private
authenticated molab route was available.

## Install and run

Tested with Python 3.13.12 and the pinned environment in
`requirements-notebook.lock.txt`.

```sh
cd /home/mbedrosian/code/marimo
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-notebook.in
.venv/bin/python scripts/build_molab_bundle.py

# Native
.venv/bin/marimo run before_you_make_it.py --no-sandbox --headless --port 2720

# Portable/WASM companion, validated locally against the same bundle
.venv/bin/marimo run before_you_make_it_wasm.py --no-sandbox --headless --port 2721
```

The portable notebook intentionally refuses to fetch an unpublished payload
from mutable `main`. Keep `before_you_make_it_wasm.py` and
`data/molab_bundle.json` together. After publication, test the actual molab URL
before submission.

## What is custom

`widgets/molecule_evidence.py`, `molecule_evidence.js`, and
`molecule_evidence.css` implement `MoleculeEvidenceLens`, which keeps molecular
identity coherent across:

- the fixed-order 256-molecule nomination union while one fit's fifty changes;
- an explicit ensemble-fifty commitment;
- same-ID predicted-to-measured motion in LogD/KSOL space;
- a separate Caco-2 view for that unchanged fifty;
- the retained generated candidate and candidate-specific next-assay record.

`ScaleJourney` uses counted level-of-detail groups, a skippable/reduced-motion
route, a real training molecule's nine-slot evidence strip, and collection-wide
endpoint coverage. Both components synchronize discrete state to Python via
`mo.ui.anywidget`; animation progress stays browser-local.

## Scientific facts exposed

- 7,608 released train + test records; nine endpoint columns; 36,003 populated
  numeric cells of 68,472 possible in the ML-ready tables.
- 2,160 held-out records with paired LogD/KSOL and 25 saved LGBM repeat/fold
  fits per endpoint.
- Fit-specific top-fifty lists nominate 256 distinct molecules; only
  `E-0024329` appears in all 25.
- The ensemble fifty yields 41 measured target passes. Exact random expectation:
  `50 × 905 / 2,160 = 20.949074…`.
- `E-0024329` has ensemble-predicted LogD 1.999 and KSOL 317.812 µM, versus
  measured LogD 0.70 and KSOL 269.0 µM. Unanimous nomination is not guaranteed
  measured success, while the complete selection remains usefully enriched.
- The same fifty contain 38 paired numeric Caco-2 records; 33 belong to the 41
  initial target passes. Missing evidence is not failure or zero.

The fits share a method and overlapping training data. They are selection
sensitivity views, not independent experts or calibrated uncertainty. The
score and thresholds are illustrative, not efficacy or clinical claims.

## Verify

```sh
.venv/bin/marimo check before_you_make_it.py before_you_make_it_wasm.py
.venv/bin/python -m pytest
.venv/bin/python scripts/build_molab_bundle.py --force

.venv/bin/marimo export html before_you_make_it.py --no-sandbox \
  -o outputs/notebook_validation/before-you-make-it-native.html --force
.venv/bin/marimo export html before_you_make_it_wasm.py --no-sandbox \
  -o outputs/notebook_validation/before-you-make-it-portable.html --force
```

The live browser harness is `scripts/validate_story_browser.py`. It records
state-aware screenshots and interaction logs under `outputs/notebook_validation/`.
See `docs/submission_walkthrough.md` and `docs/story_state_machine.md`.

## Generation, licensing, and AI assistance

Viewing never runs generation. The preserved integrated run is
`chemllama-271948`: 96 raw samples on an NVIDIA H100 80GB HBM3, 27 unique valid
candidates, 69 invalid samples, and zero duplicates. The raw-SMILES continuation
probe does not establish documented conditional analog optimization; candidate
experiments remain unknown.

OpenADMET/ExpansionRx is CC BY 4.0. Exact source revisions and hashes are in
`outputs/audit.json`; the Pat Walters benchmark revision is pinned there too.
RDKit generates original structure depictions. AI assistance was used to
implement and test the custom notebook and widget code; all scientific values
are recomputed from pinned released inputs.
