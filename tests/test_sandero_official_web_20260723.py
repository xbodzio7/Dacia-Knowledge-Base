from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
SNAPSHOT = REPOSITORY / "project" / "sources" / "dacia-pl-sandero-configurations-20260723.json"
SOURCE_CODE = "src_pl_sandero_official_web_configurations_20260723"
SNAPSHOT_SHA256 = "e02eb11d31cf7dc00bc29eb112d3b59c33e0fb08cab31c375410add981599f68"


class SanderoOfficialWeb20260723Tests(unittest.TestCase):
    def rows(self, name: str) -> list[dict[str, str]]:
        with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def source_rows(self, name: str) -> list[dict[str, str]]:
        if name == "sources.csv":
            return [row for row in self.rows(name) if row["code"] == SOURCE_CODE]
        return [row for row in self.rows(name) if row.get("source_code") == SOURCE_CODE]

    def test_snapshot_is_registered_with_exact_hash_and_dynamic_boundary(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        source = self.source_rows("sources.csv")
        self.assertEqual(len(source), 1)
        self.assertEqual(hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(), SNAPSHOT_SHA256)
        self.assertEqual(source[0]["sha256"], SNAPSHOT_SHA256)
        self.assertEqual(source[0]["source_type"], "web_snapshot")
        self.assertEqual(source[0]["document_date"], "2026-07-23")
        self.assertEqual(payload["volatility"], "dynamic_official_web")
        self.assertEqual(payload["source_code"], SOURCE_CODE)

    def test_two_official_automatic_configurations_are_active(self) -> None:
        configurations = {row["code"]: row for row in self.rows("configurations.csv")}
        expected = {
            "sandero_iii_expression_ecog120_automatic": "sandero_iii_expression",
            "sandero_iii_journey_ecog120_automatic": "sandero_iii_journey",
        }
        for code, version_code in expected.items():
            row = configurations[code]
            self.assertEqual(row["version_code"], version_code)
            self.assertEqual(row["powertrain_label"], "Eco-G 120")
            self.assertEqual(row["transmission_type"], "automatic")
            self.assertEqual(row["status"], "active")

    def test_source_relationships_cover_exact_model_versions_and_configurations(self) -> None:
        self.assertEqual(
            {(row["model_code"], row["relationship"]) for row in self.source_rows("source_models.csv")},
            {("sandero_iii", "web_configuration_for")},
        )
        self.assertEqual(
            {row["version_code"] for row in self.source_rows("source_versions.csv")},
            {"sandero_iii_expression", "sandero_iii_journey"},
        )
        self.assertEqual(
            {row["configuration_code"] for row in self.source_rows("source_configurations.csv")},
            {
                "sandero_iii_expression_ecog120_manual",
                "sandero_iii_expression_ecog120_automatic",
                "sandero_iii_journey_ecog120_manual",
                "sandero_iii_journey_ecog120_automatic",
            },
        )

    def test_four_exact_official_catalogue_prices_are_imported(self) -> None:
        actual = {
            row["configuration_code"]: (int(row["amount"]), row["price_date"], row["price_type"])
            for row in self.source_rows("configuration_prices.csv")
        }
        self.assertEqual(
            actual,
            {
                "sandero_iii_expression_ecog120_manual": (68000, "2026-07-23", "catalog_gross"),
                "sandero_iii_expression_ecog120_automatic": (74900, "2026-07-23", "catalog_gross"),
                "sandero_iii_journey_ecog120_manual": (73600, "2026-07-23", "catalog_gross"),
                "sandero_iii_journey_ecog120_automatic": (80500, "2026-07-23", "catalog_gross"),
            },
        )

    def test_version_highlights_expand_to_16_exact_standard_observations(self) -> None:
        observations = self.source_rows("configuration_attribute_availability.csv")
        self.assertEqual(len(observations), 16)
        self.assertEqual({row["availability_status"] for row in observations}, {"standard"})
        self.assertEqual({row["observation_date"] for row in observations}, {"2026-07-23"})
        automatic = {
            (row["configuration_code"], row["attribute_code"])
            for row in observations
            if row["configuration_code"].endswith("_automatic")
        }
        self.assertEqual(
            automatic,
            {
                ("sandero_iii_expression_ecog120_automatic", "manual_air_conditioning"),
                ("sandero_iii_expression_ecog120_automatic", "media_display_system"),
                ("sandero_iii_expression_ecog120_automatic", "rear_view_camera"),
                ("sandero_iii_expression_ecog120_automatic", "front_centre_armrest"),
                ("sandero_iii_journey_ecog120_automatic", "automatic_climate_control"),
                ("sandero_iii_journey_ecog120_automatic", "keyless_entry"),
                ("sandero_iii_journey_ecog120_automatic", "instrument_cluster_colour_7"),
                ("sandero_iii_journey_ecog120_automatic", "media_display_system"),
            },
        )

    def test_unproven_packages_and_default_tce_options_are_not_mapped_to_new_automatic_states(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["configurator_observation"]["visible_default_configuration"],
            "NOWE SANDERO essential TCe 100 F.2",
        )
        self.assertTrue(all(not item["imported_to_ecog_master"] for item in payload["configurator_observation"]["visible_optional_items"]))
        self.assertTrue(all(
            not item["imported_to_new_configuration"]
            for version in payload["version_observations"]
            for item in version["unassigned_version_items"]
        ))
        source_commercial_items = [
            row for row in self.rows("commercial_items.csv") if row.get("source_code") == SOURCE_CODE
        ]
        source_commercial_mappings = [
            row for row in self.rows("commercial_item_configurations.csv") if row.get("source_code") == SOURCE_CODE
        ]
        self.assertEqual(source_commercial_items, [])
        self.assertEqual(source_commercial_mappings, [])

    def test_importer_check_reproduces_master_contract(self) -> None:
        result = subprocess.run(
            [sys.executable, "tools/import_sandero_official_web_20260723.py", "--check"],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: Sandero official web configuration contract", result.stdout)


if __name__ == "__main__":
    unittest.main()
