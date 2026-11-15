from __future__ import annotations

import csv
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = "src_pl_spring_price_my26_20260206"
CONFIGS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}
sys.path.insert(0, str(ROOT / "tools"))
import import_spring_my26_price_commercial_matrix_20260206 as importer


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class SpringMY26PriceCommercialMatrixTests(unittest.TestCase):
    def test_importer_contract_and_scoped_totals(self):
        self.assertEqual(importer.check(), {
            "price_rows": 3,
            "commercial_mappings": 10,
            "source_configuration_links": 3,
            "source_grade_links": 3,
        })

    def test_source_identity_and_exact_configuration_boundary(self):
        source = next(row for row in rows("sources.csv") if row["code"] == SOURCE)
        self.assertEqual(source["document_date"], "2026-02-06")
        self.assertEqual(source["sha256"], importer.SOURCE_SHA256)
        self.assertEqual(source["file_path"], importer.SOURCE_PATH)
        self.assertEqual(source["external_reference"], importer.SOURCE_URL)
        links = [row for row in rows("source_configurations.csv") if row["source_code"] == SOURCE]
        self.assertEqual({row["configuration_code"] for row in links}, CONFIGS)
        grades = [row for row in rows("source_versions.csv") if row["source_code"] == SOURCE]
        self.assertEqual({row["version_code"] for row in grades}, {
            "spring_essential", "spring_expression", "spring_extreme"
        })

    def test_exact_price_cells_and_label_ambiguity_are_preserved(self):
        prices = [row for row in rows("configuration_prices.csv") if row["source_code"] == SOURCE]
        self.assertEqual({row["configuration_code"]: row["amount"] for row in prices}, {
            "spring_essential_electric70_automatic": "73500",
            "spring_expression_electric70_automatic": "81500",
            "spring_extreme_electric100_automatic": "85900",
        })
        self.assertTrue(all(row["price_type"] == "catalog_gross" for row in prices))
        self.assertTrue(all(row["price_date"] == "2026-02-06" for row in prices))
        self.assertTrue(all("Cena promocyjna" in row["notes"] for row in prices))
        self.assertTrue(all("catalogue prices" in row["notes"] for row in prices))

    def test_exact_commercial_matrix_values_and_applicability(self):
        mappings = [row for row in rows("commercial_item_configurations.csv") if row["source_code"] == SOURCE]
        self.assertEqual(len(mappings), 10)
        self.assertEqual(Counter((row["commercial_item_code"], row["amount"]) for row in mappings), Counter({
            ("spring_colour_lichen_khaki", "2300"): 3,
            ("spring_domestic_socket_charging_cable_option", "1500"): 3,
            ("spring_dc40_charging_option", "2750"): 1,
            ("spring_techno_package", "3500"): 1,
            ("spring_city_package", "1800"): 1,
            ("spring_power_package", "3000"): 1,
        }))
        self.assertEqual({row["configuration_code"] for row in mappings
                          if row["commercial_item_code"] == "spring_colour_lichen_khaki"}, CONFIGS)
        self.assertEqual({row["configuration_code"] for row in mappings
                          if row["commercial_item_code"] == "spring_domestic_socket_charging_cable_option"}, CONFIGS)
        self.assertEqual({row["configuration_code"] for row in mappings
                          if row["commercial_item_code"] == "spring_dc40_charging_option"},
                         {"spring_expression_electric70_automatic"})
        self.assertFalse(any(row["commercial_item_code"] == "spring_dc40_charging_option"
                             and row["configuration_code"] == "spring_extreme_electric100_automatic"
                             for row in mappings))

    def test_historical_my25_and_later_observations_remain_separate(self):
        prices = rows("configuration_prices.csv")
        old_extreme = [row for row in prices if row["configuration_code"] == "spring_extreme_electric100_automatic"
                       and row["source_code"] == "src_pl_spring_price_my25_stock_20260708"]
        self.assertEqual(len(old_extreme), 1)
        self.assertEqual((old_extreme[0]["amount"], old_extreme[0]["price_date"]), ("85900", "2026-07-08"))
        mappings = rows("commercial_item_configurations.csv")
        khaki_current = [row for row in mappings if row["code"] == "spring_colour_lichen_khaki__spring_essential_electric70_automatic"]
        self.assertEqual(len(khaki_current), 1)
        self.assertEqual((khaki_current[0]["amount"], khaki_current[0]["price_date"],
                          khaki_current[0]["source_code"]), ("2300", "2026-08-02", "src_pl_spring_commercial_context_20260802"))
        expression_my25 = [row for row in mappings if row["configuration_code"] == "spring_expression_electric70_automatic"
                           and row["commercial_item_code"] == "spring_domestic_socket_charging_cable_option"
                           and row["source_code"] == "src_pl_spring_price_my25_stock_20260708"]
        self.assertEqual(len(expression_my25), 1)

    def test_ambiguous_p_cells_and_technical_conflict_are_not_imported(self):
        mappings = [row for row in rows("commercial_item_configurations.csv") if row["source_code"] == SOURCE]
        self.assertFalse(any(row["availability_status"] in {"standard", "not_available", "unknown"}
                             for row in mappings))
        self.assertFalse(any(row["configuration_code"] == "spring_extreme_electric100_automatic"
                             and row["commercial_item_code"] == "spring_dc40_charging_option"
                             for row in mappings))
        values = rows("configuration_attribute_values.csv")
        self.assertFalse(any(row["source_code"] == SOURCE for row in values))

    def test_ids_and_codes_remain_unique(self):
        for table in ("configuration_prices.csv", "commercial_item_configurations.csv",
                      "source_configurations.csv", "source_versions.csv"):
            data = rows(table)
            self.assertEqual(len({row["id"] for row in data}), len(data), table)
        prices = rows("configuration_prices.csv")
        self.assertEqual(len({row["code"] for row in prices}), len(prices))
        mappings = rows("commercial_item_configurations.csv")
        self.assertEqual(len({row["code"] for row in mappings}), len(mappings))


if __name__ == "__main__":
    unittest.main()
