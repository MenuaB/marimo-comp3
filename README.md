# Before You Make It

Native [marimo](https://marimo.io/) notebook for a measured-data investigation
of OpenADMET ExpansionRx: select held-out molecules from saved Morgan +
LightGBM predictions, reveal their published measurements, inspect Caco-2
evidence and training context, then return to cached ChemLlama proposals.

## What it does

`before_you_make_it.py` is a nine-action guided experience: bounded chemical
space; real measured evidence; a seed-linked cached ChemLlama proposal; a
committed prediction-only top fifty; separate released LogD/KSOL and Caco-2
discoveries; coherent inspection; and a return to the same proposal with a
next-assay choice. The viewer never loads a checkpoint or performs inference:
published saved predictions apply only to released test molecules; generated
proposals retain unknown experimental fields.

## Install and launch

Tested with **Python 3.13.12**. The project-local `.venv` is intentional.

```sh
cd /mnt/weka/mbedrosian/code/marimo
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-notebook.in
.venv/bin/python -m pip check
.venv/bin/python -m pip freeze > requirements-notebook.lock.txt
.venv/bin/marimo edit before_you_make_it.py --no-sandbox --watch --headless --host 127.0.0.1 --port 2718
```

The CLI prints a localhost URL with its session token. Keep that token private;
it is neither committed nor disabled. If 2718 is occupied, choose a free local
port rather than stopping another process.

## Run in molab

[Open the live notebook in molab](https://molab.marimo.io/github/MenuaB/marimo-comp3/blob/main/before_you_make_it.py).

molab previews one GitHub notebook file, whereas this project keeps its audited
helpers and data contract in sibling files. On a GitHub/molab run, the notebook
therefore retrieves those small pinned helpers and the approved generation
artifact into a temporary workspace, then obtains the larger source data through
the existing SHA-256-checked bootstrap. The first run can take longer while
those verified inputs download; later cell interactions remain reactive.

## Data bootstrap and cache

The notebook calls `scripts/notebook_data.py:prepare()` on startup. It checks
local SHA-256 values against `outputs/audit.json`; if a pinned input is absent,
it downloads precisely the audited revision atomically and then verifies the
digest. Derived tables live in `data/notebook_cache/`, whose manifest includes
source hashes, score settings, RDKit version, and cache schema. Deleting only
that cache regenerates it; do not replace or delete the historical `outputs/`
audit/pilot files.

The notebook and helper must travel together in a portable bundle. The helper
is intentionally local because tests and notebook share one verified data path.

## Verify

```sh
.venv/bin/marimo check before_you_make_it.py
.venv/bin/python -m pytest
mkdir -p outputs/notebook_validation
.venv/bin/marimo export html before_you_make_it.py --no-sandbox -o outputs/notebook_validation/notebook_snapshot.html --force
```

For interaction verification, use a fresh browser session and follow the nine
actions in [the state-machine note](docs/story_state_machine.md). Confirm that
changing seed changes the compatible cached gallery, then retain the chosen
candidate through the separate retrospective reveals and assay-choice record.
The export is an execution snapshot, not a substitute for a live walkthrough.

## Offline ChemLlama generation

The isolated `.venv-inference` is for offline inference only. It uses Python
3.12, `transformers==5.7.0`, and the pinned
`yerevann/ChemLlama-1B@f3f7fc0aa3ad48799d4cc89e3ed822c1d016614e` checkpoint.
Run it only through `scripts/run_chemllama_h100.sbatch`, which rejects every
non-H100 CUDA device before model loading. Each run writes append-only raw
records, a manifest, and a lightweight candidate table under
`outputs/chemllama/<run-id>/`; the notebook loads only that cached table.
See `CHEMLACTICA_HANDOFF.md` and `DATA_CONTRACT.md` for evidence boundaries.

The integrated run is `chemllama-271948`: 96 raw samples on an NVIDIA H100
80GB HBM3, 27 unique valid candidates, 69 invalid samples, and no duplicates.
Those candidates are unmeasured proposals, not experimental ChemLlama results.

## Attribution and limits

The official ExpansionRx data and its source license, plus the pinned Pat
Walters benchmark prediction revision, are recorded in `outputs/audit.json`.
The notebook uses `marimo-chem-utils` for molecular navigation and grids.
AI assistance was used to implement the notebook; all reported score outputs
are recomputed from the pinned released inputs. The illustrative score,
similarity, and any structure-review cue are not evidence of efficacy, safety,
synthesizability, or clinical success.
