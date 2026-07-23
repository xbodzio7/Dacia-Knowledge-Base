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
SNAPSHOT = REPOSITORY / "project" / "sources" / "dacia-pl-sandero-stepway-configurations-20260723.json"
SOURCE_CODE = "src_pl_sandero_stepway_official_web_configurations_20260723"
SNAPSHOT_SHA256 = "dd236991cba2f14f2b49e43cddbcf643741e6609dd5c2f4dbb0bb6e9dbf98ed3"


class SanderoStepwayOfficialWeb20260723Tests(unittest.TestCase):
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

    def test_source_relationships_cover_exact_model_versions_and_configurations(self) -> None:
        self.assertEqual(
            {(row["model_code"], row["relationship"]) for row in self.source_rows("source_models.csv")},
            {("sandero_stepway_iii", "web_configuration_for")},
        )
        self.assertEqual(
            {row["version_code"] for row in self.source_rows("source_versions.csv")},
            {
                "sandero_stepway_iii_essential",
                "sandero_stepway_iii_expression",
                "sandero_stepway_iii_extreme",
            },
        )
        self.assertEqual(
            {row["configuration_code"] for row in self.source_rows("source_configurations.csv")},
            {
                "sandero_stepway_iii_essential_ecog120_manual",
                "sandero_stepway_iii_expression_ecog120_manual",
                "sandero_stepway_iii_expression_ecog120_automatic",
                "sandero_stepway_iii_extreme_ecog120_manual",
                "sandero_stepway_iii_extreme_ecog120_automatic",
            },
        )

    def test_five_exact_official_catalogue_prices_are_imported(self) -> None:
        actual = {
            row["configuration_code"]: (int(row["amount"]), row["price_date"], row["price_type"])
            for row in self.source_rows("configuration_prices.csv")
        }
        self.assertEqual(
            actual,
            {
                "sandero_stepway_iii_essential_ecog120_manual": (71700, "2026-07-23", "catalog_gross"),
                "sandero_stepway_iii_expression_ecog120_manual": (76400, "2026-07-23", "catalog_gross"),
                "sandero_stepway_iii_expression_ecog120_automatic": (83300, "2026-07-23", "catalog_gross"),
                "sandero_stepway_iii_extreme_ecog120_manual": (82500, "2026-07-23", "catalog_gross"),
                "sandero_stepway_iii_extreme_ecog120_automatic": (89400, "2026-07-23", "catalog_gross"),
            },
        )

    def test_version_highlights_expand_to_24_exact_standard_observations(self) -> None:
        observations = self.source_rows("configuration_attribute_availability.csv")
        self.assertEqual(len(observations), 24)
        self.assertEqual({row["availability_status"] for row in observations}, {"standard"})
        self.assertEqual({row["observation_date"] for row in observations}, {"2026-07-23"})

        previous_pairs = {
            (row["configuration_code"], row["attribute_code"])
            for row in self.rows("configuration_attribute_availability.csv")
            if row["source_code"] != SOURCE_CODE
        }
        newly_covered = {
            (row["configuration_code"], row["attribute_code"])
            for row in observations
            if (row["configuration_code"], row["attribute_code"]) not in previous_pairs
        }
        self.assertEqual(
            newly_covered,
            {
                ("sandero_stepway_iii_essential_ecog120_manual", "roof_rails"),
                ("sandero_stepway_iii_essential_ecog120_manual", "my_safety_button"),
                ("sandero_stepway_iii_expression_ecog120_manual", "fog_lights_front"),
                ("sandero_stepway_iii_expression_ecog120_manual", "modular_roof_rails"),
                ("sandero_stepway_iii_expression_ecog120_automatic", "fog_lights_front"),
                ("sandero_stepway_iii_expression_ecog120_automatic", "modular_roof_rails"),
            },
        )

    def test_default_tce110_media_display_package_is_preserved_but_not_imported_to_ecog(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        observation = payload["configurator_observation"]
        self.assertEqual(observation["visible_default_configuration"], "NOWE SANDERO STEPWAY essential stepway TCe 110 f.2")
        self.assertEqual(
            observation["visible_optional_items"],
            [{
                "name": "pakiet MEDIA DISPLAY",
                "price_pln": 1900,
                "imported_to_master": False,
                "reason": "The visible configurator state is TCe 110 manual. The page does not prove package applicability to the active Eco-G 120 configuration.",
            }],
        )
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
            [sys.executable, "tools/import_sandero_stepway_official_web_20260723.py", "--check"],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: Sandero Stepway official web configuration contract", result.stdout)


if __name__ == "__main__":
    unittest.main()
