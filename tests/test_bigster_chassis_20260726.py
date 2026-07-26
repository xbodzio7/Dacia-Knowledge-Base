from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
IMPORTER = ROOT / "tools" / "import_bigster_chassis_20260726.py"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
SOURCE = "src_pl_bigster_brochure_20251210"
SOURCE_PATH = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SOURCE_SHA = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
ATTRIBUTES = {
    "turning_circle_between_kerbs",
    "maximum_kerb_weight",
    "steering_type",
    "front_brake_type",
    "rear_brake_type",
    "standard_tyre_specification",
}
CONFIGURATIONS = {
    "bigster_essential_mildhybrid140_4x2_manual",
    "bigster_expression_mildhybrid140_4x2_manual",
    "bigster_extreme_mildhybrid140_4x2_manual",
    "bigster_journey_mildhybrid140_4x2_manual",
    "bigster_essential_mildhybridg140_4x2_manual",
    "bigster_expression_mildhybridg140_4x2_manual",
    "bigster_extreme_mildhybridg140_4x2_manual",
    "bigster_journey_mildhybridg140_4x2_manual",
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}
REPORTING_SPECS = (
    "bigster_mildhybrid140_4x2_manual_completeness.json",
    "bigster_mildhybridg140_4x2_manual_completeness.json",
    "bigster_hybrid155_4x2_automatic_completeness.json",
    "bigster_hybridg150_4x4_automatic_completeness.json",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterChassisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.package = [row for row in cls.values if 2336 <= int(row["id"]) <= 2419]

    def test_exact_counts_ids_scope_and_distribution(self) -> None:
        self.assertEqual(len(self.package), 84)
        self.assertEqual([int(row["id"]) for row in self.package], list(range(2336, 2420)))
        self.assertEqual({row["configuration_code"] for row in self.package}, CONFIGURATIONS)
        self.assertEqual(Counter(row["attribute_code"] for row in self.package), Counter({code: 14 for code in ATTRIBUTES}))
        self.assertEqual({row["source_code"] for row in self.package}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in self.package}, {"2025-12-10"})
        self.assertEqual({row["fuel_type_code"] for row in self.package}, {""})
        self.assertEqual({row["gear_number"] for row in self.package}, {""})

    def test_common_chassis_values_are_projected_without_losing_basis(self) -> None:
        turning = [row for row in self.package if row["attribute_code"] == "turning_circle_between_kerbs"]
        steering = [row for row in self.package if row["attribute_code"] == "steering_type"]
        front = [row for row in self.package if row["attribute_code"] == "front_brake_type"]
        self.assertEqual({row["value"] for row in turning}, {"10.97"})
        self.assertTrue(all("między krawężnikami" in row["notes"] for row in turning))
        self.assertEqual({row["value"] for row in steering}, {"Ze wspomaganiem elektrycznym"})
        self.assertEqual({row["value"] for row in front}, {"Tarcze wentylowane Φ296x26"})
        self.assertFalse(any(row["attribute_code"] == "turning_circle" for row in self.package))

    def test_maximum_kerb_weight_preserves_four_powertrain_columns(self) -> None:
        configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}
        grouped = {
            configurations[row["configuration_code"]]["powertrain_label"]: row["value"]
            for row in self.package
            if row["attribute_code"] == "maximum_kerb_weight"
        }
        self.assertEqual(grouped, {
            "mild hybrid-G 140 4x2": "1478",
            "mild hybrid 140 4x2": "1439",
            "hybrid-G 150 4x4": "1515",
            "hybrid 155 4x2": "1487",
        })

    def test_rear_brake_and_tyre_texts_preserve_powertrain_boundaries(self) -> None:
        configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}
        rear = {
            configurations[row["configuration_code"]]["powertrain_label"]: row["value"]
            for row in self.package
            if row["attribute_code"] == "rear_brake_type"
        }
        self.assertEqual(rear["hybrid-G 150 4x4"], "Tarcza pełna Ø280x9,6")
        for powertrain in {"mild hybrid-G 140 4x2", "mild hybrid 140 4x2", "hybrid 155 4x2"}:
            self.assertIn("Bęben 9”", rear[powertrain])
            self.assertIn("tarcza pełna Φ280x9,6", rear[powertrain])
        tyres = {
            configurations[row["configuration_code"]]["powertrain_label"]: row["value"]
            for row in self.package
            if row["attribute_code"] == "standard_tyre_specification"
        }
        self.assertEqual(len(tyres), 4)
        self.assertIn("EC31", tyres["mild hybrid 140 4x2"])
        self.assertIn("EC32", tyres["mild hybrid-G 140 4x2"])
        self.assertIn("EC33", tyres["hybrid 155 4x2"])
        self.assertIn("3PMSF", tyres["hybrid-G 150 4x4"])

    def test_source_hash_relationships_and_importer_contract(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(), SOURCE_SHA)
        relationships = {
            (row["source_code"], row["configuration_code"], row["relationship"])
            for row in rows(MASTER / "source_configurations.csv")
        }
        for configuration in CONFIGURATIONS:
            self.assertIn((SOURCE, configuration, "brochure_technical_data_for"), relationships)
        completed = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"], cwd=ROOT, text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Bigster brochure chassis observations", completed.stdout)

    def test_reporting_scopes_include_six_chassis_slots(self) -> None:
        required = {(code, "") for code in ATTRIBUTES}
        for name in REPORTING_SPECS:
            payload = json.loads((ROOT / "data" / "reporting" / name).read_text(encoding="utf-8"))
            slots = {(item["attribute_code"], item.get("fuel_type_code", "")) for item in payload["technical_slots"]}
            self.assertTrue(required <= slots, name)

    def test_model_receipt_advances_to_duster(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODEL_VERIFIER), "--check"], cwd=ROOT, text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        model = json.loads((ROOT / "data" / "reporting" / "brochure_chassis_measurement_context_model.json").read_text(encoding="utf-8"))
        statuses = {item["classification_code"]: item["status"] for item in model["source_resolutions"]}
        self.assertEqual(statuses["bigster_chassis_measurement_modeling"], "imported")
        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")

    def test_project_state_matches_completed_package(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 891)
        self.assertGreaterEqual(state["baseline"]["rows"], 9148)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2419)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
