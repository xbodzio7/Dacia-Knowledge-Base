from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "project" / "sources" / "sandero_stepway_price_my26_20261102_import_spec.json"
SCRIPT_PATH = ROOT / "tools" / "import_sandero_stepway_price_list_20261102.py"
MASTER = ROOT / "data" / "master"


def read_rows(filename: str) -> list[dict[str, str]]:
    with (MASTER / filename).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoStepwayPriceList20261102Tests(unittest.TestCase):
    def test_sandero_20261102_cennik_package_contract(self) -> None:
        spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("contract: PASS", result.stdout)

        source = next(
            row for row in read_rows("sources.csv")
            if row["code"] == "src_pl_sandero_stepway_price_my26_20261102"
        )
        self.assertEqual(source["document_date"], "2026-11-02")
        self.assertEqual(source["market"], "PL")
        self.assertTrue(source["external_reference"].endswith("/3b4618d7da.pdf"))
        self.assertEqual(source["file_path"], "owner_supplied/2026-11-02/3b4618d7da.pdf")
        self.assertEqual(source["sha256"], "8ee10aaf69a7807655d3fd9251fc999b7192a2b239ae865ea0e7f9e58dbbf28c")

        source_code = source["code"]
        config_links = [
            row for row in read_rows("source_configurations.csv")
            if row["source_code"] == source_code
        ]
        version_links = [
            row for row in read_rows("source_versions.csv")
            if row["source_code"] == source_code
        ]
        self.assertEqual(len(config_links), 19)
        self.assertEqual(len(version_links), 6)

        technical = [
            row for row in read_rows("configuration_attribute_values.csv")
            if row["source_code"] == source_code
        ]
        self.assertEqual(len(technical), 93)
        page3 = [row for row in technical if "PDF page 3" in row["notes"]]
        page4 = [row for row in technical if "page 4" in row["notes"]]
        page5 = [row for row in technical if "page 5" in row["notes"]]
        self.assertEqual((len(page3), len(page4), len(page5)), (24, 42, 27))
        self.assertEqual(
            Counter(row["attribute_code"] for row in page3),
            Counter({
                "wheel_size": 4,
                "wheel_material": 4,
                "wheel_design": 4,
                "wheel_finish": 4,
                "upholstery_variant": 4,
                "centre_console_variant": 4,
            }),
        )
        self.assertEqual(
            Counter(row["attribute_code"] for row in page4),
            Counter({
                "fuel_consumption_combined": 8,
                "co2_emissions": 9,
                "cargo_volume_vda": 9,
                "injection_type": 4,
                "acceleration_0_100": 4,
                "electric_motor_torque": 4,
                "electric_motor_torque_rpm": 4,
            }),
        )
        self.assertEqual(
            Counter(row["attribute_code"] for row in page5),
            Counter({
                "overall_width": 9,
                "overall_length": 2,
                "overall_width_with_mirrors": 2,
                "overall_height": 2,
                "front_track": 2,
                "rear_track": 2,
                "front_overhang": 2,
                "rear_overhang": 2,
                "wheelbase": 2,
                "ground_clearance": 2,
            }),
        )
        self.assertFalse(
            any(row["attribute_code"] == "fuel_tank_capacity" for row in page4),
            "Ambiguous Eco-G LPG total/fillable capacity must remain deferred.",
        )
        injection_rows = [row for row in page4 if row["attribute_code"] == "injection_type"]
        self.assertEqual(len(injection_rows), 4)
        self.assertTrue(all(row["value"] == "multi_point_injection" for row in injection_rows))
        eco_boot_rows = [row for row in page4 if row["attribute_code"] == "cargo_volume_vda"]
        self.assertEqual(len(eco_boot_rows), 9)
        self.assertTrue(all(row["value"] == "328" for row in eco_boot_rows))
        hybrid_motor_torque = [row for row in page4 if row["attribute_code"] == "electric_motor_torque"]
        self.assertEqual(len(hybrid_motor_torque), 4)
        self.assertTrue(all(row["value"] == "205" for row in hybrid_motor_torque))

        equipment = [
            row for row in read_rows("configuration_attribute_availability.csv")
            if row["source_code"] == source_code
        ]
        self.assertEqual(len(equipment), 27)
        self.assertEqual(
            Counter(row["attribute_code"] for row in equipment),
            Counter({
                "rear_view_camera": 1,
                "360_camera_system": 2,
                "glass_sunroof": 1,
                "heated_front_seats": 4,
                "heated_steering_wheel": 2,
                "automatic_climate_control": 2,
                "manual_air_conditioning": 2,
                "electronic_parking_brake": 1,
                "front_seat_belt_pretensioners": 4,
                "rear_seat_belt_pretensioners": 4,
                "isofix_rear": 4,
            }),
        )
        self.assertEqual(
            Counter(row["availability_status"] for row in equipment),
            Counter({"optional": 12, "not_available": 3, "standard": 12}),
        )
        self.assertFalse(
            any(row["attribute_code"] == "fuel_tank_capacity" for row in equipment)
        )
        manual_ac = [row for row in equipment if row["attribute_code"] == "manual_air_conditioning"]
        self.assertTrue(all(row["availability_status"] == "not_available" for row in manual_ac))
        camera = [row for row in equipment if row["attribute_code"] == "rear_view_camera"]
        self.assertEqual(len(camera), 1)
        self.assertEqual(camera[0]["availability_status"], "optional")

        old_prices = {
            row["configuration_code"]: int(row["amount"])
            for row in read_rows("configuration_prices.csv")
            if row["source_code"] == "src_pl_sandero_stepway_price_my26_20260811"
        }
        new_prices = [
            row for row in read_rows("configuration_prices.csv")
            if row["source_code"] == source_code
        ]
        self.assertEqual(len(new_prices), 15)
        for row in new_prices:
            self.assertEqual(
                int(row["amount"]) - old_prices[row["configuration_code"]], 500
            )
            self.assertEqual(row["price_date"], "2026-11-02")
            self.assertEqual(row["price_type"], "catalog_gross")
        for row in spec["unchanged_price_confirmations"]:
            self.assertEqual(old_prices[row["configuration_code"]], row["amount"])
            self.assertNotIn(
                row["configuration_code"],
                {item["configuration_code"] for item in new_prices},
            )

        new_item_codes = {
            "sandero_metallic_paint_option",
            "sandero_special_nonmetallic_paint_option",
            "sandero_spare_wheel_option",
        }
        items = read_rows("commercial_items.csv")
        self.assertEqual(
            {row["code"] for row in items if row["code"] in new_item_codes},
            new_item_codes,
        )
        mappings = [
            row for row in read_rows("commercial_item_configurations.csv")
            if row["source_code"] == source_code
        ]
        self.assertEqual(len(mappings), 209)
        self.assertEqual(
            Counter(row["availability_status"] for row in mappings),
            Counter({"optional": 98, "not_available": 99, "standard": 12}),
        )
        by_item: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in mappings:
            by_item[row["commercial_item_code"]].append(row)
        self.assertEqual(len(by_item), 11)
        self.assertTrue(all(len(rows) == 19 for rows in by_item.values()))

        expected_statuses = {
            "sandero_metallic_paint_option": {"optional": 19},
            "sandero_special_nonmetallic_paint_option": {"optional": 19},
            "sandero_spare_wheel_option": {"optional": 10, "not_available": 9},
            "sandero_rear_view_camera_option": {"optional": 4, "standard": 12, "not_available": 3},
            "sandero_media_nav_live_option": {"optional": 8, "not_available": 11},
            "sandero_glass_sunroof_option": {"optional": 4, "not_available": 15},
            "sandero_comfort_auto_package": {"optional": 2, "not_available": 17},
            "sandero_thermo_package": {"optional": 8, "not_available": 11},
            "sandero_winter_package": {"optional": 8, "not_available": 11},
            "sandero_media_nav_live_package": {"optional": 8, "not_available": 11},
            "sandero_easy_package": {"optional": 8, "not_available": 11},
        }
        for item_code, expected in expected_statuses.items():
            self.assertEqual(
                dict(Counter(row["availability_status"] for row in by_item[item_code])),
                expected,
                item_code,
            )

        self.assertEqual(
            Counter(row["amount"] for row in by_item["sandero_special_nonmetallic_paint_option"]),
            Counter({"2600": 11, "2800": 8}),
        )
        self.assertTrue(
            all(row["amount"] == "2600" for row in by_item["sandero_metallic_paint_option"])
        )
        self.assertTrue(
            all(row["amount"] == "800" for row in by_item["sandero_spare_wheel_option"] if row["availability_status"] == "optional")
        )
        self.assertEqual(spec["expected"]["configurations"], 19)
        self.assertEqual(spec["expected"]["catalogue_price_changes"], 15)
        self.assertEqual(spec["expected"]["commercial_mappings"], 209)


if __name__ == "__main__":
    unittest.main()
