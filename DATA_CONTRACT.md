# Data contract

## Pinned source identity

| Input | Revision | SHA-256 |
| --- | --- | --- |
| OpenADMET `expansion_data_{train,test,raw}.csv` | `6b898ccc43d10d25b230fb09e22a6e30c30022b5` | Recorded per file in `outputs/audit.json` |
| Pat Walters `expansion_log_scaled.csv`, `predictions_all.parquet` | `06582771d48af8096f6b05a5a247b177189a8fa4` | Recorded per file in `outputs/audit.json` |

`scripts/notebook_data.py` verifies those exact SHA-256 values before using an
input. Missing files are fetched atomically from the recorded URLs; a mismatch
is an error, never an overwrite. Cache identity includes these hashes, analysis
settings, RDKit version, and schema version.

## Records and evidence

The fixed primary cohort is the 2,160 official test records with numeric LogD
and KSOL. IDs are `molecule_id` (official `Molecule Name`); `SMILES` is the
original source string and `canonical_isomeric_smiles` is RDKit canonical,
isomeric SMILES. `split` is always `test` in the joined cohort and `cluster`
is the benchmark cluster label.

| Field | Meaning / unit / evidence |
| --- | --- |
| `obs_LogD` | Released experimental LogD; measurement |
| `obs_KSOL_uM` | Released kinetic solubility, µM; measurement |
| `obs_LogS` | `log10(obs_KSOL_uM + 1) - 6`; stored derived transform, not unmodified thermodynamic log molar solubility |
| `pred_LogD`, `pred_LogS` | Mean of 25 saved Morgan + LightGBM predictions per endpoint; prediction |
| `pred_KSOL_uM` | Inverse transform of mean `pred_LogS`: `max(10 ** (LogS + 6) - 1, 0)`; derived prediction |
| `prediction_count_per_endpoint` | 25 after repeat/fold completeness validation |
| `pred_score`, `obs_score` | Illustrative training-derived desirability; derived, not a clinical probability |
| `nearest_training_id`, `nearest_training_similarity` | Nearest valid official-training molecule, Morgan radius-2 / 2,048-bit Tanimoto; context |

The official test split has 2,282 rows: 2,270 numeric LogD, 2,170 numeric
KSOL, and 2,160 paired rows. The remaining 122 are exclusion/missingness
accounting, not imputed zeros or failures. The ten raw-only records are never
added to a released split.

## Score and selection

Training complete cases (n=4,934) give `LogD` lower/upper quartiles 1.4/2.9
and KSOL median 125.5 µM. For LogD `d` and stored LogS `s`:

```text
distance = max(1.4 - d, d - 2.9, 0)
logd_component = exp(-distance / 0.75)
ksol = max(10 ** (clip(s + 6, -6, 8)) - 1, 0)
score = sqrt(logd_component * ksol / (ksol + 125.5))
```

The fixed cohort is ranked by `pred_score` descending then `molecule_id`
ascending, preserving deterministic tie behavior. Fractions 50/25/10/5/2%
use `max(1, round(n * fraction))`: 1,080/540/216/108/43. Measured threshold
passes are a secondary diagnostic only: `1.4 <= obs_LogD <= 2.9` and
`obs_KSOL_uM >= 125.5`.

Random-shortlist intervals use 2,000 equal-size draws without replacement,
with seed `20260918`. They describe variation across random shortlists, not
assay uncertainty or a confidence interval around model performance.

## ChemLlama proposal contract

The viewing notebook reads cached candidate artifacts only; it never imports an
inference stack, downloads weights, or requires a GPU. Offline runs retain a
raw append-only JSONL record, manifest, rejection/duplicate summary, and this
small presentation table. The pinned checkpoint has no model card, so raw
SMILES-continuation prompts make no undocumented conditioning claim.

Every candidate row must contain:

```text
candidate_id, seed_id, smiles, canonical_isomeric_smiles,
checkpoint_id, checkpoint_revision, prompt, random_seed, decoding_settings,
generation_run_id, raw_sample_index, validation_status, rejection_reason,
similarity_to_seed, nearest_training_id, nearest_training_similarity,
computed_descriptors_with_names_units_and_tool_versions,
measured_LogD=null, measured_KSOL_uM=null,
evidence_status="proposal_unmeasured"
```

Missing values serialize as JSON `null`, never zero or `NaN`. A separate raw
generation log retains invalid and duplicate samples. Exact canonical-isomeric
matches to a released split are labeled rediscoveries, not validation. Similarity
offers context only; a saved test-prediction table cannot score new molecules.
