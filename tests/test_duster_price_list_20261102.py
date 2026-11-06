from __future__ import annotations
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))
from import_duster_price_list_20261102 import check  # noqa: E402

class DusterPriceList20261102Tests(unittest.TestCase):
    def test_official_price_list_reconciliation_is_complete_and_non_duplicative(self) -> None:
        result = check()
        self.assertEqual(result["configurations"], 16)
        self.assertEqual(result["versions"], 4)
        self.assertEqual(result["new_items"], 2)
        self.assertEqual(result["new_memberships"], 2)
        self.assertEqual(result["dated_commercial_mappings"], 64)
        self.assertEqual(result["catalogue_price_rows_reused"], 16)
        self.assertEqual(result["technical_scalar_observations_reused"], 391)
        self.assertEqual(result["technical_ranges_reused"], 16)
        self.assertEqual(result["equipment_availability_observations_reused"], 1152)

if __name__ == "__main__":
    unittest.main()
