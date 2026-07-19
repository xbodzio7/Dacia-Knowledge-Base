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

AS_OF = "2026-04-01"
SPEC = REPOSITORY / "data/reporting/jogger_tce110_manual_completeness.json"
EVIDENCE = REPOSITORY / "data/reporting/jogger_tce110_manual_gap_evidence.spec"
CONFIGURATIONS = {
    "jogger_expression_5seat_tce110_manual",
    "jogger_expression_7seat_tce110_manual",
    "jogger_extreme_5seat_tce110_manual",
    "jogger_extreme_7seat_tce110_manual",
    "jogger_journey_5seat_tce110_manual",
    "jogger_journey_7seat_tce110_manual",
}


class JoggerTce110ManualReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = completeness.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.coverage = source_coverage.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.comparison = comparison.collect_report(REPOSITORY, SPEC, EVIDENCE, AS_OF)

    def test_scope_selects_exactly_six_configurations_and_denominators(self) -> None:
        scope = self.completeness["scope"]
        self.assertEqual(set(scope["reporting_configuration_codes"]), CONFIGURATIONS)
        self.assertEqual(scope["reporting_configurations"], 6)
        self.assertEqual(scope["technical_slots"], 24)
        self.assertEqual(scope["equipment_attributes"], 53)
        self.assertEqual(scope["sources"], 1)

    def test_completeness_is_exact_and_gap_free(self) -> None:
        self.assertEqual(
            self.completeness["technical"],
            {
                "applicable": 144,
                "coverage_percent": "100.00",
                "denominator": 144,
                "missing": 0,
                "not_applicable": 0,
                "present": 144,
            },
        )
        self.assertEqual(
            self.completeness["equipment"],
            {
                "applicable": 318,
                "coverage_percent": "100.00",
                "denominator": 318,
                "missing": 0,
                "not_applicable": 0,
                "not_available": 40,
                "optional": 24,
                "recorded": 318,
                "standard": 254,
                "unknown": 0,
            },
        )
        self.assertEqual(self.completeness["gaps"], {"equipment": [], "technical": []})

    def test_source_coverage_is_complete_for_technical_equipment_and_prices(self) -> None:
        self.assertEqual(
            self.coverage["source_registration"],
            {"expected": 1, "future": 0, "inactive": 0, "metadata_complete": 1, "missing": 0, "registered": 1},
        )
        self.assertEqual(self.coverage["areas"], {"covered": 24, "denominator": 24, "missing": 0, "partial": 0, "source_missing": 0})
        self.assertEqual(self.coverage["sections"], {"covered": 162, "denominator": 162, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})
        self.assertEqual(self.coverage["records"]["technical"]["present"], 144)
        self.assertEqual(self.coverage["records"]["equipment"]["present"], 318)
        self.assertEqual(self.coverage["records"]["prices"]["present"], 6)
        self.assertEqual(self.coverage["gaps"], [])

    def test_fifteen_pairs_have_expected_types_and_are_comparable(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 15)
        self.assertEqual(
            Counter(pair["pair_type"] for pair in pairs),
            Counter({"different_version_same_transmission": 12, "same_version_same_transmission": 3}),
        )
        self.assertEqual({pair["summary"]["technical"]["not_comparable"] for pair in pairs}, {0})
        self.assertEqual({pair["summary"]["equipment"]["not_comparable"] for pair in pairs}, {0})
        self.assertEqual({pair["summary"]["prices"]["not_comparable"] for pair in pairs}, {0})

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(
            self.comparison["summary"],
            {
                "prices": {"comparisons": 15, "equal": 0, "different": 15, "not_comparable": 0},
                "technical": {"comparisons": 360, "equal": 297, "different": 63, "not_comparable": 0},
                "equipment": {"comparisons": 795, "equal": 663, "different": 132, "not_comparable": 0},
                "total_differences": 210,
            },
        )

    def test_all_seventy_five_range_comparisons_preserve_interval_semantics(self) -> None:
        ranged = [
            item
            for pair in self.comparison["pairs"]
            for item in pair["technical"]
            if "minimum_value" in item["left"] or "minimum_value" in item["right"]
        ]
        self.assertEqual(len(ranged), 75)
        self.assertEqual(Counter(item["comparison"] for item in ranged), Counter({"equal": 66, "different": 9}))
        self.assertEqual(Counter(item.get("range_relation") for item in ranged), Counter({"identical": 66, "disjoint": 9}))
        for item in ranged:
            for side in ("left", "right"):
                self.assertIn("minimum_value", item[side])
                self.assertIn("maximum_value", item[side])
                self.assertNotIn("normalized_value", item[side])

    def test_empty_gap_evidence_remains_valid_and_all_prices_differ(self) -> None:
        self.assertEqual(self.comparison["evidence_summary"], {"total": 0, "ambiguous": 0, "found": 0, "not_stated": 0, "out_of_scope": 0})
        self.assertEqual(self.comparison["summary"]["prices"], {"comparisons": 15, "equal": 0, "different": 15, "not_comparable": 0})


if __name__ == "__main__":
    unittest.main()
