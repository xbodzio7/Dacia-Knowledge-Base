from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
IMPORT = ROOT / "data" / "imports" / "striker_my26_configuration_prices_20261102.csv"
SOURCE = "src_pl_striker_price_my26_20261102"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class StrikerMy26CataloguePriceImportTests(unittest.TestCase):
    def test_all_eleven_page_one_prices_are_linked_to_exact_grade_and_powertrain(self) -> None:
        expected = {
            "striker_essential_mildhybridg140_4x2_manual": ("striker_essential", "mild hybrid-G 140 4x2", "manual", 92900),
            "striker_expression_mildhybridg140_4x2_manual": ("striker_expression", "mild hybrid-G 140 4x2", "manual", 99900),
            "striker_expression_mildhybridg140_4x2_automatic": ("striker_expression", "mild hybrid-G 140 auto 4x2", "automatic", 106900),
            "striker_extreme_mildhybridg140_4x2_automatic": ("striker_extreme", "mild hybrid-G 140 auto 4x2", "automatic", 115500),
            "striker_journey_mildhybridg140_4x2_automatic": ("striker_journey", "mild hybrid-G 140 auto 4x2", "automatic", 115500),
            "striker_expression_hybrid155_4x2_automatic": ("striker_expression", "hybrid 155 4x2", "automatic", 113000),
            "striker_extreme_hybrid155_4x2_automatic": ("striker_extreme", "hybrid 155 4x2", "automatic", 121500),
            "striker_journey_hybrid155_4x2_automatic": ("striker_journey", "hybrid 155 4x2", "automatic", 121500),
            "striker_expression_hybrid150_4x4_automatic": ("striker_expression", "hybrid 150 4x4", "automatic", 120900),
            "striker_extreme_hybrid150_4x4_automatic": ("striker_extreme", "hybrid 150 4x4", "automatic", 129500),
            "striker_journey_hybrid150_4x4_automatic": ("striker_journey", "hybrid 150 4x4", "automatic", 129500),
        }

        configurations = {
            row["code"]: row
            for row in rows(MASTER / "configurations.csv")
            if row["code"] in expected
        }
        self.assertEqual(set(configurations), set(expected))

        prices = [
            row for row in rows(MASTER / "configuration_prices.csv")
            if row["source_code"] == SOURCE
        ]
        self.assertEqual(len(prices), 11)
        self.assertEqual({row["configuration_code"] for row in prices}, set(expected))

        for code, (version, powertrain, transmission, amount) in expected.items():
            config = configurations[code]
            self.assertEqual(config["version_code"], version)
            self.assertEqual(config["powertrain_label"], powertrain)
            self.assertEqual(config["transmission_type"], transmission)
            self.assertEqual(config["status"], "active")

            matching = [row for row in prices if row["configuration_code"] == code]
            self.assertEqual(len(matching), 1)
            price = matching[0]
            self.assertEqual(
                (price["amount"], price["currency_code"], price["price_type"], price["price_date"]),
                (str(amount), "PLN", "catalog_gross", "2026-11-02"),
            )
            self.assertEqual(price["code"], f"{code}_pl_20261102")

        source_links = [
            row for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE
        ]
        self.assertEqual(len(source_links), 11)
        self.assertEqual({row["configuration_code"] for row in source_links}, set(expected))
        self.assertTrue(all(row["relationship"] == "documents" for row in source_links))

        grade_links = [
            row for row in rows(MASTER / "source_versions.csv")
            if row["source_code"] == SOURCE
        ]
        self.assertEqual(
            {row["version_code"] for row in grade_links},
            {"striker_essential", "striker_expression", "striker_extreme", "striker_journey"},
        )
        model_links = [
            row for row in rows(MASTER / "source_models.csv")
            if row["source_code"] == SOURCE
        ]
        self.assertEqual(len(model_links), 1)
        self.assertEqual((model_links[0]["model_code"], model_links[0]["relationship"]), ("striker", "price_list_for"))

        imported = rows(IMPORT)
        self.assertEqual(len(imported), 11)
        self.assertEqual({row["configuration_code"] for row in imported}, set(expected))
        self.assertTrue(all(row["source_code"] == SOURCE and row["source_page"] == "1" for row in imported))


if __name__ == "__main__":
    unittest.main()
