"""Verify Jogger page 19 fuel and LPG capacity source observations."""

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
MASTER = ROOT / "data/master"
IMPORT_DIR = ROOT / "data/imports/configuration_values"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE = "src_pl_jogger_brochure_20251217"
LATER_SOURCE = "src_pl_jogger_price_my26_20260401"
EXPECTED_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
SOURCE_ROW = 'Pojemność zbiornika paliwa (l) 50 50/40(3) 50 50/40(3) 50 50'
FOOTNOTE = '(3) Poj. całkowita / poj. użyteczna.'
ALL_CONFIGURATIONS = ['jogger_expression_5seat_tce110_manual',
 'jogger_extreme_5seat_tce110_manual',
 'jogger_journey_5seat_tce110_manual',
 'jogger_essential_5seat_ecog120_manual',
 'jogger_expression_5seat_ecog120_manual',
 'jogger_extreme_5seat_ecog120_manual',
 'jogger_extreme_5seat_ecog120_automatic',
 'jogger_journey_5seat_ecog120_automatic',
 'jogger_expression_5seat_hybrid155_automatic',
 'jogger_extreme_5seat_hybrid155_automatic',
 'jogger_journey_5seat_hybrid155_automatic',
 'jogger_expression_7seat_tce110_manual',
 'jogger_extreme_7seat_tce110_manual',
 'jogger_journey_7seat_tce110_manual',
 'jogger_essential_7seat_ecog120_manual',
 'jogger_expression_7seat_ecog120_manual',
 'jogger_extreme_7seat_ecog120_manual',
 'jogger_extreme_7seat_ecog120_automatic',
 'jogger_journey_7seat_ecog120_automatic',
 'jogger_expression_7seat_hybrid155_automatic',
 'jogger_extreme_7seat_hybrid155_automatic',
 'jogger_journey_7seat_hybrid155_automatic']
ECOG_CONFIGURATIONS = ['jogger_essential_5seat_ecog120_manual',
 'jogger_expression_5seat_ecog120_manual',
 'jogger_extreme_5seat_ecog120_manual',
 'jogger_extreme_5seat_ecog120_automatic',
 'jogger_journey_5seat_ecog120_automatic',
 'jogger_essential_7seat_ecog120_manual',
 'jogger_expression_7seat_ecog120_manual',
 'jogger_extreme_7seat_ecog120_manual',
 'jogger_extreme_7seat_ecog120_automatic',
 'jogger_journey_7seat_ecog120_automatic']
NON_ECOG_CONFIGURATIONS = ['jogger_expression_5seat_tce110_manual',
 'jogger_extreme_5seat_tce110_manual',
 'jogger_journey_5seat_tce110_manual',
 'jogger_expression_5seat_hybrid155_automatic',
 'jogger_extreme_5seat_hybrid155_automatic',
 'jogger_journey_5seat_hybrid155_automatic',
 'jogger_expression_7seat_tce110_manual',
 'jogger_extreme_7seat_tce110_manual',
 'jogger_journey_7seat_tce110_manual',
 'jogger_expression_7seat_hybrid155_automatic',
 'jogger_extreme_7seat_hybrid155_automatic',
 'jogger_journey_7seat_hybrid155_automatic']
