from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_automatic",
}
SOURCES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_sandero_stepway_brochure_20260202",
}
VALUES = {"328", "410", "1108", "1455", "78"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError(f"missing CSV header: {path}")
        return list(reader)


class SanderoStepwayBrochureCargoTests(unittest.TestCase):
    def imported_values(self) -> list[dict[str, str]]:
        return [
            row
            for row in read_rows(MASTER / "configuration_attribute_values.csv")
            if row.get("observation_date") == "2026-02-02"
            and row.get("attribute_code") == "boot_capacity"
            and row.get("configuration_code") in CONFIGURATIONS
            and row.get("source_code") in SOURCES
        ]

    def imported_contexts(self) -> list[dict[str, str]]:
        imported_codes = {row["code"] for row in self.imported_values()}
        return [
            row
            for row in read_rows(MASTER / "configuration_cargo_volume_contexts.csv")
            if row.get("configuration_attribute_value_code") in imported_codes
        ]

    def test_import_contract_check_passes(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/import_sandero_stepway_brochure_cargo_20260725.py",
                "--check",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(
            "PASS: Sandero and Stepway official brochure cargo import contract",
            completed.stdout,
        )
        with tempfile.TemporaryDirectory() as directory:
            plan = subprocess.run(
                [
                    sys.executable,
                    "tools/dkb.py",
                    "configuration-gap-resolution-plan",
                    "--json",
                    str(Path(directory) / "plan.json"),
                    "--markdown",
                    str(Path(directory) / "plan.md"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(
            plan.returncode,
            0,
            plan.stdout + plan.stderr,
        )

    def test_exact_value_and_context_counts(self) -> None:
        values = self.imported_values()
        contexts = self.imported_contexts()
        self.assertEqual(len(values), 45)
        self.assertEqual(len(contexts), 45)
        self.assertEqual({row["value"] for row in values}, VALUES)
        self.assertEqual({row["configuration_code"] for row in values}, CONFIGURATIONS)
        self.assertEqual(Counter(row["configuration_code"] for row in values), Counter({code: 5 for code in CONFIGURATIONS}))
        self.assertEqual(
            {int(row["id"]) for row in values},
            set(range(1832, 1877)),
        )
        self.assertEqual(
            {int(row["id"]) for row in contexts},
            set(range(1, 46)),
        )

    def test_each_configuration_has_exact_five_context_signatures(self) -> None:
        values_by_code = {row["code"]: row for row in self.imported_values()}
        signatures: dict[str, set[tuple[str, ...]]] = defaultdict(set)
        for row in self.imported_contexts():
            value = values_by_code[row["configuration_attribute_value_code"]]
            signatures[value["configuration_code"]].add(
                (
                    row["measurement_basis_code"],
                    row["second_row_state_code"],
                    row["third_row_state_code"],
                    row["compartment_code"],
                    row["spare_wheel_state_code"],
                    row["tyre_repair_kit_state_code"],
                    row["double_floor_state_code"],
                )
            )
        self.assertEqual(set(signatures), CONFIGURATIONS)
        self.assertTrue(all(len(items) == 5 for items in signatures.values()))
        self.assertTrue(
            all(
                all(signature[4:] == ("", "", "") for signature in items)
                for items in signatures.values()
            )
        )

    def test_context_semantics_match_source_rows(self) -> None:
        values_by_code = {row["code"]: row for row in self.imported_values()}
        mapping = {
            values_by_code[row["configuration_attribute_value_code"]]["value"]: row
            for row in self.imported_contexts()
            if values_by_code[row["configuration_attribute_value_code"]]["configuration_code"]
            == "sandero_iii_expression_ecog120_manual"
        }
        self.assertEqual(mapping["328"]["measurement_basis_code"], "vda_iso_3832")
        self.assertEqual(mapping["328"]["second_row_state_code"], "upright")
        self.assertEqual(mapping["328"]["compartment_code"], "main_luggage_compartment")
        self.assertEqual(mapping["410"]["measurement_basis_code"], "ordinary_litre")
        self.assertEqual(mapping["1108"]["second_row_state_code"], "folded")
        self.assertEqual(mapping["1108"]["compartment_code"], "source_stated_total")
        self.assertEqual(mapping["1455"]["measurement_basis_code"], "ordinary_litre")
        self.assertEqual(mapping["78"]["second_row_state_code"], "")
        self.assertEqual(mapping["78"]["compartment_code"], "underfloor_compartment")

    def test_brochure_sources_document_all_nine_configurations(self) -> None:
        rows = [
            row
            for row in read_rows(MASTER / "source_configurations.csv")
            if row.get("relationship") == "brochure_technical_data_for"
            and row.get("configuration_code") in CONFIGURATIONS
            and row.get("source_code") in SOURCES
        ]
        self.assertEqual(len(rows), 9)
        self.assertEqual({row["configuration_code"] for row in rows}, CONFIGURATIONS)

    def test_legacy_cargo_history_is_not_migrated_or_replaced(self) -> None:
        values = read_rows(MASTER / "configuration_attribute_values.csv")
        legacy = [
            row
            for row in values
            if row.get("observation_date") == "2026-06-26"
            and row.get("attribute_code") == "boot_capacity"
            and row.get("configuration_code") in CONFIGURATIONS
        ]
        self.assertEqual(len(legacy), 7)
        self.assertEqual({row["value"] for row in legacy}, {"410"})
        context_value_codes = {
            row["configuration_attribute_value_code"]
            for row in read_rows(MASTER / "configuration_cargo_volume_contexts.csv")
        }
        self.assertTrue(all(row["code"] not in context_value_codes for row in legacy))

    def test_state_and_import_report_are_complete(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Sandero and Stepway Brochure Cargo Import")
        self.assertEqual(state["baseline"]["tests"], 791)
        self.assertEqual(state["baseline"]["rows"], 8255)
        self.assertEqual(state["baseline"]["configuration_values"], 1876)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Jogger Brochure Cargo Value Import",
        )
        report = json.loads(
            (
                ROOT
                / "data"
                / "reporting"
                / "sandero_stepway_brochure_cargo_import.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(report["configuration_values_imported"], 45)
        self.assertEqual(report["cargo_context_rows_imported"], 45)
        self.assertEqual(report["source_configuration_relationships"], 9)
        self.assertFalse(report["legacy_values_migrated"])


if __name__ == "__main__":
    unittest.main()
