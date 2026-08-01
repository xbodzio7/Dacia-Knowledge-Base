"""Contract tests for the exact Stepway Extreme automatic source-gap package."""
from __future__ import annotations

import json
import unittest

from tools import import_sandero_stepway_extreme_auto_source_gap_20260626 as package


class SanderoStepwayExtremeAutomaticSourceGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = package.load_spec()
        cls.values = package.generated_value_rows(cls.spec)
        cls.ranges = package.generated_range_rows(cls.spec)
        cls.availability = package.generated_availability_rows(cls.spec)

    def test_exact_source_identity_and_specification(self) -> None:
        self.assertEqual(package.sha256(package.SOURCE), package.SOURCE_SHA256)
        self.assertEqual(len(self.spec), 6)
        self.assertEqual(len(self.values), 2)
        self.assertEqual(len(self.ranges), 3)
        self.assertEqual(len(self.availability), 1)

    def test_two_scalar_values_are_exact(self) -> None:
        self.assertEqual(
            {(row["attribute_code"], row["fuel_type_code"]): row["value"] for row in self.values},
            {("overall_height", ""): "1586", ("overall_width_with_mirrors", ""): "2012"},
        )

    def test_three_ranges_preserve_printed_endpoints(self) -> None:
        self.assertEqual(
            {(row["attribute_code"], row["fuel_type_code"]): (row["minimum_value"], row["maximum_value"]) for row in self.ranges},
            {
                ("ground_clearance", ""): ("170", "200"),
                ("max_torque_rpm", "lpg"): ("1750", "3750"),
                ("max_torque_rpm", "petrol"): ("2000", "4000"),
            },
        )

    def test_front_rear_parking_assistance_is_direct_standard_equipment(self) -> None:
        row = self.availability[0]
        self.assertEqual(row["attribute_code"], "parking_assist_system")
        self.assertEqual(row["availability_status"], "standard")
        self.assertIn("front/rear parking assistance", row["notes"])

    def test_materialized_ids_are_exact_contiguous_suffixes(self) -> None:
        values = package.selected_by_codes(package.read_rows(package.VALUE_OUTPUT), {row["code"] for row in self.values})
        ranges = package.selected_by_codes(package.read_rows(package.RANGE_OUTPUT), {row["code"] for row in self.ranges})
        availability = package.selected_by_codes(package.read_rows(package.AVAILABILITY_OUTPUT), {row["code"] for row in self.availability})
        self.assertEqual(sorted(int(row["id"]) for row in values), [3564, 3565])
        self.assertEqual(sorted(int(row["id"]) for row in ranges), [314, 315, 316])
        self.assertEqual(sorted(int(row["id"]) for row in availability), [5905])

    def test_review_partitions_resolved_out_of_scope_and_unstated_slots(self) -> None:
        review = json.loads(package.REVIEW_JSON.read_text(encoding="utf-8"))
        self.assertEqual(review, package.review_payload())
        reconciliation = review["reconciliation"]
        self.assertEqual(reconciliation["resolved_unique_slots"], 6)
        self.assertEqual(reconciliation["preserved_out_of_scope_slots"], 1)
        self.assertEqual(reconciliation["remaining_unique_slots"], 6)

    def test_reanalysis_exhausts_source_and_advances_selection(self) -> None:
        payload = package.analysis.collect(package.ROOT)
        current = next(item for item in payload["ranked_candidates"] if item["source_code"] == package.SOURCE_CODE)
        self.assertEqual(current["selection_status"], package.EXHAUSTED_CLASSIFICATION)
        selected = payload.get("selected_next_package")
        if selected is not None:
            self.assertEqual(selected["selection_status"], "eligible")
            self.assertNotEqual(selected["source_code"], package.SOURCE_CODE)

    def test_full_materialized_contract_passes(self) -> None:
        package.verify_materialized()


if __name__ == "__main__":
    unittest.main()
