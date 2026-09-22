import csv
import unittest
from pathlib import Path


class BigsterDocumentaryTechnicalReconciliation20260922Tests(unittest.TestCase):
    def test_page20_ranges_are_complete_and_source_bound(self):
        path = Path(__file__).resolve().parents[1] / "data/master/configuration_attribute_value_ranges.csv"
        rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
        rows = [r for r in rows if r["source_code"] == "src_pl_bigster_brochure_20251210" and r["observation_date"] == "2025-12-10" and r["attribute_code"] in {"co2_emissions", "fuel_consumption_combined"}]
        self.assertEqual(len(rows), 30)
        self.assertEqual({r["configuration_code"] for r in rows}, {
            "bigster_essential_mildhybrid140_4x2_manual", "bigster_expression_mildhybrid140_4x2_manual", "bigster_extreme_mildhybrid140_4x2_manual", "bigster_journey_mildhybrid140_4x2_manual",
            "bigster_essential_mildhybridg140_4x2_manual", "bigster_expression_mildhybridg140_4x2_manual", "bigster_extreme_mildhybridg140_4x2_manual", "bigster_journey_mildhybridg140_4x2_manual",
            "bigster_expression_hybrid155_4x2_automatic", "bigster_extreme_hybrid155_4x2_automatic", "bigster_journey_hybrid155_4x2_automatic",
        })
        self.assertTrue(all(r["lower_inclusive"] == "true" and r["upper_inclusive"] == "true" for r in rows))
        self.assertEqual(sum(r["attribute_code"] == "co2_emissions" for r in rows), 15)
        self.assertEqual(sum(r["attribute_code"] == "fuel_consumption_combined" for r in rows), 15)


if __name__ == "__main__":
    unittest.main()
