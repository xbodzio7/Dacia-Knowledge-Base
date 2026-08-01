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
CONFIGURATIONS = {"sandero_stepway_iii_expression_ecog120_automatic", "sandero_stepway_iii_extreme_ecog120_automatic"}
EXPECTED_TECHNICAL = {'applicable': 116, 'coverage_percent': '92.24', 'denominator': 116, 'missing': 9, 'not_applicable': 0, 'present': 107}
EXPECTED_EQUIPMENT = {'applicable': 138,
 'coverage_percent': '88.41',
 'denominator': 138,
 'missing': 16,
 'not_applicable': 0,
 'not_available': 7,
 'optional': 0,
 'recorded': 122,
 'standard': 115,
 'unknown': 0}
EXPECTED_SOURCE_REGISTRATION = {'expected': 2, 'future': 0, 'inactive': 0, 'metadata_complete': 2, 'missing': 0, 'registered': 2}
EXPECTED_AREAS = {'covered': 4, 'denominator': 8, 'missing': 0, 'partial': 4, 'source_missing': 0}
EXPECTED_SECTIONS = {'covered': 58, 'denominator': 70, 'missing': 2, 'not_applicable': 0, 'partial': 10, 'source_missing': 0}
EXPECTED_COMPARISON_SUMMARY = {'prices': {'comparisons': 1, 'equal': 0, 'different': 1, 'not_comparable': 0},
 'technical': {'comparisons': 63, 'equal': 48, 'different': 8, 'not_comparable': 7},
 'equipment': {'comparisons': 69, 'equal': 55, 'different': 1, 'not_comparable': 13},
 'total_differences': 10}
EXPECTED_EVIDENCE_SUMMARY = {'total': 25, 'ambiguous': 4, 'found': 0, 'not_stated': 13, 'out_of_scope': 8}
EXPECTED_PAIR_TYPES = {'different_version_same_transmission': 1}
EXPECTED_NOT_COMPARABLE = {'technical': 7, 'equipment': 13, 'prices': 0}
EXPECTED_RANGED = 3
EXPECTED_TECHNICAL_GAPS = 9
EXPECTED_EQUIPMENT_GAPS = 16
EXPECTED_COVERAGE_GAPS = 25


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
        self.assertEqual(scope["technical_slots"], 58)
        self.assertEqual(scope["equipment_attributes"], 69)
        self.assertEqual(scope["sources"], 2)

    def test_completeness_preserves_full_denominators_and_explicit_gaps(self) -> None:
        self.assertEqual(self.completeness["technical"], EXPECTED_TECHNICAL)
        self.assertEqual(self.completeness["equipment"], EXPECTED_EQUIPMENT)
        self.assertEqual(len(self.completeness["gaps"]["technical"]), EXPECTED_TECHNICAL_GAPS)
        self.assertEqual(len(self.completeness["gaps"]["equipment"]), EXPECTED_EQUIPMENT_GAPS)

    def test_source_coverage_preserves_partial_and_missing_sections(self) -> None:
        self.assertEqual(self.coverage["source_registration"], EXPECTED_SOURCE_REGISTRATION)
        self.assertEqual(self.coverage["areas"], EXPECTED_AREAS)
        self.assertEqual(self.coverage["sections"], EXPECTED_SECTIONS)
        self.assertEqual(self.coverage["records"]["technical"]["present"], EXPECTED_TECHNICAL["present"])
        self.assertEqual(self.coverage["records"]["equipment"]["present"], EXPECTED_EQUIPMENT["recorded"])
        self.assertEqual(self.coverage["records"]["prices"]["present"], 2)
        self.assertEqual(len(self.coverage["gaps"]), EXPECTED_COVERAGE_GAPS)

    def test_single_pair_is_same_transmission_and_evidence_aware(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(Counter(pair["pair_type"] for pair in pairs), Counter(EXPECTED_PAIR_TYPES))
        for domain, expected in EXPECTED_NOT_COMPARABLE.items():
            self.assertEqual(sum(pair["summary"][domain]["not_comparable"] for pair in pairs), expected)

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(self.comparison["summary"], EXPECTED_COMPARISON_SUMMARY)

    def test_evidence_decisions_are_preserved_without_inference(self) -> None:
        self.assertEqual(self.comparison["evidence_summary"], EXPECTED_EVIDENCE_SUMMARY)
        ranged = [item for pair in self.comparison["pairs"] for item in pair["technical"] if "minimum_value" in item["left"] or "minimum_value" in item["right"]]
        self.assertEqual(len(ranged), EXPECTED_RANGED)

    def test_two_prices_are_present_and_the_pair_price_differs(self) -> None:
        self.assertEqual(self.coverage["records"]["prices"]["records"], 2)
        self.assertEqual(self.comparison["summary"]["prices"]["different"], 1)


if __name__ == "__main__":
    unittest.main()
