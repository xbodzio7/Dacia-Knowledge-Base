from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/registered_source_completeness_reconciliation.json"


def payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class RegisteredSourceCompletenessReconciliationTests(unittest.TestCase):
    def test_every_reviewed_gap_has_one_terminal_classification(self) -> None:
        report = payload(REPORT)
        decisions = report["decisions"]
        self.assertEqual(len(decisions), 51)
        self.assertEqual(
            Counter(item["classification"] for item in decisions),
            Counter(
                {
                    "importable": 2,
                    "source-not-stated": 27,
                    "source-conflict": 2,
                    "context-unmodeled": 20,
                }
            ),
        )
        self.assertEqual(report["scope"]["data_mutations_applied"], 0)
        self.assertEqual(report["scope"]["models_or_domains_added"], 0)

    def test_active_comparison_review_closes_all_22_rows(self) -> None:
        report = payload(REPORT)
        decisions = [
            item for item in report["decisions"]
            if item["gap_type"] == "active-comparison"
        ]
        self.assertEqual(len(decisions), 22)
        self.assertEqual(
            Counter(item["classification"] for item in decisions),
            Counter({"source-not-stated": 20, "context-unmodeled": 2}),
        )
        contextual = [
            item for item in decisions
            if item["classification"] == "context-unmodeled"
        ]
        self.assertEqual(
            {item["attribute_code"] for item in contextual},
            {"gear_shift_indicator"},
        )

    def test_only_two_current_spring_prices_are_importable(self) -> None:
        report = payload(REPORT)
        importable = {
            (item["commercial_item_code"], item["configuration_code"]): item
            for item in report["decisions"]
            if item["classification"] == "importable"
        }
        expected = {
            (
                "spring_city_package",
                "spring_extreme_electric100_automatic",
            ): 1800,
            (
                "spring_power_package",
                "spring_extreme_electric100_automatic",
            ): 3000,
        }
        self.assertEqual(set(importable), set(expected))
        for key, amount in expected.items():
            self.assertEqual(importable[key]["candidate_amount_pln"], amount)
            self.assertEqual(
                importable[key]["candidate_source_code"],
                "src_pl_spring_official_configurator_20260731",
            )

    def test_project_state_advances_to_materialization_package(self) -> None:
        state = payload(ROOT / "project/state.json")
        self.assertEqual(
            state["current_package"]["package_id"],
            "registered_source_completeness_reconciliation_001",
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["package_id"],
            "reviewed_gap_state_materialization_001",
        )
        self.assertEqual(state["reference_delivery"]["pull_request"], 447)
        self.assertEqual(state["baseline"]["tests"], 1782)


if __name__ == "__main__":
    unittest.main()
