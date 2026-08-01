from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools import import_sandero_stepway_expression_source_gap_20260626 as package

ROOT = Path(__file__).resolve().parents[1]


class SanderoStepwayExpressionSourceGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = package.load_spec()
        cls.values = package.generated_value_rows(cls.spec)
        cls.ranges = package.generated_range_rows(cls.spec)

    def test_exact_source_identity_and_specification(self) -> None:
        self.assertEqual(package.sha256(package.SOURCE), package.SOURCE_SHA256)
        self.assertEqual(len(self.spec), 6)
        self.assertEqual(len(self.values), 3)
        self.assertEqual(len(self.ranges), 3)
        self.assertEqual(
            {
                (row["record_type"], row["attribute_code"], row["fuel_type_code"])
                for row in self.spec
            },
            {
                ("value", "overall_height", ""),
                ("value", "overall_width_with_mirrors", ""),
                ("value", "wheel_finish", ""),
                ("range", "ground_clearance", ""),
                ("range", "max_torque_rpm", "lpg"),
                ("range", "max_torque_rpm", "petrol"),
            },
        )

    def test_three_scalar_values_are_exact(self) -> None:
        actual = {
            (row["attribute_code"], row["fuel_type_code"]): row["value"]
            for row in self.values
        }
        self.assertEqual(
            actual,
            {
                ("overall_height", ""): "1586",
                ("overall_width_with_mirrors", ""): "2012",
                ("wheel_finish", ""): "stalowe",
            },
        )
        self.assertTrue(all(row["source_code"] == package.SOURCE_CODE for row in self.values))

    def test_three_ranges_preserve_printed_endpoints(self) -> None:
        actual = {
            (row["attribute_code"], row["fuel_type_code"]): (
                row["minimum_value"],
                row["maximum_value"],
                row["lower_inclusive"],
                row["upper_inclusive"],
            )
            for row in self.ranges
        }
        self.assertEqual(
            actual,
            {
                ("ground_clearance", ""): ("170", "200", "true", "true"),
                ("max_torque_rpm", "lpg"): ("1750", "3750", "true", "true"),
                ("max_torque_rpm", "petrol"): ("2000", "4000", "true", "true"),
            },
        )

    def test_materialized_ids_are_exact_contiguous_suffixes(self) -> None:
        values = package.selected_by_codes(
            package.read_rows(package.VALUE_OUTPUT),
            {row["code"] for row in self.values},
        )
        ranges = package.selected_by_codes(
            package.read_rows(package.RANGE_OUTPUT),
            {row["code"] for row in self.ranges},
        )
        self.assertEqual(sorted(int(row["id"]) for row in values), [3556, 3557, 3558])
        self.assertEqual(sorted(int(row["id"]) for row in ranges), [305, 306, 307])

    def test_both_completeness_scopes_use_fourth_gear(self) -> None:
        values = package.read_rows(package.VALUE_OUTPUT)
        for path in package.SCOPES:
            payload = json.loads(path.read_text(encoding="utf-8"))
            slots = {
                (slot.get("fuel_type_code", ""), slot.get("gear_number", ""))
                for slot in payload["technical_slots"]
                if slot.get("attribute_code") == "elasticity_80_120"
            }
            self.assertEqual(slots, {("lpg", "4"), ("petrol", "4")})
            self.assertEqual(payload, package.scope_payload(path, values))

    def test_review_closes_only_not_stated_slots(self) -> None:
        review = json.loads(package.REVIEW_JSON.read_text(encoding="utf-8"))
        self.assertEqual(review, package.review_payload())
        self.assertEqual(
            review["reconciliation"]["classification"],
            package.EXHAUSTED_CLASSIFICATION,
        )
        self.assertEqual(review["reconciliation"]["resolved_unique_slots"], 6)
        self.assertEqual(review["reconciliation"]["remaining_unique_slots"], 4)
        self.assertEqual(
            {item["attribute_code"] for item in review["reconciliation"]["remaining_slots"]},
            {"front_track", "rear_track", "max_power_rpm"},
        )

    def test_reanalysis_removes_false_and_resolved_gaps(self) -> None:
        payload = package.analysis.collect(ROOT)
        self.assertEqual(payload["summary"]["missing_technical_count"], 111)
        self.assertEqual(payload["summary"]["exhausted_source_candidate_count"], 5)
        current = next(
            item
            for item in payload["ranked_candidates"]
            if item["source_code"] == package.SOURCE_CODE
        )
        self.assertEqual(current["missing_technical"], 8)
        self.assertEqual(current["selection_status"], package.EXHAUSTED_CLASSIFICATION)
        selected = payload["selected_next_package"]
        self.assertIsNotNone(selected)
        self.assertEqual(selected["selection_status"], "eligible")
        self.assertNotEqual(selected["source_code"], package.SOURCE_CODE)

    def test_full_materialized_contract_passes(self) -> None:
        package.verify_materialized()


if __name__ == "__main__":
    unittest.main()
