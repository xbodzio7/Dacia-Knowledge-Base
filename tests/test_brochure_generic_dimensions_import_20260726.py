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
IMPORTER = ROOT / "tools" / "import_brochure_generic_dimensions_20260726.py"
MAPPING_VERIFIER = ROOT / "tools" / "review_brochure_generic_dimensions_semantic_mapping_20260726.py"

SOURCES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_jogger_brochure_20251217",
    "src_pl_duster_mini_brochure_20251020",
}
DIMENSIONS = {
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
}
# The append-only receipt reserves scalar IDs 2568–2949 for this exact package.
EXPECTED_ATTRIBUTE_COUNTS = Counter(
    {
        "overall_length": 36,
        "overall_width": 36,
        "overall_width_with_mirrors": 36,
        "wheelbase": 36,
        "ground_clearance": 36,
        "front_track": 36,
        "rear_track": 36,
        "front_overhang": 36,
        "rear_overhang": 36,
        "overall_height": 26,
        "roof_height_with_rails": 32,
    }
)
REPORTING_ATTRIBUTES = {
    "sandero_ecog120_manual_completeness.json": {
        "overall_height", "front_track", "overall_width", "overall_width_with_mirrors", "rear_track",
        "front_overhang", "wheelbase", "rear_overhang", "overall_length", "ground_clearance",
    },
    "sandero_ecog120_automatic_completeness.json": {
        "overall_height", "front_track", "overall_width", "overall_width_with_mirrors", "rear_track",
        "front_overhang", "wheelbase", "rear_overhang", "overall_length", "ground_clearance",
    },
    "jogger_ecog120_manual_completeness.json": DIMENSIONS,
    "jogger_ecog120_automatic_completeness.json": DIMENSIONS,
    "jogger_tce110_manual_completeness.json": DIMENSIONS,
    "jogger_hybrid155_automatic_completeness.json": DIMENSIONS,
    "duster_ecog120_completeness.json": DIMENSIONS - {"overall_height"},
    "duster_mildhybrid140_4x2_completeness.json": DIMENSIONS - {"overall_height"},
    "duster_hybrid155_completeness.json": DIMENSIONS - {"overall_height"},
}
EXPECTED_EXTREME_AUTOMATIC_REVIEW_KEYS = {
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|front_track|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|ground_clearance|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|overall_height|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|overall_width_with_mirrors|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|rear_track|none",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BrochureGenericDimensionsImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.package = [row for row in cls.values if 2568 <= int(row["id"]) <= 2949]
        cls.configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}

    def test_exact_counts_ids_sources_attributes_and_configurations(self) -> None:
        self.assertEqual(len(self.package), 382)
        self.assertEqual([int(row["id"]) for row in self.package], list(range(2568, 2950)))
        self.assertEqual(Counter(row["source_code"] for row in self.package), Counter({
            "src_pl_sandero_brochure_20260202": 40,
            "src_pl_jogger_brochure_20251217": 242,
            "src_pl_duster_mini_brochure_20251020": 100,
        }))
        self.assertEqual(Counter(row["attribute_code"] for row in self.package), EXPECTED_ATTRIBUTE_COUNTS)
        self.assertEqual(len({row["configuration_code"] for row in self.package}), 36)
        self.assertEqual({row["fuel_type_code"] for row in self.package}, {""})
        self.assertEqual({row["gear_number"] for row in self.package}, {""})

    def test_sandero_values_project_to_four_exact_configurations(self) -> None:
        selected = [row for row in self.package if row["source_code"] == "src_pl_sandero_brochure_20260202"]
        self.assertEqual(len({row["configuration_code"] for row in selected}), 4)
        expected = {
            "overall_height": "1496", "front_track": "1533", "overall_width": "1853",
            "overall_width_with_mirrors": "2012", "rear_track": "1519", "front_overhang": "833",
            "wheelbase": "2604", "rear_overhang": "665", "overall_length": "4102", "ground_clearance": "162",
        }
        for configuration in {row["configuration_code"] for row in selected}:
            actual = {row["attribute_code"]: row["value"] for row in selected if row["configuration_code"] == configuration}
            self.assertEqual(actual, expected)

    def test_jogger_separates_overall_and_rail_heights(self) -> None:
        selected = [row for row in self.package if row["source_code"] == "src_pl_jogger_brochure_20251217"]
        self.assertEqual(len({row["configuration_code"] for row in selected}), 22)
        for configuration in {row["configuration_code"] for row in selected}:
            actual = {row["attribute_code"]: row["value"] for row in selected if row["configuration_code"] == configuration}
            self.assertEqual(actual["roof_height_with_rails"], "1689")
            self.assertEqual(actual["overall_height"], "1630")
            self.assertEqual(actual["overall_length"], "4550")
            self.assertEqual(actual["ground_clearance"], "200")
            self.assertEqual(len(actual), 11)

    def test_duster_imports_only_source_related_4x2_values(self) -> None:
        selected = [row for row in self.package if row["source_code"] == "src_pl_duster_mini_brochure_20251020"]
        configurations = {row["configuration_code"] for row in selected}
        self.assertEqual(len(configurations), 10)
        self.assertTrue(all("4x2" in self.configurations[code]["powertrain_label"] for code in configurations))
        self.assertFalse(any("4x4" in self.configurations[code]["powertrain_label"] for code in configurations))
        for configuration in configurations:
            actual = {row["attribute_code"]: row["value"] for row in selected if row["configuration_code"] == configuration}
            self.assertEqual(actual["roof_height_with_rails"], "1656")
            self.assertEqual(actual["front_track"], "1574")
            self.assertEqual(actual["rear_track"], "1547")
            self.assertEqual(actual["ground_clearance"], "209")
            self.assertEqual(len(actual), 10)
        self.assertFalse(any(row["attribute_code"] in {"approach_angle", "departure_angle"} for row in self.package))

    def test_later_exact_sandero_observations_remain_present(self) -> None:
        manual = {
            "sandero_iii_expression_ecog120_manual",
            "sandero_iii_journey_ecog120_manual",
        }
        attributes = {"front_overhang", "overall_length", "overall_width", "rear_overhang", "wheelbase"}
        later = [
            row for row in self.values
            if row["configuration_code"] in manual
            and row["attribute_code"] in attributes
            and row["observation_date"] == "2026-06-26"
        ]
        historical = [
            row for row in self.package
            if row["configuration_code"] in manual and row["attribute_code"] in attributes
        ]
        self.assertEqual(len(later), 10)
        self.assertEqual(len(historical), 10)
        self.assertTrue(all(row["observation_date"] == "2026-02-02" for row in historical))

    def test_nine_reporting_scopes_include_approved_dimension_slots(self) -> None:
        self.assertEqual(len(REPORTING_ATTRIBUTES), 9)
        for filename, required in REPORTING_ATTRIBUTES.items():
            payload = json.loads((REPORTING / filename).read_text(encoding="utf-8"))
            slots = {item["attribute_code"] for item in payload["technical_slots"] if item.get("fuel_type_code", "") == ""}
            self.assertTrue(required <= slots, filename)

    def test_importer_mapping_receipt_and_deferrals_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: brochure generic dimension observations", completed.stdout)
        mapped = subprocess.run(
            [sys.executable, str(MAPPING_VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(mapped.returncode, 0, mapped.stderr or mapped.stdout)
        report = json.loads((REPORTING / "brochure_generic_dimensions_semantic_mapping_review.json").read_text(encoding="utf-8"))
        self.assertEqual(report["import_receipt"]["status"], "imported")
        self.assertEqual(report["import_receipt"]["scalar_values"], 382)
        self.assertEqual(report["import_receipt"]["duster_4x4_status"], "deferred_without_exact_source_relationship")

        evidence = json.loads((REPORTING / "configuration_gap_evidence.json").read_text(encoding="utf-8"))
        selected_evidence = {
            item["triage_key"]: item
            for item in evidence["decisions"]
            if item.get("triage_key") in EXPECTED_EXTREME_AUTOMATIC_REVIEW_KEYS
        }
        self.assertEqual(set(selected_evidence), EXPECTED_EXTREME_AUTOMATIC_REVIEW_KEYS)
        self.assertTrue(all(item["reviewed_pages"] == [2] for item in selected_evidence.values()))
        self.assertTrue(all(item["classification"] == "not_stated" for item in selected_evidence.values()))

        plan = json.loads((REPORTING / "configuration_gap_resolution_plan.json").read_text(encoding="utf-8"))
        selected_plan = {
            item["triage_key"]: item
            for item in plan["decisions"]
            if item.get("triage_key") in EXPECTED_EXTREME_AUTOMATIC_REVIEW_KEYS
        }
        self.assertEqual(set(selected_plan), EXPECTED_EXTREME_AUTOMATIC_REVIEW_KEYS)
        self.assertTrue(all(item["reviewed_pages"] == [2] for item in selected_plan.values()))
        self.assertTrue(all(item["resolution_state"] == "closed_not_stated" for item in selected_plan.values()))

    def test_project_state_matches_completed_import(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 955)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
