from __future__ import annotations
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "data/reporting/catalogue_gap_002_exact_colour_capture_20260923_batch_014.json"
class CatalogueGap002ExactColourCapture014Tests(unittest.TestCase):
    def test_jogger_essential_7seat_exact_state(self) -> None:
        capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
        item = capture["observations"][0]
        self.assertEqual(capture["gap_id"], "CAT-GAP-002")
        self.assertEqual(capture["captured_on"], "2026-09-23")
        self.assertEqual(len(capture["observations"]), 1)
        self.assertEqual(item["configuration_code"], "jogger_essential_7seat_ecog120_manual")
        self.assertEqual(item["grade"], "essential")
        self.assertEqual(item["seat_count"], 7)
        self.assertEqual(item["powertrain"], "Eco-G 120")
        self.assertEqual(item["transmission"], "manual")
        self.assertEqual(item["drive_type"], "4x2")
        self.assertEqual(item["observed_total_price_pln"], 82400)
        self.assertEqual(item["visible_colour_count"], 3)
        self.assertEqual([c["name"] for c in item["colours"]], ["biel alpejska","szary schiste","czarna perła"])
        self.assertTrue(all(c["price_pln"] is None for c in item["colours"]))
        self.assertEqual(item["selected_colour"], "biel alpejska")
        self.assertFalse(capture["policy"]["cross_configuration_projection"])
        self.assertFalse(capture["policy"]["grade_level_projection"])
        self.assertFalse(capture["policy"]["absence_interpreted_as_unavailability"])
        self.assertFalse(capture["policy"]["master_data_mutated"])
if __name__ == "__main__":
    unittest.main()
