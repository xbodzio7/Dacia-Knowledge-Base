from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import verified_pdf_candidate_ledger_review as review_tool  # noqa: E402

LEDGER = ROOT / "data" / "reporting" / "official_dacia_pdf_candidate_ledger.json"
REVIEW_JSON = ROOT / "data" / "reporting" / "verified_pdf_candidate_ledger_review.json"
REVIEW_MARKDOWN = ROOT / "data" / "reporting" / "verified_pdf_candidate_ledger_review.md"


class VerifiedPdfCandidateLedgerReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.review = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
        cls.candidates = {
            candidate["candidate_id"]: candidate
            for candidate in cls.ledger["candidates"]
        }

    def test_metadata_and_summary_are_exact(self) -> None:
        self.assertEqual(self.review["version"], 1)
        self.assertEqual(self.review["kind"], "verified_pdf_candidate_ledger_review")
        self.assertEqual(self.review["reviewed_on"], "2026-07-28")
        self.assertEqual(self.review["status"], "complete")
        self.assertEqual(
            self.review["summary"],
            {
                "sources": 5,
                "pages": 114,
                "candidates": 4256,
                "groups": 30,
                "anchors": 60,
                "decision_group_counts": {
                    "descriptive_non_import": 5,
                    "explicit_non_import": 5,
                    "requires_entity_mapping": 5,
                    "requires_existing_evidence_reconciliation": 10,
                    "requires_visual_semantic_review": 5,
                },
                "decision_candidate_counts": {
                    "descriptive_non_import": 1259,
                    "explicit_non_import": 83,
                    "requires_entity_mapping": 1184,
                    "requires_existing_evidence_reconciliation": 1583,
                    "requires_visual_semantic_review": 147,
                },
                "unassigned_candidates": 0,
                "duplicate_assignments": 0,
                "master_data_changes": 0,
                "approved_import_specs_created": 0,
            },
        )

    def test_source_page_ranges_partition_all_114_pages(self) -> None:
        pages_by_source: dict[str, list[int]] = {}
        for group in self.review["groups"]:
            pages_by_source.setdefault(group["source_code"], []).extend(
                range(group["page_start"], group["page_end"] + 1)
            )
        declared = {
            source["source_code"]: source["declared_pages"]
            for source in self.ledger["sources"]
        }
        self.assertEqual(set(pages_by_source), set(declared))
        for source_code, page_count in declared.items():
            self.assertEqual(pages_by_source[source_code], list(range(1, page_count + 1)))

    def test_every_candidate_is_assigned_exactly_once(self) -> None:
        assigned = [
            candidate_id
            for group in self.review["groups"]
            for candidate_id in group["candidate_ids"]
        ]
        self.assertEqual(len(assigned), 4256)
        self.assertEqual(len(set(assigned)), 4256)
        self.assertEqual(set(assigned), set(self.candidates))

    def test_group_candidate_counts_match_membership(self) -> None:
        for group in self.review["groups"]:
            self.assertEqual(group["candidate_count"], len(group["candidate_ids"]))
            for candidate_id in group["candidate_ids"]:
                candidate = self.candidates[candidate_id]
                self.assertEqual(candidate["source_code"], group["source_code"])
                self.assertGreaterEqual(candidate["page"], group["page_start"])
                self.assertLessEqual(candidate["page"], group["page_end"])

    def test_anchor_candidates_match_ledger_exactly(self) -> None:
        for group in self.review["groups"]:
            self.assertEqual(len(group["anchor_candidates"]), 2)
            for anchor in group["anchor_candidates"]:
                candidate = self.candidates[anchor["candidate_id"]]
                for field in (
                    "page",
                    "line_start",
                    "line_end",
                    "candidate_kind",
                    "exact_text",
                ):
                    self.assertEqual(anchor[field], candidate[field])
                self.assertIn(anchor["candidate_id"], group["candidate_ids"])

    def test_controlled_decisions_and_statuses_are_exact(self) -> None:
        self.assertEqual(
            set(self.review["controlled_decisions"]),
            set(review_tool.DECISIONS),
        )
        for group in self.review["groups"]:
            decision = review_tool.DECISIONS[group["decision_code"]]
            self.assertEqual(group["decision_status"], decision["status"])
            self.assertEqual(group["decision_summary"], decision["summary"])
            self.assertEqual(group["rationale"], decision["rationale"])

    def test_decision_candidate_totals_recalculate_exactly(self) -> None:
        totals = Counter()
        groups = Counter()
        for group in self.review["groups"]:
            totals[group["decision_code"]] += group["candidate_count"]
            groups[group["decision_code"]] += 1
        self.assertEqual(
            dict(sorted(totals.items())),
            self.review["summary"]["decision_candidate_counts"],
        )
        self.assertEqual(
            dict(sorted(groups.items())),
            self.review["summary"]["decision_group_counts"],
        )

    def test_policy_preserves_non_import_boundaries(self) -> None:
        policy = self.review["policy"]
        for field in (
            "every_candidate_assigned_exactly_once",
            "anchors_cite_candidate_id_and_exact_text",
            "group_decisions_do_not_approve_imports",
            "candidate_text_is_not_reinterpreted",
            "missing_text_is_not_negative_evidence",
            "visual_diagram_semantics_are_not_inferred",
        ):
            self.assertTrue(policy[field])
        self.assertFalse(policy["master_data_changes"])
        self.assertFalse(policy["approved_import_spec_generation"])
        self.assertFalse(self.review["promotion_boundary"]["direct_review_to_master_import"])
        self.assertFalse(
            self.review["promotion_boundary"]["direct_review_to_approved_import_spec"]
        )

    def test_evidence_references_are_repository_relative_and_present(self) -> None:
        for group in self.review["groups"]:
            self.assertGreaterEqual(len(group["evidence_references"]), 2)
            for relative in group["evidence_references"]:
                path = Path(relative)
                self.assertFalse(path.is_absolute())
                self.assertNotIn("..", path.parts)
                self.assertTrue((ROOT / path).is_file(), relative)

    def test_group_order_is_stable_by_source_and_page(self) -> None:
        keys = [
            (group["source_code"], group["page_start"], group["group_id"])
            for group in self.review["groups"]
        ]
        self.assertEqual(keys, sorted(keys))

    def test_repeated_generation_is_byte_identical(self) -> None:
        first, first_markdown = review_tool.build_from_paths(ROOT, LEDGER)
        second, second_markdown = review_tool.build_from_paths(ROOT, LEDGER)
        self.assertEqual(review_tool.canonical_json(first), review_tool.canonical_json(second))
        self.assertEqual(first_markdown, second_markdown)
        self.assertEqual(REVIEW_JSON.read_text(encoding="utf-8"), review_tool.canonical_json(first))
        self.assertEqual(REVIEW_MARKDOWN.read_text(encoding="utf-8"), first_markdown)

    def test_verify_detects_json_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "review.json"
            markdown_path = root / "review.md"
            review, markdown = review_tool.build_from_paths(ROOT, LEDGER)
            json_path.write_text(review_tool.canonical_json(review) + " ", encoding="utf-8")
            markdown_path.write_text(markdown, encoding="utf-8")
            with self.assertRaisesRegex(review_tool.LedgerReviewError, "review JSON differs"):
                review_tool.verify_output(
                    json_path,
                    review_tool.canonical_json(review),
                    "review JSON",
                )

    def test_build_rejects_missing_or_duplicate_candidate_assignment(self) -> None:
        original = review_tool.SOURCE_GROUPS
        try:
            review_tool.SOURCE_GROUPS = original[:-1]
            with self.assertRaises(review_tool.LedgerReviewError):
                review_tool.build_review(copy.deepcopy(self.ledger))
        finally:
            review_tool.SOURCE_GROUPS = original

    def test_outputs_and_next_package_remain_review_only(self) -> None:
        self.assertEqual(review_tool.DEFAULT_JSON.parts[:2], ("data", "reporting"))
        self.assertEqual(review_tool.DEFAULT_MARKDOWN.parts[:2], ("data", "reporting"))
        self.assertNotIn("data/master", review_tool.DEFAULT_JSON.as_posix())
        self.assertNotIn("data/imports", review_tool.DEFAULT_JSON.as_posix())
        self.assertEqual(
            self.review["next_package"]["name"],
            "Verified PDF Candidate Coverage Reconciliation",
        )
        self.assertIn("without creating imports", self.review["next_package"]["goal"])


if __name__ == "__main__":
    unittest.main()
