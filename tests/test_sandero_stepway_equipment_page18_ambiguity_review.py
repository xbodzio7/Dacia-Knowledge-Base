from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/sandero_stepway_equipment_page18_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("sandero_stepway_equipment_page18_review", PATH)
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
        self.assertEqual((package["package_id"], package["candidate_count"]), ("residual_gap_015", 1))

    def test_03_package_evidence_totals(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["evidence_signature_count"], package["evidence_record_count"]), (2, 3))

    def test_04_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.SanderoStepwayEquipmentPage18ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_05_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.SanderoStepwayEquipmentPage18ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_06_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.SanderoStepwayEquipmentPage18ReviewError, "not attached"):
            review.partition_signatures(candidate, [review.availability_signature("roof_rails", "optional")], {})

    def test_07_missing_rejection_reason(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.SanderoStepwayEquipmentPage18ReviewError, "reason assignment"):
            review.partition_signatures(candidate, [review.availability_signature("roof_rails", "standard")], {})

    def test_08_manifest_decision(self):
        self.assertEqual((len(review.DECISIONS), review.DECISIONS[0]["decision"]), (1, "covered"))

    def test_09_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            with self.assertRaisesRegex(review.SanderoStepwayEquipmentPage18ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_10_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.SanderoStepwayEquipmentPage18ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.decision = cls.payload["decisions"][0]
        cls.rejected = cls.decision["rejected_attached_signatures"][0]

    def test_11_source_receipt_hash(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)

    def test_12_source_receipt_page(self):
        self.assertEqual(self.payload["source_receipt"]["page"], 18)

    def test_13_summary_decision(self):
        self.assertEqual(self.payload["summary"]["decision_counts"], {"covered": 1})

    def test_14_selected_evidence_totals(self):
        self.assertEqual((self.payload["summary"]["selected_evidence_signature_count"], self.payload["summary"]["selected_evidence_record_count"]), (1, 1))

    def test_15_rejected_evidence_totals(self):
        self.assertEqual((self.payload["summary"]["rejected_attached_signature_count"], self.payload["summary"]["rejected_attached_record_count"]), (1, 2))

    def test_16_candidate_exact(self):
        self.assertEqual(self.decision["candidate_id"], review.DECISIONS[0]["candidate_id"])
        self.assertEqual(self.decision["exact_text"], review.DECISIONS[0]["exact_text"])

    def test_17_selected_attribute(self):
        selected = self.decision["selected_evidence_signatures"][0]["signature"]
        self.assertEqual(selected, {"attribute_code": "roof_rails", "availability_status": "standard"})

    def test_18_rejected_attribute(self):
        self.assertEqual(self.rejected["signature"], {"attribute_code": "modular_roof_rails", "availability_status": "standard"})
        self.assertEqual(self.rejected["record_count"], 2)

    def test_19_rejection_reason(self):
        self.assertIn("immediately following", self.rejected["rejection_reason"])
        self.assertIn("must not be substituted", self.rejected["rejection_reason"])

    def test_20_source_availability(self):
        self.assertEqual(self.decision["source_availability"], {"essential": "standard", "expression": "not_available", "extreme": "not_available"})
        self.assertEqual(tuple(self.decision["source_availability"]), review.TRIMS)

    def test_21_adjacent_row(self):
        self.assertEqual(self.decision["adjacent_row_context"]["label"], "Modułowe relingi dachowe (szare Megalith)")
        self.assertEqual({key: value for key, value in self.decision["adjacent_row_context"].items() if key != "label"}, {"essential": "not_available", "expression": "standard", "extreme": "standard"})

    def test_22_json_output(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))

    def test_23_markdown_output(self):
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_24_policy_and_next(self):
        self.assertTrue(self.payload["policy"]["rejected_evidence_preserved_with_reason"])
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertEqual(self.payload["next_package"]["name"], "Bigster Technical Page 20 Unresolved Review — Chunk 1")

    def test_25_markdown_boundary(self):
        self.assertIn("Rejected attached evidence", self.markdown)
        self.assertIn("`roof_rails` and `modular_roof_rails` remain distinct attributes", self.markdown)
        self.assertIn("Bigster Technical Page 20 Unresolved Review", self.markdown)


if __name__ == "__main__":
    unittest.main()
