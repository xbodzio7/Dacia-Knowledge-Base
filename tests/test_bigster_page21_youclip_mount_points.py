from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = ROOT / "data" / "imports" / "configuration_values" / "bigster-page21-youclip-mount-points-20251210.json"
PDF = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SOURCE = "src_pl_bigster_brochure_20251210"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage21YouClipMountPointsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        cls.spec_rows = cls.spec["rows"]
        cls.values = read_csv(MASTER / "configuration_attribute_values.csv")
        cls.attributes = read_csv(MASTER / "attributes.csv")
        cls.configurations = read_csv(MASTER / "configurations.csv")
        cls.source_configurations = read_csv(MASTER / "source_configurations.csv")
        cls.codes = {f"{row['configuration_code']}_youclip_mount_points_20251210" for row in cls.spec_rows}
        cls.imported = [row for row in cls.values if row["code"] in cls.codes]

    def test_source_receipt_and_attribute_contract(self) -> None:
        self.assertEqual(self.spec["kind"], "configuration_attribute_values")
        self.assertEqual(self.spec["package_id"], "bigster_page21_youclip_mount_points_import_20261105_001")
        self.assertEqual(self.spec["id_start"], 8217)
        self.assertEqual(self.spec["attribute_code"], "youclip_mount_points")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "integer", "unit": "", "status": "active"})
        self.assertEqual(self.spec["observation_date"], "2025-12-10")
        self.assertEqual(self.spec["source_page"], 21)
        self.assertEqual(self.spec["source_section"], "PROWADZENIE I URZĄDZENIA KONTROLNE")
        self.assertEqual(self.spec["source_sha256"], EXPECTED_SHA)
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        attribute = [row for row in self.attributes if row["code"] == "youclip_mount_points"]
        self.assertEqual(len(attribute), 1)
        self.assertEqual(attribute[0]["id"], "424")
        self.assertEqual(attribute[0]["category"], "Infotainment")
        self.assertEqual(attribute[0]["data_type"], "integer")
        self.assertEqual(attribute[0]["unit"], "")
        self.assertEqual(attribute[0]["status"], "active")

    def test_fourteen_scalar_observations_match_the_manifest(self) -> None:
        self.assertEqual(len(self.spec_rows), 14)
        self.assertEqual(len(self.imported), 14)
        ordered = sorted(self.imported, key=lambda row: int(row["id"]))
        self.assertEqual([int(row["id"]) for row in ordered], list(range(8217, 8231)))
        self.assertEqual(len({row["code"] for row in ordered}), 14)
        expected = []
        for index, row in enumerate(self.spec_rows):
            grade = row["configuration_code"].split("_")[1]
            value = "4" if grade == "essential" else "5"
            self.assertEqual(row["value"], value)
            notes = f"Source page 21, section PROWADZENIE I URZĄDZENIA KONTROLNE: {row['source_text']}."
            expected.append({
                "id": str(8217 + index),
                "code": f"{row['configuration_code']}_youclip_mount_points_20251210",
                "configuration_code": row["configuration_code"],
                "attribute_code": "youclip_mount_points",
                "fuel_type_code": "",
                "gear_number": "",
                "value": value,
                "observation_date": "2025-12-10",
                "source_code": SOURCE,
                "notes": notes,
            })
        self.assertEqual(ordered, expected)
        self.assertEqual(Counter(row["value"] for row in ordered), Counter({"4": 2, "5": 12}))

    def test_targets_are_active_linked_and_the_pdf_row_is_exact(self) -> None:
        target_codes = {row["configuration_code"] for row in self.spec_rows}
        active = {row["code"] for row in self.configurations if row["status"] == "active" and row["code"].startswith("bigster_")}
        linked = {
            row["configuration_code"]
            for row in self.source_configurations
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertEqual(len(target_codes), 14)
        self.assertTrue(target_codes <= active)
        self.assertTrue(target_codes <= linked)
        self.assertEqual(Counter(code.split("_")[1] for code in target_codes), Counter({"essential": 2, "expression": 4, "journey": 4, "extreme": 4}))
        scope_expectations = {
            "bigster_mildhybrid140_4x2_manual_completeness.json": True,
            "bigster_mildhybridg140_4x2_manual_completeness.json": True,
            "bigster_hybrid155_4x2_automatic_completeness.json": True,
            "bigster_hybridg150_4x4_automatic_completeness.json": True,
            "bigster_mildhybridg140_4x2_automatic_completeness.json": False,
            "bigster_tribrid150_4x4_automatic_completeness.json": False,
        }
        for filename, expected_in_scope in scope_expectations.items():
            scope = json.loads((ROOT / "data" / "reporting" / filename).read_text(encoding="utf-8"))
            scope_codes = {item["configuration_code"] for item in scope["configurations"]}
            technical_slots = {item["attribute_code"] for item in scope["technical_slots"]}
            self.assertEqual("youclip_mount_points" in technical_slots, expected_in_scope, filename)
            if expected_in_scope:
                self.assertTrue(scope_codes <= target_codes, filename)
            else:
                self.assertFalse(scope_codes & target_codes, filename)
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(value) for _, value in extract_page_candidates(PDF, 21))
        self.assertIn(_compact_text("Punkty mocowania YouClip 4 5 5 5"), page_text)


if __name__ == "__main__":
    unittest.main()
