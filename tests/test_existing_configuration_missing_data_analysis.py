from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import existing_configuration_missing_data_analysis as analysis

ROOT = Path(__file__).resolve().parents[1]


class ExistingConfigurationMissingDataAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = analysis.collect(ROOT)

    def test_report_has_stable_contract(self) -> None:
        self.assertEqual(self.payload["version"], 1)
        self.assertEqual(self.payload["as_of"], "2026-08-01")
        self.assertEqual(
            self.payload["kind"],
            "existing_configuration_missing_data_analysis",
        )
        summary = self.payload["summary"]
        self.assertGreater(summary["active_configuration_count"], 0)
        self.assertGreater(summary["completeness_scope_count"], 0)
        self.assertGreater(summary["scoped_configuration_count"], 0)

    def test_missing_slots_are_not_negative_and_candidates_are_ranked(self) -> None:
        for item in self.payload["configurations"]:
            self.assertGreaterEqual(item["missing_technical"], 0)
            self.assertGreaterEqual(item["missing_equipment"], 0)
            self.assertLessEqual(
                item["missing_technical"],
                item["expected_technical"],
            )
            self.assertLessEqual(
                item["missing_equipment"],
                item["expected_equipment"],
            )
        impacts = [
            item["weighted_impact"]
            for item in self.payload["ranked_candidates"]
        ]
        self.assertEqual(impacts, sorted(impacts, reverse=True))
        selected = self.payload["selected_next_package"]
        if impacts:
            self.assertEqual(selected, self.payload["ranked_candidates"][0])

    def test_not_applicable_slots_are_not_reported_missing(self) -> None:
        for item in self.payload["configurations"]:
            self.assertGreaterEqual(item["classified_not_applicable"], 0)
            technical = {
                (
                    slot["attribute_code"],
                    slot["fuel_type_code"],
                    slot["gear_number"],
                )
                for slot in item["missing_technical_slots"]
            }
            self.assertEqual(len(technical), item["missing_technical"])
            self.assertEqual(
                len(set(item["missing_equipment_attributes"])),
                item["missing_equipment"],
            )

    def test_rendering_and_checked_outputs_are_deterministic(self) -> None:
        self.assertEqual(
            analysis.render_markdown(self.payload),
            analysis.render_markdown(analysis.collect(ROOT)),
        )
        report = ROOT / "data/reporting/existing_configuration_missing_data_analysis.json"
        markdown = ROOT / "data/reporting/existing_configuration_missing_data_analysis.md"
        self.assertTrue(report.is_file())
        self.assertTrue(markdown.is_file())
        self.assertEqual(
            json.loads(report.read_text(encoding="utf-8")),
            self.payload,
        )


if __name__ == "__main__":
    unittest.main()
