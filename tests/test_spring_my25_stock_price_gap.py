from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringMy25StockPriceGapTests(unittest.TestCase):
    def test_extreme_electric100_price_is_linked_to_exact_stock_price_list(self) -> None:
        source_code = "src_pl_spring_price_my25_stock_20260708"
        configuration = "spring_extreme_electric100_automatic"

        prices = [
            row for row in rows("configuration_prices.csv")
            if row["source_code"] == source_code
            and row["configuration_code"] == configuration
            and row["price_type"] == "catalog_gross"
        ]
        self.assertEqual(len(prices), 1)
        self.assertEqual(
            (
                prices[0]["amount"],
                prices[0]["currency_code"],
                prices[0]["price_date"],
                prices[0]["code"],
            ),
            (
                "85900",
                "PLN",
                "2026-07-08",
                "spring_extreme_electric100_automatic_pl_20260708",
            ),
        )

        links = [
            row for row in rows("source_configurations.csv")
            if row["source_code"] == source_code
            and row["configuration_code"] == configuration
        ]
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["relationship"], "documents")
        self.assertIn("page 1", links[0]["notes"])

    def test_price_list_scope_does_not_leak_into_my26(self) -> None:
        source = next(
            row for row in rows("sources.csv")
            if row["code"] == "src_pl_spring_price_my25_stock_20260708"
        )
        self.assertEqual(source["document_date"], "2026-07-08")
        self.assertIn("MY25 dealer-stock scope", source["notes"])
        self.assertIn("No generalization to MY26", source["notes"])


if __name__ == "__main__":
    unittest.main()
