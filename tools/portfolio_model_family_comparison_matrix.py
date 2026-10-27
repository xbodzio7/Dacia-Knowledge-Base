#!/usr/bin/env python3
"""Generate deterministic portfolio model-family comparison matrices."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.portfolio_model_family_comparison_matrix import (
    PortfolioModelFamilyComparisonMatrixError,
    collect_matrix,
    render_csv,
    render_html,
    render_json,
    repository_root,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate JSON, CSV and standalone HTML model-family comparison "
            "outputs from the verified portfolio family summary."
        )
    )
    parser.add_argument("--json", type=Path)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--html", type=Path)
    arguments = parser.parse_args(argv)
    if not any((arguments.json, arguments.csv, arguments.html)):
        parser.error("at least one output path is required")
    return arguments


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


def main(
    argv: Sequence[str] | None = None,
    repository: Path | None = None,
) -> int:
    arguments = parse_args(argv)
    selected_repository = repository if repository is not None else repository_root()
    try:
        matrix = collect_matrix(selected_repository)
        if arguments.json is not None:
            _write(arguments.json, render_json(matrix))
        if arguments.csv is not None:
            _write(arguments.csv, render_csv(matrix))
        if arguments.html is not None:
            _write(arguments.html, render_html(matrix))
    except (PortfolioModelFamilyComparisonMatrixError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    totals = matrix["summary"]
    print("Portfolio model-family comparison matrix")
    print("----------------------------------------")
    print(f"Model families        : {totals['model_family_count']}")
    print(f"Active configurations : {totals['active_configuration_count']}")
    print(f"Reporting scopes      : {totals['reporting_scope_count']}")
    print(f"Source relationships  : {totals['source_configuration_relationship_count']}")
    print("Cross-scope pairs     : none")
    print("Rankings              : none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
