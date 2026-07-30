"""Verify Jogger page 19 DMC evidence, coexistence and adjacent conflict boundaries."""

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
SPEC = ROOT / "data/imports/configuration_values/jogger-brochure-gross-vehicle-weight-20251217.json"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE = 'src_pl_jogger_brochure_20251217'
LATER_SOURCE = 'src_pl_jogger_price_my26_20260401'
SOURCE_LABEL = 'Dopuszczalna masa całkowita (DMC)'
FIVE_ROW = 'Wersja 5-miejscowa 1685 1765 1785 1830'
SEVEN_ROW = 'Wersja 7-miejscowa 1855 1940 1960 2000'
EXPECTED_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
EXPECTED = {'jogger_expression_5seat_tce110_manual': '1685',
 'jogger_extreme_5seat_tce110_manual': '1685',
 'jogger_journey_5seat_tce110_manual': '1685',
 'jogger_essential_5seat_ecog120_manual': '1765',
 'jogger_expression_5seat_ecog120_manual': '1765',
 'jogger_extreme_5seat_ecog120_manual': '1765',
 'jogger_extreme_5seat_ecog120_automatic': '1785',
 'jogger_journey_5seat_ecog120_automatic': '1785',
 'jogger_expression_5seat_hybrid155_automatic': '1830',
 'jogger_extreme_5seat_hybrid155_automatic': '1830',
 'jogger_journey_5seat_hybrid155_automatic': '1830',
 'jogger_expression_7seat_tce110_manual': '1855',
 'jogger_extreme_7seat_tce110_manual': '1855',
 'jogger_journey_7seat_tce110_manual': '1855',
 'jogger_essential_7seat_ecog120_manual': '1940',
 'jogger_expression_7seat_ecog120_manual': '1940',
 'jogger_extreme_7seat_ecog120_manual': '1940',
 'jogger_extreme_7seat_ecog120_automatic': '1960',
 'jogger_journey_7seat_ecog120_automatic': '1960',
 'jogger_expression_7seat_hybrid155_automatic': '2000',
 'jogger_extreme_7seat_hybrid155_automatic': '2000',
 'jogger_journey_7seat_hybrid155_automatic': '2000'}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPage19GrossVehicleWeightSourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_is_strict_and_source_bounded(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3426)
        self.assertEqual(self.spec["attribute_code"], "gross_vehicle_weight")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "integer", "unit": "kg", "status": "active"})
        self.assertEqual(self.spec["observation_date"], "2025-12-17")
        self.assertEqual(self.spec["source_page"], 19)
        self.assertEqual(self.spec["source_section"], SOURCE_LABEL)

    def test_exact_twenty_two_targets_are_in_spec_once(self) -> None:
        actual = {row["configuration_code"]: row["value"] for row in self.spec["rows"]}
        self.assertEqual(len(self.spec["rows"]), 22)
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(len(actual), len(self.spec["rows"]))
        self.assertFalse(any(row.get("fuel_type_code") for row in self.spec["rows"]))

    def test_master_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted([row for row in self.values if 3426 <= int(row["id"]) <= 3447], key=lambda row: int(row["id"]))
        self.assertEqual([int(row["id"]) for row in selected], list(range(3426, 3448)))
        self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
        self.assertEqual({row["attribute_code"] for row in selected}, {"gross_vehicle_weight"})
        self.assertEqual({row["source_code"] for row in selected}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-17"})

    def test_later_official_observations_coexist_unchanged(self) -> None:
        selected = [
            row for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["attribute_code"] == "gross_vehicle_weight"
            and row["configuration_code"] in EXPECTED
        ]
        self.assertEqual(len(selected), 22)
        self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
        self.assertEqual({row["observation_date"] for row in selected}, {"2026-04-01"})

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
        active = {row["code"] for row in rows(MASTER / "configurations.csv") if row["status"] == "active"}
        linked = {
            row["configuration_code"] for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(set(EXPECTED) <= active)
        self.assertTrue(set(EXPECTED) <= linked)

    def test_page_text_contains_exact_label_and_target_rows(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        candidates = [_compact_text(text) for _, text in extract_page_candidates(PDF, 19)]
        page_text = " ".join(candidates)
        self.assertGreaterEqual(page_text.count(_compact_text(SOURCE_LABEL)), 3)
        self.assertIn(_compact_text(FIVE_ROW), page_text)
        self.assertIn(_compact_text(SEVEN_ROW), page_text)

    def test_adjacent_mislabeled_mass_blocks_are_not_imported(self) -> None:
        selected = [row for row in self.values if 3426 <= int(row["id"]) <= 3447]
        self.assertEqual(Counter(row["attribute_code"] for row in selected), Counter({"gross_vehicle_weight": 22}))
        encoded = json.dumps(self.spec, ensure_ascii=False)
        self.assertNotIn("maximum_kerb_weight", encoded)
        self.assertNotIn("gross_train_weight", encoded)


if __name__ == "__main__":
    unittest.main()
