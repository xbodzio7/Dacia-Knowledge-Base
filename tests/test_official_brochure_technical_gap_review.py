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
REPORT = ROOT / "data" / "reporting" / "official_brochure_technical_gap_review.json"
VERIFIER = ROOT / "tools" / "review_official_brochure_technical_gaps_20260726.py"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class OfficialBrochureTechnicalGapReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.classifications = {
            item["code"]: item for item in cls.report["classifications"]
        }

    def test_review_covers_all_five_archived_brochures_and_technical_pages(self) -> None:
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(self.report["scope"]["sources"], 5)
        pages = {
            item["source_code"]: item["pages"]
            for item in self.report["scope"]["technical_table_pages"]
        }
        self.assertEqual(
            pages,
            {
                "src_pl_bigster_brochure_20251210": [20, 24],
                "src_pl_jogger_brochure_20251217": [19, 22],
                "src_pl_sandero_brochure_20260202": [17, 20],
                "src_pl_sandero_stepway_brochure_20260202": [17, 20],
                "src_pl_duster_mini_brochure_20251020": [20, 21, 24],
            },
        )

    def test_current_brochure_coverage_is_unchanged(self) -> None:
        self.assertEqual(
            self.report["current_brochure_coverage"],
            {
                "scalar_values": 357,
                "ranges": 0,
                "attributes": {"boot_capacity": 287, "elasticity_80_120": 70},
                "source_configuration_relationships": 52,
            },
        )
        brochure_sources = {
            item["source_code"]
            for item in self.report["scope"]["technical_table_pages"]
        }
        values = [
            row for row in rows(MASTER / "configuration_attribute_values.csv")
            if row.get("source_code") in brochure_sources
        ]
        self.assertEqual(len(values), 357)
        self.assertEqual(
            Counter(row["attribute_code"] for row in values),
            Counter({"boot_capacity": 287, "elasticity_80_120": 70}),
        )

    def test_classification_inventory_and_status_distribution_are_exact(self) -> None:
        self.assertEqual(len(self.classifications), 29)
        self.assertEqual(
            Counter(item["status"] for item in self.classifications.values()),
            Counter(
                {
                    "covered_or_superseded": 5,
                    "exact_import_candidate": 6,
                    "requires_context_or_attribute_modeling": 5,
                    "covered_or_explicitly_deferred": 4,
                    "exact_range_candidate": 1,
                    "ambiguous_source_evidence": 1,
                    "no_observation": 2,
                    "next_package_candidate": 1,
                    "unmodeled_exact_configuration": 3,
                    "no_observation_or_generic_projection": 1,
                }
            ),
        )
        self.assertTrue(
            all(item["attributes"] and item["reason"] for item in self.classifications.values())
        )

    def test_ambiguous_and_unmodeled_evidence_is_not_recast_as_data(self) -> None:
        self.assertEqual(
            self.classifications["jogger_mass_table_label_conflict"]["status"],
            "ambiguous_source_evidence",
        )
        self.assertEqual(
            {
                code
                for code, item in self.classifications.items()
                if item["status"] == "unmodeled_exact_configuration"
            },
            {
                "sandero_tce100_without_exact_configuration",
                "stepway_tce110_without_exact_configuration",
                "duster_hybridg150_without_exact_configuration",
            },
        )
        self.assertEqual(
            self.classifications["jogger_blank_wltp_cells"]["status"],
            "no_observation",
        )
        self.assertEqual(
            self.classifications["sandero_wltp_placeholders"]["status"],
            "no_observation",
        )

    def test_priority_queue_selects_automatic_sandero_without_schema_change(self) -> None:
        queue = self.report["priority_queue"]
        self.assertEqual([item["priority"] for item in queue], [1, 2, 3, 4])
        self.assertEqual(
            queue[0]["package"],
            "Sandero Eco-G 120 Automatic Brochure Technical Import",
        )
        candidate = self.classifications["sandero_ecog120_automatic_exact_candidate"]
        self.assertEqual(candidate["status"], "next_package_candidate")
        self.assertEqual(candidate["configuration_count"], 2)
        self.assertEqual(
            set(candidate["attributes"]),
            {
                "engine_power",
                "engine_torque",
                "engine_displacement",
                "cylinder_count",
                "total_valve_count",
                "emission_standard",
                "gearbox_type",
                "gear_count",
                "top_speed",
                "acceleration_0_100",
                "fuel_tank_capacity",
                "minimum_kerb_weight",
                "gross_vehicle_weight",
                "gross_train_weight",
                "braked_trailer_weight",
            },
        )
        self.assertEqual(
            self.report["next_package"]["name"],
            "Sandero Eco-G 120 Automatic Brochure Technical Import",
        )

    def test_exact_later_candidates_remain_separate_packages(self) -> None:
        exact = {
            code
            for code, item in self.classifications.items()
            if item["status"] in {"exact_import_candidate", "exact_range_candidate"}
        }
        self.assertEqual(
            exact,
            {
                "bigster_gross_train_weight_candidate",
                "bigster_unbraked_trailer_weight_candidate",
                "jogger_hybrid155_acceleration_candidate",
                "jogger_hybrid_battery_capacity_candidate",
                "jogger_engine_speed_range_candidate",
                "duster_gross_train_weight_candidate",
                "duster_unbraked_trailer_weight_candidate",
            },
        )

    def test_review_verifier_reproduces_repository_contract(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: official brochure technical gap review", completed.stdout)

    def test_project_state_advances_to_automatic_sandero_import(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Official Brochure Technical Gap Review")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Sandero Eco-G 120 Automatic Brochure Technical Import",
        )
        self.assertEqual(state["baseline"]["rows"], 8852)
        self.assertEqual(state["baseline"]["configuration_values"], 2188)
        self.assertEqual(state["baseline"]["configuration_import_specs"], 117)


if __name__ == "__main__":
    unittest.main()
