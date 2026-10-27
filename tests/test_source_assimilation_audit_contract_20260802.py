from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDARD = ROOT / "project" / "SOURCE_ASSIMILATION_STANDARD.md"
VALIDATION = (
    ROOT
    / "project"
    / "source-audit"
    / "spring-flexicharger-correction-validation-20260802.md"
)


class SourceAssimilationAuditContractTests(unittest.TestCase):
    def test_standard_requires_complete_page_and_visual_review(self) -> None:
        text = STANDARD.read_text(encoding="utf-8")
        self.assertIn("analysed from the first page to the last page", text)
        self.assertIn("rendered page must also be inspected", text)
        self.assertIn("partial_review", text)
        self.assertIn("fully_assimilated", text)

    def test_flexicharger_validation_preserves_all_three_exact_mappings(self) -> None:
        text = VALIDATION.read_text(encoding="utf-8")
        for grade in (
            "Essential Electric 70",
            "Expression Electric 70",
            "Extreme Electric 100",
        ):
            self.assertIn(f"{grade}: domestic-socket charging cable — optional, 1500 PLN", text)
        self.assertIn(
            "Type 2 charging cable representation remains separate from the domestic-socket cable",
            text,
        )


if __name__ == "__main__":
    unittest.main()
