from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_completeness as completeness  # noqa: E402
import configuration_comparison as comparison  # noqa: E402
import source_coverage  # noqa: E402

SPEC = REPOSITORY / "data" / "reporting" / "duster_ecog120_completeness.json"
EVIDENCE = REPOSITORY / "data" / "reporting" / "duster_ecog120_gap_evidence.spec"
AS_OF = "2026-02-06"
EXPECTED_CONFIGURATIONS = {
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
}


class DusterEcoG120ReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = completeness.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.coverage = source_coverage.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.comparison = comparison.collect_report(
            REPOSITORY,
            SPEC,
            EVIDENCE,
            AS_OF,
        )

    def test_scope_selects_four_current_ecog120_configurations(self) -> None:
        self.assertEqual(
            set(self.completeness["scope"]["reporting_configuration_codes"]),
            EXPECTED_CONFIGURATIONS,
        )
        self.assertEqual(self.completeness["scope"]["reporting_configurations"], 4)
        self.assertEqual(self.completeness["scope"]["sources"], 1)

    def test_scope_has_seventeen_technical_slots_and_fifty_eight_equipment_attributes(self) -> None:
        self.assertEqual(self.completeness["scope"]["technical_slots"], 17)
        self.assertEqual(self.completeness["scope"]["equipment_attributes"], 58)

    def test_completeness_is_one_hundred_percent(self) -> None:
        self.assertEqual(
            self.completeness["technical"],
            {
                "applicable": 68,
                "coverage_percent": "100.00",
                "denominator": 68,
                "missing": 0,
                "not_applicable": 0,
                "present": 68,
            },
        )
        self.assertEqual(self.completeness["equipment"]["coverage_percent"], "100.00")
        self.assertEqual(self.completeness["equipment"]["recorded"], 232)
        self.assertEqual(self.completeness["gaps"], {"equipment": [], "technical": []})

    def test_source_coverage_is_complete(self) -> None:
        self.assertEqual(
            self.coverage["source_registration"],
            {
                "expected": 1,
                "future": 0,
                "inactive": 0,
                "metadata_complete": 1,
                "missing": 0,
                "registered": 1,
            },
        )
        self.assertEqual(self.coverage["areas"]["missing"], 0)
        self.assertEqual(self.coverage["sections"]["missing"], 0)
        self.assertEqual(self.coverage["gaps"], [])

    def test_comparison_has_six_complete_pairs(self) -> None:
        self.assertEqual(len(self.comparison["pairs"]), 6)
        self.assertEqual(
            Counter(pair["pair_type"] for pair in self.comparison["pairs"]),
            Counter({"different_version_same_transmission": 6}),
        )
        self.assertEqual(
            {pair["summary"]["technical"]["not_comparable"] for pair in self.comparison["pairs"]},
            {0},
        )

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(
            self.comparison["summary"],
            {
                "equipment": {
                    "comparisons": 348,
                    "different": 81,
                    "equal": 267,
                    "not_comparable": 0,
                },
                "prices": {
                    "comparisons": 6,
                    "different": 6,
                    "equal": 0,
                    "not_comparable": 0,
                },
                "technical": {
                    "comparisons": 102,
                    "different": 0,
                    "equal": 102,
                    "not_comparable": 0,
                },
                "total_differences": 87,
            },
        )

    def test_empty_evidence_is_valid_because_the_scope_has_no_gaps(self) -> None:
        self.assertEqual(
            self.comparison["evidence_summary"],
            {
                "ambiguous": 0,
                "found": 0,
                "not_stated": 0,
                "out_of_scope": 0,
                "total": 0,
            },
        )

    def test_default_sandero_reporting_denominator_remains_unchanged(self) -> None:
        default = comparison.collect_report(
            REPOSITORY,
            REPOSITORY / comparison.DEFAULT_COMPLETENESS_SPEC,
            REPOSITORY / comparison.DEFAULT_EVIDENCE_SPEC,
        )
        self.assertEqual(default["scope"]["reporting_configurations"], 7)
        self.assertEqual(len(default["pairs"]), 21)
        self.assertEqual(default["summary"]["total_differences"], 305)


if __name__ == "__main__":
    unittest.main()
