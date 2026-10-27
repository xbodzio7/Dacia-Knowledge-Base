from __future__ import annotations

import csv
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
VALUE_DIR = ROOT / "data/imports/configuration_values"
RANGE_DIR = ROOT / "data/imports/configuration_value_ranges"
SOURCE_CODE = "src_pl_bigster_price_my26_20260703"
SOURCE_SHA256 = "9528654fb3daf3767a2defbbc80e8a85abceecb11e04bb176aa0b76443be178a"
GROUPS = {
    "mildhybrid140": {
        "bigster_essential_mildhybrid140_4x2_manual",
        "bigster_expression_mildhybrid140_4x2_manual",
        "bigster_extreme_mildhybrid140_4x2_manual",
        "bigster_journey_mildhybrid140_4x2_manual",
    },
    "mildhybridg140": {
        "bigster_essential_mildhybridg140_4x2_manual",
        "bigster_expression_mildhybridg140_4x2_manual",
        "bigster_extreme_mildhybridg140_4x2_manual",
        "bigster_journey_mildhybridg140_4x2_manual",
    },
    "hybridg150": {
        "bigster_expression_hybridg150_4x4_automatic",
        "bigster_extreme_hybridg150_4x4_automatic",
        "bigster_journey_hybridg150_4x4_automatic",
    },
    "hybrid155": {
        "bigster_expression_hybrid155_4x2_automatic",
        "bigster_extreme_hybrid155_4x2_automatic",
        "bigster_journey_hybrid155_4x2_automatic",
    },
}
ALL_CONFIGURATIONS = set().union(*GROUPS.values())


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterTechnicalSpecifications20260703Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-07-03"
            and row["configuration_code"] in ALL_CONFIGURATIONS
        ]
        cls.ranges = [
            row
            for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
            if row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-07-03"
            and row["configuration_code"] in ALL_CONFIGURATIONS
        ]
        cls.attributes = {row["code"]: row for row in rows(MASTER / "attributes.csv")}

    def test_versioned_spec_set_contains_forty_one_values_and_one_range(self) -> None:
        scalar_specs = sorted(VALUE_DIR.glob("bigster-*-20260703.json"))
        range_specs = sorted(RANGE_DIR.glob("bigster-*-20260703.json"))
        self.assertEqual(len(scalar_specs), 41)
        self.assertEqual(
            [path.name for path in range_specs],
            ["bigster-page6-maximum-payload-range-20260703.json"],
        )
        self.assertEqual(
            {json.loads(path.read_text(encoding="utf-8"))["kind"] for path in scalar_specs},
            {"configuration_attribute_values"},
        )

    def test_exact_ids_and_package_totals_are_materialized(self) -> None:
        self.assertEqual(len(self.values), 552)
        self.assertEqual({int(row["id"]) for row in self.values}, set(range(1205, 1757)))
        self.assertEqual(len(self.ranges), 14)
        self.assertEqual({int(row["id"]) for row in self.ranges}, set(range(145, 159)))
        self.assertEqual(len({row["attribute_code"] for row in self.values}), 41)

    def test_powertrain_denominators_and_fuel_contexts_are_exact(self) -> None:
        expected = {
            "mildhybrid140": 37,
            "mildhybridg140": 41,
            "hybridg150": 40,
            "hybrid155": 40,
        }
        for group, configurations in GROUPS.items():
            counts = Counter(row["configuration_code"] for row in self.values if row["configuration_code"] in configurations)
            self.assertEqual(set(counts), configurations)
            self.assertEqual(set(counts.values()), {expected[group]})
        bifuel = GROUPS["mildhybridg140"] | GROUPS["hybridg150"]
        for configuration in bifuel:
            for attribute in ("fuel_tank_capacity", "co2_emissions", "fuel_consumption_combined"):
                contexts = {
                    row["fuel_type_code"]
                    for row in self.values
                    if row["configuration_code"] == configuration and row["attribute_code"] == attribute
                }
                self.assertEqual(contexts, {"petrol", "lpg"})
        petrol_injection = [
            row for row in self.values
            if row["attribute_code"] == "injection_type" and row["fuel_type_code"] == "petrol"
        ]
        self.assertEqual(len(petrol_injection), 14)
        self.assertEqual({row["value"] for row in petrol_injection}, {"direct_injection"})

    def test_hybrid_155_component_values_remain_separate(self) -> None:
        expected = {
            "hybrid_system_power_total": "116",
            "engine_power": "80",
            "engine_torque": "172",
            "traction_motor_power": "36",
            "starter_generator_power": "15",
            "traction_motor_torque": "205",
        }
        for configuration in GROUPS["hybrid155"]:
            observed = {
                row["attribute_code"]: row["value"]
                for row in self.values
                if row["configuration_code"] == configuration
                and row["attribute_code"] in expected
            }
            self.assertEqual(observed, expected)
        self.assertFalse(
            any(
                row["attribute_code"] == "hybrid_system_power_total"
                and row["configuration_code"] in GROUPS["hybridg150"]
                for row in self.values
            )
        )

    def test_4x2_and_4x4_dimensions_are_not_flattened(self) -> None:
        dimensions = {
            "overall_height": ({"1711"}, {"1706"}),
            "wheelbase": ({"2702"}, {"2704"}),
            "rear_overhang": ({"1015"}, {"1012"}),
            "ground_clearance": ({"220"}, {"219"}),
        }
        four_by_two = GROUPS["mildhybrid140"] | GROUPS["mildhybridg140"] | GROUPS["hybrid155"]
        for attribute, (expected_4x2, expected_4x4) in dimensions.items():
            values_4x2 = {row["value"] for row in self.values if row["attribute_code"] == attribute and row["configuration_code"] in four_by_two}
            values_4x4 = {row["value"] for row in self.values if row["attribute_code"] == attribute and row["configuration_code"] in GROUPS["hybridg150"]}
            self.assertEqual(values_4x2, expected_4x2)
            self.assertEqual(values_4x4, expected_4x4)

    def test_payload_pairs_are_ranges_not_false_scalar_values(self) -> None:
        self.assertFalse(any(row["attribute_code"] == "maximum_payload" for row in self.values))
        expected = {
            "mildhybrid140": ("451", "540"),
            "mildhybridg140": ("451", "540"),
            "hybridg150": ("462", "509"),
            "hybrid155": ("453", "521"),
        }
        for group, configurations in GROUPS.items():
            selected = [row for row in self.ranges if row["configuration_code"] in configurations]
            self.assertEqual(len(selected), len(configurations))
            self.assertEqual(
                {(row["minimum_value"], row["maximum_value"]) for row in selected},
                {expected[group]},
            )
            self.assertEqual({row["lower_inclusive"] for row in selected}, {"true"})
            self.assertEqual({row["upper_inclusive"] for row in selected}, {"true"})

    def test_neutral_attributes_do_not_add_unstated_semantics(self) -> None:
        expected = {
            "particulate_filter": ("boolean", ""),
            "hybrid_system_voltage": ("integer", "V"),
            "hybrid_battery_capacity_source_stated": ("decimal", "kWh"),
            "cargo_volume_without_spare_wheel_iso3832": ("integer", "dm3"),
            "maximum_cargo_volume_iso3832": ("integer", "dm3"),
        }
        for code, (data_type, unit) in expected.items():
            attribute = self.attributes[code]
            self.assertEqual((attribute["data_type"], attribute["unit"]), (data_type, unit))
            self.assertEqual(attribute["status"], "active")
        descriptions = " ".join(self.attributes[code]["description"].lower() for code in expected)
        self.assertIn("without classifying", descriptions)
        self.assertIn("without inferring", descriptions)

    def test_source_hash_and_provenance_are_preserved(self) -> None:
        source = next(row for row in rows(MASTER / "sources.csv") if row["code"] == SOURCE_CODE)
        path = ROOT / source["file_path"]
        self.assertTrue(path.is_file())
        self.assertEqual(source["sha256"], SOURCE_SHA256)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), SOURCE_SHA256)
        self.assertEqual({row["source_code"] for row in self.values}, {SOURCE_CODE})
        self.assertEqual({row["source_code"] for row in self.ranges}, {SOURCE_CODE})
        self.assertTrue(all("Source page" in row["notes"] for row in self.values + self.ranges))


if __name__ == "__main__":
    unittest.main()
