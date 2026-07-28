from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/duster_mini_equipment_page22_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("duster_mini_equipment_page22_review", PATH)
assert SPEC and SPEC.loader
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prioritization = json.loads((ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8"))

    def test_01_signature(self):
        self.assertEqual(review.availability_signature("x", "standard"), {"attribute_code": "x", "availability_status": "standard"})

    def test_02_package_identity(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["package_id"], package["candidate_count"]), ("residual_gap_008", 11))

    def test_03_package_evidence_totals(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["evidence_signature_count"], package["evidence_record_count"]), (27, 551))

    def test_04_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.DusterMiniEquipmentPage22ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_05_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.DusterMiniEquipmentPage22ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_06_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.DusterMiniEquipmentPage22ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.availability_signature("automatic_headlights", "optional")])

    def test_07_manifest(self):
        self.assertEqual(len(review.DECISIONS), 11)
        self.assertEqual({item["decision"] for item in review.DECISIONS}, {"covered", "partially_covered"})

    def test_08_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.DusterMiniEquipmentPage22ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_09_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.DusterMiniEquipmentPage22ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.by_line = {item["line_start"]: item for item in cls.payload["decisions"]}

    def test_10_source_receipt(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)
        self.assertEqual(self.payload["source_receipt"]["page"], 22)

    def test_11_summary(self):
        summary = self.payload["summary"]
        self.assertEqual(summary["candidate_count"], 11)
        self.assertEqual(summary["decision_counts"], {"covered": 3, "partially_covered": 8})
        self.assertEqual((summary["selected_evidence_signature_count"], summary["selected_evidence_record_count"]), (23, 524))

    def test_12_all_candidates_exact_once(self):
        ids = [item["candidate_id"] for item in self.payload["decisions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {item["candidate_id"] for item in review.DECISIONS})

    def test_13_complete_rows_covered(self):
        self.assertEqual({line for line, item in self.by_line.items() if item["authored_decision"] == "covered"}, {164, 170, 176})

    def test_14_headlights_reject_rain_sensor(self):
        attrs = {item["signature"]["attribute_code"] for item in self.by_line[15]["selected_evidence_signatures"]}
        self.assertEqual(attrs, {"automatic_headlights"})

    def test_15_esc_hsa_visual_row(self):
        for line in (117, 118):
            attrs = {item["signature"]["attribute_code"] for item in self.by_line[line]["selected_evidence_signatures"]}
            self.assertEqual(attrs, {"electronic_stability_control", "hill_start_assist"})

    def test_16_seat_belt_fragments(self):
        expected = {"driver_seat_belt_height_adjustment", "front_seat_belt_pretensioners", "rear_seat_belt_pretensioners"}
        for line in (120, 121, 122):
            attrs = {item["signature"]["attribute_code"] for item in self.by_line[line]["selected_evidence_signatures"]}
            self.assertEqual(attrs, expected)

    def test_17_instrument_cluster_states(self):
        statuses = {item["signature"]["availability_status"] for item in self.by_line[153]["selected_evidence_signatures"]}
        self.assertEqual(statuses, {"not_available", "standard"})

    def test_18_limiter_and_cruise(self):
        attrs = {item["signature"]["attribute_code"] for item in self.by_line[164]["selected_evidence_signatures"]}
        self.assertEqual(attrs, {"speed_limiter", "cruise_control"})

    def test_19_rear_parking_rejects_front(self):
        attrs = {item["signature"]["attribute_code"] for item in self.by_line[170]["selected_evidence_signatures"]}
        self.assertEqual(attrs, {"rear_parking_sensors"})

    def test_20_front_side_parking_states(self):
        selected = self.by_line[173]["selected_evidence_signatures"]
        self.assertEqual({item["signature"]["availability_status"] for item in selected}, {"not_available", "optional"})
        self.assertNotIn("standard", {item["signature"]["availability_status"] for item in selected})

    def test_21_camera_states(self):
        statuses = {item["signature"]["availability_status"] for item in self.by_line[176]["selected_evidence_signatures"]}
        self.assertEqual(statuses, {"not_available", "standard"})

    def test_22_trim_keys(self):
        for item in self.payload["decisions"]:
            self.assertEqual(tuple(item["source_availability"]), review.TRIMS)

    def test_23_rejection_totals(self):
        self.assertEqual(self.payload["summary"]["rejected_attached_signature_count"], 4)
        self.assertEqual(self.payload["summary"]["rejected_attached_record_count"], 27)

    def test_24_outputs_policy_and_next(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertTrue(self.payload["semantic_boundaries"]["automatic_headlights_remain_distinct_from_rain_sensing_wipers"])
        self.assertEqual(self.payload["next_package"]["name"], "Bigster Equipment Page 22 Ambiguity Review")

    def test_25_markdown_boundary(self):
        self.assertIn("option and package markers do not inherit standard status", self.markdown)
        self.assertIn("Bigster Equipment Page 22 Ambiguity Review", self.markdown)


if __name__ == "__main__":
    unittest.main()
