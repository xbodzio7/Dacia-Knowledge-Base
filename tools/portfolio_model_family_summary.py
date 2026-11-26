#!/usr/bin/env python3
"""Generate deterministic portfolio model-family summaries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.portfolio_model_family_summary import (
    PortfolioModelFamilySummaryError,
    collect_summary,
    render_html,
    render_json,
    render_markdown,
    repository_root,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate JSON, Markdown and standalone HTML summaries for the "
            "current source-backed model families without cross-scope pairs."
        )
    )
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--html", type=Path)
    arguments = parser.parse_args(argv)
    if not any((arguments.json, arguments.markdown, arguments.html)):
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
        summary = collect_summary(selected_repository)
        if arguments.json is not None:
            _write(arguments.json, render_json(summary))
        if arguments.markdown is not None:
            _write(arguments.markdown, render_markdown(summary))
        if arguments.html is not None:
            _write(arguments.html, render_html(summary))
    except (PortfolioModelFamilySummaryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    totals = summary["summary"]
    print("Portfolio model-family summary")
    print("------------------------------")
    print(f"Model families        : {totals['model_family_count']}")
    print(f"Active configurations : {totals['active_configuration_count']}")
    print(f"Reporting scopes      : {totals['reporting_scope_count']}")
    print(f"Provenance sources    : {totals['provenance_source_count']}")
    print(f"Source relationships  : {totals['source_configuration_relationship_count']}")
    print("Cross-scope pairs     : none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
