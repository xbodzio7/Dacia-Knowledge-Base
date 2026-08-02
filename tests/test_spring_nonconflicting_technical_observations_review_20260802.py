from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/spring_nonconflicting_technical_observations_review.json"
TOOL = ROOT / "tools/review_spring_nonconflicting_technical_observations_20260802.py"
STATE = ROOT / "project/state.json"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
HISTORICAL_PACKAGE_ID = "spring_nonconflicting_technical_observations_review_001"
CONFIGURATIONS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


def load_tool():
    spec = importlib.util.spec_from_file_location("spring_technical_review", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring technical review tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpringNonconflictingTechnicalReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = read_json(REPORT)
        cls.state = read_json(STATE)

    def test_review_is_deterministic_while_current(self) -> None:
        if self.state["current_package"]["package_id"] == HISTORICAL_PACKAGE_ID:
            tool = load_tool()
            self.assertEqual(self.report, tool.build(ROOT))
            tool.verify(ROOT)

    def test_scope_is_review_only_and_source_complete(self) -> None:
        self.assertEqual(
            self.report["scope"],
            {
                "source_codes": [
                    "src_pl_spring_brochure_20260219",
                    "src_pl_spring_price_my25_stock_20260708",
                ],
                "configuration_codes": [
                    "spring_essential_electric70_automatic",
                    "spring_expression_electric70_automatic",
                    "spring_extreme_electric100_automatic",
                ],
                "reviewed_areas": [
                    "battery",
                    "charging_times",
                    "performance",
                    "dimensions",
                    "luggage",
                ],
                "master_data_mutation_authorized": False,
            },
        )
        self.assertEqual(len(self.report["source_receipts"]), 2)
        self.assertTrue(all(row["sha256"] for row in self.report["source_receipts"]))

    def test_exact_approved_migration_boundary(self) -> None:
        approved = self.report["approved_migration"]
        self.assertEqual(approved["classification"], "context_safe_nonconflicting")
        self.assertEqual(approved["source_pages"], [18, 21])
        self.assertEqual(approved["configuration_count"], 3)
        self.assertEqual(approved["observation_count"], 36)
        self.assertEqual(len(approved["attribute_values"]), 12)
        self.assertEqual(
            {row["configuration_code"] for row in approved["observations"]},
            CONFIGURATIONS,
        )
        self.assertTrue(
            all(row["source_code"] == "src_pl_spring_brochure_20260219" for row in approved["observations"])
        )

    def test_approved_values_are_common_and_exact(self) -> None:
        values = self.report["approved_migration"]["attribute_values"]
        self.assertEqual(values["traction_battery_type"], "lithium_iron_phosphate")
        self.assertEqual(values["electric_motor_type"], "permanent_magnet_synchronous")
        self.assertEqual(values["steering_type"], "Elektryczne wspomaganie układu kierowniczego")
        self.assertEqual(
            {key: values[key] for key in (
                "overall_height",
                "front_track",
                "overall_width",
                "overall_width_with_mirrors",
                "rear_track",
                "front_overhang",
                "wheelbase",
                "rear_overhang",
                "overall_length",
            )},
            {
                "overall_height": "1489",
                "front_track": "1385",
                "overall_width": "1583",
                "overall_width_with_mirrors": "1767",
                "rear_track": "1365",
                "front_overhang": "683",
                "wheelbase": "2423",
                "rear_overhang": "595",
                "overall_length": "3701",
            },
        )
        self.assertNotIn("ground_clearance", values)

    def test_enum_support_is_bounded_to_existing_attributes(self) -> None:
        enum_support = self.report["approved_migration"]["enum_representation"]
        self.assertEqual(set(enum_support), {"electric_motor_type", "traction_battery_type"})
        self.assertEqual(enum_support["electric_motor_type"]["registry_status"], "missing")
        self.assertEqual(enum_support["traction_battery_type"]["registry_status"], "missing")
        self.assertEqual(
            enum_support["traction_battery_type"]["required_value"],
            "lithium_iron_phosphate",
        )

    def test_model_year_and_measurement_deferrals_are_preserved(self) -> None:
        classifications = {row["fact"]: row for row in self.report["classifications"]}
        self.assertEqual(
            classifications["traction battery mass"]["classification"],
            "deferred_model_year_bound",
        )
        self.assertEqual(
            classifications["traction battery nominal voltage"]["classification"],
            "deferred_model_year_bound",
        )
        self.assertEqual(
            classifications["traction battery capacity"]["classification"],
            "deferred_measurement_basis",
        )
        self.assertEqual(
            classifications["wheel-qualified ground clearance"]["classification"],
            "deferred_configuration_dependent",
        )

    def test_prohibited_automatic_migrations_remain_excluded(self) -> None:
        approved_attributes = set(self.report["approved_migration"]["attribute_values"])
        self.assertTrue(
            approved_attributes.isdisjoint(
                {
                    "top_speed",
                    "combined_range",
                    "city_range",
                    "traction_battery_voltage",
                    "traction_battery_gross_capacity",
                    "traction_battery_net_capacity",
                }
            )
        )
        classifications = {row["fact"]: row["classification"] for row in self.report["classifications"]}
        self.assertEqual(classifications["charging times"], "deferred_contextual")
        self.assertEqual(classifications["performance and range"], "represented_or_deferred")
        self.assertEqual(classifications["luggage volumes"], "already_represented")

    def test_state_and_historical_transition_contract(self) -> None:
        self.assertEqual(self.state["current_package"]["status"], "complete")
        current_id = self.state["current_package"]["package_id"]
        if current_id == HISTORICAL_PACKAGE_ID:
            self.assertEqual(
                self.state["next_package"]["package_id"],
                "spring_nonconflicting_common_technical_observations_migration_001",
            )
            self.assertEqual(self.state["baseline"]["rows"], 11730)
            self.assertEqual(self.state["baseline"]["configuration_values"], 3568)
        else:
            self.assertGreaterEqual(self.state["baseline"]["configuration_values"], 3604)
        self.assertGreaterEqual(self.state["baseline"]["tests"], 1801)


if __name__ == "__main__":
    unittest.main()
