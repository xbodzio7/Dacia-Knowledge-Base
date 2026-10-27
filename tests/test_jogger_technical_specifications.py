from __future__ import annotations

import csv
import hashlib
import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_DIR = ROOT / "data" / "imports" / "configuration_values"
SOURCE = "src_pl_jogger_price_my26_20260401"
DATE = "2026-04-01"
PDF = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
EXPECTED_SHA = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"


def csv_rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerTechnicalSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.configurations = {
            row["code"]: row
            for row in csv_rows("configurations.csv")
            if row["code"].startswith("jogger_")
        }
        cls.values = [
            row
            for row in csv_rows("configuration_attribute_values.csv")
            if row["source_code"] == SOURCE
            and row["observation_date"] == DATE
            and 725 <= int(row["id"]) <= 1036
        ]
        cls.by_semantic = {
            (
                row["configuration_code"],
                row["attribute_code"],
                row["fuel_type_code"],
            ): row
            for row in cls.values
        }
        cls.spec_paths = sorted(
            path
            for path in SPEC_DIR.glob("jogger-page6-*-20260401.json")
            if path.name not in {
                "jogger-page6-injection-type-20260401.json",
                "jogger-page6-gearbox-type-20260401.json",
                "jogger-page6-gear-count-20260401.json",
                "jogger-page6-minimum-kerb-weight-20260401.json",
                "jogger-page6-cargo-vda-luggage-cover-20260401.json",
                "jogger-page6-cargo-vda-seatback-20260401.json",
                "jogger-page6-lpg-vessel-capacity-total-20260401.json",
                "jogger-page6-lpg-vessel-filling-capacity-20260401.json",
                "jogger-page6-hybrid-system-power-total-20260401.json",
                "jogger-page6-hybrid-battery-chemistry-20260401.json",
            }
        )

    def test_exact_specification_set_is_versioned(self) -> None:
        self.assertEqual(
            [path.name for path in self.spec_paths],
            [
                "jogger-page6-acceleration-0-100-20260401.json",
                "jogger-page6-braked-trailer-weight-20260401.json",
                "jogger-page6-cylinder-count-20260401.json",
                "jogger-page6-emission-standard-20260401.json",
                "jogger-page6-engine-displacement-20260401.json",
                "jogger-page6-engine-power-20260401.json",
                "jogger-page6-engine-torque-20260401.json",
                "jogger-page6-fuel-tank-capacity-20260401.json",
                "jogger-page6-gross-vehicle-weight-20260401.json",
                "jogger-page6-hybrid-battery-voltage-20260401.json",
                "jogger-page6-max-torque-rpm-20260401.json",
                "jogger-page6-start-stop-system-20260401.json",
                "jogger-page6-starter-generator-power-20260401.json",
                "jogger-page6-top-speed-20260401.json",
                "jogger-page6-total-valve-count-20260401.json",
                "jogger-page6-traction-motor-power-20260401.json",
                "jogger-page6-traction-motor-torque-20260401.json",
            ],
        )
        payloads = [json.loads(path.read_text(encoding="utf-8")) for path in self.spec_paths]
        self.assertTrue(all(payload["version"] == 1 for payload in payloads))
        self.assertTrue(all(payload["source_page"] == 6 for payload in payloads))

    def test_import_has_contiguous_identifiers_and_exact_total(self) -> None:
        self.assertEqual(len(self.values), 312)
        self.assertEqual(
            [int(row["id"]) for row in self.values],
            list(range(725, 1037)),
        )
        self.assertEqual(len(self.by_semantic), 312)

    def test_each_powertrain_uses_selected_source_stated_denominator(self) -> None:
        counts = Counter(row["configuration_code"] for row in self.values)
        self.assertEqual(set(counts), set(self.configurations))
        for code, configuration in self.configurations.items():
            if configuration["powertrain_label"] == "TCe 110":
                expected = 12
            else:
                expected = 15
            self.assertEqual(counts[code], expected, code)

    def test_ecog_preserves_fuel_contexts_and_excludes_lpg_tank_collapse(self) -> None:
        ecog = [
            code
            for code, row in self.configurations.items()
            if row["powertrain_label"] == "Eco-G 120"
        ]
        for code in ecog:
            for attribute in ("engine_power", "engine_torque", "acceleration_0_100"):
                self.assertIn((code, attribute, "lpg"), self.by_semantic)
                self.assertIn((code, attribute, "petrol"), self.by_semantic)
            self.assertIn((code, "fuel_tank_capacity", "petrol"), self.by_semantic)
            self.assertNotIn((code, "fuel_tank_capacity", "lpg"), self.by_semantic)

    def test_seat_dependent_acceleration_and_gross_weight_are_not_flattened(self) -> None:
        expected = {
            ("jogger_essential_5seat_ecog120_manual", "acceleration_0_100", "lpg"): "10.9",
            ("jogger_essential_7seat_ecog120_manual", "acceleration_0_100", "lpg"): "11.0",
            ("jogger_expression_5seat_tce110_manual", "acceleration_0_100", ""): "10.5",
            ("jogger_expression_7seat_tce110_manual", "acceleration_0_100", ""): "11.2",
            ("jogger_expression_5seat_hybrid155_automatic", "gross_vehicle_weight", ""): "1830",
            ("jogger_expression_7seat_hybrid155_automatic", "gross_vehicle_weight", ""): "2000",
        }
        for key, value in expected.items():
            self.assertEqual(self.by_semantic[key]["value"], value)
        for code, row in self.configurations.items():
            if row["powertrain_label"] == "hybrid 155":
                self.assertNotIn((code, "acceleration_0_100", ""), self.by_semantic)

    def test_hybrid_component_values_remain_separate_from_engine_power(self) -> None:
        hybrid = [
            code
            for code, row in self.configurations.items()
            if row["powertrain_label"] == "hybrid 155"
        ]
        expected = {
            "engine_power": "80",
            "engine_torque": "172",
            "max_torque_rpm": "3000",
            "traction_motor_power": "36",
            "starter_generator_power": "15",
            "traction_motor_torque": "205",
            "hybrid_battery_voltage": "200",
        }
        for code in hybrid:
            for attribute, value in expected.items():
                self.assertEqual(self.by_semantic[(code, attribute, "")]["value"], value)
            self.assertNotEqual(self.by_semantic[(code, "engine_power", "")]["value"], "116")

    def test_deferred_ranges_and_semantic_mismatches_are_absent(self) -> None:
        deferred = {
            "co2_emissions",
            "fuel_consumption_combined",
            "maximum_payload",
            "kerb_weight",
            "cargo_volume_vda",
            "boot_capacity",
            "hybrid_battery_capacity",
            "hybrid_battery_type",
            "injection_type",
            "gearbox_type",
            "gear_count",
        }
        self.assertFalse(deferred & {row["attribute_code"] for row in self.values})

    def test_all_rows_retain_page_provenance_and_exact_registered_binary(self) -> None:
        self.assertTrue(PDF.is_file())
        self.assertEqual(PDF.stat().st_size, 2_031_453)
        digest = hashlib.sha256(PDF.read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_SHA)
        self.assertTrue(all(row["source_code"] == SOURCE for row in self.values))
        self.assertTrue(all(row["notes"].startswith("Source page 6, section ") for row in self.values))


if __name__ == "__main__":
    unittest.main()
