from __future__ import annotations

import unittest

from tools.configuration_value_range_reporting import (
    combine_latest_observations,
    range_relation,
)


class RangeReportingHelperTests(unittest.TestCase):
    def test_newer_range_supersedes_older_scalar(self) -> None:
        key = ("cfg", "height", "")
        scalar = {key: {"observation_date": "2026-01-01", "value": "100"}}
        ranged = {
            key: {
                "observation_date": "2026-02-01",
                "minimum_value": "99",
                "maximum_value": "101",
            }
        }
        result = combine_latest_observations(scalar, ranged, ValueError)
        self.assertEqual(result[key]["_observation_kind"], "range")

    def test_same_date_scalar_range_collision_is_rejected(self) -> None:
        key = ("cfg", "height", "")
        scalar = {key: {"observation_date": "2026-01-01", "value": "100"}}
        ranged = {
            key: {
                "observation_date": "2026-01-01",
                "minimum_value": "99",
                "maximum_value": "101",
            }
        }
        with self.assertRaisesRegex(ValueError, "collide on the same date"):
            combine_latest_observations(scalar, ranged, ValueError)

    def test_identical_closed_ranges(self) -> None:
        state = {
            "minimum_value": "5.7",
            "maximum_value": "6.1",
            "lower_inclusive": True,
            "upper_inclusive": True,
        }
        self.assertEqual(range_relation(state, state), "identical")

    def test_overlapping_range_and_scalar_point(self) -> None:
        ranged = {
            "minimum_value": "5.7",
            "maximum_value": "6.1",
            "lower_inclusive": True,
            "upper_inclusive": True,
        }
        point = {"normalized_value": "6.0"}
        self.assertEqual(range_relation(ranged, point), "overlapping")

    def test_touching_open_ranges_are_disjoint(self) -> None:
        left = {
            "minimum_value": "1",
            "maximum_value": "2",
            "lower_inclusive": True,
            "upper_inclusive": False,
        }
        right = {
            "minimum_value": "2",
            "maximum_value": "3",
            "lower_inclusive": True,
            "upper_inclusive": True,
        }
        self.assertEqual(range_relation(left, right), "disjoint")


if __name__ == "__main__":
    unittest.main()
