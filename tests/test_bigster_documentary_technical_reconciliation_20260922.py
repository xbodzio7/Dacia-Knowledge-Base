import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / "data" / "master" / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterDocumentaryTechnicalReconciliation20260922Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ranges = read("configuration_attribute_value_ranges.csv")
        cls.values = read("configuration_attribute_values.csv")

    def test_closure_report_declares_no_master_mutation(self):
        report = json.loads((ROOT / "data/reporting/bigster_documentary_technical_reconciliation_001.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["scope"]["master_mutations_required"], 0)
        source_code = report["source"]["source_code"]
        source_ranges = [
            row for row in self.ranges
            if row["source_code"] == source_code
        ]
        self.assertEqual(report["documentary_ranges"]["record_count"], len(source_ranges))
        self.assertEqual(
            {row["configuration_code"] for row in source_ranges},
            {
                "bigster_essential_mildhybridg140_4x2_manual",
                "bigster_expression_mildhybridg140_4x2_manual",
                "bigster_extreme_mildhybridg140_4x2_manual",
                "bigster_journey_mildhybridg140_4x2_manual",
                "bigster_essential_mildhybrid140_4x2_manual",
                "bigster_expression_mildhybrid140_4x2_manual",
                "bigster_extreme_mildhybrid140_4x2_manual",
                "bigster_journey_mildhybrid140_4x2_manual",
                "bigster_expression_hybrid155_4x2_automatic",
                "bigster_extreme_hybrid155_4x2_automatic",
                "bigster_journey_hybrid155_4x2_automatic",
            },
        )
        self.assertFalse(report["evidence_policy"]["configurator_used"])

    def test_three_import_ready_facts_are_already_source_bound_in_master(self):
        source = "src_pl_bigster_brochure_20251210"
        eco = [r for r in self.values if r["source_code"] == source and r["attribute_code"] == "eco_mode" and r["value"] == "true"]
        power = [r for r in self.values if r["source_code"] == source and r["attribute_code"] == "hybrid_system_power_total" and r["value"] == "113"]
        battery = [r for r in self.values if r["source_code"] == source and r["attribute_code"] == "hybrid_battery_type" and r["value"] == "lithium_ion"]
        self.assertEqual(len(eco), 14)
        self.assertEqual(len(power), 3)
        self.assertEqual(len(battery), 14)


if __name__ == "__main__":
    unittest.main()
