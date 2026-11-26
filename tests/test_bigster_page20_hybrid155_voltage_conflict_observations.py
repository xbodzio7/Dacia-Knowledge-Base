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
SPEC = ROOT / "data/imports/configuration_values/bigster-page20-hybrid155-system-voltage-20251210.json"
PDF = ROOT / "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf"
BROCHURE_SOURCE = "src_pl_bigster_brochure_20251210"
PRICE_SOURCE = "src_pl_bigster_price_my26_20260703"
EXPECTED_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
TARGETS = {
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterPage20Hybrid155VoltageConflictObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_preserves_source_and_integer_voltage_contract(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3322)
        self.assertEqual(self.spec["attribute_code"], "hybrid_system_voltage")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "integer", "unit": "V", "status": "active"})
        self.assertEqual(self.spec["source_page"], 20)
        self.assertEqual(self.spec["source_section"], "BATERIA")

    def test_exact_three_hybrid155_targets_are_in_spec_once(self) -> None:
        configurations = [row["configuration_code"] for row in self.spec["rows"]]
        self.assertEqual(len(configurations), 3)
        self.assertEqual(set(configurations), TARGETS)
        self.assertEqual(len(configurations), len(set(configurations)))
        self.assertEqual({row["value"] for row in self.spec["rows"]}, {"280"})
        self.assertEqual({row["source_text"] for row in self.spec["rows"]}, {"280 V / 1,4 kWh"})

    def test_brochure_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [
                row for row in self.values
                if row["source_code"] == BROCHURE_SOURCE
                and row["attribute_code"] == "hybrid_system_voltage"
                and row["configuration_code"] in TARGETS
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], [3322, 3323, 3324])
        self.assertEqual({row["value"] for row in selected}, {"280"})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-10"})

    def test_later_price_source_200v_rows_remain_unchanged(self) -> None:
        later = sorted(
            [
                row for row in self.values
                if row["source_code"] == PRICE_SOURCE
                and row["attribute_code"] == "hybrid_system_voltage"
                and row["configuration_code"] in TARGETS
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in later], [1475, 1476, 1477])
        self.assertEqual({row["value"] for row in later}, {"200"})
        self.assertEqual({row["observation_date"] for row in later}, {"2026-07-03"})

    def test_both_registered_voltage_observations_coexist(self) -> None:
        selected = [
            row for row in self.values
            if row["attribute_code"] == "hybrid_system_voltage"
            and row["configuration_code"] in TARGETS
            and row["source_code"] in {BROCHURE_SOURCE, PRICE_SOURCE}
        ]
        self.assertEqual(len(selected), 6)
        by_configuration = {}
        for row in selected:
            by_configuration.setdefault(row["configuration_code"], set()).add((row["source_code"], row["value"]))
        expected = {(BROCHURE_SOURCE, "280"), (PRICE_SOURCE, "200")}
        self.assertEqual(set(by_configuration), TARGETS)
        self.assertTrue(all(values == expected for values in by_configuration.values()))

    def test_capacity_context_is_not_imported_by_this_package(self) -> None:
        selected = [
            row for row in self.values
            if row["source_code"] == BROCHURE_SOURCE
            and row["configuration_code"] in TARGETS
            and row["attribute_code"] in {"hybrid_battery_capacity", "hybrid_battery_capacity_source_stated"}
            and row["observation_date"] == "2025-12-10"
        ]
        self.assertEqual(selected, [])

    def test_all_targets_are_active_and_linked_to_source(self) -> None:
        active = {
            row["code"]
            for row in rows(MASTER / "configurations.csv")
            if row["status"] == "active"
        }
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == BROCHURE_SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(TARGETS <= active)
        self.assertTrue(TARGETS <= linked)

    def test_page_text_contains_exact_voltage_cell(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 20))
        self.assertIn(_compact_text("280 V / 1,4 kWh"), page_text)


if __name__ == "__main__":
    unittest.main()
