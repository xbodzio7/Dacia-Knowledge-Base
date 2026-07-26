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
SPEC = ROOT / "data" / "imports" / "brochure_technical_values" / "sandero-ecog120-automatic-20260202.json"
IMPORTER = ROOT / "tools" / "import_sandero_ecog120_automatic_brochure_technical_20260726.py"
SOURCE_CODE = "src_pl_sandero_brochure_20260202"
CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
}
ATTRIBUTES = {
    "engine_power",
    "engine_torque",
    "engine_displacement",
    "cylinder_count",
    "total_valve_count",
    "emission_standard",
    "gearbox_type",
    "gear_count",
    "top_speed",
    "acceleration_0_100",
    "fuel_tank_capacity",
    "minimum_kerb_weight",
    "gross_vehicle_weight",
    "gross_train_weight",
    "braked_trailer_weight",
}
FORBIDDEN = {
    "co2_emissions",
    "fuel_consumption_combined",
    "turning_circle",
    "standard_tyre_specification",
    "maximum_kerb_weight",
    "front_suspension_specification",
    "rear_suspension_specification",
    "injection_type",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoEcoG120AutomaticBrochureTechnicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") == SOURCE_CODE
            and row.get("configuration_code") in CONFIGURATIONS
            and row.get("attribute_code") in ATTRIBUTES
        ]

    def test_exact_counts_ids_configurations_attributes_and_fuels(self) -> None:
        self.assertEqual(len(self.values), 36)
        self.assertEqual([int(row["id"]) for row in self.values], list(range(2189, 2225)))
        self.assertEqual(Counter(row["configuration_code"] for row in self.values), Counter({code: 18 for code in CONFIGURATIONS}))
        self.assertEqual(
            Counter(row["attribute_code"] for row in self.values),
            Counter(
                {
                    "engine_power": 4,
                    "engine_torque": 4,
                    "acceleration_0_100": 4,
                    **{attribute: 2 for attribute in ATTRIBUTES - {"engine_power", "engine_torque", "acceleration_0_100"}},
                }
            ),
        )
        self.assertEqual(Counter(row["fuel_type_code"] for row in self.values), Counter({"": 24, "lpg": 6, "petrol": 6}))
        self.assertEqual({row["gear_number"] for row in self.values}, {""})
        self.assertEqual(len({row["code"] for row in self.values}), 36)

    def test_exact_source_values_are_preserved_for_both_trims(self) -> None:
        expected = {
            ("engine_power", "lpg"): "90",
            ("engine_power", "petrol"): "84",
            ("engine_torque", "lpg"): "197",
            ("engine_torque", "petrol"): "190",
            ("engine_displacement", ""): "1199",
            ("cylinder_count", ""): "3",
            ("total_valve_count", ""): "12",
            ("emission_standard", ""): "euro_6e_bis",
            ("gearbox_type", ""): "dct",
            ("gear_count", ""): "6",
            ("top_speed", ""): "180",
            ("acceleration_0_100", "lpg"): "9.8",
            ("acceleration_0_100", "petrol"): "10.9",
            ("fuel_tank_capacity", ""): "50",
            ("minimum_kerb_weight", ""): "1205",
            ("gross_vehicle_weight", ""): "1665",
            ("gross_train_weight", ""): "2765",
            ("braked_trailer_weight", ""): "1100",
        }
        for configuration in CONFIGURATIONS:
            actual = {
                (row["attribute_code"], row["fuel_type_code"]): row["value"]
                for row in self.values
                if row["configuration_code"] == configuration
            }
            self.assertEqual(actual, expected)

    def test_fuel_context_is_used_only_when_source_meaning_depends_on_fuel(self) -> None:
        fuel_specific = {
            row["attribute_code"]
            for row in self.values
            if row["fuel_type_code"]
        }
        self.assertEqual(fuel_specific, {"engine_power", "engine_torque", "acceleration_0_100"})
        top_speed = [row for row in self.values if row["attribute_code"] == "top_speed"]
        self.assertEqual({row["fuel_type_code"] for row in top_speed}, {""})
        self.assertEqual({row["value"] for row in top_speed}, {"180"})

    def test_excluded_evidence_is_not_materialized(self) -> None:
        target_values = [
            row for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") == SOURCE_CODE
            and row.get("configuration_code") in CONFIGURATIONS
        ]
        self.assertFalse({row["attribute_code"] for row in target_values} & FORBIDDEN)
        self.assertEqual(
            {item["code"] for item in self.spec["excluded_evidence"]},
            {
                "maximum_kerb_weight_requires_explicit_attribute",
                "wltp_country_placeholders_are_not_observations",
                "model_wide_chassis_rows_outside_exact_import",
                "tce100_column_without_exact_configuration",
            },
        )

    def test_source_relationships_and_provenance_are_exact(self) -> None:
        relationships = [
            row for row in rows(MASTER / "source_configurations.csv")
            if row.get("source_code") == SOURCE_CODE
            and row.get("configuration_code") in CONFIGURATIONS
        ]
        self.assertEqual(len(relationships), 2)
        self.assertEqual({row["relationship"] for row in relationships}, {"brochure_technical_data_for"})
        self.assertTrue(all("Source page 17" in row["notes"] for row in self.values))
        self.assertEqual({row["observation_date"] for row in self.values}, {"2026-02-02"})

    def test_reporting_scope_contains_new_exact_slots(self) -> None:
        payload = json.loads(
            (ROOT / "data" / "reporting" / "sandero_ecog120_automatic_completeness.json").read_text(encoding="utf-8")
        )
        slots = {
            (item["attribute_code"], item.get("fuel_type_code", ""))
            for item in payload["technical_slots"]
        }
        self.assertIn(("gearbox_type", ""), slots)
        self.assertIn(("minimum_kerb_weight", ""), slots)
        for attribute, fuel in {
            ("engine_power", "lpg"),
            ("engine_power", "petrol"),
            ("engine_torque", "lpg"),
            ("engine_torque", "petrol"),
            ("acceleration_0_100", "lpg"),
            ("acceleration_0_100", "petrol"),
            ("gross_train_weight", ""),
            ("gross_vehicle_weight", ""),
            ("braked_trailer_weight", ""),
        }:
            self.assertIn((attribute, fuel), slots)

    def test_importer_is_append_only_and_idempotent(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Sandero Eco-G 120 automatic brochure technical values", completed.stdout)

    def test_project_state_advances_to_towing_mass_package(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Sandero Eco-G 120 Automatic Brochure Technical Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Bigster and Duster Brochure Towing Mass Import")
        self.assertEqual(state["baseline"]["configuration_values"], 2224)
        self.assertEqual(state["baseline"]["rows"], 8888)
        self.assertEqual(state["baseline"]["configuration_import_specs"], 117)


if __name__ == "__main__":
    unittest.main()
