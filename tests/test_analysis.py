"""Focused regression checks for the notebook's scientific data path."""
from __future__ import annotations

import json
import math
import unittest

import numpy as np

from scripts.notebook_data import ksol_from_logs, logs_from_ksol, prepare, score, score_from_observed, shortlist


class NotebookAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cohort, cls.metrics, cls.manifest = prepare()
        cls.constants = cls.manifest["constants"]

    def test_source_cohort_and_pilot_regressions(self):
        self.assertEqual(len(self.cohort), 2160)
        self.assertEqual(self.manifest["rows"]["train_complete"], 4934)
        self.assertEqual(self.manifest["missing_test_accounting"]["outside_paired"], 122)
        top_10 = self.metrics.loc[np.isclose(self.metrics.fraction, 0.10)].iloc[0]
        top_2 = self.metrics.loc[np.isclose(self.metrics.fraction, 0.02)].iloc[0]
        self.assertEqual(int(top_10.n), 216)
        self.assertEqual(int(top_2.n), 43)
        self.assertAlmostEqual(top_10.predicted_mean, 0.7942619913570331, places=12)
        self.assertAlmostEqual(top_10.measured_mean, 0.7461249726859417, places=12)
        self.assertAlmostEqual(top_2.predicted_mean, 0.8248401217273029, places=12)
        self.assertAlmostEqual(top_2.measured_mean, 0.7538348622359935, places=12)

    def test_observed_changes_cannot_change_prediction_ranking_or_constants(self):
        original_order = self.cohort.sort_values(["pred_score", "molecule_id"], ascending=[False, True], kind="stable").molecule_id.tolist()
        altered = self.cohort.copy()
        altered["obs_LogD"] = altered["obs_LogD"] + 100.0
        altered["obs_KSOL_uM"] = 0.0
        altered["obs_score"] = score_from_observed(altered.obs_LogD, altered.obs_KSOL_uM, self.constants)
        altered_order = altered.sort_values(["pred_score", "molecule_id"], ascending=[False, True], kind="stable").molecule_id.tolist()
        self.assertEqual(original_order, altered_order)
        self.assertEqual(self.constants, {"logd_low": 1.4, "logd_high": 2.9, "ksol_median_um": 125.5})

    def test_nested_shortlists_and_shared_denominators(self):
        ordered = self.cohort.sort_values(["pred_score", "molecule_id"], ascending=[False, True], kind="stable")
        previous = set(ordered.head(1080).molecule_id)
        for fraction, size in [(0.25, 540), (0.10, 216), (0.05, 108), (0.02, 43)]:
            selected = ordered.head(size)
            self.assertTrue(set(selected.molecule_id).issubset(previous))
            row = self.metrics.loc[np.isclose(self.metrics.fraction, fraction)].iloc[0]
            actual_pass = (selected.obs_LogD.between(1.4, 2.9) & (selected.obs_KSOL_uM >= 125.5)).sum()
            self.assertEqual(int(row.measured_count), size)
            self.assertEqual(int(row.threshold_pass_count), int(actual_pass))
            previous = set(selected.molecule_id)

    def test_score_thresholds_transform_and_zero_handling(self):
        self.assertAlmostEqual(float(logs_from_ksol(np.array([0.0]))[0]), -6.0)
        self.assertAlmostEqual(float(ksol_from_logs(np.array([-6.0]))[0]), 0.0, places=12)
        values = np.array([0.0, 1.0, 125.5, 1000.0])
        self.assertTrue(np.allclose(ksol_from_logs(logs_from_ksol(values)), values, atol=1e-10))
        boundary = score(np.array([1.4, 2.9, 1.399]), np.array([-3.0, -3.0, -3.0]), **self.constants)
        self.assertGreaterEqual(boundary[0], boundary[2])
        self.assertTrue(np.all((self.cohort.obs_score >= 0) & (self.cohort.obs_score <= 1)))

    def test_nearest_analogs_are_training_context_and_json_null_is_standard(self):
        train_ids = set(__import__("pandas").read_csv("data/expansion_data_train.csv")["Molecule Name"])
        self.assertTrue(set(self.cohort.nearest_training_id).issubset(train_ids))
        self.assertTrue(np.all((self.cohort.nearest_training_similarity >= 0) & (self.cohort.nearest_training_similarity <= 1)))
        self.assertAlmostEqual(float(self.cohort.nearest_training_similarity.median()), 0.6363636363636364)
        self.assertEqual(int((self.cohort.nearest_training_similarity >= 0.8).sum()), 242)
        record = {"measured_LogD": None, "measured_KSOL_uM": None, "evidence_status": "proposal_unmeasured"}
        encoded = json.dumps(record, allow_nan=False)
        self.assertIn("null", encoded)
        self.assertNotIn("NaN", encoded)

    def test_default_fifty_caco2_and_stability_regressions(self):
        selected = shortlist(self.cohort, 50)
        self.assertEqual(len(selected), 50)
        self.assertAlmostEqual(selected.pred_score.mean(), 0.8228211410121915, places=12)
        self.assertAlmostEqual(selected.obs_score.mean(), 0.7485762984188178, places=12)
        self.assertEqual(int(selected.measured_threshold_pass.sum()), 41)
        self.assertEqual(int(selected.cluster.nunique()), 16)
        paired = selected.dropna(subset=["Caco-2 Permeability Papp A>B", "Caco-2 Permeability Efflux"])
        self.assertEqual(len(paired), 38)
        self.assertEqual(int(paired.measured_threshold_pass.sum()), 33)
        self.assertEqual(int(selected.selection_stability_count.min()), 4)
        self.assertEqual(float(selected.selection_stability_count.median()), 15.0)
        self.assertEqual(int(selected.selection_stability_count.max()), 25)

    def test_cache_identity_is_json_canonical_and_warm_cache_hits(self):
        first, metrics, manifest = prepare()
        second, _, repeat_manifest = prepare()
        self.assertEqual(manifest["identity"], repeat_manifest["identity"])
        self.assertEqual(first.molecule_id.tolist(), second.molecule_id.tolist())
        self.assertIsInstance(manifest["identity"]["analysis"]["shortlist_counts"], list)


if __name__ == "__main__":
    unittest.main()
