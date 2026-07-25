from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

import test_source_coverage as source_coverage_tests

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))
import source_coverage as coverage  # noqa: E402


class SourceCoverageRepositoryAsOfTests(unittest.TestCase):
    def test_unscoped_newer_observation_advances_report_date(self) -> None:
        helper = source_coverage_tests.SourceCoverageTests(
            methodName="test_reports_registered_sources_and_record_gaps"
        )
        with tempfile.TemporaryDirectory() as directory:
            repository, spec = helper.fixture(Path(directory))
            master = repository / "data" / "master"

            configurations = master / "configurations.csv"
            with configurations.open(
                "a",
                encoding="utf-8",
                newline="",
            ) as handle:
                csv.writer(handle).writerow(
                    ["3", "cfg_outside_scope", "ver_outside", "active"]
                )

            values = master / "configuration_attribute_values.csv"
            with values.open("a", encoding="utf-8", newline="") as handle:
                csv.writer(handle).writerow(
                    [
                        "3",
                        "outside_power",
                        "cfg_outside_scope",
                        "engine_power",
                        "",
                        "110",
                        "2026-06-02",
                        "src_a",
                        "newer repository observation outside selected scope",
                    ]
                )

            report = coverage.collect_report(repository, spec)

        self.assertEqual(report["as_of"], "2026-06-02")
        self.assertEqual(report["scope"]["reporting_configurations"], 2)
        self.assertEqual(report["records"]["technical"]["present"], 2)


if __name__ == "__main__":
    unittest.main()
