from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
sys.path.insert(0, str(ROOT / "tools"))

import configuration_comparison  # noqa: E402
import configuration_completeness  # noqa: E402
import source_coverage  # noqa: E402

SOURCE_CODE = "src_pl_duster_price_my26_20260703"
CONFIGURATION_CODES = {
    "duster_iii_expression_hybridg150_4x4_automatic",
    "duster_iii_extreme_hybridg150_4x4_automatic",
    "duster_iii_journey_hybridg150_4x4_automatic",
}
EXPECTED_CURRENT_PRICES = {
    "duster_iii_expression_hybridg150_4x4_automatic": 119900,
    "duster_iii_extreme_hybridg150_4x4_automatic": 125900,
    "duster_iii_journey_hybridg150_4x4_automatic": 126100,
}
COMPLETENESS_SPEC = REPORTING / "duster_hybridg150_4x4_completeness.json"
EVIDENCE_SPEC = REPORTING / "duster_hybridg150_4x4_gap_evidence.spec"
RECONCILIATION = (
    REPORTING
    / "duster_current_range_configuration_catalog_reconciliation_20260808.json"
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DusterCurrentRangeConfigurationCatalogReconciliationTests(unittest.TestCase):
    def test_three_exact_active_identities_are_source_linked(self) -> None:
        configurations = {
            row["code"]: row
            for row in rows(MASTER / "configurations.csv")
            if row["code"] in CONFIGURATION_CODES
        }
        self.assertEqual(set(configurations), CONFIGURATION_CODES)
        self.assertTrue(
            all(row["status"] == "active" for row in configurations.values())
        )
        self.assertTrue(
            all(
                row["powertrain_label"] == "hybrid-G 150 4x4"
                and row["transmission_type"] == "automatic"
                for row in configurations.values()
            )
        )

        relationships = [
            row
            for row in rows(MASTER / "source_configurations.csv")
            if row["source_code"] == SOURCE_CODE
            and row["configuration_code"] in CONFIGURATION_CODES
        ]
        self.assertEqual(
            {row["configuration_code"] for row in relationships},
            CONFIGURATION_CODES,
        )
        self.assertEqual(len(relationships), 3)
        self.assertTrue(all(row["relationship"] == "documents" for row in relationships))

    def test_identity_only_scope_preserves_observation_boundaries(self) -> None:
        spec = json.loads(COMPLETENESS_SPEC.read_text(encoding="utf-8"))
        evidence = json.loads(EVIDENCE_SPEC.read_text(encoding="utf-8"))
        self.assertEqual(
            {item["configuration_code"] for item in spec["configurations"]},
            CONFIGURATION_CODES,
        )
        self.assertEqual(
            {item["source_code"] for item in spec["configurations"]},
            {SOURCE_CODE},
        )
        self.assertEqual(spec["technical_slots"], [
            {"attribute_code": "drive_type", "fuel_type_code": ""},
            {"attribute_code": "gearbox_type", "fuel_type_code": ""},
            {"attribute_code": "gear_count", "fuel_type_code": ""},
            {"attribute_code": "engine_type", "fuel_type_code": ""},
            {"attribute_code": "emission_standard", "fuel_type_code": ""},
            {"attribute_code": "engine_displacement", "fuel_type_code": ""},
            {"attribute_code": "cylinder_count", "fuel_type_code": ""},
            {"attribute_code": "total_valve_count", "fuel_type_code": ""},
            {"attribute_code": "top_speed", "fuel_type_code": ""},
            {"attribute_code": "acceleration_0_100", "fuel_type_code": ""},
            {"attribute_code": "fuel_tank_capacity", "fuel_type_code": "petrol"},
            {"attribute_code": "minimum_kerb_weight", "fuel_type_code": ""},
            {"attribute_code": "gross_vehicle_weight", "fuel_type_code": ""},
            {"attribute_code": "braked_trailer_weight", "fuel_type_code": ""},
            {"attribute_code": "cargo_volume_without_spare_wheel_iso3832", "fuel_type_code": ""},
            {"attribute_code": "maximum_cargo_volume_iso3832", "fuel_type_code": ""},
            {"attribute_code": "engine_power", "fuel_type_code": "petrol"},
            {"attribute_code": "engine_torque", "fuel_type_code": "petrol"},
            {"attribute_code": "injection_type", "fuel_type_code": "petrol"},
            {"attribute_code": "engine_power", "fuel_type_code": "lpg"},
            {"attribute_code": "engine_torque", "fuel_type_code": "lpg"},
            {"attribute_code": "injection_type", "fuel_type_code": "lpg"},
            {"attribute_code": "hybrid_system_voltage", "fuel_type_code": ""},
            {"attribute_code": "traction_motor_power", "fuel_type_code": ""},
            {"attribute_code": "starter_generator_power", "fuel_type_code": ""},
            {"attribute_code": "co2_emissions", "fuel_type_code": "petrol"},
            {"attribute_code": "fuel_consumption_combined", "fuel_type_code": "petrol"},
            {"attribute_code": "co2_emissions", "fuel_type_code": "lpg"},
            {"attribute_code": "fuel_consumption_combined", "fuel_type_code": "lpg"},
        ]
        self.assertEqual(spec["equipment_attributes"], [])
        self.assertEqual(evidence, {"as_of": "2026-07-03", "decisions": [], "version": 1})

    def test_exact_current_catalog_prices_are_recorded(self) -> None:
        prices = {
            row["configuration_code"]: row
            for row in rows(MASTER / "configuration_prices.csv")
            if row["configuration_code"] in CONFIGURATION_CODES
        }
        self.assertEqual(
            {code: int(row["amount"]) for code, row in prices.items()},
            EXPECTED_CURRENT_PRICES,
        )
        self.assertEqual({row["market"] for row in prices.values()}, {"PL"})
        self.assertEqual(
            {row["price_type"] for row in prices.values()}, {"catalog_gross"}
        )
        self.assertEqual({row["currency_code"] for row in prices.values()}, {"PLN"})
        self.assertEqual({row["price_date"] for row in prices.values()}, {"2026-07-03"})
        self.assertEqual({row["source_code"] for row in prices.values()}, {SOURCE_CODE})

    def test_reporting_tools_cover_identity_without_projecting_observations(self) -> None:
        completeness = configuration_completeness.collect_report(
            ROOT, COMPLETENESS_SPEC, "2026-07-03"
        )
        coverage = source_coverage.collect_report(
            ROOT, COMPLETENESS_SPEC, "2026-07-03"
        )
        comparison = configuration_comparison.collect_report(
            ROOT, COMPLETENESS_SPEC, EVIDENCE_SPEC, "2026-07-03"
        )

        self.assertEqual(completeness["scope"]["reporting_configurations"], 3)
        self.assertEqual(completeness["technical"]["denominator"], 87)
        self.assertEqual(completeness["equipment"]["denominator"], 0)
        self.assertEqual(coverage["source_registration"]["registered"], 1)
        self.assertEqual(coverage["source_registration"]["missing"], 0)
        self.assertEqual(coverage["records"]["identity_links"]["missing"], 0)
        self.assertEqual(coverage["records"]["prices"]["missing"], 0)
        self.assertEqual(coverage["records"]["technical"]["present"], 87)
        self.assertEqual(comparison["scope"]["pair_count"], 3)
        self.assertEqual(comparison["summary"]["prices"]["different"], 3)
        self.assertEqual(comparison["summary"]["technical"]["comparisons"], 87)
        self.assertEqual(comparison["summary"]["technical"]["not_comparable"], 0)

    def test_reconciliation_receipt_preserves_existing_rows_and_prices(self) -> None:
        report = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "complete")
        self.assertEqual(
            set(report["changes"]["added_current_configurations"]),
            CONFIGURATION_CODES,
        )
        self.assertFalse(report["changes"]["existing_configuration_rows_deleted"])
        self.assertFalse(report["changes"]["existing_status_values_changed"])
        self.assertFalse(report["changes"]["price_rows_changed"])
        self.assertEqual(
            report["next_package"]["package_id"],
            "duster_hybridg150_current_price_import_001",
        )


if __name__ == "__main__":
    unittest.main()
