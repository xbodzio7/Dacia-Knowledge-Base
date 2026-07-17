from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_comparison as comparison  # noqa: E402
import configuration_comparison_pair_summary as pair_summary  # noqa: E402
from tests.test_configuration_comparison import (  # noqa: E402
    ConfigurationComparisonTests,
)


class ConfigurationComparisonPairSummaryContractTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path, Path]:
        return ConfigurationComparisonTests().fixture(root)

    def test_fixture_summary_uses_existing_pair_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = comparison.collect_report(
                repository,
                completeness,
                evidence,
            )

        rows = pair_summary.pair_summary_rows(report)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["price_comparisons"], "1")
        self.assertEqual(row["price_different"], "1")
        self.assertEqual(row["technical_comparisons"], "3")
        self.assertEqual(row["technical_equal"], "1")
        self.assertEqual(row["technical_not_comparable"], "2")
        self.assertEqual(row["equipment_comparisons"], "2")
        self.assertEqual(row["equipment_different"], "1")
        self.assertEqual(row["equipment_not_comparable"], "1")
        self.assertEqual(row["total_comparisons"], "6")
        self.assertEqual(row["total_equal"], "1")
        self.assertEqual(row["total_different"], "2")
        self.assertEqual(row["total_not_comparable"], "3")

    def test_csv_is_deterministic_and_has_stable_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = comparison.collect_report(
                repository,
                completeness,
                evidence,
            )

        rendered = pair_summary.render_csv(report)
        self.assertEqual(rendered, pair_summary.render_csv(report))
        reader = csv.DictReader(rendered.splitlines())
        rows = list(reader)
        self.assertEqual(
            reader.fieldnames,
            list(pair_summary.PAIR_SUMMARY_FIELDS),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["pair_code"],
            "cfg_a__vs__cfg_b",
        )

    def test_pair_type_filter_produces_header_only_when_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, completeness, evidence = self.fixture(
                Path(directory)
            )
            report = comparison.collect_report(
                repository,
                completeness,
                evidence,
                pair_type_filter="same_version_different_transmission",
            )

        rendered = pair_summary.render_csv(report)
        self.assertEqual(list(csv.DictReader(rendered.splitlines())), [])
        self.assertEqual(rendered.count("\n"), 1)

    def test_cli_writes_pair_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, completeness, evidence = self.fixture(root)
            output = root / "pair-summary.csv"
            with mock.patch.object(
                pair_summary.comparison,
                "repository_root",
                return_value=repository,
            ):
                result = pair_summary.main(
                    [
                        "--completeness-spec",
                        str(completeness),
                        "--evidence-spec",
                        str(evidence),
                        "--csv",
                        str(output),
                    ]
                )

            self.assertEqual(result, 0)
            rows = list(
                csv.DictReader(
                    output.read_text(encoding="utf-8").splitlines()
                )
            )
            self.assertEqual(len(rows), 1)

    def test_repository_snapshot_has_21_pairs_and_expected_types(self) -> None:
        report = comparison.collect_report(
            REPOSITORY,
            REPOSITORY / comparison.DEFAULT_COMPLETENESS_SPEC,
            REPOSITORY / comparison.DEFAULT_EVIDENCE_SPEC,
        )
        rows = pair_summary.pair_summary_rows(report)
        self.assertEqual(len(rows), 21)
        self.assertEqual(
            Counter(row["pair_type"] for row in rows),
            Counter(
                {
                    "different_version_same_transmission": 11,
                    "different_version_different_transmission": 8,
                    "same_version_different_transmission": 2,
                }
            ),
        )
        self.assertEqual(
            {row["total_comparisons"] for row in rows},
            {"115"},
        )
        self.assertEqual(
            sum(int(row["total_different"]) for row in rows),
            305,
        )
        self.assertEqual(
            sum(int(row["price_different"]) for row in rows),
            report["summary"]["prices"]["different"],
        )
        self.assertEqual(
            sum(int(row["technical_different"]) for row in rows),
            report["summary"]["technical"]["different"],
        )
        self.assertEqual(
            sum(int(row["equipment_different"]) for row in rows),
            report["summary"]["equipment"]["different"],
        )


if __name__ == "__main__":
    unittest.main()
