from __future__ import annotations

import csv
import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "import_bigster_equipment_commercial.py"
SPEC = importlib.util.spec_from_file_location(
    "import_bigster_equipment_commercial", MODULE_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
IMPORTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = IMPORTER
SPEC.loader.exec_module(IMPORTER)
MASTER = ROOT / "data" / "master"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterEquipmentCommercial20260703Tests(unittest.TestCase):
    def test_versioned_specs_have_exact_source_backed_counts(self) -> None:
        self.assertEqual(len(IMPORTER.load_equipment_spec()), 1316)
        self.assertEqual(len(IMPORTER.load_commercial_items_spec()), 7)
        self.assertEqual(len(IMPORTER.load_commercial_attributes_spec()), 17)
        self.assertEqual(len(IMPORTER.load_commercial_configurations_spec()), 48)

    def test_equipment_spec_covers_fourteen_configurations_and_ninety_four_attributes(self) -> None:
        spec = IMPORTER.load_equipment_spec()
        self.assertEqual(len({row["configuration_code"] for row in spec}), 14)
        self.assertEqual(len({row["attribute_code"] for row in spec}), 94)
        self.assertEqual(
            set(Counter(row["configuration_code"] for row in spec).values()),
            {94},
        )
        attributes = {row["code"]: row for row in rows("attributes.csv")}
        for code in {row["attribute_code"] for row in spec}:
            self.assertEqual(attributes[code]["status"], "active")
            self.assertIn(attributes[code]["data_type"], {"boolean", "string"})

    def test_generated_availability_preserves_status_distribution_and_qualifiers(self) -> None:
        generated = IMPORTER.generated_availability_rows()
        self.assertEqual(len(generated), 1316)
        self.assertEqual(
            Counter(row["availability_status"] for row in generated),
            Counter({"standard": 1045, "optional": 92, "not_available": 179}),
        )
        status = {
            (row["configuration_code"], row["attribute_code"]): row[
                "availability_status"
            ]
            for row in generated
        }
        self.assertEqual(
            status[("bigster_extreme_mildhybrid140_4x2_manual", "glass_sunroof")],
            "standard",
        )
        self.assertEqual(
            status[("bigster_journey_mildhybrid140_4x2_manual", "glass_sunroof")],
            "optional",
        )
        self.assertEqual(
            status[("bigster_extreme_hybridg150_4x4_automatic", "hill_descent_control")],
            "standard",
        )
        self.assertEqual(
            status[("bigster_extreme_hybrid155_4x2_automatic", "hill_descent_control")],
            "not_available",
        )

    def test_master_availability_matches_generated_contract_and_contiguous_suffix(self) -> None:
        actual = [
            row
            for row in rows("configuration_attribute_availability.csv")
            if row["source_code"] == IMPORTER.SOURCE_CODE
            and row["configuration_code"].startswith("bigster_")
        ]
        self.assertEqual(len(actual), 1316)
        self.assertEqual(
            IMPORTER.semantic_payload(actual, IMPORTER.AVAILABILITY_FIELDS[1:]),
            IMPORTER.semantic_payload(
                IMPORTER.generated_availability_rows(),
                IMPORTER.AVAILABILITY_FIELDS[1:],
            ),
        )
        self.assertEqual([int(row["id"]) for row in actual], list(range(3157, 4473)))

    def test_commercial_catalog_and_prices_match_exact_configuration_scope(self) -> None:
        items = IMPORTER.generated_commercial_items()
        members = IMPORTER.generated_commercial_attributes()
        mappings = IMPORTER.generated_commercial_configurations()
        self.assertEqual(Counter(row["item_type"] for row in items), Counter({"package": 4, "option": 3}))
        self.assertEqual(
            Counter(row["commercial_item_code"] for row in mappings),
            Counter(
                {
                    "bigster_winter_package": 12,
                    "bigster_winter_plus_package": 12,
                    "bigster_parking_package": 8,
                    "bigster_easy_package": 4,
                    "bigster_media_nav_live_option": 4,
                    "bigster_power_tailgate_option": 4,
                    "bigster_panoramic_roof_option": 4,
                }
            ),
        )
        self.assertEqual(len(members), 17)
        prices = {row["commercial_item_code"]: row["amount"] for row in mappings}
        self.assertEqual(prices["bigster_easy_package"], "2700")
        self.assertEqual(prices["bigster_panoramic_roof_option"], "4300")
        self.assertEqual(prices["bigster_winter_plus_package"], "2300")

    def test_commercial_memberships_align_with_availability_features(self) -> None:
        memberships = {
            row["commercial_item_code"]: set()
            for row in IMPORTER.generated_commercial_attributes()
        }
        for row in IMPORTER.generated_commercial_attributes():
            memberships[row["commercial_item_code"]].add(row["attribute_code"])
        self.assertEqual(
            memberships["bigster_panoramic_roof_option"], {"glass_sunroof"}
        )
        self.assertEqual(
            memberships["bigster_winter_plus_package"],
            {"heated_front_seats", "heated_steering_wheel", "heated_windscreen"},
        )
        self.assertTrue(
            {"front_parking_sensors", "rear_parking_sensors", "360_camera_system"}
            <= memberships["bigster_easy_package"]
        )

    def test_source_hash_and_evidence_boundary_are_locked(self) -> None:
        self.assertEqual(
            IMPORTER.file_sha256(IMPORTER.SOURCE), IMPORTER.SOURCE_SHA256
        )
        equipment_codes = {
            row["attribute_code"] for row in IMPORTER.load_equipment_spec()
        }
        self.assertTrue(
            {
                "roof_rails",
                "glass_sunroof",
                "hill_descent_control",
                "instrument_cluster_colour_10_1",
            }
            <= equipment_codes
        )
        self.assertTrue(
            {
                "engine_displacement",
                "maximum_speed",
                "fuel_tank_capacity",
                "maximum_payload",
            }.isdisjoint(equipment_codes)
        )


if __name__ == "__main__":
    unittest.main()
