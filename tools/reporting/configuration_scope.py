"""Shared validation for declarative configuration-reporting subsets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


EXPLICIT_SUBSET = "explicit_subset"


class ConfigurationScopeError(RuntimeError):
    """Raised when a reporting specification selects an invalid scope."""


@dataclass(frozen=True)
class ConfigurationScope:
    """Resolved configuration subset and repository-wide disclosure data."""

    mode: str
    status: str
    configuration_sources: dict[str, str]
    selected_rows: dict[str, dict[str, str]]
    status_codes: tuple[str, ...]
    excluded_codes: tuple[str, ...]

    @property
    def selected_codes(self) -> tuple[str, ...]:
        return tuple(sorted(self.configuration_sources))


def resolve_configuration_scope(
    spec: Mapping[str, Any],
    configurations: Sequence[dict[str, str]],
) -> ConfigurationScope:
    """Resolve an explicit reporting subset without auto-enrolling new rows."""

    mode = spec.get("configuration_scope", EXPLICIT_SUBSET)
    if mode != EXPLICIT_SUBSET:
        raise ConfigurationScopeError(
            "configuration_scope must equal 'explicit_subset'"
        )

    status = spec.get("configuration_status")
    if not isinstance(status, str) or not status:
        raise ConfigurationScopeError("configuration_status must be non-empty")

    rows_by_code: dict[str, dict[str, str]] = {}
    for row in configurations:
        code = row.get("code", "")
        if code and code not in rows_by_code:
            rows_by_code[code] = row

    raw_mappings = spec.get("configurations")
    if not isinstance(raw_mappings, list) or not raw_mappings:
        raise ConfigurationScopeError(
            "configurations must be a non-empty list"
        )

    configuration_sources: dict[str, str] = {}
    selected_rows: dict[str, dict[str, str]] = {}
    for item in raw_mappings:
        if not isinstance(item, dict):
            raise ConfigurationScopeError(
                "configuration entries must be objects"
            )
        code = item.get("configuration_code")
        source = item.get("source_code")
        if not isinstance(code, str) or not code:
            raise ConfigurationScopeError(
                "configuration_code must be non-empty"
            )
        if not isinstance(source, str) or not source:
            raise ConfigurationScopeError("source_code must be non-empty")
        if code in configuration_sources:
            raise ConfigurationScopeError(
                f"duplicate configuration in reporting scope: {code}"
            )

        row = rows_by_code.get(code)
        if row is None:
            raise ConfigurationScopeError(
                f"reporting configuration is missing: {code}"
            )
        actual_status = row.get("status", "")
        if actual_status != status:
            raise ConfigurationScopeError(
                "reporting configuration status differs from declared scope: "
                f"{code} ({actual_status!r} != {status!r})"
            )

        configuration_sources[code] = source
        selected_rows[code] = row

    status_codes = tuple(
        sorted(
            row.get("code", "")
            for row in configurations
            if row.get("status") == status and row.get("code")
        )
    )
    excluded_codes = tuple(
        code for code in status_codes if code not in configuration_sources
    )

    return ConfigurationScope(
        mode=EXPLICIT_SUBSET,
        status=status,
        configuration_sources=configuration_sources,
        selected_rows=selected_rows,
        status_codes=status_codes,
        excluded_codes=excluded_codes,
    )
