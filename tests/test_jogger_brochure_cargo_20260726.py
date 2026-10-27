from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE_CODE = "src_pl_jogger_brochure_20251217"
CONFIGURATIONS = {
    "jogger_essential_5seat_ecog120_manual",
    "jogger_expression_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "jogger_expression_5seat_tce110_manual",
    "jogger_extreme_5seat_tce110_manual",
    "jogger_journey_5seat_tce110_manual",
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_essential_7seat_ecog120_manual",
    "jogger_expression_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_automatic",
    "jogger_journey_7seat_ecog120_automatic",
    "jogger_expression_7seat_tce110_manual",
    "jogger_extreme_7seat_tce110_manual",
    "jogger_journey_7seat_tce110_manual",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
}
FIVE_SEAT = {code for code in CONFIGURATIONS if "_5seat_" in code}
SEVEN_SEAT = CONFIGURATIONS - FIVE_SEAT
VALUES = {"708", "829", "1819", "2094", "160", "212", "565", "699", "696", "820"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError(f"missing CSV header: {path}")
        return list(reader)


class JoggerBrochureCargoTests(unittest.TestCase):
    def imported_values(self) -> list[dict[str, str]]:
        return [
            row
            for row in read_rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") == SOURCE_CODE
            and row.get("observation_date") == "2025-12-17"
            and row.get("attribute_code") == "boot_capacity"
            and row.get("configuration_code") in CONFIGURATIONS
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
                "tools/import_jogger_brochure_cargo_20260726.py",
                "--check",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(
            "PASS: Jogger official brochure cargo import contract",
            completed.stdout,
        )

    def test_exact_values_contexts_ids_and_source_relationships(self) -> None:
        values = self.imported_values()
        contexts = self.imported_contexts()
        self.assertEqual(len(values), 110)
        self.assertEqual(len(contexts), 110)
        self.assertEqual({row["configuration_code"] for row in values}, CONFIGURATIONS)
        self.assertEqual({row["value"] for row in values}, VALUES)
        self.assertEqual(
            Counter(row["configuration_code"] for row in values),
            Counter(
                {
                    **{code: 4 for code in FIVE_SEAT},
                    **{code: 6 for code in SEVEN_SEAT},
                }
            ),
        )
        self.assertEqual(
            {int(row["id"]) for row in values},
            set(range(1877, 1987)),
        )
        self.assertEqual(
            {int(row["id"]) for row in contexts},
            set(range(46, 156)),
        )
        relations = [
            row
            for row in read_rows(MASTER / "source_configurations.csv")
            if row.get("source_code") == SOURCE_CODE
            and row.get("relationship") == "brochure_technical_data_for"
            and row.get("configuration_code") in CONFIGURATIONS
        ]
        self.assertEqual(len(relations), 22)
        self.assertEqual({row["configuration_code"] for row in relations}, CONFIGURATIONS)

    def test_layout_contexts_are_exact_and_ambiguous_maximum_is_absent(self) -> None:
        values = {row["code"]: row for row in self.imported_values()}
        contexts = {
            row["configuration_attribute_value_code"]: row
            for row in self.imported_contexts()
        }
        self.assertEqual(set(values), set(contexts))
        self.assertFalse({row["value"] for row in values.values()} & {"1807", "2085"})

        five_states: Counter[tuple[str, str, str]] = Counter()
        seven_states: Counter[tuple[str, str, str]] = Counter()
        for code, value in values.items():
            context = contexts[code]
            self.assertEqual(context["spare_wheel_state_code"], "")
            self.assertEqual(context["tyre_repair_kit_state_code"], "")
            self.assertEqual(context["double_floor_state_code"], "")
            key = (
                context["measurement_basis_code"],
                context["second_row_state_code"],
                context["third_row_state_code"],
            )
            if value["configuration_code"] in FIVE_SEAT:
                five_states[key] += 1
            else:
                seven_states[key] += 1

        self.assertEqual(
            five_states,
            Counter(
                {
                    ("vda_iso_3832", "upright", ""): 11,
                    ("ordinary_litre", "upright", ""): 11,
                    ("vda_iso_3832", "folded", ""): 11,
                    ("ordinary_litre", "folded", ""): 11,
                }
            ),
        )
        self.assertEqual(
            seven_states,
            Counter(
                {
                    ("vda_iso_3832", "upright", "upright"): 11,
                    ("ordinary_litre", "upright", "upright"): 11,
                    ("vda_iso_3832", "upright", "folded"): 11,
                    ("ordinary_litre", "upright", "folded"): 11,
                    ("vda_iso_3832", "upright", "removed"): 11,
                    ("ordinary_litre", "upright", "removed"): 11,
                }
            ),
        )

    def test_gap_resolution_plan_accepts_contextual_jogger_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/dkb.py",
                    "configuration-gap-resolution-plan",
                    "--json",
                    str(output / "plan.json"),
                    "--markdown",
                    str(output / "plan.md"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
