from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import configuration_shortlist as cli  # noqa: E402
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
                "value",
                "observation_date",
                "source_code",
                "notes",
            ),
            [
                (1, "cfg_a_seats", "cfg_a", "number_of_seats", "", 5, "2026-01-01", "src_a", ""),
                (2, "cfg_b_seats", "cfg_b", "number_of_seats", "", 5, "2026-01-01", "src_b", ""),
                (3, "cfg_c_seats", "cfg_c", "number_of_seats", "", 7, "2026-01-01", "src_c", ""),
                (4, "cfg_a_power", "cfg_a", "engine_power", "petrol", 90, "2026-01-01", "src_a", ""),
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
        return root

    def test_unfiltered_shortlist_is_price_sorted_and_reports_unknowns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            report = collect_report(repository, ShortlistCriteria())
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
