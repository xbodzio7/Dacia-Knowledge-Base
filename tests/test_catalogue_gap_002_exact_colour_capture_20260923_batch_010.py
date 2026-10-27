from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "data/reporting/catalogue_gap_002_exact_colour_capture_20260923_batch_010.json"


class CatalogueGap002ExactColourCapture010Tests(unittest.TestCase):
    def test_new_exact_surface_is_complete_and_nonprojected(self) -> None:
        capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
        observations = capture["observations"]
        self.assertEqual(capture["gap_id"], "CAT-GAP-002")
        self.assertEqual(capture["captured_on"], "2026-09-23")
        self.assertEqual(len(observations), 1)
        item = observations[0]
        self.assertEqual(item["configuration_code"], "jogger_journey_7seat_tce110_manual")
        self.assertEqual(item["visible_colour_count"], 7)
        self.assertEqual(item["visible_colour_count"], len(item["colours"]))
        self.assertTrue(item["selected_colour"])
        self.assertIn(item["selected_colour"], {c["name"] for c in item["colours"]})
        self.assertIn("?conf=", item["exact_state_url"])
        self.assertIsInstance(item["observed_total_price_pln"], int)
        self.assertTrue(all(c["price_pln"] is None for c in item["colours"]))
        self.assertFalse(capture["policy"]["cross_configuration_projection"])
        self.assertFalse(capture["policy"]["grade_level_projection"])
        self.assertFalse(capture["policy"]["absence_interpreted_as_unavailability"])
        self.assertFalse(capture["policy"]["master_data_mutated"])


if __name__ == "__main__":
    unittest.main()
