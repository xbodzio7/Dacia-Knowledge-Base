from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT_PATH = ROOT / "data" / "reporting" / "jogger_my26_20261001_paint_and_heated_seat_applicability_review_20261119_001.json"
REGISTRY_PATH = ROOT / "data" / "reporting" / "report_registry.json"
SOURCE_PATH = ROOT / "owner_supplied" / "2026-10-01" / "f5cdbd7878.pdf"
SOURCE_SHA256 = "12e536c1e60e9e7f91228b27a9d962cecacb5a5287d585f419a14af3003e8b46"
SOURCE_CODE = "src_pl_jogger_price_my26_20261001"
REPORT_ID = "jogger_my26_20261001_paint_and_heated_seat_applicability_review_20261119_001"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPaintHeatedSeatApplicabilityReviewTests(unittest.TestCase):
    def test_source_archive_and_report_provenance_are_consistent(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(), SOURCE_SHA256)
        sources = {row["code"]: row for row in read_csv(MASTER / "sources.csv")}
        source = sources[SOURCE_CODE]
        self.assertEqual(source["sha256"], SOURCE_SHA256)
        self.assertEqual(source["document_date"], "2026-10-01")
        self.assertEqual(source["file_path"], "owner_supplied/2026-10-01/f5cdbd7878.pdf")
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["analysed_commit_sha"], "053a96054fe387754f3eb2c4f53e1de5672c669c")
        self.assertEqual(report["scope"]["source_configurations_reviewed"], 12)

    def test_metallic_paint_pair_is_not_promoted_or_confused_with_special_nonmetallic_paint(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        findings = {item["finding_id"]: item for item in report["findings"]}
        self.assertEqual(findings["jogger-metallic-paint-price-pair"]["status"], "needs_review")
        self.assertEqual(report["evidence"]["page_3"]["rows"][1]["grade_cells"], ["2800 / 3000"] * 3)
        items = {row["code"]: row for row in read_csv(MASTER / "commercial_items.csv")}
        self.assertIn("jogger_special_nonmetallic_paint_option", items)
        self.assertNotIn("jogger_metallic_paint_option", items)
        mappings = read_csv(MASTER / "commercial_item_configurations.csv")
        metallic = [row for row in mappings if row["source_code"] == SOURCE_CODE and row["commercial_item_code"] == "jogger_metallic_paint_option"]
        self.assertEqual(metallic, [])
        self.assertEqual(report["outcome"]["commercial_mappings_added"], 0)

    def test_heated_seat_and_winter_package_mappings_match_the_source(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        mappings = [row for row in read_csv(MASTER / "commercial_item_configurations.csv") if row["source_code"] == SOURCE_CODE]
        self.assertEqual(len(mappings), 54)
        heated = [row for row in mappings if row["commercial_item_code"] == "jogger_heated_front_seats_option"]
        self.assertEqual(len(heated), 6)
        self.assertEqual(sum(row["availability_status"] == "optional" and row["amount"] == "700" for row in heated), 4)
        self.assertEqual(sum(row["availability_status"] == "not_available" for row in heated), 2)
        self.assertFalse(any(row["configuration_code"].startswith("jogger_extreme_") and row["availability_status"] == "optional" for row in heated))
        winter = [row for row in mappings if row["commercial_item_code"] == "jogger_winter_package"]
        self.assertEqual(len(winter), 12)
        self.assertEqual(sum(row["availability_status"] == "optional" and row["amount"] == "1200" for row in winter), 6)
        self.assertEqual(sum(row["availability_status"] == "not_available" for row in winter), 6)
        findings = {item["finding_id"]: item for item in report["findings"]}
        self.assertEqual(findings["jogger-extreme-heated-seat-package-dependency"]["status"], "resolved")
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        entries = [item for item in registry["reports"] if item["report_id"] == REPORT_ID]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["json_path"], f"data/reporting/{REPORT_ID}.json")
        self.assertEqual(entries[0]["markdown_path"], f"data/reporting/{REPORT_ID}.md")


if __name__ == "__main__":
    unittest.main()
