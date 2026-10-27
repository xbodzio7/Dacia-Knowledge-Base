from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/bigster_technical_page20_unresolved_review_chunk1.py"
SPEC = importlib.util.spec_from_file_location("bigster_page20_unresolved_chunk1", PATH)
assert SPEC and SPEC.loader
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prioritization = json.loads(
            (ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8")
        )

    def test_01_source_fact_columns(self):
        fact = review.source_fact(
            "x", {column: [column] for column in review.POWERTRAIN_COLUMNS}, "r"
        )
        self.assertEqual(tuple(fact["values_by_powertrain"]), review.POWERTRAIN_COLUMNS)

    def test_02_package_identity(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(
            (package["package_id"], package["candidate_count"]),
            ("residual_gap_016", 40),
        )

    def test_03_chunk_identity(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(
            (package["group_candidate_count"], package["chunk_index"], package["chunk_count"]),
            (69, 1, 2),
        )

    def test_04_zero_evidence_input(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(
            (package["evidence_signature_count"], package["evidence_record_count"]),
            (0, 0),
        )

    def test_05_wrong_kind(self):
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "x"
        with self.assertRaisesRegex(
            review.BigsterPage20UnresolvedChunk1ReviewError, "kind"
        ):
            review.validate_prioritization(payload)

    def test_06_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(
            review.BigsterPage20UnresolvedChunk1ReviewError, "imports"
        ):
            review.validate_prioritization(payload)

    def test_07_candidate_digest(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(
            review.candidate_digest(package["candidates"]),
            review.PACKAGE_CANDIDATE_DIGEST,
        )

    def test_08_partition_complete(self):
        candidates = review.validate_prioritization(self.prioritization)["candidates"]
        partition = review.authored_partition(candidates)
        self.assertEqual(set(partition), set(range(1, 41)))

    def test_09_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            with self.assertRaisesRegex(
                review.BigsterPage20UnresolvedChunk1ReviewError, "restricted"
            ):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_10_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(
                review.BigsterPage20UnresolvedChunk1ReviewError, "differs"
            ):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(
            ROOT, review.DEFAULT_PRIORITIZATION
        )
        cls.by_line = {
            item["line_start"]: item for item in cls.payload["decisions"]
        }

    def test_11_source_receipt(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)
        self.assertEqual(self.payload["source_receipt"]["page"], 20)

    def test_12_summary_counts(self):
        self.assertEqual(
            self.payload["summary"]["decision_counts"],
            {
                "context_only_non_import": 24,
                "unresolved_signature_mismatch": 16,
            },
        )

    def test_13_zero_selected_evidence(self):
        self.assertEqual(
            (
                self.payload["summary"]["selected_evidence_signature_count"],
                self.payload["summary"]["selected_evidence_record_count"],
            ),
            (0, 0),
        )
        self.assertTrue(
            all(
                item["selected_evidence_signatures"] == []
                for item in self.payload["decisions"]
            )
        )

    def test_14_exact_candidate_order(self):
        package = review.validate_prioritization(
            json.loads((ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8"))
        )
        self.assertEqual(
            [item["candidate_id"] for item in self.payload["decisions"]],
            [item["candidate_id"] for item in package["candidates"]],
        )
        self.assertEqual(
            [item["exact_text"] for item in self.payload["decisions"]],
            [item["exact_text"] for item in package["candidates"]],
        )

    def test_15_visual_columns(self):
        layout = self.payload["source_page_layout"]
        self.assertEqual(tuple(layout["powertrain_columns"]), review.POWERTRAIN_COLUMNS)
        self.assertEqual(layout["column_labels"]["hybrid_g_150_4x4"], "HYBRID-G 150 4×4")

    def test_16_propulsion_group(self):
        self.assertEqual(self.by_line[12]["logical_row"], "propulsion")
        self.assertEqual(
            self.by_line[12]["authored_decision"],
            "unresolved_signature_mismatch",
        )
        self.assertEqual(self.by_line[10]["row_role"], "logical_row_fragment")
        fact = self.by_line[12]["source_facts"][0]
        self.assertIn(
            "Elektryczny full hybrid 280 V",
            fact["values_by_powertrain"]["hybrid_155"],
        )

    def test_17_power_and_torque_groups(self):
        power = self.by_line[20]["source_facts"][0]
        torque = self.by_line[24]["source_facts"][0]
        self.assertIn(
            "113 kW (150 KM) – moc łączna",
            power["values_by_powertrain"]["hybrid_g_150_4x4"],
        )
        self.assertIn(
            "205 N.m przy 0–1630 obr./min – elektryczny",
            torque["values_by_powertrain"]["hybrid_155"],
        )

    def test_18_engine_rows(self):
        self.assertEqual(
            self.by_line[31]["source_facts"][0]["values_by_powertrain"]["mild_hybrid_140"],
            ["Wtrysk bezpośredni"],
        )
        self.assertEqual(
            self.by_line[33]["source_facts"][0]["values_by_powertrain"]["hybrid_155"],
            ["1789"],
        )
        self.assertEqual(
            self.by_line[36]["source_facts"][0]["values_by_powertrain"]["hybrid_155"],
            ["4 cylindry", "16 zaworów"],
        )

    def test_19_battery_and_performance(self):
        battery = self.by_line[44]["source_facts"][0]
        self.assertEqual(
            battery["values_by_powertrain"]["hybrid_155"],
            ["Litowo-jonowy", "280 V", "1,4 kWh"],
        )
        self.assertEqual(
            self.by_line[47]["source_facts"][0]["values_by_powertrain"]["mild_hybrid_g_140"],
            ["180"],
        )
        self.assertEqual(
            self.by_line[49]["source_facts"][0]["values_by_powertrain"]["hybrid_g_150_4x4"],
            ["10,4"],
        )

    def test_20_drivetrain_and_gearbox(self):
        drivetrain = self.by_line[53]["source_facts"][0]
        gearbox = self.by_line[56]["source_facts"][0]
        self.assertEqual(
            drivetrain["values_by_powertrain"]["hybrid_g_150_4x4"],
            ["4×4 z tylnym silnikiem elektrycznym"],
        )
        self.assertEqual(
            gearbox["values_by_powertrain"]["hybrid_155"],
            ["Automatyczna", "Multi-mode", "4+2"],
        )

    def test_21_prior_rear_brake_reference(self):
        prior = self.payload["prior_review_reference"]
        self.assertEqual(prior["package_id"], "residual_gap_001")
        self.assertEqual(prior["line_start"], 77)
        self.assertEqual(prior["authored_decision"], "covered_by_selected_evidence")
        self.assertTrue(
            all(
                self.by_line[line]["logical_row"] == "rear_brakes_prior_review"
                for line in (74, 79, 80)
            )
        )

    def test_22_milestone_review(self):
        milestone = self.payload["milestone_review"]
        self.assertEqual(milestone["package_interval"], 5)
        self.assertEqual(len(milestone["packages_reviewed"]), 5)
        self.assertFalse(milestone["durable_architectural_decision_required"])
        self.assertFalse(milestone["separate_review_only_pull_request_required"])

    def test_23_json_output(self):
        self.assertEqual(
            (ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"),
            review.canonical_json(self.payload),
        )

    def test_24_markdown_output(self):
        self.assertEqual(
            (ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"),
            self.markdown,
        )
        self.assertIn("Prior rear-brake decision", self.markdown)
        self.assertIn("Five-package milestone review", self.markdown)

    def test_25_policy_and_next(self):
        self.assertTrue(self.payload["policy"]["zero_attached_evidence_preserved"])
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertEqual(
            self.payload["next_package"]["name"],
            "Bigster Technical Page 20 Unresolved Review — Chunk 2",
        )
        self.assertIn("zero attached evidence signatures", self.markdown)


if __name__ == "__main__":
    unittest.main()
