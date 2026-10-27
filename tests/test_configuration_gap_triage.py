from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))
import configuration_gap_triage as triage  # noqa: E402


class ConfigurationGapTriageTests(unittest.TestCase):
    def reports(self) -> tuple[dict, dict]:
        completeness = {
            "version": 1,
            "as_of": "2026-06-01",
            "technical": {
                "missing": 1,
                "not_applicable": 0,
            },
            "equipment": {
                "missing": 1,
                "not_applicable": 0,
                "standard": 3,
                "optional": 0,
                "not_available": 1,
                "unknown": 0,
            },
            "gaps": {
                "technical": [
                    {
                        "configuration_code": "cfg_b",
                        "source_code": "src_b",
                        "category": "Dimensions",
                        "attribute_code": "vehicle_height",
                        "fuel_type_code": "",
                        "state": "missing",
                    }
                ],
                "equipment": [
                    {
                        "configuration_code": "cfg_a",
                        "source_code": "src_a",
                        "category": "Comfort",
                        "attribute_code": "heated_seat",
                        "state": "missing",
                    }
                ],
            },
        }
        source = {
            "version": 1,
            "as_of": "2026-06-01",
            "records": {
                "technical": {
                    "missing": 1,
                    "source_missing": 0,
                },
                "equipment": {
                    "missing": 1,
                    "source_missing": 0,
                },
            },
            "sources": [
                {
                    "source_code": "src_a",
                    "registration_state": "registered",
                    "configuration_code": "cfg_a",
                    "document_date": "2026-06-01",
                    "file_path": "PDF/a.pdf",
                    "sha256": "a" * 64,
                },
                {
                    "source_code": "src_b",
                    "registration_state": "registered",
                    "configuration_code": "cfg_b",
                    "document_date": "2026-06-01",
                    "file_path": "PDF/b.pdf",
                    "sha256": "b" * 64,
                },
            ],
            "gaps": [
                {
                    "source_code": "src_b",
                    "configuration_code": "cfg_b",
                    "area": "technical",
                    "section": "Dimensions",
                    "attribute_code": "vehicle_height",
                    "fuel_type_code": "",
                    "state": "record_missing",
                },
                {
                    "source_code": "src_a",
                    "configuration_code": "cfg_a",
                    "area": "equipment",
                    "section": "Comfort",
                    "attribute_code": "heated_seat",
                    "fuel_type_code": "",
                    "state": "record_missing",
                },
            ],
        }
        return completeness, source

    def test_builds_neutral_queue_and_preserves_source_metadata(self) -> None:
        completeness, source = self.reports()
        report = triage.build_triage_report(completeness, source)

        self.assertEqual(report["summary"]["total_candidates"], 2)
        self.assertEqual(report["summary"]["technical_candidates"], 1)
        self.assertEqual(report["summary"]["equipment_candidates"], 1)
        self.assertEqual(report["summary"]["priority_assigned"], 0)
        self.assertEqual(report["summary"]["auto_import_enabled"], 0)
        self.assertEqual(
            report["ordering"]["strategy"],
            "lexicographic_non_priority",
        )
        self.assertTrue(
            all(item["priority"] == "unassigned" for item in report["queue"])
        )
        self.assertTrue(
            all(item["auto_import"] is False for item in report["queue"])
        )
        self.assertEqual(report["queue"][0]["domain"], "technical")
        self.assertEqual(report["queue"][0]["sha256"], "b" * 64)

    def test_groups_queue_by_source_configuration_category_and_section(
        self,
    ) -> None:
        completeness, source = self.reports()
        report = triage.build_triage_report(completeness, source)

        groups = report["groups"]
        self.assertEqual(len(groups["by_source"]), 2)
        self.assertEqual(len(groups["by_configuration"]), 2)
        self.assertEqual(len(groups["by_category"]), 2)
        self.assertEqual(len(groups["by_section"]), 2)
        self.assertEqual(
            sum(item["total"] for item in groups["by_source"]),
            2,
        )

    def test_input_order_does_not_change_output(self) -> None:
        completeness, source = self.reports()
        first = triage.build_triage_report(completeness, source)

        completeness["gaps"]["technical"].reverse()
        completeness["gaps"]["equipment"].reverse()
        source["gaps"].reverse()
        source["sources"].reverse()
        second = triage.build_triage_report(completeness, source)

        self.assertEqual(
            triage.render_json(first),
            triage.render_json(second),
        )

    def test_rejects_input_report_date_mismatch(self) -> None:
        completeness, source = self.reports()
        source["as_of"] = "2026-05-31"

        with self.assertRaisesRegex(
            triage.GapTriageError,
            "input report dates differ",
        ):
            triage.build_triage_report(completeness, source)

    def test_rejects_gap_set_mismatch(self) -> None:
        completeness, source = self.reports()
        source["gaps"].pop()

        with self.assertRaisesRegex(
            triage.GapTriageError,
            "input gap sets differ",
        ):
            triage.build_triage_report(completeness, source)

    def test_rejects_source_registration_gap(self) -> None:
        completeness, source = self.reports()
        source["records"]["technical"]["source_missing"] = 1

        with self.assertRaisesRegex(
            triage.GapTriageError,
            "source-registration gaps",
        ):
            triage.build_triage_report(completeness, source)

    def test_json_and_markdown_are_deterministic(self) -> None:
        completeness, source = self.reports()
        report = triage.build_triage_report(completeness, source)

        first = triage.render_json(report)
        second = triage.render_json(report)
        self.assertEqual(first, second)
        self.assertNotIn("generated_at", first)
        self.assertTrue(first.endswith("\n"))

        markdown = triage.render_markdown(report)
        self.assertIn("# Configuration Gap Triage", markdown)
        self.assertIn("not a business priority", markdown)
        self.assertIn("`source_verification_required`", markdown)
        self.assertIn("`vehicle_height`", markdown)
        self.assertIn("a" * 64, markdown)

    def test_parse_args_accepts_snapshot_and_outputs(self) -> None:
        arguments = triage.parse_args(
            [
                "--spec",
                "scope.json",
                "--as-of",
                "2026-06-01",
                "--json",
                "triage.json",
                "--markdown",
                "triage.md",
            ]
        )
        self.assertEqual(arguments.spec, Path("scope.json"))
        self.assertEqual(arguments.as_of, "2026-06-01")
        self.assertEqual(arguments.json_path, Path("triage.json"))
        self.assertEqual(arguments.markdown, Path("triage.md"))


if __name__ == "__main__":
    unittest.main()
