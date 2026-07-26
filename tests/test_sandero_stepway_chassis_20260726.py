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
IMPORTER = ROOT / "tools" / "import_sandero_stepway_chassis_20260726.py"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
ATTRIBUTES = {
    "turning_circle_between_kerbs",
    "maximum_kerb_weight",
    "standard_tyre_specification",
    "front_suspension",
    "rear_suspension",
}
CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_automatic",
}
SOURCES = {
    "src_pl_sandero_brochure_20260202": (
        ROOT / "PDF" / "Broszury" / "DACIA SANDERO broszura 20260202.pdf",
        "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
    ),
    "src_pl_sandero_stepway_brochure_20260202": (
        ROOT / "PDF" / "Broszury" / "DACIA SANDERO STEPWAY broszura 20260202.pdf",
        "800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48",
    ),
}
REPORTING_SPECS = (
    "configuration_completeness.json",
    "sandero_ecog120_manual_completeness.json",
    "sandero_ecog120_automatic_completeness.json",
    "sandero_stepway_ecog120_automatic_completeness.json",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SanderoStepwayChassisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.package = [row for row in cls.values if 2291 <= int(row["id"]) <= 2335]

    def test_exact_counts_ids_configurations_attributes_and_sources(self) -> None:
        self.assertEqual(len(self.package), 45)
        self.assertEqual([int(row["id"]) for row in self.package], list(range(2291, 2336)))
        self.assertEqual({row["configuration_code"] for row in self.package}, CONFIGURATIONS)
        self.assertEqual(Counter(row["attribute_code"] for row in self.package), Counter({code: 9 for code in ATTRIBUTES}))
        self.assertEqual(Counter(row["source_code"] for row in self.package), Counter({
            "src_pl_sandero_brochure_20260202": 20,
            "src_pl_sandero_stepway_brochure_20260202": 25,
        }))
        self.assertEqual({row["observation_date"] for row in self.package}, {"2026-02-02"})
        self.assertEqual({row["fuel_type_code"] for row in self.package}, {""})
        self.assertEqual({row["gear_number"] for row in self.package}, {""})

    def test_turning_diameter_uses_explicit_between_kerbs_attribute(self) -> None:
        turning = [row for row in self.package if row["attribute_code"] == "turning_circle_between_kerbs"]
        self.assertEqual(len(turning), 9)
        self.assertEqual({row["value"] for row in turning}, {"10.64"})
        self.assertTrue(all("między krawężnikami" in row["notes"] for row in turning))
        self.assertFalse(any(row["attribute_code"] == "turning_circle" for row in self.package))

    def test_maximum_kerb_weight_preserves_powertrain_and_model_values(self) -> None:
        actual = {
            row["configuration_code"]: row["value"]
            for row in self.package
            if row["attribute_code"] == "maximum_kerb_weight"
        }
        expected = {
            "sandero_iii_expression_ecog120_manual": "1209",
            "sandero_iii_journey_ecog120_manual": "1209",
            "sandero_iii_expression_ecog120_automatic": "1232",
            "sandero_iii_journey_ecog120_automatic": "1232",
            "sandero_stepway_iii_essential_ecog120_manual": "1225",
            "sandero_stepway_iii_expression_ecog120_manual": "1225",
            "sandero_stepway_iii_extreme_ecog120_manual": "1225",
            "sandero_stepway_iii_expression_ecog120_automatic": "1249",
            "sandero_stepway_iii_extreme_ecog120_automatic": "1249",
        }
        self.assertEqual(actual, expected)

    def test_model_wide_source_text_is_preserved_without_decomposition(self) -> None:
        tyres = {
            ("stepway" if row["configuration_code"].startswith("sandero_stepway_") else "sandero", row["value"])
            for row in self.package
            if row["attribute_code"] == "standard_tyre_specification"
        }
        self.assertEqual(tyres, {
            ("sandero", "185/65 R15 88H - 195/55 R16 87H"),
            ("stepway", "205/60 R16 92H"),
        })
        front = {row["value"] for row in self.package if row["attribute_code"] == "front_suspension"}
        rear = {row["value"] for row in self.package if row["attribute_code"] == "rear_suspension"}
        self.assertEqual(len(front), 1)
        self.assertEqual(len(rear), 1)
        self.assertIn("McPherson", next(iter(front)))
        self.assertIn("Belka skrętna", next(iter(rear)))

    def test_later_configuration_pdf_observations_remain_unchanged(self) -> None:
        later = [
            row for row in self.values
            if row["observation_date"] == "2026-06-26"
            and row["configuration_code"] in CONFIGURATIONS
            and row["attribute_code"] in {"turning_circle", "standard_tyre_specification"}
        ]
        self.assertEqual(Counter(row["attribute_code"] for row in later), Counter({"turning_circle": 7, "standard_tyre_specification": 7}))
        self.assertEqual({row["value"] for row in later if row["attribute_code"] == "turning_circle"}, {"10.64"})
        self.assertEqual({row["value"] for row in later if row["attribute_code"] == "standard_tyre_specification"}, {"205/60 R16 92H"})

    def test_source_hashes_relationships_and_importer_contract(self) -> None:
        for _, (path, expected_hash) in SOURCES.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected_hash)
        relationships = {
            (row["source_code"], row["configuration_code"], row["relationship"])
            for row in rows(MASTER / "source_configurations.csv")
        }
        for row in self.package:
            self.assertIn((row["source_code"], row["configuration_code"], "brochure_technical_data_for"), relationships)
        completed = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Sandero and Stepway brochure chassis observations", completed.stdout)

    def test_reporting_scopes_include_four_new_chassis_slots(self) -> None:
        required = {
            ("turning_circle_between_kerbs", ""),
            ("maximum_kerb_weight", ""),
            ("front_suspension", ""),
            ("rear_suspension", ""),
        }
        for name in REPORTING_SPECS:
            payload = json.loads((ROOT / "data" / "reporting" / name).read_text(encoding="utf-8"))
            slots = {(item["attribute_code"], item.get("fuel_type_code", "")) for item in payload["technical_slots"]}
            self.assertTrue(required <= slots, name)

    def test_model_receipt_and_project_state_advance(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODEL_VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        model = json.loads((ROOT / "data" / "reporting" / "brochure_chassis_measurement_context_model.json").read_text(encoding="utf-8"))
        statuses = {item["classification_code"]: item["status"] for item in model["source_resolutions"]}
        self.assertEqual(statuses["sandero_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(statuses["stepway_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")

        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 883)
        self.assertGreaterEqual(state["baseline"]["rows"], 9064)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2335)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
