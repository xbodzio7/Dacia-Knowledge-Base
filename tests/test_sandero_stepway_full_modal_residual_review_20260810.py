from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.review_sandero_stepway_full_modal_residual_20260810 import (
    NEGATIVE,
    TECHNICAL_TARGET_HINTS,
    build_report,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/sandero_stepway_full_modal_residual_review_20260810.json"


class SanderoStepwayFullModalResidualReviewTests(unittest.TestCase):
    def test_report_matches_live_classification(self) -> None:
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(build_report(), expected)

    def test_review_accounts_for_every_live_residual_row(self) -> None:
        summary = build_report()["summary"]
        self.assertEqual(summary["current_residual_rows"], 940)
        self.assertEqual(
            summary["safe_normalization_candidate_rows"]
            + summary["preserved_evidence_rows"],
            940,
        )

    def test_negative_or_base_wording_is_never_a_safe_candidate(self) -> None:
        self.assertEqual(len(NEGATIVE), 5)
        report = build_report()
        self.assertEqual(report["policy_counts"]["preserve_negative_or_base"], 59)

    def test_door_count_uses_current_canonical_attribute(self) -> None:
        self.assertEqual(TECHNICAL_TARGET_HINTS["Liczba drzwi"], ["number_of_doors"])
        self.assertNotIn("door_count", TECHNICAL_TARGET_HINTS["Liczba drzwi"])

    def test_model_qualified_context_remains_preserved(self) -> None:
        report = build_report()
        self.assertEqual(report["policy_counts"]["preserve_technical_context"], 60)


if __name__ == "__main__":
    unittest.main()
