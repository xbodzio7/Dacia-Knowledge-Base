from __future__ import annotations

import csv
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
sys.path.insert(0, str(ROOT / "tools"))

import import_jogger_fog_light_superseding_observations as importer  # noqa: E402


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerFogLightSupersedingObservationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.availability = read(MASTER / "configuration_attribute_availability.csv")

    def test_source_hashes_and_exact_existing_configuration_scope(self) -> None:
        self.assertEqual(
            hashlib.sha256(importer.APRIL_SOURCE.read_bytes()).hexdigest(),
            importer.APRIL_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(importer.JULY_SOURCE.read_bytes()).hexdigest(),
            importer.JULY_SHA256,
        )
        importer.verify_repository_contract()

    def test_spec_has_six_direct_expression_cells(self) -> None:
        rows = importer.load_spec()
        self.assertEqual(len(rows), 6)
        self.assertEqual(tuple(row["configuration_code"] for row in rows), importer.CONFIGURATIONS)
        self.assertEqual({row["attribute_code"] for row in rows}, {"fog_lights"})
        self.assertEqual({row["availability_status"] for row in rows}, {"not_available"})
        self.assertEqual({row["source_page"] for row in rows}, {"4"})
        self.assertEqual({row["source_label"] for row in rows}, {"Światła przeciwmgłowe"})
        self.assertEqual({row["source_symbol"] for row in rows}, {"-"})

    def test_april_standard_history_is_preserved_byte_for_semantic_contract(self) -> None:
        history = importer.april_history(self.availability)
        self.assertEqual(len(history), 6)
        self.assertEqual(
            [int(row["id"]) for row in history],
            [1868, 2080, 2239, 2451, 2663, 2822],
        )
        self.assertEqual({row["availability_status"] for row in history}, {"standard"})
        self.assertEqual({row["observation_date"] for row in history}, {"2026-04-01"})
        self.assertEqual({row["source_code"] for row in history}, {importer.APRIL_SOURCE_CODE})

    def test_july_rows_match_generated_contract_and_contiguous_suffix(self) -> None:
        importer.check()
        rows = importer.selected_july_rows(self.availability)
        self.assertEqual(len(rows), 6)
        self.assertEqual([int(row["id"]) for row in rows], list(range(5897, 5903)))
        self.assertEqual(
            importer.semantic_payload(rows),
            importer.semantic_payload(importer.generated_rows()),
        )

    def test_latest_observation_changes_only_expression_fog_light_status(self) -> None:
        latest: dict[tuple[str, str], dict[str, str]] = {}
        for row in self.availability:
            key = (row["configuration_code"], row["attribute_code"])
            if key not in latest or row["observation_date"] > latest[key]["observation_date"]:
                latest[key] = row
        for configuration in importer.CONFIGURATIONS:
            row = latest[(configuration, importer.ATTRIBUTE_CODE)]
            self.assertEqual(row["availability_status"], "not_available")
            self.assertEqual(row["observation_date"], "2026-07-03")
            self.assertEqual(row["source_code"], importer.JULY_SOURCE_CODE)

    def test_history_contains_exactly_two_dated_states_per_configuration(self) -> None:
        for configuration in importer.CONFIGURATIONS:
            rows = [
                row
                for row in self.availability
                if row["configuration_code"] == configuration
                and row["attribute_code"] == importer.ATTRIBUTE_CODE
            ]
            self.assertEqual(
                [(row["observation_date"], row["availability_status"]) for row in rows],
                [("2026-04-01", "standard"), ("2026-07-03", "not_available")],
            )

    def test_package_adds_no_model_version_or_configuration(self) -> None:
        models = read(MASTER / "models.csv")
        versions = read(MASTER / "versions.csv")
        configurations = read(MASTER / "configurations.csv")
        self.assertEqual(len(models), 19)
        self.assertEqual(len(versions), 22)
        self.assertEqual(len(configurations), 81)
        self.assertEqual(
            {
                row["code"]
                for row in configurations
                if row["code"] in set(importer.CONFIGURATIONS)
            },
            set(importer.CONFIGURATIONS),
        )


if __name__ == "__main__":
    unittest.main()
