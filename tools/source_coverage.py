#!/usr/bin/env python3
"""Compatibility facade adding explicit configuration reporting subsets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import _source_coverage_base as _base
from _source_coverage_base import *  # noqa: F401,F403
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
        raise SourceCoverageError(str(exc)) from exc


def _scope_spec_as_of(
    spec: dict[str, Any],
    as_of_value: str | None,
) -> dict[str, Any]:
    """Project dated technical-slot scope without weakening base validation."""
    if as_of_value is None:
        return spec

    as_of = _base.iso_date(as_of_value, "--as-of")
    raw_slots = spec.get("technical_slots")
    if not isinstance(raw_slots, list):
        return spec

    scoped_slots: list[Any] = []
    for item in raw_slots:
        if not isinstance(item, dict):
            scoped_slots.append(item)
            continue
        effective_from_value = str(item.get("effective_from", ""))
        if effective_from_value:
            effective_from = _base.iso_date(
                effective_from_value,
                "technical slot effective_from",
            )
            if effective_from > as_of:
                continue
        scoped_slots.append(item)

    return {**spec, "technical_slots": scoped_slots}


def collect_report(
    repository: Path,
    spec_path: Path,
    as_of_value: str | None = None,
) -> dict[str, Any]:
    scope = _resolve(repository, spec_path)
    original_read_json = _base.read_json

    def read_json_as_of(path: Path) -> dict[str, Any]:
        return _scope_spec_as_of(original_read_json(path), as_of_value)

    _base.read_json = read_json_as_of
    try:
        with selected_configuration_reader(_base, repository, scope):
            report = _ORIGINAL_COLLECT(repository, spec_path, as_of_value)
    finally:
        _base.read_json = original_read_json
    report["scope"].update(disclosure(scope))
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    rendered = _ORIGINAL_MARKDOWN(report)
    marker = "| Expected sources |"
    rows = "\n".join(scope_markdown_rows(report["scope"])) + "\n"
    return rendered.replace(marker, rows + marker, 1)


def main(argv: Sequence[str] | None = None) -> int:
    _base.collect_report = collect_report
    _base.render_markdown = render_markdown
    return _ORIGINAL_MAIN(argv)


if __name__ == "__main__":
    raise SystemExit(main())
