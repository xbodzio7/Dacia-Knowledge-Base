from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import documentation_baseline  # noqa: E402
import project_state  # noqa: E402
import review_post_cross_model_workspace_priority_selection_20260727 as priority_review  # noqa: E402

PRIORITY_REPORT = (
    REPOSITORY
    / "data"
    / "reporting"
    / "post_cross_model_workspace_priority_selection_review.json"
)


class ProjectStateContractTests(unittest.TestCase):
    def fixture(self) -> dict[str, object]:
        return {
            "version": 1,
            "updated_on": "2026-07-17",
            "repository": {
                "full_name": "owner/repository",
                "default_branch": "main",
                "source_of_truth": "repository",
                "main_sha_tracking": "dynamic",
            },
            "phase": "Tooling",
            "reference_delivery": {
                "name": "Previous package",
                "pull_request": 12,
                "head_sha": "a" * 40,
                "quality_run": 34,
            },
            "baseline": {
                "tests": 10,
                "csv_files": 2,
                "rows": 20,
                "configuration_values": 3,
                "configuration_import_specs": 1,
                "configuration_value_ranges": 1,
                "configuration_range_import_specs": 1,
                "availability_records": 4,
                "attributes": 5,
                "attribute_categories": 2,
            },
            "current_package": {
                "name": "Current package",
                "status": "planned",
                "goal": "Do the current work.",
            },
            "next_package": {
                "name": "Next package",
                "status": "planned",
                "goal": "Do the next work.",
            },
            "autonomy": {
                "mode": "autonomous_until_action_required",
                "allowed_operations": ["run_tests"],
                "stop_conditions": ["missing_access"],
                "action_required_fields": [
                    "reason",
                    "required_action",
                    "options_and_consequences",
                    "resume_stage",
                ],
            },
            "review_policy": {
                "review_only_pull_requests": "exception_only",
                "milestone_review_interval_packages": 5,
                "one_logical_package_per_pull_request": True,
                "delete_remote_branches_automatically": False,
            },
        }

    def baseline(self) -> documentation_baseline.Baseline:
        return documentation_baseline.Baseline(
            version=1,
            tests=11,
            csv_files=3,
            master_rows=21,
            empty_csv_files=0,
            relationships=2,
            status_rules=3,
            validator_version="1.0",
            configuration_values=4,
            configuration_import_specs=2,
            configuration_value_ranges=2,
            configuration_range_import_specs=2,
            configuration_availability=5,
            availability_standard=4,
            availability_optional=0,
            availability_not_available=1,
            availability_unknown=0,
            attributes=6,
            attribute_categories=3,
            sqlite_tables=3,
            sqlite_rows=21,
            sqlite_verified=False,
        )

    def test_repository_state_is_valid_and_summary_is_current(self) -> None:
        state = project_state.read_state(REPOSITORY / "project" / "state.json")
        project_state.validate_state(state)
        expected = project_state.render_summary(state)
        actual = (REPOSITORY / "project" / "STATE_SUMMARY.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(actual, expected)
        self.assertEqual(project_state.check_references(REPOSITORY), [])

    def test_repository_baseline_matches_canonical_state(self) -> None:
        state = project_state.read_state(REPOSITORY / "project" / "state.json")
        live = documentation_baseline.collect_baseline(REPOSITORY)
        self.assertEqual(project_state.baseline_drift(state, live), [])
        self.assertEqual(
            documentation_baseline.check_documents(REPOSITORY, live),
            [],
        )

    def test_summary_is_deterministic(self) -> None:
        state = self.fixture()
        project_state.validate_state(state)
        first = project_state.render_summary(state)
        self.assertEqual(first, project_state.render_summary(state))
        self.assertIn("Current package", first)
        self.assertIn("ACTION_REQUIRED", first)

    def test_invalid_sha_is_rejected(self) -> None:
        state = self.fixture()
        state["reference_delivery"]["head_sha"] = "invalid"
        with self.assertRaisesRegex(
            project_state.StateError,
            "40-character SHA",
        ):
            project_state.validate_state(state)

    def test_duplicate_operations_are_rejected(self) -> None:
        state = self.fixture()
        state["autonomy"]["allowed_operations"] = ["run_tests", "run_tests"]
        with self.assertRaisesRegex(project_state.StateError, "duplicates"):
            project_state.validate_state(state)

    def test_live_baseline_projection_detects_drift(self) -> None:
        state = self.fixture()
        live = self.baseline()
        projection = project_state.live_baseline_payload(live)
        self.assertEqual(
            projection,
            {
                "tests": 11,
                "csv_files": 3,
                "rows": 21,
                "configuration_values": 4,
                "configuration_import_specs": 2,
                "configuration_value_ranges": 2,
                "configuration_range_import_specs": 2,
                "availability_records": 5,
                "attributes": 6,
                "attribute_categories": 3,
            },
        )
        drift = project_state.baseline_drift(state, live)
        self.assertEqual(len(drift), 10)
        self.assertTrue(all("live value" in item for item in drift))

    def test_synchronized_state_updates_only_live_fields(self) -> None:
        state = self.fixture()
        synchronized = project_state.synchronized_state(state, self.baseline())
        self.assertEqual(synchronized["baseline"]["tests"], 11)
        self.assertEqual(synchronized["baseline"]["rows"], 21)
        self.assertEqual(
            synchronized["current_package"],
            state["current_package"],
        )
        self.assertEqual(state["baseline"]["tests"], 10)

    def test_apply_writes_exact_summary_and_state(self) -> None:
        state = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "state.json"
            summary_path = root / "summary.md"
            project_state.write_state(state_path, state)
            loaded = project_state.read_state(state_path)
            project_state.write_atomic(
                summary_path,
                project_state.render_summary(loaded),
            )
            self.assertEqual(
                summary_path.read_text(encoding="utf-8"),
                project_state.render_summary(state),
            )
            self.assertEqual(
                project_state.read_state(state_path),
                state,
            )


class PostCrossModelWorkspacePrioritySelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(PRIORITY_REPORT.read_text(encoding="utf-8"))

    def test_metadata_and_source_milestone_are_exact(self) -> None:
        self.assertEqual(self.report["version"], 1)
        self.assertEqual(
            self.report["kind"],
            "post_cross_model_workspace_priority_selection_review",
        )
        self.assertEqual(self.report["reviewed_on"], "2026-07-27")
        self.assertEqual(self.report["status"], "complete")
        self.assertEqual(
            self.report["source_milestone"],
            "cross_model_workspace_entry_point.json",
        )

    def test_selection_policy_preserves_stable_weights(self) -> None:
        policy = self.report["selection_policy"]
        self.assertEqual(policy["scale"], "1_to_5")
        self.assertEqual(
            policy["weights_percent"],
            {
                "consumer_value": 30,
                "evidence_readiness": 25,
                "existing_tooling_reuse": 20,
                "low_implementation_risk": 15,
                "dependency_clearance": 10,
            },
        )
        self.assertEqual(sum(policy["weights_percent"].values()), 100)

    def test_repository_readiness_records_completed_consumer_flow(self) -> None:
        readiness = self.report["repository_readiness"]
        self.assertEqual(
            readiness["latest_documented_public_release"],
            "data-products-v1.8.1",
        )
        self.assertEqual(readiness["public_release_archive_members"], 85)
        self.assertEqual(readiness["offline_workspace_primary_cards"], 5)
        self.assertEqual(readiness["offline_workspace_local_links"], 84)
        self.assertEqual(readiness["active_configurations"], 72)
        self.assertEqual(readiness["model_families"], 5)
        self.assertEqual(readiness["independent_comparison_scopes"], 19)
        self.assertEqual(readiness["within_scope_pairs"], 114)
        self.assertEqual(readiness["recorded_differences"], 1695)

    def test_repository_readiness_records_pdf_foundation(self) -> None:
        readiness = self.report["repository_readiness"]
        self.assertEqual(readiness["registered_official_brochures"], 5)
        self.assertEqual(readiness["registered_brochure_pages"], 114)
        self.assertEqual(readiness["registered_brochure_bytes"], 40608101)
        self.assertTrue(readiness["registered_brochures_have_sha256"])
        self.assertEqual(readiness["pdf_text_backend_in_quality_ci"], "pdftotext")
        self.assertEqual(
            readiness["existing_pdf_review_command"],
            "configuration-gap-source-review",
        )
        self.assertEqual(len(readiness["existing_declarative_import_commands"]), 2)

    def test_candidate_order_scores_and_statuses_are_exact(self) -> None:
        candidates = self.report["candidates"]
        self.assertEqual(
            [candidate["rank"] for candidate in candidates],
            [1, 2, 3, 4, 5],
        )
        self.assertEqual(
            [candidate["weighted_score"] for candidate in candidates],
            [81, 78, 76, 57, 46],
        )
        self.assertEqual(
            [candidate["status"] for candidate in candidates],
            [
                "selected",
                "follow_up",
                "follow_up",
                "blocked_evidence",
                "blocked_source",
            ],
        )
        self.assertEqual(
            candidates[0]["code"],
            "pdf_candidate_extraction_automation_review",
        )

    def test_selection_requires_candidate_only_pdf_review(self) -> None:
        selection = self.report["selection"]
        self.assertEqual(
            selection["name"],
            "PDF Candidate Extraction Automation Review",
        )
        self.assertEqual(selection["weighted_score"], 81)
        self.assertIn("candidate-only", selection["rationale"])
        self.assertIn("without changing source data", selection["rationale"])
        self.assertEqual(
            self.report["next_package"]["name"],
            "PDF Candidate Extraction Automation Review",
        )

    def test_pdf_review_contract_preserves_evidence_boundaries(self) -> None:
        contract = self.report["pdf_candidate_extraction_review_contract"]
        self.assertEqual(contract["registered_source_count"], 5)
        self.assertEqual(contract["registered_page_count"], 114)
        self.assertIn("source_sha256", contract["required_candidate_provenance"])
        self.assertIn(
            "requires_visual_review",
            contract["required_status_boundaries"],
        )
        self.assertIn(
            "ambiguous_source_evidence",
            contract["required_status_boundaries"],
        )
        self.assertIn(
            "no_master_data_changes",
            contract["required_verification"],
        )
        self.assertIn(
            "no_approved_import_spec_generation",
            contract["required_verification"],
        )
        self.assertIn("OCR implementation", contract["non_goals"])
        self.assertIn("automatic approval", contract["non_goals"])
        self.assertIn("resolving ambiguous evidence", contract["non_goals"])

    def test_verifier_and_project_state_accept_completed_review(self) -> None:
        priority_review.verify()
        state = project_state.read_state(REPOSITORY / "project" / "state.json")
        self.assertGreaterEqual(state["baseline"]["tests"], 1071)
        self.assertGreaterEqual(state["baseline"]["rows"], 11092)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 3267)
        self.assertGreaterEqual(state["baseline"]["availability_records"], 5770)


if __name__ == "__main__":
    unittest.main()
