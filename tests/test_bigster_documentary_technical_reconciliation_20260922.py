import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BigsterDocumentaryTechnicalReconciliation20260922Tests(unittest.TestCase):
    def test_closure_report_declares_no_master_mutation(self):
        report = json.loads((ROOT / "data/reporting/bigster_documentary_technical_reconciliation_001.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["scope"]["master_mutations_required"], 0)
        self.assertEqual(report["documentary_ranges"]["record_count"], 30)
        self.assertFalse(report["evidence_policy"]["configurator_used"])

    def test_three_import_ready_facts_are_already_source_bound_in_master(self):
        rows = list(csv.DictReader((ROOT / "data/master/configuration_attribute_values.csv").open(encoding="utf-8-sig", newline="")))
        source = "src_pl_bigster_brochure_20251210"
        eco = [r for r in rows if r["source_code"] == source and r["attribute_code"] == "eco_mode" and r["value"] == "true"]
        power = [r for r in rows if r["source_code"] == source and r["attribute_code"] == "hybrid_system_power_total" and r["value"] == "113"]
        battery = [r for r in rows if r["source_code"] == source and r["attribute_code"] == "hybrid_battery_type" and r["value"] == "lithium_ion"]
        self.assertEqual(len(eco), 14)
        self.assertEqual(len(power), 3)
        self.assertEqual(len(battery), 14)


if __name__ == "__main__":
    unittest.main()
