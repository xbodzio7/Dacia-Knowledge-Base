from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/duster_mini_technical_page21_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("duster_mini_page21_review", PATH)
assert SPEC and SPEC.loader
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prioritization = json.loads((ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8"))

    def test_signature(self):
        self.assertEqual(
            review.signature("steering_type", "x"),
            {"attribute_code": "steering_type", "value": "x", "fuel_type_code": "", "gear_number": ""},
        )

    def test_fact(self):
        self.assertEqual(review.fact("x", ["y"], "z"), {"attribute_code": "x", "source_values": ["y"], "reason": "z"})

    def test_package(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["package_id"], package["candidate_count"], package["evidence_signature_count"]), ("residual_gap_006", 1, 7))

    def test_record_count(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(package["evidence_record_count"], 21)

    def test_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.DusterMiniPage21ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.DusterMiniPage21ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.DusterMiniPage21ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.signature("steering_type", "wrong")])

    def test_manifest(self):
        self.assertEqual(len(review.DECISIONS), 1)
        self.assertEqual(review.DECISIONS[0]["decision"], "partially_covered")

    def test_restricted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.DusterMiniPage21ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.DusterMiniPage21ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.decision = cls.payload["decisions"][0]

    def test_source_receipt(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)
        self.assertEqual(self.payload["source_receipt"]["page"], 21)

    def test_summary(self):
        self.assertEqual(
            self.payload["summary"],
            {
                "candidate_count": 1,
                "decision_counts": {"partially_covered": 1},
                "selected_evidence_signature_count": 1,
                "selected_evidence_record_count": 3,
                "candidates_with_selected_evidence": 1,
                "candidates_without_selected_evidence": 0,
            },
        )

    def test_candidate_identity(self):
        self.assertEqual(self.decision["candidate_id"], review.DECISIONS[0]["candidate_id"])
        self.assertEqual(self.decision["line_start"], 56)
        self.assertEqual(self.decision["exact_text"], review.DECISIONS[0]["exact_text"])

    def test_selected_signature(self):
        selected = self.decision["selected_evidence_signatures"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["signature"], review.signature("steering_type", "Elektryczne wspomaganie układu kierowniczego"))
        self.assertEqual(selected[0]["record_count"], 3)

    def test_selected_records_are_hybrid155(self):
        for record in self.decision["selected_evidence_signatures"][0]["records"]:
            self.assertIn("hybrid155", record["configuration_code"])
            self.assertEqual((record["source_code"], record["source_page"]), (review.SOURCE_CODE, 21))

    def test_rejected_attributes(self):
        attributes = {item["signature"]["attribute_code"] for item in self.decision["selected_evidence_signatures"]}
        self.assertEqual(attributes, {"steering_type"})
        for code in {"turning_circle_wheel_track", "front_brake_type", "rear_brake_type", "standard_tyre_specification", "maximum_kerb_weight", "payload"}:
            self.assertNotIn(code, attributes)

    def test_hybrid_g_remains_source_fact(self):
        self.assertEqual(self.decision["source_facts"][0]["attribute_code"], "steering_type")
        self.assertIn("Hybrid-G 150 4x4", self.decision["source_facts"][0]["reason"])

    def test_policy(self):
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertFalse(self.payload["policy"]["approved_import_spec_generation"])
        self.assertTrue(self.payload["policy"]["cross_attribute_evidence_not_silently_substituted"])
        self.assertTrue(self.payload["semantic_boundaries"]["turning_circle_is_a_distinct_row"])

    def test_next_package(self):
        self.assertEqual(self.payload["next_package"]["name"], "Duster Mini Equipment Page 23 Ambiguity Review")

    def test_markdown(self):
        self.assertEqual(self.markdown, review.render_markdown(copy.deepcopy(self.payload)))
        self.assertIn("Partially covered | 1", self.markdown)
        self.assertIn("steering-type row", self.markdown)

    def test_committed_outputs(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_no_configuration_projection(self):
        self.assertTrue(self.payload["semantic_boundaries"]["no_configuration_projection_is_created"])

    def test_source_path(self):
        self.assertTrue((ROOT / review.SOURCE_PATH).is_file())

    def test_review_status(self):
        self.assertEqual(self.payload["status"], "complete")
        self.assertEqual(self.decision["authored_decision"], "partially_covered")

    def test_exact_evidence_totals(self):
        self.assertEqual(self.decision["selected_evidence_signature_count"], 1)
        self.assertEqual(self.decision["selected_evidence_record_count"], 3)


if __name__ == "__main__":
    unittest.main()
