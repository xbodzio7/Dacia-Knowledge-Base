from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "data" / "reporting" / "brochure_gear_performance_context_model.json"
DECISIONS_PATH = ROOT / "project" / "DECISIONS.md"
VALUES_PATH = ROOT / "data" / "master" / "configuration_attribute_values.csv"


class BrochureGearPerformanceContextModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))

    def test_model_accepts_one_optional_positive_integer_column(self) -> None:
        decision = self.model["decision"]
        self.assertEqual(self.model["status"], "accepted")
        self.assertEqual(self.model["canonical_attribute"], "elasticity_80_120")
        self.assertEqual(decision["storage"], "configuration_attribute_values_optional_column")
        self.assertEqual(decision["planned_column"], "gear_number")
        self.assertEqual(decision["column_position"], "after_fuel_type_code_before_value")
        self.assertEqual(decision["data_type"], "positive_integer")
        self.assertEqual(decision["initial_eligible_attributes"], ["elasticity_80_120"])

    def test_existing_dimensions_are_reused_not_duplicated(self) -> None:
        reused = self.model["existing_dimensions_reused"]
        self.assertEqual(set(reused), {"speed_interval", "fuel", "passenger_layout", "powertrain_and_transmission"})
        identity = self.model["planned_semantics"]["observation_identity_dimensions"]
        self.assertEqual(identity, ["configuration_code", "attribute_code", "fuel_type_code", "gear_number"])
        serialized = json.dumps(self.model, ensure_ascii=False)
        self.assertIn("configuration_attribute_values.fuel_type_code", serialized)
        self.assertIn("exact configurations", serialized)

    def test_source_evidence_covers_sandero_stepway_and_jogger(self) -> None:
        evidence = {item["source_code"]: item for item in self.model["source_evidence"]}
        self.assertEqual(
            set(evidence),
            {
                "src_pl_sandero_brochure_20260202",
                "src_pl_sandero_stepway_brochure_20260202",
                "src_pl_jogger_brochure_20251217",
            },
        )
        self.assertEqual(evidence["src_pl_sandero_brochure_20260202"]["gear_numbers"], [4, 5])
        self.assertEqual(evidence["src_pl_sandero_stepway_brochure_20260202"]["gear_numbers"], [4, 5, 6])
        self.assertEqual(evidence["src_pl_jogger_brochure_20251217"]["gear_numbers"], [4])
        self.assertTrue(evidence["src_pl_jogger_brochure_20251217"]["passenger_layout_specific"])

    def test_rejected_alternatives_and_validation_boundary_are_explicit(self) -> None:
        alternatives = {item["alternative"] for item in self.model["rejected_alternatives"]}
        self.assertEqual(
            alternatives,
            {
                "gear_specific_attribute_codes",
                "one_to_one_gear_context_relation",
                "generic_key_value_measurement_context",
                "duplicate_fuel_layout_or_transmission_fields",
            },
        )
        validation = "\n".join(self.model["planned_validation"])
        self.assertIn("canonical positive integer", validation)
        self.assertIn("eligible performance attribute", validation)
        self.assertIn("reporting and latest-value selection include gear_number", validation)
        self.assertIn("Blank is not unknown", self.model["planned_semantics"]["blank_value"])

    def test_modeling_package_changes_no_master_schema_or_values(self) -> None:
        with VALUES_PATH.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            row_count = sum(1 for _ in reader)
        self.assertEqual(
            header,
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "fuel_type_code",
                "value",
                "observation_date",
                "source_code",
                "notes",
            ],
        )
        self.assertEqual(row_count, 2118)
        decisions = DECISIONS_PATH.read_text(encoding="utf-8")
        self.assertIn("## D-024 — Observation-level selected-gear context", decisions)
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Brochure Gear-Specific Performance Context Modeling")
        self.assertEqual(state["baseline"]["tests"], 813)
        self.assertEqual(state["baseline"]["rows"], 8782)


if __name__ == "__main__":
    unittest.main()
