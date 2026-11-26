from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import configuration_shortlist as cli  # noqa: E402
from reporting.commercial_offers import collect_commercial_components  # noqa: E402
from reporting.configuration_shortlist import (  # noqa: E402
    ShortlistCriteria,
    ShortlistError,
    collect_report,
    normalize_criteria,
    render_csv,
    render_json,
    render_markdown,
)


class ConfigurationShortlistTests(unittest.TestCase):
    def write_csv(
        self,
        path: Path,
        headers: tuple[str, ...],
        rows: list[tuple[object, ...]],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

    def fixture(self, root: Path) -> Path:
        master = root / "data" / "master"
        self.write_csv(
            master / "models.csv",
            (
                "id",
                "code",
                "name",
                "generation",
                "production_from",
                "production_to",
                "body_type_code",
                "segment_code",
                "status",
                "notes",
            ),
            [
                (1, "model_a", "Model A", "I", 2025, "", "suv", "C", "current", ""),
                (2, "model_b", "Model B", "I", 2025, "", "mpv", "C", "current", ""),
            ],
        )
        self.write_csv(
            master / "versions.csv",
            ("id", "code", "model_code", "name", "status", "notes"),
            [
                (1, "version_a", "model_a", "Expression", "active", ""),
                (2, "version_b", "model_a", "Extreme", "active", ""),
                (3, "version_c", "model_b", "Journey", "active", ""),
            ],
        )
        self.write_csv(
            master / "configurations.csv",
            (
                "id",
                "code",
                "version_code",
                "powertrain_label",
                "transmission_type",
                "status",
                "notes",
            ),
            [
                (1, "cfg_a", "version_a", "Eco-G 120", "manual", "active", ""),
                (2, "cfg_b", "version_b", "Eco-G 120", "automatic", "active", ""),
                (3, "cfg_c", "version_c", "Hybrid 155", "manual", "active", ""),
                (4, "cfg_d", "version_c", "Hybrid 155", "automatic", "active", ""),
                (5, "cfg_archived", "version_a", "TCe 90", "manual", "archived", ""),
            ],
        )
        self.write_csv(
            master / "configuration_prices.csv",
            (
                "id",
                "code",
                "configuration_code",
                "market",
                "price_type",
                "amount",
                "currency_code",
                "price_date",
                "source_code",
                "notes",
            ),
            [
                (1, "cfg_a_old", "cfg_a", "PL", "catalog_gross", 65000, "PLN", "2025-01-01", "src_old", ""),
                (2, "cfg_a_new", "cfg_a", "PL", "catalog_gross", 70000, "PLN", "2026-01-01", "src_a", ""),
                (3, "cfg_b_new", "cfg_b", "PL", "catalog_gross", 90000, "PLN", "2026-01-01", "src_b", ""),
                (4, "cfg_c_new", "cfg_c", "PL", "catalog_gross", 80000, "PLN", "2026-01-01", "src_c", ""),
                (5, "wrong_market", "cfg_d", "DE", "catalog_gross", 75000, "EUR", "2026-01-01", "src_d", ""),
            ],
        )
        self.write_csv(
            master / "configuration_attribute_values.csv",
            (
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "fuel_type_code",
                "gear_number",
                "value",
                "observation_date",
                "source_code",
                "notes",
            ),
            [
                (1, "cfg_a_seats", "cfg_a", "number_of_seats", "", "", 5, "2026-01-01", "src_a", ""),
                (2, "cfg_b_seats", "cfg_b", "number_of_seats", "", "", 5, "2026-01-01", "src_b", ""),
                (3, "cfg_c_seats", "cfg_c", "number_of_seats", "", "", 7, "2026-01-01", "src_c", ""),
                (4, "cfg_a_power", "cfg_a", "engine_power", "petrol", "", 90, "2026-01-01", "src_a", ""),
            ],
        )
        self.write_csv(
            master / "configuration_attribute_availability.csv",
            (
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "availability_status",
                "observation_date",
                "source_code",
                "notes",
            ),
            [
                (1, "a_heated", "cfg_a", "heated_steering_wheel", "standard", "2026-01-01", "src_a", ""),
                (2, "a_nav", "cfg_a", "navigation_system", "optional", "2026-01-01", "src_a", ""),
                (3, "a_camera", "cfg_a", "rear_view_camera", "standard", "2026-01-01", "src_a", ""),
                (4, "b_heated", "cfg_b", "heated_steering_wheel", "optional", "2026-01-01", "src_b", ""),
                (5, "b_nav", "cfg_b", "navigation_system", "not_available", "2026-01-01", "src_b", ""),
                (6, "c_heated", "cfg_c", "heated_steering_wheel", "not_available", "2026-01-01", "src_c", ""),
                (7, "c_camera", "cfg_c", "rear_view_camera", "optional", "2026-01-01", "src_c", ""),
                (8, "d_nav", "cfg_d", "navigation_system", "standard", "2026-01-01", "src_d", ""),
                (9, "d_camera", "cfg_d", "rear_view_camera", "standard", "2026-01-01", "src_d", ""),
            ],
        )
        self.write_csv(
            master / "commercial_items.csv",
            (
                "id", "code", "name", "item_type", "observation_date",
                "source_code", "status", "notes",
            ),
            [
                (1, "nav_package", "Pakiet nawigacji", "package", "2025-12-01", "src_offer", "active", ""),
            ],
        )
        self.write_csv(
            master / "commercial_item_attributes.csv",
            (
                "id", "code", "commercial_item_code", "attribute_code",
                "source_text", "notes",
            ),
            [
                (1, "nav_package__navigation", "nav_package", "navigation_system", "Nawigacja", ""),
            ],
        )
        self.write_csv(
            master / "commercial_item_configurations.csv",
            (
                "id", "code", "commercial_item_code", "configuration_code",
                "availability_status", "amount", "currency_code", "price_date",
                "source_code", "notes",
            ),
            [
                (1, "nav_package__offer", "nav_package", "cfg_a", "optional", 1200, "PLN", "2025-12-01", "src_offer", ""),
                (2, "nav_package__selected", "nav_package", "cfg_a", "standard", "", "PLN", "2026-01-01", "src_saved_configuration", ""),
            ],
        )
        return root

    def test_unfiltered_shortlist_is_price_sorted_and_reports_unknowns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(repository, ShortlistCriteria())
            commercial = collect_commercial_components(
                repository,
                {"cfg_a"},
                "2026-01-01",
            )
        self.assertEqual(report["as_of"], "2026-01-01")
        self.assertEqual(
            [item["configuration_code"] for item in report["results"]],
            ["cfg_a", "cfg_c", "cfg_b", "cfg_d"],
        )
        self.assertEqual(report["summary"]["active_configurations"], 4)
        self.assertEqual(report["summary"]["matched_configurations"], 4)
        self.assertEqual(
            report["summary"]["data_unknowns"],
            {
                "catalog_price_missing": 1,
                "number_of_seats_missing": 1,
                "required_equipment_missing": {},
            },
        )
        self.assertEqual(len(commercial["cfg_a"]), 1)
        offer = commercial["cfg_a"][0]
        self.assertEqual(offer["code"], "nav_package")
        self.assertEqual(offer["availability_status"], "optional")
        self.assertEqual(offer["amount"], 1200.0)
        self.assertTrue(offer["selected_state_observed"])
        self.assertEqual(
            offer["selected_state_source_code"],
            "src_saved_configuration",
        )

        spring_codes = {
            "spring_essential_electric70_automatic",
            "spring_expression_electric70_automatic",
            "spring_extreme_electric100_automatic",
        }
        with tempfile.TemporaryDirectory() as directory:
            spring_repository = Path(directory)
            spring_master = spring_repository / "data" / "master"
            self.write_csv(
                spring_master / "commercial_items.csv",
                (
                    "id", "code", "name", "item_type", "observation_date",
                    "source_code", "status", "notes",
                ),
                [
                    (1, "spring_type2_charging_cable_option", "Przewód Type 2", "option", "2026-02-19", "src_brochure", "active", ""),
                    (2, "spring_domestic_socket_charging_cable_option", "FlexiCharger", "option", "2026-07-08", "src_price", "active", ""),
                    (3, "spring_techno_package", "Pakiet Techno", "package", "2026-02-19", "src_brochure", "active", ""),
                    (4, "spring_dc40_charging_option", "DC 40 kW", "option", "2026-02-19", "src_brochure", "active", ""),
                ],
            )
            self.write_csv(
                spring_master / "commercial_item_attributes.csv",
                (
                    "id", "code", "commercial_item_code", "attribute_code",
                    "source_text", "notes",
                ),
                [
                    (1, "type2", "spring_type2_charging_cable_option", "type2_charging_cable_supplied", "Type 2", ""),
                    (2, "domestic", "spring_domestic_socket_charging_cable_option", "domestic_socket_charging_cable", "FlexiCharger", ""),
                    (3, "techno", "spring_techno_package", "navigation_system", "Techno", ""),
                    (4, "dc40", "spring_dc40_charging_option", "dc_charging_supported", "DC 40 kW", ""),
                ],
            )
            self.write_csv(
                spring_master / "commercial_item_configurations.csv",
                (
                    "id", "code", "commercial_item_code", "configuration_code",
                    "availability_status", "amount", "currency_code", "price_date",
                    "source_code", "notes",
                ),
                [
                    (1, "type2_e", "spring_type2_charging_cable_option", "spring_essential_electric70_automatic", "optional", "", "PLN", "", "src_brochure", ""),
                    (2, "type2_x", "spring_type2_charging_cable_option", "spring_expression_electric70_automatic", "optional", "", "PLN", "", "src_brochure", ""),
                    (3, "type2_r", "spring_type2_charging_cable_option", "spring_extreme_electric100_automatic", "optional", "", "PLN", "", "src_brochure", ""),
                    (4, "domestic_e", "spring_domestic_socket_charging_cable_option", "spring_essential_electric70_automatic", "optional", 1500, "PLN", "2026-08-02", "src_current", ""),
                    (5, "domestic_x", "spring_domestic_socket_charging_cable_option", "spring_expression_electric70_automatic", "optional", 1500, "PLN", "2026-07-08", "src_price", ""),
                    (6, "domestic_r", "spring_domestic_socket_charging_cable_option", "spring_extreme_electric100_automatic", "optional", 1500, "PLN", "2026-08-02", "src_current", ""),
                    (7, "techno_x", "spring_techno_package", "spring_expression_electric70_automatic", "optional", "", "PLN", "", "src_brochure", ""),
                    (8, "dc40_x", "spring_dc40_charging_option", "spring_expression_electric70_automatic", "optional", "", "PLN", "", "src_brochure", ""),
                ],
            )
            self.write_csv(
                spring_master / "configuration_attribute_availability.csv",
                (
                    "id", "code", "configuration_code", "attribute_code",
                    "availability_status", "observation_date", "source_code", "notes",
                ),
                [
                    (1, "type2_standard_e", "spring_essential_electric70_automatic", "type2_charging_cable_supplied", "standard", "2026-07-31", "src_current", ""),
                    (2, "type2_standard_x", "spring_expression_electric70_automatic", "type2_charging_cable_supplied", "standard", "2026-08-02", "src_saved", ""),
                    (3, "type2_standard_r", "spring_extreme_electric100_automatic", "type2_charging_cable_supplied", "standard", "2026-08-02", "src_saved", ""),
                ],
            )
            spring_historical = collect_commercial_components(
                spring_repository,
                spring_codes,
                "2026-02-19",
            )
            spring_current = collect_commercial_components(
                spring_repository,
                spring_codes,
                "2026-08-08",
            )

        for configuration_code in spring_codes:
            historical_codes = {
                item["code"] for item in spring_historical[configuration_code]
            }
            current_codes = {
                item["code"] for item in spring_current[configuration_code]
            }
            self.assertIn("spring_type2_charging_cable_option", historical_codes)
            self.assertNotIn("spring_type2_charging_cable_option", current_codes)
            self.assertIn(
                "spring_domestic_socket_charging_cable_option",
                current_codes,
            )
        current_unpriced = {
            (configuration_code, item["code"])
            for configuration_code, items in spring_current.items()
            for item in items
            if item["amount"] is None
        }
        self.assertEqual(
            current_unpriced,
            {
                (
                    "spring_expression_electric70_automatic",
                    "spring_techno_package",
                ),
                (
                    "spring_expression_electric70_automatic",
                    "spring_dc40_charging_option",
                ),
            },
        )
        reconciliation = json.loads(
            (
                REPOSITORY
                / "data"
                / "reporting"
                / "spring_type2_current_selector_reconciliation_20260808.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(reconciliation["selector_offer_rows_after"], 164)
        self.assertEqual(reconciliation["unpriced_selector_offer_rows_after"], 2)
        self.assertEqual(reconciliation["historical_mapping_rows_preserved"], 3)

        pricing_script = (
            REPOSITORY
            / "tools"
            / "reporting"
            / "configuration_shortlist_v12_pricing.js"
        )
        pricing_text = pricing_script.read_text(encoding="utf-8")
        for marker in (
            "configurator-summary-panel",
            "cards.length !== 1",
            "System nie wybiera samochodu arbitralnie",
            "Nie jest to katalog innych dostępnych wyborów",
            "Filtry wyposażenia służą do zawężania shortlisty",
            "configuratorSummaryMarkup",
            "configurator_navigation_state_integration_v1",
            "najpierw 1 wariant",
            "#configurator-summary-panel, #results-heading",
            ".commercial-choice-panel, .commercial-offers",
            "configurator_exact_appearance_status_v1",
            "po wyborze 1 wariantu",
            "brak dokładnego zapisu",
            "#configurator-selected-colours",
            "#configurator-selected-wheels",
            "#configurator-selected-upholsteries",
        ):
            self.assertIn(marker, pricing_text)
        if shutil.which("node"):
            program = r'''
const api = require(process.argv[1]);
const configuration = {
  configuration_code: "cfg_a",
  model_name: "Model A",
  version_name: "Expression",
  powertrain_label: "Eco-G 120",
  transmission_type: "manual",
  catalog_price: {state: "recorded", amount: "70000", currency_code: "PLN"},
  price_components: [
    {code: "one", name: "Opcja 1", kind: "option", availability_status: "optional", amount: 1000, currency_code: "PLN"},
    {code: "two", name: "Opcja 2", kind: "option", availability_status: "optional", amount: 2000, currency_code: "PLN"}
  ]
};
const observation = {
  observed_on: "2026-08-07",
  selected_colour: {value: "Zielony"},
  selected_wheels: {value: "18 cali"},
  selected_upholstery: {value: "Tapicerka testowa"}
};
process.stdout.write(api.configuratorSummaryMarkup(configuration, observation, ["one", "two"]));
'''
            completed = subprocess.run(
                ["node", "-e", program, str(pricing_script)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Podsumowanie konfiguracji", completed.stdout)
            self.assertIn("Opcja 1", completed.stdout)
            self.assertIn("Zielony", completed.stdout)
            self.assertIn("nie potwierdza ich wzajemnej kompatybilności", completed.stdout)

            navigation_program = r'''
require(process.argv[1]);
const api = globalThis.DkbConfiguratorNavigationState;
const appearance = globalThis.DkbConfiguratorExactAppearanceStatus;
process.stdout.write(JSON.stringify({
  summary0: api.summaryStatus(0),
  summary1: api.summaryStatus(1),
  summary3: api.summaryStatus(3),
  commercialSelected: api.commercialStatus(2, 3, 1),
  commercialChoices: api.commercialStatus(0, 3, 1),
  commercialMany: api.commercialStatus(0, 6, 3),
  commercialNone: api.commercialStatus(0, 0, 1),
  appearanceNone: appearance.appearanceStatus([], 0, "biel alpejska"),
  appearanceMany: appearance.appearanceStatus([], 3, "biel alpejska"),
  appearanceExact: appearance.appearanceStatus([], 1, "biel alpejska"),
  appearanceSelected: appearance.appearanceStatus(["zieleń cedrowa"], 2, "biel alpejska"),
  appearanceMultiFilter: appearance.appearanceStatus(["biały", "zielony"], 2, ""),
  appearanceMissing: appearance.appearanceStatus([], 1, ""),
  compactLength: appearance.compactStatus("x".repeat(60)).length
}));
'''
            navigation = subprocess.run(
                ["node", "-e", navigation_program, str(pricing_script)],
                text=True,
                capture_output=True,
                check=True,
            )
            states = json.loads(navigation.stdout)
            self.assertEqual(states["summary0"], "brak wyników")
            self.assertEqual(states["summary1"], "gotowe")
            self.assertEqual(states["summary3"], "zawęź: 3 wariantów")
            self.assertEqual(states["commercialSelected"], "wybrano: 2")
            self.assertEqual(states["commercialChoices"], "oferty: 3")
            self.assertEqual(states["commercialMany"], "najpierw 1 wariant")
            self.assertEqual(states["commercialNone"], "brak potwierdzonych ofert")
            self.assertEqual(states["appearanceNone"], "brak wyniku")
            self.assertEqual(states["appearanceMany"], "po wyborze 1 wariantu")
            self.assertEqual(states["appearanceExact"], "biel alpejska")
            self.assertEqual(states["appearanceSelected"], "zieleń cedrowa")
            self.assertEqual(states["appearanceMultiFilter"], "dokładne filtry: 2")
            self.assertEqual(states["appearanceMissing"], "brak dokładnego zapisu")
            self.assertLessEqual(states["compactLength"], 38)

    def test_metadata_powertrain_and_price_filters_compose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(
                repository,
                ShortlistCriteria(
                    models=("model_a",),
                    transmissions=("automatic",),
                    powertrains=("eco-g",),
                    minimum_price=Decimal("85000"),
                    maximum_price=Decimal("95000"),
                ),
            )
        self.assertEqual(
            [item["configuration_code"] for item in report["results"]],
            ["cfg_b"],
        )
        reasons = report["summary"]["exclusion_reason_counts"]
        self.assertEqual(reasons["model"], 2)
        self.assertEqual(reasons["transmission"], 2)
        self.assertEqual(reasons["powertrain"], 2)

    def test_seat_filter_excludes_missing_values_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(
                repository,
                ShortlistCriteria(seats=7),
            )
        self.assertEqual(
            [item["configuration_code"] for item in report["results"]],
            ["cfg_c"],
        )
        reasons = report["summary"]["exclusion_reason_counts"]
        self.assertEqual(reasons["number_of_seats"], 2)
        self.assertEqual(reasons["number_of_seats_missing"], 1)

    def test_required_equipment_accepts_standard_or_optional(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(
                repository,
                ShortlistCriteria(
                    required_equipment=("heated_steering_wheel",),
                ),
            )
        self.assertEqual(
            [item["configuration_code"] for item in report["results"]],
            ["cfg_a", "cfg_b"],
        )
        reasons = report["summary"]["exclusion_reason_counts"]
        self.assertEqual(
            reasons["equipment_not_available:heated_steering_wheel"],
            1,
        )
        self.assertEqual(
            reasons["equipment_missing:heated_steering_wheel"],
            1,
        )
        self.assertEqual(
            report["summary"]["data_unknowns"][
                "required_equipment_missing"
            ],
            {"heated_steering_wheel": 1},
        )

    def test_standard_equipment_rejects_optional_and_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(
                repository,
                ShortlistCriteria(
                    required_standard_equipment=(
                        "heated_steering_wheel",
                    ),
                ),
            )
        self.assertEqual(
            [item["configuration_code"] for item in report["results"]],
            ["cfg_a"],
        )
        reasons = report["summary"]["exclusion_reason_counts"]
        self.assertEqual(
            reasons["equipment_not_standard:heated_steering_wheel"],
            2,
        )
        self.assertEqual(
            reasons["equipment_missing:heated_steering_wheel"],
            1,
        )

    def test_as_of_uses_historical_price_and_excludes_future_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(
                repository,
                ShortlistCriteria(as_of="2025-06-01"),
            )
        self.assertEqual(report["results"][0]["configuration_code"], "cfg_a")
        self.assertEqual(
            report["results"][0]["catalog_price"]["amount"],
            "65000",
        )
        self.assertEqual(report["summary"]["data_unknowns"]["catalog_price_missing"], 3)
        self.assertEqual(report["summary"]["data_unknowns"]["number_of_seats_missing"], 4)

    def test_invalid_criteria_and_unknown_codes_fail(self) -> None:
        with self.assertRaisesRegex(
            ShortlistError,
            "minimum price cannot exceed maximum price",
        ):
            normalize_criteria(
                ShortlistCriteria(
                    minimum_price=Decimal("2"),
                    maximum_price=Decimal("1"),
                )
            )
        with self.assertRaisesRegex(ShortlistError, "positive integer"):
            normalize_criteria(ShortlistCriteria(seats=0))
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            with self.assertRaisesRegex(ShortlistError, "unknown model"):
                collect_report(
                    repository,
                    ShortlistCriteria(models=("missing_model",)),
                )
            with self.assertRaisesRegex(
                ShortlistError,
                "unknown equipment attribute",
            ):
                collect_report(
                    repository,
                    ShortlistCriteria(
                        required_equipment=("missing_equipment",),
                    ),
                )

    def test_renderers_are_deterministic_and_preserve_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(
                repository,
                ShortlistCriteria(
                    required_equipment=("rear_view_camera",),
                ),
            )
        json_text = render_json(report)
        markdown = render_markdown(report)
        csv_text = render_csv(report)
        self.assertEqual(json_text, render_json(report))
        self.assertEqual(markdown, render_markdown(report))
        self.assertEqual(csv_text, render_csv(report))
        self.assertIn('"source_code": "src_a"', json_text)
        self.assertIn("rear_view_camera=standard", markdown)
        self.assertIn("required_equipment_sources", csv_text)
        self.assertIn("rear_view_camera=src_c", csv_text)

    def test_cli_writes_all_output_formats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = self.fixture(root / "repository")
            json_path = root / "shortlist.json"
            markdown_path = root / "shortlist.md"
            csv_path = root / "shortlist.csv"
            result = cli.main(
                [
                    "--model",
                    "model_a",
                    "--max-price",
                    "95000",
                    "--json",
                    str(json_path),
                    "--markdown",
                    str(markdown_path),
                    "--csv",
                    str(csv_path),
                ],
                repository=repository,
            )
            self.assertEqual(result, 0)
            self.assertEqual(
                len(json.loads(json_path.read_text(encoding="utf-8"))["results"]),
                2,
            )
            self.assertIn("# Configuration Shortlist", markdown_path.read_text(encoding="utf-8"))
            self.assertEqual(
                len(list(csv.DictReader(csv_path.read_text(encoding="utf-8").splitlines()))),
                2,
            )

    def test_empty_shortlist_has_valid_markdown_and_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(
                repository,
                ShortlistCriteria(minimum_price=Decimal("999999")),
            )
        self.assertEqual(report["summary"]["matched_configurations"], 0)
        self.assertIn("No matches", render_markdown(report))
        self.assertEqual(
            list(csv.DictReader(render_csv(report).splitlines())),
            [],
        )


if __name__ == "__main__":
    unittest.main()
