from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DataProductsV110AcceleratedReleaseContractTest(unittest.TestCase):
    def test_accelerated_policy_is_canonical_and_documented(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        policy = state["execution_policy"]
        self.assertEqual(policy["mode"], "accelerated_milestone_closure")
        self.assertTrue(policy["focused_tests_during_development"])
        self.assertTrue(policy["full_quality_on_final_head"])
        self.assertTrue(policy["batch_mechanical_repairs"])
        self.assertTrue(policy["open_pr_after_package_stabilization"])
        self.assertEqual(
            policy["allow_multi_source_package"],
            "only_for_one_logical_closure_scope",
        )

        start_here = (ROOT / "project/START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("ACCELERATED_MILESTONE_CLOSURE.md", start_here)

        maintainer = (
            ROOT / "project/AUTONOMOUS_MAINTAINER.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Accelerated milestone closure mode", maintainer)

        decision = (ROOT / "project/DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("## D-ACC-001 — Accelerated milestone closure mode", decision)

    def test_release_notes_include_interface_repairs(self) -> None:
        release_source = (
            ROOT / "tools/reporting/data_product_release.py"
        ).read_text(encoding="utf-8")
        self.assertIn('elif version == "1.10.0":', release_source)
        self.assertIn("forced dark theme", release_source)
        self.assertIn("two-axis sticky comparison grid", release_source)
        self.assertIn("grouped commercial grade choices", release_source)

    def test_current_interface_repair_contract_remains_present(self) -> None:
        selection_html = (
            ROOT / "tools/reporting/configuration_shortlist_selection_html.py"
        ).read_text(encoding="utf-8")
        self.assertIn("Interface repair v1.6", selection_html)
        self.assertIn("position:sticky;top:0", selection_html)
        self.assertIn("position:sticky;left:0", selection_html)
        self.assertIn("--parameter-column:280px", selection_html)
        self.assertIn("--data-column:260px", selection_html)


if __name__ == "__main__":
    unittest.main()
