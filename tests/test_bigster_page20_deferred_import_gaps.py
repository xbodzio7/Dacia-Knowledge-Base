from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SOURCE = "src_pl_bigster_brochure_20251210"
PDF = ROOT / "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
SPECS = {
    "hybrid_system_power_total": ROOT / "data/imports/configuration_values/bigster-page20-hybrid-system-power-total-20251210.json",
    "traction_motor_torque": ROOT / "data/imports/configuration_values/bigster-page20-traction-motor-torque-20251210.json",
    "hybrid_battery_type": ROOT / "data/imports/configuration_values/bigster-page20-hybrid-battery-type-20251210.json",
}
HYBRID_G = {
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20DeferredImportGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.specs = {code: json.loads(path.read_text(encoding="utf-8")) for code, path in SPECS.items()}
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.active_bigster = {
            row["code"]
            for row in rows(MASTER / "configurations.csv")
            if row["status"] == "active" and row["code"].startswith("bigster_")
        }
        cls.imported = [
            row
            for row in cls.values
            if row["source_code"] == SOURCE
            and row["observation_date"] == "2025-12-10"
            and row["attribute_code"] in SPECS
        ]

    def test_three_strict_specs_preserve_attribute_contracts_and_id_receipts(self) -> None:
        expected = {
            "hybrid_system_power_total": (3282, 3, {"data_type": "decimal", "unit": "kW", "status": "active"}),
            "traction_motor_torque": (3285, 3, {"data_type": "decimal", "unit": "Nm", "status": "active"}),
            "hybrid_battery_type": (3288, 14, {"data_type": "enum", "unit": "", "status": "active"}),
        }
        for attribute, (start, count, contract) in expected.items():
            spec = self.specs[attribute]
            self.assertEqual(spec["kind"], "configuration_attribute_values")
            self.assertEqual(spec["attribute_code"], attribute)
            self.assertEqual(spec["id_start"], start)
            self.assertEqual(spec["attribute_contract"], contract)
            self.assertEqual(len(spec["rows"]), count)
            self.assertEqual(spec["source_page"], 20)
            self.assertEqual(spec["source_section"], "ZUŻYCIE PALIWA I EMISJA CO2")

    def test_exactly_twenty_contiguous_master_rows_match_the_specs(self) -> None:
        selected = sorted(self.imported, key=lambda row: int(row["id"]))
        self.assertEqual([int(row["id"]) for row in selected], list(range(3282, 3302)))
        self.assertEqual(len({row["code"] for row in selected}), 20)
        self.assertEqual(
            Counter(row["attribute_code"] for row in selected),
            Counter({"hybrid_system_power_total": 3, "traction_motor_torque": 3, "hybrid_battery_type": 14}),
        )
        self.assertEqual(
            {row["attribute_code"]: {item["value"] for item in selected if item["attribute_code"] == row["attribute_code"]} for row in selected},
            {
                "hybrid_system_power_total": {"113"},
                "traction_motor_torque": {"87"},
                "hybrid_battery_type": {"lithium_ion"},
            },
        )

    def test_targets_are_exactly_the_reviewed_configuration_sets(self) -> None:
        by_attribute = {
            attribute: {row["configuration_code"] for row in self.imported if row["attribute_code"] == attribute}
            for attribute in SPECS
        }
        self.assertEqual(by_attribute["hybrid_system_power_total"], HYBRID_G)
        self.assertEqual(by_attribute["traction_motor_torque"], HYBRID_G)
        self.assertEqual(by_attribute["hybrid_battery_type"], self.active_bigster)
        self.assertEqual(len(self.active_bigster), 14)

    def test_every_target_has_the_registered_brochure_relationship(self) -> None:
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(self.active_bigster <= linked)

    def test_conflicting_rpm_capacity_and_voltage_observations_are_preserved(self) -> None:
        current = {
            (row["configuration_code"], row["attribute_code"]): row["value"]
            for row in self.values
            if row["source_code"] == "src_pl_bigster_price_my26_20260703"
        }
        for code in HYBRID_G:
            self.assertEqual(current[(code, "max_power_rpm")], "5000")
            self.assertEqual(current[(code, "max_torque_rpm")], "1750")
            self.assertEqual(current[(code, "hybrid_battery_capacity_source_stated")], "0.839")
        hybrid155 = {code for code in self.active_bigster if "hybrid155" in code}
        self.assertEqual(len(hybrid155), 3)
        for code in hybrid155:
            self.assertEqual(current[(code, "hybrid_system_voltage")], "200")
        imported_attributes = {row["attribute_code"] for row in self.imported}
        self.assertTrue(imported_attributes.isdisjoint({"max_power_rpm", "max_torque_rpm", "hybrid_battery_capacity_source_stated", "hybrid_system_voltage"}))

    def test_completeness_scopes_declare_every_new_observed_slot(self) -> None:
        expected = {
            "bigster_mildhybrid140_4x2_manual_completeness.json": {"hybrid_battery_type"},
            "bigster_mildhybridg140_4x2_manual_completeness.json": {"hybrid_battery_type"},
            "bigster_hybrid155_4x2_automatic_completeness.json": {"hybrid_battery_type"},
            "bigster_hybridg150_4x4_automatic_completeness.json": {"hybrid_battery_type", "hybrid_system_power_total", "traction_motor_torque"},
        }
        for filename, required in expected.items():
            payload = json.loads((ROOT / "data/reporting" / filename).read_text(encoding="utf-8"))
            slots = {item["attribute_code"] for item in payload["technical_slots"] if item["fuel_type_code"] == ""}
            self.assertTrue(required <= slots)

    def test_source_page_contains_all_three_atomic_receipts(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        text = " ".join(_compact_text(value) for _, value in extract_page_candidates(PDF, 20))
        for expected in ("113 (150 KM) moc łączna", "87 przy 1630 elektryczny", "Litowo-jonowy"):
            self.assertIn(_compact_text(expected), text)


if __name__ == "__main__":
    unittest.main()
