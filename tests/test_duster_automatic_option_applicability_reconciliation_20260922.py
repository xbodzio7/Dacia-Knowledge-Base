import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/duster_automatic_option_applicability_reconciliation_20260920.json"
COMMERCIAL = ROOT / "data/master/commercial_item_configurations.csv"


class DusterAutomaticOptionApplicabilityReconciliationTest(unittest.TestCase):
    def test_report_is_master_reconciled(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "complete")
        self.assertEqual(
            report["master_reconciliation"]["result"],
            "All unambiguous configuration-level package identities from the existing evidence report are already present in the commercial master. No additional master mutation is required in this reconciliation package. Numbered winter labels remain evidence-only.",
        )

    def test_all_unambiguous_exact_configuration_items_exist(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        expected = set(report["master_reconciliation"]["resolved_exact_configuration_items"])
        with COMMERCIAL.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        codes = {row["code"] for row in rows}
        self.assertTrue(expected <= codes)
        self.assertEqual(len(expected), 8)

    def test_numbered_winter_labels_remain_deferred(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        deferred = report["master_reconciliation"]["unresolved_source_bound_items"]
        self.assertEqual(len(deferred), 5)
        self.assertTrue(any("ZIMOWY II" in item for item in deferred))
        self.assertTrue(any("ZIMOWY III" in item for item in deferred))
        self.assertTrue(any("winter package naming conflict" in item for item in deferred))


if __name__ == "__main__":
    unittest.main()
