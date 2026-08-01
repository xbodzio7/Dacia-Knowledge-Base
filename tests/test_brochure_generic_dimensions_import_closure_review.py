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
REPORT = REPORTING / "brochure_generic_dimensions_import_closure_review.json"
VERIFIER = ROOT / "tools" / "review_brochure_generic_dimensions_import_closure_20260726.py"

SOURCE_COUNTS = Counter(
    {
        "src_pl_sandero_brochure_20260202": 40,
        "src_pl_jogger_brochure_20251217": 242,
        "src_pl_duster_mini_brochure_20251020": 100,
    }
)
ATTRIBUTE_COUNTS = Counter(
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
REPORTING_SCOPES = {
    "sandero_ecog120_manual_completeness.json": 10,
    "sandero_ecog120_automatic_completeness.json": 10,
    "jogger_ecog120_manual_completeness.json": 11,
    "jogger_ecog120_automatic_completeness.json": 11,
    "jogger_tce110_manual_completeness.json": 11,
    "jogger_hybrid155_automatic_completeness.json": 11,
    "duster_ecog120_completeness.json": 10,
    "duster_mildhybrid140_4x2_completeness.json": 10,
    "duster_hybrid155_completeness.json": 10,
}
REVIEW_KEYS = {
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|front_track|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|rear_track|none",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BrochureGenericDimensionsImportClosureReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.values = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if 2568 <= int(row["id"]) <= 2949
        ]
        cls.configurations = {
            row["code"]: row for row in rows(MASTER / "configurations.csv")
        }

    def test_report_metadata_and_totals_are_exact(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "brochure_generic_dimensions_import_closure_review",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-26")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["import_package"],
            {
                "name": "Brochure Generic Dimensions Observation Import",
                "pull_request": 272,
                "merge_sha": "b46248d",
            },
        )
        self.assertEqual(
            self.report["totals"],
            {
                "sources": 3,
                "configurations": 36,
                "scalar_values": 382,
                "range_values": 0,
                "new_attributes": 0,
                "reporting_scopes": 9,
                "reporting_slot_entries": 94,
            },
        )

    def test_exact_ids_source_counts_and_attribute_counts(self) -> None:
        self.assertEqual(len(self.values), 382)
        self.assertEqual(
            [int(row["id"]) for row in self.values],
            list(range(2568, 2950)),
        )
        self.assertEqual(
            Counter(row["source_code"] for row in self.values),
            SOURCE_COUNTS,
        )
        self.assertEqual(
            Counter(row["attribute_code"] for row in self.values),
            ATTRIBUTE_COUNTS,
        )
        self.assertEqual(
            {row["observation_date"] for row in self.values},
            {"2025-10-20", "2025-12-17", "2026-02-02"},
        )

    def test_exact_configuration_scope_and_duster_4x4_deferral(self) -> None:
        by_source = {
            source: {
                row["configuration_code"]
                for row in self.values
                if row["source_code"] == source
            }
            for source in SOURCE_COUNTS
        }
        self.assertEqual(
            len(by_source["src_pl_sandero_brochure_20260202"]),
            4,
        )
        self.assertEqual(
            len(by_source["src_pl_jogger_brochure_20251217"]),
            22,
        )
        duster = by_source["src_pl_duster_mini_brochure_20251020"]
        self.assertEqual(len(duster), 10)
        self.assertTrue(
            all(
                "4x2"
                in self.configurations[configuration]["powertrain_label"]
                for configuration in duster
            )
        )
        self.assertFalse(
            any(
                "4x4"
                in self.configurations[configuration]["powertrain_label"]
                for configuration in duster
            )
        )
        self.assertFalse(
            any(
                row["attribute_code"]
                in {"approach_angle", "departure_angle"}
                for row in self.values
            )
        )

    def test_nine_reporting_scopes_contain_94_dimension_entries(self) -> None:
        total = 0
        for filename, expected in REPORTING_SCOPES.items():
            payload = json.loads(
                (REPORTING / filename).read_text(encoding="utf-8")
            )
            slots = {
                item["attribute_code"]
                for item in payload["technical_slots"]
                if item.get("fuel_type_code", "") == ""
            }
            if filename.startswith("jogger_"):
                required = set(ATTRIBUTE_COUNTS)
            elif filename.startswith("duster_"):
                required = set(ATTRIBUTE_COUNTS) - {"overall_height"}
            else:
                required = set(ATTRIBUTE_COUNTS) - {"roof_height_with_rails"}
            self.assertEqual(len(required), expected, filename)
            self.assertTrue(required <= slots, filename)
            total += len(required)
        self.assertEqual(total, 94)

    def test_later_exact_sandero_values_preserve_precedence(self) -> None:
        configurations = {
            "sandero_iii_expression_ecog120_manual",
            "sandero_iii_journey_ecog120_manual",
        }
        attributes = {
            "front_overhang",
            "overall_length",
            "overall_width",
            "rear_overhang",
            "wheelbase",
        }
        historical = [
            row
            for row in self.values
            if row["configuration_code"] in configurations
            and row["attribute_code"] in attributes
        ]
        later = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if row["configuration_code"] in configurations
            and row["attribute_code"] in attributes
            and row["observation_date"] == "2026-06-26"
        ]
        self.assertEqual(len(historical), 10)
        self.assertEqual(len(later), 10)
        self.assertEqual(
            {
                (row["configuration_code"], row["attribute_code"])
                for row in historical
            },
            {
                (row["configuration_code"], row["attribute_code"])
                for row in later
            },
        )

    def test_evidence_receipts_and_boundaries_are_preserved(self) -> None:
        evidence = json.loads(
            (REPORTING / "configuration_gap_evidence.json").read_text(
                encoding="utf-8"
            )
        )
        selected = {
            item["triage_key"]: item
            for item in evidence["decisions"]
            if item.get("triage_key") in REVIEW_KEYS
        }
        self.assertEqual(set(selected), REVIEW_KEYS)
        self.assertTrue(
            all(item["reviewed_pages"] == [2] for item in selected.values())
        )
        self.assertTrue(
            all(item["classification"] == "not_stated" for item in selected.values())
        )

        residual = json.loads(
            (
                REPORTING / "official_brochure_residual_evidence_review.json"
            ).read_text(encoding="utf-8")
        )
        receipt = residual["follow_up_import_receipt"]
        self.assertEqual(receipt["scalar_values"], 382)
        self.assertEqual(
            set(receipt["resolved_classifications"]),
            {"sandero_dimensions_and_cargo", "jogger_dimensions_and_cargo"},
        )
        self.assertEqual(
            receipt["partially_resolved_classifications"],
            ["duster_wltp_placeholders_and_dimensions"],
        )
        self.assertEqual(len(self.report["preserved_boundaries"]), 4)

    def test_closure_verifier_reproduces_repository_contract(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr or completed.stdout,
        )
        self.assertIn(
            "PASS: brochure generic dimensions import closure review",
            completed.stdout,
        )

    def test_project_state_preserves_closure_baseline(self) -> None:
        state = json.loads(
            (ROOT / "project" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 955)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
        self.assertGreaterEqual(
            state["baseline"]["configuration_value_ranges"],
            244,
        )
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
