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
REPORT = REPORTING / "brochure_chassis_modeling_closure_review.json"
VERIFIER = ROOT / "tools" / "review_brochure_chassis_modeling_closure_20260726.py"

SOURCES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_sandero_stepway_brochure_20260202",
    "src_pl_bigster_brochure_20251210",
    "src_pl_duster_mini_brochure_20251020",
    "src_pl_jogger_brochure_20251217",
}
ATTRIBUTES = {
    "turning_circle_between_kerbs",
    "turning_circle_wheel_track",
    "maximum_kerb_weight",
    "standard_tyre_specification",
    "front_suspension",
    "rear_suspension",
    "steering_type",
    "front_brake_type",
    "rear_brake_type",
}
EXPECTED_SCALAR_COUNTS = Counter(
    {
        "turning_circle_between_kerbs": 45,
        "turning_circle_wheel_track": 10,
        "maximum_kerb_weight": 33,
        "standard_tyre_specification": 55,
        "front_suspension": 31,
        "rear_suspension": 31,
        "steering_type": 24,
        "front_brake_type": 24,
        "rear_brake_type": 24,
    }
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BrochureChassisModelingClosureReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.scalar = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if row["source_code"] in SOURCES and row["attribute_code"] in ATTRIBUTES
        ]
        cls.ranges = [
            row
            for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
            if row["source_code"] == "src_pl_duster_mini_brochure_20251020"
            and row["attribute_code"] == "payload"
        ]

    def test_report_closes_four_packages_and_hands_off_broader_review(self) -> None:
        self.assertEqual(self.report["kind"], "brochure_chassis_modeling_closure_review")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(self.report["decision_reference"], "D-016")
        self.assertEqual(self.report["selected_variant"], "separate_unambiguous_attributes")
        self.assertEqual(len(self.report["packages"]), 4)
        self.assertEqual({item["pull_request"] for item in self.report["packages"]}, {264, 265, 266, 267})
        self.assertEqual(
            self.report["next_package"]["name"],
            "Official Brochure Technical Gap Resolution Closure Review",
        )

    def test_exact_scalar_counts_ids_sources_and_configurations(self) -> None:
        self.assertEqual(len(self.scalar), 277)
        self.assertEqual([int(row["id"]) for row in self.scalar], list(range(2291, 2568)))
        self.assertEqual(Counter(row["attribute_code"] for row in self.scalar), EXPECTED_SCALAR_COUNTS)
        self.assertEqual({row["source_code"] for row in self.scalar}, SOURCES)
        self.assertEqual(len({row["configuration_code"] for row in self.scalar}), 55)
        self.assertEqual(
            {row["observation_date"] for row in self.scalar},
            {"2025-10-20", "2025-12-10", "2025-12-17", "2026-02-02"},
        )

    def test_payload_ranges_remain_exact_closed_intervals(self) -> None:
        self.assertEqual(len(self.ranges), 10)
        self.assertEqual([int(row["id"]) for row in self.ranges], list(range(235, 245)))
        self.assertEqual(len({row["configuration_code"] for row in self.ranges}), 10)
        self.assertTrue(all(row["lower_inclusive"] == "true" for row in self.ranges))
        self.assertTrue(all(row["upper_inclusive"] == "true" for row in self.ranges))
        self.assertTrue(all(float(row["minimum_value"]) <= float(row["maximum_value"]) for row in self.ranges))

    def test_source_relationships_match_imported_targets(self) -> None:
        relationships = rows(MASTER / "source_configurations.csv")
        for source in SOURCES:
            expected = {row["configuration_code"] for row in self.scalar if row["source_code"] == source}
            actual = {
                row["configuration_code"]
                for row in relationships
                if row["source_code"] == source and row["relationship"] == "brochure_technical_data_for"
            }
            self.assertEqual(actual, expected, source)

    def test_all_model_resolutions_are_imported_but_jogger_mass_conflict_is_blocked(self) -> None:
        model = json.loads((REPORTING / "brochure_chassis_measurement_context_model.json").read_text(encoding="utf-8"))
        statuses = {item["classification_code"]: item["status"] for item in model["source_resolutions"]}
        self.assertEqual(set(statuses.values()), {"imported"})
        jogger = next(
            item
            for item in model["source_resolutions"]
            if item["classification_code"] == "jogger_chassis_candidate_and_modeling"
        )
        self.assertEqual(jogger["blocked_related_classification"], "jogger_mass_table_label_conflict")
        gap = json.loads((REPORTING / "official_brochure_technical_gap_review.json").read_text(encoding="utf-8"))
        conflict = next(item for item in gap["classifications"] if item["code"] == "jogger_mass_table_label_conflict")
        self.assertEqual(conflict["status"], "ambiguous_source_evidence")
        forbidden = {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"}
        imported = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if row["source_code"] == "src_pl_jogger_brochure_20251217"
            and row["attribute_code"] in forbidden
        ]
        self.assertEqual(imported, [])

    def test_fifteen_reporting_scopes_preserve_chassis_slots(self) -> None:
        scopes = self.report["reporting_contract"]["scopes"]
        self.assertEqual(sum(scopes.values()), 15)
        self.assertEqual(scopes, {"sandero_and_stepway": 4, "bigster": 4, "duster": 3, "jogger": 4})
        required_files = {
            "configuration_completeness.json",
            "sandero_ecog120_automatic_completeness.json",
            "sandero_ecog120_manual_completeness.json",
            "sandero_stepway_ecog120_automatic_completeness.json",
            "bigster_hybrid155_4x2_automatic_completeness.json",
            "bigster_hybridg150_4x4_automatic_completeness.json",
            "bigster_mildhybrid140_4x2_manual_completeness.json",
            "bigster_mildhybridg140_4x2_manual_completeness.json",
            "duster_ecog120_completeness.json",
            "duster_mildhybrid140_4x2_completeness.json",
            "duster_hybrid155_completeness.json",
            "jogger_ecog120_automatic_completeness.json",
            "jogger_ecog120_manual_completeness.json",
            "jogger_hybrid155_automatic_completeness.json",
            "jogger_tce110_manual_completeness.json",
        }
        self.assertTrue(all((REPORTING / filename).is_file() for filename in required_files))

    def test_closure_verifier_and_all_import_receipts_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: brochure chassis modeling closure review", completed.stdout)

    def test_project_state_preserves_completed_closure_receipt(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 915)
        self.assertGreaterEqual(state["baseline"]["rows"], 9306)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2567)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
