from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SPEC = ROOT / "data/imports/configuration_values/bigster-page20-emission-standard-20251210.json"
PDF = ROOT / "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
BROCHURE_SOURCE = "src_pl_bigster_brochure_20251210"
PRICE_SOURCE = "src_pl_bigster_price_my26_20260703"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20EmissionStandardConflictObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.active_bigster = {
            row["code"]
            for row in rows(MASTER / "configurations.csv")
            if row["status"] == "active" and row["code"].startswith("bigster_")
        }

    def test_spec_preserves_source_and_enum_contract(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3308)
        self.assertEqual(self.spec["attribute_code"], "emission_standard")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "enum", "unit": "", "status": "active"})
        self.assertEqual(self.spec["source_page"], 20)
        self.assertEqual(self.spec["source_section"], "SILNIKI")
        domain = {row["code"] for row in rows(MASTER / "enums/emission_standards.csv") if row["status"] == "active"}
        self.assertIn("euro_6e_bis", domain)

    def test_all_fourteen_active_bigster_configurations_are_in_spec_once(self) -> None:
        configurations = [row["configuration_code"] for row in self.spec["rows"]]
        self.assertEqual(len(configurations), 14)
        self.assertEqual(set(configurations), self.active_bigster)
        self.assertEqual(len(configurations), len(set(configurations)))
        self.assertEqual({row["value"] for row in self.spec["rows"]}, {"euro_6e_bis"})
        self.assertEqual({row["source_text"] for row in self.spec["rows"]}, {"Euro 6e-bis"})

    def test_brochure_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [
                row for row in self.values
                if row["source_code"] == BROCHURE_SOURCE
                and row["attribute_code"] == "emission_standard"
                and row["configuration_code"] in self.active_bigster
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3308, 3322)))
        self.assertEqual({row["value"] for row in selected}, {"euro_6e_bis"})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-10"})

    def test_later_price_source_euro_6_rows_remain_unchanged(self) -> None:
        later = sorted(
            [
                row for row in self.values
                if row["source_code"] == PRICE_SOURCE
                and row["attribute_code"] == "emission_standard"
                and row["configuration_code"] in self.active_bigster
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in later], list(range(1296, 1310)))
        self.assertEqual({row["value"] for row in later}, {"euro_6"})
        self.assertEqual({row["observation_date"] for row in later}, {"2026-07-03"})

    def test_both_registered_source_observations_coexist(self) -> None:
        selected = [
            row for row in self.values
            if row["attribute_code"] == "emission_standard"
            and row["configuration_code"] in self.active_bigster
            and row["source_code"] in {BROCHURE_SOURCE, PRICE_SOURCE}
        ]
        self.assertEqual(len(selected), 28)
        keys = {
            (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"], row["source_code"])
            for row in selected
        }
        self.assertEqual(len(keys), 28)
        by_configuration = {}
        for row in selected:
            by_configuration.setdefault(row["configuration_code"], set()).add((row["source_code"], row["value"]))
        expected = {(BROCHURE_SOURCE, "euro_6e_bis"), (PRICE_SOURCE, "euro_6")}
        self.assertEqual(set(by_configuration), self.active_bigster)
        self.assertTrue(all(values == expected for values in by_configuration.values()))

    def test_all_targets_have_registered_source_relationship(self) -> None:
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == BROCHURE_SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(self.active_bigster <= linked)

    def test_page_text_contains_exact_emission_standard(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 20))
        self.assertIn(_compact_text("Euro 6e-bis"), page_text)


if __name__ == "__main__":
    unittest.main()
