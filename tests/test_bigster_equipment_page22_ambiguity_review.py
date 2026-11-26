from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/bigster_equipment_page22_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("bigster_equipment_page22_review", PATH)
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
        self.assertEqual((package["package_id"], package["candidate_count"]), ("residual_gap_009", 7))

    def test_03_package_evidence_totals(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["evidence_signature_count"], package["evidence_record_count"]), (18, 126))

    def test_04_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.BigsterEquipmentPage22ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_05_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.BigsterEquipmentPage22ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_06_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.BigsterEquipmentPage22ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.availability_signature("manual_air_conditioning", "optional")])

    def test_07_manifest(self):
        self.assertEqual(len(review.DECISIONS), 7)
        self.assertEqual({item["decision"] for item in review.DECISIONS}, {"covered", "partially_covered"})

    def test_08_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.BigsterEquipmentPage22ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_09_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.BigsterEquipmentPage22ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.by_line = {item["line_start"]: item for item in cls.payload["decisions"]}

    def attrs(self, line):
        return {item["signature"]["attribute_code"] for item in self.by_line[line]["selected_evidence_signatures"]}

    def statuses(self, line):
        return {item["signature"]["availability_status"] for item in self.by_line[line]["selected_evidence_signatures"]}

    def test_10_source_receipt(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)
        self.assertEqual(self.payload["source_receipt"]["page"], 22)

    def test_11_summary(self):
        summary = self.payload["summary"]
        self.assertEqual(summary["candidate_count"], 7)
        self.assertEqual(summary["decision_counts"], {"covered": 3, "partially_covered": 4})
        self.assertEqual((summary["selected_evidence_signature_count"], summary["selected_evidence_record_count"]), (18, 126))

    def test_12_all_candidates_exact_once(self):
        ids = [item["candidate_id"] for item in self.payload["decisions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {item["candidate_id"] for item in review.DECISIONS})

    def test_13_complete_rows_covered(self):
        self.assertEqual({line for line, item in self.by_line.items() if item["authored_decision"] == "covered"}, {22, 29, 48})

    def test_14_manual_air_conditioning(self):
        self.assertEqual(self.attrs(22), {"manual_air_conditioning"})
        self.assertEqual(self.statuses(22), {"not_available", "standard"})

    def test_15_automatic_climate_visual_row(self):
        self.assertEqual(self.attrs(24), {"automatic_climate_control", "dual_zone_climate_control", "rear_air_vents"})
        self.assertEqual(self.statuses(24), {"not_available", "standard"})

    def test_16_folding_mirrors(self):
        self.assertEqual(self.attrs(29), {"side_mirrors_folding"})
        self.assertEqual(self.statuses(29), {"not_available", "standard"})

    def test_17_console_variant(self):
        self.assertEqual(self.attrs(40), {"front_centre_armrest"})
        self.assertEqual(self.statuses(40), {"not_available", "standard"})

    def test_18_wireless_charging(self):
        self.assertEqual(self.attrs(48), {"wireless_charging"})
        self.assertEqual(self.statuses(48), {"not_available", "standard"})

    def test_19_heated_steering_wheel(self):
        self.assertEqual(self.attrs(97), {"heated_steering_wheel"})
        self.assertEqual(self.statuses(97), {"not_available", "optional"})

    def test_20_heated_windscreen(self):
        self.assertEqual(self.attrs(100), {"heated_windscreen"})
        self.assertEqual(self.statuses(100), {"not_available", "optional"})

    def test_21_trim_keys(self):
        for item in self.payload["decisions"]:
            self.assertEqual(tuple(item["source_availability"]), review.TRIMS)

    def test_22_no_rejections(self):
        self.assertEqual(self.payload["summary"]["rejected_attached_signature_count"], 0)
        self.assertEqual(self.payload["summary"]["rejected_attached_record_count"], 0)

    def test_23_outputs(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_24_policy_and_next(self):
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertTrue(self.payload["semantic_boundaries"]["automatic_climate_dual_zone_and_rear_vents_remain_distinct"])
        self.assertEqual(self.payload["next_package"]["name"], "Jogger Equipment Page 20 Ambiguity Review")

    def test_25_markdown_boundary(self):
        self.assertIn("Winter-package components do not inherit standard status", self.markdown)
        self.assertIn("Jogger Equipment Page 20 Ambiguity Review", self.markdown)


if __name__ == "__main__":
    unittest.main()
