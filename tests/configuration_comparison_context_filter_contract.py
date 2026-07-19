from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_comparison as core  # noqa: E402
import configuration_comparison_context as context_filter  # noqa: E402
import dkb  # noqa: E402
from tests.test_configuration_comparison import (  # noqa: E402
    ConfigurationComparisonTests,
)


class ConfigurationComparisonContextFilterContractTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path, Path]:
        return ConfigurationComparisonTests().fixture(root)

    def test_fixture_exposes_catalog_contexts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = core.collect_report(
                repository,
                completeness,
                evidence,
            )

        self.assertEqual(
            context_filter.difference_contexts(report),
            (
                "",
                "fuel_type_code=",
                "market=PL;currency_code=PLN",
            ),
        )

    def test_exact_context_filters_price_and_empty_equipment_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = core.collect_report(
                repository,
                completeness,
                evidence,
            )

        known_contexts = context_filter.difference_contexts(report)
        price_rows = context_filter.difference_csv_rows(
            report,
            difference_context="market=PL;currency_code=PLN",
            known_contexts=known_contexts,
        )
        equipment_rows = context_filter.difference_csv_rows(
            report,
            difference_context="",
            known_contexts=known_contexts,
        )

        self.assertEqual(len(price_rows), 1)
        self.assertEqual(price_rows[0]["domain"], "prices")
        self.assertEqual(price_rows[0]["item_code"], "catalog_gross")
        self.assertEqual(len(equipment_rows), 1)
        self.assertEqual(equipment_rows[0]["domain"], "equipment")
        self.assertEqual(equipment_rows[0]["context"], "")

    def test_context_composes_with_pair_domain_and_item_filters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            full_report = core.collect_report(
                repository,
                completeness,
                evidence,
            )
            filtered_report = core.collect_report(
                repository,
                completeness,
                evidence,
                pair_type_filter=(
                    "different_version_different_transmission"
                ),
            )

        known_items = core.difference_item_codes(full_report)
        known_contexts = context_filter.difference_contexts(full_report)
        rendered = context_filter.render_difference_csv(
            filtered_report,
            "prices",
            "catalog_gross",
            known_items,
            "market=PL;currency_code=PLN",
            known_contexts,
        )
        rows = list(csv.DictReader(rendered.splitlines()))
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["pair_type"],
            "different_version_different_transmission",
        )

        header_only = context_filter.render_difference_csv(
            filtered_report,
            "technical",
            "catalog_gross",
            known_items,
            "market=PL;currency_code=PLN",
            known_contexts,
        )
        self.assertEqual(
            list(csv.DictReader(header_only.splitlines())),
            [],
        )
        self.assertEqual(header_only.count("\n"), 1)

    def test_unknown_context_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = core.collect_report(
                repository,
                completeness,
                evidence,
            )

        with self.assertRaisesRegex(
            core.ComparisonError,
            "unsupported difference context",
        ):
            context_filter.render_difference_csv(
                report,
                difference_context="fuel_type_code=diesel",
                known_contexts=context_filter.difference_contexts(report),
            )

    def test_context_is_validated_against_full_report_before_pair_filter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            full_report = core.collect_report(
                repository,
                completeness,
                evidence,
            )
            empty_report = core.collect_report(
                repository,
                completeness,
                evidence,
                pair_type_filter="same_version_different_transmission",
            )

        rendered = context_filter.render_difference_csv(
            empty_report,
            difference_context="market=PL;currency_code=PLN",
            known_contexts=context_filter.difference_contexts(full_report),
        )
        self.assertEqual(list(csv.DictReader(rendered.splitlines())), [])
        self.assertEqual(rendered.count("\n"), 1)

    def test_wrapper_preserves_json_markdown_and_csv_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, completeness, evidence = self.fixture(root)
            json_path = root / "comparison.json"
            markdown_path = root / "comparison.md"
            html_path = root / "comparison.html"
            csv_path = root / "differences.csv"
            expected_report = core.collect_report(
                repository,
                completeness,
                evidence,
            )

            with mock.patch.object(
                context_filter.core,
                "repository_root",
                return_value=repository,
            ):
                result = context_filter.main(
                    [
                        "--completeness-spec",
                        str(completeness),
                        "--evidence-spec",
                        str(evidence),
                        "--difference-context",
                        "market=PL;currency_code=PLN",
                        "--json",
                        str(json_path),
                        "--markdown",
                        str(markdown_path),
                        "--html",
                        str(html_path),
                        "--csv",
                        str(csv_path),
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(
                json_path.read_text(encoding="utf-8"),
                core.render_json(expected_report),
            )
            self.assertEqual(
                markdown_path.read_text(encoding="utf-8"),
                core.render_markdown(expected_report),
            )
            self.assertEqual(
                html_path.read_text(encoding="utf-8"),
                core.render_html(expected_report),
            )
            reader = csv.DictReader(
                csv_path.read_text(encoding="utf-8").splitlines()
            )
            rows = list(reader)
            self.assertEqual(
                reader.fieldnames,
                list(core.DIFFERENCE_CSV_FIELDS),
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["domain"], "prices")

    def test_unified_cli_routes_only_context_and_help_to_wrapper(self) -> None:
        completed = SimpleNamespace(returncode=0)
        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            self.assertEqual(
                dkb.run_script(
                    "configuration-comparison",
                    [
                        "--difference-context",
                        "fuel_type_code=lpg",
                    ],
                ),
                0,
            )
            self.assertEqual(
                Path(run.call_args.args[0][1]).name,
                "configuration_comparison_context.py",
            )

        with mock.patch.object(
            dkb.subprocess,
            "run",
            return_value=completed,
        ) as run:
            self.assertEqual(
                dkb.run_script(
                    "configuration-comparison",
                    ["--csv", "differences.csv"],
                ),
                0,
            )
            self.assertEqual(
                Path(run.call_args.args[0][1]).name,
                "configuration_comparison.py",
            )

        self.assertIn(
            "--difference-context CONTEXT",
            dkb.SCRIPT_COMMANDS["configuration-comparison"][2],
        )

    def test_repository_snapshot_context_counts_and_default_compatibility(
        self,
    ) -> None:
        report = core.collect_report(
            REPOSITORY,
            REPOSITORY / core.DEFAULT_COMPLETENESS_SPEC,
            REPOSITORY / core.DEFAULT_EVIDENCE_SPEC,
        )
        contexts = context_filter.difference_contexts(report)
        self.assertEqual(
            contexts,
            (
                "",
                "fuel_type_code=",
                "fuel_type_code=lpg",
                "fuel_type_code=petrol",
                "market=PL;currency_code=PLN",
            ),
        )
        self.assertEqual(
            context_filter.render_difference_csv(report),
            core.render_difference_csv(report),
        )
        self.assertEqual(len(core.difference_csv_rows(report)), 305)

        expected_counts = {
            "": 24,
            "fuel_type_code=": 144,
            "fuel_type_code=lpg": 61,
            "fuel_type_code=petrol": 55,
            "market=PL;currency_code=PLN": 21,
        }
        for context, expected in expected_counts.items():
            with self.subTest(context=context):
                self.assertEqual(
                    len(
                        context_filter.difference_csv_rows(
                            report,
                            difference_context=context,
                            known_contexts=contexts,
                        )
                    ),
                    expected,
                )

        known_items = core.difference_item_codes(report)
        for context in (
            "fuel_type_code=lpg",
            "fuel_type_code=petrol",
        ):
            with self.subTest(co2_context=context):
                self.assertEqual(
                    len(
                        context_filter.difference_csv_rows(
                            report,
                            difference_item_code="co2_emissions",
                            known_item_codes=known_items,
                            difference_context=context,
                            known_contexts=contexts,
                        )
                    ),
                    17,
                )


if __name__ == "__main__":
    unittest.main()
