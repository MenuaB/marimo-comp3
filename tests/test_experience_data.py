"""Regression checks for the guided-story data contracts."""
from __future__ import annotations

import unittest

from scripts.experience_data import (
    active_budget_reference,
    build_visual_payload,
    evidence_accounting,
    load_pinned_generation,
    scale_landmarks,
)
from scripts.notebook_data import build_fit_nomination_data, prepare


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
        self.assertAlmostEqual(first["random_expected_passes"], 50 * 905 / 2160)
        self.assertAlmostEqual(first["random_simulation_mean_passes"], 20.993)

    def test_fit_nomination_identity_pairing_and_prediction_only_order(self):
        nominations = build_fit_nomination_data(self.cohort)
        self.assertEqual(len(nominations["fit_keys"]), 25)
        self.assertTrue(all(len(ids) == 50 for ids in nominations["nominations"].values()))
        self.assertEqual(len(nominations["union_order"]), 256)
        self.assertEqual(nominations["intersection_ids"], ["E-0024329"])
        overlaps = list(nominations["fit_to_ensemble_overlap"].values())
        self.assertEqual((min(overlaps), max(overlaps)), (21, 36))
        self.assertEqual(float(__import__("numpy").median(overlaps)), 29.0)
        paired = {(row["molecule_id"], row["fit_key"]) for row in nominations["predictions"]}
        self.assertEqual(len(paired), 256 * 25)
        self.assertEqual(len(paired), len(nominations["predictions"]))

        altered = self.cohort.copy()
        altered["obs_LogD"] = 1000.0
        altered["obs_KSOL_uM"] = 0.0
        altered["measured_threshold_pass"] = False
        changed = build_fit_nomination_data(altered, force=True)
        self.assertEqual(nominations["union_order"], changed["union_order"])
        self.assertEqual(nominations["nominations"], changed["nominations"])
        self.assertEqual(nominations["intersection_ids"], changed["intersection_ids"])

    def test_visual_payload_preserves_ids_evidence_and_generation(self):
        payload = build_visual_payload()
        self.assertEqual(payload["schema_version"], "before-you-make-it-visual-v3")
        self.assertEqual(payload["retrospective"]["ensemble_target_passes"], 41)
        self.assertEqual(payload["retrospective"]["caco_paired"], 38)
        self.assertEqual(payload["retrospective"]["caco_paired_among_target_passes"], 33)
        self.assertEqual(payload["retrospective"]["fit_target_passes_summary"], {"minimum": 31, "median": 38.0, "maximum": 42})
        self.assertEqual(payload["depictions"]["encoding"], "gzip+base64")
        self.assertEqual(set(payload["depictions"]["items"]), set(payload["evidence_records"]))
        unanimous = payload["evidence_records"]["E-0024329"]
        self.assertAlmostEqual(unanimous["ensemble_prediction"]["LogD"], 1.9990820203)
        self.assertAlmostEqual(unanimous["measurement_summary"]["LogD"], 0.7)
        self.assertFalse(unanimous["measurement_summary"]["target_pass"])
        for candidate in payload["candidates"]:
            record = payload["evidence_records"][candidate["candidate_id"]]
            self.assertEqual(record["role"], "generated_proposal")
            self.assertTrue(all(endpoint["status"] == "missing" for endpoint in record["endpoints"]))


if __name__ == "__main__":
    unittest.main()
