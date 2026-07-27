from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "brochure_chassis_measurement_context_model.json"
VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
NEW_CODES = {
    "turning_circle_between_kerbs",
    "turning_circle_wheel_track",
    "maximum_kerb_weight",
    "payload",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BrochureChassisMeasurementContextModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.attributes = {row["code"]: row for row in rows(MASTER / "attributes.csv")}

    def test_four_new_attributes_have_exact_ids_and_contracts(self) -> None:
        expected = {
            "turning_circle_between_kerbs": ("389", "Performance", "decimal", "m"),
            "turning_circle_wheel_track": ("390", "Performance", "decimal", "m"),
            "maximum_kerb_weight": ("391", "Weights", "integer", "kg"),
            "payload": ("392", "Weights", "integer", "kg"),
        }
        self.assertEqual(set(expected), NEW_CODES)
        for code, contract in expected.items():
            row = self.attributes[code]
            self.assertEqual((row["id"], row["category"], row["data_type"], row["unit"]), contract)
            self.assertEqual(row["status"], "active")

    def test_turning_measurement_bases_are_separate(self) -> None:
        resolutions = {item["classification_code"]: item for item in self.report["source_resolutions"]}
        self.assertEqual(
            resolutions["duster_chassis_mass_and_payload_modeling"]["turning_attribute"],
            "turning_circle_wheel_track",
        )
        for code, item in resolutions.items():
            if code != "duster_chassis_mass_and_payload_modeling":
                self.assertEqual(item["turning_attribute"], "turning_circle_between_kerbs")
        self.assertIn("turning_circle", self.attributes)

    def test_payload_range_semantics_reuse_existing_range_table(self) -> None:
        payload_rule = next(item for item in self.report["rules"] if item["code"] == "payload_preserves_scalar_or_range")
        self.assertIn("configuration_attribute_values", payload_rule["decision"])
        self.assertIn("configuration_attribute_value_ranges", payload_rule["decision"])
        self.assertIn("maximum_payload", payload_rule["decision"])

    def test_compound_specs_map_to_existing_string_attributes(self) -> None:
        mappings = {item["attribute_code"] for item in self.report["existing_specification_mappings"]}
        expected = {
            "standard_tyre_specification",
            "front_suspension",
            "rear_suspension",
            "front_brake_type",
            "rear_brake_type",
            "steering_type",
        }
        self.assertEqual(mappings, expected)
        for code in expected:
            self.assertEqual(self.attributes[code]["data_type"], "string")
            self.assertEqual(self.attributes[code]["status"], "active")

    def test_model_covers_all_five_deferred_classifications(self) -> None:
        expected = {
            "bigster_chassis_measurement_modeling",
            "jogger_chassis_candidate_and_modeling",
            "sandero_chassis_and_maximum_mass_modeling",
            "stepway_chassis_and_maximum_mass_modeling",
            "duster_chassis_mass_and_payload_modeling",
        }
        self.assertEqual(set(self.report["scope"]["classification_codes"]), expected)
        self.assertEqual(
            {item["classification_code"] for item in self.report["source_resolutions"]},
            expected,
        )
        statuses = {
            item["classification_code"]: item["status"]
            for item in self.report["source_resolutions"]
        }
        self.assertEqual(statuses["bigster_chassis_measurement_modeling"], "imported")
        self.assertEqual(statuses["sandero_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(statuses["stepway_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(statuses["duster_chassis_mass_and_payload_modeling"], "imported")
        self.assertEqual(statuses["jogger_chassis_candidate_and_modeling"], "imported")

    def test_jogger_ambiguous_mass_labels_remain_blocked(self) -> None:
        jogger = next(
            item for item in self.report["source_resolutions"]
            if item["classification_code"] == "jogger_chassis_candidate_and_modeling"
        )
        self.assertEqual(jogger["blocked_related_classification"], "jogger_mass_table_label_conflict")
        rule = next(item for item in self.report["rules"] if item["code"] == "ambiguous_labels_are_not_reassigned")
        self.assertIn("not semantically reassigned", rule["decision"])

    def test_follow_up_imports_respect_modeled_attributes(self) -> None:
        scalar = [row for row in rows(MASTER / "configuration_attribute_values.csv") if row["attribute_code"] in NEW_CODES]
        ranges = [row for row in rows(MASTER / "configuration_attribute_value_ranges.csv") if row["attribute_code"] in NEW_CODES]
        self.assertEqual(len(scalar), 100)
        self.assertEqual(
            {row["attribute_code"] for row in scalar},
            {"turning_circle_between_kerbs", "turning_circle_wheel_track", "maximum_kerb_weight"},
        )
        self.assertEqual(
            {row["observation_date"] for row in scalar},
            {"2025-10-20", "2025-12-10", "2025-12-17", "2026-02-02"},
        )
        self.assertEqual(len(ranges), 10)
        self.assertEqual({row["attribute_code"] for row in ranges}, {"payload"})
        self.assertEqual({row["observation_date"] for row in ranges}, {"2025-10-20"})

    def test_verifier_and_project_state_are_complete(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: brochure chassis measurement context model", completed.stdout)

        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 875)
        self.assertGreaterEqual(state["baseline"]["rows"], 9019)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2290)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 234)


if __name__ == "__main__":
    unittest.main()
