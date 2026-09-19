# ChemLlama generation handoff

This supersedes the historical Chemlactica handoff. Offline generation uses
`yerevann/ChemLlama-1B@f3f7fc0aa3ad48799d4cc89e3ed822c1d016614e` on allocated
H100 hardware only. The runner rejects A6000 and every other non-H100 device
before any checkpoint loading.

The notebook remains inference-free and consumes only audited cached outputs.
It never applies released-test ADMET predictions to a new generated structure.

## Completed run evidence

The successful smoke run is Slurm job `271947`; the successful main pilot is
job `271948`. Both ran on `gpu03`, which recorded `NVIDIA H100 80GB HBM3`,
CUDA 12.6, PyTorch `2.7.1+cu126`, bfloat16, and one visible allocated device.
The main pilot used 3 training seeds × 32 raw samples and produced 96 raw
records: 27 unique valid candidates, 69 invalid records, and 0 duplicates.
Its immutable manifest, raw JSONL, and candidate table are under
`outputs/chemllama/chemllama-271948/`.

The initial H100 attempts `271942` and `271943` are preserved in Slurm logs:
the first exposed an unavailable `srun` executable on the compute node and the
second exposed the Transformers 5 `generator=` API removal. `271945` is also
preserved as a parser-defect run; it must not be used for presentation. The
runner was repaired, then `271947` confirmed the conservative explicit-SMILES
parser before the main run. The model emitted `SIMILAR` markers in raw output;
those are recorded as observed delimiters only, not a claim about undocumented
conditioning semantics.

## Deterministic seeds

`outputs/chemllama_preparation/seed_manifest.json` contains three real,
complete-case official-training seeds. They are selected by highest measured
training desirability, then molecule ID, taking at most one seed per benchmark
cluster. They are future proposal seeds, not held-out evaluation winners.

## Input and output contract

Tokenizer/config preflight is in
`outputs/chemllama_preparation/tokenizer_preflight.json`. The pinned revision
has no model card, so no unsupported tag or similarity-condition semantics are
introduced. Computed RDKit cLogP is not experimental LogD.

For each future sample, retain this record contract:

```text
candidate_id, seed_id, smiles, canonical_isomeric_smiles
checkpoint_id, checkpoint_revision, prompt, random_seed, decoding_settings
generation_run_id, raw_sample_index, validation_status, rejection_reason
similarity_to_seed, nearest_training_id, nearest_training_similarity
computed_descriptors_with_names_units_and_tool_versions
measured_LogD = null, measured_KSOL_uM = null
evidence_status = "proposal_unmeasured"
```

Retain invalid and duplicate raw samples in a separate immutable run log. A
deduplicated valid set does not establish chemical novelty, and an analog’s
measurement cannot be transferred to a proposal.

## Feasibility plan

Use a modest proposed budget of **3 seeds × 32 raw samples**, with documented
random seeds and decoding settings. Validate SMILES, canonicalize, deduplicate,
compute clearly named descriptors with tool versions, and find nearest training
context using the existing Morgan radius-2 / 2,048-bit fingerprint definition.
Cache the verified candidate table and raw run log before presenting any
proposal. The existing saved benchmark predictions apply only to released test
molecules and must not be used to score newly generated structures.

## Outstanding decisions

1. Exact checkpoint identifier and immutable revision.
2. Supported prompt/template and any similarity conditioning semantics.
3. Hardware, runtime, license, and checkpoint-download provenance.
4. Acceptance/rejection criteria and descriptor set before inspecting outputs.
5. A cache/loading path suitable for a clean notebook runtime.
