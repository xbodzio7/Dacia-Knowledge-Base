from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC = ROOT / "data" / "imports" / "brochure_technical_values" / "jogger-hybrid-performance-completion-20251217.json"
IMPORTER = ROOT / "tools" / "import_jogger_brochure_hybrid_performance_20260726.py"
SOURCE = "src_pl_jogger_brochure_20251217"
SCALAR_ATTRIBUTES = {
    "acceleration_0_100",
    "hybrid_battery_capacity_source_stated",
    "max_power_rpm",
}
RANGE_ATTRIBUTES = {"max_power_rpm", "max_torque_rpm"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerBrochureHybridPerformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.scalars = [
            row for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") == SOURCE
            and row.get("observation_date") == "2025-12-17"
            and row.get("attribute_code") in SCALAR_ATTRIBUTES
        ]
        cls.ranges = [
            row for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
            if row.get("source_code") == SOURCE
            and row.get("observation_date") == "2025-12-17"
            and row.get("attribute_code") in RANGE_ATTRIBUTES
        ]

    def test_exact_scalar_and_range_ids_counts_and_contexts(self) -> None:
        self.assertEqual(len(self.scalars), 18)
        self.assertEqual([int(row["id"]) for row in self.scalars], list(range(2273, 2291)))
        self.assertEqual(Counter(row["attribute_code"] for row in self.scalars), Counter({
            "acceleration_0_100": 6,
            "hybrid_battery_capacity_source_stated": 6,
            "max_power_rpm": 6,
        }))
        self.assertEqual({row["fuel_type_code"] for row in self.scalars}, {""})
        self.assertEqual({row["gear_number"] for row in self.scalars}, {""})

        self.assertEqual(len(self.ranges), 58)
        self.assertEqual([int(row["id"]) for row in self.ranges], list(range(177, 235)))
        self.assertEqual(Counter(row["attribute_code"] for row in self.ranges), Counter({
            "max_power_rpm": 26,
            "max_torque_rpm": 32,
        }))
        self.assertEqual(Counter(row["fuel_type_code"] for row in self.ranges), Counter({
            "petrol": 32,
            "lpg": 20,
            "": 6,
        }))
        self.assertTrue(all(row["lower_inclusive"] == "true" and row["upper_inclusive"] == "true" for row in self.ranges))

    def test_hybrid_acceleration_preserves_five_and_seven_seat_values(self) -> None:
        acceleration = [row for row in self.scalars if row["attribute_code"] == "acceleration_0_100"]
        five = [row for row in acceleration if "_5seat_" in row["configuration_code"]]
        seven = [row for row in acceleration if "_7seat_" in row["configuration_code"]]
        self.assertEqual(len(five), 3)
        self.assertEqual(len(seven), 3)
        self.assertEqual({row["value"] for row in five}, {"8.9"})
        self.assertEqual({row["value"] for row in seven}, {"9"})

    def test_hybrid_battery_capacity_remains_source_stated(self) -> None:
        battery = [
            row for row in self.scalars
            if row["attribute_code"] == "hybrid_battery_capacity_source_stated"
        ]
        self.assertEqual(len(battery), 6)
        self.assertEqual({row["value"] for row in battery}, {"1.4"})
        self.assertTrue(all("1,4 kWh" in row["notes"] for row in battery))
        self.assertFalse(any(row["attribute_code"] in {"battery_capacity_gross", "battery_capacity_net", "battery_capacity_usable"} for row in self.scalars))

    def test_hybrid_engine_speed_point_and_range_are_not_flattened(self) -> None:
        power = [row for row in self.scalars if row["attribute_code"] == "max_power_rpm"]
        torque = [row for row in self.ranges if row["attribute_code"] == "max_torque_rpm" and "hybrid155" in row["configuration_code"]]
        self.assertEqual(len(power), 6)
        self.assertEqual({row["value"] for row in power}, {"5600"})
        self.assertEqual(len(torque), 6)
        self.assertEqual({(row["minimum_value"], row["maximum_value"]) for row in torque}, {("3000", "4000")})
        self.assertEqual({row["fuel_type_code"] for row in power + torque}, {""})

    def test_ecog_and_tce_ranges_preserve_source_fuel_context(self) -> None:
        tce_power = [row for row in self.ranges if row["attribute_code"] == "max_power_rpm" and "tce110" in row["configuration_code"]]
        tce_torque = [row for row in self.ranges if row["attribute_code"] == "max_torque_rpm" and "tce110" in row["configuration_code"]]
        self.assertEqual(len(tce_power), 6)
        self.assertEqual(len(tce_torque), 6)
        self.assertEqual({row["fuel_type_code"] for row in tce_power + tce_torque}, {"petrol"})
        self.assertEqual({(row["minimum_value"], row["maximum_value"]) for row in tce_power}, {("5000", "5250")})
        self.assertEqual({(row["minimum_value"], row["maximum_value"]) for row in tce_torque}, {("2900", "3500")})

        ecog_power = [row for row in self.ranges if row["attribute_code"] == "max_power_rpm" and "ecog120" in row["configuration_code"]]
        ecog_torque = [row for row in self.ranges if row["attribute_code"] == "max_torque_rpm" and "ecog120" in row["configuration_code"]]
        self.assertEqual(Counter(row["fuel_type_code"] for row in ecog_power), Counter({"lpg": 10, "petrol": 10}))
        self.assertEqual(Counter(row["fuel_type_code"] for row in ecog_torque), Counter({"lpg": 10, "petrol": 10}))
        self.assertEqual({(row["minimum_value"], row["maximum_value"]) for row in ecog_power}, {("4500", "5000")})

    def test_newer_my26_observations_remain_unchanged(self) -> None:
        all_ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
        newer_petrol_power = [
            row for row in all_ranges
            if row["attribute_code"] == "max_power_rpm"
            and "jogger_" in row["configuration_code"]
            and "ecog120" in row["configuration_code"]
            and row["fuel_type_code"] == "petrol"
            and row["observation_date"] == "2026-04-01"
        ]
        self.assertEqual(len(newer_petrol_power), 10)
        self.assertEqual({(row["minimum_value"], row["maximum_value"]) for row in newer_petrol_power}, {("4500", "5750")})

        newer_hybrid_acceleration = [
            row for row in all_ranges
            if row["attribute_code"] == "acceleration_0_100"
            and "jogger_" in row["configuration_code"]
            and "hybrid155" in row["configuration_code"]
            and row["observation_date"] == "2026-04-01"
        ]
        self.assertEqual(len(newer_hybrid_acceleration), 6)
        self.assertEqual({(row["minimum_value"], row["maximum_value"]) for row in newer_hybrid_acceleration}, {("8.9", "9")})

    def test_all_twenty_two_configurations_have_exact_source_relationships(self) -> None:
        relationships = [
            row for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE
            and row["configuration_code"].startswith("jogger_")
        ]
        self.assertEqual(len(relationships), 22)
        self.assertEqual(len({row["configuration_code"] for row in relationships}), 22)
        self.assertEqual({row["relationship"] for row in relationships}, {"brochure_technical_data_for"})

    def test_hybrid_reporting_scope_includes_completed_slots(self) -> None:
        payload = json.loads(
            (ROOT / "data" / "reporting" / "jogger_hybrid155_automatic_completeness.json").read_text(encoding="utf-8")
        )
        slots = {
            (item["attribute_code"], item.get("fuel_type_code", ""))
            for item in payload["technical_slots"]
        }
        self.assertIn(("acceleration_0_100", ""), slots)
        self.assertIn(("hybrid_battery_capacity_source_stated", ""), slots)
        self.assertIn(("max_power_rpm", ""), slots)
        self.assertIn(("max_torque_rpm", ""), slots)

    def test_importer_is_append_only_and_project_state_advances(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Jogger brochure hybrid performance completion", completed.stdout)

        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Jogger Brochure Hybrid Performance Completion")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Brochure Chassis Measurement Context Modeling")
        self.assertEqual(state["baseline"]["tests"], 867)
        self.assertEqual(state["baseline"]["rows"], 9015)
        self.assertEqual(state["baseline"]["configuration_values"], 2290)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertEqual(state["baseline"]["configuration_import_specs"], 117)
        self.assertEqual(state["baseline"]["configuration_range_import_specs"], 20)


if __name__ == "__main__":
    unittest.main()
