from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SpringExpressionFlexiChargerCorrectionTests(unittest.TestCase):
    def test_expression_mapping_is_exact_and_priced(self) -> None:
        path = ROOT / "data/master/commercial_item_configurations.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        matches = [
            row
            for row in rows
            if row["code"]
            == "spring_domestic_socket_charging_cable_option__spring_expression_electric70_automatic"
        ]
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual(row["availability_status"], "optional")
        self.assertEqual(row["amount"], "1500")
        self.assertEqual(row["currency_code"], "PLN")
        self.assertEqual(row["price_date"], "2026-07-08")
        self.assertEqual(row["source_code"], "src_pl_spring_price_my25_stock_20260708")

    def test_all_three_spring_grades_have_domestic_cable_mapping(self) -> None:
        path = ROOT / "data/master/commercial_item_configurations.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        mappings = {
            row["configuration_code"]: (row["availability_status"], row["amount"])
            for row in rows
            if row["commercial_item_code"]
            == "spring_domestic_socket_charging_cable_option"
        }
        self.assertEqual(
            mappings,
            {
                "spring_essential_electric70_automatic": ("optional", "1500"),
                "spring_expression_electric70_automatic": ("optional", "1500"),
                "spring_extreme_electric100_automatic": ("optional", "1500"),
            },
        )


if __name__ == "__main__":
    unittest.main()
