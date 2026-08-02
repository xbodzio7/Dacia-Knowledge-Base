import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringChargingCableCommercialSemanticsMigrationTests(unittest.TestCase):
    def test_type2_membership_and_history(self):
        memberships = rows("data/master/commercial_item_attributes.csv")
        row = next(
            item
            for item in memberships
            if item["commercial_item_code"] == "spring_type2_charging_cable_option"
        )
        self.assertEqual(row["attribute_code"], "type2_charging_cable_supplied")
        mappings = [
            item
            for item in rows("data/master/commercial_item_configurations.csv")
            if item["commercial_item_code"] == "spring_type2_charging_cable_option"
        ]
        self.assertEqual(len(mappings), 3)
        self.assertTrue(
            all(
                item["availability_status"] == "optional"
                and item["source_code"] == "src_pl_spring_brochure_20260219"
                for item in mappings
            )
        )

    def test_domestic_socket_exact_boundary(self):
        items = {item["code"]: item for item in rows("data/master/commercial_items.csv")}
        self.assertIn("spring_domestic_socket_charging_cable_option", items)
        memberships = {
            item["commercial_item_code"]: item
            for item in rows("data/master/commercial_item_attributes.csv")
        }
        self.assertEqual(
            memberships["spring_domestic_socket_charging_cable_option"]["attribute_code"],
            "domestic_socket_charging_cable",
        )
        mappings = [
            item
            for item in rows("data/master/commercial_item_configurations.csv")
            if item["commercial_item_code"]
            == "spring_domestic_socket_charging_cable_option"
        ]
        by_configuration = {item["configuration_code"]: item for item in mappings}
        self.assertEqual(
            set(by_configuration),
            {
                "spring_essential_electric70_automatic",
                "spring_expression_electric70_automatic",
                "spring_extreme_electric100_automatic",
            },
        )
        for configuration in (
            "spring_essential_electric70_automatic",
            "spring_extreme_electric100_automatic",
        ):
            item = by_configuration[configuration]
            self.assertEqual(item["availability_status"], "optional")
            self.assertEqual(item["amount"], "1500")
            self.assertEqual(item["currency_code"], "PLN")
            self.assertEqual(item["price_date"], "2026-08-02")
            self.assertEqual(item["source_code"], "src_pl_spring_commercial_context_20260802")
        expression = by_configuration["spring_expression_electric70_automatic"]
        self.assertEqual(expression["availability_status"], "optional")
        self.assertEqual(expression["amount"], "1500")
        self.assertEqual(expression["currency_code"], "PLN")
        self.assertEqual(expression["price_date"], "2026-07-08")
        self.assertEqual(expression["source_code"], "src_pl_spring_price_my25_stock_20260708")


if __name__ == "__main__":
    unittest.main()
