import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class BigsterSeptemberPriceListDeltaTests(unittest.TestCase):
    def test_bigster_september_2026_price_list_delta(self):
        cfg = rows(ROOT / "data/master/configurations.csv")
        prices = rows(ROOT / "data/master/configuration_prices.csv")
        availability = rows(ROOT / "data/master/configuration_attribute_availability.csv")
        values = rows(ROOT / "data/master/configuration_attribute_values.csv")
        sources = rows(ROOT / "data/master/sources.csv")
        source = "src_pl_bigster_price_my26_20260901"
        expected_prices = {
            "bigster_expression_mildhybridg140_4x2_automatic": 115600,
            "bigster_extreme_mildhybridg140_4x2_automatic": 124100,
            "bigster_journey_mildhybridg140_4x2_automatic": 123700,
        }

        self.assertEqual(
            {row["configuration_code"] for row in cfg
             if row["configuration_code"] in expected_prices},
            set(expected_prices),
        )
        source_prices = {
            row["configuration_code"]: row
            for row in prices
            if row["source_code"] == source
        }
        for code, amount in expected_prices.items():
            with self.subTest(configuration=code):
                self.assertIn(code, source_prices)
                self.assertEqual(int(source_prices[code]["amount"]), amount)
                scoped_availability = [
                    row for row in availability
                    if row["configuration_code"] == code
                    and row["source_code"] == source
                ]
                self.assertGreater(len(scoped_availability), 50)
                self.assertTrue(all("Source page 4–5" in row["notes"]
                                    for row in scoped_availability))
                self.assertTrue(any(
                    row["configuration_code"] == code
                    and row["attribute_code"] == "gearbox_type"
                    and row["value"] == "automatic"
                    and row["source_code"] == source
                    for row in values
                ))
                self.assertTrue(any(
                    row["configuration_code"] == code
                    and row["attribute_code"] == "fuel_consumption_combined"
                    and row["fuel_type_code"] == "lpg"
                    and row["value"] == "7.3"
                    and row["source_code"] == source
                    and "Source page 6" in row["notes"]
                    for row in values
                ))
        self.assertTrue(any(
            row["code"] == source and row["document_date"] == "2026-09-01"
            for row in sources
        ))


if __name__ == "__main__":
    unittest.main()
