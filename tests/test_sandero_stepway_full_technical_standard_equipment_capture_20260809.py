from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FULL_CAPTURE = ROOT / "project/sources/dacia-pl-sandero-stepway-full-technical-standard-equipment-20260809.json"
EXACT_STATES = ROOT / "project/sources/dacia-pl-sandero-stepway-exact-configurator-states-20260809.json"


class SanderoStepwayFullTechnicalStandardEquipmentCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.capture = json.loads(FULL_CAPTURE.read_text(encoding="utf-8"))
        cls.exact = json.loads(EXACT_STATES.read_text(encoding="utf-8"))

    def test_capture_covers_all_exact_current_states_once(self) -> None:
        expected = {
            item["configuration_code"]: item["exact_state_url"]
            for item in self.exact["configurations"]
        }
        observed = {
            item["configuration_code"]: item["observed_url"]
            for item in self.capture["configurations"]
        }
        self.assertEqual(len(observed), 15)
        self.assertEqual(observed, expected)

    def test_summary_matches_all_literal_modal_rows(self) -> None:
        equipment = sum(
            len(group["items"])
            for item in self.capture["configurations"]
            for group in item["equipment"]
        )
        technical = sum(
            len(group["items"])
            for item in self.capture["configurations"]
            for group in item["technical"]
        )
        self.assertEqual(
            self.capture["summary"],
            {
                "exact_configuration_surfaces": 15,
                "standard_equipment_rows": 1029,
                "technical_rows": 679,
            },
        )
        self.assertEqual((equipment, technical), (1029, 679))

    def test_every_configuration_has_full_grouped_content(self) -> None:
        for item in self.capture["configurations"]:
            with self.subTest(configuration=item["configuration_code"]):
                self.assertGreaterEqual(len(item["equipment"]), 7)
                self.assertGreaterEqual(len(item["technical"]), 14)
                self.assertGreaterEqual(sum(len(group["items"]) for group in item["equipment"]), 65)
                self.assertGreaterEqual(sum(len(group["items"]) for group in item["technical"]), 44)
                self.assertTrue(all(group["group"] for group in item["equipment"]))
                self.assertTrue(all(group["group"] for group in item["technical"]))
                self.assertTrue(all(group["items"] for group in item["equipment"]))
                self.assertTrue(all(group["items"] for group in item["technical"]))

    def test_technical_rows_preserve_labels_and_values(self) -> None:
        essential = next(
            item for item in self.capture["configurations"]
            if item["configuration_code"] == "sandero_iii_essential_tce100_manual"
        )
        rows = {
            row["label"]: row["value"]
            for group in essential["technical"]
            for row in group["items"]
        }
        self.assertEqual(rows["Moc maksymalna kW (KM)"], "74 (100)")
        self.assertEqual(rows["Maksymalny moment obrotowy w Nm"], "200 przy 2900-3500")
        self.assertEqual(rows["Przyspieszenie 0-100 km/h (s)"], "9,7")
        self.assertEqual(rows["Maksymalna masa przyczepy z hamulcem (kg)"], "980")

    def test_standard_equipment_is_not_reduced_to_highlights(self) -> None:
        essential = next(
            item for item in self.capture["configurations"]
            if item["configuration_code"] == "sandero_iii_essential_tce100_manual"
        )
        labels = {
            label for group in essential["equipment"] for label in group["items"]
        }
        self.assertIn("system multimedialny Media Control (radio DAB, 2 głośniki, Bluetooth, 1xUSB, aplikacja DMC)", labels)
        self.assertIn("aktywny system wspomagania nagłego hamowania z funkcją wykrywania pieszych, rowerzystów (AEBS07)", labels)
        self.assertIn("system monitorowania ciśnienia w oponach (pośredni)", labels)

    def test_capture_preserves_non_import_boundaries(self) -> None:
        self.assertEqual(self.capture["observed_on"], "2026-08-09")
        self.assertIn("No accessory, price, financing or optional-equipment row is included.", self.capture["normalization_boundaries"])
        self.assertIn("Capture does not itself authorize canonical master-data import.", self.capture["normalization_boundaries"])


if __name__ == "__main__":
    unittest.main()
