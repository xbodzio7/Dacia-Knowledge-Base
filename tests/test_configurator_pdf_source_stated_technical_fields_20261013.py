import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "project/sources/dacia-pl-configurator-native-pdf-page-ledger-20260809.json"
MASTER = ROOT / "data/master/configuration_attribute_values.csv"

class ConfiguratorPdfSourceStatedTechnicalFieldsTest(unittest.TestCase):
    def test_all_210_observations_are_already_exactly_covered(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        with MASTER.open(encoding="utf-8-sig", newline="") as handle:
            values = list(csv.DictReader(handle))
        contracts = [
            ("Rodzaj nadwozia", "body_style_source_stated", 5),
            ("Typ techniczny", "technical_type_code", 6),
            ("Rodzaj skrzyni biegów", "gearbox_source_description", 6),
        ]
        self.assertEqual(len(ledger["documents"]), 70)
        for label, attribute, page_number in contracts:
            with self.subTest(attribute=attribute):
                for doc in ledger["documents"]:
                    page = next(p for p in doc["pages_ledger"] if p["page"] == page_number and "technical" in p["sections"])
                    raw = next(line.strip() for line in page["text"].splitlines() if line.strip().startswith(label + " "))
                    expected_value = raw[len(label):].strip()
                    matches = [
                        row for row in values
                        if row["configuration_code"] == doc["configuration_code"]
                        and row["attribute_code"] == attribute
                        and row["observation_date"] == "2026-08-09"
                        and row["source_code"] == doc["source_code"]
                        and row["value"] == expected_value
                    ]
                    self.assertEqual(len(matches), 1, (doc["configuration_code"], attribute, raw))
                    self.assertIn(raw, matches[0]["notes"])

if __name__ == "__main__":
    unittest.main()
