#!/usr/bin/env python3
"""Generate deterministic portfolio source-coverage matrices."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.portfolio_source_coverage_matrix import (
    PortfolioSourceCoverageMatrixError,
    collect_matrix,
    render_csv,
    render_html,
    render_json,
    repository_root,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate JSON, CSV and standalone HTML outputs with one row per "
            "used provenance source."
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
    except (PortfolioSourceCoverageMatrixError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = matrix["summary"]
    print("Portfolio source coverage matrix")
    print("--------------------------------")
    print(f"Used provenance sources : {summary['provenance_source_count']}")
    print(
        "Source relationships    : "
        f"{summary['source_configuration_relationship_count']}"
    )
    print(f"Active configurations   : {summary['active_configuration_count']}")
    print(f"Active versions         : {summary['active_version_count']}")
    print(f"Model families          : {summary['model_family_count']}")
    print("Source scoring          : none")
    print("Rankings                : none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
