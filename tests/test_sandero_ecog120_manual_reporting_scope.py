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
CONFIGURATIONS = {'sandero_iii_expression_ecog120_manual',
 'sandero_iii_journey_ecog120_manual',
 'sandero_stepway_iii_essential_ecog120_manual',
 'sandero_stepway_iii_expression_ecog120_manual',
 'sandero_stepway_iii_extreme_ecog120_manual'}
EXPECTED_TECHNICAL = {'applicable': 300, 'coverage_percent': '96.00', 'denominator': 300, 'missing': 12, 'not_applicable': 0, 'present': 288}
EXPECTED_EQUIPMENT = {'applicable': 345,
 'coverage_percent': '86.96',
 'denominator': 345,
 'missing': 45,
 'not_applicable': 0,
 'not_available': 23,
 'optional': 0,
 'recorded': 300,
 'standard': 277,
 'unknown': 0}
EXPECTED_SOURCE_REGISTRATION = {'expected': 5, 'future': 0, 'inactive': 0, 'metadata_complete': 5, 'missing': 0, 'registered': 5}
EXPECTED_AREAS = {'covered': 12, 'denominator': 20, 'missing': 0, 'partial': 8, 'source_missing': 0}
EXPECTED_SECTIONS = {'covered': 138, 'denominator': 175, 'missing': 7, 'not_applicable': 0, 'partial': 30, 'source_missing': 0}
EXPECTED_COMPARISON_SUMMARY = {'prices': {'comparisons': 10, 'equal': 0, 'different': 10, 'not_comparable': 0},
 'technical': {'comparisons': 688, 'equal': 469, 'different': 171, 'not_comparable': 48},
 'equipment': {'comparisons': 690, 'equal': 529, 'different': 20, 'not_comparable': 141},
 'total_differences': 201}
EXPECTED_EVIDENCE_SUMMARY = {'total': 57, 'ambiguous': 0, 'found': 0, 'not_stated': 40, 'out_of_scope': 17}
EXPECTED_PAIR_TYPES = {'different_version_same_transmission': 10}
EXPECTED_NOT_COMPARABLE = {'technical': 48, 'equipment': 141, 'prices': 0}
EXPECTED_RANGED = 43
EXPECTED_TECHNICAL_GAPS = 12
EXPECTED_EQUIPMENT_GAPS = 45
EXPECTED_COVERAGE_GAPS = 57


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
        self.assertEqual(scope["technical_slots"], 60)
        self.assertEqual(scope["equipment_attributes"], 69)
        self.assertEqual(scope["sources"], 5)

    def test_completeness_preserves_full_denominators_and_explicit_gaps(self) -> None:
        self.assertEqual(self.completeness["technical"], EXPECTED_TECHNICAL)
        self.assertEqual(self.completeness["equipment"], EXPECTED_EQUIPMENT)
        self.assertEqual(len(self.completeness["gaps"]["technical"]), EXPECTED_TECHNICAL_GAPS)
        self.assertEqual(len(self.completeness["gaps"]["equipment"]), EXPECTED_EQUIPMENT_GAPS)

    def test_source_coverage_preserves_partial_and_missing_sections(self) -> None:
        self.assertEqual(self.coverage["source_registration"], EXPECTED_SOURCE_REGISTRATION)
        self.assertEqual(self.coverage["areas"], EXPECTED_AREAS)
        self.assertEqual(self.coverage["sections"], EXPECTED_SECTIONS)
        self.assertEqual(
            self.coverage["records"]["technical"]["present"],
            EXPECTED_TECHNICAL["present"],
        )
        self.assertEqual(
            self.coverage["records"]["equipment"]["present"],
            EXPECTED_EQUIPMENT["recorded"],
        )
        self.assertEqual(self.coverage["records"]["prices"]["present"], 5)
        self.assertEqual(len(self.coverage["gaps"]), EXPECTED_COVERAGE_GAPS)

    def test_ten_pairs_are_same_transmission_and_evidence_aware(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 10)
        self.assertEqual(
            Counter(pair["pair_type"] for pair in pairs),
            Counter(EXPECTED_PAIR_TYPES),
        )
        for domain, expected in EXPECTED_NOT_COMPARABLE.items():
            with self.subTest(domain=domain):
                self.assertEqual(
                    sum(pair["summary"][domain]["not_comparable"] for pair in pairs),
                    expected,
                )

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(self.comparison["summary"], EXPECTED_COMPARISON_SUMMARY)

    def test_evidence_decisions_are_preserved_without_inference(self) -> None:
        self.assertEqual(self.comparison["evidence_summary"], EXPECTED_EVIDENCE_SUMMARY)
        ranged = [
            item
            for pair in self.comparison["pairs"]
            for item in pair["technical"]
            if "minimum_value" in item["left"] or "minimum_value" in item["right"]
        ]
        self.assertEqual(len(ranged), EXPECTED_RANGED)

    def test_all_five_prices_are_present_and_all_ten_pair_prices_differ(self) -> None:
        self.assertEqual(self.coverage["records"]["prices"]["records"], 5)
        self.assertEqual(
            sum(pair["summary"]["prices"]["different"] for pair in self.comparison["pairs"]),
            10,
        )


if __name__ == "__main__":
    unittest.main()
