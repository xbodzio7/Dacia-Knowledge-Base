"""Runtime adapters and disclosure fields for reporting subsets."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any, Iterator, Mapping

from reporting.configuration_scope import ConfigurationScope


def disclosure(scope: ConfigurationScope) -> dict[str, Any]:
    """Return stable fields shared by report scope objects."""

    return {
        "configuration_scope": scope.mode,
        "reporting_configurations": len(scope.selected_codes),
        "reporting_configuration_codes": list(scope.selected_codes),
        "repository_status_configurations": len(scope.status_codes),
        "excluded_configurations": len(scope.excluded_codes),
        "excluded_configuration_codes": list(scope.excluded_codes),
    }


@contextmanager
def selected_configuration_reader(
    module: ModuleType,
    repository: Path,
    scope: ConfigurationScope,
) -> Iterator[None]:
    """Hide unselected rows with the report status from legacy readers."""

    original = module.read_csv
    configuration_path = (
        repository / "data" / "master" / "configurations.csv"
    ).resolve()
    selected = set(scope.selected_codes)

    def read_csv(path: Path) -> list[dict[str, str]]:
        rows = original(path)
        if path.resolve() != configuration_path:
            return rows
        return [
            row
            for row in rows
            if row.get("status") != scope.status
            or row.get("code") in selected
        ]

    module.read_csv = read_csv
    try:
        yield
    finally:
        module.read_csv = original


def scope_markdown_rows(scope: Mapping[str, Any]) -> list[str]:
    """Return common Markdown disclosure rows."""

    return [
        f"| Configuration scope | `{scope['configuration_scope']}` |",
        f"| Reporting configurations | {scope['reporting_configurations']} |",
        (
            "| Repository configurations with selected status | "
            f"{scope['repository_status_configurations']} |"
        ),
        f"| Excluded configurations | {scope['excluded_configurations']} |",
    ]
