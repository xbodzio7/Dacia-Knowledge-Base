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
    "cargo_volume_vda_to_luggage_cover": {
        "id": "360",
        "name": "Cargo volume VDA to luggage-cover height",
        "description_fragment": "luggage-cover",
        "five_seat": "708",
        "seven_seat": "160",
        "source_text": "708/160",
        "id_start": 1129,
    },
    "cargo_volume_vda_to_seatback": {
        "id": "361",
        "name": "Cargo volume VDA to seat-back height",
        "description_fragment": "seat-back",
        "five_seat": "607",
        "seven_seat": "506",
        "source_text": "607/506",
        "id_start": 1151,
    },
}

sys.path.insert(0, str(TOOLS))
import import_configuration_values as importer  # noqa: E402


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerCargoMeasurementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.attributes = {
            row["code"]: row for row in csv_rows(MASTER / "attributes.csv")
        }
        cls.configurations = {
            row["code"]
            for row in csv_rows(MASTER / "configurations.csv")
            if row["code"].startswith("jogger_") and row["status"] == "active"
        }
        cls.values = [
            row
            for row in csv_rows(MASTER / "configuration_attribute_values.csv")
            if row["attribute_code"] in ATTRIBUTES
            and row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-04-01"
        ]
        cls.by_key = {
            (row["configuration_code"], row["attribute_code"]): row
            for row in cls.values
        }
        cls.specs = {
            code: importer.load_spec(
                SPEC_DIR
                / (
                    "jogger-page6-cargo-vda-luggage-cover-20260401.json"
                    if code == "cargo_volume_vda_to_luggage_cover"
                    else "jogger-page6-cargo-vda-seatback-20260401.json"
                )
            )
            for code in ATTRIBUTES
        }

    def test_measurement_specific_attribute_contracts_are_active(self) -> None:
        for code, expected in ATTRIBUTES.items():
            with self.subTest(attribute=code):
                row = self.attributes[code]
                self.assertEqual(row["id"], expected["id"])
                self.assertEqual(row["category"], "Capacities")
                self.assertEqual(row["name"], expected["name"])
                self.assertEqual(row["data_type"], "integer")
                self.assertEqual(row["unit"], "L")
                self.assertEqual(row["status"], "active")
                self.assertIn(expected["description_fragment"], row["description"])
        self.assertIn("boot_capacity", self.attributes)
        self.assertIn("cargo_volume_vda", self.attributes)

    def test_two_specs_and_master_rows_form_contiguous_contract(self) -> None:
        for code, expected in ATTRIBUTES.items():
            spec = self.specs[code]
            self.assertEqual(spec.id_start, expected["id_start"])
            self.assertEqual(spec.attribute_code, code)
            self.assertEqual(len(spec.rows), 22)
            self.assertFalse(importer.verify_import(ROOT, spec).missing_rows)
        self.assertEqual(len(self.values), 44)
        self.assertEqual(
            [int(row["id"]) for row in self.values],
            list(range(1129, 1173)),
        )

    def test_every_active_jogger_configuration_has_both_measurements(self) -> None:
        self.assertEqual(len(self.configurations), 22)
        self.assertEqual(len(self.by_key), 44)
        for configuration in self.configurations:
            for attribute in ATTRIBUTES:
                self.assertIn((configuration, attribute), self.by_key)

    def test_five_and_seven_seat_values_match_exact_source_pairs(self) -> None:
        for code, expected in ATTRIBUTES.items():
            rows = [row for row in self.values if row["attribute_code"] == code]
            counts = Counter(row["value"] for row in rows)
            self.assertEqual(
                counts,
                Counter({expected["five_seat"]: 11, expected["seven_seat"]: 11}),
            )
            for row in rows:
                expected_value = (
                    expected["five_seat"]
                    if "_5seat_" in row["configuration_code"]
                    else expected["seven_seat"]
                )
                self.assertEqual(row["value"], expected_value)

    def test_qualified_rows_do_not_populate_generic_cargo_attributes(self) -> None:
        all_values = csv_rows(MASTER / "configuration_attribute_values.csv")
        generic = [
            row
            for row in all_values
            if row["source_code"] == SOURCE_CODE
            and row["observation_date"] == "2026-04-01"
            and row["attribute_code"] in {"boot_capacity", "cargo_volume_vda"}
        ]
        self.assertFalse(generic)
        self.assertTrue(
            all("VDA cargo volume" in row["notes"] for row in self.values)
        )

    def test_registered_source_page_section_text_and_hash_contract(self) -> None:
        for code, expected in ATTRIBUTES.items():
            spec = self.specs[code]
            importer.verify_registered_sources(ROOT, spec, verify_text=False)
            self.assertEqual(spec.source_page, 6)
            self.assertEqual(spec.source_section, "BAGAŻNIK")
            self.assertEqual({row.source_text for row in spec.rows}, {expected["source_text"]})
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)


if __name__ == "__main__":
    unittest.main()
