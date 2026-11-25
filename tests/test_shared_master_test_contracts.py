from __future__ import annotations

import ast
import unittest

from tools.check_shared_master_test_contracts import (
    _comprehension_origin,
    _has_exact_source_scope,
    _master_attributes,
)


class SharedMasterTestContractGuardTests(unittest.TestCase):
    def test_detects_shared_master_csv_readers(self) -> None:
        tree = ast.parse(
            """
class Example:
    @classmethod
    def setUpClass(cls):
        cls.items = read("commercial_items.csv")
"""
        )
        self.assertEqual(_master_attributes(tree), {"items": "commercial_items.csv"})

    def test_unfiltered_shared_table_comprehension_is_not_source_scoped(self) -> None:
        tree = ast.parse(
            '{row["observation_date"] for row in self.items}'
        )
        master = {"items": "commercial_items.csv"}
        sourced, fields = _comprehension_origin(tree.body[0].value, master)
        self.assertTrue(sourced)
        self.assertFalse(_has_exact_source_scope(fields, tree.body[0].value))

    def test_exact_source_code_filter_is_recognized(self) -> None:
        tree = ast.parse(
            '{row["code"] for row in self.items if row["source_code"] in owned_sources}'
        )
        master = {"items": "commercial_items.csv"}
        sourced, fields = _comprehension_origin(tree.body[0].value, master)
        self.assertTrue(sourced)
        self.assertTrue(_has_exact_source_scope(fields, tree.body[0].value))


if __name__ == "__main__":
    unittest.main()
