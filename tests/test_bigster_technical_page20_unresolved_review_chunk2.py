from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/bigster_technical_page20_unresolved_review_chunk2.py"
SPEC = importlib.util.spec_from_file_location("bigster_page20_unresolved_chunk2", PATH)
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
            ("residual_gap_017", 29),
        )

    def test_03_chunk_identity(self):
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(
            (package["group_candidate_count"], package["chunk_index"], package["chunk_count"]),
            (69, 2, 2),
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
            review.BigsterPage20UnresolvedChunk2ReviewError, "kind"
        ):
            review.validate_prioritization(payload)

    def test_06_import_policy(self):
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(
            review.BigsterPage20UnresolvedChunk2ReviewError, "imports"
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
        self.assertEqual(set(partition), set(range(1, 30)))

    def test_09_restricted_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            with self.assertRaisesRegex(
                review.BigsterPage20UnresolvedChunk2ReviewError, "restricted"
            ):
                review.ensure_safe_output(root, Path("data/master/x"))

    def test_10_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x"
            path.write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(
                review.BigsterPage20UnresolvedChunk2ReviewError, "differs"
            ):
                review.verify_output(path, "y", "x")


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.markdown = review.build_from_path(
            ROOT, review.DEFAULT_PRIORITIZATION
        )
        cls.by_row = {
            item["logical_row"]: item
            for item in cls.payload["decisions"]
            if item["source_facts"]
        }

    def test_11_source_receipt_and_summary(self):
        self.assertEqual(self.payload["source_receipt"]["sha256"], review.SOURCE_SHA256)
        self.assertEqual(self.payload["source_receipt"]["page"], 20)
        self.assertEqual(
            self.payload["summary"]["decision_counts"],
            {
                "context_only_non_import": 21,
                "unresolved_signature_mismatch": 8,
            },
        )

    def test_12_zero_selected_evidence(self):
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

    def test_13_exact_candidate_order(self):
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

    def test_14_visual_columns_and_tank(self):
        layout = self.payload["source_page_layout"]
        self.assertEqual(tuple(layout["powertrain_columns"]), review.POWERTRAIN_COLUMNS)
        tank = self.by_row["fuel_tank_capacity"]["source_facts"][0]
        self.assertEqual(
            tank["values_by_powertrain"]["mild_hybrid_g_140"],
            ["LPG: 50", "Benzyna: 50"],
        )

    def test_15_co2_group(self):
        fact = self.by_row["co2_emissions_combined"]["source_facts"][0]
        self.assertEqual(
            fact["values_by_powertrain"]["mild_hybrid_g_140"],
            ["Benzyna: 130/132", "LPG: 114/116"],
        )

    def test_16_consumption_group(self):
        fact = self.by_row["fuel_consumption_combined"]["source_facts"][0]
        self.assertEqual(
            fact["values_by_powertrain"]["hybrid_g_150_4x4"],
            ["5,9/7,2 (LPG)"],
        )

    def test_17_payload_and_label_roles(self):
        fact = self.by_row["payload"]["source_facts"][0]
        self.assertEqual(fact["values_by_powertrain"]["hybrid_155"], ["453/521"])
        labels = [
            item for item in self.payload["decisions"]
            if item["logical_row"].endswith("_label")
        ]
        self.assertEqual(len(labels), 3)
        self.assertTrue(
            all(item["row_role"] == "surrounding_row_label_fragment" for item in labels)
        )

    def test_18_luggage_vda_rows(self):
        shelf = self.by_row["luggage_vda_shelf"]["source_facts"][0]
        folded = self.by_row["luggage_vda_folded"]["source_facts"][0]
        self.assertEqual(
            shelf["values_by_powertrain"]["hybrid_g_150_4x4"],
            ["444", "nie ma zestawu naprawczego / koła zapasowego"],
        )
        self.assertEqual(
            folded["values_by_powertrain"]["mild_hybrid_140"],
            ["1937 / 1894"],
        )

    def test_19_luggage_liters_shelf(self):
        shelf = self.by_row["luggage_liters_shelf"]["source_facts"][0]
        self.assertEqual(
            shelf["values_by_powertrain"]["hybrid_155"],
            ["612 / 566"],
        )

    def test_20_luggage_liters_folded_literal_sequence(self):
        folded = self.by_row["luggage_liters_folded"]["source_facts"][0]
        self.assertEqual(
            folded["values_by_powertrain"]["mild_hybrid_140"],
            ["1960**", "2002 / 1981"],
        )

    def test_21_footnote_roles(self):
        footnotes = [
            item for item in self.payload["decisions"]
            if item["row_role"] == "footnote_context"
        ]
        self.assertEqual(len(footnotes), 7)
        self.assertTrue(
            all(item["authored_decision"] == "context_only_non_import" for item in footnotes)
        )

    def test_22_source_note_roles(self):
        notes = [
            item for item in self.payload["decisions"]
            if item["row_role"] == "source_note_context"
        ]
        self.assertEqual(len(notes), 3)

    def test_23_prior_chunk_reference(self):
        prior = self.payload["prior_chunk_reference"]
        self.assertEqual(prior["package_id"], "residual_gap_016")
        self.assertEqual(prior["candidate_count"], 40)
        self.assertEqual((prior["chunk_index"], prior["chunk_count"]), (1, 2))

    def test_24_deterministic_outputs(self):
        self.assertEqual(
            (ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"),
            review.canonical_json(self.payload),
        )
        self.assertEqual(
            (ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"),
            self.markdown,
        )
        self.assertIn("## Chunk boundary", self.markdown)

    def test_25_policy_and_next(self):
        self.assertTrue(self.payload["policy"]["zero_attached_evidence_preserved"])
        self.assertTrue(
            self.payload["policy"][
                "literal_source_values_preserved_without_invented_interpretation"
            ]
        )
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertEqual(
            self.payload["next_package"]["name"],
            "Duster Mini Technical Page 21 Unresolved Review — Chunk 1",
        )
        self.assertIn("1960**", self.markdown)
        self.assertIn("2002 / 1981", self.markdown)


if __name__ == "__main__":
    unittest.main()
