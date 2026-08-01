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
        counts = Counter()
        for group in report["review_groups"]:
            counts[group["classification"]] += group["row_count"]
        self.assertEqual(
            counts,
            Counter(
                {
                    "importable": 2,
                    "source-not-stated": 27,
                    "source-conflict": 2,
                    "context-unmodeled": 20,
                }
            ),
        )
        self.assertEqual(sum(counts.values()), report["scope"]["reviewed_gap_rows"])
        self.assertEqual(report["scope"]["data_mutations_applied"], 0)
        self.assertEqual(report["scope"]["models_or_domains_added"], 0)

    def test_active_comparison_review_closes_all_22_rows(self) -> None:
        groups = [
            group for group in payload(REPORT)["review_groups"]
            if group["area"] == "active-comparison"
        ]
        counts = Counter()
        for group in groups:
            counts[group["classification"]] += group["row_count"]
        self.assertEqual(
            counts,
            Counter({"source-not-stated": 20, "context-unmodeled": 2}),
        )
        contextual = [
            group for group in groups
            if group["classification"] == "context-unmodeled"
        ]
        self.assertEqual(len(contextual), 1)
        self.assertEqual(contextual[0]["item"], "gear_shift_indicator")
        self.assertEqual(contextual[0]["row_count"], 2)

    def test_only_two_current_spring_prices_are_importable(self) -> None:
        groups = [
            group for group in payload(REPORT)["review_groups"]
            if group["classification"] == "importable"
        ]
        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group["configuration_code"], "spring_extreme_electric100_automatic")
        self.assertEqual(group["candidate_source_code"], "src_pl_spring_official_configurator_20260731")
        self.assertEqual(
            {item: amount for item, amount in group["rows"]},
            {"spring_city_package": 1800, "spring_power_package": 3000},
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
