from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "imports" / "configuration_values" / "bigster-page20-eco-mode-20251210.json"
MASTER = ROOT / "data" / "master"
PDF = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SOURCE = "src_pl_bigster_brochure_20251210"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20EcoModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.rows = cls.spec["rows"]
        cls.codes = {
            row["code"]: row
            for row in read_csv(MASTER / "configuration_attribute_values.csv")
            if row["attribute_code"] == "eco_mode" and row["source_code"] == SOURCE
        }
        cls.active_bigster = {
            row["code"]
            for row in read_csv(MASTER / "configurations.csv")
            if row["status"] == "active" and row["code"].startswith("bigster_")
        }

    def test_spec_preserves_the_verified_source_receipt(self) -> None:
        self.assertEqual(self.spec["kind"], "configuration_attribute_values")
        self.assertEqual(self.spec["id_start"], 3268)
        self.assertEqual(self.spec["attribute_code"], "eco_mode")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "boolean", "unit": "", "status": "active"})
        self.assertEqual((self.spec["source_page"], self.spec["source_section"]), (20, "ZUŻYCIE PALIWA I EMISJA CO2"))
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)

    def test_all_fourteen_current_bigster_configurations_are_imported_once(self) -> None:
        configurations = [row["configuration_code"] for row in self.rows]
        self.assertEqual(len(configurations), 14)
        self.assertEqual(set(configurations), self.active_bigster)
        self.assertEqual(len(configurations), len(set(configurations)))

    def test_master_rows_are_contiguous_and_match_the_spec(self) -> None:
        selected = sorted(self.codes.values(), key=lambda row: int(row["id"]))
        self.assertEqual([int(row["id"]) for row in selected], list(range(3268, 3282)))
        expected = {
            (row["configuration_code"], "eco_mode", "", "2025-12-10", SOURCE): "true"
            for row in self.rows
        }
        actual = {
            (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"], row["source_code"]): row["value"]
            for row in selected
        }
        self.assertEqual(actual, expected)

    def test_values_are_boolean_source_backed_and_do_not_replace_other_observations(self) -> None:
        selected = list(self.codes.values())
        self.assertEqual({row["value"] for row in selected}, {"true"})
        self.assertEqual({row["source_code"] for row in selected}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-10"})
        self.assertTrue(all("Tryb Eco Tak" in row["notes"] for row in selected))
        all_eco = [row for row in read_csv(MASTER / "configuration_attribute_values.csv") if row["attribute_code"] == "eco_mode"]
        self.assertEqual(len(all_eco), 14)

    def test_every_imported_configuration_has_the_registered_source_relationship(self) -> None:
        linked = {
            row["configuration_code"]
            for row in read_csv(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(self.active_bigster <= linked)
        scope_names = {
            "bigster_mildhybrid140_4x2_manual_completeness.json",
            "bigster_mildhybridg140_4x2_manual_completeness.json",
            "bigster_hybridg150_4x4_automatic_completeness.json",
            "bigster_hybrid155_4x2_automatic_completeness.json",
        }
        for name in scope_names:
            payload = json.loads((ROOT / "data/reporting" / name).read_text(encoding="utf-8"))
            slots = {(item["attribute_code"], item.get("fuel_type_code", "")) for item in payload["technical_slots"]}
            self.assertIn(("eco_mode", ""), slots, name)

    def test_source_page_contains_the_shared_eco_mode_value(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 20))
        self.assertIn(_compact_text("Tryb Eco Tak"), page_text)


if __name__ == "__main__":
    unittest.main()
