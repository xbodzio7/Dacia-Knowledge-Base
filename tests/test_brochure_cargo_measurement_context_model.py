from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


class BrochureCargoMeasurementContextModelTests(unittest.TestCase):
    def test_complete_model_contract(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/model_brochure_cargo_measurement_context_20260725.py",
                "--check",
            ],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(
            "PASS: brochure cargo measurement-context model contract",
            completed.stdout,
        )

        state = json.loads(
            (REPOSITORY / "project" / "state.json").read_text(encoding="utf-8")
        )
        self.assertTrue(state["phase"])
        self.assertGreaterEqual(state["baseline"]["tests"], 766)
        self.assertGreaterEqual(state["baseline"]["rows"], 8145)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertTrue(state["next_package"]["name"])

        report = json.loads(
            (
                REPOSITORY
                / "data"
                / "reporting"
                / "brochure_cargo_measurement_context_model.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(report["canonical_attribute_code"], "boot_capacity")
        self.assertEqual(
            report["context_relation"]["file"],
            "data/master/configuration_cargo_volume_contexts.csv",
        )
        self.assertEqual(
            report["context_relation"]["cardinality"],
            "zero_or_one_context_per_configuration_attribute_value",
        )
        self.assertIn("measurement_basis_code", report["context_relation"]["required_fields"])
        self.assertIn("compartment_code", report["context_relation"]["required_fields"])
        self.assertEqual(
            report["inherited_from_configuration"],
            ["passenger_layout", "number_of_seats", "drive_type"],
        )
        self.assertFalse(report["legacy_policy"]["migrate_existing_values"])
        self.assertEqual(report["deferred"], ["gear_specific_elasticity_context"])


if __name__ == "__main__":
    unittest.main()
