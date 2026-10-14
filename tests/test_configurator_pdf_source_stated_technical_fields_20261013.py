import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "project/sources/dacia-pl-configurator-native-pdf-page-ledger-20260809.json"
MASTER = ROOT / "data/master/configuration_attribute_values.csv"
RECONCILIATION = ROOT / "data/reporting/configurator_pdf_standing_400m_reconciliation_20261014.json"
DEFERRAL_REPORT = ROOT / "data/reporting/configurator_pdf_source_stated_technical_field_deferral_reconciliation_20261013.json"
RESIDUAL_AUDIT = ROOT / "data/reporting/configurator_pdf_unhandled_technical_label_residual_audit_20261014.json"

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
                        and (row["value"].strip().replace(",", ".").rstrip("0").rstrip(".") if "." in row["value"].strip().replace(",", ".") else row["value"].strip()) == expected_value
                    ]
                    self.assertEqual(len(matches), 1, (doc["configuration_code"], attribute, raw))
                    self.assertIn(raw, matches[0]["notes"])

    def test_standing_400m_values_are_exact_and_non_numeric_markers_are_not_imported(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        with MASTER.open(encoding="utf-8-sig", newline="") as handle:
            values = list(csv.DictReader(handle))
        candidates = []
        non_numeric = []
        for doc in ledger["documents"]:
            for page in doc["pages_ledger"]:
                if "technical" not in page["sections"]:
                    continue
                for line in page["text"].splitlines():
                    raw = " ".join(line.split())
                    if not raw.startswith("400 m ze startu zatrzymanego (s) "):
                        continue
                    value = raw[len("400 m ze startu zatrzymanego (s) "):].strip().replace(",", ".")
                    if value.replace(".", "", 1).isdigit():
                        normalized = value.rstrip("0").rstrip(".") if "." in value else value
                        candidates.append((doc, raw, normalized))
                    else:
                        non_numeric.append((doc, raw, value))
        self.assertEqual(len(candidates), 40)
        self.assertEqual(len(non_numeric), 3)
        for doc, raw, expected_value in candidates:
            matches = [
                row for row in values
                if row["configuration_code"] == doc["configuration_code"]
                and row["attribute_code"] == "standing_400m"
                and row["observation_date"] == "2026-08-09"
                and row["source_code"] == doc["source_code"]
                and (row["value"].strip().replace(",", ".").rstrip("0").rstrip(".") if "." in row["value"].strip().replace(",", ".") else row["value"].strip()) == expected_value
            ]
            self.assertEqual(len(matches), 1, (doc["configuration_code"], raw))
            self.assertIn(raw, matches[0]["notes"])
        for doc, raw, marker in non_numeric:
            self.assertEqual(marker.casefold(), "nd")
            matches = [
                row for row in values
                if row["configuration_code"] == doc["configuration_code"]
                and row["attribute_code"] == "standing_400m"
                and row["observation_date"] == "2026-08-09"
                and row["source_code"] == doc["source_code"]
            ]
            self.assertEqual(matches, [], (doc["configuration_code"], raw))
        receipt = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
        audit = json.loads(RESIDUAL_AUDIT.read_text(encoding="utf-8"))
        deferrals = json.loads(DEFERRAL_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["counts"]["numeric_candidates"], 40)
        self.assertEqual(receipt["counts"]["exact_existing_source_observations"], 40)
        self.assertEqual(receipt["counts"]["new_master_rows"], 0)
        self.assertEqual(receipt["counts"]["non_numeric_markers"], 3)
        self.assertEqual(audit["counts"]["candidate_lines"], 43)
        self.assertEqual(audit["counts"]["remaining_deferred_after"], 130)
        self.assertEqual(audit["counts"]["unhandled_label_deferrals_after"], 0)
        self.assertEqual(deferrals["summary"]["remaining_deferred_observations"], 130)
        self.assertEqual(deferrals["remaining_deferred_by_reason"]["technical:unhandled_label"], 0)

    def test_layout_dependent_height_candidates_are_reconciled_without_ambiguous_scalar_projection(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        with MASTER.open(encoding="utf-8-sig", newline="") as handle:
            values = list(csv.DictReader(handle))
        candidates = []
        for doc in ledger["documents"]:
            for page in doc["pages_ledger"]:
                if "technical" not in page["sections"]:
                    continue
                for line in page["text"].splitlines():
                    raw = " ".join(line.split())
                    if raw.startswith("Wysokość całkowita ") and doc["configuration_code"].startswith(("duster_iii_", "bigster_", "jogger_")):
                        candidates.append((doc, raw))
        self.assertEqual(len(candidates), 52)
        by_family = {
            "duster": [x for x in candidates if x[0]["configuration_code"].startswith("duster_iii_")],
            "bigster": [x for x in candidates if x[0]["configuration_code"].startswith("bigster_")],
            "jogger": [x for x in candidates if x[0]["configuration_code"].startswith("jogger_")],
        }
        self.assertEqual({k: len(v) for k, v in by_family.items()}, {"duster": 16, "bigster": 14, "jogger": 22})
        for family, family_candidates in by_family.items():
            for doc, raw in family_candidates:
                config, source = doc["configuration_code"], doc["source_code"]
                literal = [row for row in values if row["configuration_code"] == config
                    and row["attribute_code"] == "overall_height_source_stated"
                    and row["observation_date"] == "2026-08-09" and row["source_code"] == source
                    and raw in row["notes"]]
                self.assertEqual(len(literal), 1, (config, raw))
                numeric = [row for row in values if row["configuration_code"] == config
                    and row["attribute_code"] == "overall_height"
                    and row["observation_date"] == "2026-08-09" and row["source_code"] == source]
                if family == "jogger":
                    expected = "1689" if "_5seat_" in config else "1684"
                    self.assertEqual(len(numeric), 1, (config, raw))
                    self.assertEqual(numeric[0]["value"], expected, (config, raw))
                    self.assertIn(raw, numeric[0]["notes"])
                else:
                    self.assertEqual(numeric, [], (config, raw))

    def test_roof_height_with_rails_context_is_not_projected_to_inapplicable_configurations(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        with MASTER.open(encoding="utf-8-sig", newline="") as handle:
            values = list(csv.DictReader(handle))
        candidates = []
        for doc in ledger["documents"]:
            for page in doc["pages_ledger"]:
                if "technical" not in page["sections"]:
                    continue
                for line in page["text"].splitlines():
                    raw = " ".join(line.split())
                    if not raw.startswith("Wysokość pojazdu nieobciążonego z relingami (mm) "):
                        continue
                    config = doc["configuration_code"]
                    if (config.startswith("sandero_iii_") and not config.startswith("sandero_stepway_")) or config.startswith("spring_"):
                        candidates.append((doc, raw))
        self.assertEqual(len(candidates), 10)
        base_sandero = [x for x in candidates if x[0]["configuration_code"].startswith("sandero_iii_")]
        spring = [x for x in candidates if x[0]["configuration_code"].startswith("spring_")]
        self.assertEqual(len(base_sandero), 7)
        self.assertEqual(len(spring), 3)
        for doc, raw in base_sandero:
            self.assertTrue(raw.endswith("1586 (Stepway)"), (doc["configuration_code"], raw))
        for doc, raw in spring:
            self.assertTrue(raw.endswith("b.d."), (doc["configuration_code"], raw))
        for doc, raw in candidates:
            numeric = [
                row for row in values
                if row["configuration_code"] == doc["configuration_code"]
                and row["attribute_code"] == "roof_height_with_rails"
                and row["observation_date"] == "2026-08-09"
                and row["source_code"] == doc["source_code"]
            ]
            self.assertEqual(numeric, [], (doc["configuration_code"], raw))

if __name__ == "__main__":
    unittest.main()
