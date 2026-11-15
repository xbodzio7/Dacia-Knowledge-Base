from __future__ import annotations

import csv
import hashlib
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
import sys
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
        codes = set(importer.EXPECTED_COLOURS)
        items = [row for row in self.items if row["code"] in codes]
        memberships = [row for row in self.memberships if row["commercial_item_code"] in codes]
        mapping_sources = {
            importer.SOURCE_CODE,
            importer.APPROVED_CURRENT_MAPPING_STATE["source_code"],
        }
        mappings = [
            row for row in self.mappings
            if row["commercial_item_code"] in codes and row["source_code"] in mapping_sources
        ]
        self.assertEqual([int(row["id"]) for row in items], list(range(34, 40)))
        self.assertEqual([int(row["id"]) for row in memberships], list(range(88, 94)))
        self.assertEqual([int(row["id"]) for row in mappings], list(range(150, 168)))
        self.assertEqual(len(items), 6)
        self.assertEqual(len(memberships), 6)
        self.assertEqual(len(mappings), 18)

    def test_every_colour_maps_to_all_three_existing_configurations(self) -> None:
        codes = set(importer.EXPECTED_COLOURS)
        mapping_sources = {
            importer.SOURCE_CODE,
            importer.APPROVED_CURRENT_MAPPING_STATE["source_code"],
        }
        mappings = [
            row for row in self.mappings
            if row["commercial_item_code"] in codes and row["source_code"] in mapping_sources
        ]
        self.assertEqual(
            Counter(row["commercial_item_code"] for row in mappings),
            Counter({code: 3 for code in codes}),
        )
        self.assertEqual({row["configuration_code"] for row in mappings}, set(importer.CONFIGURATIONS))

    def test_exact_current_essential_white_and_khaki_pricing(self) -> None:
        components = collect_commercial_components(ROOT, list(importer.CONFIGURATIONS), "2026-08-02")
        colour_codes = set(importer.EXPECTED_COLOURS)
        selected = [
            (configuration_code, row)
            for configuration_code, component_rows in components.items()
            for row in component_rows
            if row["code"] in colour_codes
            and row.get("price_date", "") in ("", "2026-02-06", "2026-08-02")
        ]
        self.assertEqual(len(selected), 18)
        priced = [entry for entry in selected if entry[1]["amount"] is not None]
        self.assertEqual(len(priced), 4)
        priced_by_configuration = {
            (configuration_code, row["code"]): row
            for configuration_code, row in priced
        }
        khaki_code = "spring_colour_lichen_khaki"
        self.assertEqual(
            set(priced_by_configuration),
            {
                ("spring_essential_electric70_automatic", khaki_code),
                ("spring_expression_electric70_automatic", khaki_code),
                ("spring_extreme_electric100_automatic", khaki_code),
                ("spring_essential_electric70_automatic", "spring_colour_biel_alpejska"),
            },
        )
        expected_khaki = {
            "spring_essential_electric70_automatic": ("2026-08-02", "src_pl_spring_commercial_context_20260802"),
            "spring_expression_electric70_automatic": ("2026-02-06", "src_pl_spring_price_my26_20260206"),
            "spring_extreme_electric100_automatic": ("2026-02-06", "src_pl_spring_price_my26_20260206"),
        }
        for configuration_code, (price_date, source_code) in expected_khaki.items():
            row = priced_by_configuration[(configuration_code, khaki_code)]
            self.assertEqual(row["amount"], 2300.0)
            self.assertEqual(row["currency_code"], "PLN")
            self.assertEqual(row["price_date"], price_date)
            self.assertEqual(row["source_code"], source_code)
        white = priced_by_configuration[
            ("spring_essential_electric70_automatic", "spring_colour_biel_alpejska")
        ]
        self.assertEqual(white["amount"], 0.0)
        self.assertEqual(white["currency_code"], "PLN")
        self.assertEqual(white["price_date"], "2026-08-02")
        self.assertEqual(white["source_code"], "src_pl_spring_commercial_context_20260802")
        unpriced = [row for _, row in selected if row["amount"] is None]
        self.assertEqual(len(unpriced), 14)
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
