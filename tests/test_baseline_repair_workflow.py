from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "baseline-repair.yml"
GUIDANCE = ROOT / "project" / "BASELINE_REPAIR_WORKFLOW.md"


class BaselineRepairWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.guidance = GUIDANCE.read_text(encoding="utf-8")

    def test_generator_treats_noop_as_valid_and_continues(self) -> None:
        section = self.workflow.split(
            "- name: Reject unexpected generated paths", 1
        )[1].split(
            "- name: Upload canonical generated files", 1
        )[0]
        self.assertIn('if [[ -z "$changed" ]]; then', section)
        self.assertIn("continuing through the no-op verification", section)
        self.assertNotIn("exit 1", section)

    def test_both_apply_outcomes_publish_an_exact_target_head(self) -> None:
        self.assertIn(
            'echo "target_head_sha=$EXPECTED_HEAD_SHA" >> "$GITHUB_OUTPUT"',
            self.workflow,
        )
        self.assertIn(
            'echo "target_head_sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"',
            self.workflow,
        )
        self.assertIn(
            "TARGET_HEAD_SHA: ${{ steps.apply.outputs.target_head_sha }}",
            self.workflow,
        )

    def test_required_checks_dispatch_after_every_successful_apply(self) -> None:
        dispatch = self.workflow.split(
            "- name: Verify exact PR head and dispatch required checks", 1
        )[1]
        self.assertIn("if: steps.apply.outcome == 'success'", dispatch)
        self.assertNotIn("if: steps.apply.outputs.changed == 'true'", dispatch)
        self.assertIn('workflow_id: "quality.yml", ref: branch', dispatch)
        self.assertIn(
            'workflow_id: "repository-baselines.yml", ref: branch',
            dispatch,
        )
        self.assertIn('const changed = process.env.REPAIR_CHANGED === "true";', dispatch)

    def test_final_verification_is_bounded_and_fails_closed(self) -> None:
        dispatch = self.workflow.split(
            "- name: Verify exact PR head and dispatch required checks", 1
        )[1]
        self.assertIn("attempt <= 10", dispatch)
        self.assertIn("setTimeout(resolve, 2000)", dispatch)
        self.assertIn("if (!verified)", dispatch)
        self.assertIn("refusing dispatch", dispatch)
        self.assertIn("pr.head.sha === targetHead", dispatch)
        self.assertIn("mainRef.object.sha === expectedBase", dispatch)

    def test_documentation_records_noop_and_race_protection(self) -> None:
        self.assertIn("No-op repairs and dispatch guarantees", self.guidance)
        self.assertIn("unchanged head SHA", self.guidance)
        self.assertIn("bounded GitHub API reads", self.guidance)
        self.assertIn("tests/test_baseline_repair_workflow.py", self.guidance)


if __name__ == "__main__":
    unittest.main()
