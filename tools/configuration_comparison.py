#!/usr/bin/env python3
"""Compatibility facade adding explicit configuration reporting subsets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import _configuration_comparison_base as _base
from _configuration_comparison_base import *  # noqa: F401,F403
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


def main(argv: Sequence[str] | None = None) -> int:
    _base.collect_report = collect_report
    _base.render_markdown = render_markdown
    return _ORIGINAL_MAIN(argv)


if __name__ == "__main__":
    raise SystemExit(main())
