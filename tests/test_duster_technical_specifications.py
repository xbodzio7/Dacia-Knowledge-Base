from __future__ import annotations

import csv
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPECS = ROOT / "data" / "imports" / "configuration_values"
SOURCE = "src_pl_duster_price_my26_py25_20260206"

sys.path.insert(0, str(ROOT / "tools"))
import configuration_completeness  # noqa: E402

EXPECTED_COUNTS = {
    "acceleration_0_100": 28,
    "braked_trailer_weight": 24,
    "cargo_volume_vda": 24,
    "co2_emissions": 28,
    "cylinder_count": 24,
    "engine_displacement": 24,
    "engine_power": 28,
    "engine_torque": 24,
    "fuel_consumption_combined": 28,
    "fuel_tank_capacity": 32,
    "max_power_rpm": 24,
    "max_torque_rpm": 20,
    "standing_km": 18,
    "starter_generator_power": 7,
    "top_speed": 28,
    "total_valve_count": 24,
    "traction_motor_power": 7,
}


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterTechnicalSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.all_values = rows("configuration_attribute_values.csv")
        cls.values = [
            row for row in cls.all_values
            if row["configuration_code"].startswith("duster_iii_")
        ]
        cls.configurations = {
            row["code"]
            for row in rows("configurations.csv")
            if row["code"].startswith("duster_iii_")
        }
        cls.spec_paths = sorted(SPECS.glob("duster-page*.json"))
        cls.specs = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in cls.spec_paths
        ]

    def test_33_specs_expand_to_392_exact_master_rows(self) -> None:
        self.assertEqual(len(self.specs), 33)
        expected = []
        for spec in self.specs:
            date = spec["observation_date"]
            for offset, item in enumerate(spec["rows"]):
                fuel = item.get("fuel_type_code", spec["fuel_type_code"])
                parts = [
                    item["configuration_code"],
                    spec["attribute_code"],
                ]
                if fuel:
                    parts.append(fuel)
                parts.append(date.replace("-", ""))
                expected.append((
                    str(spec["id_start"] + offset),
                    "_".join(parts),
                    item["configuration_code"],
                    spec["attribute_code"],
                    fuel,
                    item["value"],
                    date,
                    item["source_code"],
                ))
        actual = [
            (
                row["id"], row["code"], row["configuration_code"],
                row["attribute_code"], row["fuel_type_code"], row["value"],
                row["observation_date"], row["source_code"],
            )
            for row in self.values
        ]
        self.assertEqual(len(expected), 392)
        self.assertEqual(actual, expected)
        self.assertEqual([int(row["id"]) for row in self.values], list(range(311, 703)))

    def test_attribute_and_context_counts_are_stable(self) -> None:
        self.assertEqual(Counter(row["attribute_code"] for row in self.values), EXPECTED_COUNTS)
        self.assertEqual(
            Counter(row["fuel_type_code"] for row in self.values),
            Counter({"": 320, "lpg": 36, "petrol": 36}),
        )
        self.assertEqual(
            Counter(row["observation_date"] for row in self.values),
            Counter({"2026-02-06": 372, "2025-10-01": 20}),
        )
        self.assertEqual({row["source_code"] for row in self.values}, {SOURCE})

    def test_every_configuration_has_unambiguous_core_values(self) -> None:
        for attribute in (
            "engine_displacement", "cylinder_count", "total_valve_count",
            "braked_trailer_weight", "cargo_volume_vda",
        ):
            self.assertEqual(
                {row["configuration_code"] for row in self.values if row["attribute_code"] == attribute},
                self.configurations,
                attribute,
            )

    def test_bifuel_contexts_preserve_source_distinctions(self) -> None:
        eco_g_100 = "duster_iii_essential_ecog100_4x2_manual"
        expected = {
            ("top_speed", "petrol", "163"), ("top_speed", "lpg", "168"),
            ("acceleration_0_100", "petrol", "14"), ("acceleration_0_100", "lpg", "13.2"),
            ("fuel_tank_capacity", "petrol", "50"), ("fuel_tank_capacity", "lpg", "51"),
            ("co2_emissions", "petrol", "148"), ("co2_emissions", "lpg", "128"),
            ("fuel_consumption_combined", "petrol", "6.5"),
            ("fuel_consumption_combined", "lpg", "7.9"),
        }
        actual = {
            (row["attribute_code"], row["fuel_type_code"], row["value"])
            for row in self.values
            if row["configuration_code"] == eco_g_100
            and row["attribute_code"] in {item[0] for item in expected}
        }
        self.assertEqual(actual, expected)

        eco_g_120 = "duster_iii_essential_ecog120_4x2_manual"
        power_torque = {
            (row["attribute_code"], row["fuel_type_code"], row["value"])
            for row in self.values
            if row["configuration_code"] == eco_g_120
            and row["attribute_code"] in {"engine_power", "engine_torque"}
        }
        self.assertEqual(power_torque, {
            ("engine_power", "lpg", "90"), ("engine_power", "petrol", "84"),
            ("engine_torque", "lpg", "197"), ("engine_torque", "petrol", "190"),
        })

    def test_hybrid_motor_components_are_not_collapsed_into_system_power(self) -> None:
        h140 = "duster_iii_expression_hybrid140_4x2_automatic"
        h155 = "duster_iii_expression_hybrid155_4x2_automatic"
        actual = {
            (row["configuration_code"], row["attribute_code"], row["value"])
            for row in self.values
            if row["configuration_code"] in {h140, h155}
            and row["attribute_code"] in {"engine_power", "traction_motor_power", "starter_generator_power"}
        }
        self.assertEqual(actual, {
            (h140, "engine_power", "69"),
            (h140, "traction_motor_power", "36"),
            (h140, "starter_generator_power", "15"),
            (h155, "engine_power", "80"),
            (h155, "traction_motor_power", "35"),
            (h155, "starter_generator_power", "15"),
        })

    def test_trim_dependent_or_ambiguous_rows_are_not_imported(self) -> None:
        forbidden = {
            "kerb_weight", "gross_vehicle_weight", "maximum_payload",
            "standard_tyre_specification", "drive_type", "gear_count",
        }
        self.assertFalse([row for row in self.values if row["attribute_code"] in forbidden])
        self.assertFalse(any("hybridg150" in row["configuration_code"] for row in self.values))

    def test_prices_and_reporting_scope_remain_stable(self) -> None:
        prices = [
            row for row in rows("configuration_prices.csv")
            if row["configuration_code"].startswith("duster_iii_")
        ]
        self.assertEqual(len(prices), 24)
        report = configuration_completeness.collect_report(
            ROOT, ROOT / "data" / "reporting" / "configuration_completeness.json"
        )
        self.assertEqual(report["scope"]["reporting_configurations"], 7)
        self.assertEqual(report["scope"]["repository_status_configurations"], 53)
        self.assertEqual(report["scope"]["excluded_configurations"], 46)

    def test_repository_totals_match_technical_package(self) -> None:
        self.assertEqual(len(self.all_values), 1172)
        self.assertEqual(len(list(SPECS.glob("*.json"))), 67)


if __name__ == "__main__":
    unittest.main()
