from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = "src_pl_jogger_price_my26_20261001"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPriceMatrixCorrection20261001Tests(unittest.TestCase):
    def test_source_page_one_seven_seat_ecog120_grade_alignment(self) -> None:
        prices = [r for r in rows("configuration_prices.csv") if r["source_code"] == SOURCE]
        by_config = {r["configuration_code"]: r for r in prices}
        # Official page 1: 7-seat Eco-G 120 manual = "-" / 86,550 / 94,400 PLN.
        self.assertNotIn("jogger_essential_7seat_ecog120_manual", by_config)
        self.assertEqual(by_config["jogger_expression_7seat_ecog120_manual"]["amount"], "86550")
        self.assertEqual(by_config["jogger_extreme_7seat_ecog120_manual"]["amount"], "94400")
        self.assertEqual(len(prices), 11)
        self.assertEqual(by_config["jogger_extreme_7seat_ecog120_automatic"]["amount"], "101300")
        self.assertEqual(by_config["jogger_expression_7seat_hybrid155_automatic"]["amount"], "108050")
        self.assertEqual(by_config["jogger_extreme_7seat_hybrid155_automatic"]["amount"], "115900")

    def test_source_relationships_cover_only_printed_configuration_matrix(self) -> None:
        configs = [r for r in rows("source_configurations.csv") if r["source_code"] == SOURCE]
        grades = [r for r in rows("source_versions.csv") if r["source_code"] == SOURCE]
        expected = {
            "jogger_essential_5seat_ecog120_manual", "jogger_expression_5seat_ecog120_manual",
            "jogger_extreme_5seat_ecog120_manual", "jogger_extreme_5seat_ecog120_automatic",
            "jogger_expression_5seat_hybrid155_automatic", "jogger_extreme_5seat_hybrid155_automatic",
            "jogger_essential_7seat_ecog120_manual", "jogger_expression_7seat_ecog120_manual",
            "jogger_extreme_7seat_ecog120_manual", "jogger_extreme_7seat_ecog120_automatic",
            "jogger_expression_7seat_hybrid155_automatic", "jogger_extreme_7seat_hybrid155_automatic",
        }
        self.assertEqual({r["configuration_code"] for r in configs}, expected)
        self.assertEqual(len(configs), 12)
        self.assertEqual({r["version_code"] for r in grades}, {
            "jogger_essential", "jogger_expression", "jogger_extreme"
        })
        self.assertEqual(len(grades), 3)

    def test_previous_price_history_is_retained(self) -> None:
        prices = rows("configuration_prices.csv")
        for date in ("2026-04-01", "2026-07-03"):
            historical = [
                r for r in prices
                if r["configuration_code"] == "jogger_essential_7seat_ecog120_manual"
                and r["price_date"] == date
            ]
            self.assertEqual(len(historical), 1)
            self.assertEqual(historical[0]["amount"], "82400")


if __name__ == "__main__":
    unittest.main()
