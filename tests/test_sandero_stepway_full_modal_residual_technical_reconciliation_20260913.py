from __future__ import annotations

import unittest

from tools.reconcile_sandero_stepway_full_modal_residual_technical_20260913 import MAPPING, audit


class SanderoStepwayResidualTechnicalReconciliationTests(unittest.TestCase):
    def test_candidate_contract(self) -> None:
        result = audit()
        self.assertEqual(result["candidate_rows"], 315)
        self.assertEqual(result["mapping_labels"], 21)

    def test_all_current_mapping_targets_exist(self) -> None:
        result = audit()
        self.assertEqual(result["attributes_missing_from_current_dictionary"], [])

    def test_no_materialization_or_promotion(self) -> None:
        result = audit()
        self.assertFalse(result["materialization_performed"])
        self.assertFalse(result["promotion_allowed"])

    def test_known_semantic_blocker_is_explicit(self) -> None:
        result = audit()
        self.assertEqual(
            result["review_required"]["Rodzaj napędu"],
            "drive_layout_value_vocabulary_requires_reconciliation",
        )
        self.assertEqual(MAPPING["Liczba drzwi"], "number_of_doors")
        self.assertNotIn("door_count", MAPPING.values())


if __name__ == "__main__":
    unittest.main()
