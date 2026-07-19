from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from reporting.configuration_comparison_workbook_rows import build_sheets
from reporting.deterministic_xlsx_sheet import write_workbook

WORKBOOK_FILENAME = "configuration-comparison-workbook.xlsx"


def write_bundle_workbook(
    repository: Path,
    build_root: Path,
    manifest: Mapping[str, Any],
) -> Path:
    path = build_root / WORKBOOK_FILENAME
    write_workbook(path, build_sheets(repository, build_root, manifest))
    return path
