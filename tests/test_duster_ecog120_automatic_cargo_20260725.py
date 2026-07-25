from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
SOURCE_CODE = "src_pl_duster_price_my26_20260703"
SOURCE_SHA256 = "40bb4f3db9019c500fcb4c759f5ad395aa3b35a68bb22aa74f031fefe09727f2"
CONFIGURATION_CODES = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
ATTRIBUTE_VALUES = {
    "cargo_volume_without_spare_wheel_iso3832": "439",
    "maximum_cargo_volume_iso3832": "1373",
}
SPEC_PATHS = (
    REPOSITORY
    / "data"
    / "imports"
    / "configuration_values"
    / "duster-page6-cargo-volume-without-spare-wheel-iso3832-20260703.json",
    REPOSITORY
    / "data"
    / "imports"
    / "configuration_values"
    / "duster-page6-maximum-cargo-volume-iso3832-20260703.json",
)

sys.path.insert(0, str(REPOSITORY / "tools"))
import configuration_completeness  # noqa: E402
import import_configuration_values as value_importer  # noqa: E402


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterEcoG120AutomaticCargo20260725Tests(unittest.TestCase):
    def test_registered_source_identity_and_exact_configuration_links(self) -> None:
        source = next(row for row in rows("sources.csv") if row["code"] == SOURCE_CODE)
        source_path = REPOSITORY / source["file_path"]
        self.assertEqual(source["market"], "PL")
        self.assertEqual(source["document_date"], "2026-07-03")
        self.assertEqual(source["sha256"], SOURCE_SHA256)
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(), SOURCE_SHA256)
        relationships = [
            row
            for row in rows("source_configurations.csv")
            if row["source_code"] == SOURCE_CODE
            and row["configuration_code"] in CONFIGURATION_CODES
            and row["relationship"] == "catalogue_technical_data_for"
        ]
        self.assertEqual(len(relationships), 3)
        self.assertEqual(
            {row["configuration_code"] for row in relationships},
            CONFIGURATION_CODES,
        )

    def test_two_declarative_specs_match_master_exactly(self) -> None:
        specs = [value_importer.load_spec(path) for path in SPEC_PATHS]
        self.assertEqual(
            {spec.attribute_code for spec in specs},
            set(ATTRIBUTE_VALUES),
        )
        self.assertEqual([spec.id_start for spec in specs], [1826, 1829])
        for spec in specs:
            plan = value_importer.verify_import(REPOSITORY, spec)
            self.assertEqual(len(plan.existing_rows), 3)
            self.assertEqual(plan.missing_rows, ())

    def test_six_cargo_observations_are_exact_and_source_scoped(self) -> None:
        selected = [
            row
            for row in rows("configuration_attribute_values.csv")
            if row["source_code"] == SOURCE_CODE
            and row["configuration_code"] in CONFIGURATION_CODES
            and row["attribute_code"] in ATTRIBUTE_VALUES
        ]
        self.assertEqual(len(selected), 6)
        self.assertEqual({row["fuel_type_code"] for row in selected}, {""})
        self.assertEqual({row["observation_date"] for row in selected}, {"2026-07-03"})
        keyed = {
            (row["configuration_code"], row["attribute_code"]): row["value"]
            for row in selected
        }
        for configuration_code in CONFIGURATION_CODES:
            for attribute_code, value in ATTRIBUTE_VALUES.items():
                self.assertEqual(keyed[(configuration_code, attribute_code)], value)

    def test_petrol_co2_remains_unimported(self) -> None:
        forbidden = [
            row
            for row in rows("configuration_attribute_values.csv")
            if row["configuration_code"] in CONFIGURATION_CODES
            and row["attribute_code"] == "co2_emissions"
            and row["fuel_type_code"] == "petrol"
        ]
        self.assertEqual(forbidden, [])

    def test_reporting_scope_is_complete_with_two_cargo_slots(self) -> None:
        report = configuration_completeness.collect_report(
            REPOSITORY,
            REPOSITORY
            / "data"
            / "reporting"
            / "duster_ecog120_automatic_completeness.json",
        )
        self.assertEqual(report["scope"]["reporting_configurations"], 3)
        self.assertEqual(report["scope"]["technical_slots"], 31)
        self.assertEqual(report["technical"]["denominator"], 93)
        self.assertEqual(report["technical"]["present"], 93)
        self.assertEqual(report["technical"]["missing"], 0)

    def test_importer_and_project_state_contract(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/import_duster_ecog120_automatic_cargo_20260725.py",
                "--check",
            ],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stdout + completed.stderr,
        )
        self.assertIn(
            "PASS: Duster Eco-G 120 automatic cargo and emissions-gap contract",
            completed.stdout,
        )
        state = json.loads(
            (REPOSITORY / "project" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            state["phase"],
            "Duster Eco-G 120 Automatic Cargo and Emissions Gap Review",
        )
        self.assertEqual(state["baseline"]["tests"], 758)
        self.assertEqual(state["baseline"]["rows"], 8135)
        self.assertEqual(state["baseline"]["configuration_values"], 1831)
        self.assertEqual(state["baseline"]["configuration_import_specs"], 114)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 176)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertIn("Brochure", state["next_package"]["name"])


if __name__ == "__main__":
    unittest.main()
