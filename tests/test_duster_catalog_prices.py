from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE_CODE = "src_pl_duster_price_my26_py25_20260206"

EXPECTED = {
    "duster_iii_essential_ecog100_4x2_manual": 82000,
    "duster_iii_expression_ecog100_4x2_manual": 90000,
    "duster_iii_extreme_ecog100_4x2_manual": 96000,
    "duster_iii_journey_ecog100_4x2_manual": 96000,
    "duster_iii_expression_mildhybrid130_4x2_manual": 97600,
    "duster_iii_extreme_mildhybrid130_4x2_manual": 103600,
    "duster_iii_journey_mildhybrid130_4x2_manual": 103800,
    "duster_iii_expression_hybrid140_4x2_automatic": 112100,
    "duster_iii_extreme_hybrid140_4x2_automatic": 118100,
    "duster_iii_journey_hybrid140_4x2_automatic": 118300,
    "duster_iii_journey_plus_hybrid140_4x2_automatic": 123600,
    "duster_iii_expression_mildhybrid130_4x4_manual": 111900,
    "duster_iii_extreme_mildhybrid130_4x4_manual": 117900,
    "duster_iii_journey_mildhybrid130_4x4_manual": 117900,
    "duster_iii_essential_ecog120_4x2_manual": 82000,
    "duster_iii_expression_ecog120_4x2_manual": 90000,
    "duster_iii_extreme_ecog120_4x2_manual": 96000,
    "duster_iii_journey_ecog120_4x2_manual": 96200,
    "duster_iii_expression_mildhybrid140_4x2_manual": 97600,
    "duster_iii_extreme_mildhybrid140_4x2_manual": 103600,
    "duster_iii_journey_mildhybrid140_4x2_manual": 103800,
    "duster_iii_expression_hybrid155_4x2_automatic": 112100,
    "duster_iii_extreme_hybrid155_4x2_automatic": 118100,
    "duster_iii_journey_hybrid155_4x2_automatic": 118300,
}


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterCatalogPriceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.all_prices = rows("configuration_prices.csv")
        cls.prices = [row for row in cls.all_prices if row["source_code"] == SOURCE_CODE]
        cls.configurations = {row["code"] for row in rows("configurations.csv")}

    def test_exact_twenty_four_source_supported_prices(self) -> None:
        self.assertEqual(len(self.prices), 24)
        self.assertEqual(
            {row["configuration_code"]: int(row["amount"]) for row in self.prices},
            EXPECTED,
        )

    def test_prices_use_canonical_market_type_currency_and_date(self) -> None:
        self.assertEqual({row["market"] for row in self.prices}, {"PL"})
        self.assertEqual({row["price_type"] for row in self.prices}, {"catalog_gross"})
        self.assertEqual({row["currency_code"] for row in self.prices}, {"PLN"})
        self.assertEqual({row["price_date"] for row in self.prices}, {"2026-02-06"})

    def test_every_price_references_an_existing_bootstrap_configuration(self) -> None:
        self.assertEqual(set(EXPECTED), {row["configuration_code"] for row in self.prices})
        self.assertLessEqual(set(EXPECTED), self.configurations)

    def test_codes_are_unique_and_deterministic(self) -> None:
        codes = [row["code"] for row in self.prices]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(
            set(codes),
            {f"{configuration}_pl_20260206" for configuration in EXPECTED},
        )

    def test_notes_preserve_scope_and_exclude_promotions(self) -> None:
        notes = {row["notes"] for row in self.prices}
        self.assertEqual(
            notes,
            {"Source page 1, ROCZNIK 2025; catalogue gross price. Promotional discount and financing claims excluded."},
        )
        imported_amounts = {int(row["amount"]) for row in self.prices}
        self.assertNotIn(10000, imported_amounts)
        self.assertNotIn(18000, imported_amounts)

    def test_existing_sandero_prices_remain_unchanged(self) -> None:
        sandero = [row for row in self.all_prices if row["configuration_code"].startswith("sandero")]
        self.assertEqual(len(sandero), 7)
        self.assertEqual({row["price_date"] for row in sandero}, {"2026-06-26"})


if __name__ == "__main__":
    unittest.main()
