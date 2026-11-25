from __future__ import annotations

import re
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
WORKFLOW = REPOSITORY / ".github" / "workflows" / "baseline-repair.yml"


class BaselineRepairWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_dispatch_requires_only_the_pull_request_number(self) -> None:
        inputs = re.search(
            r"workflow_dispatch:\s*\n\s+inputs:\s*\n(?P<body>.*?)(?=\n\npermissions:)",
            self.workflow,
            re.DOTALL,
        )
        self.assertIsNotNone(inputs)
        body = inputs.group("body")
        self.assertRegex(body, r"^\s{6}pr_number:")
        self.assertNotRegex(body, r"(?m)^\s{6}(?:pr_branch|expected_head_sha):")
        self.assertIn("context.payload.inputs.pr_number", self.workflow)

    def test_read_only_job_derives_and_validates_pr_identity(self) -> None:
        self.assertIn("pr.state !== \"open\"", self.workflow)
        self.assertIn('pr.base.ref !== "main"', self.workflow)
        self.assertIn("pr.head.repo.full_name.toLowerCase()", self.workflow)
        self.assertIn("pr.base.sha !== mainRef.object.sha", self.workflow)
        self.assertIn('core.setOutput("branch", pr.head.ref)', self.workflow)
        self.assertIn('core.setOutput("head_sha", pr.head.sha)', self.workflow)
        self.assertIn('ref: ${{ steps.verify.outputs.head_sha }}', self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)

    def test_write_credentials_are_isolated_from_pr_code(self) -> None:
        self.assertIn("generate-baseline-repair:", self.workflow)
        self.assertIn("write-back-baseline-repair:", self.workflow)
        generation = self.workflow.split("  write-back-baseline-repair:", 1)[0]
        writeback = self.workflow.split("  write-back-baseline-repair:", 1)[1]
        self.assertRegex(generation, r"(?m)^\s{6}contents: read$")
        self.assertRegex(generation, r"(?m)^\s{6}pull-requests: read$")
        self.assertNotRegex(generation, r"(?m)^\s{6}contents: write$")
        self.assertRegex(writeback, r"(?m)^\s{6}contents: write$")
        self.assertIn("Re-verify the exact open PR before write-back", writeback)
        self.assertIn("PR identity, base or exact head changed; refusing baseline write-back.", writeback)
        self.assertNotIn("pull_request_target:", self.workflow)

    def test_writeback_is_limited_to_exact_generated_file_allowlist(self) -> None:
        for path in (
            "CHANGELOG.md",
            "README.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ):
            self.assertIn(path, self.workflow)
        self.assertIn("exact six-file allowlist", self.workflow)
        self.assertIn("find baseline-repair -type l", self.workflow)
        self.assertIn('git push origin "HEAD:refs/heads/$PR_BRANCH"', self.workflow)
        self.assertNotRegex(self.workflow, r"(?m)^\s*git push .*--force")

    def test_updated_head_receives_normal_required_workflows(self) -> None:
        self.assertIn('workflow_id: "quality.yml"', self.workflow)
        self.assertIn('workflow_id: "repository-baselines.yml"', self.workflow)
        self.assertIn("pr.head.sha !== commit", self.workflow)
        self.assertIn("mainRef.object.sha !== expectedBase", self.workflow)


if __name__ == "__main__":
    unittest.main()
