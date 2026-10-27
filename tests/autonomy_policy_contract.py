from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import autonomy_decision  # noqa: E402
import project_state  # noqa: E402


class AutonomyPolicyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = project_state.read_state(REPOSITORY / "project" / "state.json")

    def event(
        self,
        stage: str,
        outcome: str = "pass",
        **values: object,
    ) -> dict[str, object]:
        event: dict[str, object] = {
            "version": 1,
            "stage": stage,
            "outcome": outcome,
        }
        event.update(values)
        return event

    def test_successful_stages_continue_without_user_action(self) -> None:
        expected = {
            "analysis": "implement_package",
            "implementation": "run_tests_and_quality",
            "quality": "publish_package",
            "publication": "create_pull_request",
            "pull_request": "monitor_ci",
            "merge": "update_project_state_and_documentation",
            "state_update": "start_next_package",
        }
        for stage, action in expected.items():
            with self.subTest(stage=stage):
                decision = autonomy_decision.resolve_decision(
                    self.state,
                    self.event(stage),
                )
                self.assertEqual(decision["disposition"], "CONTINUE")
                self.assertEqual(decision["action"], action)
                self.assertFalse(decision["stop"])
                self.assertIsNone(decision["action_required"])

    def test_current_green_mergeable_ci_continues_to_merge(self) -> None:
        decision = autonomy_decision.resolve_decision(
            self.state,
            self.event(
                "ci",
                head_current=True,
                checks_passed=True,
                mergeable=True,
            ),
        )
        self.assertEqual(decision["action"], "merge_pull_request")
        self.assertFalse(decision["stop"])

    def test_stale_head_is_reverified_without_stopping(self) -> None:
        decision = autonomy_decision.resolve_decision(
            self.state,
            self.event(
                "ci",
                head_current=False,
                checks_passed=True,
                mergeable=True,
            ),
        )
        self.assertEqual(decision["action"], "reverify_pull_request_head")
        self.assertEqual(decision["disposition"], "CONTINUE")

    def test_transient_mergeability_is_retried(self) -> None:
        decision = autonomy_decision.resolve_decision(
            self.state,
            self.event(
                "ci",
                head_current=True,
                checks_passed=True,
                mergeable=False,
            ),
        )
        self.assertEqual(decision["disposition"], "RETRY")
        self.assertEqual(decision["action"], "refresh_mergeability_and_retry")

    def test_in_scope_failure_is_repaired_and_retried(self) -> None:
        decision = autonomy_decision.resolve_decision(
            self.state,
            self.event(
                "quality",
                "fail",
                reason_code="test_failure",
                in_scope=True,
            ),
        )
        self.assertEqual(decision["disposition"], "REPAIR_AND_RETRY")
        self.assertEqual(decision["action"], "repair_quality_and_retry")
        self.assertFalse(decision["stop"])

    def test_declared_stop_condition_requires_user_action(self) -> None:
        decision = autonomy_decision.resolve_decision(
            self.state,
            self.event(
                "implementation",
                "blocked",
                reason_code="ambiguous_source_evidence",
            ),
        )
        self.assertEqual(decision["disposition"], "ACTION_REQUIRED")
        self.assertTrue(decision["stop"])
        self.assertEqual(
            list(decision["action_required"]),
            [
                "reason",
                "required_action",
                "options_and_consequences",
                "resume_stage",
            ],
        )
        self.assertEqual(
            decision["action_required"]["resume_stage"],
            "implementation",
        )

    def test_out_of_scope_failure_requires_scope_decision(self) -> None:
        decision = autonomy_decision.resolve_decision(
            self.state,
            self.event(
                "implementation",
                "fail",
                reason_code="unexpected_dependency",
                in_scope=False,
            ),
        )
        self.assertEqual(decision["disposition"], "ACTION_REQUIRED")
        self.assertEqual(
            decision["reason_code"],
            "scope_expansion_beyond_current_milestone",
        )

    def test_invalid_passing_ci_event_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            autonomy_decision.DecisionError,
            "head_current is required",
        ):
            autonomy_decision.resolve_decision(
                self.state,
                self.event("ci"),
            )

    def test_rendered_decision_is_deterministic(self) -> None:
        decision = autonomy_decision.resolve_decision(
            self.state,
            self.event("analysis"),
        )
        rendered = autonomy_decision.render_json(decision)
        self.assertEqual(rendered, autonomy_decision.render_json(decision))
        self.assertTrue(rendered.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
