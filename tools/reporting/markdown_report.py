"""
Markdown report generator for validation results.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


def write_validation_report(
    output: Path,
    repository_ok: bool,
    csv_ok: bool,
    statistics: dict[str, Any],
    uniqueness_ok: bool = True,
    uniqueness_errors: Sequence[str] = (),
    references_ok: bool = True,
    reference_errors: Sequence[str] = (),
    year_ranges_ok: bool = True,
    year_range_errors: Sequence[str] = (),
    statuses_ok: bool = True,
    status_errors: Sequence[str] = (),
    association_ranges_ok: bool = True,
    association_range_errors: Sequence[str] = (),
    association_intervals_ok: bool = True,
    association_interval_errors: Sequence[str] = (),
) -> None:
    """Generate a Markdown validation report."""

    output.parent.mkdir(parents=True, exist_ok=True)

    overall_ok = (
        repository_ok
        and csv_ok
        and uniqueness_ok
        and references_ok
        and year_ranges_ok
        and statuses_ok
        and association_ranges_ok
        and association_intervals_ok
    )

    with output.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        handle.write("# DKB Validation Report\n\n")
        handle.write(
            f"**Generated:** "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            "\n\n"
        )

        handle.write("## Status\n\n")
        handle.write(
            f"- Overall validation: "
            f"**{'PASS' if overall_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Repository structure: "
            f"**{'PASS' if repository_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- CSV files validation: "
            f"**{'PASS' if csv_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Key uniqueness: "
            f"**{'PASS' if uniqueness_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Cross-file references: "
            f"**{'PASS' if references_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Year ranges: "
            f"**{'PASS' if year_ranges_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Lifecycle statuses: "
            f"**{'PASS' if statuses_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Association ranges: "
            f"**{'PASS' if association_ranges_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Association interval uniqueness: "
            f"**{'PASS' if association_intervals_ok else 'FAIL'}**"
            "\n\n"
        )

        if uniqueness_errors:
            handle.write("## Uniqueness errors\n\n")

            for error in uniqueness_errors:
                handle.write(f"- {error}\n")

            handle.write("\n")

        if reference_errors:
            handle.write("## Reference errors\n\n")

            for error in reference_errors:
                handle.write(f"- {error}\n")

            handle.write("\n")

        if year_range_errors:
            handle.write("## Year range errors\n\n")

            for error in year_range_errors:
                handle.write(f"- {error}\n")

            handle.write("\n")

        if status_errors:
            handle.write("## Status errors\n\n")

            for error in status_errors:
                handle.write(f"- {error}\n")

            handle.write("\n")

        if association_range_errors:
            handle.write("## Association range errors\n\n")

            for error in association_range_errors:
                handle.write(f"- {error}\n")

            handle.write("\n")

        if association_interval_errors:
            handle.write("## Association interval errors\n\n")

            for error in association_interval_errors:
                handle.write(f"- {error}\n")

            handle.write("\n")

        handle.write("## Statistics\n\n")
        handle.write(
            f"- CSV files: "
            f"{statistics.get('csv_files', 0)}\n"
        )
        handle.write(
            f"- Total rows: "
            f"{statistics.get('rows', 0)}\n"
        )
        handle.write(
            f"- Empty files: "
            f"{statistics.get('empty_files', 0)}"
            "\n\n"
        )

        handle.write("## Largest datasets\n\n")

        for dataset in statistics.get("datasets", [])[:15]:
            handle.write(
                f"- `{dataset['name']}` — "
                f"{dataset['rows']} rows "
                f"({dataset['columns']} cols, "
                f"{dataset['completeness']}% filled)\n"
            )

        handle.write("\n---\n")
        handle.write(
            "Report generated automatically "
            "by DKB Validator.\n"
        )
