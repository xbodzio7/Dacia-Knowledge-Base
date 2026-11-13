from __future__ import annotations
import csv
import json
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))
from import_duster_price_list_20261102 import check  # noqa: E402

REPORT = REPOSITORY / "data" / "reporting" / "duster_price_list_20261102_commercial_reconciliation.json"
SOURCES = REPOSITORY / "data" / "master" / "sources.csv"
SOURCE = "src_pl_duster_price_my26_20261102"
SOURCE_SHA256 = "dd6c65d048d7531251967ba39bb8ab6767256882325254e9b3eaafac11d89118"
SOURCE_PATH = "PDF/Cenniki/DACIA DUSTER cennik MY26 20261102.pdf"


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

    def test_archived_source_and_printed_page_inventory_are_exact(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        source = report["source"]
        self.assertEqual(source["source_code"], SOURCE)
        self.assertEqual(source["page_count"], 10)
        self.assertEqual(source["raw_pdf_sha256"], SOURCE_SHA256)
        self.assertEqual(source["raw_pdf_repository_path"], SOURCE_PATH)
        with SOURCES.open(encoding="utf-8-sig", newline="") as handle:
            registered = next(row for row in csv.DictReader(handle) if row["code"] == SOURCE)
        self.assertIn("Pages 7–10 visually reviewed", registered["notes"])
        self.assertNotIn("require visual review", registered["notes"])
        self.assertEqual([page["page"] for page in report["page_inventory"]], list(range(1, 11)))

    def test_hybrid_155_voltage_preserves_distinct_source_contexts(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        technical = report["reconciliation"]["technical_scalars"]
        self.assertNotIn("unmaterialized_source_delta", technical)
        self.assertIn("230 V", technical["result"])
        self.assertIn("260 V", technical["result"])
        self.assertNotIn("280 V", technical["result"])
        deferred = [item for item in report["deferred"] if item["item"] == "Hybrid 155 battery voltage narrative/table discrepancy"]
        self.assertEqual(len(deferred), 1)
        self.assertEqual(deferred[0]["page"], 2)
        self.assertIn("260 V", deferred[0]["reason"])
        self.assertIn("230 V", deferred[0]["reason"])
        self.assertEqual(report["page_inventory"][5]["page"], 6)
        self.assertIn("230 V", report["page_inventory"][5]["classification"])
        self.assertEqual(report["page_inventory"][-1]["page"], 10)
        self.assertEqual(report["page_inventory"][-1]["section"], "Legal and commercial terms")
        self.assertEqual(report["page_inventory"][5]["review"], "complete_with_contextual_discrepancy")
        self.assertTrue(any("contains 10 pages" in note for note in report["evidence_notes"]))
        self.assertFalse(any("contains 9 pages" in note for note in report["evidence_notes"]))


if __name__ == "__main__":
    unittest.main()
