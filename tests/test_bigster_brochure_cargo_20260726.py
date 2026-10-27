from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
IMPORTED_CONFIGURATIONS = {
    "bigster_essential_mildhybrid140_4x2_manual",
    "bigster_expression_mildhybrid140_4x2_manual",
    "bigster_extreme_mildhybrid140_4x2_manual",
    "bigster_journey_mildhybrid140_4x2_manual",
    "bigster_essential_mildhybridg140_4x2_manual",
    "bigster_expression_mildhybridg140_4x2_manual",
    "bigster_extreme_mildhybridg140_4x2_manual",
    "bigster_journey_mildhybridg140_4x2_manual",
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
}
DEFERRED_CONFIGURATIONS = {
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}
DEFERRED_VALUES = {"444", "1712", "556", "1856"}
ALL_VALUES = {
    "609", "1877", "660", "1960",
    "667", "1937", "702", "2002", "624", "1894", "681", "1981",
    "546", "1851", "612", "1912", "488", "1791", "566", "1866",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError(f"missing CSV header: {path}")
        return list(reader)


class BigsterBrochureCargoTests(unittest.TestCase):
    def imported_values(self) -> list[dict[str, str]]:
        return [
            row
            for row in read_rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") == SOURCE_CODE
            and row.get("observation_date") == "2025-12-10"
            and row.get("attribute_code") == "boot_capacity"
            and row.get("configuration_code") in IMPORTED_CONFIGURATIONS
        ]

    def imported_contexts(self) -> list[dict[str, str]]:
        value_codes = {row["code"] for row in self.imported_values()}
        return [
            row
            for row in read_rows(MASTER / "configuration_cargo_volume_contexts.csv")
            if row.get("configuration_attribute_value_code") in value_codes
        ]

    def test_import_contract_check_passes(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/import_bigster_brochure_cargo_20260726.py",
                "--check",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(
            "PASS: Bigster official brochure cargo import contract",
            completed.stdout,
        )

    def test_exact_counts_ids_values_and_relationships(self) -> None:
        values = self.imported_values()
        contexts = self.imported_contexts()
        self.assertEqual(len(values), 68)
        self.assertEqual(len(contexts), 68)
        self.assertEqual({row["configuration_code"] for row in values}, IMPORTED_CONFIGURATIONS)
        self.assertEqual({row["value"] for row in values}, ALL_VALUES)
        self.assertEqual(
            Counter(row["configuration_code"] for row in values),
            Counter(
                {
                    "bigster_essential_mildhybrid140_4x2_manual": 4,
                    "bigster_expression_mildhybrid140_4x2_manual": 8,
                    "bigster_extreme_mildhybrid140_4x2_manual": 8,
                    "bigster_journey_mildhybrid140_4x2_manual": 8,
                    "bigster_essential_mildhybridg140_4x2_manual": 4,
                    "bigster_expression_mildhybridg140_4x2_manual": 4,
                    "bigster_extreme_mildhybridg140_4x2_manual": 4,
                    "bigster_journey_mildhybridg140_4x2_manual": 4,
                    "bigster_expression_hybrid155_4x2_automatic": 8,
                    "bigster_extreme_hybrid155_4x2_automatic": 8,
                    "bigster_journey_hybrid155_4x2_automatic": 8,
                }
            ),
        )
        self.assertEqual({int(row["id"]) for row in values}, set(range(1987, 2055)))
        self.assertEqual({int(row["id"]) for row in contexts}, set(range(156, 224)))
        relations = [
            row
            for row in read_rows(MASTER / "source_configurations.csv")
            if row.get("source_code") == SOURCE_CODE
            and row.get("relationship") == "brochure_technical_data_for"
            and row.get("configuration_code") in IMPORTED_CONFIGURATIONS
        ]
        self.assertEqual(len(relations), 11)
        self.assertEqual({row["configuration_code"] for row in relations}, IMPORTED_CONFIGURATIONS)

    def test_equipment_context_and_deferral_boundaries_are_exact(self) -> None:
        values = {row["code"]: row for row in self.imported_values()}
        contexts = {
            row["configuration_attribute_value_code"]: row
            for row in self.imported_contexts()
        }
        self.assertEqual(set(values), set(contexts))
        equipment_counts: Counter[tuple[str, str]] = Counter()
        for code, value in values.items():
            context = contexts[code]
            self.assertEqual(context["double_floor_state_code"], "")
            self.assertEqual(context["third_row_state_code"], "")
            equipment = (
                context["spare_wheel_state_code"],
                context["tyre_repair_kit_state_code"],
            )
            equipment_counts[equipment] += 1
            if (
                "_essential_mildhybrid140_" in value["configuration_code"]
                or "_mildhybridg140_" in value["configuration_code"]
            ):
                self.assertEqual(equipment, ("absent", "present"))
        self.assertEqual(
            equipment_counts,
            Counter({("absent", "present"): 44, ("present", "absent"): 24}),
        )
        self.assertFalse({row["configuration_code"] for row in values.values()} & DEFERRED_CONFIGURATIONS)
        self.assertFalse({row["value"] for row in values.values()} & DEFERRED_VALUES)

        report = json.loads(
            (ROOT / "data" / "reporting" / "bigster_brochure_cargo_import.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(report["deferred"]["hybrid_g_150_4x4_values"], [444, 1712, 556, 1856])
        self.assertIn("does not identify a powertrain", report["deferred"]["generic_dimensions_reason"])

    def test_gap_resolution_plan_accepts_contextual_bigster_history(self) -> None:
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
