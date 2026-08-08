from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data/imports/spring_nonconflicting_common_technical_20260219.csv"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
REPORT = ROOT / "data/reporting/spring_nonconflicting_common_technical_migration.json"
CONFIGURATIONS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}
ATTRIBUTES = {
    "electric_motor_type",
    "traction_battery_type",
    "steering_type",
    "overall_height",
    "front_track",
    "overall_width",
    "overall_width_with_mirrors",
    "rear_track",
    "front_overhang",
    "wheelbase",
    "rear_overhang",
    "overall_length",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class SpringCommonTechnicalMigrationTest(unittest.TestCase):
    def test_spec_is_exact_three_by_twelve_matrix(self) -> None:
        data = rows(SPEC)
        self.assertEqual(len(data), 36)
        self.assertEqual(Counter(r["configuration_code"] for r in data), Counter({c: 12 for c in CONFIGURATIONS}))
        self.assertEqual(Counter(r["attribute_code"] for r in data), Counter({a: 3 for a in ATTRIBUTES}))

    def test_spec_preserves_page_boundaries(self) -> None:
        for row in rows(SPEC):
            expected = "18" if row["attribute_code"] in {"electric_motor_type", "traction_battery_type", "steering_type"} else "21"
            self.assertEqual(row["source_page"], expected)

    def test_enum_registry_contains_only_required_new_rules(self) -> None:
        registry = {r["attribute_code"]: r for r in rows(ROOT / "data/master/attribute_enum_domains.csv")}
        self.assertEqual(registry["electric_motor_type"]["domain_file"], "electric_motor_types.csv")
        self.assertEqual(registry["traction_battery_type"]["domain_file"], "battery_chemistries.csv")

    def test_controlled_enum_values_exist(self) -> None:
        battery = {r["code"] for r in rows(ROOT / "data/master/enums/battery_chemistries.csv")}
        motor = {r["code"] for r in rows(ROOT / "data/master/enums/electric_motor_types.csv")}
        self.assertIn("lithium_iron_phosphate", battery)
        self.assertEqual(motor, {"permanent_magnet_synchronous"})

    def test_master_contains_exact_contiguous_migration_suffix(self) -> None:
        data = [r for r in rows(VALUES) if r["source_code"] == "src_pl_spring_brochure_20260219" and r["observation_date"] == "2026-02-19" and r["attribute_code"] in ATTRIBUTES]
        self.assertEqual(len(data), 36)
        self.assertEqual([int(r["id"]) for r in data], list(range(3569, 3605)))

    def test_no_deferred_my25_or_contextual_values_were_added(self) -> None:
        forbidden = {"traction_battery_weight", "battery_weight", "traction_battery_voltage", "battery_voltage", "traction_battery_capacity_gross", "traction_battery_capacity_net", "ground_clearance"}
        data = [r for r in rows(VALUES) if r["configuration_code"] in CONFIGURATIONS and r["source_code"] == "src_pl_spring_brochure_20260219" and r["observation_date"] == "2026-02-19"]
        self.assertFalse(forbidden.intersection({r["attribute_code"] for r in data}))


    def test_reporting_scopes_include_all_common_technical_slots(self) -> None:
        expected_counts = {
            "spring_electric70_automatic_completeness.json": 31,
            "spring_electric100_automatic_completeness.json": 12,
        }
        expected = {(attribute, "") for attribute in ATTRIBUTES}
        for filename, count in expected_counts.items():
            payload = json.loads((ROOT / "data/reporting" / filename).read_text(encoding="utf-8"))
            slots = {
                (row["attribute_code"], row.get("fuel_type_code", ""))
                for row in payload["technical_slots"]
            }
            self.assertEqual(len(payload["technical_slots"]), count, filename)
            self.assertTrue(expected.issubset(slots), filename)

    def test_report_records_exact_scope_and_deferrals(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["observation_count"], 36)
        self.assertEqual(report["value_id_range"], [3569, 3604])
        self.assertIn("battery_mass_204_kg_my2025_stock_only", report["preserved_deferrals"])
        self.assertEqual(
            report["dependent_reports_updated"],
            [
                "data/reporting/existing_configuration_missing_data_analysis.json",
                "data/reporting/existing_configuration_missing_data_analysis.md",
            ],
        )
        analysis = json.loads(
            (ROOT / "data/reporting/existing_configuration_missing_data_analysis.json").read_text(encoding="utf-8")
        )
        self.assertEqual(analysis["summary"]["completeness_scope_count"], 24)
        self.assertEqual(analysis["summary"]["missing_technical_count"], 97)

    def test_importer_verify_mode_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/import_spring_nonconflicting_common_technical_20260219.py", "--verify"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("PASS (36 values", completed.stdout)

    def test_state_manifest_tracks_every_durable_output(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        manifest = set(state["current_package"]["manifest_paths"])
        required = {
            "data/master/attribute_enum_domains.csv",
            "data/master/enums/battery_chemistries.csv",
            "data/master/enums/electric_motor_types.csv",
            "data/imports/spring_nonconflicting_common_technical_20260219.csv",
            "data/master/configuration_attribute_values.csv",
            "data/reporting/spring_electric70_automatic_completeness.json",
            "data/reporting/spring_electric100_automatic_completeness.json",
            "data/reporting/existing_configuration_missing_data_analysis.json",
            "data/reporting/existing_configuration_missing_data_analysis.md",
            "tools/import_spring_nonconflicting_common_technical_20260219.py",
            "data/reporting/spring_nonconflicting_common_technical_migration.json",
            "data/reporting/spring_nonconflicting_common_technical_migration.md",
            "project/packages/spring-nonconflicting-common-technical-observations-migration-20260802.md",
            "tests/test_spring_nonconflicting_common_technical_observations_migration_20260802.py",
            "tests/test_attribute_enum_domains.py",
            "tests/test_verified_pdf_candidate_coverage_reconciliation.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        }
        for relative in required - {"project/state.json", "project/STATE_SUMMARY.md"}:
            self.assertTrue((ROOT / relative).is_file(), relative)
        if state["current_package"]["package_id"] == "spring_nonconflicting_common_technical_observations_migration_001":
            self.assertTrue(required.issubset(manifest))
        else:
            self.assertEqual(state["current_package"]["status"], "complete")
            self.assertGreaterEqual(state["baseline"]["configuration_values"], 3604)


if __name__ == "__main__":
    unittest.main()
