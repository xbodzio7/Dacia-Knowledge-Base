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
REPORT = REPORTING / "official_brochure_technical_gap_resolution_closure_review.json"
VERIFIER = ROOT / "tools" / "review_official_brochure_technical_gap_resolution_closure_20260726.py"

SOURCES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_sandero_stepway_brochure_20260202",
    "src_pl_jogger_brochure_20251217",
    "src_pl_bigster_brochure_20251210",
    "src_pl_duster_mini_brochure_20251020",
}
EXPECTED_SCALAR = Counter(
    {
        "src_pl_sandero_brochure_20260202": 92,
        "src_pl_sandero_stepway_brochure_20260202": 72,
        "src_pl_jogger_brochure_20251217": 248,
        "src_pl_bigster_brochure_20251210": 180,
        "src_pl_duster_mini_brochure_20251020": 144,
    }
)
EXPECTED_CURRENT_SCALAR = Counter(
    {
        "src_pl_sandero_brochure_20260202": 132,
        "src_pl_sandero_stepway_brochure_20260202": 72,
        "src_pl_jogger_brochure_20251217": 516,
        "src_pl_bigster_brochure_20251210": 248,
        "src_pl_duster_mini_brochure_20251020": 244,
    }
)
EXPECTED_RANGES = Counter(
    {
        "src_pl_jogger_brochure_20251217": 58,
        "src_pl_duster_mini_brochure_20251020": 10,
    }
)
EXPECTED_CURRENT_RANGES = EXPECTED_RANGES + Counter(
    {"src_pl_bigster_brochure_20251210": 34}
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class OfficialBrochureTechnicalGapResolutionClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.original = json.loads((REPORTING / "official_brochure_technical_gap_review.json").read_text(encoding="utf-8"))
        cls.scalar = [
            row
            for row in rows(MASTER / "configuration_attribute_values.csv")
            if row["source_code"] in SOURCES
        ]
        cls.ranges = [
            row
            for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
            if row["source_code"] in SOURCES
        ]

    def test_original_twenty_nine_classifications_partition_exactly(self) -> None:
        self.assertEqual(len(self.original["classifications"]), 29)
        self.assertEqual(self.report["original_inventory"]["priority_classifications"], 13)
        self.assertEqual(self.report["original_inventory"]["residual_classifications"], 16)
        resolved = {
            code
            for package in self.report["priority_resolutions"]
            for code in package["classification_codes"]
        }
        residual = set(self.report["residual_evidence"]["classification_codes"])
        original = {item["code"] for item in self.original["classifications"]}
        self.assertEqual(resolved | residual, original)
        self.assertTrue(resolved.isdisjoint(residual))

    def test_four_priority_packages_have_exact_receipts(self) -> None:
        packages = self.report["priority_resolutions"]
        self.assertEqual([item["priority"] for item in packages], [1, 2, 3, 4])
        self.assertEqual({item.get("pull_request") for item in packages[:3]}, {260, 261, 262})
        self.assertEqual(packages[3]["pull_requests"], [263, 264, 265, 266, 267, 268])
        self.assertEqual(sum(item["scalar_values"] for item in packages), 379)
        self.assertEqual(sum(item["range_values"] for item in packages), 68)
        self.assertEqual(sum(item["new_attributes"] for item in packages), 4)

    def test_current_brochure_scalar_and_range_coverage_is_exact(self) -> None:
        self.assertEqual(len(self.scalar), 1212)
        self.assertEqual(len(self.ranges), 102)
        self.assertEqual(
            Counter(row["source_code"] for row in self.scalar),
            EXPECTED_CURRENT_SCALAR,
        )
        self.assertEqual(Counter(row["source_code"] for row in self.ranges), EXPECTED_CURRENT_RANGES)
        self.assertEqual(
            Counter(self.report["current_brochure_coverage"]["scalar_values_by_source"]),
            EXPECTED_SCALAR,
        )
        self.assertEqual(
            Counter(self.report["current_brochure_coverage"]["range_values_by_source"]),
            EXPECTED_RANGES,
        )

    def test_priority_id_receipts_are_contiguous(self) -> None:
        scalar = [row for row in self.scalar if 2189 <= int(row["id"]) <= 2567]
        ranges = [row for row in self.ranges if 177 <= int(row["id"]) <= 244]
        self.assertEqual(len(scalar), 379)
        self.assertEqual([int(row["id"]) for row in scalar], list(range(2189, 2568)))
        self.assertEqual(len(ranges), 68)
        self.assertEqual([int(row["id"]) for row in ranges], list(range(177, 245)))

    def test_sixteen_residual_classifications_preserve_source_statuses(self) -> None:
        classifications = {item["code"]: item for item in self.original["classifications"]}
        residual = self.report["residual_evidence"]["classification_codes"]
        counts = Counter(classifications[code]["status"] for code in residual)
        self.assertEqual(
            counts,
            Counter(
                {
                    "covered_or_superseded": 5,
                    "covered_or_explicitly_deferred": 4,
                    "unmodeled_exact_configuration": 3,
                    "no_observation": 2,
                    "ambiguous_source_evidence": 1,
                    "no_observation_or_generic_projection": 1,
                }
            ),
        )

    def test_blank_ambiguous_and_generic_evidence_remains_unimported(self) -> None:
        self.assertFalse(any(
            row["source_code"] == "src_pl_jogger_brochure_20251217"
            and row["attribute_code"] in {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"}
            for row in self.scalar
        ))
        self.assertFalse(any(
            row["source_code"] in {"src_pl_jogger_brochure_20251217", "src_pl_sandero_brochure_20260202"}
            and row["attribute_code"] in {"co2_emissions", "fuel_consumption_combined"}
            for row in self.scalar
        ))
        approved = [
            row
            for row in self.scalar
            if 2568 <= int(row["id"]) <= 2949
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
        self.assertFalse(any(
            row["attribute_code"] in {"approach_angle", "departure_angle"}
            for row in approved
        ))

    def test_closure_verifier_and_priority_receipts_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: official brochure technical gap resolution closure review", completed.stdout)

    def test_project_state_preserves_completed_closure_receipt(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 923)
        self.assertGreaterEqual(state["baseline"]["rows"], 9306)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2567)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
