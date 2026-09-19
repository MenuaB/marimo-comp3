"""Regression checks for the guided-story data contracts."""
from __future__ import annotations

import unittest

from scripts.experience_data import active_budget_reference, evidence_accounting, load_pinned_generation, scale_landmarks
from scripts.notebook_data import prepare


class ExperienceDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cohort, _, _ = prepare()

    def test_pinned_generation_is_the_approved_run_with_raw_provenance(self):
        candidates, manifest, seeds = load_pinned_generation()
        self.assertEqual(manifest["generation_run_id"], "chemllama-271948")
        self.assertEqual(manifest["counts"], {"raw": 96, "valid_unique": 27, "invalid": 69, "duplicate": 0})
        self.assertEqual(len(candidates), 27)
        self.assertTrue(set(candidates.seed_id).issubset({seed["seed_id"] for seed in seeds}))
        self.assertTrue(candidates.measured_LogD.isna().all())
        self.assertTrue(candidates.measured_KSOL_uM.isna().all())

    def test_scale_and_recorded_evidence_accounting(self):
        landmarks = scale_landmarks()
        self.assertEqual(landmarks[-1]["count"], 166_000_000_000)
        self.assertAlmostEqual(landmarks[-1]["hypothetical_years_at_one_per_second"], 5260.222577128806)
        accounting = evidence_accounting()
        self.assertEqual(accounting["records"], 7608)
        self.assertEqual(accounting["recorded_values"], 36003)
        self.assertEqual(accounting["possible_cells"], 68472)
        self.assertEqual(accounting["missing_or_non_numeric"], 32469)

    def test_fixed_fifty_comparator_is_same_cohort_and_deterministic(self):
        first = active_budget_reference(self.cohort, 50)
        second = active_budget_reference(self.cohort, 50)
        self.assertEqual(first, second)
        self.assertEqual(first["selected_passes"], 41)
        self.assertEqual(first["selected_count"], 50)
        self.assertAlmostEqual(first["random_expected_passes"], 20.993)


if __name__ == "__main__":
    unittest.main()
