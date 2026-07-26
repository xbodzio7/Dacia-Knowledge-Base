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
IMPORTER = ROOT / "tools" / "import_jogger_chassis_20260726.py"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
SOURCE = "src_pl_jogger_brochure_20251217"
SOURCE_PATH = ROOT / "PDF" / "Broszury" / "DACIA JOGGER broszura 20251217.pdf"
SOURCE_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
ATTRIBUTES = {
    "turning_circle_between_kerbs",
    "standard_tyre_specification",
    "front_suspension",
    "rear_suspension",
}
MASS_ATTRIBUTES = {
    "kerb_weight",
    "minimum_kerb_weight",
    "maximum_kerb_weight",
    "gross_vehicle_weight",
    "gross_train_weight",
    "maximum_payload",
    "payload",
}
CONFIGURATIONS = {
    "jogger_essential_5seat_ecog120_manual",
    "jogger_expression_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "jogger_expression_5seat_tce110_manual",
    "jogger_extreme_5seat_tce110_manual",
    "jogger_journey_5seat_tce110_manual",
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_essential_7seat_ecog120_manual",
    "jogger_expression_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_automatic",
    "jogger_journey_7seat_ecog120_automatic",
    "jogger_expression_7seat_tce110_manual",
    "jogger_extreme_7seat_tce110_manual",
    "jogger_journey_7seat_tce110_manual",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
}
REPORTING_SPECS = (
    "jogger_ecog120_manual_completeness.json",
    "jogger_ecog120_automatic_completeness.json",
    "jogger_tce110_manual_completeness.json",
    "jogger_hybrid155_automatic_completeness.json",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerChassisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = rows(MASTER / "configuration_attribute_values.csv")
        cls.package = [row for row in cls.values if 2480 <= int(row["id"]) <= 2567]
        cls.configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}

    def test_exact_counts_ids_scope_and_distribution(self) -> None:
        self.assertEqual(len(self.package), 88)
        self.assertEqual([int(row["id"]) for row in self.package], list(range(2480, 2568)))
        self.assertEqual({row["configuration_code"] for row in self.package}, CONFIGURATIONS)
        self.assertEqual(Counter(row["attribute_code"] for row in self.package), Counter({code: 22 for code in ATTRIBUTES}))
        self.assertEqual({row["source_code"] for row in self.package}, {SOURCE})
        self.assertEqual({row["observation_date"] for row in self.package}, {"2025-12-17"})
        self.assertEqual({row["fuel_type_code"] for row in self.package}, {""})
        self.assertEqual({row["gear_number"] for row in self.package}, {""})

    def test_model_wide_values_are_projected_to_all_exact_configurations(self) -> None:
        by_attribute = {
            attribute: {row["value"] for row in self.package if row["attribute_code"] == attribute}
            for attribute in ATTRIBUTES
        }
        self.assertEqual(by_attribute["turning_circle_between_kerbs"], {"11.39"})
        self.assertEqual(by_attribute["standard_tyre_specification"], {"205/60 R16 92H"})
        self.assertEqual(len(by_attribute["front_suspension"]), 1)
        self.assertEqual(len(by_attribute["rear_suspension"]), 1)
        self.assertIn("McPherson", next(iter(by_attribute["front_suspension"])))
        self.assertIn("Belka skrętna", next(iter(by_attribute["rear_suspension"])))
        for attribute in ATTRIBUTES:
            self.assertEqual(
                {row["configuration_code"] for row in self.package if row["attribute_code"] == attribute},
                CONFIGURATIONS,
            )

    def test_turning_measurement_basis_is_explicit(self) -> None:
        turning = [row for row in self.package if row["attribute_code"] == "turning_circle_between_kerbs"]
        self.assertEqual(len(turning), 22)
        self.assertTrue(all("między krawężnikami" in row["notes"] for row in turning))
        self.assertFalse(any(row["attribute_code"] == "turning_circle" for row in self.package))

    def test_mass_table_conflict_remains_unimported(self) -> None:
        self.assertFalse({row["attribute_code"] for row in self.package} & MASS_ATTRIBUTES)
        self.assertFalse(any(
            row["source_code"] == SOURCE
            and row["observation_date"] == "2025-12-17"
            and row["attribute_code"] in MASS_ATTRIBUTES
            for row in self.values
        ))
        review = json.loads((ROOT / "data" / "reporting" / "official_brochure_technical_gap_review.json").read_text(encoding="utf-8"))
        conflict = next(item for item in review["classifications"] if item["code"] == "jogger_mass_table_label_conflict")
        self.assertEqual(conflict["status"], "ambiguous_source_evidence")
        self.assertIn("no semantic reassignment", conflict["reason"])

    def test_source_hash_relationships_and_importer_contract(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(), SOURCE_SHA)
        relationships = {
            (row["source_code"], row["configuration_code"], row["relationship"])
            for row in rows(MASTER / "source_configurations.csv")
        }
        for configuration in CONFIGURATIONS:
            self.assertIn((SOURCE, configuration, "brochure_technical_data_for"), relationships)
        completed = subprocess.run(
            [sys.executable, str(IMPORTER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("PASS: Jogger brochure chassis observations", completed.stdout)

    def test_reporting_scopes_include_four_chassis_slots(self) -> None:
        required = {(code, "") for code in ATTRIBUTES}
        for name in REPORTING_SPECS:
            payload = json.loads((ROOT / "data" / "reporting" / name).read_text(encoding="utf-8"))
            slots = {(item["attribute_code"], item.get("fuel_type_code", "")) for item in payload["technical_slots"]}
            self.assertTrue(required <= slots, name)

    def test_model_receipt_closes_all_five_chassis_resolutions(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODEL_VERIFIER), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        model = json.loads((ROOT / "data" / "reporting" / "brochure_chassis_measurement_context_model.json").read_text(encoding="utf-8"))
        self.assertEqual({item["status"] for item in model["source_resolutions"]}, {"imported"})
        jogger = next(item for item in model["source_resolutions"] if item["classification_code"] == "jogger_chassis_candidate_and_modeling")
        self.assertEqual(jogger["blocked_related_classification"], "jogger_mass_table_label_conflict")
        self.assertEqual(model["next_package"]["name"], "Brochure Chassis Modeling Closure Review")

    def test_project_state_matches_completed_package(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Jogger Chassis Observation Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Brochure Chassis Modeling Closure Review")
        self.assertEqual(state["baseline"]["tests"], 907)
        self.assertEqual(state["baseline"]["rows"], 9306)
        self.assertEqual(state["baseline"]["configuration_values"], 2567)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertEqual(state["baseline"]["attributes"], 385)


if __name__ == "__main__":
    unittest.main()
