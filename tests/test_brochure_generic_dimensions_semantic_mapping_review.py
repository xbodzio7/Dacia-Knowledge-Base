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
REPORT = REPORTING / "brochure_generic_dimensions_semantic_mapping_review.json"
VERIFIER = ROOT / "tools" / "review_brochure_generic_dimensions_semantic_mapping_20260726.py"

ATTRIBUTE_CODES = {
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


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def mapping(items: list[dict[str, object]]) -> dict[str, int]:
    return {str(item["attribute_code"]): int(item["value"]) for item in items}


class BrochureGenericDimensionsSemanticMappingReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.sources = {item["source_code"]: item for item in cls.report["sources"]}
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.relationships = rows(MASTER / "source_configurations.csv")

    def test_visual_review_maps_three_exact_source_pages(self) -> None:
        self.assertEqual(self.report["method"], "visual_pdf_diagram_review")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(self.report["scope"], {
            "sources": 3,
            "source_pages": 3,
            "active_configurations": 53,
            "source_related_configurations": 36,
            "import_eligible_configurations": 36,
        })
        self.assertEqual(
            {source: item["page"] for source, item in self.sources.items()},
            {
                "src_pl_sandero_brochure_20260202": 20,
                "src_pl_jogger_brochure_20251217": 22,
                "src_pl_duster_mini_brochure_20251020": 24,
            },
        )

    def test_sandero_mapping_is_visually_explicit(self) -> None:
        self.assertEqual(
            mapping(self.sources["src_pl_sandero_brochure_20260202"]["mappings"]),
            {
                "overall_height": 1496,
                "front_track": 1533,
                "overall_width": 1853,
                "overall_width_with_mirrors": 2012,
                "rear_track": 1519,
                "front_overhang": 833,
                "wheelbase": 2604,
                "rear_overhang": 665,
                "overall_length": 4102,
                "ground_clearance": 162,
            },
        )
        self.assertEqual(self.sources["src_pl_sandero_brochure_20260202"]["planned_scalar_values"], 40)

    def test_jogger_mapping_separates_roof_and_rail_heights(self) -> None:
        mapped = mapping(self.sources["src_pl_jogger_brochure_20251217"]["mappings"])
        self.assertEqual(mapped["roof_height_with_rails"], 1689)
        self.assertEqual(mapped["overall_height"], 1630)
        self.assertEqual(mapped["overall_length"], 4550)
        self.assertEqual(mapped["wheelbase"], 2898)
        self.assertEqual(mapped["ground_clearance"], 200)
        self.assertEqual(len(mapped), 11)
        self.assertEqual(self.sources["src_pl_jogger_brochure_20251217"]["planned_scalar_values"], 242)

    def test_duster_maps_4x2_and_defers_4x4(self) -> None:
        duster = self.sources["src_pl_duster_mini_brochure_20251020"]
        eligible = mapping(duster["eligible_4x2_mappings"])
        deferred = mapping(duster["deferred_4x4_mappings"])
        self.assertEqual((eligible["roof_height_with_rails"], deferred["roof_height_with_rails"]), (1656, 1661))
        self.assertEqual((eligible["front_track"], deferred["front_track"]), (1574, 1573))
        self.assertEqual((eligible["rear_track"], deferred["rear_track"]), (1547, 1562))
        self.assertEqual((eligible["ground_clearance"], deferred["ground_clearance"]), (209, 217))
        self.assertEqual(duster["import_eligible_configurations"], 10)
        self.assertEqual(duster["planned_scalar_values"], 100)
        self.assertEqual(duster["deferred_scalar_values"], 0)
        self.assertEqual(duster["deferred_mapping_template_values"], 10)

    def test_source_relationships_define_thirty_six_import_targets(self) -> None:
        counts = Counter(
            row["source_code"]
            for row in self.relationships
            if row["relationship"] == "brochure_technical_data_for"
            and row["source_code"] in self.sources
        )
        self.assertEqual(counts, Counter({
            "src_pl_sandero_brochure_20260202": 4,
            "src_pl_jogger_brochure_20251217": 22,
            "src_pl_duster_mini_brochure_20251020": 10,
        }))
        self.assertEqual(sum(counts.values()), 36)

    def test_import_plan_has_382_unique_historical_values(self) -> None:
        self.assertEqual(self.report["import_plan"], {
            "sources": 3,
            "configurations": 36,
            "scalar_values": 382,
            "sandero_scalar_values": 40,
            "jogger_scalar_values": 242,
            "duster_4x2_scalar_values": 100,
            "duster_4x4_scalar_values": 0,
            "mode": "append_only_historical_observations",
        })
        self.assertEqual(self.report["attribute_contract"]["new_attributes"], 0)
        self.assertEqual(set(self.report["attribute_contract"]["codes"]), ATTRIBUTE_CODES)
        self.assertEqual(
            max(
                int(row["id"])
                for row in self.values
                if row["source_code"] in self.sources
                and row["attribute_code"] in ATTRIBUTE_CODES
            ),
            2949,
        )
        brochure_sources = set(self.sources)
        approved = [
            row
            for row in self.values
            if row["source_code"] in brochure_sources
            and row["attribute_code"] in ATTRIBUTE_CODES
            and 2568 <= int(row["id"]) <= 2949
        ]
        self.assertEqual(len(approved), 382)
        self.assertEqual(
            [int(row["id"]) for row in approved],
            list(range(2568, 2950)),
        )
        self.assertEqual(
            Counter(row["source_code"] for row in approved),
            Counter({
                "src_pl_sandero_brochure_20260202": 40,
                "src_pl_jogger_brochure_20251217": 242,
                "src_pl_duster_mini_brochure_20251020": 100,
            }),
        )

    def test_visual_exclusions_block_false_offroad_and_interior_mappings(self) -> None:
        excluded = {item["source_code"]: item for item in self.report["excluded_visual_values"]}
        self.assertIn(14, excluded["src_pl_duster_mini_brochure_20251020"]["values"])
        self.assertIn("approach_angle", excluded["src_pl_duster_mini_brochure_20251020"]["reason"])
        self.assertIn("seatback", excluded["src_pl_duster_mini_brochure_20251020"]["reason"])
        self.assertIn(1985, excluded["src_pl_sandero_brochure_20260202"]["values"])
        self.assertIn(1243, excluded["src_pl_jogger_brochure_20251217"]["values"])
        self.assertEqual(len(self.report["non_inference_contract"]), 7)

    def test_verifier_and_project_state_complete_review(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: brochure generic dimensions semantic mapping review", completed.stdout)

        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 955)
        self.assertGreaterEqual(state["baseline"]["rows"], 9688)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2949)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
