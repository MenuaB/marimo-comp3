"""Audit ExpansionRx source data and draw the first selection-pressure plot.

Run with: python scripts/first_experiment.py
Dependencies are pinned in requirements-audit.txt. Inputs are downloaded at
fixed upstream revisions and checked against recorded SHA-256 hashes.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from urllib.request import urlretrieve

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import rdFingerprintGenerator


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
HF_REV = "6b898ccc43d10d25b230fb09e22a6e30c30022b5"
GH_REV = "06582771d48af8096f6b05a5a247b177189a8fa4"
HF_BASE = f"https://huggingface.co/datasets/openadmet/openadmet-expansionrx-challenge-data/resolve/{HF_REV}"
GH_BASE = f"https://raw.githubusercontent.com/PatWalters/expansion-ml-comparison/{GH_REV}"
SOURCES = {
    "expansion_data_train.csv": (f"{HF_BASE}/expansion_data_train.csv", "c5214ad8c8a4d7d4d09082fcce24fe16c97a980a1e0873b91b8c8e474b79f6e4"),
    "expansion_data_test.csv": (f"{HF_BASE}/expansion_data_test.csv", "e21c0ef19795317216287e924e00ca3ef9388b7032a7fa4c7f27e2580372c85e"),
    "expansion_data_raw.csv": (f"{HF_BASE}/expansion_data_raw.csv", "f674ec74cca1146bc386f832a32d4b8d921d3c312f92cb436cc005901c724a3c"),
    "expansion_log_scaled.csv": (f"{GH_BASE}/expansion_log_scaled.csv", "809d29584bdf4d8359d2bfa3c2673383c7f8fcef4c85ae5429915f53e8d3c858"),
    "predictions_all.parquet": (f"{GH_BASE}/results/expansion/predictions_all.parquet", "f53d4d674372b55db89b30e5d8e5a3445bef0210ae25b2b92509c317c72ffd54"),
}
MODELS = ["lgbm", "monroe", "chemeleon"]
MODEL_LABELS = {
    "lgbm": "Morgan + LightGBM",
    "monroe": "Monroe + TabPFN",
    "chemeleon": "ChemProp + CheMeleon",
}
FRACTIONS = [1.0, 0.5, 0.25, 0.10, 0.05, 0.02]


def fetch_inputs() -> None:
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(exist_ok=True)
    for name, (url, expected) in SOURCES.items():
        path = DATA / name
        if not path.exists():
            urlretrieve(url, path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError(f"Source checksum mismatch: {name}: {digest}")


def source_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "expansion_data_train.csv")
    test = pd.read_csv(DATA / "expansion_data_test.csv")
    raw = pd.read_csv(DATA / "expansion_data_raw.csv")
    benchmark = pd.read_csv(DATA / "expansion_log_scaled.csv")
    for frame in (train, test, raw):
        frame["Molecule Name"] = frame["Molecule Name"].astype(str)
    benchmark["Name"] = benchmark["Name"].astype(str)
    return train, test, raw, benchmark


def score(logd: np.ndarray, logs: np.ndarray, low: float, high: float, median_um: float) -> np.ndarray:
    """Illustrative train-defined desirability; not a universal medicinal target."""
    distance = np.maximum.reduce([low - logd, logd - high, np.zeros_like(logd)])
    logd_part = np.exp(-distance / ((high - low) / 2))
    ksol_um = np.maximum(np.power(10.0, np.clip(logs + 6.0, -6.0, 8.0)) - 1.0, 0.0)
    sol_part = ksol_um / (ksol_um + median_um)
    return np.sqrt(logd_part * sol_part)


def structure_audit(train: pd.DataFrame, test: pd.DataFrame, eligible_names: set[str]) -> dict:
    rdBase.DisableLog("rdApp.error")
    all_frames = [("train", train), ("test", test)]
    canonical = {}
    invalid = {}
    multicomponent = {}
    for part, frame in all_frames:
        strings = []
        bad = 0
        multi = 0
        for smiles in frame["SMILES"]:
            mol = Chem.MolFromSmiles(smiles) if isinstance(smiles, str) else None
            if mol is None:
                strings.append(None)
                bad += 1
            else:
                strings.append(Chem.MolToSmiles(mol, isomericSmiles=True))
                multi += int(len(Chem.GetMolFrags(mol)) > 1)
        canonical[part] = strings
        invalid[part] = bad
        multicomponent[part] = multi
    train_set = set(canonical["train"]) - {None}
    test_set = set(canonical["test"]) - {None}
    test_canon = dict(zip(test["Molecule Name"], canonical["test"]))
    eligible = [test_canon[n] for n in eligible_names]

    # Same definition is used later for the nearest-training-analog view.
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    train_fps = [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in sorted(train_set)]
    nearest = []
    for smiles in eligible:
        mol = Chem.MolFromSmiles(smiles) if smiles else None
        if mol is None:
            continue
        fp = generator.GetFingerprint(mol)
        nearest.append(max(DataStructs.BulkTanimotoSimilarity(fp, train_fps)))
    return {
        "invalid_smiles": invalid,
        "multi_component_smiles": multicomponent,
        "duplicate_canonical_within_train": len(canonical["train"]) - len(train_set) - invalid["train"],
        "duplicate_canonical_within_test": len(canonical["test"]) - len(test_set) - invalid["test"],
        "exact_canonical_structures_across_split": len(train_set & test_set),
        "eligible_nearest_train_morgan_median": float(np.median(nearest)),
        "eligible_nearest_train_morgan_ge_0_8": int(sum(x >= 0.8 for x in nearest)),
        "eligible_nearest_train_morgan_n": len(nearest),
    }


def prediction_data(test: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    path = DATA / "predictions_all.parquet"
    db = duckdb.connect()
    preds = db.execute(
        "SELECT method, endpoint, repeat, fold, Name, SMILES, y_true, y_pred "
        "FROM read_parquet(?) WHERE method IN ('lgbm', 'monroe', 'chemeleon') "
        "AND endpoint IN ('LogD', 'LogS')",
        [str(path)],
    ).df()
    full = test[test["LogD"].notna() & test["KSOL"].notna()].copy()
    full["observed_LogS"] = np.log10(full["KSOL"].to_numpy() + 1.0) - 6.0
    names = set(full["Molecule Name"])
    preds = preds[preds["Name"].isin(names)].copy()
    counts = preds.groupby(["method", "endpoint", "Name"]).size()
    per_model = {}
    for model in MODELS:
        for endpoint in ["LogD", "LogS"]:
            subset = preds[(preds.method == model) & (preds.endpoint == endpoint)]
            seen = set(subset["Name"])
            per_model[f"{model}/{endpoint}"] = {
                "molecules": len(seen),
                "rows": len(subset),
                "min_replicates": int(counts.loc[(model, endpoint)].min()),
                "max_replicates": int(counts.loc[(model, endpoint)].max()),
            }
            if seen != names or counts.loc[(model, endpoint)].min() != 25 or counts.loc[(model, endpoint)].max() != 25:
                raise ValueError(f"Incomplete predictions for {model}/{endpoint}")
            expected = full.set_index("Molecule Name")["LogD" if endpoint == "LogD" else "observed_LogS"]
            truth_delta = (subset["y_true"].to_numpy() - expected.loc[subset["Name"]].to_numpy())
            if np.nanmax(np.abs(truth_delta)) > 1e-7:
                raise ValueError(f"Prediction label mismatch for {model}/{endpoint}")
            smiles = full.set_index("Molecule Name")["SMILES"]
            if not (subset["SMILES"].to_numpy() == smiles.loc[subset["Name"]].to_numpy()).all():
                raise ValueError(f"SMILES mismatch for {model}/{endpoint}")

    mean_pred = preds.groupby(["method", "endpoint", "Name"], as_index=False)["y_pred"].mean()
    wide = mean_pred.pivot(index=["method", "Name"], columns="endpoint", values="y_pred").reset_index()
    wide = wide.rename(columns={"LogD": "pred_LogD", "LogS": "pred_LogS"})
    observed = full[["Molecule Name", "SMILES", "LogD", "KSOL", "observed_LogS"]].rename(
        columns={"LogD": "obs_LogD", "observed_LogS": "obs_LogS"}
    )
    wide = wide.merge(observed, left_on="Name", right_on="Molecule Name", validate="many_to_one")
    return wide, per_model


def pressure_results(wide: pd.DataFrame, train: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    complete_train = train[train["LogD"].notna() & train["KSOL"].notna()]
    low = float(complete_train["LogD"].quantile(0.25))
    high = float(complete_train["LogD"].quantile(0.75))
    median_um = float(complete_train["KSOL"].median())
    rule = {"LogD_window_train_IQR": [low, high], "KSOL_half_score_train_median_uM": median_um,
            "formula": "sqrt(exp(-distance_to_LogD_window / half_window_width) * KSOL_uM/(KSOL_uM + train_median_KSOL_uM))",
            "status": "illustrative pilot, fixed using training rows only"}
    rows = []
    for model in MODELS:
        part = wide[wide.method == model].copy()
        observed = score(part["obs_LogD"].to_numpy(), part["obs_LogS"].to_numpy(), low, high, median_um)
        predicted = score(part["pred_LogD"].to_numpy(), part["pred_LogS"].to_numpy(), low, high, median_um)
        order = np.argsort(-predicted, kind="stable")
        for fraction in FRACTIONS:
            k = max(1, int(round(len(part) * fraction)))
            chosen = order[:k]
            rows.append({"model": model, "fraction": fraction, "n": k,
                         "predicted_mean": float(np.mean(predicted[chosen])),
                         "observed_mean": float(np.mean(observed[chosen])),
                         "random_reference": float(np.mean(observed)),
                         "observed_oracle_ceiling": float(np.mean(np.sort(observed)[-k:]))})
    return pd.DataFrame(rows), rule


def main() -> None:
    fetch_inputs()
    train, test, raw, benchmark = source_data()
    for frame, label in [(train, "train"), (test, "test"), (raw, "raw")]:
        if frame["Molecule Name"].duplicated().any():
            raise ValueError(f"Duplicate source names in {label}")
    if set(train["Molecule Name"]) & set(test["Molecule Name"]):
        raise ValueError("Official train/test names overlap")
    train_names, test_names = set(train["Molecule Name"]), set(test["Molecule Name"])
    official_split = pd.concat([train, test], ignore_index=True)
    raw_join = official_split.merge(raw, on="Molecule Name", suffixes=("_split", "_raw"), validate="one_to_one")
    if not (raw_join["SMILES_split"] == raw_join["SMILES_raw"]).all():
        raise ValueError("Official split SMILES differ from official raw data")
    raw_censored = {}
    for endpoint in ["LogD", "KSOL"]:
        raw_values = raw_join[f"{endpoint}_raw"].astype(str)
        split_values = pd.to_numeric(raw_join[f"{endpoint}_split"], errors="coerce")
        numeric_raw = pd.to_numeric(raw_values, errors="coerce")
        if not np.isclose(split_values, numeric_raw, equal_nan=True).all():
            raise ValueError(f"Official split {endpoint} differs from raw data")
        raw_censored[endpoint] = int(raw_values.str.contains(r"[<>]").sum())
    bench_train = benchmark[benchmark.ds == "train"]
    bench_test = benchmark[benchmark.ds == "test"]
    if train_names != set(bench_train.Name) or test_names != set(bench_test.Name):
        raise ValueError("Benchmark does not match official train/test molecules")
    for official, bench in [(train, bench_train), (test, bench_test)]:
        joined = official.merge(bench, left_on="Molecule Name", right_on="Name", validate="one_to_one")
        if not (joined["SMILES_x"] == joined["SMILES_y"]).all():
            raise ValueError("Benchmark SMILES differ from official source")
        logd_delta = (joined["LogD_x"] - joined["LogD_y"]).abs().dropna()
        logs_delta = (np.log10(joined["KSOL"] + 1.0) - 6.0 - joined["LogS"]).abs().dropna()
        if logd_delta.max() > 1e-8 or logs_delta.max() > 1e-8:
            raise ValueError("Benchmark transform differs from official source")

    full = test[test["LogD"].notna() & test["KSOL"].notna()].copy()
    structure = structure_audit(train, test, set(full["Molecule Name"]))
    wide, prediction_coverage = prediction_data(test)
    if len(wide) != len(full) * len(MODELS):
        raise ValueError("Not all eligible rows have all model predictions")
    pressure, rule = pressure_results(wide, train)
    pressure.to_csv(OUTPUTS / "first_pressure_data.csv", index=False)

    raw_extra = set(raw["Molecule Name"]) - train_names - test_names
    clusters_train = set(bench_train.cluster)
    clusters_test = set(bench_test.cluster)
    audit = {
        "sources": {name: {"url": url, "sha256": checksum} for name, (url, checksum) in SOURCES.items()},
        "rows": {"official_train": len(train), "official_test": len(test), "official_raw": len(raw),
                 "benchmark_train": len(bench_train), "benchmark_test": len(bench_test),
                 "raw_only_not_in_split": len(raw_extra),
                 "test_LogD": int(test.LogD.notna().sum()), "test_KSOL": int(test.KSOL.notna().sum()),
                 "test_both": len(full), "train_both": int((train.LogD.notna() & train.KSOL.notna()).sum())},
        "raw_extra_names": sorted(raw_extra),
        "explicitly_censored_raw_labels_in_split": raw_censored,
        "official_raw_to_split": "Split molecules have identical SMILES and numeric LogD/KSOL values; explicit inequality labels become missing",
        "official_to_benchmark": "Exact name and SMILES match; LogD unchanged; LogS = log10(KSOL_uM + 1) - 6",
        "benchmark_clusters_crossing_split": len(clusters_train & clusters_test),
        "structures": structure,
        "prediction_coverage": prediction_coverage,
        "pilot_scoring_rule": rule,
    }
    (OUTPUTS / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6), sharey=True)
    for ax, model in zip(axes, MODELS):
        part = pressure[(pressure.model == model) & (pressure.fraction < 1)].sort_values("fraction", ascending=False)
        x = np.arange(len(part))
        ax.plot(x, part.predicted_mean, "--o", color="#4072a4", label="Predicted winner score", markersize=4)
        ax.plot(x, part.observed_mean, "-o", color="#d07036", label="Measured winner score", markersize=4)
        ax.plot(x, part.random_reference, ":", color="#777777", label="Random-selection mean")
        ax.plot(x, part.observed_oracle_ceiling, "-.", color="#777777", label="Measured best possible")
        ax.set_xticks(x, [f"{int(f * 100)}\n(n={n:,})" for f, n in zip(part.fraction, part.n)])
        ax.set_xlim(-0.2, len(part) - 0.8)
        ax.set_ylim(0.55, 0.9)
        ax.set_title(MODEL_LABELS[model], fontsize=11)
        ax.grid(axis="y", color="0.88", linewidth=0.7)
    axes[0].set_ylabel("Mean joint desirability (0–1)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.subplots_adjust(left=0.07, right=0.99, top=0.82, bottom=0.28, wspace=0.10)
    fig.suptitle("Do predicted ADMET winners win in measured data?", fontsize=14, y=0.97)
    fig.supxlabel("Test molecules retained (%)", fontsize=10, y=0.15)
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.075), fontsize=8)
    fig.text(0.5, 0.018, "OpenADMET ExpansionRx released test measurements (n=2,160); Pat Walters' stored model predictions. Pilot score fixed from training data.", ha="center", fontsize=8)
    fig.savefig(OUTPUTS / "first_pressure_plot.png", dpi=190)
    fig.savefig(OUTPUTS / "first_pressure_plot.pdf")
    plt.close(fig)
    print(json.dumps({"rows": audit["rows"], "structures": structure, "pilot_scoring_rule": rule}, indent=2))
    print(pressure.to_string(index=False))


if __name__ == "__main__":
    main()
