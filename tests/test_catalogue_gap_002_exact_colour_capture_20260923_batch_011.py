from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "data/reporting/catalogue_gap_002_exact_colour_capture_20260923_batch_011.json"


class CatalogueGap002ExactColourCapture011Tests(unittest.TestCase):
    def test_exact_state_is_complete_and_nonprojected(self) -> None:
        capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
        observations = capture["observations"]
        self.assertEqual(capture["gap_id"], "CAT-GAP-002")
        self.assertEqual(capture["captured_on"], "2026-09-23")
        self.assertEqual(len(observations), 1)
        item = observations[0]
        self.assertEqual(item["configuration_code"], "duster_iii_essential_ecog120_manual")
        self.assertEqual(item["drive_type"], "4x2")
        self.assertEqual(item["visible_colour_count"], 3)
        self.assertEqual(item["visible_colour_count"], len(item["colours"]))
        self.assertEqual(
            [(c["name"], c["price_pln"]) for c in item["colours"]],
            [
                ("biel alpejska", 0),
                ("szary schiste", 2700),
                ("khaki lichen", 2700),
            ],
        )
        self.assertEqual(item["selected_colour"], "biel alpejska")
        self.assertEqual(item["observed_total_price_pln"], 82000)
        self.assertEqual(item["exact_state_url"], capture["source_url"])
        self.assertFalse(capture["policy"]["cross_configuration_projection"])
        self.assertFalse(capture["policy"]["grade_level_projection"])
        self.assertFalse(capture["policy"]["absence_interpreted_as_unavailability"])
        self.assertFalse(capture["policy"]["master_data_mutated"])


if __name__ == "__main__":
    unittest.main()
