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
SPEC = REPOSITORY / "data/reporting/sandero_ecog120_manual_completeness.json"
EVIDENCE = REPOSITORY / "data/reporting/sandero_ecog120_manual_gap_evidence.json"
CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_manual",
}


class SanderoEcoG120ManualReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = completeness.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.coverage = source_coverage.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.comparison = comparison.collect_report(REPOSITORY, SPEC, EVIDENCE, AS_OF)

    def test_scope_selects_exactly_five_manual_configurations(self) -> None:
        scope = self.completeness["scope"]
        self.assertEqual(set(scope["reporting_configuration_codes"]), CONFIGURATIONS)
        self.assertEqual(scope["reporting_configurations"], 5)
        self.assertEqual(scope["technical_slots"], 45)
        self.assertEqual(scope["equipment_attributes"], 69)
        self.assertEqual(scope["sources"], 5)

    def test_completeness_preserves_full_denominators_and_explicit_gaps(self) -> None:
        self.assertEqual(
            self.completeness["technical"],
            {
                "applicable": 225,
                "coverage_percent": "98.22",
                "denominator": 225,
                "missing": 4,
                "not_applicable": 0,
                "present": 221,
            },
        )
        self.assertEqual(
            self.completeness["equipment"],
            {
                "applicable": 345,
                "coverage_percent": "86.38",
                "denominator": 345,
                "missing": 47,
                "not_applicable": 0,
                "not_available": 23,
                "optional": 0,
                "recorded": 298,
                "standard": 275,
                "unknown": 0,
            },
        )
        self.assertEqual(len(self.completeness["gaps"]["technical"]), 4)
        self.assertEqual(len(self.completeness["gaps"]["equipment"]), 47)

    def test_source_coverage_preserves_partial_and_missing_sections(self) -> None:
        self.assertEqual(
            self.coverage["source_registration"],
            {
                "expected": 5,
                "future": 0,
                "inactive": 0,
                "metadata_complete": 5,
                "missing": 0,
                "registered": 5,
            },
        )
        self.assertEqual(
            self.coverage["areas"],
            {"covered": 11, "denominator": 20, "missing": 0, "partial": 9, "source_missing": 0},
        )
        self.assertEqual(
            self.coverage["sections"],
            {
                "covered": 134,
                "denominator": 170,
                "missing": 7,
                "not_applicable": 0,
                "partial": 29,
                "source_missing": 0,
            },
        )
        self.assertEqual(self.coverage["records"]["technical"]["present"], 221)
        self.assertEqual(self.coverage["records"]["equipment"]["present"], 298)
        self.assertEqual(self.coverage["records"]["prices"]["present"], 5)
        self.assertEqual(len(self.coverage["gaps"]), 51)

    def test_ten_pairs_are_same_transmission_and_evidence_aware(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 10)
        self.assertEqual(
            Counter(pair["pair_type"] for pair in pairs),
            Counter({"different_version_same_transmission": 10}),
        )
        self.assertEqual(sum(pair["summary"]["technical"]["not_comparable"] for pair in pairs), 10)
        self.assertEqual(sum(pair["summary"]["equipment"]["not_comparable"] for pair in pairs), 148)
        self.assertEqual(sum(pair["summary"]["prices"]["not_comparable"] for pair in pairs), 0)

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(
            self.comparison["summary"],
            {
                "equipment": {"comparisons": 690, "different": 14, "equal": 528, "not_comparable": 148},
                "prices": {"comparisons": 10, "different": 10, "equal": 0, "not_comparable": 0},
                "technical": {"comparisons": 450, "different": 122, "equal": 318, "not_comparable": 10},
                "total_differences": 146,
            },
        )

    def test_evidence_decisions_are_preserved_without_inference(self) -> None:
        self.assertEqual(
            self.comparison["evidence_summary"],
            {"ambiguous": 0, "found": 0, "not_stated": 34, "out_of_scope": 17, "total": 51},
        )
        ranged = [
            item
            for pair in self.comparison["pairs"]
            for item in pair["technical"]
            if "minimum_value" in item["left"] or "minimum_value" in item["right"]
        ]
        self.assertEqual(ranged, [])

    def test_all_five_prices_are_present_and_all_ten_pair_prices_differ(self) -> None:
        self.assertEqual(self.coverage["records"]["prices"]["records"], 5)
        self.assertEqual(sum(pair["summary"]["prices"]["different"] for pair in self.comparison["pairs"]), 10)


if __name__ == "__main__":
    unittest.main()
