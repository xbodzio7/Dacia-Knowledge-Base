from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src_pl_spring_brochure_20260219"
DATE = "2026-02-19"
CONFIGURATIONS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}


def rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringTechnical20260219Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = [
            row for row in rows("data/master/configuration_attribute_values.csv")
            if row["source_code"] == SOURCE and row["observation_date"] == DATE
            and row["configuration_code"] in CONFIGURATIONS
            and row["id"].isdigit() and 3499 <= int(row["id"]) <= 3552
        ]
        cls.contexts = [
            row for row in rows("data/master/configuration_cargo_volume_contexts.csv")
            if row["configuration_attribute_value_code"].startswith("spring_")
            and row["configuration_attribute_value_code"].endswith("_boot_capacity_20260219")
        ]
        cls.ranges = [
            row for row in rows("data/master/configuration_attribute_value_ranges.csv")
            if row["source_code"] == SOURCE and row["observation_date"] == DATE
            and row["configuration_code"] in CONFIGURATIONS
            and row["attribute_code"] == "max_power_rpm"
        ]

    def test_importer_check_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, "tools/import_spring_technical_20260219.py", "--check"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_row_counts_and_suffixes(self) -> None:
        self.assertEqual(len(self.values), 54)
        self.assertEqual(len(self.ranges), 3)
        self.assertEqual(len(self.contexts), 3)
        self.assertEqual(sorted(int(row["id"]) for row in self.values), list(range(3499, 3553)))
        self.assertEqual(sorted(int(row["id"]) for row in self.ranges), [299, 300, 301])
        self.assertEqual(sorted(int(row["id"]) for row in self.contexts), [318, 319, 320])

    def test_each_configuration_has_eighteen_values_and_one_range(self) -> None:
        for code in CONFIGURATIONS:
            self.assertEqual(sum(row["configuration_code"] == code for row in self.values), 18)
            self.assertEqual(sum(row["configuration_code"] == code for row in self.ranges), 1)

    def test_grade_bounded_values(self) -> None:
        lookup = {(row["configuration_code"], row["attribute_code"]): row["value"] for row in self.values}
        self.assertEqual(lookup[("spring_essential_electric70_automatic", "electric_motor_power")], "52")
        self.assertEqual(lookup[("spring_expression_electric70_automatic", "electric_motor_power")], "52")
        self.assertEqual(lookup[("spring_extreme_electric100_automatic", "electric_motor_power")], "75")
        self.assertEqual(lookup[("spring_essential_electric70_automatic", "combined_range")], "222")
        self.assertEqual(lookup[("spring_expression_electric70_automatic", "combined_range")], "225")
        self.assertEqual(lookup[("spring_extreme_electric100_automatic", "acceleration_0_100")], "9.6")

    def test_power_rpm_ranges_preserve_endpoints(self) -> None:
        lookup = {row["configuration_code"]: row for row in self.ranges}
        self.assertEqual((lookup["spring_essential_electric70_automatic"]["minimum_value"], lookup["spring_essential_electric70_automatic"]["maximum_value"]), ("3625", "12000"))
        self.assertEqual((lookup["spring_expression_electric70_automatic"]["minimum_value"], lookup["spring_expression_electric70_automatic"]["maximum_value"]), ("3625", "12000"))
        self.assertEqual((lookup["spring_extreme_electric100_automatic"]["minimum_value"], lookup["spring_extreme_electric100_automatic"]["maximum_value"]), ("5228", "12000"))
        self.assertTrue(all(row["lower_inclusive"] == "true" and row["upper_inclusive"] == "true" for row in self.ranges))

    def test_boot_capacity_has_exact_iso_context(self) -> None:
        self.assertTrue(all(row["measurement_basis_code"] == "vda_iso_3832" for row in self.contexts))
        self.assertTrue(all(row["second_row_state_code"] == "upright" for row in self.contexts))
        self.assertTrue(all(row["compartment_code"] == "main_luggage_compartment" for row in self.contexts))
        self.assertTrue(all(not row["spare_wheel_state_code"] and not row["tyre_repair_kit_state_code"] for row in self.contexts))

    def test_ambiguous_fields_remain_unimported(self) -> None:
        excluded = {
            "engine_torque", "max_torque_rpm", "battery_capacity_gross",
            "battery_capacity_net", "energy_consumption_combined", "city_range",
            "dc_charging_time", "dc_charging_supported", "overall_length",
            "overall_width", "overall_height",
        }
        self.assertFalse({row["attribute_code"] for row in self.values} & excluded)
        self.assertFalse({row["attribute_code"] for row in self.ranges} & excluded)

    def test_completeness_scope_is_exact(self) -> None:
        payload = json.loads((ROOT / "data/reporting/spring_electric70_automatic_completeness.json").read_text(encoding="utf-8"))
        self.assertEqual([item["configuration_code"] for item in payload["configurations"]], [
            "spring_essential_electric70_automatic",
            "spring_expression_electric70_automatic",
        ])
        self.assertEqual(len(payload["technical_slots"]), 19)
        self.assertEqual(len(payload["equipment_attributes"]), 42)
        self.assertEqual(payload["not_applicable"], {"technical": [], "equipment": []})

    def test_repository_baselines_and_reconciliation_preserve_spring_counts(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 3604)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 316)
        reconciliation = json.loads((ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json").read_text(encoding="utf-8"))
        counts = reconciliation["summary"]["active_evidence_record_counts"]
        self.assertEqual(counts["configuration_attribute_values"], 3490)
        self.assertEqual(counts["configuration_attribute_value_ranges"], 316)


if __name__ == "__main__":
    unittest.main()
