from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import configuration_completeness as completeness  # noqa: E402
import configuration_comparison as comparison  # noqa: E402
import source_coverage  # noqa: E402

AS_OF = "2026-06-26"
SPEC = REPOSITORY / "data/reporting/sandero_stepway_ecog120_automatic_completeness.json"
EVIDENCE = REPOSITORY / "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json"
CONFIGURATIONS = {
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_automatic",
}


class SanderoStepwayEcoG120AutomaticReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = completeness.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.coverage = source_coverage.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.comparison = comparison.collect_report(REPOSITORY, SPEC, EVIDENCE, AS_OF)

    def test_scope_selects_exactly_two_automatic_configurations(self) -> None:
        scope = self.completeness["scope"]
        self.assertEqual(set(scope["reporting_configuration_codes"]), CONFIGURATIONS)
        self.assertEqual(scope["reporting_configurations"], 2)
        self.assertEqual(scope["technical_slots"], 45)
        self.assertEqual(scope["equipment_attributes"], 69)
        self.assertEqual(scope["sources"], 2)

    def test_completeness_preserves_full_denominators_and_explicit_gaps(self) -> None:
        self.assertEqual(
            self.completeness["technical"],
            {
                "applicable": 90,
                "coverage_percent": "98.89",
                "denominator": 90,
                "missing": 1,
                "not_applicable": 0,
                "present": 89,
            },
        )
        self.assertEqual(
            self.completeness["equipment"],
            {
                "applicable": 138,
                "coverage_percent": "87.68",
                "denominator": 138,
                "missing": 17,
                "not_applicable": 0,
                "not_available": 7,
                "optional": 0,
                "recorded": 121,
                "standard": 114,
                "unknown": 0,
            },
        )
        self.assertEqual(len(self.completeness["gaps"]["technical"]), 1)
        self.assertEqual(len(self.completeness["gaps"]["equipment"]), 17)

    def test_source_coverage_preserves_partial_and_missing_sections(self) -> None:
        self.assertEqual(
            self.coverage["source_registration"],
            {
                "expected": 2,
                "future": 0,
                "inactive": 0,
                "metadata_complete": 2,
                "missing": 0,
                "registered": 2,
            },
        )
        self.assertEqual(
            self.coverage["areas"],
            {"covered": 5, "denominator": 8, "missing": 0, "partial": 3, "source_missing": 0},
        )
        self.assertEqual(
            self.coverage["sections"],
            {
                "covered": 58,
                "denominator": 68,
                "missing": 2,
                "not_applicable": 0,
                "partial": 8,
                "source_missing": 0,
            },
        )
        self.assertEqual(self.coverage["records"]["technical"]["present"], 89)
        self.assertEqual(self.coverage["records"]["equipment"]["present"], 121)
        self.assertEqual(self.coverage["records"]["prices"]["present"], 2)
        self.assertEqual(len(self.coverage["gaps"]), 18)

    def test_single_pair_is_same_transmission_and_evidence_aware(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(
            Counter(pair["pair_type"] for pair in pairs),
            Counter({"different_version_same_transmission": 1}),
        )
        pair = pairs[0]
        self.assertEqual(pair["summary"]["technical"]["not_comparable"], 1)
        self.assertEqual(pair["summary"]["equipment"]["not_comparable"], 13)
        self.assertEqual(pair["summary"]["prices"]["not_comparable"], 0)

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(
            self.comparison["summary"],
            {
                "equipment": {"comparisons": 69, "different": 1, "equal": 55, "not_comparable": 13},
                "prices": {"comparisons": 1, "different": 1, "equal": 0, "not_comparable": 0},
                "technical": {"comparisons": 45, "different": 7, "equal": 37, "not_comparable": 1},
                "total_differences": 9,
            },
        )

    def test_evidence_decisions_are_preserved_without_inference(self) -> None:
        self.assertEqual(
            self.comparison["evidence_summary"],
            {"ambiguous": 0, "found": 0, "not_stated": 10, "out_of_scope": 8, "total": 18},
        )
        ranged = [
            item
            for pair in self.comparison["pairs"]
            for item in pair["technical"]
            if "minimum_value" in item["left"] or "minimum_value" in item["right"]
        ]
        self.assertEqual(ranged, [])

    def test_two_prices_are_present_and_the_pair_price_differs(self) -> None:
        self.assertEqual(self.coverage["records"]["prices"]["records"], 2)
        self.assertEqual(self.comparison["summary"]["prices"]["different"], 1)


if __name__ == "__main__":
    unittest.main()
