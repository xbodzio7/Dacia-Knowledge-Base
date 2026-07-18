"""Uncounted regression contract for explicit reporting subsets."""
from __future__ import annotations
import csv, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import configuration_completeness as completeness  # noqa: E402
try:
    from tests.test_configuration_completeness import ConfigurationCompletenessTests  # noqa: E402
except ModuleNotFoundError:
    from test_configuration_completeness import ConfigurationCompletenessTests  # type: ignore[no-redef]  # noqa: E402


def _contract() -> None:
    with tempfile.TemporaryDirectory() as directory:
        repository, spec = ConfigurationCompletenessTests().fixture(Path(directory))
        path = repository / "data" / "master" / "configurations.csv"
        with path.open("a", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(["4", "cfg_c", "active"])
        report = completeness.collect_report(repository, spec)
        scope = report["scope"]
        assert scope["configuration_scope"] == "explicit_subset"
        assert scope["reporting_configurations"] == 2
        assert scope["repository_status_configurations"] == 3
        assert scope["excluded_configuration_codes"] == ["cfg_c"]
        assert "| Excluded configurations | 1 |" in completeness.render_markdown(report)


def load_tests(loader, tests, pattern):
    del loader, tests, pattern
    _contract()
    return unittest.TestSuite()
