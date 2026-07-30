from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from tools.validators.enum_domains import (
    load_enum_domain_values,
    validate_enum_domains,
)
from tools.validators.statuses import configured_status_rules

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC = (
    ROOT
    / "data"
    / "imports"
    / "configuration_values"
    / "jogger-page6-hybrid-battery-chemistry-20260401.json"
)
JOGGER_SOURCE = "src_pl_jogger_price_my26_20260401"
BIGSTER_SOURCE = "src_pl_bigster_brochure_20251210"
HYBRID_CONFIGURATIONS = {
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
}


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class AttributeEnumDomainTests(unittest.TestCase):
    def test_registry_contains_all_migrated_domains(self) -> None:
        rows = csv_rows(MASTER / "attribute_enum_domains.csv")
        mappings = {row["attribute_code"]: row["domain_file"] for row in rows}
        self.assertEqual(
            mappings,
            {
                "aspiration_type": "aspiration_types.csv",
                "cylinder_configuration": "cylinder_configurations.csv",
                "drive_type": "drive_types.csv",
                "emission_standard": "emission_standards.csv",
                "engine_type": "engine_types.csv",
                "fuel_type": "fuel_types.csv",
                "gearbox_type": "transmission_type.csv",
                "hybrid_battery_type": "battery_chemistries.csv",
                "injection_type": "injection_types.csv",
                "recommended_fuel": "recommended_fuels.csv",
            },
        )
        self.assertTrue(all(row["status"] == "active" for row in rows))

    def test_battery_chemistry_domain_is_controlled(self) -> None:
        rows = csv_rows(MASTER / "enums" / "battery_chemistries.csv")
        self.assertEqual(
            rows,
            [
                {
                    "code": "lithium_ion",
                    "name": "Lithium-ion",
                    "description": "Lithium-ion rechargeable battery chemistry",
                    "status": "active",
                }
            ],
        )

    def test_global_enum_domain_validation_accepts_repository(self) -> None:
        checked, errors = validate_enum_domains(ROOT)
        self.assertGreaterEqual(checked, 100)
        self.assertEqual(errors, [])

    def test_every_enum_observation_resolves_through_registry(self) -> None:
        domains, _, errors = load_enum_domain_values(ROOT)
        self.assertEqual(errors, [])
        attribute_types = {
            row["code"]: row["data_type"] for row in csv_rows(MASTER / "attributes.csv")
        }
        enum_rows = [
            row
            for row in csv_rows(MASTER / "configuration_attribute_values.csv")
            if attribute_types[row["attribute_code"]] == "enum"
        ]
        self.assertEqual(len(enum_rows), 239)
        for row in enum_rows:
            self.assertIn(row["attribute_code"], domains)
            self.assertIn(row["value"], domains[row["attribute_code"]])

    def test_status_rules_are_resolved_from_registry(self) -> None:
        rules, errors = configured_status_rules(ROOT)
        self.assertEqual(errors, [])
        paths = [rule.path for rule in rules]
        self.assertEqual(len(paths), len(set(paths)))
        for row in csv_rows(MASTER / "attribute_enum_domains.csv"):
            self.assertIn(f"data/master/enums/{row['domain_file']}", paths)

    def test_import_spec_has_exact_hybrid_denominator(self) -> None:
        payload = json.loads(SPEC.read_text(encoding="utf-8"))
        self.assertEqual(payload["id_start"], 1199)
        self.assertEqual(payload["attribute_code"], "hybrid_battery_type")
        self.assertEqual(payload["attribute_contract"]["data_type"], "enum")
        self.assertEqual(payload["source_page"], 6)
        self.assertEqual(len(payload["rows"]), 6)
        self.assertEqual(
            {row["configuration_code"] for row in payload["rows"]},
            HYBRID_CONFIGURATIONS,
        )
        self.assertEqual({row["value"] for row in payload["rows"]}, {"lithium_ion"})

    def test_twenty_lithium_ion_observations_are_materialized(self) -> None:
        rows = [
            row
            for row in csv_rows(MASTER / "configuration_attribute_values.csv")
            if row["attribute_code"] == "hybrid_battery_type"
        ]
        self.assertEqual(len(rows), 20)
        self.assertEqual({row["value"] for row in rows}, {"lithium_ion"})

        jogger_rows = [row for row in rows if row["source_code"] == JOGGER_SOURCE]
        self.assertEqual({int(row["id"]) for row in jogger_rows}, set(range(1199, 1205)))
        self.assertEqual(
            {row["configuration_code"] for row in jogger_rows},
            HYBRID_CONFIGURATIONS,
        )
        self.assertEqual(
            {row["observation_date"] for row in jogger_rows},
            {"2026-04-01"},
        )

        active_bigster = {
            row["code"]
            for row in csv_rows(MASTER / "configurations.csv")
            if row["status"] == "active" and row["code"].startswith("bigster_")
        }
        bigster_rows = [row for row in rows if row["source_code"] == BIGSTER_SOURCE]
        self.assertEqual({int(row["id"]) for row in bigster_rows}, set(range(3288, 3302)))
        self.assertEqual(
            {row["configuration_code"] for row in bigster_rows},
            active_bigster,
        )
        self.assertEqual(len(active_bigster), 14)
        self.assertEqual(
            {row["observation_date"] for row in bigster_rows},
            {"2025-12-10"},
        )

    def test_capacity_remains_deferred_and_provenance_is_preserved(self) -> None:
        values = csv_rows(MASTER / "configuration_attribute_values.csv")
        capacity_rows = [
            row
            for row in values
            if row["attribute_code"] == "hybrid_battery_capacity"
            and row["configuration_code"] in HYBRID_CONFIGURATIONS
        ]
        self.assertEqual(capacity_rows, [])
        chemistry_rows = [
            row for row in values if row["attribute_code"] == "hybrid_battery_type"
        ]
        expected_sources = {JOGGER_SOURCE, BIGSTER_SOURCE}
        self.assertEqual(
            {row["source_code"] for row in chemistry_rows},
            expected_sources,
        )
        self.assertTrue(
            all("litowo-jonowy" in row["notes"].lower() for row in chemistry_rows)
        )
        sources = {
            row["code"]: row
            for row in csv_rows(MASTER / "sources.csv")
            if row["code"] in expected_sources
        }
        self.assertEqual(set(sources), expected_sources)
        for source in sources.values():
            self.assertEqual(len(source["sha256"]), 64)
            self.assertTrue((ROOT / source["file_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
