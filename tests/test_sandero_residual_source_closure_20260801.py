from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def payload(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

class SanderoResidualSourceClosureTests(unittest.TestCase):
    def test_spec_has_three_exact_rows(self):
        spec = rows(ROOT / "data/imports/sandero_residual_source_closure_20260801.csv")
        self.assertEqual(len(spec), 3)
        self.assertEqual({row["record_type"] for row in spec}, {"value", "availability"})

    def test_two_wheel_finish_values_are_exact(self):
        selected = {
            (row["configuration_code"], row["attribute_code"]): row
            for row in rows(ROOT / "data/master/configuration_attribute_values.csv")
            if row["code"].endswith("_residual_source_closure_20260626")
        }
        self.assertEqual(selected[("sandero_iii_expression_ecog120_manual", "wheel_finish")]["value"], "stalowe")
        self.assertEqual(selected[("sandero_iii_journey_ecog120_manual", "wheel_finish")]["value"], "aluminiowe")
        self.assertEqual({int(row["id"]) for row in selected.values()}, {3566, 3567})

    def test_journey_parking_assistance_is_standard(self):
        selected = [
            row for row in rows(ROOT / "data/master/configuration_attribute_availability.csv")
            if row["code"].endswith("_residual_source_closure_20260626")
        ]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["attribute_code"], "parking_assist_system")
        self.assertEqual(selected[0]["availability_status"], "standard")
        self.assertEqual(int(selected[0]["id"]), 5906)

    def test_source_hashes_match_registered_files(self):
        expected = {
            "PDF/Cenniki/NOWE SANDERO expression Eco-G 120 f.pdf": "82a8853d90b492e48595ff33db73632dc309b8a12d08d11dd3c259fca4eaff68",
            "PDF/Cenniki/NOWE SANDERO journey Eco-G 120 f.pdf": "7ab1526e7bc2a72ff2b179f30cd0c8c223633f1100d31aa7dd80594325b302a3",
            "PDF/Cenniki/DACIA SANDERO I SANDERO STEPWAY cennik MY26 20260703.pdf": "5af2dbaf268480ec1e7e6d6e35fd2037b6fba3fb79972026e4f68c08055ba783",
        }
        for relative, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), digest)

    def test_all_three_sources_have_exhaustion_receipts(self):
        names = [
            "sandero_expression_source_gap_review.json",
            "sandero_journey_source_gap_review.json",
            "sandero_tce_catalog_source_gap_review.json",
        ]
        reviews = [payload(ROOT / "data/reporting" / name) for name in names]
        self.assertEqual({item["reconciliation"]["classification"] for item in reviews}, {"source_exhausted_not_stated"})

    def test_tce_review_preserves_nine_unimported_slots(self):
        review = payload(ROOT / "data/reporting/sandero_tce_catalog_source_gap_review.json")
        remaining = review["reconciliation"]["remaining_slots"]
        self.assertEqual(len(remaining), 9)
        self.assertEqual(sum(item["attribute_code"] == "elasticity_80_120" for item in remaining), 6)
        self.assertEqual(sum(item["attribute_code"] == "overall_height" for item in remaining), 3)
        self.assertTrue(all(item.get("gear_number", "") == "" for item in remaining))

    def test_analysis_has_no_eligible_source_candidate(self):
        report = payload(ROOT / "data/reporting/existing_configuration_missing_data_analysis.json")
        self.assertEqual(report["summary"]["eligible_candidate_count"], 0)
        self.assertIsNone(report["selected_next_package"] )
        ranked = {item["source_code"]: item for item in report["ranked_candidates"]}
        self.assertEqual(ranked["src_pl_sandero_stepway_catalog_tce_slice_20260703"]["selection_status"], "source_exhausted_not_stated")

    def test_completed_closure_remains_preserved_after_follow_up_packages(self):
        state = payload(ROOT / "project/state.json")
        self.assertGreaterEqual(state["reference_delivery"]["pull_request"], 449)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertTrue(state["current_package"]["package_id"])
        self.assertTrue(state["next_package"]["package_id"])
        self.assertEqual(state["baseline"]["configuration_values"], 3567)
        self.assertGreaterEqual(state["baseline"]["availability_records"], 5906)


if __name__ == "__main__":
    unittest.main()
