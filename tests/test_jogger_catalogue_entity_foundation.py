from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = "src_pl_jogger_price_my26_20260401"
DATE = "2026-04-01"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerCatalogueEntityFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.configurations = {
            row["code"]: row
            for row in rows("configurations.csv")
            if row["code"].startswith("jogger_")
        }

    def test_source_is_registered_with_exact_provenance_boundary(self) -> None:
        source = next(row for row in rows("sources.csv") if row["code"] == SOURCE)
        self.assertEqual(source["market"], "PL")
        self.assertEqual(source["document_date"], DATE)
        self.assertEqual(
            source["sha256"],
            "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b",
        )
        self.assertEqual(
            source["file_path"],
            "PDF/Cenniki/DACIA JOGGER cennik MY26 20260401.pdf",
        )
        self.assertIn("archive pending", source["notes"])

    def test_four_versions_and_twenty_two_configurations_are_exact(self) -> None:
        versions = {
            row["code"]
            for row in rows("versions.csv")
            if row["model_code"] == "jogger" and row["status"] == "active"
        }
        self.assertEqual(
            versions,
            {"jogger_essential", "jogger_expression", "jogger_extreme", "jogger_journey"},
        )
        self.assertEqual(len(self.configurations), 22)
        self.assertEqual(
            sum("_5seat_" in code for code in self.configurations), 11
        )
        self.assertEqual(
            sum("_7seat_" in code for code in self.configurations), 11
        )
        self.assertTrue(
            all("seat" not in row["powertrain_label"].casefold() for row in self.configurations.values())
        )

    def test_source_relationships_cover_the_complete_catalogue(self) -> None:
        self.assertIn(
            (SOURCE, "jogger"),
            {(row["source_code"], row["model_code"]) for row in rows("source_models.csv")},
        )
        version_pairs = {
            (row["source_code"], row["version_code"])
            for row in rows("source_versions.csv")
            if row["source_code"] == SOURCE
        }
        self.assertEqual(len(version_pairs), 4)
        configuration_pairs = {
            (row["source_code"], row["configuration_code"])
            for row in rows("source_configurations.csv")
            if row["source_code"] == SOURCE
        }
        self.assertEqual(
            configuration_pairs,
            {(SOURCE, code) for code in self.configurations},
        )

    def test_twenty_two_catalogue_prices_match_page_one(self) -> None:
        prices = {
            row["configuration_code"]: int(row["amount"])
            for row in rows("configuration_prices.csv")
            if row["source_code"] == SOURCE
        }
        self.assertEqual(len(prices), 22)
        self.assertEqual(prices["jogger_essential_5seat_ecog120_manual"], 77900)
        self.assertEqual(prices["jogger_journey_7seat_hybrid155_automatic"], 118050)
        scoped = [
            row for row in rows("configuration_prices.csv") if row["source_code"] == SOURCE
        ]
        self.assertTrue(all(row["market"] == "PL" for row in scoped))
        self.assertTrue(all(row["price_type"] == "catalog_gross" for row in scoped))
        self.assertTrue(all(row["currency_code"] == "PLN" for row in scoped))
        self.assertTrue(all(row["price_date"] == DATE for row in scoped))

    def test_seat_count_is_an_explicit_dated_observation(self) -> None:
        values = {
            row["configuration_code"]: row
            for row in rows("configuration_attribute_values.csv")
            if row["source_code"] == SOURCE and row["attribute_code"] == "number_of_seats"
        }
        self.assertEqual(set(values), set(self.configurations))
        for code, row in values.items():
            self.assertEqual(row["value"], "5" if "_5seat_" in code else "7")
            self.assertEqual(row["observation_date"], DATE)
            self.assertEqual(row["fuel_type_code"], "")



if __name__ == "__main__":
    unittest.main()
