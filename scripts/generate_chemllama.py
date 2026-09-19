"""Run and audit a ChemLlama-1B SMILES-continuation experiment on an H100.

The script is deliberately independent of the notebook environment.  It never
loads weights until ``h100_device_record`` has rejected non-H100 hardware.
Raw records are append-only JSONL; candidate rows retain their raw provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger, rdBase
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdFingerprintGenerator

ROOT = Path(__file__).resolve().parents[1]
SMILES_TOKEN = re.compile(r"[^\s,;|]+")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def h100_device_record(torch) -> dict:
    """Require a visible H100 before any model construction or weight access."""
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("ChemLlama inference requires an allocated CUDA H100")
    devices = []
    for index in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(index)
        if "a6000" in name.lower() or "h100" not in name.lower():
            raise RuntimeError(f"Refusing non-H100 CUDA device {index}: {name}")
        props = torch.cuda.get_device_properties(index)
        devices.append({"index": index, "name": name, "uuid": str(getattr(props, "uuid", "unavailable"))})
    return {
        "visible_device_count": len(devices), "devices": devices,
        "cuda_version": torch.version.cuda, "torch_version": torch.__version__,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }


def canonical(smiles: str) -> str | None:
    molecule = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(molecule, isomericSmiles=True) if molecule is not None else None


def extract_smiles(continuation: str, seed_smiles: str) -> tuple[str | None, str | None]:
    """Extract an explicit generated structure, never a seed plus metadata tag."""
    text = continuation.strip()
    if text.startswith(seed_smiles):
        text = text[len(seed_smiles):].strip()
    # The smoke probe empirically emits repeated ``SIMILAR`` markers followed
    # by SMILES. This is an observed output delimiter only, not evidence for an
    # undocumented conditioning interpretation.
    tagged = re.findall(r"(?:SIMILAR){1,2}([A-Za-z0-9@+\-\[\]\(\)=#$\\/%.]+)", text)
    for candidate in tagged:
        value = canonical(candidate)
        if value and value != canonical(seed_smiles):
            return candidate, "observed_similar_marker"
    for token in SMILES_TOKEN.findall(text):
        candidate = token.strip("`'\".()[]{}")
        if candidate.upper().startswith(("SMILES", "FORMULA", "WEIGHT", "TPSA", "CLOGP", "QED", "SAS", "SIMILAR")):
            continue
        value = canonical(candidate)
        if value and value != canonical(seed_smiles):
            return candidate, None
    return None, "no_parseable_new_smiles"


def training_context() -> tuple[pd.DataFrame, dict[str, str], object, list]:
    train = pd.read_csv(ROOT / "data" / "expansion_data_train.csv").rename(columns={"Molecule Name": "molecule_id"})
    test = pd.read_csv(ROOT / "data" / "expansion_data_test.csv").rename(columns={"Molecule Name": "molecule_id"})
    train["canonical"] = train.SMILES.map(canonical)
    test["canonical"] = test.SMILES.map(canonical)
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    train = train.sort_values("molecule_id", kind="stable").reset_index(drop=True)
    identities = {row.canonical: f"{row.molecule_id}:train" for row in train.itertuples()}
    identities.update({row.canonical: f"{row.molecule_id}:test" for row in test.itertuples()})
    return train, identities, generator, [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in train.SMILES]


def candidate_record(smiles: str, seed: dict, raw: dict, train: pd.DataFrame, dataset_identities: dict[str, str], generator, train_fps: list) -> dict:
    molecule = Chem.MolFromSmiles(smiles)
    canonical_smiles = Chem.MolToSmiles(molecule, isomericSmiles=True)
    fp = generator.GetFingerprint(molecule)
    values = DataStructs.BulkTanimotoSimilarity(fp, train_fps)
    nearest_index = values.index(max(values))
    descriptors = {
        "molecular_weight_Da": round(float(Descriptors.MolWt(molecule)), 4),
        "rdkit_clogp": round(float(Crippen.MolLogP(molecule)), 4),
        "tpsa_A2": round(float(Descriptors.TPSA(molecule)), 4),
        "hbd": int(Lipinski.NumHDonors(molecule)), "hba": int(Lipinski.NumHAcceptors(molecule)),
        "rdkit_version": rdBase.rdkitVersion,
    }
    return {
        "candidate_id": f"C-{raw['raw_sample_index']:04d}", "generation_run_id": raw["generation_run_id"],
        "raw_sample_index": raw["raw_sample_index"], "seed_id": seed["seed_id"], "smiles": smiles,
        "canonical_isomeric_smiles": canonical_smiles, "checkpoint_id": raw["checkpoint_id"],
        "checkpoint_revision": raw["checkpoint_revision"], "exact_prompt": raw["exact_prompt"],
        "decoding_settings": raw["decoding_settings"], "random_seed_or_rng_state_scheme": raw["random_seed_or_rng_state_scheme"],
        "validation_status": "valid_unique", "rejection_reason": None, "duplicate_of": None,
        "similarity_to_seed": float(DataStructs.TanimotoSimilarity(fp, generator.GetFingerprint(Chem.MolFromSmiles(seed["smiles"])))),
        "nearest_training_id": str(train.iloc[nearest_index].molecule_id), "nearest_training_similarity": float(max(values)),
        "computed_descriptors": descriptors,
        "exact_dataset_match_id_and_split": dataset_identities.get(canonical_smiles),
        "measured_LogD": None, "measured_KSOL_uM": None, "measured_Caco2_Papp_A_to_B": None,
        "measured_Caco2_efflux": None,
        "evidence_status": "rediscovery_known_structure" if canonical_smiles in dataset_identities else "proposal_unmeasured",
    }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--smoke-only", action="store_true")
    args = parser.parse_args()
    config = read_json(args.config)
    RDLogger.DisableLog("rdApp.error")
    output = ROOT / "outputs" / "chemllama" / args.run_id
    output.mkdir(parents=True, exist_ok=False)

    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = h100_device_record(torch)
    seeds = read_json(ROOT / "outputs" / "chemllama_preparation" / "seed_manifest.json")["seeds"]
    per_seed = config["smoke_raw_samples_total"] if args.smoke_only else config["main_raw_samples_per_seed"]
    if args.smoke_only:
        plan = [(seeds[index % len(seeds)], index) for index in range(per_seed)]
    else:
        plan = [(seed, index) for seed in seeds for index in range(per_seed)]
    if len(plan) > config["max_total_raw_samples"]:
        raise ValueError("Configured run exceeds approved raw-sample cap")

    start = time.monotonic()
    model_path = snapshot_download(config["checkpoint_id"], revision=config["checkpoint_revision"], cache_dir=config["cache_dir"])
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    dtype = torch.bfloat16 if config["dtype"] == "bfloat16" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(model_path, dtype=dtype, local_files_only=True).to("cuda").eval()
    train, dataset_identities, generator, train_fps = training_context()
    raw_path = output / "raw_generation.jsonl"
    candidates: list[dict] = []
    seen: dict[str, str] = {}
    with raw_path.open("x") as raw_file, torch.inference_mode():
        for sample_index, (seed, local_index) in enumerate(plan):
            prompt = config["prompt_template"].format(seed_smiles=seed["smiles"])
            encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=True).to("cuda")
            # Transformers 5 removed ``generator=`` from generate; seed the
            # allocated CUDA RNG immediately before each recorded sample.
            torch.cuda.manual_seed_all(config["rng_seed"] + sample_index)
            generated = model.generate(**encoded, do_sample=True, temperature=config["temperature"], top_p=config["top_p"], top_k=config["top_k"], max_new_tokens=config["max_new_tokens"], pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id)
            continuation = tokenizer.decode(generated[0][encoded.input_ids.shape[1]:], skip_special_tokens=True)
            extracted, parsing_note = extract_smiles(continuation, seed["smiles"])
            raw = {"generation_run_id": args.run_id, "raw_sample_index": sample_index, "seed_id": seed["seed_id"], "checkpoint_id": config["checkpoint_id"], "checkpoint_revision": config["checkpoint_revision"], "exact_prompt": prompt, "random_seed_or_rng_state_scheme": f"cuda_manual_seed({config['rng_seed']} + raw_sample_index)", "decoding_settings": {key: config[key] for key in ("temperature", "top_p", "top_k", "max_new_tokens", "dtype")}, "raw_generated_text": continuation, "extracted_smiles": extracted, "extraction_method": parsing_note, "validation_status": "invalid", "rejection_reason": parsing_note}
            if extracted:
                candidate = candidate_record(extracted, seed, raw, train, dataset_identities, generator, train_fps)
                identity = candidate["canonical_isomeric_smiles"]
                if identity in seen:
                    raw["validation_status"] = "duplicate"; raw["rejection_reason"] = "duplicate_canonical_isomeric_smiles"; raw["duplicate_of"] = seen[identity]
                else:
                    seen[identity] = candidate["candidate_id"]
                    raw["validation_status"] = "valid_unique"; raw["rejection_reason"] = None
                    candidates.append(candidate)
            raw_file.write(json.dumps(raw, allow_nan=False) + "\n")
            raw_file.flush()
    pd.DataFrame(candidates).to_json(output / "candidates.json", orient="records", indent=2)
    counts = {"raw": len(plan), "valid_unique": len(candidates), "invalid": len(plan) - len(candidates) - sum(1 for line in raw_path.read_text().splitlines() if json.loads(line)["validation_status"] == "duplicate"), "duplicate": sum(1 for line in raw_path.read_text().splitlines() if json.loads(line)["validation_status"] == "duplicate")}
    manifest = {"generation_run_id": args.run_id, "created_at_utc": datetime.now(timezone.utc).isoformat(), "config": config, "model_path": model_path, "device": device, "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "slurm_node": os.environ.get("SLURMD_NODENAME"), "platform": platform.platform(), "runtime_seconds": round(time.monotonic() - start, 3), "counts": counts, "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(), "candidate_sha256": hashlib.sha256((output / "candidates.json").read_bytes()).hexdigest(), "prompt_preflight": "Raw continuation only; checkpoint has no model card at pinned revision, so no undocumented chemistry tag or similarity-conditioning claim is made."}
    write_json(output / "manifest.json", manifest)
    write_json(output / "summary.json", counts)


if __name__ == "__main__":
    main()
