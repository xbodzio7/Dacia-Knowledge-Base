from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data" / "master" / "configuration_attribute_values.csv"
STATE = ROOT / "project" / "state.json"
IMPORTER = ROOT / "tools" / "import_brochure_gear_performance_20260726.py"
SOURCES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_sandero_stepway_brochure_20260202",
    "src_pl_jogger_brochure_20251217",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BrochureGearPerformanceValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = [
            row for row in read_rows(VALUES)
            if row.get("attribute_code") == "elasticity_80_120"
            and row.get("source_code") in SOURCES
        ]

    def test_exact_ids_counts_and_observation_identity(self) -> None:
        self.assertEqual(len(self.rows), 70)
        self.assertEqual([int(row["id"]) for row in self.rows], list(range(2119, 2189)))
        self.assertEqual(len({row["code"] for row in self.rows}), 70)
        self.assertEqual(
            len({(row["configuration_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"]) for row in self.rows}),
            70,
        )
        self.assertTrue(all(f"_gear{row['gear_number']}_" in row["code"] for row in self.rows))

    def test_source_fuel_gear_and_model_distributions(self) -> None:
        self.assertEqual(
            Counter(row["source_code"] for row in self.rows),
            Counter({
                "src_pl_sandero_brochure_20260202": 16,
                "src_pl_sandero_stepway_brochure_20260202": 22,
                "src_pl_jogger_brochure_20251217": 32,
            }),
        )
        self.assertEqual(Counter(row["fuel_type_code"] for row in self.rows), Counter({"lpg": 30, "petrol": 40}))
        self.assertEqual(Counter(row["gear_number"] for row in self.rows), Counter({"4": 50, "5": 14, "6": 6}))
        model_counts = Counter(
            "sandero_stepway" if row["configuration_code"].startswith("sandero_stepway_")
            else "sandero" if row["configuration_code"].startswith("sandero_")
            else "jogger"
            for row in self.rows
        )
        self.assertEqual(model_counts, Counter({"sandero": 16, "sandero_stepway": 22, "jogger": 32}))

    def test_exact_source_table_values_are_preserved(self) -> None:
        by_identity = {
            (row["configuration_code"], row["fuel_type_code"], row["gear_number"]): row["value"]
            for row in self.rows
        }
        expected = {
            ("sandero_iii_expression_ecog120_manual", "lpg", "4"): "7.4",
            ("sandero_iii_expression_ecog120_manual", "petrol", "5"): "11.7",
            ("sandero_iii_expression_ecog120_automatic", "lpg", "5"): "8",
            ("sandero_stepway_iii_essential_ecog120_manual", "petrol", "6"): "19",
            ("sandero_stepway_iii_extreme_ecog120_automatic", "lpg", "4"): "8.3",
            ("jogger_expression_5seat_tce110_manual", "petrol", "4"): "11.4",
            ("jogger_essential_5seat_ecog120_manual", "lpg", "4"): "8.1",
            ("jogger_journey_5seat_ecog120_automatic", "petrol", "4"): "9.2",
            ("jogger_expression_7seat_tce110_manual", "petrol", "4"): "12.3",
            ("jogger_extreme_7seat_ecog120_manual", "lpg", "4"): "8.2",
            ("jogger_journey_7seat_ecog120_automatic", "petrol", "4"): "9.5",
            ("jogger_extreme_7seat_hybrid155_automatic", "petrol", "4"): "6.5",
        }
        for identity, value in expected.items():
            self.assertEqual(by_identity[identity], value)

    def test_stepway_automatic_blank_gears_are_not_inferred(self) -> None:
        automatic = [
            row for row in self.rows
            if row["configuration_code"].startswith("sandero_stepway_")
            and row["configuration_code"].endswith("_automatic")
        ]
        self.assertEqual(len(automatic), 4)
        self.assertEqual({row["gear_number"] for row in automatic}, {"4"})
        self.assertFalse(any(row["gear_number"] in {"5", "6"} for row in automatic))

    def test_exact_configuration_scope_and_seat_layouts(self) -> None:
        codes = {row["configuration_code"] for row in self.rows}
        self.assertEqual(len(codes), 31)
        self.assertFalse(any(code.startswith(("sandero_iii_tce", "sandero_stepway_iii_tce")) for code in codes))
        jogger = {code for code in codes if code.startswith("jogger_")}
        self.assertEqual(len(jogger), 22)
        self.assertEqual(sum("_5seat_" in code for code in jogger), 11)
        self.assertEqual(sum("_7seat_" in code for code in jogger), 11)

    def test_declarative_import_contract_is_idempotent(self) -> None:
        result = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("PASS: exact brochure selected-gear performance values", result.stdout)

    def test_project_state_advances_to_import_closure_review(self) -> None:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Brochure Gear-Specific Performance Value Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Brochure Gear-Specific Performance Import Closure Review")
        self.assertEqual(state["baseline"]["configuration_values"], 2188)
        self.assertEqual(state["baseline"]["configuration_import_specs"], 117)


if __name__ == "__main__":
    unittest.main()
