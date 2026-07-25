from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
MASTER = REPOSITORY / "data" / "master"
RO_SOURCE = "src_ro_duster_ecog120_automatic_homologation_20260725"
PL_SOURCE = "src_pl_duster_ecog120_automatic_wltp_20260725"
SOURCE_CODES = {RO_SOURCE, PL_SOURCE}
RO_SNAPSHOT = (
    REPOSITORY
    / "project"
    / "sources"
    / "dacia-ro-duster-ecog120-automatic-homologation-20260725.json"
)
PL_SNAPSHOT = (
    REPOSITORY
    / "project"
    / "sources"
    / "dacia-pl-duster-ecog120-automatic-wltp-20260725.json"
)
EXPECTED_HASHES = {
    RO_SOURCE: "045bf18bc8ed2dee6ee86692e8fb7cf9a3005e6cf389c3b743376f7abe96d75d",
    PL_SOURCE: "9fb6f9ec816ab8ddc813b4ab53c09394454c420bc01866db0b17d027faf126e7",
}
CONFIGURATION_CODES = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
CARGO_ATTRIBUTES = {
    "boot_capacity",
    "cargo_volume_vda",
    "cargo_volume_vda_to_luggage_cover",
    "cargo_volume_vda_to_seatback",
    "cargo_volume_without_spare_wheel_iso3832",
    "maximum_cargo_volume_iso3832",
}

sys.path.insert(0, str(REPOSITORY / "tools"))
import configuration_completeness  # noqa: E402


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterEcoG120AutomaticHomologation20260725Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = rows("sources.csv")
        cls.values = [
            row
            for row in rows("configuration_attribute_values.csv")
            if row["source_code"] in SOURCE_CODES
        ]
        cls.ranges = [
            row
            for row in rows("configuration_attribute_value_ranges.csv")
            if row["source_code"] in SOURCE_CODES
        ]

    def test_snapshots_are_registered_with_exact_hashes_and_markets(self) -> None:
        source_rows = {
            row["code"]: row
            for row in self.sources
            if row["code"] in SOURCE_CODES
        }
        self.assertEqual(set(source_rows), SOURCE_CODES)
        self.assertEqual(source_rows[RO_SOURCE]["market"], "RO")
        self.assertEqual(source_rows[PL_SOURCE]["market"], "PL")
        for source_code, path in (
            (RO_SOURCE, RO_SNAPSHOT),
            (PL_SOURCE, PL_SNAPSHOT),
        ):
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, EXPECTED_HASHES[source_code])
            self.assertEqual(source_rows[source_code]["sha256"], actual)
            self.assertEqual(source_rows[source_code]["document_date"], "2026-07-25")

    def test_sixty_scalar_observations_preserve_fuel_context(self) -> None:
        self.assertEqual(len(self.values), 60)
        self.assertEqual(
            Counter(row["source_code"] for row in self.values),
            {RO_SOURCE: 54, PL_SOURCE: 6},
        )
        self.assertEqual(
            Counter(row["configuration_code"] for row in self.values),
            Counter({code: 20 for code in CONFIGURATION_CODES}),
        )
        keyed = {
            (
                row["configuration_code"],
                row["attribute_code"],
                row["fuel_type_code"],
            ): row["value"]
            for row in self.values
        }
        for code in CONFIGURATION_CODES:
            self.assertEqual(keyed[(code, "engine_power", "lpg")], "90")
            self.assertEqual(keyed[(code, "engine_power", "petrol")], "84")
            self.assertEqual(keyed[(code, "engine_torque", "lpg")], "200")
            self.assertEqual(keyed[(code, "engine_torque", "petrol")], "190")
            self.assertEqual(keyed[(code, "fuel_consumption_combined", "lpg")], "7.6")
            self.assertEqual(
                keyed[(code, "fuel_consumption_combined", "petrol")],
                "6.2",
            )
            self.assertEqual(keyed[(code, "co2_emissions", "lpg")], "123")
            self.assertNotIn((code, "co2_emissions", "petrol"), keyed)

    def test_performance_towing_and_mass_values_are_exact(self) -> None:
        keyed = {
            (row["configuration_code"], row["attribute_code"]): row["value"]
            for row in self.values
            if not row["fuel_type_code"]
        }
        expected = {
            "gear_count": "6",
            "top_speed": "180",
            "turning_circle": "10.96",
            "gross_vehicle_weight": "1805",
            "gross_train_weight": "3305",
            "braked_trailer_weight": "1500",
            "unbraked_trailer_weight": "715",
            "roof_load": "80",
            "fuel_tank_capacity": "51",
        }
        for code in CONFIGURATION_CODES:
            for attribute, value in expected.items():
                self.assertEqual(keyed[(code, attribute)], value)

    def test_eighteen_ranges_preserve_source_endpoints(self) -> None:
        self.assertEqual(len(self.ranges), 18)
        self.assertEqual(
            Counter(row["attribute_code"] for row in self.ranges),
            {
                "max_power_rpm": 6,
                "max_torque_rpm": 6,
                "kerb_weight": 3,
                "maximum_payload": 3,
            },
        )
        self.assertTrue(all(row["lower_inclusive"] == "true" for row in self.ranges))
        self.assertTrue(all(row["upper_inclusive"] == "true" for row in self.ranges))
        keyed = {
            (
                row["configuration_code"],
                row["attribute_code"],
                row["fuel_type_code"],
            ): (row["minimum_value"], row["maximum_value"])
            for row in self.ranges
        }
        for code in CONFIGURATION_CODES:
            self.assertEqual(
                keyed[(code, "max_power_rpm", "lpg")],
                ("4500", "5000"),
            )
            self.assertEqual(
                keyed[(code, "max_power_rpm", "petrol")],
                ("4500", "5750"),
            )
            self.assertEqual(
                keyed[(code, "max_torque_rpm", "lpg")],
                ("1750", "4000"),
            )
            self.assertEqual(
                keyed[(code, "max_torque_rpm", "petrol")],
                ("1750", "4000"),
            )
            self.assertEqual(
                keyed[(code, "kerb_weight", "")],
                ("1358", "1381"),
            )
            self.assertEqual(
                keyed[(code, "maximum_payload", "")],
                ("454", "477"),
            )

    def test_exact_card_sources_do_not_supply_cargo_volume(self) -> None:
        observed = {
            (row["configuration_code"], row["attribute_code"])
            for row in self.values + self.ranges
            if row["configuration_code"] in CONFIGURATION_CODES
        }
        self.assertFalse(
            {
                (configuration, attribute)
                for configuration, attribute in observed
                if attribute in CARGO_ATTRIBUTES
            }
        )
        for path in (RO_SNAPSHOT, PL_SNAPSHOT):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for card in payload["cards"]:
                non_imports = {
                    item["attribute_code"]
                    for item in card.get("non_imports", [])
                }
                self.assertTrue(non_imports & CARGO_ATTRIBUTES)

    def test_completeness_scope_is_exact_and_fully_present(self) -> None:
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
        self.assertEqual(report["equipment"]["denominator"], 0)

    def test_importer_check_reproduces_master_contract(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "tools/import_duster_ecog120_automatic_homologation_20260725.py",
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
            "PASS: Duster Eco-G 120 automatic homologation contract",
            completed.stdout,
        )

    def test_project_state_exposes_new_denominators_and_next_gap(self) -> None:
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
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 176)
        self.assertEqual(
            state["current_package"]["name"],
            "Duster Eco-G 120 Automatic Cargo and Emissions Gap Review",
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertIn("Brochure", state["next_package"]["name"])


if __name__ == "__main__":
    unittest.main()
