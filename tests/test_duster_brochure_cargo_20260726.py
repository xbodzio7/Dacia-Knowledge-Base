from __future__ import annotations

import csv
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = "src_pl_duster_mini_brochure_20251020"
CONFIGURATIONS = {
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
    "duster_iii_expression_mildhybrid140_4x2_manual",
    "duster_iii_extreme_mildhybrid140_4x2_manual",
    "duster_iii_journey_mildhybrid140_4x2_manual",
    "duster_iii_expression_hybrid155_4x2_automatic",
    "duster_iii_extreme_hybrid155_4x2_automatic",
    "duster_iii_journey_hybrid155_4x2_automatic",
}
FORBIDDEN_AUTOMATICS = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError(f"missing CSV header: {path}")
        return list(reader)


class DusterBrochureCargoTests(unittest.TestCase):
    def imported_values(self) -> list[dict[str, str]]:
        return [
            row for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") == SOURCE
            and row.get("attribute_code") == "boot_capacity"
            and row.get("observation_date") == "2025-10-20"
        ]

    def test_import_contract_check_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/import_duster_brochure_cargo_20260726.py", "--check"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("PASS: Duster official brochure cargo import contract", completed.stdout)

    def test_exact_values_contexts_ids_and_relationships(self) -> None:
        values = self.imported_values()
        self.assertEqual(len(values), 64)
        self.assertEqual({row["configuration_code"] for row in values}, CONFIGURATIONS)
        self.assertEqual({int(row["id"]) for row in values}, set(range(2055, 2119)))
        self.assertEqual(
            Counter(row["configuration_code"] for row in values),
            Counter({code: (4 if "ecog120" in code else 8) for code in CONFIGURATIONS}),
        )
        value_codes = {row["code"] for row in values}
        contexts = [row for row in rows(MASTER / "configuration_cargo_volume_contexts.csv") if row.get("configuration_attribute_value_code") in value_codes]
        self.assertEqual(len(contexts), 64)
        self.assertEqual({int(row["id"]) for row in contexts}, set(range(224, 288)))
        relationships = [row for row in rows(MASTER / "source_configurations.csv") if row.get("source_code") == SOURCE and row.get("relationship") == "brochure_technical_data_for"]
        self.assertEqual({row["configuration_code"] for row in relationships}, CONFIGURATIONS)
        self.assertEqual({int(row["id"]) for row in relationships}, set(range(207, 217)))

    def test_context_and_deferral_boundaries_are_exact(self) -> None:
        values = self.imported_values()
        self.assertFalse({row["configuration_code"] for row in values} & FORBIDDEN_AUTOMATICS)
        self.assertFalse({"348", "1414", "400", "1527", "456", "1548"} & {row["value"] for row in values})
        value_codes = {row["code"] for row in values}
        contexts = [row for row in rows(MASTER / "configuration_cargo_volume_contexts.csv") if row.get("configuration_attribute_value_code") in value_codes]
        self.assertEqual({row["measurement_basis_code"] for row in contexts}, {"vda_iso_3832", "ordinary_litre"})
        self.assertEqual({row["second_row_state_code"] for row in contexts}, {"upright", "folded"})
        self.assertEqual({row["third_row_state_code"] for row in contexts}, {""})
        self.assertEqual({row["double_floor_state_code"] for row in contexts}, {""})
        eco_codes = {row["code"] for row in values if "ecog120" in row["configuration_code"]}
        eco_contexts = [row for row in contexts if row["configuration_attribute_value_code"] in eco_codes]
        self.assertEqual({(row["tyre_repair_kit_state_code"], row["spare_wheel_state_code"]) for row in eco_contexts}, {("present", "absent")})

    def test_gap_resolution_plan_accepts_contextual_duster_history(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/dkb.py", "configuration-gap-resolution-plan", "--json", "/tmp/duster-gap-plan.json", "--markdown", "/tmp/duster-gap-plan.md"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
