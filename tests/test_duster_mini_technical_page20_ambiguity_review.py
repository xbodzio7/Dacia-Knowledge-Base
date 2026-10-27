from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/duster_mini_technical_page20_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("duster_mini_page20_review", PATH)
assert SPEC and SPEC.loader
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prioritization = json.loads((ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8"))

    def test_signature(self):
        self.assertEqual(review.signature("boot_capacity", "453"), {"attribute_code": "boot_capacity", "value": "453", "fuel_type_code": "", "gear_number": ""})

    def test_range_signature(self):
        self.assertEqual(review.range_signature("payload", "455", "487"), {"attribute_code": "payload", "minimum_value": "455", "maximum_value": "487", "lower_inclusive": "true", "upper_inclusive": "true", "fuel_type_code": ""})

    def test_fact(self):
        self.assertEqual(review.fact("boot_capacity", ["1545"], "x"), {"attribute_code": "boot_capacity", "source_values": ["1545"], "reason": "x"})

    def test_package(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["package_id"], package["candidate_count"], package["evidence_signature_count"]), ("residual_gap_003", 5, 26))

    def test_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.DusterMiniPage20ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.DusterMiniPage20ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.DusterMiniPage20ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.signature("boot_capacity", "453")])

    def test_manifest(self):
        ids = [item["candidate_id"] for item in review.DECISIONS]
        self.assertEqual(len(ids), 5)
        self.assertEqual(len(set(ids)), 5)

    def test_statuses(self):
        self.assertTrue({item["decision"] for item in review.DECISIONS} <= review.DECISION_STATUSES)

    def test_restricted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.DusterMiniPage20ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.DusterMiniPage20ReviewError, "differs"):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(ROOT, review.DEFAULT_PRIORITIZATION)
        cls.by_line = {item["line_start"]: item for item in cls.payload["decisions"]}

    def test_source_receipt(self):
        self.assertEqual(cls := self.payload["source_receipt"], {"source_code": review.SOURCE_CODE, "file_path": review.SOURCE_PATH.as_posix(), "sha256": review.SOURCE_SHA256, "page": 20, "review_basis": "authored visual review of the archived page-20 technical table"})

    def test_summary(self):
        self.assertEqual(self.payload["summary"], {"candidate_count": 5, "decision_counts": {"covered_by_selected_evidence": 3, "partially_covered": 2}, "selected_evidence_signature_count": 9, "selected_evidence_record_count": 34, "candidates_with_selected_evidence": 5, "candidates_without_selected_evidence": 0})

    def test_unique(self):
        self.assertEqual(len({item["candidate_id"] for item in self.payload["decisions"]}), 5)

    def test_boundaries(self):
        for decision in self.payload["decisions"]:
            for evidence in decision["selected_evidence_signatures"]:
                for record in evidence["records"]:
                    self.assertEqual((record["source_code"], record["source_page"]), (review.SOURCE_CODE, 20))

    def test_steering(self):
        self.assertEqual([item["signature"] for item in self.by_line[52]["selected_evidence_signatures"]], [review.signature("steering_type", "Elektryczne wspomaganie układu kierowniczego")])

    def test_kerb_mass(self):
        self.assertEqual([item["signature"]["value"] for item in self.by_line[87]["selected_evidence_signatures"]], ["1350", "1376"])

    def test_payload(self):
        self.assertEqual([(item["signature"]["minimum_value"], item["signature"]["maximum_value"]) for item in self.by_line[95]["selected_evidence_signatures"]], [("455", "487"), ("454", "528")])

    def test_upright_cargo(self):
        self.assertEqual([item["signature"]["value"] for item in self.by_line[103]["selected_evidence_signatures"]], ["453", "517", "474"])
        self.assertEqual(self.by_line[103]["authored_decision"], "partially_covered")

    def test_folded_cargo(self):
        self.assertEqual([item["signature"]["value"] for item in self.by_line[106]["selected_evidence_signatures"]], ["1566"])
        self.assertEqual(self.by_line[106]["source_facts"][0]["source_values"], ["1545", "1609"])

    def test_hybrid_page_boundary(self):
        facts = self.by_line[103]["source_facts"]
        self.assertEqual(facts[0]["source_values"], ["430", "349", "1415"])
        selected = {item["signature"]["value"] for line in (103, 106) for item in self.by_line[line]["selected_evidence_signatures"]}
        self.assertTrue({"430", "349", "1415"}.isdisjoint(selected))

    def test_policy(self):
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertFalse(self.payload["policy"]["approved_import_spec_generation"])
        self.assertTrue(self.payload["policy"]["following_page_evidence_not_silently_substituted"])

    def test_next_package(self):
        self.assertEqual(self.payload["next_package"]["name"], "Sandero Technical Page 17 Ambiguity Review")

    def test_markdown(self):
        self.assertEqual(self.markdown, review.render_markdown(copy.deepcopy(self.payload)))
        self.assertIn("Partially covered | 2", self.markdown)

    def test_committed_outputs(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_decision_partition(self):
        self.assertEqual({line: self.by_line[line]["authored_decision"] for line in self.by_line}, {52: "covered_by_selected_evidence", 87: "covered_by_selected_evidence", 95: "covered_by_selected_evidence", 103: "partially_covered", 106: "partially_covered"})


if __name__ == "__main__":
    unittest.main()
