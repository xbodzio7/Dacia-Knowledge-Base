from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/sandero_stepway_technical_page17_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("sandero_stepway_page17_review", PATH)
assert SPEC and SPEC.loader
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prioritization = json.loads((ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8"))

    def test_signature_default_context(self):
        self.assertEqual(
            review.signature("maximum_kerb_weight", "1225"),
            {"attribute_code": "maximum_kerb_weight", "value": "1225", "fuel_type_code": "", "gear_number": ""},
        )

    def test_signature_fuel_context(self):
        self.assertEqual(
            review.signature("turning_circle_between_kerbs", "10.64", "petrol"),
            {"attribute_code": "turning_circle_between_kerbs", "value": "10.64", "fuel_type_code": "petrol", "gear_number": ""},
        )

    def test_fact(self):
        self.assertEqual(
            review.fact("minimum_kerb_weight", ["1095"], "x"),
            {"attribute_code": "minimum_kerb_weight", "source_values": ["1095"], "reason": "x"},
        )

    def test_package(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(
            (package["package_id"], package["candidate_count"], package["evidence_signature_count"]),
            ("residual_gap_005", 4, 12),
        )

    def test_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.SanderoStepwayPage17ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.SanderoStepwayPage17ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.SanderoStepwayPage17ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.signature("turning_circle_between_kerbs", "1")])

    def test_manifest(self):
        ids = [item["candidate_id"] for item in review.DECISIONS]
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(set(ids)), 4)

    def test_statuses(self):
        self.assertEqual(
            {item["decision"] for item in review.DECISIONS},
            {"partially_covered", "unresolved_signature_mismatch"},
        )

    def test_restricted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.SanderoStepwayPage17ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.SanderoStepwayPage17ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.by_line = {item["line_start"]: item for item in cls.payload["decisions"]}

    def test_source_receipt(self):
        self.assertEqual(
            self.payload["source_receipt"],
            {
                "source_code": review.SOURCE_CODE,
                "file_path": review.SOURCE_PATH.as_posix(),
                "sha256": review.SOURCE_SHA256,
                "page": 17,
                "review_basis": "authored visual review of the archived page-17 technical table",
            },
        )

    def test_summary(self):
        self.assertEqual(
            self.payload["summary"],
            {
                "candidate_count": 4,
                "decision_counts": {"partially_covered": 3, "unresolved_signature_mismatch": 1},
                "selected_evidence_signature_count": 5,
                "selected_evidence_record_count": 15,
                "candidates_with_selected_evidence": 3,
                "candidates_without_selected_evidence": 1,
            },
        )

    def test_boundaries(self):
        self.assertEqual(len({item["candidate_id"] for item in self.payload["decisions"]}), 4)
        for decision in self.payload["decisions"]:
            for evidence in decision["selected_evidence_signatures"]:
                for record in evidence["records"]:
                    self.assertEqual((record["source_code"], record["source_page"]), (review.SOURCE_CODE, 17))

    def test_steering_signature(self):
        selected = [item["signature"] for item in self.by_line[42]["selected_evidence_signatures"]]
        self.assertEqual(selected, [review.signature("turning_circle_between_kerbs", "10.64")])

    def test_steering_rejects_other_attributes(self):
        attributes = {item["signature"]["attribute_code"] for item in self.by_line[42]["selected_evidence_signatures"]}
        self.assertEqual(attributes, {"turning_circle_between_kerbs"})
        self.assertNotIn("front_suspension", attributes)
        self.assertNotIn("maximum_kerb_weight", attributes)

    def test_minimum_row_signature_mismatch(self):
        decision = self.by_line[80]
        self.assertEqual(decision["authored_decision"], "unresolved_signature_mismatch")
        self.assertEqual(decision["selected_evidence_signatures"], [])

    def test_minimum_row_source_facts(self):
        self.assertEqual(self.by_line[80]["source_facts"][0]["source_values"], ["1095", "1194", "1222"])

    def test_maximum_label(self):
        self.assertEqual(
            [item["signature"]["value"] for item in self.by_line[81]["selected_evidence_signatures"]],
            ["1225", "1249"],
        )

    def test_maximum_continuation(self):
        self.assertEqual(
            [item["signature"]["value"] for item in self.by_line[83]["selected_evidence_signatures"]],
            ["1225", "1249"],
        )

    def test_tce_value_remains_unattached(self):
        self.assertEqual(self.by_line[81]["source_facts"][0]["source_values"], ["1149"])
        self.assertEqual(self.by_line[83]["source_facts"][0]["source_values"], ["1149"])

    def test_policy(self):
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertFalse(self.payload["policy"]["approved_import_spec_generation"])
        self.assertTrue(self.payload["policy"]["cross_row_evidence_not_silently_substituted"])
        self.assertTrue(self.payload["semantic_boundaries"]["review_is_not_import_approval"])

    def test_next_package(self):
        self.assertEqual(self.payload["next_package"]["name"], "Duster Mini Technical Page 21 Ambiguity Review")

    def test_markdown(self):
        self.assertEqual(self.markdown, review.render_markdown(copy.deepcopy(self.payload)))
        self.assertIn("Partially covered | 3", self.markdown)
        self.assertIn("Unresolved signature mismatch | 1", self.markdown)

    def test_committed_outputs(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_decision_partition(self):
        self.assertEqual(
            {line: self.by_line[line]["authored_decision"] for line in self.by_line},
            {42: "partially_covered", 80: "unresolved_signature_mismatch", 81: "partially_covered", 83: "partially_covered"},
        )


if __name__ == "__main__":
    unittest.main()
