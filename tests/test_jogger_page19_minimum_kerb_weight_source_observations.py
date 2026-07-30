"""Verify Jogger page 19 minimum-kerb-weight source observations."""

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
SPEC = ROOT / "data/imports/configuration_values/jogger-brochure-minimum-kerb-weight-20251217.json"
PDF = ROOT / "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
BROCHURE_SOURCE = "src_pl_jogger_brochure_20251217"
PRICE_SOURCE = "src_pl_jogger_price_my26_20260401"
EXPECTED_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
EXPECTED = {'jogger_expression_5seat_tce110_manual': '1193',
 'jogger_extreme_5seat_tce110_manual': '1193',
 'jogger_journey_5seat_tce110_manual': '1193',
 'jogger_essential_5seat_ecog120_manual': '1292',
 'jogger_expression_5seat_ecog120_manual': '1292',
 'jogger_extreme_5seat_ecog120_manual': '1292',
 'jogger_extreme_5seat_ecog120_automatic': '1326',
 'jogger_journey_5seat_ecog120_automatic': '1326',
 'jogger_expression_5seat_hybrid155_automatic': '1359',
 'jogger_extreme_5seat_hybrid155_automatic': '1359',
 'jogger_journey_5seat_hybrid155_automatic': '1359',
 'jogger_expression_7seat_tce110_manual': '1221',
 'jogger_extreme_7seat_tce110_manual': '1221',
 'jogger_journey_7seat_tce110_manual': '1221',
 'jogger_essential_7seat_ecog120_manual': '1321',
 'jogger_expression_7seat_ecog120_manual': '1321',
 'jogger_extreme_7seat_ecog120_manual': '1321',
 'jogger_extreme_7seat_ecog120_automatic': '1354',
 'jogger_journey_7seat_ecog120_automatic': '1354',
 'jogger_expression_7seat_hybrid155_automatic': '1388',
 'jogger_extreme_7seat_hybrid155_automatic': '1388',
 'jogger_journey_7seat_hybrid155_automatic': '1388'}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPage19MinimumKerbWeightSourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.values = rows(MASTER / "configuration_attribute_values.csv")

    def test_spec_is_strict_and_source_bounded(self) -> None:
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        self.assertEqual(self.spec["id_start"], 3362)
        self.assertEqual(self.spec["attribute_code"], "minimum_kerb_weight")
        self.assertEqual(
            self.spec["attribute_contract"],
            {"data_type": "integer", "unit": "kg", "status": "active"},
        )
        self.assertEqual(self.spec["observation_date"], "2025-12-17")
        self.assertEqual(self.spec["source_page"], 19)
        self.assertEqual(self.spec["source_section"], "Minimalna masa własna")

    def test_exact_twenty_two_targets_are_in_spec_once(self) -> None:
        actual = {row["configuration_code"]: row["value"] for row in self.spec["rows"]}
        self.assertEqual(len(self.spec["rows"]), 22)
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(len(actual), len(self.spec["rows"]))
        self.assertEqual({row["source_code"] for row in self.spec["rows"]}, {BROCHURE_SOURCE})
        self.assertFalse(any(row.get("fuel_type_code") for row in self.spec["rows"]))

    def test_brochure_rows_are_contiguous_and_exact(self) -> None:
        selected = sorted(
            [
                row
                for row in self.values
                if row["source_code"] == BROCHURE_SOURCE
                and row["attribute_code"] == "minimum_kerb_weight"
                and row["configuration_code"] in EXPECTED
            ],
            key=lambda row: int(row["id"]),
        )
        self.assertEqual([int(row["id"]) for row in selected], list(range(3362, 3384)))
        self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
        self.assertEqual({row["observation_date"] for row in selected}, {"2025-12-17"})

    def test_later_official_source_observations_coexist_unchanged(self) -> None:
        selected = [
            row
            for row in self.values
            if row["source_code"] == PRICE_SOURCE
            and row["attribute_code"] == "minimum_kerb_weight"
            and row["configuration_code"] in EXPECTED
        ]
        self.assertEqual(len(selected), 22)
        self.assertEqual({row["configuration_code"]: row["value"] for row in selected}, EXPECTED)
        self.assertEqual({row["observation_date"] for row in selected}, {"2026-04-01"})

    def test_targets_are_active_and_linked_to_brochure(self) -> None:
        active = {
            row["code"]
            for row in rows(MASTER / "configurations.csv")
            if row["status"] == "active"
        }
        linked = {
            row["configuration_code"]
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == BROCHURE_SOURCE
            and row["relationship"] == "brochure_technical_data_for"
        }
        self.assertTrue(set(EXPECTED) <= active)
        self.assertTrue(set(EXPECTED) <= linked)

    def test_page_text_contains_exact_label_and_rows(self) -> None:
        if shutil.which("pdftotext") is None:
            self.skipTest("pdftotext unavailable")
        page_text = " ".join(
            _compact_text(text)
            for _, text in extract_page_candidates(PDF, 19)
        )
        self.assertIn(_compact_text("Minimalna masa własna"), page_text)
        self.assertIn(
            _compact_text("Wersja 5-miejscowa 1193 1292 1326 1359"),
            page_text,
        )
        self.assertIn(
            _compact_text("Wersja 7-miejscowa 1221 1321 1354 1388"),
            page_text,
        )

    def test_mislabeled_mass_blocks_are_not_part_of_this_import(self) -> None:
        selected = [row for row in self.values if 3362 <= int(row["id"]) <= 3383]
        self.assertEqual({row["attribute_code"] for row in selected}, {"minimum_kerb_weight"})
        encoded = json.dumps(self.spec, ensure_ascii=False)
        self.assertNotIn("maximum_kerb_weight", encoded)
        self.assertNotIn("gross_train_weight", encoded)
        self.assertNotIn("gross_vehicle_weight", encoded)


if __name__ == "__main__":
    unittest.main()
