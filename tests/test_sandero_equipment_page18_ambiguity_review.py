from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/sandero_equipment_page18_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("sandero_equipment_page18_review", PATH)
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
        self.assertEqual((package["package_id"], package["candidate_count"]), ("residual_gap_013", 1))

    def test_03_package_evidence_totals(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["evidence_signature_count"], package["evidence_record_count"]), (2, 4))

    def test_04_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.SanderoEquipmentPage18ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_05_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.SanderoEquipmentPage18ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_06_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.SanderoEquipmentPage18ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.availability_signature("rear_view_camera", "package")])

    def test_07_manifest_length(self):
        self.assertEqual(len(review.DECISIONS), 1)

    def test_08_manifest_decision(self):
        self.assertEqual(review.DECISIONS[0]["decision"], "deferred_source_conflict")

    def test_09_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            with self.assertRaisesRegex(review.SanderoEquipmentPage18ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_10_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.SanderoEquipmentPage18ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.decision = cls.payload["decisions"][0]

    def test_11_source_receipt_hash(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)

    def test_12_source_receipt_page(self):
        self.assertEqual(self.payload["source_receipt"]["page"], 18)

    def test_13_summary_count(self):
        self.assertEqual(self.payload["summary"]["candidate_count"], 1)

    def test_14_summary_decisions(self):
        self.assertEqual(self.payload["summary"]["decision_counts"], {"deferred_source_conflict": 1})

    def test_15_summary_evidence(self):
        self.assertEqual((self.payload["summary"]["selected_evidence_signature_count"], self.payload["summary"]["selected_evidence_record_count"]), (2, 4))

    def test_16_candidate_exact(self):
        self.assertEqual(self.decision["candidate_id"], review.DECISIONS[0]["candidate_id"])
        self.assertEqual(self.decision["exact_text"], review.DECISIONS[0]["exact_text"])

    def test_17_attribute(self):
        self.assertEqual({item["signature"]["attribute_code"] for item in self.decision["selected_evidence_signatures"]}, {"rear_view_camera"})

    def test_18_statuses(self):
        self.assertEqual({item["signature"]["availability_status"] for item in self.decision["selected_evidence_signatures"]}, {"optional", "standard"})

    def test_19_source_availability(self):
        self.assertEqual(self.decision["source_availability"], {"essential": "not_available", "expression": "optional", "journey": "standard"})

    def test_20_trim_order(self):
        self.assertEqual(tuple(self.decision["source_availability"]), review.TRIMS)

    def test_21_no_rejections(self):
        self.assertEqual(self.payload["summary"]["rejected_attached_signature_count"], 0)
        self.assertEqual(self.payload["summary"]["rejected_attached_record_count"], 0)

    def test_22_json_output(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))

    def test_23_markdown_output(self):
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_24_policy_and_next(self):
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertTrue(self.payload["semantic_boundaries"]["brochure_and_price_list_versus_later_official_web_expression_states_remain_in_conflict"])
        self.assertEqual(self.payload["next_package"]["name"], "Sandero Equipment Page 19 Ambiguity Review")

    def test_25_markdown_boundary(self):
        self.assertIn("Expression optional marker is not overwritten by later official-web standard records", self.markdown)
        self.assertIn("Sandero Equipment Page 19 Ambiguity Review", self.markdown)


if __name__ == "__main__":
    unittest.main()
