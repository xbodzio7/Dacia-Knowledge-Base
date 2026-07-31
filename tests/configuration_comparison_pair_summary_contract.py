from __future__ import annotations

import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from tools import configuration_comparison as comparison
from tools import configuration_comparison_pair_summary as pair_summary

REPOSITORY = Path(__file__).resolve().parents[1]


class ConfigurationComparisonPairSummaryContractTests(unittest.TestCase):
    def test_pair_summary_rows_flatten_context_and_counts(self) -> None:
        report = {
            "pairs": [
                {
                    "left_configuration_code": "cfg_left",
                    "right_configuration_code": "cfg_right",
                    "pair_type": "same_version_different_transmission",
                    "summary": {
                        "all": {
                            "comparisons": 10,
                            "different": 3,
                            "equal": 5,
                            "not_comparable": 2,
                        },
                        "price": {
                            "comparisons": 1,
                            "different": 1,
                            "equal": 0,
                            "not_comparable": 0,
                        },
                        "technical": {
                            "comparisons": 6,
                            "different": 2,
                            "equal": 3,
                            "not_comparable": 1,
                        },
                        "equipment": {
                            "comparisons": 3,
                            "different": 0,
                            "equal": 2,
                            "not_comparable": 1,
                        },
                    },
                    "differences": [
                        {
                            "state": "different",
                            "domain": "technical",
                            "item_code": "engine_power",
                            "left_context": {
                                "fuel_type_code": "lpg",
                                "market": "PL",
                            },
                            "right_context": {
                                "fuel_type_code": "petrol",
                                "market": "PL",
                            },
                        },
                        {
                            "state": "different",
                            "domain": "price",
                            "item_code": "list_price",
                            "left_context": {"market": "PL", "currency_code": "PLN"},
                            "right_context": {"market": "PL", "currency_code": "PLN"},
                        },
                        {
                            "state": "equal",
                            "domain": "equipment",
                            "item_code": "rear_parking_sensors",
                            "left_context": {},
                            "right_context": {},
                        },
                    ],
                }
            ]
        }

        rows = pair_summary.pair_summary_rows(report)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["left_configuration_code"], "cfg_left")
        self.assertEqual(row["right_configuration_code"], "cfg_right")
        self.assertEqual(row["pair_type"], "same_version_different_transmission")
        self.assertEqual(row["total_comparisons"], "10")
        self.assertEqual(row["total_different"], "3")
        self.assertEqual(row["price_different"], "1")
        self.assertEqual(row["technical_different"], "2")
        self.assertEqual(row["equipment_different"], "0")
        self.assertEqual(row["different_items"], "price:list_price;technical:engine_power")
        self.assertEqual(row["different_contexts"], "fuel_type_code=lpg;market=PL | fuel_type_code=petrol;market=PL;market=PL;currency_code=PLN")

    def test_write_pair_summary_uses_stable_field_order(self) -> None:
        report = {
            "pairs": [
                {
                    "left_configuration_code": "cfg_left",
                    "right_configuration_code": "cfg_right",
                    "pair_type": "same_version_different_transmission",
                    "summary": {
                        "all": {"comparisons": 1, "different": 0, "equal": 1, "not_comparable": 0},
                        "price": {"comparisons": 0, "different": 0, "equal": 0, "not_comparable": 0},
                        "technical": {"comparisons": 1, "different": 0, "equal": 1, "not_comparable": 0},
                        "equipment": {"comparisons": 0, "different": 0, "equal": 0, "not_comparable": 0},
                    },
                    "differences": [],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "pair-summary.csv"
            pair_summary.write_pair_summary(report, output)
            with output.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(list(rows[0]), pair_summary.PAIR_SUMMARY_FIELDS)
            self.assertEqual(len(rows), 1)

    def test_repository_snapshot_has_21_pairs_and_expected_types(self) -> None:
        report = comparison.collect_report(
            REPOSITORY,
            REPOSITORY / comparison.DEFAULT_COMPLETENESS_SPEC,
            REPOSITORY / comparison.DEFAULT_EVIDENCE_SPEC,
        )
        rows = pair_summary.pair_summary_rows(report)
        self.assertEqual(len(rows), 21)
        self.assertEqual(
            Counter(row["pair_type"] for row in rows),
            Counter(
                {
                    "different_version_same_transmission": 11,
                    "different_version_different_transmission": 8,
                    "same_version_different_transmission": 2,
                }
            ),
        )
        self.assertEqual(
            {row["total_comparisons"] for row in rows},
            {"135", "137", "139"},
        )
        self.assertEqual(
            sum(int(row["total_different"]) for row in rows),
            365,
        )
        self.assertEqual(
            sum(int(row["price_different"]) for row in rows),
            report["summary"]["prices"]["different"],
        )
        self.assertEqual(
            sum(int(row["technical_different"]) for row in rows),
            report["summary"]["technical"]["different"],
        )
        self.assertEqual(
            sum(int(row["equipment_different"]) for row in rows),
            report["summary"]["equipment"]["different"],
        )


if __name__ == "__main__":
    unittest.main()
