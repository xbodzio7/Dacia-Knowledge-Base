from __future__ import annotations

import csv
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SPEC_ROOT = ROOT / "data" / "imports" / "configuration_values"
MASTER = ROOT / "data" / "master"

sys.path.insert(0, str(TOOLS))
import import_configuration_values as importer  # noqa: E402


def csv_rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


class ConfigurationValueImportSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = sorted(SPEC_ROOT.glob("*.json"))
        cls.specs = [
            importer.load_spec(path)
            for path in cls.paths
        ]

    def test_repository_contains_versioned_import_specs(self) -> None:
        self.assertTrue(self.paths)
        self.assertEqual(
            [path.name for path in self.paths],
            ["sandero-maximum-payload-20260626.json"],
        )
        self.assertTrue(
            all(spec.path.is_absolute() for spec in self.specs),
        )

    def test_each_spec_matches_master_rows_exactly(self) -> None:
        for spec in self.specs:
            with self.subTest(spec=spec.path.name):
                plan = importer.verify_import(ROOT, spec)
                self.assertEqual(plan.missing_rows, ())
                self.assertEqual(
                    len(plan.existing_rows),
                    len(spec.rows),
                )

    def test_specs_generate_globally_disjoint_identifiers(self) -> None:
        identifiers: list[str] = []
        codes: list[str] = []
        semantic: list[tuple[str, str, str, str]] = []
        for spec in self.specs:
            rows = importer.build_expected_rows(ROOT, spec)
            identifiers.extend(row["id"] for row in rows)
            codes.extend(row["code"].casefold() for row in rows)
            semantic.extend(
                (
                    row["configuration_code"],
                    row["attribute_code"],
                    row["fuel_type_code"],
                    row["observation_date"],
                )
                for row in rows
            )

        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(len(semantic), len(set(semantic)))

    def test_specs_use_registered_source_configuration_pairs(self) -> None:
        sources = {
            row["code"]: row
            for row in csv_rows("sources.csv")
        }
        pairs = {
            (row["source_code"], row["configuration_code"])
            for row in csv_rows("source_configurations.csv")
        }

        for spec in self.specs:
            for row in spec.rows:
                with self.subTest(
                    spec=spec.path.name,
                    configuration=row.configuration_code,
                ):
                    source = sources[row.source_code]
                    self.assertEqual(source["status"], "active")
                    self.assertTrue(source["file_path"])
                    self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")
                    self.assertIn(
                        (row.source_code, row.configuration_code),
                        pairs,
                    )

    def test_registered_source_files_match_declared_hashes(self) -> None:
        for spec in self.specs:
            with self.subTest(spec=spec.path.name):
                importer.verify_registered_sources(
                    ROOT,
                    spec,
                    verify_text=False,
                )

    def test_one_off_value_test_is_replaced_by_shared_contract(self) -> None:
        self.assertFalse(
            (
                ROOT
                / "tests"
                / "test_sandero_maximum_payload_values.py"
            ).exists(),
        )
        self.assertTrue(
            (
                ROOT
                / "tests"
                / "test_configuration_value_import_specs.py"
            ).is_file(),
        )


if __name__ == "__main__":
    unittest.main()
