from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "bigster_technical_page20_ambiguity_review.py"
SPEC = importlib.util.spec_from_file_location("bigster_page20_review", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class BigsterPage20ReviewUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prioritization = json.loads(
            (ROOT / review.DEFAULT_PRIORITIZATION).read_text(encoding="utf-8")
        )

    def test_signature_helper_uses_complete_scalar_identity(self) -> None:
        self.assertEqual(
            review.signature("gross_train_weight", "3430"),
            {
                "attribute_code": "gross_train_weight",
                "value": "3430",
                "fuel_type_code": "",
                "gear_number": "",
            },
        )

    def test_fact_helper_preserves_source_values(self) -> None:
        self.assertEqual(
            review.fact("boot_capacity", ["444", "556"], "deferred"),
            {
                "attribute_code": "boot_capacity",
                "source_values": ["444", "556"],
                "reason": "deferred",
            },
        )

    def test_validate_prioritization_selects_exact_package(self) -> None:
        package = review.validate_prioritization(self.prioritization)
        self.assertEqual(package["package_id"], "residual_gap_001")
        self.assertEqual(package["candidate_count"], 23)

    def test_validate_prioritization_rejects_wrong_kind(self) -> None:
        payload = copy.deepcopy(self.prioritization)
        payload["kind"] = "different"
        with self.assertRaisesRegex(review.BigsterPage20ReviewError, "kind"):
            review.validate_prioritization(payload)

    def test_validate_prioritization_rejects_import_policy_drift(self) -> None:
        payload = copy.deepcopy(self.prioritization)
        payload["policy"]["approved_import_spec_generation"] = True
        with self.assertRaisesRegex(review.BigsterPage20ReviewError, "imports"):
            review.validate_prioritization(payload)

    def test_selected_signatures_rejects_missing_signature(self) -> None:
        candidate = review.validate_prioritization(self.prioritization)["candidates"][0]
        with self.assertRaisesRegex(review.BigsterPage20ReviewError, "not attached"):
            review.selected_signatures(
                candidate,
                [review.signature("gross_vehicle_weight", "1930")],
            )

    def test_authored_manifest_contains_exactly_23_unique_candidates(self) -> None:
        identifiers = [item["candidate_id"] for item in review.DECISIONS]
        self.assertEqual(len(identifiers), 23)
        self.assertEqual(len(set(identifiers)), 23)

    def test_authored_manifest_uses_only_supported_decisions(self) -> None:
        self.assertTrue(
            {item["decision"] for item in review.DECISIONS}
            <= review.DECISION_STATUSES
        )

    def test_restricted_output_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            with self.assertRaisesRegex(review.BigsterPage20ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/master/review.json"))
            with self.assertRaisesRegex(review.BigsterPage20ReviewError, "restricted"):
                review.ensure_safe_output(root, Path("data/imports/review.json"))

    def test_verify_output_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.json"
            path.write_text("different\n", encoding="utf-8")
            with self.assertRaisesRegex(review.BigsterPage20ReviewError, "differs"):
                review.verify_output(path, "expected\n", "review")


class BigsterPage20ReviewRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload, cls.markdown = review.build_from_path(
            ROOT, review.DEFAULT_PRIORITIZATION
        )
        cls.by_line = {
            item["line_start"]: item for item in cls.payload["decisions"]
        }

    def test_source_receipt_is_hash_verified(self) -> None:
        self.assertEqual(
            self.payload["source_receipt"]["sha256"],
            review.SOURCE_SHA256,
        )
        self.assertEqual(self.payload["source_receipt"]["page"], 20)

    def test_summary_matches_authored_partition(self) -> None:
        self.assertEqual(
            self.payload["summary"],
            {
                "candidate_count": 23,
                "decision_counts": {
                    "context_only_non_import": 7,
                    "covered_by_selected_evidence": 9,
                    "deferred_source_conflict": 2,
                    "partially_covered": 3,
                    "unresolved_signature_mismatch": 2,
                },
                "selected_evidence_signature_count": 36,
                "selected_evidence_record_count": 143,
                "candidates_with_selected_evidence": 12,
                "candidates_without_selected_evidence": 11,
            },
        )

    def test_every_candidate_is_decided_once(self) -> None:
        identifiers = [item["candidate_id"] for item in self.payload["decisions"]]
        self.assertEqual(len(identifiers), 23)
        self.assertEqual(len(set(identifiers)), 23)

    def test_selected_records_preserve_source_and_page(self) -> None:
        for decision in self.payload["decisions"]:
            for evidence in decision["selected_evidence_signatures"]:
                for record in evidence["records"]:
                    self.assertEqual(record["source_code"], review.SOURCE_CODE)
                    self.assertEqual(record["source_page"], 20)

    def test_steering_row_selects_only_steering_signature(self) -> None:
        selected = self.by_line[63]["selected_evidence_signatures"]
        self.assertEqual(
            [item["signature"] for item in selected],
            [review.signature("steering_type", "Ze wspomaganiem elektrycznym")],
        )

    def test_gross_vehicle_row_rejects_gross_train_substitution(self) -> None:
        decision = self.by_line[113]
        self.assertEqual(
            decision["authored_decision"], "unresolved_signature_mismatch"
        )
        self.assertEqual(decision["selected_evidence_signatures"], [])
        self.assertEqual(
            decision["source_facts"][0]["attribute_code"],
            "gross_vehicle_weight",
        )

    def test_braked_trailer_row_rejects_unbraked_substitution(self) -> None:
        decision = self.by_line[118]
        self.assertEqual(
            decision["authored_decision"], "unresolved_signature_mismatch"
        )
        self.assertEqual(
            decision["source_facts"][0]["source_values"],
            ["1500", "1500", "1500", "1000"],
        )

    def test_unbraked_rows_select_all_four_exact_values(self) -> None:
        for line in (121, 123):
            values = {
                item["signature"]["value"]
                for item in self.by_line[line]["selected_evidence_signatures"]
            }
            self.assertEqual(values, {"710", "740", "745", "750"})

    def test_hybrid_g_cargo_values_remain_deferred(self) -> None:
        deferred = {
            value
            for line in (125, 135)
            for fact in self.by_line[line]["source_facts"]
            for value in fact["source_values"]
        }
        self.assertEqual(deferred, {"444", "556"})
        self.assertTrue(
            all(
                self.by_line[line]["authored_decision"]
                == "deferred_source_conflict"
                for line in (125, 135)
            )
        )

    def test_adjacent_spare_wheel_fragments_are_selected_on_own_candidates(self) -> None:
        upright = {
            item["signature"]["value"]
            for item in self.by_line[127]["selected_evidence_signatures"]
        }
        folded = {
            item["signature"]["value"]
            for item in self.by_line[132]["selected_evidence_signatures"]
        }
        self.assertEqual(upright, {"624", "488"})
        self.assertEqual(folded, {"1894", "1791"})

    def test_context_lines_do_not_create_scalar_selection(self) -> None:
        for line in (107, 128, 130, 133, 137, 140, 142):
            decision = self.by_line[line]
            self.assertEqual(
                decision["authored_decision"], "context_only_non_import"
            )
            self.assertEqual(decision["selected_evidence_signatures"], [])

    def test_policy_preserves_no_import_boundary(self) -> None:
        self.assertFalse(self.payload["policy"]["master_data_changes"])
        self.assertFalse(
            self.payload["policy"]["approved_import_spec_generation"]
        )
        self.assertFalse(self.payload["policy"]["automatic_promotion"])

    def test_next_package_is_jogger_page19_review(self) -> None:
        self.assertEqual(
            self.payload["next_package"]["name"],
            "Jogger Technical Page 19 Ambiguity Review",
        )
        self.assertIn("16 ambiguous technical candidates", self.payload["next_package"]["goal"])

    def test_markdown_is_deterministic_and_complete(self) -> None:
        self.assertEqual(
            self.markdown,
            review.render_markdown(copy.deepcopy(self.payload)),
        )
        self.assertIn("Unresolved signature mismatch | 2", self.markdown)
        self.assertIn("Hybrid-G 150 4x4 cargo remains deferred", self.markdown)

    def test_committed_reports_match_deterministic_output(self) -> None:
        self.assertEqual(
            (ROOT / review.DEFAULT_JSON).read_text(encoding="utf-8"),
            review.canonical_json(self.payload),
        )
        self.assertEqual(
            (ROOT / review.DEFAULT_MARKDOWN).read_text(encoding="utf-8"),
            self.markdown,
        )


if __name__ == "__main__":
    unittest.main()
