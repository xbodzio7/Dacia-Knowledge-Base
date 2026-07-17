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
                "availability_records": 5,
                "attributes": 6,
                "attribute_categories": 3,
            },
        )
        drift = project_state.baseline_drift(state, live)
        self.assertEqual(len(drift), 8)
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


if __name__ == "__main__":
    unittest.main()
