"""Verify the exact non-Hybrid subset of Jogger page 19 braked-trailer observations."""

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
SPEC = ROOT / "data/imports/configuration_values/jogger-brochure-braked-trailer-weight-non-hybrid-20251217.json"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE = 'src_pl_jogger_brochure_20251217'
LATER_SOURCE = 'src_pl_jogger_price_my26_20260401'
SOURCE_LABEL = 'Maks. masa całkowita przyczepy'
FIVE_ROW = 'Wersja 5-miejscowa 1200 1200 1200 1200'
SEVEN_ROW = 'Wersja 7-miejscowa 1200 1200 1200 1200'
EXPECTED_SHA = 'eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6'
EXPECTED = {'jogger_expression_5seat_tce110_manual': '1200',
 'jogger_extreme_5seat_tce110_manual': '1200',
 'jogger_journey_5seat_tce110_manual': '1200',
 'jogger_essential_5seat_ecog120_manual': '1200',
 'jogger_expression_5seat_ecog120_manual': '1200',
 'jogger_extreme_5seat_ecog120_manual': '1200',
 'jogger_extreme_5seat_ecog120_automatic': '1200',
 'jogger_journey_5seat_ecog120_automatic': '1200',
 'jogger_expression_7seat_tce110_manual': '1200',
 'jogger_extreme_7seat_tce110_manual': '1200',
 'jogger_journey_7seat_tce110_manual': '1200',
 'jogger_essential_7seat_ecog120_manual': '1200',
 'jogger_expression_7seat_ecog120_manual': '1200',
 'jogger_extreme_7seat_ecog120_manual': '1200',
 'jogger_extreme_7seat_ecog120_automatic': '1200',
 'jogger_journey_7seat_ecog120_automatic': '1200'}
HYBRID = {'jogger_expression_5seat_hybrid155_automatic',
 'jogger_expression_7seat_hybrid155_automatic',
 'jogger_extreme_5seat_hybrid155_automatic',
 'jogger_extreme_7seat_hybrid155_automatic',
 'jogger_journey_5seat_hybrid155_automatic',
 'jogger_journey_7seat_hybrid155_automatic'}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPage19BrakedTrailerWeightNonHybridSourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_is_strict_and_source_bounded(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3448)
        self.assertEqual(self.spec["attribute_code"], "braked_trailer_weight")
        self.assertEqual(self.spec["attribute_contract"], {"data_type": "integer", "unit": "kg", "status": "active"})
        self.assertEqual(self.spec["observation_date"], "2025-12-17")
        self.assertEqual(self.spec["source_page"], 19)
        self.assertEqual(self.spec["source_section"], SOURCE_LABEL)

    def test_exact_sixteen_non_hybrid_targets_are_in_spec_once(self) -> None:
        actual = {row["configuration_code"]: row["value"] for row in self.spec["rows"]}
        self.assertEqual(len(self.spec["rows"]), 16)
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(set(actual) & HYBRID, set())
        self.assertEqual({row["source_code"] for row in self.spec["rows"]}, {SOURCE})
        self.assertFalse(any(row.get("fuel_type_code") for row in self.spec["rows"]))

    def test_master_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [row for row in self.values if 3448 <= int(row["id"]) <= 3463],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3448, 3464)))
        self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
        self.assertEqual({row["attribute_code"] for row in selected}, {"braked_trailer_weight"})
        self.assertEqual({row["source_code"] for row in selected}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-17"})

    def test_later_non_hybrid_observations_coexist_unchanged(self) -> None:
        selected = [
            row for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["attribute_code"] == "braked_trailer_weight"
            and row["configuration_code"] in EXPECTED
        ]
        self.assertEqual(len(selected), 16)
        self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
        self.assertEqual({row["observation_date"] for row in selected}, {"2026-04-01"})

    def test_hybrid_conflict_remains_excluded_and_later_value_is_1000(self) -> None:
        later = [
            row for row in self.values
            if row["source_code"] == LATER_SOURCE
            and row["attribute_code"] == "braked_trailer_weight"
            and row["configuration_code"] in HYBRID
        ]
        brochure = [
            row for row in self.values
            if row["source_code"] == SOURCE
            and row["attribute_code"] == "braked_trailer_weight"
            and row["configuration_code"] in HYBRID
        ]
        self.assertEqual({row["configuration_code"] for row in later}, HYBRID)
        self.assertEqual({row["value"] for row in later}, {"1000"})
        self.assertEqual(brochure, [])

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
        active = {row["code"] for row in rows(MASTER / "configurations.csv") if row["status"] == "active"}
        linked = {
            row["configuration_code"] for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(set(EXPECTED) <= active)
        self.assertTrue(set(EXPECTED) <= linked)

    def test_page_text_contains_exact_label_and_rows(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        candidates = [_compact_text(text) for _, text in extract_page_candidates(PDF, 19)]
        page_text = " ".join(candidates)
        self.assertIn(_compact_text(SOURCE_LABEL), page_text)
        self.assertIn(_compact_text(FIVE_ROW), page_text)
        self.assertIn(_compact_text(SEVEN_ROW), page_text)


if __name__ == "__main__":
    unittest.main()
