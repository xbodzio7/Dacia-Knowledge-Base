from __future__ import annotations

import csv
import hashlib
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MASTER = ROOT / "data" / "master"
SPEC_DIR = ROOT / "data" / "imports" / "configuration_values"
SOURCE_CODE = "src_pl_jogger_price_my26_20260401"
PDF = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
EXPECTED_SHA = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"
ATTRIBUTES = {
    "lpg_vessel_capacity_total": {
        "id": "362",
        "name": "Total LPG vessel capacity",
        "value": "50",
        "id_start": 1173,
        "filename": "jogger-page6-lpg-vessel-capacity-total-20260401.json",
    },
    "lpg_vessel_filling_capacity": {
        "id": "363",
        "name": "LPG vessel filling capacity",
        "value": "40",
        "id_start": 1183,
        "filename": "jogger-page6-lpg-vessel-filling-capacity-20260401.json",
    },
}
SOURCE_TEXT = "LPG całkowita pojemność/pojemność napełniania: 50/40"

sys.path.insert(0, str(TOOLS))
import import_configuration_values as importer  # noqa: E402


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerLpgCapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = {
            row["code"]: row for row in csv_rows(MASTER / "attributes.csv")
        }
        cls.ecog_configurations = {
            row["code"]
            for row in csv_rows(MASTER / "configurations.csv")
            if row["code"].startswith("jogger_")
            and "_ecog120_" in row["code"]
            and row["status"] == "active"
        }
        cls.values = [
            row
            for row in csv_rows(MASTER / "configuration_attribute_values.csv")
            if row["attribute_code"] in ATTRIBUTES
            and row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-04-01"
        ]
        cls.specs = {
            code: importer.load_spec(SPEC_DIR / expected["filename"])
            for code, expected in ATTRIBUTES.items()
        }

    def test_lpg_capacity_attribute_contracts_are_active(self) -> None:
        for code, expected in ATTRIBUTES.items():
            with self.subTest(attribute=code):
                row = self.attributes[code]
                self.assertEqual(row["id"], expected["id"])
                self.assertEqual(row["category"], "Capacities")
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["data_type"], "decimal")
                self.assertEqual(row["unit"], "L")
                self.assertEqual(row["status"], "active")
                self.assertIn("LPG", row["description"])
        self.assertIn("fuel_tank_capacity", self.attributes)

    def test_two_specs_and_master_rows_form_contiguous_contract(self) -> None:
        for code, expected in ATTRIBUTES.items():
            spec = self.specs[code]
            self.assertEqual(spec.id_start, expected["id_start"])
            self.assertEqual(spec.attribute_code, code)
            self.assertEqual(len(spec.rows), 10)
            self.assertFalse(importer.verify_import(ROOT, spec).missing_rows)
        self.assertEqual(len(self.values), 20)
        self.assertEqual(
            [int(row["id"]) for row in self.values],
            list(range(1173, 1193)),
        )

    def test_import_covers_all_and_only_active_ecog_configurations(self) -> None:
        self.assertEqual(len(self.ecog_configurations), 10)
        for code in ATTRIBUTES:
            actual = {
                row["configuration_code"]
                for row in self.values
                if row["attribute_code"] == code
            }
            self.assertEqual(actual, self.ecog_configurations)
        self.assertFalse(
            [row for row in self.values if "_ecog120_" not in row["configuration_code"]]
        )

    def test_values_and_lpg_context_match_the_source_pair(self) -> None:
        self.assertEqual(
            Counter((row["attribute_code"], row["value"]) for row in self.values),
            Counter({
                ("lpg_vessel_capacity_total", "50"): 10,
                ("lpg_vessel_filling_capacity", "40"): 10,
            }),
        )
        self.assertEqual({row["fuel_type_code"] for row in self.values}, {"lpg"})

    def test_petrol_tank_rows_remain_unchanged_and_generic_lpg_is_absent(self) -> None:
        all_values = csv_rows(MASTER / "configuration_attribute_values.csv")
        petrol = [
            row
            for row in all_values
            if row["configuration_code"] in self.ecog_configurations
            and row["attribute_code"] == "fuel_tank_capacity"
            and row["source_code"] == SOURCE_CODE
            and row["fuel_type_code"] == "petrol"
        ]
        self.assertEqual(len(petrol), 10)
        self.assertEqual({row["value"] for row in petrol}, {"50"})
        self.assertFalse(
            [
                row
                for row in all_values
                if row["configuration_code"] in self.ecog_configurations
                and row["attribute_code"] == "fuel_tank_capacity"
                and row["source_code"] == SOURCE_CODE
                and row["fuel_type_code"] == "lpg"
            ]
        )

    def test_registered_source_page_text_and_hash_contract(self) -> None:
        for spec in self.specs.values():
            importer.verify_registered_sources(ROOT, spec, verify_text=False)
            self.assertEqual(spec.source_page, 6)
            self.assertEqual(spec.source_section, "EMISJA CO2")
            self.assertEqual({row.source_text for row in spec.rows}, {SOURCE_TEXT})
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)


if __name__ == "__main__":
    unittest.main()
