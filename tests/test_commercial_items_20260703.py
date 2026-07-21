from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

from reporting.commercial_offers import collect_commercial_components  # noqa: E402
from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402
from reporting.configuration_shortlist_html import collect_browser_catalog  # noqa: E402

MASTER = REPOSITORY / "data" / "master"
DATE = "2026-07-03"


def read(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class CommercialItems20260703Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = read("commercial_items.csv")
        cls.members = read("commercial_item_attributes.csv")
        cls.mappings = read("commercial_item_configurations.csv")
        cls.prices = read("configuration_prices.csv")
        cls.availability = read("configuration_attribute_availability.csv")

    def test_complete_source_backed_registration_counts(self) -> None:
        self.assertEqual(len(self.items), 27)
        self.assertEqual(len(self.members), 68)
        self.assertEqual(len(self.mappings), 86)
        self.assertEqual({row["observation_date"] for row in self.items}, {DATE})
        self.assertEqual({row["price_date"] for row in self.mappings}, {DATE})
        self.assertEqual({row["currency_code"] for row in self.mappings}, {"PLN"})
        self.assertEqual({row["availability_status"] for row in self.mappings}, {"optional"})

    def test_each_item_has_membership_and_source(self) -> None:
        item_codes = {row["code"] for row in self.items}
        member_codes = {row["commercial_item_code"] for row in self.members}
        self.assertEqual(item_codes, member_codes)
        self.assertEqual(
            {row["source_code"] for row in self.items},
            {
                "src_pl_sandero_stepway_price_my26_20260703",
                "src_pl_duster_price_my26_20260703",
                "src_pl_jogger_price_my26_20260703",
                "src_pl_bigster_price_my26_20260703",
            },
        )
        self.assertTrue(all(row["source_text"] for row in self.members))

    def test_bigster_items_are_registered_without_invented_configurations(self) -> None:
        bigster = {row["code"] for row in self.items if row["code"].startswith("bigster_")}
        mapped = {row["commercial_item_code"] for row in self.mappings}
        self.assertTrue(bigster)
        self.assertTrue(bigster.isdisjoint(mapped))

    def test_july_catalog_prices_cover_all_registered_configuration_relationships(self) -> None:
        source_codes = {
            "src_pl_sandero_stepway_price_my26_20260703",
            "src_pl_duster_price_my26_20260703",
            "src_pl_jogger_price_my26_20260703",
        }
        july = [
            row for row in self.prices
            if row["price_date"] == DATE and row["source_code"] in source_codes
        ]
        self.assertEqual(len(july), 39)
        self.assertEqual(len({row["configuration_code"] for row in july}), 39)

    def test_package_membership_updates_equipment_availability(self) -> None:
        latest = {}
        for row in self.availability:
            key = (row["configuration_code"], row["attribute_code"])
            if key not in latest or row["observation_date"] > latest[key]["observation_date"]:
                latest[key] = row
        expected_optional = (
            ("sandero_stepway_iii_expression_ecog120_automatic", "keyless_entry"),
            ("sandero_iii_journey_ecog120_manual", "heated_steering_wheel"),
            ("sandero_stepway_iii_extreme_ecog120_manual", "wireless_charging"),
            ("duster_iii_extreme_hybrid155_4x2_automatic", "adaptive_cruise_control"),
            ("jogger_extreme_5seat_ecog120_automatic", "side_mirrors_folding"),
        )
        for key in expected_optional:
            self.assertEqual(latest[key]["availability_status"], "optional")
            self.assertEqual(latest[key]["observation_date"], DATE)

    def test_browser_catalog_contains_real_price_components(self) -> None:
        catalog = collect_browser_catalog(REPOSITORY, ShortlistCriteria())
        by_code = {row["configuration_code"]: row for row in catalog["configurations"]}
        stepway = by_code["sandero_stepway_iii_expression_ecog120_automatic"]
        components = {row["code"]: row for row in stepway["price_components"]}
        self.assertEqual(stepway["catalog_price"]["price_date"], DATE)
        self.assertEqual(components["sandero_comfort_auto_package"]["amount"], 2000.0)
        self.assertIn("keyless_entry", components["sandero_comfort_auto_package"]["equipment_codes"])
        self.assertIn("—", stepway["display_name"])

    def test_commercial_loader_respects_historical_as_of(self) -> None:
        current = collect_commercial_components(
            REPOSITORY,
            ["sandero_stepway_iii_expression_ecog120_automatic"],
            DATE,
        )
        historical = collect_commercial_components(
            REPOSITORY,
            ["sandero_stepway_iii_expression_ecog120_automatic"],
            "2026-06-30",
        )
        self.assertTrue(current)
        self.assertEqual(historical, {})


if __name__ == "__main__":
    unittest.main()
