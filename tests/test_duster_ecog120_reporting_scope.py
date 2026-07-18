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

AS_OF = "2026-02-06"
SCOPES = {
    "ecog100": {
        "spec": REPOSITORY / "data" / "reporting" / "duster_ecog100_completeness.json",
        "evidence": REPOSITORY / "data" / "reporting" / "duster_ecog100_gap_evidence.spec",
        "configurations": {
            "duster_iii_essential_ecog100_4x2_manual",
            "duster_iii_expression_ecog100_4x2_manual",
            "duster_iii_extreme_ecog100_4x2_manual",
            "duster_iii_journey_ecog100_4x2_manual",
        },
        "technical_slots": 21,
        "technical_records": 84,
        "technical_comparisons": 126,
        "equal_prices": 1,
        "different_prices": 5,
        "total_differences": 86,
    },
    "ecog120": {
        "spec": REPOSITORY / "data" / "reporting" / "duster_ecog120_completeness.json",
        "evidence": REPOSITORY / "data" / "reporting" / "duster_ecog120_gap_evidence.spec",
        "configurations": {
            "duster_iii_essential_ecog120_4x2_manual",
            "duster_iii_expression_ecog120_4x2_manual",
            "duster_iii_extreme_ecog120_4x2_manual",
            "duster_iii_journey_ecog120_4x2_manual",
        },
        "technical_slots": 17,
        "technical_records": 68,
        "technical_comparisons": 102,
        "equal_prices": 0,
        "different_prices": 6,
        "total_differences": 87,
    },
}


class DusterEcoGReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = {
            name: completeness.collect_report(REPOSITORY, scope["spec"], AS_OF)
            for name, scope in SCOPES.items()
        }
        cls.coverage = {
            name: source_coverage.collect_report(REPOSITORY, scope["spec"], AS_OF)
            for name, scope in SCOPES.items()
        }
        cls.comparison = {
            name: comparison.collect_report(
                REPOSITORY,
                scope["spec"],
                scope["evidence"],
                AS_OF,
            )
            for name, scope in SCOPES.items()
        }

    def test_scopes_select_four_current_ecog_configurations(self) -> None:
        for name, scope in SCOPES.items():
            report = self.completeness[name]
            self.assertEqual(
                set(report["scope"]["reporting_configuration_codes"]),
                scope["configurations"],
                name,
            )
            self.assertEqual(report["scope"]["reporting_configurations"], 4, name)
            self.assertEqual(report["scope"]["sources"], 1, name)

    def test_scopes_have_expected_technical_slots_and_fifty_eight_equipment_attributes(self) -> None:
        for name, scope in SCOPES.items():
            report = self.completeness[name]
            self.assertEqual(report["scope"]["technical_slots"], scope["technical_slots"], name)
            self.assertEqual(report["scope"]["equipment_attributes"], 58, name)

    def test_completeness_is_one_hundred_percent(self) -> None:
        for name, scope in SCOPES.items():
            expected = scope["technical_records"]
            report = self.completeness[name]
            self.assertEqual(
                report["technical"],
                {
                    "applicable": expected,
                    "coverage_percent": "100.00",
                    "denominator": expected,
                    "missing": 0,
                    "not_applicable": 0,
                    "present": expected,
                },
                name,
            )
            self.assertEqual(report["equipment"]["coverage_percent"], "100.00", name)
            self.assertEqual(report["equipment"]["recorded"], 232, name)
            self.assertEqual(report["gaps"], {"equipment": [], "technical": []}, name)

    def test_source_coverage_is_complete(self) -> None:
        for name, report in self.coverage.items():
            self.assertEqual(
                report["source_registration"],
                {
                    "expected": 1,
                    "future": 0,
                    "inactive": 0,
                    "metadata_complete": 1,
                    "missing": 0,
                    "registered": 1,
                },
                name,
            )
            self.assertEqual(report["areas"]["missing"], 0, name)
            self.assertEqual(report["sections"]["missing"], 0, name)
            self.assertEqual(report["gaps"], [], name)

    def test_comparisons_have_six_complete_pairs(self) -> None:
        for name, report in self.comparison.items():
            self.assertEqual(len(report["pairs"]), 6, name)
            self.assertEqual(
                Counter(pair["pair_type"] for pair in report["pairs"]),
                Counter({"different_version_same_transmission": 6}),
                name,
            )
            self.assertEqual(
                {pair["summary"]["technical"]["not_comparable"] for pair in report["pairs"]},
                {0},
                name,
            )

    def test_comparison_summaries_are_stable(self) -> None:
        for name, scope in SCOPES.items():
            technical_comparisons = scope["technical_comparisons"]
            self.assertEqual(
                self.comparison[name]["summary"],
                {
                    "equipment": {
                        "comparisons": 348,
                        "different": 81,
                        "equal": 267,
                        "not_comparable": 0,
                    },
                    "prices": {
                        "comparisons": 6,
                        "different": scope["different_prices"],
                        "equal": scope["equal_prices"],
                        "not_comparable": 0,
                    },
                    "technical": {
                        "comparisons": technical_comparisons,
                        "different": 0,
                        "equal": technical_comparisons,
                        "not_comparable": 0,
                    },
                    "total_differences": scope["total_differences"],
                },
                name,
            )

    def test_empty_evidence_is_valid_because_the_scopes_have_no_gaps(self) -> None:
        expected = {
            "ambiguous": 0,
            "found": 0,
            "not_stated": 0,
            "out_of_scope": 0,
            "total": 0,
        }
        for name, report in self.comparison.items():
            self.assertEqual(report["evidence_summary"], expected, name)

    def test_reporting_denominators_remain_independent(self) -> None:
        default = comparison.collect_report(
            REPOSITORY,
            REPOSITORY / comparison.DEFAULT_COMPLETENESS_SPEC,
            REPOSITORY / comparison.DEFAULT_EVIDENCE_SPEC,
        )
        self.assertEqual(default["scope"]["reporting_configurations"], 7)
        self.assertEqual(len(default["pairs"]), 21)
        self.assertEqual(default["summary"]["total_differences"], 305)
        self.assertTrue(
            SCOPES["ecog100"]["configurations"].isdisjoint(
                SCOPES["ecog120"]["configurations"]
            )
        )


if __name__ == "__main__":
    unittest.main()
