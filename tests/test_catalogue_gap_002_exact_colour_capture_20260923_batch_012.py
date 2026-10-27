from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "data/reporting/catalogue_gap_002_exact_colour_capture_20260923_batch_012.json"


class CatalogueGap002ExactColourCapture012Tests(unittest.TestCase):
    def test_duster_expression_ecog120_exact_state(self) -> None:
        capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
        item = capture["observations"][0]

        self.assertEqual(capture["gap_id"], "CAT-GAP-002")
        self.assertEqual(capture["captured_on"], "2026-09-23")
        self.assertEqual(len(capture["observations"]), 1)
        self.assertEqual(item["configuration_code"], "duster_iii_expression_ecog120_manual")
        self.assertEqual(item["grade"], "expression")
        self.assertEqual(item["powertrain"], "Eco-G 120")
        self.assertEqual(item["transmission"], "manual")
        self.assertEqual(item["drive_type"], "4x2")
        self.assertEqual(item["observed_total_price_pln"], 90000)
        self.assertEqual(item["visible_colour_count"], 7)
        self.assertEqual(
            [(c["name"], c["price_pln"]) for c in item["colours"]],
            [
                ("biel alpejska", 0),
                ("szary schiste", 2700),
                ("brązowy terracotta", 2900),
                ("khaki lichen", 2700),
                ("czarna perła", 2700),
                ("sandstone", 2700),
                ("zielony cedar", 2700),
            ],
        )
        self.assertEqual(item["selected_colour"], "biel alpejska")
        self.assertFalse(capture["policy"]["cross_configuration_projection"])
        self.assertFalse(capture["policy"]["grade_level_projection"])
        self.assertFalse(capture["policy"]["absence_interpreted_as_unavailability"])
        self.assertFalse(capture["policy"]["master_data_mutated"])


if __name__ == "__main__":
    unittest.main()
