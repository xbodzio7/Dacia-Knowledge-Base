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
        "equipment_records": 232,
        "pair_count": 6,
        "equal_prices": 1,
        "different_prices": 5,
        "equipment_differences": 81,
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
        "equipment_records": 232,
        "pair_count": 6,
        "equal_prices": 0,
        "different_prices": 6,
        "equipment_differences": 81,
        "total_differences": 87,
    },
    "hybrid140": {
        "spec": REPOSITORY / "data" / "reporting" / "duster_hybrid140_completeness.json",
        "evidence": REPOSITORY / "data" / "reporting" / "duster_hybrid140_gap_evidence.spec",
        "configurations": {
            "duster_iii_expression_hybrid140_4x2_automatic",
            "duster_iii_extreme_hybrid140_4x2_automatic",
            "duster_iii_journey_hybrid140_4x2_automatic",
            "duster_iii_journey_plus_hybrid140_4x2_automatic",
        },
        "technical_slots": 15,
        "technical_records": 60,
        "technical_comparisons": 90,
        "equipment_records": 232,
        "pair_count": 6,
        "equal_prices": 0,
        "different_prices": 6,
        "equipment_differences": 56,
        "total_differences": 62,
    },
    "hybrid155": {
        "spec": REPOSITORY / "data" / "reporting" / "duster_hybrid155_completeness.json",
        "evidence": REPOSITORY / "data" / "reporting" / "duster_hybrid155_gap_evidence.spec",
        "configurations": {
            "duster_iii_expression_hybrid155_4x2_automatic",
            "duster_iii_extreme_hybrid155_4x2_automatic",
            "duster_iii_journey_hybrid155_4x2_automatic",
        },
        "technical_slots": 16,
        "technical_records": 48,
        "technical_comparisons": 48,
        "equipment_records": 174,
        "pair_count": 3,
        "equal_prices": 0,
        "different_prices": 3,
        "equipment_differences": 28,
        "total_differences": 31,
    },
    "mildhybrid130_4x2": {
        "spec": REPOSITORY / "data" / "reporting" / "duster_mildhybrid130_4x2_completeness.json",
        "evidence": REPOSITORY / "data" / "reporting" / "duster_mildhybrid130_4x2_gap_evidence.spec",
        "configurations": {
            "duster_iii_expression_mildhybrid130_4x2_manual",
            "duster_iii_extreme_mildhybrid130_4x2_manual",
            "duster_iii_journey_mildhybrid130_4x2_manual",
        },
        "technical_slots": 15,
        "technical_records": 45,
        "technical_comparisons": 45,
        "equipment_records": 174,
        "pair_count": 3,
        "equal_prices": 0,
        "different_prices": 3,
        "equipment_differences": 28,
        "total_differences": 31,
    },
    "mildhybrid130_4x4": {
        "spec": REPOSITORY / "data" / "reporting" / "duster_mildhybrid130_4x4_completeness.json",
        "evidence": REPOSITORY / "data" / "reporting" / "duster_mildhybrid130_4x4_gap_evidence.spec",
        "configurations": {
            "duster_iii_expression_mildhybrid130_4x4_manual",
            "duster_iii_extreme_mildhybrid130_4x4_manual",
            "duster_iii_journey_mildhybrid130_4x4_manual",
        },
        "technical_slots": 15,
        "technical_records": 45,
        "technical_comparisons": 45,
        "equipment_records": 174,
        "pair_count": 3,
        "equal_prices": 1,
        "different_prices": 2,
        "equipment_differences": 28,
        "total_differences": 30,
    },
}


class DusterReportingScopeTests(unittest.TestCase):
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

    def test_scopes_select_expected_current_configurations(self) -> None:
        for name, scope in SCOPES.items():
            report = self.completeness[name]
            self.assertEqual(
                set(report["scope"]["reporting_configuration_codes"]),
                scope["configurations"],
                name,
            )
            self.assertEqual(
                report["scope"]["reporting_configurations"],
                len(scope["configurations"]),
                name,
            )
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
            self.assertEqual(report["equipment"]["recorded"], scope["equipment_records"], name)
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

    def test_comparisons_have_expected_complete_pairs(self) -> None:
        for name, scope in SCOPES.items():
            report = self.comparison[name]
            pair_count = scope["pair_count"]
            self.assertEqual(len(report["pairs"]), pair_count, name)
            self.assertEqual(
                Counter(pair["pair_type"] for pair in report["pairs"]),
                Counter({"different_version_same_transmission": pair_count}),
                name,
            )
            self.assertEqual(
                {pair["summary"]["technical"]["not_comparable"] for pair in report["pairs"]},
                {0},
                name,
            )

    def test_comparison_summaries_are_stable(self) -> None:
        for name, scope in SCOPES.items():
            summary = self.comparison[name]["summary"]
            technical_comparisons = scope["technical_comparisons"]
            pair_count = scope["pair_count"]
            equipment_comparisons = pair_count * 58
            self.assertEqual(
                summary["technical"],
                {
                    "comparisons": technical_comparisons,
                    "different": 0,
                    "equal": technical_comparisons,
                    "not_comparable": 0,
                },
                name,
            )
            self.assertEqual(
                summary["prices"],
                {
                    "comparisons": pair_count,
                    "different": scope["different_prices"],
                    "equal": scope["equal_prices"],
                    "not_comparable": 0,
                },
                name,
            )
            self.assertEqual(
                summary["equipment"],
                {
                    "comparisons": equipment_comparisons,
                    "different": scope["equipment_differences"],
                    "equal": equipment_comparisons - scope["equipment_differences"],
                    "not_comparable": 0,
                },
                name,
            )
            self.assertEqual(summary["total_differences"], scope["total_differences"], name)

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
        scope_sets = [scope["configurations"] for scope in SCOPES.values()]
        for index, current in enumerate(scope_sets):
            for other in scope_sets[index + 1:]:
                self.assertTrue(current.isdisjoint(other))


if __name__ == "__main__":
    unittest.main()