SPEC_PATHS = [
    IMPORT_DIR / "jogger-brochure-fuel-tank-capacity-20251217.json",
    IMPORT_DIR / "jogger-brochure-lpg-vessel-total-capacity-20251217.json",
    IMPORT_DIR / "jogger-brochure-lpg-vessel-filling-capacity-20251217.json",
]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPage19FuelLpgCapacitySourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.specs = [json.loads(path.read_text(encoding="utf-8")) for path in SPEC_PATHS]
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_specs_are_strict_source_bounded_and_contiguous(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual([spec["id_start"] for spec in self.specs], [3384, 3406, 3416])
        self.assertEqual(
            [spec["attribute_code"] for spec in self.specs],
            ["fuel_tank_capacity", "lpg_vessel_capacity_total", "lpg_vessel_filling_capacity"],
        )
        self.assertEqual([len(spec["rows"]) for spec in self.specs], [22, 10, 10])
        self.assertTrue(all(spec["observation_date"] == "2025-12-17" for spec in self.specs))
        self.assertTrue(all(spec["source_page"] == 19 for spec in self.specs))
        self.assertTrue(all(spec["source_section"] == "Pojemność zbiornika paliwa (l)" for spec in self.specs))

    def test_fuel_tank_targets_preserve_petrol_context(self) -> None:
        spec = self.specs[0]
        actual = {row["configuration_code"]: row.get("fuel_type_code", "") for row in spec["rows"]}
        self.assertEqual(set(actual), set(ALL_CONFIGURATIONS))
        self.assertEqual({code for code, fuel in actual.items() if fuel == "petrol"}, set(ECOG_CONFIGURATIONS))
        self.assertEqual({code for code, fuel in actual.items() if fuel == ""}, set(NON_ECOG_CONFIGURATIONS))
        self.assertEqual({row["value"] for row in spec["rows"]}, {"50"})

    def test_lpg_total_and_filling_targets_are_separate(self) -> None:
        total, filling = self.specs[1], self.specs[2]
        self.assertEqual({row["configuration_code"] for row in total["rows"]}, set(ECOG_CONFIGURATIONS))
        self.assertEqual({row["configuration_code"] for row in filling["rows"]}, set(ECOG_CONFIGURATIONS))
        self.assertEqual({row.get("fuel_type_code", "") for row in total["rows"] + filling["rows"]}, {"lpg"})
        self.assertEqual({row["value"] for row in total["rows"]}, {"50"})
        self.assertEqual({row["value"] for row in filling["rows"]}, {"40"})

    def test_master_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [row for row in self.values if 3384 <= int(row["id"]) <= 3425],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3384, 3426)))
        self.assertEqual(
            Counter((row["attribute_code"], row["fuel_type_code"], row["value"]) for row in selected),
            Counter({
                ("fuel_tank_capacity", "petrol", "50"): 10,
                ("fuel_tank_capacity", "", "50"): 12,
                ("lpg_vessel_capacity_total", "lpg", "50"): 10,
                ("lpg_vessel_filling_capacity", "lpg", "40"): 10,
            }),
        )
        self.assertEqual({row["source_code"] for row in selected}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-17"})

    def test_later_official_observations_coexist_unchanged(self) -> None:
        selected = [
            row
            for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["configuration_code"] in ALL_CONFIGURATIONS
            and row["attribute_code"] in {
                "fuel_tank_capacity",
                "lpg_vessel_capacity_total",
                "lpg_vessel_filling_capacity",
            }
        ]
        self.assertEqual(len(selected), 42)
        self.assertEqual(
            Counter((row["attribute_code"], row["fuel_type_code"], row["value"]) for row in selected),
            Counter({
                ("fuel_tank_capacity", "petrol", "50"): 10,
                ("fuel_tank_capacity", "", "50"): 12,
                ("lpg_vessel_capacity_total", "lpg", "50"): 10,
                ("lpg_vessel_filling_capacity", "lpg", "40"): 10,
            }),
        )
        self.assertEqual({row["observation_date"] for row in selected}, {"2026-04-01"})

    def test_source_page_contains_row_and_capacity_footnote(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(_compact_text(text) for _, text in extract_page_candidates(PDF, 19))
        self.assertIn(_compact_text(SOURCE_ROW), page_text)
        self.assertIn(_compact_text(FOOTNOTE), page_text)

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
        active = {row["code"] for row in rows(MASTER / "configurations.csv") if row["status"] == "active"}
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(set(ALL_CONFIGURATIONS) <= active)
        self.assertTrue(set(ALL_CONFIGURATIONS) <= linked)

    def test_capacity_semantics_are_not_collapsed(self) -> None:
        selected = [row for row in self.values if 3384 <= int(row["id"]) <= 3425]
        self.assertEqual(
            {row["attribute_code"] for row in selected},
            {"fuel_tank_capacity", "lpg_vessel_capacity_total", "lpg_vessel_filling_capacity"},
        )
        self.assertFalse(any(row["attribute_code"] == "fuel_tank_capacity" and row["fuel_type_code"] == "lpg" for row in selected))


if __name__ == "__main__":
    unittest.main()
