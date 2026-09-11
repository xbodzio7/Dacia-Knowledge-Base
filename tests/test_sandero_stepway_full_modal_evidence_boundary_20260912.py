from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/sandero_stepway_full_modal_evidence_boundary_20260912.json"
RECONCILIATION = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"


class SanderoStepwayFullModalEvidenceBoundaryTests(unittest.TestCase):
    def test_report_matches_source_reconciliation_boundaries(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))

        self.assertEqual(report["source_code"], "src_pl_sandero_stepway_full_modal_20260809")
        self.assertEqual(report["scope"]["captured_rows"], reconciliation["summary"]["captured_rows"])
        self.assertEqual(report["scope"]["current_residual_rows"], 940)
        self.assertEqual(report["counts"], {
            "preserved_negative_or_base_equipment": 59,
            "preserved_unmapped_equipment": 96,
            "preserved_schema_gap_equipment": 9,
            "preserved_contextual_technical": 124,
            "preserved_model_qualified_technical": 60,
            "preserved_evidence_boundary_total": 348,
        })

    def test_policy_forbids_promotion(self) -> None:
        policy = json.loads(REPORT.read_text(encoding="utf-8"))["policy"]
        self.assertFalse(policy["master_data_changes"])
        self.assertFalse(policy["approved_import_spec_generation"])
        self.assertFalse(policy["automatic_promotion"])
        self.assertTrue(policy["negative_evidence_is_not_inferred"])
        self.assertTrue(policy["composite_or_model_qualified_values_are_not_projected"])
        self.assertTrue(policy["parser_artifacts_are_not_promoted"])


if __name__ == "__main__":
    unittest.main()
