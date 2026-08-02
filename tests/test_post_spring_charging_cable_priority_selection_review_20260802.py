from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/review_post_spring_charging_cable_priority_selection_20260802.py"
REPORT = ROOT / "data/reporting/post_spring_charging_cable_priority_selection_review.json"
STATE = ROOT / "project/state.json"
REVIEW_PACKAGE = "post_spring_charging_cable_priority_selection_review_001"
SELECTED_PACKAGE = "spring_biel_alpejska_default_colour_migration_001"


def load_tool():
    spec = importlib.util.spec_from_file_location("priority_review", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load priority review tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PostSpringChargingCablePrioritySelectionReviewTests(unittest.TestCase):
    def test_review_is_deterministic_and_review_only(self):
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        state = json.loads(STATE.read_text(encoding="utf-8"))
        if state["current_package"]["package_id"] == REVIEW_PACKAGE:
            tool = load_tool()
            self.assertEqual(payload, tool.build(ROOT))
        self.assertEqual(payload["package_id"], REVIEW_PACKAGE)
        self.assertEqual(
            payload["mutation_summary"],
            {
                "master_rows_changed": 0,
                "configuration_values_added": 0,
                "commercial_mappings_changed": 0,
            },
        )

    def test_selection_preserves_exact_evidence_boundary(self):
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["selection"]["package_id"], SELECTED_PACKAGE)
        evidence = payload["selected_evidence"]
        self.assertEqual(evidence["current_direct_value_count"], 0)
        self.assertEqual(evidence["attribute_code"], "exterior_color")
        self.assertEqual(evidence["value"], "biel alpejska")
        self.assertEqual(
            evidence["source_code"],
            "src_pl_spring_commercial_context_20260802",
        )
        self.assertEqual(
            evidence["commercial_mapping"]["current_availability_status"],
            "optional",
        )
        self.assertIsNone(evidence["commercial_mapping"]["current_amount"])
        self.assertEqual(
            evidence["commercial_mapping"]["target_availability_status"],
            "standard",
        )
        self.assertEqual(evidence["commercial_mapping"]["target_amount_pln"], 0)

    def test_canonical_state_points_to_selected_package(self):
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["package_id"], SELECTED_PACKAGE)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["package_id"],
            "post_spring_biel_alpejska_priority_selection_review_001",
        )
        self.assertEqual(state["baseline"]["rows"], 11729)


if __name__ == "__main__":
    unittest.main()
