"""Verified data preparation for the Before You Make It notebook.

This module deliberately does not import the historical plotting script.  It
uses the same source revisions, transform, score, and stable ranking, while
putting reproducible notebook caches under ``data/notebook_cache``.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from urllib.request import urlopen

import duckdb
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import rdFingerprintGenerator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "notebook_cache"
AUDIT_PATH = ROOT / "outputs" / "audit.json"
ANALYSIS_CONFIG_PATH = ROOT / "config" / "notebook_analysis.json"
SCHEMA_VERSION = "before-you-make-it-v2"
FRACTIONS = (0.50, 0.25, 0.10, 0.05, 0.02)
RANDOM_SEED = 20260918


def analysis_config() -> dict[str, object]:
    """Read the small, explicit analysis contract used by cache and notebook."""
    return json.loads(ANALYSIS_CONFIG_PATH.read_text())


def _sources() -> dict[str, dict[str, str]]:
    return json.loads(AUDIT_PATH.read_text())["sources"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_sources() -> dict[str, str]:
    """Fetch absent pinned inputs atomically and reject any digest mismatch."""
    DATA.mkdir(exist_ok=True)
    sources = _sources()
    hashes: dict[str, str] = {}
    for name, source in sources.items():
        path = DATA / name
        if not path.exists():
            fd, temporary = tempfile.mkstemp(prefix=f".{name}.", dir=DATA)
            try:
                with os.fdopen(fd, "wb") as out, urlopen(source["url"]) as response:
                    while block := response.read(1024 * 1024):
                        out.write(block)
                candidate = Path(temporary)
                if sha256(candidate) != source["sha256"]:
                    raise ValueError(f"Downloaded checksum mismatch: {name}")
                candidate.replace(path)
            finally:
                Path(temporary).unlink(missing_ok=True)
        digest = sha256(path)
        if digest != source["sha256"]:
            raise ValueError(
                f"Existing checksum mismatch for {name}: {digest}; expected {source['sha256']}"
            )
        hashes[name] = digest
    return hashes


def logs_from_ksol(ksol_um: np.ndarray | pd.Series) -> np.ndarray:
    values = np.asarray(ksol_um, dtype=float)
    return np.log10(values + 1.0) - 6.0


def ksol_from_logs(logs: np.ndarray | pd.Series) -> np.ndarray:
    values = np.asarray(logs, dtype=float)
    return np.maximum(np.power(10.0, np.clip(values + 6.0, -6.0, 8.0)) - 1.0, 0.0)


def score(logd: np.ndarray | pd.Series, logs: np.ndarray | pd.Series, logd_low: float, logd_high: float, ksol_median_um: float) -> np.ndarray:
    """Pilot-compatible illustrative desirability, calculated in LogS space."""
    logd_values = np.asarray(logd, dtype=float)
    distance = np.maximum.reduce([logd_low - logd_values, logd_values - logd_high, np.zeros_like(logd_values)])
    logd_component = np.exp(-distance / ((logd_high - logd_low) / 2.0))
    ksol_um = ksol_from_logs(logs)
    solubility_component = ksol_um / (ksol_um + ksol_median_um)
    return np.sqrt(logd_component * solubility_component)


def score_from_observed(logd: np.ndarray | pd.Series, ksol_um: np.ndarray | pd.Series, constants: dict[str, float]) -> np.ndarray:
    return score(logd, logs_from_ksol(ksol_um), **constants)


def _cache_identity(hashes: dict[str, str]) -> dict[str, object]:
    config = analysis_config()
    return {
        "schema_version": SCHEMA_VERSION,
        "source_hashes": hashes,
        "rdkit": rdBase.rdkitVersion,
        "analysis": config,
    }


def _read_cache(identity: dict[str, object]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]] | None:
    manifest_path = CACHE / "manifest.json"
    table_path = CACHE / "joined.pkl"
    metrics_path = CACHE / "pressure_metrics.csv"
    if not (manifest_path.exists() and table_path.exists() and metrics_path.exists()):
        return None
    manifest = json.loads(manifest_path.read_text())
    # JSON makes tuples lists, so compare canonical JSON-compatible identity.
    if json.dumps(manifest.get("identity"), sort_keys=True) != json.dumps(identity, sort_keys=True):
        return None
    try:
        return pd.read_pickle(table_path), pd.read_csv(metrics_path), manifest
    except (ValueError, OSError, EOFError):
        return None


def _canonical(smiles: str) -> str:
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    return Chem.MolToSmiles(molecule, isomericSmiles=True)


def _nearest_training(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    ordered_train = train.sort_values("molecule_id", kind="stable").reset_index(drop=True)
    train_fps = [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in ordered_train["SMILES"]]
    nearest_ids: list[str] = []
    similarities: list[float] = []
    for smiles in test["SMILES"]:
        fp = generator.GetFingerprint(Chem.MolFromSmiles(smiles))
        values = DataStructs.BulkTanimotoSimilarity(fp, train_fps)
        highest = max(values)
        # train is ID sorted, so this makes ties deterministic.
        nearest_ids.append(str(ordered_train.iloc[values.index(highest)]["molecule_id"]))
        similarities.append(float(highest))
    return pd.DataFrame({"nearest_training_id": nearest_ids, "nearest_training_similarity": similarities})


def _validate_predictions(predictions: pd.DataFrame, expected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    expected_names = set(expected["molecule_id"])
    subset = predictions[(predictions.method == "lgbm") & predictions.endpoint.isin(["LogD", "LogS"])].copy()
    subset = subset[subset.Name.isin(expected_names)]
    keys = subset.groupby(["endpoint", "Name"]).size()
    if len(keys) != len(expected) * 2 or keys.min() != 25 or keys.max() != 25:
        raise ValueError("LGBM predictions must have exactly 25 rows per eligible molecule and endpoint")
    fit_keys = subset[["repeat", "fold"]].drop_duplicates()
    if len(fit_keys) != 25:
        raise ValueError("Expected 25 distinct repeat/fold prediction keys")
    for endpoint in ("LogD", "LogS"):
        endpoint_keys = subset.loc[subset.endpoint == endpoint, ["Name", "repeat", "fold"]]
        if endpoint_keys.duplicated().any() or endpoint_keys.groupby("Name").size().nunique() != 1:
            raise ValueError(f"Incomplete distinct repeat/fold coverage for {endpoint}")
    for endpoint, column in (("LogD", "obs_LogD"), ("LogS", "obs_LogS")):
        part = subset[subset.endpoint == endpoint]
        truth = expected.set_index("molecule_id")[column]
        delta = np.abs(part.y_true.to_numpy() - truth.loc[part.Name].to_numpy())
        if not np.all(np.isfinite(delta)) or delta.max() > 1e-7:
            raise ValueError(f"Stored y_true does not match {endpoint} source data")
    mean = subset.groupby(["Name", "endpoint"], as_index=False)["y_pred"].mean()
    wide = mean.pivot(index="Name", columns="endpoint", values="y_pred").reset_index()
    fit_wide = subset.pivot(index=["Name", "repeat", "fold"], columns="endpoint", values="y_pred").reset_index()
    return (wide.rename(columns={"Name": "molecule_id", "LogD": "pred_LogD", "LogS": "pred_LogS"}),
            fit_wide.rename(columns={"Name": "molecule_id", "LogD": "pred_fit_LogD", "LogS": "pred_fit_LogS"}))


def _random_intervals(observed: np.ndarray, sizes: list[int], seed: int, draws: int) -> dict[int, tuple[float, float]]:
    rng = np.random.default_rng(seed)
    intervals: dict[int, tuple[float, float]] = {}
    n = len(observed)
    for size in sizes:
        samples = np.empty(draws, dtype=float)
        for index in range(len(samples)):
            samples[index] = observed[rng.choice(n, size=size, replace=False)].mean()
        intervals[size] = (float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975)))
    return intervals


def _metrics(table: pd.DataFrame, constants: dict[str, float], config: dict[str, object]) -> pd.DataFrame:
    ordered = table.sort_values(["pred_score", "molecule_id"], ascending=[False, True], kind="stable")
    observed_all = table["obs_score"].to_numpy()
    sizes = [max(1, int(round(len(table) * fraction))) for fraction in FRACTIONS]
    intervals = _random_intervals(observed_all, sizes, int(config["random_shortlist_seed"]), int(config["random_shortlist_draws"]))
    rows = []
    for fraction, size in zip(FRACTIONS, sizes):
        selected = ordered.head(size)
        pass_rule = (selected.obs_LogD.between(constants["logd_low"], constants["logd_high"]) & (selected.obs_KSOL_uM >= constants["ksol_median_um"]))
        rows.append({
            "fraction": fraction, "n": size,
            "predicted_mean": selected.pred_score.mean(), "measured_mean": selected.obs_score.mean(),
            "measured_gain_over_whole": selected.obs_score.mean() - observed_all.mean(),
            "prediction_minus_measurement": selected.pred_score.mean() - selected.obs_score.mean(),
            "measured_count": int(selected.obs_score.notna().sum()),
            "threshold_pass_count": int(pass_rule.sum()), "threshold_pass_fraction": float(pass_rule.mean()),
            "random_mean": float(observed_all.mean()),
            "random_low_95": intervals[size][0], "random_high_95": intervals[size][1],
        })
    return pd.DataFrame(rows)


def shortlist(table: pd.DataFrame, count: int) -> pd.DataFrame:
    if count not in analysis_config()["shortlist_counts"]:
        raise ValueError(f"Unsupported shortlist count: {count}")
    return table.sort_values(["pred_score", "molecule_id"], ascending=[False, True], kind="stable").head(count).copy()


def selection_stability(fit_predictions: pd.DataFrame, constants: dict[str, float], count: int = 50) -> pd.DataFrame:
    """Pair endpoints by the same fit key, then count inclusion in each fit top-k."""
    work = fit_predictions.copy()
    work["fit_score"] = score(work.pred_fit_LogD, work.pred_fit_LogS, **constants)
    selected = (work.sort_values(["repeat", "fold", "fit_score", "molecule_id"], ascending=[True, True, False, True], kind="stable")
                .groupby(["repeat", "fold"], group_keys=False).head(count))
    frequency = selected.groupby("molecule_id").size().rename("selection_stability_count").reset_index()
    return frequency


def prepare(force: bool = False) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Return the fixed test cohort, pressure metrics, and preparation manifest."""
    hashes = ensure_sources()
    config = analysis_config()
    identity = _cache_identity(hashes)
    if not force:
        cached = _read_cache(identity)
        if cached is not None:
            return cached

    train_raw = pd.read_csv(DATA / "expansion_data_train.csv")
    test_raw = pd.read_csv(DATA / "expansion_data_test.csv")
    benchmark = pd.read_csv(DATA / "expansion_log_scaled.csv")
    if len(train_raw) != 5326 or len(test_raw) != 2282:
        raise ValueError("Unexpected official split size")
    complete_train = train_raw.dropna(subset=["LogD", "KSOL"])
    if len(complete_train) != 4934:
        raise ValueError("Unexpected training complete-case count")
    constants = {
        "logd_low": float(complete_train.LogD.quantile(0.25)),
        "logd_high": float(complete_train.LogD.quantile(0.75)),
        "ksol_median_um": float(complete_train.KSOL.median()),
    }
    if constants != {"logd_low": 1.4, "logd_high": 2.9, "ksol_median_um": 125.5}:
        raise ValueError(f"Unexpected training-derived constants: {constants}")
    benchmark = benchmark.rename(columns={"Name": "molecule_id", "SMILES": "benchmark_SMILES"})
    train = train_raw.rename(columns={"Molecule Name": "molecule_id"}).merge(
        benchmark.loc[benchmark.ds == "train", ["molecule_id", "benchmark_SMILES", "cluster"]], on="molecule_id", validate="one_to_one"
    )
    test = test_raw.rename(columns={"Molecule Name": "molecule_id"}).dropna(subset=["LogD", "KSOL"]).copy()
    if len(test) != 2160:
        raise ValueError("Unexpected paired test cohort count")
    test = test.rename(columns={"LogD": "obs_LogD", "KSOL": "obs_KSOL_uM"})
    test["obs_LogS"] = logs_from_ksol(test.obs_KSOL_uM)
    test = test.merge(
        benchmark.loc[benchmark.ds == "test", ["molecule_id", "benchmark_SMILES", "cluster"]], on="molecule_id", validate="one_to_one"
    )
    if not (test.SMILES == test.benchmark_SMILES).all() or not (train.SMILES == train.benchmark_SMILES).all():
        raise ValueError("Official and benchmark structures disagree")
    test["canonical_isomeric_smiles"] = test.SMILES.map(_canonical)
    train["canonical_isomeric_smiles"] = train.SMILES.map(_canonical)
    if set(test.canonical_isomeric_smiles) & set(train.canonical_isomeric_smiles):
        raise ValueError("Exact canonical train/test overlap")

    connection = duckdb.connect()
    predictions = connection.execute(
        "SELECT method, endpoint, repeat, fold, Name, SMILES, y_true, y_pred FROM read_parquet(?) "
        "WHERE method = 'lgbm' AND endpoint IN ('LogD', 'LogS')", [str(DATA / "predictions_all.parquet")]
    ).df()
    means, fit_predictions = _validate_predictions(predictions, test)
    table = test.merge(means, on="molecule_id", validate="one_to_one")
    table = pd.concat([table.reset_index(drop=True), _nearest_training(train, table)], axis=1)
    table["split"] = "test"
    table["prediction_count_per_endpoint"] = 25
    table["pred_KSOL_uM"] = ksol_from_logs(table.pred_LogS)
    table["obs_score"] = score_from_observed(table.obs_LogD, table.obs_KSOL_uM, constants)
    table["pred_score"] = score(table.pred_LogD, table.pred_LogS, **constants)
    table["measured_threshold_pass"] = table.obs_LogD.between(constants["logd_low"], constants["logd_high"]) & (table.obs_KSOL_uM >= constants["ksol_median_um"])
    stability = selection_stability(fit_predictions, constants)
    table = table.merge(stability, on="molecule_id", how="left", validate="one_to_one")
    table["selection_stability_count"] = table.selection_stability_count.fillna(0).astype(int)
    if not np.isfinite(table[["pred_LogD", "pred_LogS", "pred_score", "obs_score"]].to_numpy()).all():
        raise ValueError("Non-finite analysis output")
    metrics = _metrics(table, constants, config)
    reference = metrics.loc[np.isclose(metrics.fraction, 0.10)].iloc[0]
    strict = metrics.loc[np.isclose(metrics.fraction, 0.02)].iloc[0]
    if not (math.isclose(reference.predicted_mean, 0.7942619913570331, abs_tol=1e-9) and math.isclose(reference.measured_mean, 0.7461249726859417, abs_tol=1e-9) and math.isclose(strict.predicted_mean, 0.8248401217273029, abs_tol=1e-9) and math.isclose(strict.measured_mean, 0.7538348622359935, abs_tol=1e-9)):
        raise ValueError("Pilot aggregate regression mismatch")

    CACHE.mkdir(parents=True, exist_ok=True)
    table.to_pickle(CACHE / "joined.pkl")
    metrics.to_csv(CACHE / "pressure_metrics.csv", index=False)
    stability.to_csv(CACHE / "selection_stability.csv", index=False)
    top_50 = shortlist(table, 50)
    caco_numeric = top_50.dropna(subset=["Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux"])
    manifest = {
        "identity": identity, "constants": constants, "rows": {"train_complete": len(complete_train), "test_paired": len(table)},
        "missing_test_accounting": {"total_test": 2282, "numeric_LogD": 2270, "numeric_KSOL": 2170, "paired": 2160, "outside_paired": 122},
        "cluster_cross_split": int(len(set(benchmark.loc[benchmark.ds == "train", "cluster"]) & set(benchmark.loc[benchmark.ds == "test", "cluster"]))),
        "nearest_training": {"median": float(table.nearest_training_similarity.median()), "ge_0_8": int((table.nearest_training_similarity >= 0.8).sum())},
        "top_50": {
            "predicted_mean": float(top_50.pred_score.mean()), "measured_mean": float(top_50.obs_score.mean()),
            "target_passes": int(top_50.measured_threshold_pass.sum()), "clusters": int(top_50.cluster.nunique()),
            "caco2_paired_numeric": int(len(caco_numeric)),
            "caco2_paired_numeric_among_target_passes": int(caco_numeric.measured_threshold_pass.sum()),
            "stability": {"union": int(len(stability)), "minimum": int(top_50.selection_stability_count.min()), "median": float(top_50.selection_stability_count.median()), "maximum": int(top_50.selection_stability_count.max())},
        },
    }
    temporary = CACHE / "manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    temporary.replace(CACHE / "manifest.json")
    return table, metrics, manifest


