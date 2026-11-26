from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "data/reporting/catalogue_gap_002_exact_colour_capture_20260923_batch_013.json"


class CatalogueGap002ExactColourCapture013Tests(unittest.TestCase):
    def test_two_jogger_expression_exact_states(self) -> None:
        capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
        self.assertEqual(capture["gap_id"], "CAT-GAP-002")
        self.assertEqual(capture["captured_on"], "2026-09-23")
        self.assertEqual(len(capture["observations"]), 2)

        expected = [
            ("jogger_expression_5seat_tce110_manual", "TCe 110", 84050),
            ("jogger_expression_5seat_ecog120_manual", "Eco-G 120", 82050),
        ]
        expected_colours = [
            "biel alpejska", "szary schiste", "sandstone", "zielony cedar",
            "szary urban", "czarna perła", "brązowy terracotta",
        ]

        for item, (code, powertrain, price) in zip(capture["observations"], expected):
            self.assertEqual(item["configuration_code"], code)
            self.assertEqual(item["grade"], "expression")
            self.assertEqual(item["seat_count"], 5)
            self.assertEqual(item["powertrain"], powertrain)
            self.assertEqual(item["transmission"], "manual")
            self.assertEqual(item["drive_type"], "4x2")
            self.assertEqual(item["observed_total_price_pln"], price)
            self.assertEqual(item["visible_colour_count"], 7)
            self.assertEqual([c["name"] for c in item["colours"]], expected_colours)
            self.assertTrue(all(c["price_pln"] is None for c in item["colours"]))
            self.assertEqual(item["selected_colour"], "biel alpejska")

        self.assertFalse(capture["policy"]["cross_configuration_projection"])
        self.assertFalse(capture["policy"]["grade_level_projection"])
        self.assertFalse(capture["policy"]["absence_interpreted_as_unavailability"])
        self.assertFalse(capture["policy"]["master_data_mutated"])


if __name__ == "__main__":
    unittest.main()
