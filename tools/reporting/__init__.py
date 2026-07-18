"""Shared reporting helpers."""

from reporting import configuration_scope as _scope
from reporting.configuration_scope_runtime import (
    disclosure,
    scope_markdown_rows,
    selected_configuration_reader,
)

_original_resolve = _scope.resolve_configuration_scope


def _resolve_with_not_applicable_check(spec, configurations):
    mappings = spec.get("configurations", [])
    selected = {
        item.get("configuration_code", "")
        for item in mappings
        if isinstance(item, dict)
    }
    groups = spec.get("not_applicable", {})
    referenced = {
        item.get("configuration_code", "")
        for group in ("technical", "equipment")
        for item in groups.get(group, [])
        if isinstance(groups, dict) and isinstance(item, dict)
    }
    outside = sorted(referenced - selected)
    if outside:
        raise _scope.ConfigurationScopeError(
            "spec configurations differ from explicit reporting subset: "
            f"not_applicable references {outside}"
        )
    return _original_resolve(spec, configurations)


_scope.resolve_configuration_scope = _resolve_with_not_applicable_check
_scope.disclosure = disclosure
_scope.scope_markdown_rows = scope_markdown_rows
_scope.selected_configuration_reader = selected_configuration_reader
