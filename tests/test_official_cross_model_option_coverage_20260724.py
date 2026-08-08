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
SNAPSHOT = REPOSITORY / "project" / "sources" / "dacia-pl-cross-model-option-coverage-20260724.json"
SOURCE_CODE = "src_pl_cross_model_option_coverage_20260724"
SNAPSHOT_SHA256 = "283dcb96119804f6f100ba3d7c93d968f862aa06667a681198cb7bb77e24cf63"

sys.path.insert(0, str(REPOSITORY / "tools"))
from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402
from reporting.configuration_shortlist_html import collect_browser_catalog  # noqa: E402


class OfficialCrossModelOptionCoverage20260724Tests(unittest.TestCase):
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
        self.assertEqual(source[0]["document_date"], "2026-07-24")
        self.assertEqual(payload["volatility"], "dynamic_official_web")
        self.assertEqual(payload["source_code"], SOURCE_CODE)

    def test_source_relationships_cover_exact_imported_grades_and_configurations(self) -> None:
        self.assertEqual(
            {row["model_code"] for row in self.source_rows("source_models.csv")},
            {"sandero_iii", "sandero_stepway_iii", "jogger"},
        )
        self.assertEqual(len(self.source_rows("source_versions.csv")), 9)
        self.assertEqual(len(self.source_rows("source_configurations.csv")), 31)
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        expected_versions = {item["version_code"] for item in payload["version_observations"]}
        expected_configurations = {
            code
            for item in payload["version_observations"]
            for code in item["configurations"]
        }
        self.assertEqual(
            {row["version_code"] for row in self.source_rows("source_versions.csv")},
            expected_versions,
        )
        self.assertEqual(
            {row["configuration_code"] for row in self.source_rows("source_configurations.csv")},
            expected_configurations,
        )

    def test_factory_antenna_coverage_contains_31_exact_observations(self) -> None:
        rows = [
            row for row in self.source_rows("configuration_attribute_availability.csv")
            if row["attribute_code"] == "shark_fin_antenna"
        ]
        self.assertEqual(len(rows), 31)
        self.assertEqual(
            {row["availability_status"] for row in rows},
            {"standard", "not_available"},
        )
        negatives = {
            row["configuration_code"] for row in rows
            if row["availability_status"] == "not_available"
        }
        self.assertEqual(
            negatives,
            {
                "sandero_stepway_iii_essential_ecog120_manual",
                "jogger_essential_5seat_ecog120_manual",
                "jogger_essential_7seat_ecog120_manual",
            },
        )
        self.assertTrue(all(row["observation_date"] == "2026-07-24" for row in rows))

    def test_jogger_journey_folding_mirror_history_is_preserved_and_corrected(self) -> None:
        journey_codes = {
            "jogger_journey_5seat_ecog120_automatic",
            "jogger_journey_5seat_hybrid155_automatic",
            "jogger_journey_5seat_tce110_manual",
            "jogger_journey_7seat_ecog120_automatic",
            "jogger_journey_7seat_hybrid155_automatic",
            "jogger_journey_7seat_tce110_manual",
        }
        all_rows = [
            row for row in self.rows("configuration_attribute_availability.csv")
            if row["configuration_code"] in journey_codes
            and row["attribute_code"] == "side_mirrors_folding"
        ]
        historical = [row for row in all_rows if row["observation_date"] == "2026-04-01"]
        current = [row for row in all_rows if row["source_code"] == SOURCE_CODE]
        self.assertEqual(len(historical), 6)
        self.assertEqual({row["availability_status"] for row in historical}, {"not_available"})
        self.assertEqual(len(current), 6)
        self.assertEqual({row["availability_status"] for row in current}, {"standard"})
        self.assertEqual({row["configuration_code"] for row in current}, journey_codes)

    def test_browser_catalog_uses_latest_journey_folding_mirror_observation(self) -> None:
        catalog = collect_browser_catalog(REPOSITORY, ShortlistCriteria())
        journey = [
            item for item in catalog["configurations"]
            if item["version_code"] == "jogger_journey"
        ]
        self.assertEqual(len(journey), 6)
        for item in journey:
            state = item["equipment"]["side_mirrors_folding"]
            self.assertEqual(state["availability_status"], "standard")
            self.assertEqual(state["observation_date"], "2026-07-24")
            self.assertEqual(state["source_code"], SOURCE_CODE)

    def test_existing_exact_package_mappings_are_not_broadened(self) -> None:
        mappings = self.rows("commercial_item_configurations.csv")
        sandero_easy = [
            row for row in mappings
            if row["commercial_item_code"] == "sandero_easy_package"
        ]
        jogger_drive = [
            row for row in mappings
            if row["commercial_item_code"] == "jogger_drive_package"
        ]
        self.assertEqual(len(sandero_easy), 12)
        self.assertEqual(
            {row["amount"] for row in sandero_easy if row["price_date"] == "2026-07-03"},
            {"1600"},
        )
        self.assertEqual(
            {row["amount"] for row in sandero_easy if row["price_date"] == "2026-08-09"},
            {"1400"},
        )
        self.assertEqual(
            {row["configuration_code"] for row in sandero_easy},
            {
                "sandero_iii_journey_tce100_manual",
                "sandero_iii_journey_ecog120_manual",
                "sandero_iii_journey_ecog120_automatic",
                "sandero_stepway_iii_extreme_tce110_manual",
                "sandero_stepway_iii_extreme_ecog120_manual",
                "sandero_stepway_iii_extreme_ecog120_automatic",
            },
        )
        self.assertEqual(len(jogger_drive), 8)
        self.assertEqual(
            [row for row in self.rows("commercial_items.csv") if row.get("source_code") == SOURCE_CODE],
            [],
        )
        self.assertEqual(
            [row for row in mappings if row.get("source_code") == SOURCE_CODE],
            [],
        )

    def test_bigster_is_unchanged_and_duster_remains_explicit_non_import(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(payload["existing_coverage_reviews"][0]["model_code"], "bigster")
        duster = next(
            item for item in payload["non_import_reviews"]
            if item.get("model_code") == "duster_iii"
        )
        self.assertEqual(duster["result"], "no_exact_configuration_import")
        self.assertEqual(duster["preserved_state"], "missing records remain unimported and therefore unknown")

        source_availability = self.source_rows("configuration_attribute_availability.csv")
        self.assertFalse(any(row["configuration_code"].startswith("duster_iii_") for row in source_availability))
        self.assertFalse(any(row["configuration_code"].startswith("bigster_") for row in source_availability))

        all_rows = self.rows("configuration_attribute_availability.csv")
        bigster_shark = [
            row for row in all_rows
            if row["configuration_code"].startswith("bigster_")
            and row["attribute_code"] == "shark_fin_antenna"
        ]
        bigster_folding = [
            row for row in all_rows
            if row["configuration_code"].startswith("bigster_")
            and row["attribute_code"] == "side_mirrors_folding"
        ]
        self.assertEqual(len(bigster_shark), 14)
        self.assertEqual(len(bigster_folding), 14)

    def test_importer_check_reproduces_master_contract(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "tools/import_official_cross_model_option_coverage_20260724.py",
                "--check",
            ],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: official cross-model option coverage contract", result.stdout)


if __name__ == "__main__":
    unittest.main()
