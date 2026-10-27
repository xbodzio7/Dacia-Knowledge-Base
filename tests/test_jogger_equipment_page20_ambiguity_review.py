from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/jogger_equipment_page20_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("jogger_equipment_page20_review", PATH)
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
        self.assertEqual((package["package_id"], package["candidate_count"]), ("residual_gap_010", 5))

    def test_03_package_evidence_totals(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual((package["evidence_signature_count"], package["evidence_record_count"]), (10, 198))

    def test_04_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.JoggerEquipmentPage20ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_05_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.JoggerEquipmentPage20ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_06_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.JoggerEquipmentPage20ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.availability_signature("electronic_stability_control", "optional")])

    def test_07_manifest(self):
        self.assertEqual(len(review.DECISIONS), 5)
        self.assertEqual({item["decision"] for item in review.DECISIONS}, {"partially_covered", "context_only_non_import", "deferred_source_conflict"})

    def test_08_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.JoggerEquipmentPage20ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_09_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.JoggerEquipmentPage20ReviewError, "differs"):
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
        self.assertEqual(self.payload["source_receipt"]["page"], 20)

    def test_11_summary(self):
        summary = self.payload["summary"]
        self.assertEqual(summary["candidate_count"], 5)
        self.assertEqual(summary["decision_counts"], {"covered": 0, "partially_covered": 3, "context_only_non_import": 1, "deferred_source_conflict": 1})
        self.assertEqual((summary["selected_evidence_signature_count"], summary["selected_evidence_record_count"]), (8, 154))

    def test_12_all_candidates_exact_once(self):
        ids = [item["candidate_id"] for item in self.payload["decisions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {item["candidate_id"] for item in review.DECISIONS})

    def test_13_decision_distribution(self):
        self.assertEqual({line: item["authored_decision"] for line, item in self.by_line.items()}, {104: "partially_covered", 125: "partially_covered", 126: "partially_covered", 127: "context_only_non_import", 138: "deferred_source_conflict"})

    def test_14_esc_hsa_row(self):
        self.assertEqual(self.attrs(104), {"electronic_stability_control", "hill_start_assist"})

    def test_15_airbag_first_fragment(self):
        self.assertEqual(self.attrs(125), {"driver_front_airbag", "passenger_front_airbag"})

    def test_16_airbag_marker_fragment(self):
        self.assertEqual(self.attrs(126), {"driver_front_airbag", "passenger_front_airbag"})

    def test_17_deactivation_context_only(self):
        self.assertEqual(self.by_line[127]["selected_evidence_signature_count"], 0)
        self.assertIn("no attached signature represents deactivation", self.by_line[127]["rationale"])

    def test_18_camera_conflict_decision(self):
        self.assertEqual(self.by_line[138]["authored_decision"], "deferred_source_conflict")
        self.assertEqual(self.statuses(138), {"not_available", "standard"})

    def test_19_camera_source_trim_states(self):
        self.assertEqual(self.by_line[138]["source_availability"], {"essential": "not_available", "expression": "standard", "extreme": "standard", "journey": "not_available"})

    def test_20_camera_standard_contains_journey_records(self):
        standard = next(item for item in self.by_line[138]["selected_evidence_signatures"] if item["signature"]["availability_status"] == "standard")
        self.assertTrue(any(record["configuration_code"].startswith("jogger_journey_") for record in standard["records"]))

    def test_21_trim_keys(self):
        for item in self.payload["decisions"]:
            self.assertEqual(tuple(item["source_availability"]), review.TRIMS)

    def test_22_rejection_totals(self):
        self.assertEqual(self.payload["summary"]["rejected_attached_signature_count"], 2)
        self.assertEqual(self.payload["summary"]["rejected_attached_record_count"], 44)

    def test_23_outputs(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_24_policy_and_next(self):
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertTrue(self.payload["semantic_boundaries"]["brochure_and_later_price_list_camera_states_remain_in_conflict"])
        self.assertEqual(self.payload["next_package"]["name"], "Bigster Equipment Page 21 Ambiguity Review")

    def test_25_markdown_boundary(self):
        self.assertIn("passenger-airbag deactivation clause does not inherit airbag-presence evidence", self.markdown)
        self.assertIn("2025-12 brochure and 2026-04 price-list camera states remain an explicit unresolved conflict", self.markdown)


if __name__ == "__main__":
    unittest.main()
