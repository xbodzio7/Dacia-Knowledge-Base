from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
REPORT = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"
SOURCE_CODE = "src_pl_sandero_stepway_full_modal_20260809"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoStepwayFullModalCanonicalReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.sources = rows("sources.csv")
        cls.source_configurations = rows("source_configurations.csv")
        cls.values = rows("configuration_attribute_values.csv")
        cls.availability = rows("configuration_attribute_availability.csv")

    def test_report_reconciles_every_captured_row(self) -> None:
        summary = self.report["summary"]
        self.assertEqual(summary["configuration_surfaces"], 15)
        self.assertEqual(summary["captured_rows"], 1708)
        self.assertEqual(summary["equipment_rows"], 1029)
        self.assertEqual(summary["technical_rows"], 679)
        self.assertEqual(
            summary["equipment_rows_safely_mapped"]
            + summary["equipment_rows_preserved_unmatched_or_ambiguous"],
            1029,
        )
        self.assertEqual(
            summary["technical_rows_safely_mapped"]
            + summary["technical_rows_already_canonically_covered"]
            + summary["technical_rows_preserved_unmatched_or_ambiguous"],
            679,
        )

    def test_source_and_all_exact_configuration_relationships_are_registered(self) -> None:
        source = [row for row in self.sources if row["code"] == SOURCE_CODE]
        self.assertEqual(len(source), 1)
        self.assertEqual(source[0]["document_date"], "2026-08-09")
        related = [
            row for row in self.source_configurations if row["source_code"] == SOURCE_CODE
        ]
        self.assertEqual(len(related), 15)
        self.assertEqual(len({row["configuration_code"] for row in related}), 15)
        self.assertTrue(all(row["relationship"] == "documents" for row in related))

    def test_canonical_observations_are_dated_and_source_bounded(self) -> None:
        equipment = [row for row in self.availability if row["source_code"] == SOURCE_CODE]
        technical = [row for row in self.values if row["source_code"] == SOURCE_CODE]
        self.assertEqual(len(equipment), 588)
        self.assertEqual(len(technical), 26)
        self.assertTrue(all(row["observation_date"] == "2026-08-09" for row in equipment))
        self.assertTrue(all(row["observation_date"] == "2026-08-09" for row in technical))
        self.assertEqual(len({row["code"] for row in equipment}), len(equipment))
        self.assertEqual(len({row["code"] for row in technical}), len(technical))

    def test_unmatched_evidence_remains_explicit(self) -> None:
        summary = self.report["summary"]
        self.assertEqual(summary["equipment_rows_preserved_unmatched_or_ambiguous"], 441)
        self.assertEqual(summary["technical_rows_preserved_unmatched_or_ambiguous"], 499)
        boundaries = self.report["boundaries"]
        self.assertIn(
            "Absence from a standard-equipment modal never implies not_available.",
            boundaries,
        )
        unresolved_equipment = {
            row["literal"] for row in self.report["unresolved_equipment_literals"]
        }
        unresolved_technical = {
            row["label"] for row in self.report["unresolved_technical_labels"]
        }
        self.assertIn("światła automatyczne, wycieraczki automatyczne", unresolved_equipment)
        self.assertIn("Moc maksymalna kW (KM)", unresolved_technical)


if __name__ == "__main__":
    unittest.main()
