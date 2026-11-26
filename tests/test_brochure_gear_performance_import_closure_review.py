from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "brochure_gear_performance_import_closure_review.json"
VERIFIER = ROOT / "tools" / "review_brochure_gear_performance_import_closure_20260726.py"
SOURCES = {
    "src_pl_sandero_brochure_20260202": 16,
    "src_pl_sandero_stepway_brochure_20260202": 22,
    "src_pl_jogger_brochure_20251217": 32,
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BrochureGearPerformanceImportClosureReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.values = [
            row for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("attribute_code") == "elasticity_80_120"
            and row.get("source_code") in SOURCES
        ]

    def test_closure_receipt_matches_exact_source_and_context_totals(self) -> None:
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["totals"],
            {
                "sources": 3,
                "configurations": 31,
                "values": 70,
                "fuel_counts": {"lpg": 29, "petrol": 41},
                "gear_counts": {"4": 50, "5": 14, "6": 6},
                "reporting_scopes": 8,
                "difference_contexts": 6,
            },
        )
        self.assertEqual(Counter(row["source_code"] for row in self.values), Counter(SOURCES))
        self.assertEqual(Counter(row["gear_number"] for row in self.values), Counter({"4": 50, "5": 14, "6": 6}))
        self.assertEqual(Counter(row["fuel_type_code"] for row in self.values), Counter({"lpg": 29, "petrol": 41}))

    def test_exact_configuration_scope_preserves_jogger_layouts(self) -> None:
        configurations = {row["configuration_code"] for row in self.values}
        self.assertEqual(len(configurations), 31)
        self.assertEqual(sum(code.startswith("sandero_iii_") for code in configurations), 4)
        self.assertEqual(sum(code.startswith("sandero_stepway_iii_") for code in configurations), 5)
        jogger = {code for code in configurations if code.startswith("jogger_")}
        self.assertEqual(len(jogger), 22)
        self.assertEqual(sum("_5seat_" in code for code in jogger), 11)
        self.assertEqual(sum("_7seat_" in code for code in jogger), 11)

    def test_non_inference_boundaries_remain_explicit_and_enforced(self) -> None:
        self.assertEqual(len(self.report["deferred_evidence"]), 6)
        self.assertEqual(
            {item["code"] for item in self.report["deferred_evidence"]},
            {
                "sandero_tce_column_without_exact_configuration",
                "stepway_tce110_without_exact_configuration",
                "stepway_automatic_fifth_and_sixth_gear_blank",
                "jogger_only_fourth_gear_stated",
                "no_cross_fuel_projection",
                "no_cross_configuration_projection",
            },
        )
        stepway_automatic = [
            row for row in self.values
            if row["configuration_code"].startswith("sandero_stepway_")
            and row["configuration_code"].endswith("_automatic")
        ]
        self.assertEqual(len(stepway_automatic), 4)
        self.assertEqual({row["gear_number"] for row in stepway_automatic}, {"4"})
        self.assertFalse(any(row["configuration_code"].startswith(("sandero_iii_tce", "sandero_stepway_iii_tce")) for row in self.values))

    def test_reporting_contract_lists_all_six_selected_gear_contexts(self) -> None:
        self.assertEqual(
            set(self.report["reporting_contract"]["gear_contexts"]),
            {
                "fuel_type_code=lpg;gear_number=4",
                "fuel_type_code=lpg;gear_number=5",
                "fuel_type_code=lpg;gear_number=6",
                "fuel_type_code=petrol;gear_number=4",
                "fuel_type_code=petrol;gear_number=5",
                "fuel_type_code=petrol;gear_number=6",
            },
        )
        self.assertEqual(len(self.report["reporting_contract"]["covered_surfaces"]), 8)

    def test_closure_verifier_reproduces_repository_contract(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: brochure selected-gear performance import closure review", completed.stdout)

    def test_project_state_preserves_closure_baseline_after_follow_up_reviews(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 834)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2188)
        self.assertGreaterEqual(state["baseline"]["rows"], 8852)
        self.assertGreaterEqual(state["baseline"]["configuration_import_specs"], 117)


if __name__ == "__main__":
    unittest.main()
