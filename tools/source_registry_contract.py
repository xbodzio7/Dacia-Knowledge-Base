"""Shared comparison rules for duplicated source-registry metadata."""

from __future__ import annotations

from collections.abc import Mapping


# Structured source identity is canonical in data/master/sources.csv.
# The free-form notes field is editorial provenance and is intentionally excluded.
SOURCE_REGISTRY_IDENTITY_FIELDS = (
    "id",
    "code",
    "source_type",
    "title",
    "publisher",
    "market",
    "document_date",
    "external_reference",
    "file_path",
    "sha256",
    "status",
)


def source_registry_identity_differences(
    expected: Mapping[str, object],
    actual: Mapping[str, object],
) -> dict[str, tuple[str, str]]:
    """Return structured identity differences; explanatory notes are not identity."""
    differences: dict[str, tuple[str, str]] = {}
    for field in SOURCE_REGISTRY_IDENTITY_FIELDS:
        expected_value = str(expected.get(field, ""))
        actual_value = str(actual.get(field, ""))
        if expected_value != actual_value:
            differences[field] = (expected_value, actual_value)
    return differences


def source_registry_identity_matches(
    expected: Mapping[str, object],
    actual: Mapping[str, object],
) -> bool:
    """Compare source identity while allowing editorial notes to evolve."""
    return not source_registry_identity_differences(expected, actual)
