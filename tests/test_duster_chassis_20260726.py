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
IMPORTER = ROOT / "tools" / "import_duster_chassis_20260726.py"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
SOURCE = "src_pl_duster_mini_brochure_20251020"
SOURCE_PATH = ROOT / "PDF" / "Broszury" / "DACIA DUSTER mini broszura 20251020.pdf"
SOURCE_SHA = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
SCALAR_ATTRIBUTES = {
    "turning_circle_wheel_track",
    "maximum_kerb_weight",
    "steering_type",
    "front_brake_type",
    "rear_brake_type",
    "standard_tyre_specification",
}
CONFIGURATIONS = {
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
    "duster_iii_expression_mildhybrid140_4x2_manual",
    "duster_iii_extreme_mildhybrid140_4x2_manual",
    "duster_iii_journey_mildhybrid140_4x2_manual",
    "duster_iii_expression_hybrid155_4x2_automatic",
    "duster_iii_extreme_hybrid155_4x2_automatic",
    "duster_iii_journey_hybrid155_4x2_automatic",
}
AUTOMATIC_ECOG = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
REPORTING_SPECS = (
    "duster_ecog120_completeness.json",
    "duster_mildhybrid140_4x2_completeness.json",
    "duster_hybrid155_completeness.json",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterChassisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
        cls.scalar_package = [row for row in cls.values if 2420 <= int(row["id"]) <= 2479]
        cls.range_package = [row for row in cls.ranges if 235 <= int(row["id"]) <= 244]
        cls.configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}

    def test_exact_scalar_and_range_counts_ids_scope_and_sources(self) -> None:
        self.assertEqual(len(self.scalar_package), 60)
        self.assertEqual([int(row["id"]) for row in self.scalar_package], list(range(2420, 2480)))
        self.assertEqual({row["configuration_code"] for row in self.scalar_package}, CONFIGURATIONS)
        self.assertEqual(Counter(row["attribute_code"] for row in self.scalar_package), Counter({code: 10 for code in SCALAR_ATTRIBUTES}))
        self.assertEqual({row["source_code"] for row in self.scalar_package}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in self.scalar_package}, {"2025-10-20"})

        self.assertEqual(len(self.range_package), 10)
        self.assertEqual([int(row["id"]) for row in self.range_package], list(range(235, 245)))
        self.assertEqual({row["configuration_code"] for row in self.range_package}, CONFIGURATIONS)
        self.assertEqual({row["attribute_code"] for row in self.range_package}, {"payload"})
        self.assertEqual({row["source_code"] for row in self.range_package}, {SOURCE})
        self.assertEqual({row["lower_inclusive"] for row in self.range_package}, {"true"})
        self.assertEqual({row["upper_inclusive"] for row in self.range_package}, {"true"})

    def test_wheel_track_turning_basis_and_common_steering_are_explicit(self) -> None:
        turning = [row for row in self.scalar_package if row["attribute_code"] == "turning_circle_wheel_track"]
        steering = [row for row in self.scalar_package if row["attribute_code"] == "steering_type"]
        self.assertEqual({row["value"] for row in turning}, {"10.96"})
        self.assertTrue(all("wg śladu kół" in row["notes"] for row in turning))
        self.assertEqual({row["value"] for row in steering}, {"Elektryczne wspomaganie układu kierowniczego"})
        self.assertFalse(any(row["attribute_code"] == "turning_circle" for row in self.scalar_package))

    def test_powertrain_specific_mass_brakes_and_tyres_are_preserved(self) -> None:
        def grouped(attribute: str) -> dict[str, str]:
            return {
                self.configurations[row["configuration_code"]]["powertrain_label"]: row["value"]
                for row in self.scalar_package
                if row["attribute_code"] == attribute
            }

        self.assertEqual(grouped("maximum_kerb_weight"), {
            "Eco-G 120 4x2": "1350",
            "mild hybrid 140 4x2": "1376",
            "hybrid 155 4x2": "1454",
        })
        self.assertEqual(grouped("front_brake_type"), {
            "Eco-G 120 4x2": "Tarczowe wentylowane Φ280x24",
            "mild hybrid 140 4x2": "Tarczowe wentylowane Φ280x24",
            "hybrid 155 4x2": "Tarczowe wentylowane Φ296x26",
        })
        rear = grouped("rear_brake_type")
        self.assertEqual(len(set(rear.values())), 1)
        self.assertIn("Bębnowe 9\"", next(iter(rear.values())))
        tyres = grouped("standard_tyre_specification")
        self.assertEqual(tyres["Eco-G 120 4x2"], "215/70/R16; 215/65/R17; 215/60/R18; letnie")
        self.assertEqual(tyres["mild hybrid 140 4x2"], "215/70/R16; 215/65/R17; 215/60/R18; letnie")
        self.assertEqual(tyres["hybrid 155 4x2"], "215/65/R17; 215/60/R18; letnie")

    def test_payload_ranges_preserve_numeric_intervals_and_source_order(self) -> None:
        grouped = {
            self.configurations[row["configuration_code"]]["powertrain_label"]: (
                row["minimum_value"], row["maximum_value"]
            )
            for row in self.range_package
        }
        self.assertEqual(grouped, {
            "Eco-G 120 4x2": ("455", "487"),
            "mild hybrid 140 4x2": ("454", "528"),
            "hybrid 155 4x2": ("451", "525"),
        })
        self.assertTrue(all("Maks./min. ładowność" in row["notes"] for row in self.range_package))
        self.assertTrue(all("without semantic reassignment" in row["notes"] for row in self.range_package))
        self.assertFalse(any(row["attribute_code"] == "maximum_payload" for row in self.range_package))

    def test_automatic_ecog_and_unrepresented_powertrains_remain_excluded(self) -> None:
        self.assertFalse({row["configuration_code"] for row in self.scalar_package} & AUTOMATIC_ECOG)
        self.assertFalse({row["configuration_code"] for row in self.range_package} & AUTOMATIC_ECOG)
        self.assertEqual(
            {
                row["configuration_code"] for row in self.values
                if row["configuration_code"] in AUTOMATIC_ECOG
                and row["attribute_code"] == "turning_circle"
                and row["observation_date"] == "2026-07-25"
            },
            AUTOMATIC_ECOG,
        )
        self.assertEqual(
            {
                row["configuration_code"] for row in self.ranges
                if row["configuration_code"] in AUTOMATIC_ECOG
                and row["attribute_code"] == "maximum_payload"
                and row["observation_date"] == "2026-07-25"
            },
            AUTOMATIC_ECOG,
        )
        selected_powertrains = {self.configurations[code]["powertrain_label"] for code in CONFIGURATIONS}
        self.assertEqual(selected_powertrains, {"Eco-G 120 4x2", "mild hybrid 140 4x2", "hybrid 155 4x2"})

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
        self.assertIn("PASS: Duster brochure chassis observations", completed.stdout)

    def test_reporting_scopes_include_seven_context_preserving_slots(self) -> None:
        required = {(code, "") for code in (*SCALAR_ATTRIBUTES, "payload")}
        for name in REPORTING_SPECS:
            payload = json.loads((ROOT / "data" / "reporting" / name).read_text(encoding="utf-8"))
            slots = {(item["attribute_code"], item.get("fuel_type_code", "")) for item in payload["technical_slots"]}
            self.assertTrue(required <= slots, name)

    def test_model_receipt_and_project_state_advance_to_jogger(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODEL_VERIFIER), "--check"], cwd=ROOT, text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        model = json.loads((ROOT / "data" / "reporting" / "brochure_chassis_measurement_context_model.json").read_text(encoding="utf-8"))
        statuses = {item["classification_code"]: item["status"] for item in model["source_resolutions"]}
        self.assertEqual(statuses["duster_chassis_mass_and_payload_modeling"], "imported")
        self.assertEqual(statuses["jogger_chassis_candidate_and_modeling"], "model_defined_import_pending")
        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")

        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Duster Chassis Observation Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Jogger Chassis Observation Import")
        self.assertEqual(state["baseline"]["tests"], 899)
        self.assertEqual(state["baseline"]["rows"], 9218)
        self.assertEqual(state["baseline"]["configuration_values"], 2479)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
