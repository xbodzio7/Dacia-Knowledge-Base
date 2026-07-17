from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))
import configuration_comparison as comparison  # noqa: E402


class ConfigurationComparisonTests(unittest.TestCase):
    def write_csv(
        self,
        path: Path,
        header: list[str],
        rows: list[list[str]],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def fixture(self, root: Path) -> tuple[Path, Path, Path]:
        repository = root / "repository"
        master = repository / "data" / "master"
        reporting = repository / "data" / "reporting"
        reporting.mkdir(parents=True)

        self.write_csv(
            master / "configurations.csv",
            [
                "id",
                "code",
                "version_code",
                "powertrain_label",
                "transmission_type",
                "status",
                "notes",
            ],
            [
                [
                    "1",
                    "cfg_a",
                    "version_a",
                    "Powertrain",
                    "manual",
                    "active",
                    "",
                ],
                [
                    "2",
                    "cfg_b",
                    "version_b",
                    "Powertrain",
                    "automatic",
                    "active",
                    "",
                ],
            ],
        )
        self.write_csv(
            master / "sources.csv",
            ["id", "code", "status"],
            [
                ["1", "src_a", "active"],
                ["2", "src_b", "active"],
            ],
        )
        self.write_csv(
            master / "attributes.csv",
            [
                "id",
                "code",
                "category",
                "name",
                "data_type",
                "unit",
                "description",
                "status",
            ],
            [
                [
                    "1",
                    "engine_power",
                    "Engine",
                    "Power",
                    "integer",
                    "kW",
                    "",
                    "active",
                ],
                [
                    "2",
                    "engine_torque",
                    "Engine",
                    "Torque",
                    "integer",
                    "Nm",
                    "",
                    "active",
                ],
                [
                    "3",
                    "vehicle_height",
                    "Dimensions",
                    "Height",
                    "integer",
                    "mm",
                    "",
                    "active",
                ],
                [
                    "4",
                    "fog_lights",
                    "Lighting",
                    "Fog lights",
                    "boolean",
                    "",
                    "",
                    "active",
                ],
                [
                    "5",
                    "heated_seat",
                    "Comfort",
                    "Heated seat",
                    "boolean",
                    "",
                    "",
                    "active",
                ],
            ],
        )
        self.write_csv(
            master / "configuration_prices.csv",
            [
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
            ],
            [
                [
                    "1",
                    "a_old",
                    "cfg_a",
                    "PL",
                    "catalog_gross",
                    "90",
                    "PLN",
                    "2026-01-01",
                    "src_a",
                    "",
                ],
                [
                    "2",
                    "a",
                    "cfg_a",
                    "PL",
                    "catalog_gross",
                    "100",
                    "PLN",
                    "2026-06-01",
                    "src_a",
                    "",
                ],
                [
                    "3",
                    "b",
                    "cfg_b",
                    "PL",
                    "catalog_gross",
                    "120",
                    "PLN",
                    "2026-06-01",
                    "src_b",
                    "",
                ],
            ],
        )
        self.write_csv(
            master / "configuration_attribute_values.csv",
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "fuel_type_code",
                "value",
                "observation_date",
                "source_code",
                "notes",
            ],
            [
                [
                    "1",
                    "a_power_old",
                    "cfg_a",
                    "engine_power",
                    "",
                    "90",
                    "2026-01-01",
                    "src_a",
                    "",
                ],
                [
                    "2",
                    "a_power",
                    "cfg_a",
                    "engine_power",
                    "",
                    "100",
                    "2026-06-01",
                    "src_a",
                    "",
                ],
                [
                    "3",
                    "b_power",
                    "cfg_b",
                    "engine_power",
                    "",
                    "100",
                    "2026-06-01",
                    "src_b",
                    "",
                ],
                [
                    "4",
                    "a_torque",
                    "cfg_a",
                    "engine_torque",
                    "",
                    "180",
                    "2026-06-01",
                    "src_a",
                    "",
                ],
            ],
        )
        self.write_csv(
            master / "configuration_attribute_availability.csv",
            [
                "id",
                "code",
                "configuration_code",
                "attribute_code",
                "availability_status",
                "observation_date",
                "source_code",
                "notes",
            ],
            [
                [
                    "1",
                    "a_fog",
                    "cfg_a",
                    "fog_lights",
                    "standard",
                    "2026-06-01",
                    "src_a",
                    "",
                ],
                [
                    "2",
                    "b_fog",
                    "cfg_b",
                    "fog_lights",
                    "not_available",
                    "2026-06-01",
                    "src_b",
                    "",
                ],
                [
                    "3",
                    "b_heated",
                    "cfg_b",
                    "heated_seat",
                    "standard",
                    "2026-06-01",
                    "src_b",
                    "",
                ],
            ],
        )

        completeness = {
            "version": 1,
            "configuration_status": "active",
            "configurations": [
                {
                    "configuration_code": "cfg_a",
                    "source_code": "src_a",
                },
                {
                    "configuration_code": "cfg_b",
                    "source_code": "src_b",
                },
            ],
            "technical_slots": [
                {
                    "attribute_code": "engine_power",
                    "fuel_type_code": "",
                },
                {
                    "attribute_code": "engine_torque",
                    "fuel_type_code": "",
                },
                {
                    "attribute_code": "vehicle_height",
                    "fuel_type_code": "",
                },
            ],
            "equipment_attributes": [
                "fog_lights",
                "heated_seat",
            ],
            "not_applicable": {
                "technical": [
                    {
                        "configuration_code": "cfg_b",
                        "attribute_code": "engine_torque",
                        "fuel_type_code": "",
                    }
                ],
                "equipment": [],
            },
        }
        completeness_path = (
            reporting / "configuration_completeness.json"
        )
        completeness_path.write_text(
            json.dumps(completeness, indent=2) + "\n",
            encoding="utf-8",
        )

        evidence = {
            "version": 1,
            "as_of": "2026-06-01",
            "review_scope": "source_page_evidence",
            "review_policy": {
                "allowed_classifications": [
                    "ambiguous",
                    "found",
                    "not_stated",
                    "out_of_scope",
                ],
                "auto_import": False,
            },
            "decisions": [
                {
                    "domain": "technical",
                    "configuration_code": "cfg_a",
                    "attribute_code": "vehicle_height",
                    "fuel_type_code": "",
                    "classification": "not_stated",
                    "reason_code": "not_stated",
                    "source_code": "src_a",
                    "reviewed_pages": [1],
                },
                {
                    "domain": "technical",
                    "configuration_code": "cfg_b",
                    "attribute_code": "vehicle_height",
                    "fuel_type_code": "",
                    "classification": "out_of_scope",
                    "reason_code": "alternative",
                    "source_code": "src_b",
                    "reviewed_pages": [1],
                    "basis": {
                        "type": "configuration_field",
                        "value": "alternative",
                    },
                },
                {
                    "domain": "equipment",
                    "configuration_code": "cfg_a",
                    "attribute_code": "heated_seat",
                    "fuel_type_code": "",
                    "classification": "not_stated",
                    "reason_code": "not_stated",
                    "source_code": "src_a",
                    "reviewed_pages": [2],
                },
            ],
        }
        evidence_path = reporting / "configuration_gap_evidence.json"
        evidence_path.write_text(
            json.dumps(evidence, indent=2) + "\n",
            encoding="utf-8",
        )
        return repository, completeness_path, evidence_path

    def test_distinguishes_recorded_differences_and_evidence_states(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = comparison.collect_report(
                repository,
                completeness,
                evidence,
            )

        self.assertEqual(report["scope"]["active_configurations"], 2)
        self.assertEqual(report["scope"]["pair_count"], 1)
        self.assertEqual(report["summary"]["prices"]["different"], 1)
        self.assertEqual(report["summary"]["technical"]["equal"], 1)
        self.assertEqual(
            report["summary"]["technical"]["not_comparable"],
            2,
        )
        self.assertEqual(
            report["summary"]["equipment"]["different"],
            1,
        )
        self.assertEqual(
            report["summary"]["equipment"]["not_comparable"],
            1,
        )
        self.assertEqual(
            report["evidence_summary"],
            {
                "total": 3,
                "ambiguous": 0,
                "found": 0,
                "not_stated": 2,
                "out_of_scope": 1,
            },
        )
        pair = report["pairs"][0]
        self.assertEqual(
            pair["prices"][0]["left"]["amount"],
            "100",
        )
        self.assertEqual(
            pair["prices"][0]["amount_delta_right_minus_left"],
            "20",
        )

    def test_deterministic_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = comparison.collect_report(
                repository,
                completeness,
                evidence,
            )

        rendered = comparison.render_json(report)
        self.assertEqual(rendered, comparison.render_json(report))
        self.assertNotIn("generated_at", rendered)
        markdown = comparison.render_markdown(report)
        self.assertIn("# Configuration Comparison Report", markdown)
        self.assertIn("`different_version_different_transmission`", markdown)
        self.assertIn("`fog_lights`", markdown)
        self.assertIn("not_stated=2", markdown)

    def test_rejects_evidence_scope_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            payload["decisions"].pop()
            evidence.write_text(
                json.dumps(payload),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                comparison.ComparisonError,
                "evidence decisions differ",
            ):
                comparison.collect_report(
                    repository,
                    completeness,
                    evidence,
                )

    def test_rejects_duplicate_current_price(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            path = (
                repository
                / "data"
                / "master"
                / "configuration_prices.csv"
            )
            with path.open("a", encoding="utf-8", newline="") as handle:
                csv.writer(handle).writerow(
                    [
                        "4",
                        "a_duplicate",
                        "cfg_a",
                        "PL",
                        "catalog_gross",
                        "101",
                        "PLN",
                        "2026-06-01",
                        "src_a",
                        "",
                    ]
                )
            with self.assertRaisesRegex(
                comparison.ComparisonError,
                "duplicate current records",
            ):
                comparison.collect_report(
                    repository,
                    completeness,
                    evidence,
                )


if __name__ == "__main__":
    unittest.main()
