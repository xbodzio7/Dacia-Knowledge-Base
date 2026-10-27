from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/duster_mini_equipment_page23_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("duster_mini_equipment_page23_review", PATH)
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
        self.assertEqual((package["package_id"], package["candidate_count"]), ("residual_gap_007", 26))

    def test_03_package_evidence_totals(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["evidence_signature_count"], package["evidence_record_count"]), (61, 623))

    def test_04_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.DusterMiniEquipmentPage23ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_05_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.DusterMiniEquipmentPage23ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_06_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.DusterMiniEquipmentPage23ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.availability_signature("fog_lights", "optional")])

    def test_07_manifest(self):
        self.assertEqual(len(review.DECISIONS), 26)
        self.assertEqual({item["decision"] for item in review.DECISIONS}, {"covered", "partially_covered"})

    def test_08_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.DusterMiniEquipmentPage23ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_09_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.DusterMiniEquipmentPage23ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.by_line = {item["line_start"]: item for item in cls.payload["decisions"]}

    def test_10_source_receipt(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)
        self.assertEqual(self.payload["source_receipt"]["page"], 23)

    def test_11_summary(self):
        summary = self.payload["summary"]
        self.assertEqual(summary["candidate_count"], 26)
        self.assertEqual(summary["decision_counts"], {"covered": 6, "partially_covered": 20})
        self.assertEqual((summary["selected_evidence_signature_count"], summary["selected_evidence_record_count"]), (43, 518))

    def test_12_all_candidates_exact_once(self):
        ids = [item["candidate_id"] for item in self.payload["decisions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {item["candidate_id"] for item in review.DECISIONS})

    def test_13_complete_rows_covered(self):
        self.assertEqual({line for line, item in self.by_line.items() if item["authored_decision"] == "covered"}, {5, 15, 17, 28, 30, 35})

    def test_14_front_windows_reject_one_touch(self):
        attrs = {item["signature"]["attribute_code"] for item in self.by_line[28]["selected_evidence_signatures"]}
        self.assertEqual(attrs, {"front_windows_power"})

    def test_15_rear_windows_preserve_states(self):
        signatures = {tuple(item["signature"].values()) for item in self.by_line[30]["selected_evidence_signatures"]}
        self.assertEqual(signatures, {("rear_windows_power", "not_available"), ("rear_windows_power", "standard")})

    def test_16_driver_seat_rejects_other_seats(self):
        attrs = {item["signature"]["attribute_code"] for item in self.by_line[35]["selected_evidence_signatures"]}
        self.assertEqual(attrs, {"driver_seat_height_adjustment"})

    def test_17_passenger_seat_row(self):
        attrs = {item["signature"]["attribute_code"] for item in self.by_line[42]["selected_evidence_signatures"]}
        self.assertEqual(attrs, {"passenger_seat_adjustment", "passenger_seat_height_adjustment"})

    def test_18_wireless_charging_states(self):
        statuses = {item["signature"]["availability_status"] for item in self.by_line[62]["selected_evidence_signatures"]}
        self.assertEqual(statuses, {"not_available", "optional", "standard"})

    def test_19_media_rows(self):
        self.assertEqual({item["signature"]["attribute_code"] for item in self.by_line[66]["selected_evidence_signatures"]}, {"media_control_system"})
        self.assertEqual({item["signature"]["attribute_code"] for item in self.by_line[73]["selected_evidence_signatures"]}, {"media_display_system"})

    def test_20_connected_services_fragments(self):
        for line in (92, 94, 95):
            self.assertEqual({item["signature"]["attribute_code"] for item in self.by_line[line]["selected_evidence_signatures"]}, {"connected_services"})

    def test_21_parking_package_optional_only(self):
        selected = self.by_line[107]["selected_evidence_signatures"]
        self.assertEqual([item["signature"] for item in selected], [review.availability_signature("front_parking_sensors", "optional")])

    def test_22_winter_packages_optional_only(self):
        for line in (112, 118):
            self.assertEqual([item["signature"]["availability_status"] for item in self.by_line[line]["selected_evidence_signatures"]], ["optional"])
        for line in (115, 123):
            self.assertEqual([item["signature"] for item in self.by_line[line]["selected_evidence_signatures"]], [review.availability_signature("heated_windscreen", "optional")])

    def test_23_package_passenger_seat_fragments(self):
        for line in (122, 127):
            self.assertEqual([item["signature"] for item in self.by_line[line]["selected_evidence_signatures"]], [review.availability_signature("passenger_seat_adjustment", "optional")])

    def test_24_adaptive_cruise_only(self):
        selected = self.by_line[142]["selected_evidence_signatures"]
        self.assertEqual([item["signature"] for item in selected], [review.availability_signature("adaptive_cruise_control", "optional")])
        self.assertEqual(selected[0]["record_count"], 1)

    def test_25_outputs_policy_and_next(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertTrue(self.payload["semantic_boundaries"]["bullet_option_and_dash_symbols_remain_distinct"])
        self.assertEqual(self.payload["next_package"]["name"], "Duster Mini Equipment Page 22 Ambiguity Review")


if __name__ == "__main__":
    unittest.main()
