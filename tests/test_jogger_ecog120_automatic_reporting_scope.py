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
SPEC = REPOSITORY / "data/reporting/jogger_ecog120_automatic_completeness.json"
EVIDENCE = REPOSITORY / "data/reporting/jogger_ecog120_automatic_gap_evidence.spec"
CONFIGURATIONS = {
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_extreme_7seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "jogger_journey_7seat_ecog120_automatic",
}


class JoggerEcoG120AutomaticReportingScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.completeness = completeness.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.coverage = source_coverage.collect_report(REPOSITORY, SPEC, AS_OF)
        cls.comparison = comparison.collect_report(REPOSITORY, SPEC, EVIDENCE, AS_OF)

    def test_scope_selects_exactly_four_configurations_and_denominators(self) -> None:
        scope = self.completeness["scope"]
        self.assertEqual(set(scope["reporting_configuration_codes"]), CONFIGURATIONS)
        self.assertEqual(scope["reporting_configurations"], 4)
        self.assertEqual(scope["technical_slots"], 34)
        self.assertEqual(scope["equipment_attributes"], 53)
        self.assertEqual(scope["sources"], 1)

    def test_completeness_is_exact_and_gap_free(self) -> None:
        self.assertEqual(
            self.completeness["technical"],
            {
                "applicable": 136,
                "coverage_percent": "100.00",
                "denominator": 136,
                "missing": 0,
                "not_applicable": 0,
                "present": 136,
            },
        )
        self.assertEqual(
            self.completeness["equipment"],
            {
                "applicable": 212,
                "coverage_percent": "100.00",
                "denominator": 212,
                "missing": 0,
                "not_applicable": 0,
                "not_available": 20,
                "optional": 14,
                "recorded": 212,
                "standard": 178,
                "unknown": 0,
            },
        )
        self.assertEqual(self.completeness["gaps"], {"equipment": [], "technical": []})

    def test_source_coverage_is_complete_for_technical_equipment_and_prices(self) -> None:
        self.assertEqual(
            self.coverage["source_registration"],
            {"expected": 1, "future": 0, "inactive": 0, "metadata_complete": 1, "missing": 0, "registered": 1},
        )
        self.assertEqual(self.coverage["areas"], {"covered": 16, "denominator": 16, "missing": 0, "partial": 0, "source_missing": 0})
        self.assertEqual(self.coverage["sections"], {"covered": 108, "denominator": 108, "missing": 0, "not_applicable": 0, "partial": 0, "source_missing": 0})
        self.assertEqual(self.coverage["records"]["technical"]["present"], 136)
        self.assertEqual(self.coverage["records"]["equipment"]["present"], 212)
        self.assertEqual(self.coverage["records"]["prices"]["present"], 4)
        self.assertEqual(self.coverage["gaps"], [])

    def test_six_pairs_have_expected_types_and_are_comparable(self) -> None:
        pairs = self.comparison["pairs"]
        self.assertEqual(len(pairs), 6)
        self.assertEqual(
            Counter(pair["pair_type"] for pair in pairs),
            Counter({"different_version_same_transmission": 4, "same_version_same_transmission": 2}),
        )
        self.assertEqual({pair["summary"]["technical"]["not_comparable"] for pair in pairs}, {0})
        self.assertEqual({pair["summary"]["equipment"]["not_comparable"] for pair in pairs}, {0})
        self.assertEqual({pair["summary"]["prices"]["not_comparable"] for pair in pairs}, {0})

    def test_comparison_summary_is_stable(self) -> None:
        self.assertEqual(
            self.comparison["summary"],
            {
                "prices": {"comparisons": 6, "equal": 0, "different": 6, "not_comparable": 0},
                "technical": {"comparisons": 204, "equal": 172, "different": 32, "not_comparable": 0},
                "equipment": {"comparisons": 318, "equal": 282, "different": 36, "not_comparable": 0},
                "total_differences": 74,
            },
        )

    def test_all_fifty_four_range_comparisons_preserve_interval_semantics(self) -> None:
        ranged = [
            item
            for pair in self.comparison["pairs"]
            for item in pair["technical"]
            if "minimum_value" in item["left"] or "minimum_value" in item["right"]
        ]
        self.assertEqual(len(ranged), 54)
        self.assertEqual(Counter(item["comparison"] for item in ranged), Counter({"equal": 50, "different": 4}))
        self.assertTrue(all(item.get("range_relation") in {"identical", "overlapping", "disjoint"} for item in ranged))
        for item in ranged:
            for side in ("left", "right"):
                self.assertIn("minimum_value", item[side])
                self.assertIn("maximum_value", item[side])
                self.assertNotIn("normalized_value", item[side])

    def test_empty_gap_evidence_remains_valid_and_all_prices_differ(self) -> None:
        self.assertEqual(self.comparison["evidence_summary"], {"total": 0, "ambiguous": 0, "found": 0, "not_stated": 0, "out_of_scope": 0})
        self.assertEqual(sum(pair["summary"]["prices"]["different"] for pair in self.comparison["pairs"]), 6)


if __name__ == "__main__":
    unittest.main()
