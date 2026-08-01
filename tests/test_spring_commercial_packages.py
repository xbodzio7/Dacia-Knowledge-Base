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

import import_spring_commercial_packages as importer  # noqa: E402
from reporting.commercial_offers import collect_commercial_components  # noqa: E402


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringCommercialPackagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = read(MASTER / "commercial_items.csv")
        cls.memberships = read(MASTER / "commercial_item_attributes.csv")
        cls.mappings = read(MASTER / "commercial_item_configurations.csv")
        cls.availability = read(MASTER / "configuration_attribute_availability.csv")

    def test_registered_source_hash_and_existing_configuration_boundary(self) -> None:
        digest = hashlib.sha256(importer.SOURCE.read_bytes()).hexdigest()
        self.assertEqual(digest, importer.SOURCE_SHA256)
        self.assertEqual(importer.selected_configurations(), importer.SELECTED_CONFIGURATIONS)

    def test_versioned_specs_preserve_exact_counts_and_blank_prices(self) -> None:
        self.assertEqual(len(importer.load_items_spec()), 5)
        self.assertEqual(len(importer.load_attributes_spec()), 18)
        mappings = importer.load_configurations_spec()
        self.assertEqual(len(mappings), 7)
        self.assertTrue(all(row["availability_status"] == "optional" for row in mappings))
        self.assertTrue(all(not row["amount"] and row["currency_code"] == "PLN" for row in mappings))

    def test_master_rows_match_generated_contract_and_contiguous_suffixes(self) -> None:
        importer.check()
        spring_items = [
            row
            for row in self.items
            if row["source_code"] == importer.SOURCE_CODE
            and row["code"] in importer.EXPECTED_ITEMS
        ]
        spring_memberships = [
            row
            for row in self.memberships
            if row["commercial_item_code"] in importer.EXPECTED_ITEMS
        ]
        spring_mappings = [
            row
            for row in self.mappings
            if row["code"] in importer.EXPECTED_MAPPING_CODES
        ]
        self.assertEqual([int(row["id"]) for row in spring_items], list(range(29, 34)))
        self.assertEqual([int(row["id"]) for row in spring_memberships], list(range(70, 88)))
        self.assertEqual([int(row["id"]) for row in spring_mappings], list(range(143, 150)))

    def test_item_applicability_is_limited_to_exact_brochure_grades(self) -> None:
        spring = [
            row
            for row in self.mappings
            if row["commercial_item_code"] in importer.EXPECTED_ITEMS
        ]
        self.assertEqual(
            Counter(row["commercial_item_code"] for row in spring),
            Counter(importer.EXPECTED_MAPPING_COUNTS),
        )
        self.assertEqual(
            {(row["commercial_item_code"], row["configuration_code"]) for row in spring},
            set(importer.EXPECTED_MAPPING_PAGES),
        )

    def test_reviewed_prices_and_remaining_unknowns_are_exposed_without_inference(self) -> None:
        components = collect_commercial_components(
            ROOT,
            sorted(importer.SELECTED_CONFIGURATIONS),
            "2026-07-31",
        )
        package_components = {
            code: [row for row in rows if row["code"] in importer.EXPECTED_ITEMS]
            for code, rows in components.items()
        }
        self.assertEqual(
            {code: len(rows) for code, rows in package_components.items()},
            {
                "spring_essential_electric70_automatic": 1,
                "spring_expression_electric70_automatic": 3,
                "spring_extreme_electric100_automatic": 3,
            },
        )
        extreme = {
            row["code"]: row
            for row in package_components["spring_extreme_electric100_automatic"]
        }
        self.assertEqual(extreme["spring_city_package"]["amount"], 1800.0)
        self.assertEqual(extreme["spring_power_package"]["amount"], 3000.0)
        self.assertEqual(
            extreme["spring_type2_charging_cable_option"]["amount"],
            None,
        )
        unknown = [
            row
            for rows in package_components.values()
            for row in rows
            if row["amount"] is None
        ]
        self.assertEqual(
    {
        code: sum(row["amount"] is None for row in rows)
        for code, rows in package_components.items()
    },
    {
        "spring_essential_electric70_automatic": 1,
        "spring_expression_electric70_automatic": 3,
        "spring_extreme_electric100_automatic": 1,
    },
)
        self.assertTrue(all(row["price_date"] == "" for row in unknown))
        self.assertEqual(
            {extreme[code]["price_date"] for code in ("spring_city_package", "spring_power_package")},
            {"2026-07-31"},
        )

    def test_package_membership_aligns_with_direct_optional_matrix_cells(self) -> None:
        latest: dict[tuple[str, str], dict[str, str]] = {}
        for row in self.availability:
            key = (row["configuration_code"], row["attribute_code"])
            if key not in latest or row["observation_date"] > latest[key]["observation_date"]:
                latest[key] = row
        for key in (
            ("spring_expression_electric70_automatic", "rear_view_camera"),
            ("spring_expression_electric70_automatic", "dc_charging_supported"),
            ("spring_extreme_electric100_automatic", "front_parking_sensors"),
            ("spring_extreme_electric100_automatic", "dc_charging_supported"),
        ):
            self.assertEqual(latest[key]["availability_status"], "optional")

    def test_package_does_not_add_models_versions_or_configurations(self) -> None:
        versions = read(MASTER / "versions.csv")
        configurations = read(MASTER / "configurations.csv")
        self.assertEqual(
            {row["code"] for row in versions if row["code"].startswith("spring_")},
            {"spring_essential", "spring_expression", "spring_extreme"},
        )
        self.assertEqual(
            {row["code"] for row in configurations if row["code"].startswith("spring_")},
            importer.SELECTED_CONFIGURATIONS,
        )

    def test_power_package_preserves_source_v2l_boundary(self) -> None:
        membership = next(
            row
            for row in self.memberships
            if row["code"] == "spring_power_package__vehicle_to_load"
        )
        self.assertIn("same brochure also lists V2L", membership["notes"])
        self.assertIn("funkcja ładowania dwukierunkowego V2L", membership["source_text"])
        self.assertFalse(
            any(
                row["configuration_code"] == "spring_extreme_electric100_automatic"
                and row["attribute_code"] == "vehicle_to_load"
                for row in self.availability
            ),
            "This package must not backfill a direct availability row that the earlier matrix import did not contain.",
        )


if __name__ == "__main__":
    unittest.main()
