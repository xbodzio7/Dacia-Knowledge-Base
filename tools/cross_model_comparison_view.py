#!/usr/bin/env python3
"""Generate a scope-preserving cross-model navigation view."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.cross_model_comparison_view import (
    CrossModelViewError,
    collect_view,
    render_html,
    render_json,
    repository_root,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic JSON and standalone HTML navigation over "
            "the existing reporting scopes without cross-scope pairs."
        )
    )
    parser.add_argument("--json", type=Path, help="Write the deterministic JSON view.")
    parser.add_argument("--html", type=Path, help="Write the standalone HTML view.")
    arguments = parser.parse_args(argv)
    if arguments.json is None and arguments.html is None:
        parser.error("at least one of --json or --html is required")
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
        view = collect_view(selected_repository)
        if arguments.json is not None:
            _write(arguments.json, render_json(view))
        if arguments.html is not None:
            _write(arguments.html, render_html(view))
    except (CrossModelViewError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = view["summary"]
    assert isinstance(summary, dict)
    print("Cross-model comparison view")
    print("---------------------------")
    print(f"Model families        : {summary['model_family_count']}")
    print(f"Reporting scopes      : {summary['reporting_scope_count']}")
    print(f"Active configurations : {summary['active_configuration_count']}")
    print(f"Within-scope pairs    : {summary['within_scope_pair_count']}")
    print("Cross-scope pairs     : none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
