from __future__ import annotations

import csv
import hashlib
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
sys.path.insert(0, str(ROOT / "tools"))

import import_spring_exterior_colour_options as importer  # noqa: E402
from reporting.commercial_offers import collect_commercial_components  # noqa: E402


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringExteriorColourOptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = read(MASTER / "commercial_items.csv")
        cls.memberships = read(MASTER / "commercial_item_attributes.csv")
        cls.mappings = read(MASTER / "commercial_item_configurations.csv")

    def test_registered_source_hash_and_existing_configuration_boundary(self) -> None:
        self.assertEqual(hashlib.sha256(importer.SOURCE.read_bytes()).hexdigest(), importer.SOURCE_SHA256)
        importer.verify_source_and_scope()

    def test_spec_preserves_six_exact_names_and_finish_classes(self) -> None:
        rows = importer.load_spec()
        self.assertEqual(len(rows), 6)
        self.assertEqual(
            Counter(row["finish_type"] for row in rows),
            Counter({"non_metallic": 5, "metallic": 1}),
        )
        self.assertEqual(
            {row["name"] for row in rows},
            {name for name, _ in importer.EXPECTED_COLOURS.values()},
        )

    def test_master_rows_match_generated_contract_and_contiguous_suffixes(self) -> None:
        importer.check()
        codes = set(importer.EXPECTED_COLOURS)
        items = [row for row in self.items if row["code"] in codes]
        memberships = [row for row in self.memberships if row["commercial_item_code"] in codes]
        mappings = [row for row in self.mappings if row["commercial_item_code"] in codes]
        self.assertEqual([int(row["id"]) for row in items], list(range(34, 40)))
        self.assertEqual([int(row["id"]) for row in memberships], list(range(88, 94)))
        self.assertEqual([int(row["id"]) for row in mappings], list(range(150, 168)))

    def test_every_colour_maps_to_all_three_existing_configurations(self) -> None:
        codes = set(importer.EXPECTED_COLOURS)
        mappings = [row for row in self.mappings if row["commercial_item_code"] in codes]
        self.assertEqual(
            Counter(row["commercial_item_code"] for row in mappings),
            Counter({code: 3 for code in codes}),
        )
        self.assertEqual({row["configuration_code"] for row in mappings}, set(importer.CONFIGURATIONS))

    def test_only_approved_essential_khaki_mapping_is_priced(self) -> None:
        components = collect_commercial_components(ROOT, list(importer.CONFIGURATIONS), "2026-08-02")
        colour_codes = set(importer.EXPECTED_COLOURS)
        selected = [
            row for rows in components.values() for row in rows
            if row["code"] in colour_codes
        ]
        self.assertEqual(len(selected), 18)
        priced = [row for row in selected if row["amount"] is not None]
        self.assertEqual(len(priced), 1)
        self.assertEqual(priced[0]["code"], "spring_colour_lichen_khaki")
        self.assertEqual(priced[0]["configuration_code"], "spring_essential_electric70_automatic")
        self.assertEqual(priced[0]["amount"], 2300.0)
        self.assertEqual(priced[0]["currency_code"], "PLN")
        self.assertEqual(priced[0]["price_date"], "2026-08-02")
        unpriced = [row for row in selected if row["amount"] is None]
        self.assertEqual(len(unpriced), 17)
        self.assertTrue(
            all(row["currency_code"] == "PLN" and row["price_date"] == "" for row in unpriced)
        )

    def test_each_colour_membership_uses_only_exterior_color(self) -> None:
        codes = set(importer.EXPECTED_COLOURS)
        memberships = [row for row in self.memberships if row["commercial_item_code"] in codes]
        self.assertEqual({row["attribute_code"] for row in memberships}, {"exterior_color"})
        self.assertTrue(all("single scalar colour value" in row["notes"] for row in memberships))

    def test_package_adds_no_model_version_or_configuration(self) -> None:
        models = read(MASTER / "models.csv")
        versions = read(MASTER / "versions.csv")
        configurations = read(MASTER / "configurations.csv")
        self.assertEqual(len(models), 19)
        self.assertEqual(
            {row["code"] for row in versions if row["code"].startswith("spring_")},
            {"spring_essential", "spring_expression", "spring_extreme"},
        )
        self.assertEqual(
            {row["code"] for row in configurations if row["code"].startswith("spring_")},
            set(importer.CONFIGURATIONS),
        )


if __name__ == "__main__":
    unittest.main()
