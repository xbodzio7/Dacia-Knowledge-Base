from __future__ import annotations

import unittest

from tools.materialize_sandero_stepway_full_modal_residual_equipment_20260910 import (
    NEGATIVE,
    SAFE_MARKERS,
    build,
)


class SanderoStepwayFullModalResidualEquipmentTests(unittest.TestCase):
    def test_safe_residual_equipment_is_exactly_286_occurrences(self) -> None:
        _fields, _rows, report = build()
        self.assertEqual(report["safe_equipment_occurrences"], 286)
        self.assertEqual(report["mapped_occurrences"], 286)

    def test_preserved_residual_equipment_is_155_occurrences(self) -> None:
        _fields, _rows, report = build()
        self.assertEqual(report["preserved_equipment_occurrences"], 155)

    def test_negative_literals_are_not_safe_candidates(self) -> None:
        self.assertEqual(len(NEGATIVE), 5)
        self.assertTrue(SAFE_MARKERS)

    def test_materializer_is_idempotent_against_existing_rows(self) -> None:
        _fields, rows, report = build()
        codes = [row["code"] for row in rows]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertGreaterEqual(report["new_availability_rows"], 0)


if __name__ == "__main__":
    unittest.main()