def training_seeds() -> list[dict[str, object]]:
    """Select three high-score complete training examples from distinct clusters."""
    ensure_sources()
    train = pd.read_csv(DATA / "expansion_data_train.csv").dropna(subset=["LogD", "KSOL"]).rename(columns={"Molecule Name": "molecule_id"})
    benchmark = pd.read_csv(DATA / "expansion_log_scaled.csv")
    clusters = benchmark.loc[benchmark.ds == "train", ["Name", "cluster"]].rename(columns={"Name": "molecule_id"})
    train = train.merge(clusters, on="molecule_id", validate="one_to_one")
    constants = {"logd_low": 1.4, "logd_high": 2.9, "ksol_median_um": 125.5}
    train["measured_score"] = score_from_observed(train.LogD, train.KSOL, constants)
    chosen = train.sort_values(["measured_score", "molecule_id"], ascending=[False, True], kind="stable").drop_duplicates("cluster").head(3)
    return [{
        "seed_id": row.molecule_id, "smiles": row.SMILES, "canonical_isomeric_smiles": _canonical(row.SMILES),
        "cluster": int(row.cluster), "measured_LogD": float(row.LogD), "measured_KSOL_uM": float(row.KSOL),
        "measured_score": float(row.measured_score),
    } for row in chosen.itertuples(index=False)]
