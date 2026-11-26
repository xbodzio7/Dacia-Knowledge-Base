#!/usr/bin/env python3
"""Compatibility facade adding explicit configuration reporting subsets."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import _configuration_comparison_base as _base
from _configuration_comparison_base import *  # noqa: F401,F403
from reporting.configuration_comparison_html import render_html
from reporting.configuration_scope import (
    ConfigurationScopeError,
    disclosure,
    resolve_configuration_scope,
    scope_markdown_rows,
    selected_configuration_reader,
)

_ORIGINAL_COLLECT = _base.collect_report
_ORIGINAL_MARKDOWN = _base.render_markdown
_ORIGINAL_MAIN = _base.main


def _resolve(repository: Path, spec_path: Path):
    spec = _base.read_json(spec_path)
    configurations = _base.read_csv(
        repository / "data" / "master" / "configurations.csv"
    )
    try:
        return resolve_configuration_scope(spec, configurations)
    except ConfigurationScopeError as exc:
        raise ComparisonError(str(exc)) from exc


def collect_report(
    repository: Path,
    completeness_spec: Path,
    evidence_spec: Path,
    as_of_value: str | None = None,
    pair_type_filter: str | None = None,
) -> dict[str, Any]:
    scope = _resolve(repository, completeness_spec)
    with selected_configuration_reader(_base, repository, scope):
        report = _ORIGINAL_COLLECT(
            repository,
            completeness_spec,
            evidence_spec,
            as_of_value,
            pair_type_filter,
        )
    report["scope"].update(disclosure(scope))
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    rendered = _ORIGINAL_MARKDOWN(report)
    legacy = (
        f"| Active configurations | "
        f"{report['scope']['active_configurations']} |"
    )
    rows = "\n".join(scope_markdown_rows(report["scope"]))
    return rendered.replace(legacy, rows, 1)


def _extract_html_argument(
    argv: Sequence[str],
) -> tuple[list[str], Path | None]:
    remaining: list[str] = []
    html_path: Path | None = None
    index = 0
    while index < len(argv):
        argument = argv[index]
        value: str | None = None
        if argument == "--html":
            index += 1
            if index >= len(argv):
                raise ComparisonError("--html requires a path")
            value = argv[index]
        elif argument.startswith("--html="):
            value = argument.split("=", 1)[1]
        else:
            remaining.append(argument)
        if value is not None:
            if not value:
                raise ComparisonError("--html requires a path")
            if html_path is not None:
                raise ComparisonError("--html may be provided only once")
            html_path = Path(value)
        index += 1
    return remaining, html_path


def _write_html(argv: Sequence[str], html_path: Path) -> None:
    arguments = _base.parse_args(argv)
    repository = _base.repository_root()
    completeness_spec = arguments.completeness_spec
    evidence_spec = arguments.evidence_spec
    if not completeness_spec.is_absolute():
        completeness_spec = repository / completeness_spec
    if not evidence_spec.is_absolute():
        evidence_spec = repository / evidence_spec
    report = collect_report(
        repository,
        completeness_spec,
        evidence_spec,
        arguments.as_of,
        arguments.pair_type,
    )
    _base.write_atomic(html_path, render_html(report))
    print(f"HTML configuration comparison report written to {html_path}")


def main(argv: Sequence[str] | None = None) -> int:
    raw_arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        arguments, html_path = _extract_html_argument(raw_arguments)
    except ComparisonError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    _base.collect_report = collect_report
    _base.render_markdown = render_markdown
    try:
        result = _ORIGINAL_MAIN(arguments)
    except SystemExit:
        if "--help" in arguments or "-h" in arguments:
            print("  --html FILE             Write a self-contained interactive HTML report.")
        raise
    if result != 0 or html_path is None:
        return result
    try:
        _write_html(arguments, html_path)
    except (ComparisonError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
