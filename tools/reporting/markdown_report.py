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
    attributes_ok: bool = True,
    references_ok: bool = True,
    reference_errors: Sequence[str] = (),
) -> None:
    """Generate a Markdown validation report."""

    output.parent.mkdir(parents=True, exist_ok=True)

    overall_ok = (
        repository_ok
        and csv_ok
        and attributes_ok
        and references_ok
    )

    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("# DKB Validation Report\n\n")
        handle.write(
            f"**Generated:** "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
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
            f"- Attribute uniqueness: "
            f"**{'PASS' if attributes_ok else 'FAIL'}**\n"
        )
        handle.write(
            f"- Cross-file references: "
            f"**{'PASS' if references_ok else 'FAIL'}**\n\n"
        )

        if reference_errors:
            handle.write("## Reference errors\n\n")

            for error in reference_errors:
                handle.write(f"- {error}\n")

            handle.write("\n")

        handle.write("## Statistics\n\n")
        handle.write(
            f"- CSV files: {statistics.get('csv_files', 0)}\n"
        )
        handle.write(
            f"- Total rows: {statistics.get('rows', 0)}\n"
        )
        handle.write(
            f"- Empty files: {statistics.get('empty_files', 0)}\n\n"
        )

        handle.write("## Largest datasets\n\n")

        for dataset in statistics.get("datasets", [])[:15]:
            handle.write(
                f"- `{dataset['name']}` — {dataset['rows']} rows "
                f"({dataset['columns']} cols, "
                f"{dataset['completeness']}% filled)\n"
            )

        handle.write("\n---\n")
        handle.write(
            "Report generated automatically by DKB Validator.\n"
        )
