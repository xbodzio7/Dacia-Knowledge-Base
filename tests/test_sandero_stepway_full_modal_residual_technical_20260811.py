from __future__ import annotations

import unittest

from tools.materialize_sandero_stepway_full_modal_residual_technical_20260811 import MAPPING, verify


class SanderoStepwayResidualTechnicalTests(unittest.TestCase):
    def test_mapping_targets_exist_and_are_current(self) -> None:
        self.assertEqual(MAPPING["Liczba drzwi"][0], "number_of_doors")
        self.assertNotIn("door_count", {target for target, _kind in MAPPING.values()})

    def test_live_candidate_count_is_315(self) -> None:
        result = verify()
        self.assertEqual(result["candidate_rows"], 315)

    def test_materialization_is_idempotent(self) -> None:
        result = verify()
        self.assertLessEqual(result["materialized_rows"], result["candidate_rows"])


if __name__ == "__main__":
    unittest.main()
