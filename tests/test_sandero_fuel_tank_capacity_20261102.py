from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "imports" / "configuration_values" / "sandero-ecog120-fuel-tank-capacity-20261102.json"
MASTER = ROOT / "data" / "master"

sys.path.insert(0, str(ROOT / "tools"))
import import_configuration_values as importer  # noqa: E402


class SanderoEcoGFuelTankCapacity20261102Tests(unittest.TestCase):
    def test_cennik_import_is_exact_and_source_verified(self) -> None:
        spec = importer.load_spec(SPEC)
        plan = importer.verify_import(ROOT, spec)
        self.assertEqual(len(spec.rows), 18)
        self.assertEqual(len(plan.existing_rows), 18)
        self.assertEqual(plan.missing_rows, ())
        self.assertEqual(spec.source_page, 5)
        self.assertEqual(spec.observation_date, "2026-11-02")
        self.assertEqual(spec.attribute_code, "fuel_tank_capacity")
        self.assertEqual(
            {row.fuel_type_code for row in spec.rows},
            {"petrol", "lpg"},
        )
        self.assertEqual(
            {row.value for row in spec.rows if row.fuel_type_code == "petrol"},
            {"50"},
        )
        self.assertEqual(
            {row.value for row in spec.rows if row.fuel_type_code == "lpg"},
            {"40"},
        )
        self.assertEqual(
            len({row.configuration_code for row in spec.rows}),
            9,
        )

        historical_specs = (
            (
                "configuration_completeness.json",
                "configuration_gap_evidence.json",
            ),
            (
                "sandero_ecog120_manual_completeness.json",
                "sandero_ecog120_manual_gap_evidence.json",
            ),
            (
                "sandero_ecog120_automatic_completeness.json",
                "sandero_ecog120_automatic_gap_evidence.json",
            ),
            (
                "sandero_stepway_ecog120_automatic_completeness.json",
                "sandero_stepway_ecog120_automatic_gap_evidence.json",
            ),
        )
        for completeness_name, evidence_name in historical_specs:
            with self.subTest(completeness_spec=completeness_name):
                completeness = json.loads(
                    (ROOT / "data" / "reporting" / completeness_name).read_text(
                        encoding="utf-8"
                    )
                )
                evidence = json.loads(
                    (ROOT / "data" / "reporting" / evidence_name).read_text(
                        encoding="utf-8"
                    )
                )
                capacity_slots = [
                    row
                    for row in completeness["technical_slots"]
                    if row["attribute_code"] == "fuel_tank_capacity"
                ]
                historical_contexts = {
                    row["fuel_type_code"]
                    for row in capacity_slots
                    if not row.get("effective_from")
                    or row["effective_from"] <= evidence["as_of"]
                }
                self.assertEqual(historical_contexts, {""})
                dated_contexts = {
                    (row["fuel_type_code"], row["effective_from"])
                    for row in capacity_slots
                    if row.get("effective_from")
                }
                if completeness_name == "configuration_completeness.json":
                    self.assertEqual(
                        dated_contexts,
                        {
                            ("lpg", spec.observation_date),
                            ("petrol", spec.observation_date),
                        },
                    )
                else:
                    self.assertEqual(dated_contexts, set())
                self.assertLess(evidence["as_of"], spec.observation_date)

    def test_import_preserves_older_undifferentiated_observations(self) -> None:
        with (MASTER / "configuration_attribute_values.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        configs = {
            row.configuration_code
            for row in importer.load_spec(SPEC).rows
        }
        older = [
            row for row in rows
            if row["configuration_code"] in configs
            and row["attribute_code"] == "fuel_tank_capacity"
            and row["fuel_type_code"] == ""
            and row["observation_date"] < "2026-11-02"
        ]
        self.assertEqual(len(older), 9)
        self.assertEqual({row["value"] for row in older}, {"50"})
        current = [
            row for row in rows
            if row["source_code"] == "src_pl_sandero_stepway_price_my26_20261102"
            and row["attribute_code"] == "fuel_tank_capacity"
        ]
        self.assertEqual(len(current), 18)
        self.assertFalse(
            any(
                row["attribute_code"] in {
                    "lpg_vessel_capacity_total",
                    "lpg_vessel_filling_capacity",
                }
                and row["source_code"] == "src_pl_sandero_stepway_price_my26_20261102"
                for row in rows
            )
        )
        self.assertTrue(
            all(
                "does not distinguish total LPG vessel capacity from filling capacity"
                in row["notes"]
                for row in current
            )
        )


if __name__ == "__main__":
    unittest.main()
