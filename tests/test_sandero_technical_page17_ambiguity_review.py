from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/sandero_technical_page17_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("sandero_page17_review", PATH)
assert SPEC and SPEC.loader
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prioritization = json.loads((ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8"))

    def test_signature_default_context(self):
        self.assertEqual(
            review.signature("maximum_kerb_weight", "1209"),
            {"attribute_code": "maximum_kerb_weight", "value": "1209", "fuel_type_code": "", "gear_number": ""},
        )

    def test_signature_fuel_context(self):
        self.assertEqual(
            review.signature("engine_power", "90", "lpg"),
            {"attribute_code": "engine_power", "value": "90", "fuel_type_code": "lpg", "gear_number": ""},
        )

    def test_fact(self):
        self.assertEqual(
            review.fact("engine_power", ["74"], "x"),
            {"attribute_code": "engine_power", "source_values": ["74"], "reason": "x"},
        )

    def test_package(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(
            (package["package_id"], package["candidate_count"], package["evidence_signature_count"]),
            ("residual_gap_004", 5, 10),
        )

    def test_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(review.SanderoPage17ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.SanderoPage17ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_missing_signature(self):
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.SanderoPage17ReviewError, "not attached"):
            review.selected_signatures(candidate, [review.signature("engine_power", "1")])

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
            with self.assertRaisesRegex(review.SanderoPage17ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(review.SanderoPage17ReviewError, "differs"):
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
                "candidate_count": 5,
                "decision_counts": {"covered_by_selected_evidence": 0, "partially_covered": 5},
                "selected_evidence_signature_count": 8,
                "selected_evidence_record_count": 16,
                "candidates_with_selected_evidence": 5,
                "candidates_without_selected_evidence": 0,
            },
        )

    def test_unique(self):
        self.assertEqual(len({item["candidate_id"] for item in self.payload["decisions"]}), 5)

    def test_boundaries(self):
        for decision in self.payload["decisions"]:
            for evidence in decision["selected_evidence_signatures"]:
                for record in evidence["records"]:
                    self.assertEqual((record["source_code"], record["source_page"]), (review.SOURCE_CODE, 17))

    def test_power(self):
        selected = [item["signature"] for item in self.by_line[15]["selected_evidence_signatures"]]
        self.assertEqual(selected, [review.signature("engine_power", "90", "lpg"), review.signature("engine_power", "84", "petrol")])
        self.assertEqual(self.by_line[15]["source_facts"][0]["source_values"], ["74", "90", "84"])

    def test_torque(self):
        selected = [item["signature"] for item in self.by_line[19]["selected_evidence_signatures"]]
        self.assertEqual(selected, [review.signature("engine_torque", "197", "lpg"), review.signature("engine_torque", "190", "petrol")])
        self.assertEqual(self.by_line[19]["source_facts"][0]["source_values"], ["200", "197", "190"])

    def test_kerb_mass(self):
        self.assertEqual(
            [item["signature"]["value"] for item in self.by_line[82]["selected_evidence_signatures"]],
            ["1209", "1232"],
        )
        self.assertEqual(self.by_line[82]["source_facts"][0]["source_values"], ["1132"])

    def test_gross_vehicle_row(self):
        self.assertEqual(
            [item["signature"] for item in self.by_line[84]["selected_evidence_signatures"]],
            [review.signature("gross_vehicle_weight", "1665")],
        )

    def test_gross_train_row(self):
        self.assertEqual(
            [item["signature"] for item in self.by_line[87]["selected_evidence_signatures"]],
            [review.signature("gross_train_weight", "2765")],
        )

    def test_cross_attribute_signatures_are_rejected(self):
        vehicle_attributes = {item["signature"]["attribute_code"] for item in self.by_line[84]["selected_evidence_signatures"]}
        train_attributes = {item["signature"]["attribute_code"] for item in self.by_line[87]["selected_evidence_signatures"]}
        self.assertEqual(vehicle_attributes, {"gross_vehicle_weight"})
        self.assertEqual(train_attributes, {"gross_train_weight"})

    def test_policy(self):
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertFalse(self.payload["policy"]["approved_import_spec_generation"])
        self.assertTrue(self.payload["policy"]["cross_attribute_evidence_not_silently_substituted"])
        self.assertTrue(self.payload["policy"]["unattached_powertrain_values_not_inferred"])

    def test_next_package(self):
        self.assertEqual(self.payload["next_package"]["name"], "Sandero Stepway Technical Page 17 Ambiguity Review")

    def test_markdown(self):
        self.assertEqual(self.markdown, review.render_markdown(copy.deepcopy(self.payload)))
        self.assertIn("Partially covered | 5", self.markdown)
        self.assertIn("automatic evidence is not projected", self.markdown)

    def test_committed_outputs(self):
        self.assertEqual((ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"), review.canonical_json(self.payload))
        self.assertEqual((ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"), self.markdown)

    def test_decision_partition(self):
        self.assertEqual(
            {line: self.by_line[line]["authored_decision"] for line in self.by_line},
            {15: "partially_covered", 19: "partially_covered", 82: "partially_covered", 84: "partially_covered", 87: "partially_covered"},
        )


if __name__ == "__main__":
    unittest.main()
