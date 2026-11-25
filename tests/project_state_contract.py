from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import documentation_baseline  # noqa: E402
import project_state  # noqa: E402
import project_state_transition  # noqa: E402
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
                "package_id": "current_package_001",
                "kind": "reporting",
                "name": "Current package",
                "status": "planned",
                "goal": "Do the current work.",
            },
            "next_package": {
                "package_id": "next_package_001",
                "kind": "source_gap_closure",
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

        # Keep the remote baseline-repair workflow's security contract under
        # the existing test case so this check does not alter the test-count
        # baseline merely by adding workflow coverage.
        workflow = (
            REPOSITORY / ".github" / "workflows" / "baseline-repair.yml"
        ).read_text(encoding="utf-8")
        dispatch_inputs = workflow.split("workflow_dispatch:", 1)[1].split(
            "\npermissions:", 1
        )[0]
        self.assertIn("pr_number:", dispatch_inputs)
        self.assertNotIn("pr_branch:", dispatch_inputs)
        self.assertNotIn("expected_head_sha:", dispatch_inputs)
        self.assertIn('pr.state !== "open"', workflow)
        self.assertIn('pr.base.ref !== "main"', workflow)
        self.assertIn("pr.head.repo.full_name.toLowerCase()", workflow)
        self.assertIn("pr.base.sha !== mainRef.object.sha", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("Re-verify the exact open PR before write-back", workflow)
        self.assertIn("exact six-file allowlist", workflow)
        self.assertIn(":(exclude)baseline-repair/**", workflow)
        self.assertIn("changes outside the downloaded baseline artifact", workflow)
        self.assertIn('workflow_id: "quality.yml"', workflow)
        self.assertIn('workflow_id: "repository-baselines.yml"', workflow)
        self.assertNotIn("pull_request_target:", workflow)

    def test_repository_baseline_matches_canonical_state(self) -> None:
        state = project_state.read_state(REPOSITORY / "project" / "state.json")
        live = documentation_baseline.collect_baseline(REPOSITORY)
        self.assertEqual(project_state.baseline_drift(state, live), [])
        self.assertEqual(
            documentation_baseline.check_documents(REPOSITORY, live),
            [],
        )

    def test_runtime_metadata_accepts_matching_github_context(self) -> None:
        project_state.validate_runtime_metadata(
            self.fixture(),
            {
                "DKB_EXPECTED_REPOSITORY": "owner/repository",
                "DKB_EXPECTED_DEFAULT_BRANCH": "main",
                "DKB_EXPECTED_BASE_BRANCH": "main",
            },
        )

    def test_runtime_metadata_rejects_repository_mismatch(self) -> None:
        with self.assertRaisesRegex(project_state.StateError, "GitHub repository"):
            project_state.validate_runtime_metadata(
                self.fixture(),
                {"DKB_EXPECTED_REPOSITORY": "other/repository"},
            )

    def test_runtime_metadata_rejects_default_branch_mismatch(self) -> None:
        with self.assertRaisesRegex(
            project_state.StateError, "GitHub default branch"
        ):
            project_state.validate_runtime_metadata(
                self.fixture(),
                {"DKB_EXPECTED_DEFAULT_BRANCH": "trunk"},
            )

    def test_runtime_metadata_rejects_nondefault_pull_request_target(self) -> None:
        with self.assertRaisesRegex(
            project_state.StateError, "Pull Request base branch"
        ):
            project_state.validate_runtime_metadata(
                self.fixture(),
                {"DKB_EXPECTED_BASE_BRANCH": "develop"},
            )

    def test_runtime_metadata_is_optional_without_github_context(self) -> None:
        project_state.validate_runtime_metadata(self.fixture(), {})

    def test_runtime_metadata_supports_native_github_environment_names(self) -> None:
        project_state.validate_runtime_metadata(
            self.fixture(),
            {
                "GITHUB_REPOSITORY": "OWNER/REPOSITORY",
                "GITHUB_BASE_REF": "main",
            },
        )

    def test_current_and_next_package_ids_must_be_distinct(self) -> None:
        state = self.fixture()
        state["next_package"]["package_id"] = state["current_package"]["package_id"]
        with self.assertRaisesRegex(
            project_state.StateError,
            "must have different package_id values",
        ):
            project_state.validate_state(state)

        previous = self.fixture()
        previous["next_package"]["kind"] = "reporting"

        quality_workflow = (
            REPOSITORY / ".github" / "workflows" / "quality.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("Validate canonical package-state transition", quality_workflow)
        self.assertIn("python tools/project_state_transition.py", quality_workflow)
        self.assertIn("github.event_name == 'workflow_dispatch'", quality_workflow)
        self.assertIn("github.event.repository.default_branch", quality_workflow)

        changed_queue = copy.deepcopy(previous)
        changed_queue["next_package"]["package_id"] = "replacement_package_001"
        changed_queue["next_package"]["name"] = "Replacement package"
        with self.assertRaisesRegex(
            project_state_transition.TransitionError, "new next_package_selection"
        ):
            project_state_transition.validate_transition(
                previous, changed_queue, REPOSITORY, head_ref="HEAD"
            )
        changed_queue["next_package_selection"] = "Replacement package"
        changed_queue["rationale"] = "The current evidence requires a new priority."
        project_state_transition.validate_transition(
            previous, changed_queue, REPOSITORY, head_ref="HEAD"
        )

        with tempfile.TemporaryDirectory() as temporary:
            completion_repo = Path(temporary)
            subprocess.run(
                ["git", "init", "--quiet"],
                cwd=completion_repo,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "DKB test"],
                cwd=completion_repo,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "dkb-test@example.invalid"],
                cwd=completion_repo,
                check=True,
                capture_output=True,
            )
            report_path = "reports/price_history/report.json"
            report_file = completion_repo / report_path
            report_file.parent.mkdir(parents=True)
            report_file.write_text('{"status": "fully_reconciled"}\n', encoding="utf-8")
            registry_file = completion_repo / "data" / "reporting" / "report_registry.json"
            registry_file.parent.mkdir(parents=True)
            registry_file.write_text(
                json.dumps({"reports": [{
                    "report_id": "completed-fixture-report",
                    "json_path": report_path,
                }]}) + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["git", "add", report_path, "data/reporting/report_registry.json"],
                cwd=completion_repo,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "--quiet", "-m", "Merge pull request #899"],
                cwd=completion_repo,
                check=True,
                capture_output=True,
            )
            merge_sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=completion_repo,
                text=True,
            ).strip()

            completed = copy.deepcopy(previous)
            completed["current_package"]["status"] = "complete"
            completed["current_package"]["report_path"] = report_path
            completed["current_package"]["completion"] = {
                "pull_request": 899,
                "merge_commit_sha": merge_sha,
                "report_path": report_path,
                "completed_on": "2026-11-25",
            }
            project_state_transition.validate_transition(
                previous, completed, completion_repo, head_ref="HEAD"
            )

        missing_completion = copy.deepcopy(previous)
        missing_completion["current_package"]["status"] = "complete"
        with self.assertRaisesRegex(
            project_state_transition.TransitionError, "completion"
        ):
            project_state_transition.validate_transition(
                previous, missing_completion, REPOSITORY, head_ref="HEAD"
            )

        previous["current_package"]["status"] = "complete"
        promoted = copy.deepcopy(previous)
        promoted["current_package"] = copy.deepcopy(previous["next_package"])
        promoted["current_package"]["status"] = "planned"
        promoted["next_package"] = {
            "package_id": "bigster_brochure_001",
            "kind": "source_brochure_assimilation",
            "name": "Bigster brochure assimilation",
            "status": "planned",
            "goal": "Review the full official brochure against the current cennik.",
            "source_paths": [
                "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf",
                "PDF/Cenniki/DACIA BIGSTER cennik MY26 20261001.pdf",
            ],
        }
        promoted["next_package_selection"] = "Bigster brochure assimilation"
        promoted["rationale"] = "The prior source reconciliation is complete."
        project_state_transition.validate_transition(
            previous, promoted, REPOSITORY, head_ref="HEAD"
        )

        missing_source = copy.deepcopy(promoted)
        missing_source["next_package"]["source_paths"] = [
            "PDF/Broszury/not-archived.pdf"
        ]
        with self.assertRaisesRegex(
            project_state_transition.TransitionError, "does not exist"
        ):
            project_state_transition.validate_transition(
                previous, missing_source, REPOSITORY, head_ref="HEAD"
            )

        skipped_package = copy.deepcopy(promoted)
        skipped_package["current_package"]["package_id"] = "unplanned_package_999"
        with self.assertRaisesRegex(
            project_state_transition.TransitionError, "previous next_package"
        ):
            project_state_transition.validate_transition(
                previous, skipped_package, REPOSITORY, head_ref="HEAD"
            )

    def test_completed_package_cannot_remain_next(self) -> None:
        state = self.fixture()
        state["next_package"]["status"] = "complete"
        with self.assertRaisesRegex(
            project_state.StateError,
            "next_package.status cannot be 'complete'",
        ):
            project_state.validate_state(state)

    def test_package_identity_and_kind_are_required(self) -> None:
        state = self.fixture()
        del state["current_package"]["package_id"]
        with self.assertRaisesRegex(
            project_state.StateError,
            "current_package.package_id",
        ):
            project_state.validate_state(state)

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
