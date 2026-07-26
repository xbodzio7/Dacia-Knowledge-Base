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
REPORTING = ROOT / "data" / "reporting"
REPORT = REPORTING / "official_brochure_residual_evidence_review.json"
VERIFIER = ROOT / "tools" / "review_official_brochure_residual_evidence_20260726.py"

CORE_DIMENSIONS = {
    "overall_length",
    "overall_width",
    "overall_width_with_mirrors",
    "overall_height",
    "roof_height_with_rails",
    "wheelbase",
    "ground_clearance",
    "front_track",
    "rear_track",
    "front_overhang",
    "rear_overhang",
    "approach_angle",
    "departure_angle",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class OfficialBrochureResidualEvidenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.closure = json.loads((REPORTING / "official_brochure_technical_gap_resolution_closure_review.json").read_text(encoding="utf-8"))
        cls.gap = json.loads((REPORTING / "official_brochure_technical_gap_review.json").read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        versions = {row["code"]: row for row in rows(MASTER / "versions.csv")}
        cls.models = {
            row["code"]: versions.get(row.get("version_code", ""), {}).get("model_code", "")
            for row in rows(MASTER / "configurations.csv")
            if row.get("status") == "active"
        }

    def test_sixteen_residual_classifications_partition_exactly(self) -> None:
        stable = {item["code"] for item in self.report["stable_non_import"]}
        covered = {item["code"] for item in self.report["closed_by_existing_exact_coverage"]}
        candidates = {item["code"] for item in self.report["semantic_mapping_review_candidates"]}
        residual = set(self.closure["residual_evidence"]["classification_codes"])
        self.assertEqual(len(stable), 11)
        self.assertEqual(len(covered), 2)
        self.assertEqual(len(candidates), 3)
        self.assertEqual(stable | covered | candidates, residual)
        self.assertTrue(stable.isdisjoint(covered))
        self.assertTrue(stable.isdisjoint(candidates))
        self.assertTrue(covered.isdisjoint(candidates))

    def test_stable_non_imports_preserve_source_boundaries(self) -> None:
        classifications = {item["code"]: item for item in self.gap["classifications"]}
        stable = {item["code"]: item["resolution"] for item in self.report["stable_non_import"]}
        self.assertEqual(
            {code for code, item in classifications.items() if item["status"] == "unmodeled_exact_configuration"},
            {
                "sandero_tce100_without_exact_configuration",
                "stepway_tce110_without_exact_configuration",
                "duster_hybridg150_without_exact_configuration",
            },
        )
        self.assertEqual(stable["jogger_blank_wltp_cells"], "no_observation")
        self.assertEqual(stable["sandero_wltp_placeholders"], "no_observation")
        self.assertEqual(stable["jogger_mass_table_label_conflict"], "blocked_until_corrected_official_source")

    def test_bigster_and_stepway_dimensions_are_already_covered(self) -> None:
        covered = {item["code"]: item for item in self.report["closed_by_existing_exact_coverage"]}
        self.assertEqual(covered["bigster_dimensions_covered_and_cargo_deferred"]["existing_dimension_values"], 140)
        self.assertEqual(covered["bigster_dimensions_covered_and_cargo_deferred"]["active_configurations"], 14)
        self.assertEqual(covered["stepway_dimensions_and_cargo"]["existing_dimension_values"], 25)
        self.assertEqual(covered["stepway_dimensions_and_cargo"]["active_configurations"], 5)

    def test_three_dimension_candidates_have_exact_review_scopes(self) -> None:
        candidates = {item["code"]: item for item in self.report["semantic_mapping_review_candidates"]}
        self.assertEqual(set(candidates), {
            "sandero_dimensions_and_cargo",
            "jogger_dimensions_and_cargo",
            "duster_wltp_placeholders_and_dimensions",
        })
        self.assertEqual(candidates["sandero_dimensions_and_cargo"]["source_page"], 20)
        self.assertEqual(candidates["sandero_dimensions_and_cargo"]["missing_exact_dimension_configurations"], 2)
        self.assertEqual(candidates["jogger_dimensions_and_cargo"]["source_page"], 22)
        self.assertEqual(candidates["jogger_dimensions_and_cargo"]["missing_exact_dimension_configurations"], 22)
        self.assertEqual(candidates["duster_wltp_placeholders_and_dimensions"]["source_page"], 24)
        self.assertEqual(candidates["duster_wltp_placeholders_and_dimensions"]["active_configurations"], 27)

    def test_current_dimension_coverage_matches_repository(self) -> None:
        selected = {
            model: [
                row
                for row in self.values
                if self.models.get(row["configuration_code"]) == model
                and row["attribute_code"] in CORE_DIMENSIONS
            ]
            for model in {"sandero_iii", "sandero_stepway_iii", "jogger", "bigster", "duster_iii"}
        }
        self.assertEqual(len(selected["sandero_iii"]), 10)
        self.assertEqual(len({row["configuration_code"] for row in selected["sandero_iii"]}), 2)
        self.assertEqual(len(selected["sandero_stepway_iii"]), 25)
        self.assertEqual(len({row["configuration_code"] for row in selected["sandero_stepway_iii"]}), 5)
        self.assertEqual(selected["jogger"], [])
        self.assertEqual(len(selected["bigster"]), 140)
        self.assertEqual(len({row["configuration_code"] for row in selected["bigster"]}), 14)
        self.assertEqual(selected["duster_iii"], [])

    def test_no_generic_dimension_was_imported_from_brochures(self) -> None:
        brochure_sources = {
            "src_pl_sandero_brochure_20260202",
            "src_pl_sandero_stepway_brochure_20260202",
            "src_pl_jogger_brochure_20251217",
            "src_pl_bigster_brochure_20251210",
            "src_pl_duster_mini_brochure_20251020",
        }
        self.assertFalse(any(
            row["source_code"] in brochure_sources and row["attribute_code"] in CORE_DIMENSIONS
            for row in self.values
        ))
        turning = [
            row for row in self.values
            if row["source_code"] == "src_pl_duster_mini_brochure_20251020"
            and row["attribute_code"] == "turning_circle_wheel_track"
        ]
        self.assertEqual(len(turning), 10)

    def test_review_verifier_and_source_closure_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: official brochure residual evidence review", completed.stdout)

    def test_project_state_matches_completed_review(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Official Brochure Residual Evidence Review")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Brochure Generic Dimensions Semantic Mapping Review")
        self.assertEqual(state["baseline"]["tests"], 931)
        self.assertEqual(state["baseline"]["rows"], 9306)
        self.assertEqual(state["baseline"]["configuration_values"], 2567)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
