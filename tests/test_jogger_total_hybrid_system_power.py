from __future__ import annotations

import csv
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MASTER = ROOT / "data" / "master"
SPEC = (
    ROOT
    / "data"
    / "imports"
    / "configuration_values"
    / "jogger-page6-hybrid-system-power-total-20260401.json"
)
SOURCE_CODE = "src_pl_jogger_price_my26_20260401"
PDF = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
EXPECTED_SHA = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"

sys.path.insert(0, str(TOOLS))
import import_configuration_values as importer  # noqa: E402


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerTotalHybridSystemPowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = importer.load_spec(SPEC)
        cls.attributes = {
            row["code"]: row for row in csv_rows(MASTER / "attributes.csv")
        }
        cls.hybrid_configurations = {
            row["code"]
            for row in csv_rows(MASTER / "configurations.csv")
            if row["code"].startswith("jogger_")
            and "_hybrid155_" in row["code"]
            and row["status"] == "active"
        }
        cls.all_values = csv_rows(MASTER / "configuration_attribute_values.csv")
        cls.values = [
            row
            for row in cls.all_values
            if row["attribute_code"] == "hybrid_system_power_total"
            and row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-04-01"
        ]

    def test_attribute_is_active_total_system_power_contract(self) -> None:
        attribute = self.attributes["hybrid_system_power_total"]
        self.assertEqual(attribute["id"], "364")
        self.assertEqual(attribute["category"], "Hybrid System")
        self.assertEqual(attribute["name"], "Total hybrid system power")
        self.assertEqual(attribute["data_type"], "decimal")
        self.assertEqual(attribute["unit"], "kW")
        self.assertEqual(attribute["status"], "active")
        self.assertIn("complete hybrid propulsion system", attribute["description"])
        self.assertIn("not a calculated sum", attribute["description"])

    def test_spec_and_master_rows_form_exact_contiguous_contract(self) -> None:
        self.assertEqual(self.spec.id_start, 1193)
        self.assertEqual(self.spec.attribute_code, "hybrid_system_power_total")
        self.assertEqual(len(self.spec.rows), 6)
        self.assertEqual(len(self.values), 6)
        self.assertEqual(
            [int(row["id"]) for row in self.values],
            list(range(1193, 1199)),
        )
        self.assertFalse(importer.verify_import(ROOT, self.spec).missing_rows)

    def test_import_covers_all_and_only_active_hybrid155_configurations(self) -> None:
        self.assertEqual(len(self.hybrid_configurations), 6)
        self.assertEqual(
            {row["configuration_code"] for row in self.values},
            self.hybrid_configurations,
        )
        self.assertEqual({row["value"] for row in self.values}, {"116"})
        self.assertEqual({row["fuel_type_code"] for row in self.values}, {""})

    def test_total_system_power_does_not_rewrite_or_sum_components(self) -> None:
        components = {
            "engine_power": "80",
            "traction_motor_power": "36",
            "starter_generator_power": "15",
        }
        for configuration in self.hybrid_configurations:
            for attribute, expected_value in components.items():
                matching = [
                    row
                    for row in self.all_values
                    if row["configuration_code"] == configuration
                    and row["attribute_code"] == attribute
                    and row["source_code"] == SOURCE_CODE
                ]
                self.assertEqual(len(matching), 1, (configuration, attribute))
                self.assertEqual(matching[0]["value"], expected_value)
        self.assertNotEqual(116, sum(int(value) for value in components.values()))
        self.assertTrue(
            all("not a calculated sum" in row["notes"] for row in self.values)
        )

    def test_unspecified_capacity_remains_excluded_after_chemistry_import(self) -> None:
        excluded = [
            row
            for row in self.all_values
            if row["configuration_code"] in self.hybrid_configurations
            and row["source_code"] == SOURCE_CODE
            and row["attribute_code"] == "hybrid_battery_capacity"
        ]
        self.assertFalse(excluded)
        voltage = [
            row
            for row in self.all_values
            if row["configuration_code"] in self.hybrid_configurations
            and row["source_code"] == SOURCE_CODE
            and row["attribute_code"] == "hybrid_battery_voltage"
        ]
        self.assertEqual(len(voltage), 6)
        self.assertEqual({row["value"] for row in voltage}, {"200"})

    def test_registered_source_page_text_and_hash_contract(self) -> None:
        importer.verify_registered_sources(ROOT, self.spec, verify_text=False)
        self.assertEqual(self.spec.source_page, 6)
        self.assertEqual(self.spec.source_section, "SILNIKI")
        self.assertEqual({row.source_text for row in self.spec.rows}, {"116 kW"})
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)


if __name__ == "__main__":
    unittest.main()
