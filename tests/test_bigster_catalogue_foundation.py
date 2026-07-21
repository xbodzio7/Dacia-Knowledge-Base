from __future__ import annotations

import csv
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
SOURCE = "src_pl_bigster_price_my26_20260703"
DATE = "2026-07-03"


def read(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterCatalogueFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.versions = read("versions.csv")
        cls.configurations = read("configurations.csv")
        cls.prices = read("configuration_prices.csv")
        cls.source_versions = read("source_versions.csv")
        cls.source_configurations = read("source_configurations.csv")

    def test_four_source_backed_versions(self) -> None:
        rows = [row for row in self.versions if row["model_code"] == "bigster"]
        self.assertEqual(
            {(row["code"], row["name"]) for row in rows},
            {
                ("bigster_essential", "Essential"),
                ("bigster_expression", "Expression"),
                ("bigster_extreme", "Extreme"),
                ("bigster_journey", "Journey"),
            },
        )

    def test_fourteen_non_empty_price_matrix_configurations(self) -> None:
        rows = [row for row in self.configurations if row["version_code"].startswith("bigster_")]
        self.assertEqual(len(rows), 14)
        self.assertEqual(sum(row["transmission_type"] == "manual" for row in rows), 8)
        self.assertEqual(sum(row["transmission_type"] == "automatic" for row in rows), 6)

    def test_unavailable_essential_hybrid_cells_are_not_modeled(self) -> None:
        codes = {row["code"] for row in self.configurations}
        self.assertNotIn("bigster_essential_hybrid155_4x2_automatic", codes)
        self.assertNotIn("bigster_essential_hybridg150_4x4_automatic", codes)

    def test_exact_catalogue_prices(self) -> None:
        rows = {
            row["configuration_code"]: int(row["amount"])
            for row in self.prices
            if row["source_code"] == SOURCE and row["price_date"] == DATE
        }
        self.assertEqual(len(rows), 14)
        self.assertEqual(rows["bigster_essential_mildhybrid140_4x2_manual"], 101400)
        self.assertEqual(rows["bigster_expression_hybrid155_4x2_automatic"], 124900)
        self.assertEqual(rows["bigster_extreme_hybridg150_4x4_automatic"], 137600)
        self.assertEqual(rows["bigster_journey_hybridg150_4x4_automatic"], 137200)

    def test_source_relationships_cover_every_version_and_configuration(self) -> None:
        version_codes = {
            row["version_code"] for row in self.source_versions if row["source_code"] == SOURCE
        }
        configuration_codes = {
            row["configuration_code"]
            for row in self.source_configurations
            if row["source_code"] == SOURCE
        }
        self.assertEqual(version_codes, {
            "bigster_essential", "bigster_expression", "bigster_extreme", "bigster_journey"
        })
        self.assertEqual(len(configuration_codes), 14)


if __name__ == "__main__":
    unittest.main()
