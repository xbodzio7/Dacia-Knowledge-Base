"""
Markdown report generator for validation results.
"""

from pathlib import Path
from datetime import datetime
from typing import Any


def write_validation_report(
    output: Path,
    repository_ok: bool,
    csv_ok: bool,
    statistics: dict[str, Any],
) -> None:
    """Generate a markdown validation report."""
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as f:
        f.write("# DKB Validation Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Status\n\n")
        f.write(f"- Repository structure: **{'PASS' if repository_ok else 'FAIL'}**\n")
        f.write(f"- CSV files validation: **{'PASS' if csv_ok else 'FAIL'}**\n\n")

        f.write("## Statistics\n\n")
        f.write(f"- CSV files: {statistics.get('csv_files', 0)}\n")
        f.write(f"- Total rows: {statistics.get('rows', 0)}\n")
        f.write(f"- Empty files: {statistics.get('empty_files', 0)}\n\n")

        f.write("## Largest datasets\n\n")
        for dataset in statistics.get("datasets", [])[:15]:
            f.write(
                f"- `{dataset['name']}` — {dataset['rows']} rows "
                f"({dataset['columns']} cols, {dataset['completeness']}% filled)\n"
            )

        f.write("\n---\n")
        f.write("Report generated automatically by DKB Validator.\n")
