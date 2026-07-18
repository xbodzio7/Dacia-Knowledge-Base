"""Shared reporting helpers."""

from reporting import configuration_scope as _scope
from reporting.configuration_scope_runtime import (
    disclosure,
    scope_markdown_rows,
    selected_configuration_reader,
)

_scope.disclosure = disclosure
_scope.scope_markdown_rows = scope_markdown_rows
_scope.selected_configuration_reader = selected_configuration_reader
