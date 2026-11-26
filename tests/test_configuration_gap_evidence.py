from __future__ import annotations

import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))
import configuration_gap_evidence as evidence  # noqa: E402


class ConfigurationGapEvidenceTests(unittest.TestCase):
    def write_csv(
        self,
        path: Path,
        fieldnames: list[str],
        rows: list[dict[str, str]],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)

    def fixture(
        self,
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, dict, dict]:
        temporary = tempfile.TemporaryDirectory()
        repository = Path(temporary.name)

        self.write_csv(
            repository
            / "data"
            / "master"
            / "configuration_attribute_availability.csv",
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "availability_status",
                "observation_date",
                "source_code",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "manual-ac",
                    "configuration_code": "cfg_manual",
                    "attribute_code": "manual_air_conditioning",
                    "availability_status": "standard",
                    "observation_date": "2026-06-01",
                    "source_code": "src_manual",
                    "notes": "Source page 4: klimatyzacja manualna",
                }
            ],
        )
        self.write_csv(
            repository / "data" / "master" / "configurations.csv",
            [
                "id",
                "code",
                "version_code",
                "powertrain_label",
                "transmission_type",
                "status",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "cfg_manual",
                    "version_code": "version_manual",
                    "powertrain_label": "Eco-G",
                    "transmission_type": "manual",
                    "status": "active",
                    "notes": "",
                },
                {
                    "id": "2",
                    "code": "cfg_auto",
                    "version_code": "version_auto",
                    "powertrain_label": "Eco-G",
                    "transmission_type": "automatic",
                    "status": "active",
                    "notes": "",
                },
            ],
        )
        self.write_csv(
            repository / "data" / "master" / "attributes.csv",
            [
                "id",
                "code",
                "category",
                "name",
                "data_type",
                "unit",
                "description",
                "status",
            ],
            [
                {
                    "id": "1",
                    "code": "gear_shift_indicator",
                    "category": "Driving Systems",
                    "name": "Gear shift indicator",
                    "data_type": "boolean",
                    "unit": "",
                    "description": (
                        "Driver display provides "
                        "gear-change recommendations"
                    ),
                    "status": "active",
                },
                {
                    "id": "2",
                    "code": "manual_air_conditioning",
                    "category": "HVAC",
                    "name": "Manual air conditioning",
                    "data_type": "boolean",
                    "unit": "",
                    "description": "Manual climate control system",
                    "status": "active",
                },
            ],
        )

        def queue_item(
            sequence: int,
            triage_key: str,
            source_code: str,
            configuration_code: str,
            category: str,
            attribute_code: str,
        ) -> dict:
            return {
                "sequence": sequence,
                "triage_key": triage_key,
                "domain": "equipment",
                "source_code": source_code,
                "configuration_code": configuration_code,
                "category": category,
                "section": category,
                "attribute_code": attribute_code,
                "fuel_type_code": "",
                "document_date": "2026-06-01",
                "file_path": f"PDF/{source_code}.pdf",
                "sha256": (
                    "a" * 64
                    if source_code == "src_manual"
                    else "b" * 64
                ),
            }

        triage_report = {
            "version": 1,
            "as_of": "2026-06-01",
            "queue": [
                queue_item(
                    1,
                    "manual-auto-climate",
                    "src_manual",
                    "cfg_manual",
                    "HVAC",
                    "automatic_climate_control",
                ),
                queue_item(
                    2,
                    "auto-gear-shift",
                    "src_auto",
                    "cfg_auto",
                    "Driving Systems",
                    "gear_shift_indicator",
                ),
                queue_item(
                    3,
                    "manual-unknown",
                    "src_manual",
                    "cfg_manual",
                    "Driving Systems",
                    "blind_spot_monitoring",
                ),
            ],
        }

        def common(
            row: dict,
            classification: str,
        ) -> dict:
            return {
                "triage_key": row["triage_key"],
                "domain": row["domain"],
                "source_code": row["source_code"],
                "configuration_code": row["configuration_code"],
                "category": row["category"],
                "attribute_code": row["attribute_code"],
                "fuel_type_code": "",
                "document_date": row["document_date"],
                "file_path": row["file_path"],
                "sha256": row["sha256"],
                "classification": classification,
                "candidate_value": "",
                "auto_import": False,
            }

        availability = common(
            triage_report["queue"][0],
            "out_of_scope",
        )
        availability.update(
            {
                "manual_source_review_required": False,
                "reason_code": "explicit_alternative_state",
                "review_note": "Manual climate control is explicit.",
                "basis": {
                    "type": "availability_record",
                    "attribute_code": "manual_air_conditioning",
                    "availability_status": "standard",
                    "observation_date": "2026-06-01",
                    "source_code": "src_manual",
                    "source_page": 4,
                    "source_section": "",
                    "source_text": "klimatyzacja manualna",
                },
            }
        )

        configuration = common(
            triage_report["queue"][1],
            "out_of_scope",
        )
        configuration.update(
            {
                "manual_source_review_required": False,
                "reason_code": "automatic_transmission_scope",
                "review_note": "Gear-change recommendations are manual.",
                "basis": {
                    "type": "configuration_field",
                    "field": "transmission_type",
                    "value": "automatic",
                    "attribute_description": (
                        "Driver display provides "
                        "gear-change recommendations"
                    ),
                },
            }
        )

        ambiguous = common(
            triage_report["queue"][2],
            "ambiguous",
        )
        ambiguous.update(
            {
                "manual_source_review_required": True,
                "reason_code": (
                    "direct_source_statement_not_yet_retained"
                ),
                "review_note": "Manual PDF page review is required.",
                "source_page": None,
                "source_section": "",
                "source_text": "",
                "basis": None,
            }
        )

        evidence_spec = {
            "version": 1,
            "as_of": "2026-06-01",
            "review_scope": "structured_evidence_only",
            "review_policy": {
                "allowed_classifications": sorted(
                    evidence.CLASSIFICATIONS
                ),
                "auto_import": False,
            },
            "decisions": [
                availability,
                configuration,
                ambiguous,
            ],
        }
        return (
            temporary,
            repository,
            triage_report,
            evidence_spec,
        )

    def test_builds_conservative_evidence_report(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)

        report = evidence.build_evidence_report(
            repository,
            triage,
            spec,
        )

        self.assertEqual(report["summary"]["total_decisions"], 3)
        self.assertEqual(report["summary"]["found"], 0)
        self.assertEqual(report["summary"]["not_stated"], 0)
        self.assertEqual(report["summary"]["ambiguous"], 1)
        self.assertEqual(report["summary"]["out_of_scope"], 2)
        self.assertEqual(
            report["summary"]["manual_source_review_required"],
            1,
        )
        self.assertEqual(report["summary"]["candidate_imports"], 0)
        self.assertFalse(report["pdf_page_review_complete"])

    def test_validates_availability_basis_source_text(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec["decisions"][0]["basis"]["source_text"] = "wrong"

        with self.assertRaisesRegex(
            evidence.GapEvidenceError,
            "source_text differs",
        ):
            evidence.build_evidence_report(
                repository,
                triage,
                spec,
            )

    def test_validates_automatic_transmission_scope_basis(
        self,
    ) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        configurations = (
            repository / "data" / "master" / "configurations.csv"
        )
        text = configurations.read_text(encoding="utf-8")
        configurations.write_text(
            text.replace("cfg_auto,version_auto,Eco-G,automatic", "cfg_auto,version_auto,Eco-G,manual"),
            encoding="utf-8",
            newline="\n",
        )

        with self.assertRaisesRegex(
            evidence.GapEvidenceError,
            "configuration basis differs",
        ):
            evidence.build_evidence_report(
                repository,
                triage,
                spec,
            )

    def test_rejects_gap_set_mismatch(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec["decisions"].pop()

        with self.assertRaisesRegex(
            evidence.GapEvidenceError,
            "do not match triage queue",
        ):
            evidence.build_evidence_report(
                repository,
                triage,
                spec,
            )

    def test_rejects_source_metadata_mismatch(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec["decisions"][2]["sha256"] = "c" * 64

        with self.assertRaisesRegex(
            evidence.GapEvidenceError,
            "metadata differs",
        ):
            evidence.build_evidence_report(
                repository,
                triage,
                spec,
            )

    def test_rejects_ambiguous_without_manual_review(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec["decisions"][2][
            "manual_source_review_required"
        ] = False

        with self.assertRaisesRegex(
            evidence.GapEvidenceError,
            "require manual source review",
        ):
            evidence.build_evidence_report(
                repository,
                triage,
                spec,
            )

    def test_rejects_found_without_source_evidence(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        decision = spec["decisions"][2]
        decision["classification"] = "found"
        decision["manual_source_review_required"] = False

        with self.assertRaisesRegex(
            evidence.GapEvidenceError,
            "positive source_page",
        ):
            evidence.build_evidence_report(
                repository,
                triage,
                spec,
            )

    def test_json_and_markdown_are_deterministic(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        report = evidence.build_evidence_report(
            repository,
            triage,
            spec,
        )

        first = evidence.render_json(report)
        second = evidence.render_json(report)
        self.assertEqual(first, second)
        self.assertNotIn("generated_at", first)
        self.assertTrue(first.endswith("\n"))

        markdown = evidence.render_markdown(report)
        self.assertIn(
            "# Configuration Gap Evidence Review",
            markdown,
        )
        self.assertIn(
            "does not claim that the seven registered PDFs",
            markdown,
        )
        self.assertIn("| Ambiguous | 1 |", markdown)
        self.assertIn("| Out of scope | 2 |", markdown)

    def test_source_page_scope_reports_completed_review(self) -> None:
        temporary, repository, triage, spec = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec["review_scope"] = "source_page_evidence"
        decision = spec["decisions"][2]
        decision.update(
            {
                "classification": "not_stated",
                "manual_source_review_required": False,
                "reason_code": "not_stated_on_relevant_pages",
                "review_note": "Relevant pages were reviewed.",
                "candidate_value": "",
                "source_page": None,
                "source_section": "",
                "source_text": "",
                "reviewed_pages": [3, 4],
                "basis": None,
                "auto_import": False,
            }
        )

        report = evidence.build_evidence_report(
            repository,
            triage,
            spec,
        )

        self.assertEqual(
            report["review_scope"],
            "source_page_evidence",
        )
        self.assertTrue(report["pdf_page_review_complete"])
        self.assertEqual(
            report["next_action"],
            "plan_evidence_backed_resolution",
        )
        self.assertEqual(report["summary"]["not_stated"], 1)
        markdown = evidence.render_markdown(report)
        self.assertIn(
            "Relevant registered PDF pages were reviewed",
            markdown,
        )
        self.assertIn("reviewed pages 3, 4", markdown)

    def test_parse_args_accepts_specs_snapshot_and_outputs(self) -> None:
        arguments = evidence.parse_args(
            [
                "--evidence-spec",
                "evidence.json",
                "--completeness-spec",
                "scope.json",
                "--as-of",
                "2026-06-01",
                "--json",
                "report.json",
                "--markdown",
                "report.md",
            ]
        )
        self.assertEqual(
            arguments.evidence_spec,
            Path("evidence.json"),
        )
        self.assertEqual(
            arguments.completeness_spec,
            Path("scope.json"),
        )
        self.assertEqual(arguments.as_of, "2026-06-01")
        self.assertEqual(arguments.json_path, Path("report.json"))
        self.assertEqual(arguments.markdown, Path("report.md"))


if __name__ == "__main__":
    unittest.main()
