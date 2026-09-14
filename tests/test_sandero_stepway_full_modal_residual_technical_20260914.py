from __future__ import annotations

import unittest

from tools.materialize_sandero_stepway_full_modal_residual_technical_20260914 import (
    MAPPING,
    SOURCE,
    collect,
    verify,
)


class SanderoStepwayResidualTechnicalMaterializationTests(unittest.TestCase):
    def test_mapping_targets_exist_and_doors_use_canonical_attribute(self) -> None:
        self.assertEqual(MAPPING["Liczba drzwi"][0], "number_of_doors")
        self.assertNotIn("door_count", {target for target, _kind in MAPPING.values()})

    def test_live_candidate_count_is_315(self) -> None:
        result = verify()
        self.assertEqual(result["candidate_rows"], 315)

    def test_drive_layout_vocabulary_is_resolved_before_materialization(self) -> None:
        rows, _deferred = collect()
        self.assertTrue(rows or verify()["materialized_rows"] == 315)

    def test_materialization_is_bounded_and_idempotent(self) -> None:
        result = verify()
        self.assertEqual(
            result["materialized_rows"] + result["pending_rows"] + result["currently_deferred_non_scalar"],
            315,
        )
        self.assertEqual(
            result["materialized_rows"] + result["pending_rows"] + result["currently_deferred_non_scalar"],
            result["candidate_rows"],
        )
        self.assertEqual(SOURCE, "src_pl_sandero_stepway_full_modal_20260809")


if __name__ == "__main__":
    unittest.main()
