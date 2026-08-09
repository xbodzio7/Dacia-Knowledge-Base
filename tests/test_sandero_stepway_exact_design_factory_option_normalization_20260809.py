from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
CAPTURE = (
    ROOT
    / "project/sources/dacia-pl-sandero-stepway-exact-configurator-states-20260809.json"
)
SOURCE_CODE = "src_pl_sandero_stepway_exact_configurator_states_20260809"
DATE = "2026-08-09"

OPTION_ITEMS = {
    "NA487": "sandero_media_nav_live_option",
    "PCU20": "sandero_media_display_package",
    "PCU64": "sandero_media_nav_live_package",
    "PCU66": "sandero_winter_package",
    "PCU68": "sandero_easy_package",
    "PCV0Y": "sandero_comfort_auto_package",
    "PCV12": "sandero_thermo_package",
    "RRCAM": "sandero_rear_view_camera_option",
    "TOELEC": "sandero_glass_sunroof_option",
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoStepwayExactDesignFactoryOptionNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
        cls.sources = read_csv("sources.csv")
        cls.source_configurations = read_csv("source_configurations.csv")
        cls.items = read_csv("commercial_items.csv")
        cls.item_attributes = read_csv("commercial_item_attributes.csv")
        cls.mappings = read_csv("commercial_item_configurations.csv")
        cls.values = read_csv("configuration_attribute_values.csv")

    def test_deterministic_import_verifier_passes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "tools/import_sandero_stepway_exact_configurator_states_20260809.py",
                "--verify",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_source_and_all_exact_configuration_relationships_are_registered(self) -> None:
        source = next(row for row in self.sources if row["code"] == SOURCE_CODE)
        self.assertEqual(source["document_date"], DATE)
        self.assertEqual(source["file_path"], CAPTURE.relative_to(ROOT).as_posix())
        self.assertEqual(source["sha256"], hashlib.sha256(CAPTURE.read_bytes()).hexdigest())
        expected = {
            configuration["configuration_code"]
            for configuration in self.capture["configurations"]
        }
        observed = {
            row["configuration_code"]
            for row in self.source_configurations
            if row["source_code"] == SOURCE_CODE
        }
        self.assertEqual(observed, expected)

    def test_exact_colour_membership_is_normalized_without_inferred_prices(self) -> None:
        colour_items = {
            row["commercial_item_code"]: row["source_text"]
            for row in self.item_attributes
            if row["attribute_code"] == "exterior_color"
            and row["code"].startswith("sandero_stepway_colour_")
        }
        self.assertEqual(len(colour_items), 9)
        current = [
            row
            for row in self.mappings
            if row["source_code"] == SOURCE_CODE
            and row["commercial_item_code"] in colour_items
        ]
        self.assertEqual(len(current), 93)
        for configuration in self.capture["configurations"]:
            rows = [
                row
                for row in current
                if row["configuration_code"] == configuration["configuration_code"]
            ]
            observed = {colour_items[row["commercial_item_code"]] for row in rows}
            self.assertEqual(observed, set(configuration["colours"]))
            selected = [row for row in rows if row["availability_status"] == "standard"]
            self.assertEqual(len(selected), 1)
            self.assertEqual(colour_items[selected[0]["commercial_item_code"]], configuration["selected_colour"])
            self.assertEqual((selected[0]["amount"], selected[0]["price_date"]), ("0", DATE))
            for row in rows:
                if row not in selected:
                    self.assertEqual((row["amount"], row["price_date"]), ("", ""))

    def test_all_nonzero_factory_options_keep_exact_current_amounts(self) -> None:
        expected = {}
        for configuration in self.capture["configurations"]:
            for option in configuration["factory_options"]:
                amount = int("".join(character for character in option["price_text"] if character.isdigit()))
                if amount:
                    expected[(configuration["configuration_code"], OPTION_ITEMS[option["source_item_code"]])] = str(amount)
        current = {
            (row["configuration_code"], row["commercial_item_code"]): row
            for row in self.mappings
            if row["source_code"] == SOURCE_CODE
            and row["commercial_item_code"] in set(OPTION_ITEMS.values())
        }
        self.assertEqual(len(expected), 40)
        self.assertEqual(set(current), set(expected))
        for key, amount in expected.items():
            self.assertEqual(current[key]["amount"], amount)
            self.assertEqual(current[key]["price_date"], DATE)
            self.assertEqual(current[key]["availability_status"], "optional")

    def test_current_easy_price_supersedes_but_does_not_delete_history(self) -> None:
        current = [
            row for row in self.mappings
            if row["commercial_item_code"] == "sandero_easy_package"
            and row["source_code"] == SOURCE_CODE
        ]
        historical = [
            row for row in self.mappings
            if row["commercial_item_code"] == "sandero_easy_package"
            and row["source_code"] == "src_pl_sandero_stepway_price_my26_20260703"
        ]
        self.assertEqual(len(current), 6)
        self.assertEqual({row["amount"] for row in current}, {"1400"})
        self.assertEqual(len(historical), 6)
        self.assertEqual({row["amount"] for row in historical}, {"1600"})

    def test_selected_wheel_and_upholstery_values_are_exact_for_all_states(self) -> None:
        current = [row for row in self.values if row["source_code"] == SOURCE_CODE]
        self.assertEqual(len(current), 60)
        for configuration in self.capture["configurations"]:
            rows = {
                row["attribute_code"]: row["value"]
                for row in current
                if row["configuration_code"] == configuration["configuration_code"]
            }
            self.assertEqual(set(rows), {"wheel_size", "wheel_material", "wheel_design", "upholstery_variant"})
            expected_design = configuration["selected_wheel"].split()[-1]
            if configuration["selected_wheel"].endswith("TAMIA BLACK"):
                expected_design = "TAMIA BLACK"
            self.assertEqual(rows["wheel_design"], expected_design)
            self.assertEqual(rows["upholstery_variant"], configuration["selected_upholstery"].removeprefix("tapicerka ").removeprefix("Tapicerka "))
        essential_designs = {
            row["value"] for row in current
            if row["attribute_code"] == "wheel_design"
            and row["configuration_code"].startswith("sandero_stepway_iii_essential_")
        }
        self.assertEqual(essential_designs, {"ERALIA"})

    def test_master_row_counts_match_the_closed_package(self) -> None:
        self.assertGreaterEqual(len(self.sources), 37)
        self.assertEqual(len(self.source_configurations), 269)
        self.assertEqual(len(self.items), 50)
        self.assertEqual(len(self.item_attributes), 103)
        self.assertEqual(len(self.mappings), 322)
        self.assertEqual(len(self.values), 3664)


if __name__ == "__main__":
    unittest.main()
