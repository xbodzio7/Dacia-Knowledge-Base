import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "cross_model_configurator_conflict_closure.json"


class CrossModelConfiguratorConflictClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_all_saved_states_have_unique_canonical_identity_matches(self):
        rows = self.data["rows"]
        self.assertEqual(len(rows), 18)
        self.assertEqual(len({row["configuration_code"] for row in rows}), 18)
        self.assertEqual(len({row["canonical_configuration_code"] for row in rows}), 18)
        self.assertEqual(self.data["canonical_identity_matches"], 18)

    def test_classification_totals_close_without_unresolved_conflicts(self):
        self.assertEqual(self.data["direct_current_identity_matches"], 8)
        self.assertEqual(self.data["phase_qualified_identity_matches"], 10)
        self.assertEqual(self.data["unresolved_identity_conflicts"], 0)
        self.assertEqual(self.data["destructive_replacements"], 0)
        self.assertEqual(self.data["historical_observations_removed"], 0)
        self.assertEqual(self.data["milestone_status"], "complete")

    def test_phase_qualified_rows_keep_explicit_source_phase(self):
        qualified = [
            row for row in self.data["rows"]
            if row["classification"] == "phase_qualified_identity_match"
        ]
        self.assertEqual(len(qualified), 10)
        self.assertTrue(all(row.get("source_phase") in {"new", "F.2"} for row in qualified))

    def test_closure_policy_forbids_unsafe_promotion_and_history_deletion(self):
        policy = self.data["closure_policy"]
        for key in (
            "dated_observations_coexist",
            "no_cross_phase_promotion",
            "no_cross_grade_transfer",
            "no_cross_powertrain_transfer",
            "no_history_deletion",
            "raw_source_lines_remain_reporting_evidence",
        ):
            self.assertIs(policy[key], True)


if __name__ == "__main__":
    unittest.main()
