from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))
import configuration_gap_resolution_plan as planning  # noqa: E402


class ConfigurationGapResolutionPlanTests(unittest.TestCase):
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
    ) -> tuple[
        tempfile.TemporaryDirectory[str],
        Path,
        dict,
    ]:
        temporary = tempfile.TemporaryDirectory()
        repository = Path(temporary.name)
        master = repository / "data" / "master"

        self.write_csv(
            master / "attributes.csv",
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
                    "code": "wheel_design",
                    "category": "Wheels",
                    "name": "Wheel design",
                    "data_type": "string",
                    "unit": "",
                    "description": "Commercial wheel design name.",
                    "status": "active",
                },
                {
                    "id": "2",
                    "code": "wheel_finish",
                    "category": "Wheels",
                    "name": "Wheel finish",
                    "data_type": "string",
                    "unit": "",
                    "description": "Wheel finish.",
                    "status": "active",
                },
            ],
        )
        self.write_csv(
            master / "configurations.csv",
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
                    "code": "sandero_stepway_iii_essential_ecog120_manual",
                    "version_code": "stepway_essential",
                    "powertrain_label": "Eco-G 120",
                    "transmission_type": "manual",
                    "status": "active",
                    "notes": "",
                }
            ],
        )
        self.write_csv(
            master / "sources.csv",
            [
                "id",
                "code",
                "title",
                "document_date",
                "file_path",
                "sha256",
                "status",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "src_a",
                    "title": "Source A",
                    "document_date": "2026-06-26",
                    "file_path": "PDF/source-a.pdf",
                    "sha256": "a" * 64,
                    "status": "active",
                    "notes": "",
                }
            ],
        )
        self.write_csv(
            master / "source_configurations.csv",
            [
                "id",
                "code",
                "source_code",
                "configuration_code",
                "status",
                "notes",
            ],
            [
                {
                    "id": "1",
                    "code": "src-a-cfg",
                    "source_code": "src_a",
                    "configuration_code": (
                        "sandero_stepway_iii_essential_ecog120_manual"
                    ),
                    "status": "active",
                    "notes": "",
                }
            ],
        )
        self.write_csv(
            master / "configuration_attribute_values.csv",
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "fuel_type_code",
                "value",
                "observation_date",
                "source_code",
                "notes",
            ],
            [
                {
                    "id": "309",
                    "code": "existing",
                    "configuration_code": (
                        "sandero_stepway_iii_essential_ecog120_manual"
                    ),
                    "attribute_code": "wheel_finish",
                    "fuel_type_code": "",
                    "value": "painted",
                    "observation_date": "2026-06-26",
                    "source_code": "src_a",
                    "notes": "Source page 2: painted",
                }
            ],
        )

        common = {
            "domain": "technical",
            "source_code": "src_a",
            "configuration_code": (
                "sandero_stepway_iii_essential_ecog120_manual"
            ),
            "category": "Wheels",
            "fuel_type_code": "",
            "document_date": "2026-06-26",
            "file_path": "PDF/source-a.pdf",
            "sha256": "a" * 64,
            "auto_import": False,
        }
        evidence = {
            "version": 1,
            "as_of": "2026-06-26",
            "review_scope": "source_page_evidence",
            "review_policy": {
                "auto_import": False,
            },
            "decisions": [
                {
                    **common,
                    "triage_key": "found",
                    "attribute_code": "wheel_design",
                    "classification": "found",
                    "candidate_value": "ERALIA",
                    "source_page": 2,
                    "source_section": "Felgi",
                    "source_text": "ERALIA",
                    "reviewed_pages": [2],
                },
                {
                    **common,
                    "triage_key": "not-stated",
                    "attribute_code": "wheel_design",
                    "classification": "not_stated",
                    "candidate_value": "",
                    "source_page": None,
                    "source_section": "",
                    "source_text": "",
                    "reviewed_pages": [2],
                },
                {
                    **common,
                    "triage_key": "out-of-scope",
                    "attribute_code": "wheel_finish",
                    "classification": "out_of_scope",
                    "candidate_value": "",
                    "source_page": 2,
                    "source_section": "Felgi",
                    "source_text": "stalowe",
                    "reviewed_pages": [2],
                },
            ],
        }
        return temporary, repository, evidence

    def test_builds_resolution_plan_for_all_evidence_states(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec = planning.build_expected_plan_spec(repository, evidence)
        report = planning.build_report(repository, evidence, spec)

        self.assertEqual(report["summary"]["total_decisions"], 3)
        self.assertEqual(report["summary"]["ready_for_import"], 1)
        self.assertEqual(report["summary"]["closed_not_stated"], 1)
        self.assertEqual(report["summary"]["closed_out_of_scope"], 1)
        self.assertEqual(report["summary"]["candidate_packages"], 1)
        self.assertEqual(report["summary"]["planned_rows"], 1)

    def test_zero_candidates_route_to_closure_milestone(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        evidence["decisions"] = [
            decision
            for decision in evidence["decisions"]
            if decision["classification"] != "found"
        ]

        spec = planning.build_expected_plan_spec(repository, evidence)
        report = planning.build_report(repository, evidence, spec)

        self.assertEqual(report["summary"]["total_decisions"], 2)
        self.assertEqual(report["summary"]["ready_for_import"], 0)
        self.assertEqual(report["summary"]["candidate_packages"], 0)
        self.assertEqual(report["summary"]["planned_rows"], 0)
        self.assertEqual(
            report["next_package"],
            "Configuration Gap Closure Documentation Milestone",
        )

    def test_found_candidate_reuses_existing_string_model(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec = planning.build_expected_plan_spec(repository, evidence)

        candidate = spec["decisions"][0]
        package = spec["candidate_packages"][0]
        proposed = package["proposed_import_spec"]

        self.assertEqual(candidate["resolution_state"], "ready_for_import")
        self.assertFalse(candidate["requires_model_change"])
        self.assertEqual(
            candidate["resolution_route"],
            "configuration_attribute_values",
        )
        self.assertEqual(proposed["id_start"], 310)
        self.assertEqual(proposed["attribute_code"], "wheel_design")
        self.assertEqual(proposed["attribute_contract"]["data_type"], "string")
        self.assertEqual(proposed["rows"][0]["value"], "ERALIA")

    def test_rejects_existing_conflicting_value(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = (
            repository
            / "data"
            / "master"
            / "configuration_attribute_values.csv"
        )
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        rows.append(
            {
                "id": "310",
                "code": "conflict",
                "configuration_code": (
                    "sandero_stepway_iii_essential_ecog120_manual"
                ),
                "attribute_code": "wheel_design",
                "fuel_type_code": "",
                "value": "TAMIA",
                "observation_date": "2026-06-26",
                "source_code": "src_a",
                "notes": "Source page 2: TAMIA",
            }
        )
        self.write_csv(
            path,
            list(rows[0]),
            rows,
        )

        with self.assertRaisesRegex(
            planning.GapResolutionPlanError,
            "already exists or conflicts",
        ):
            planning.build_expected_plan_spec(repository, evidence)

    def test_rejects_missing_source_configuration_pair(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = (
            repository
            / "data"
            / "master"
            / "source_configurations.csv"
        )
        self.write_csv(
            path,
            [
                "id",
                "code",
                "source_code",
                "configuration_code",
                "status",
                "notes",
            ],
            [],
        )

        with self.assertRaisesRegex(
            planning.GapResolutionPlanError,
            "does not document configuration",
        ):
            planning.build_expected_plan_spec(repository, evidence)

    def test_rejects_found_without_candidate_value(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        evidence["decisions"][0]["candidate_value"] = ""

        with self.assertRaisesRegex(
            planning.GapResolutionPlanError,
            "found candidate_value",
        ):
            planning.build_expected_plan_spec(repository, evidence)

    def test_rejects_ambiguous_evidence(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        evidence["decisions"][1]["classification"] = "ambiguous"

        with self.assertRaisesRegex(
            planning.GapResolutionPlanError,
            "cannot accept ambiguous",
        ):
            planning.build_expected_plan_spec(repository, evidence)

    def test_rejects_plan_decision_set_mismatch(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec = planning.build_expected_plan_spec(repository, evidence)
        spec["decisions"].pop()

        with self.assertRaisesRegex(
            planning.GapResolutionPlanError,
            "differs from current evidence",
        ):
            planning.build_report(repository, evidence, spec)

    def test_rejects_plan_content_mismatch(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec = planning.build_expected_plan_spec(repository, evidence)
        spec["decisions"][0]["requires_model_change"] = True

        with self.assertRaisesRegex(
            planning.GapResolutionPlanError,
            "differs from current evidence",
        ):
            planning.build_report(repository, evidence, spec)

    def test_json_and_markdown_are_deterministic(self) -> None:
        temporary, repository, evidence = self.fixture()
        self.addCleanup(temporary.cleanup)
        spec = planning.build_expected_plan_spec(repository, evidence)
        report = planning.build_report(repository, evidence, spec)

        self.assertEqual(
            planning.render_json(report),
            planning.render_json(report),
        )
        markdown = planning.render_markdown(report)
        self.assertIn("# Configuration Gap Resolution Plan", markdown)
        self.assertIn("| Ready for import | 1 |", markdown)
        self.assertIn("ERALIA", markdown)
        self.assertIn("Automatic import: `false`", markdown)

    def test_parse_args_accepts_specs_and_outputs(self) -> None:
        arguments = planning.parse_args(
            [
                "--evidence-spec",
                "evidence.json",
                "--plan-spec",
                "plan.json",
                "--write-plan-spec",
                "new-plan.json",
                "--json",
                "report.json",
                "--markdown",
                "report.md",
            ]
        )
        self.assertEqual(arguments.evidence_spec, Path("evidence.json"))
        self.assertEqual(arguments.plan_spec, Path("plan.json"))
        self.assertEqual(
            arguments.write_plan_spec,
            Path("new-plan.json"),
        )
        self.assertEqual(arguments.json_path, Path("report.json"))
        self.assertEqual(arguments.markdown, Path("report.md"))


if __name__ == "__main__":
    unittest.main()
