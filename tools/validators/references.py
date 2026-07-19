"""
Cross-reference validation between Dacia Knowledge Base CSV files.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:
    from validators.enum_domains import validate_enum_domains
except ModuleNotFoundError:  # package import in unit tests
    from tools.validators.enum_domains import validate_enum_domains


@dataclass(frozen=True)
class ReferenceRule:
    """Describe one CSV foreign-key-like relationship."""

    source_file: str
    source_column: str
    target_file: str
    target_column: str = "code"
    allow_empty: bool = False


REFERENCE_RULES: tuple[ReferenceRule, ...] = (
    ReferenceRule(
        "data/master/models.csv",
        "body_type_code",
        "data/master/body_types.csv",
    ),
    ReferenceRule(
        "data/master/models.csv",
        "segment_code",
        "data/master/segments.csv",
    ),
    ReferenceRule(
        "data/master/engines.csv",
        "engine_type",
        "data/master/enums/engine_types.csv",
    ),
    ReferenceRule(
        "data/master/engines.csv",
        "induction",
        "data/master/enums/aspiration_types.csv",
    ),
    ReferenceRule(
        "data/master/engines.csv",
        "fuel_type",
        "data/master/enums/fuel_types.csv",
    ),
    ReferenceRule(
        "data/master/engines.csv",
        "emission_standard",
        "data/master/enums/emission_standards.csv",
    ),
    ReferenceRule(
        "data/master/gearboxes.csv",
        "type",
        "data/master/enums/transmission_type.csv",
    ),
    ReferenceRule(
        "data/master/gearboxes.csv",
        "drive_type",
        "data/master/enums/drive_types.csv",
    ),
    ReferenceRule(
        "data/master/model_engines.csv",
        "model_code",
        "data/master/models.csv",
    ),
    ReferenceRule(
        "data/master/model_engines.csv",
        "engine_code",
        "data/master/engines.csv",
    ),
    ReferenceRule(
        "data/master/model_engines.csv",
        "default_fuel",
        "data/master/enums/fuel_types.csv",
    ),
    ReferenceRule(
        "data/master/model_gearboxes.csv",
        "model_code",
        "data/master/models.csv",
    ),
    ReferenceRule(
        "data/master/model_gearboxes.csv",
        "gearbox_code",
        "data/master/gearboxes.csv",
    ),
    ReferenceRule(
        "data/master/configuration_attribute_availability.csv",
        "configuration_code",
        "data/master/configurations.csv",
    ),
    ReferenceRule(
        "data/master/configuration_attribute_availability.csv",
        "attribute_code",
        "data/master/attributes.csv",
    ),
    ReferenceRule(
        "data/master/configuration_attribute_availability.csv",
        "availability_status",
        "data/master/enums/equipment_availability_statuses.csv",
    ),
    ReferenceRule(
        "data/master/configuration_attribute_availability.csv",
        "source_code",
        "data/master/sources.csv",
    ),
    ReferenceRule(
        "data/master/configuration_attribute_values.csv",
        "configuration_code",
        "data/master/configurations.csv",
    ),
    ReferenceRule(
        "data/master/configuration_attribute_values.csv",
        "attribute_code",
        "data/master/attributes.csv",
    ),
    ReferenceRule(
        "data/master/configuration_attribute_values.csv",
        "fuel_type_code",
        "data/master/enums/fuel_types.csv",
        allow_empty=True,
    ),
    ReferenceRule(
        "data/master/configuration_attribute_values.csv",
        "source_code",
        "data/master/sources.csv",
    ),
    ReferenceRule(
        "data/master/configuration_prices.csv",
        "configuration_code",
        "data/master/configurations.csv",
    ),
    ReferenceRule(
        "data/master/configuration_prices.csv",
        "currency_code",
        "data/master/currencies.csv",
    ),
    ReferenceRule(
        "data/master/configuration_prices.csv",
        "source_code",
        "data/master/sources.csv",
    ),
    ReferenceRule(
        "data/master/configurations.csv",
        "version_code",
        "data/master/versions.csv",
    ),
    ReferenceRule(
        "data/master/configurations.csv",
        "transmission_type",
        "data/master/enums/transmission_type.csv",
    ),
    ReferenceRule(
        "data/master/source_configurations.csv",
        "source_code",
        "data/master/sources.csv",
    ),
    ReferenceRule(
        "data/master/source_configurations.csv",
        "configuration_code",
        "data/master/configurations.csv",
    ),
    ReferenceRule(
        "data/master/versions.csv",
        "model_code",
        "data/master/models.csv",
    ),
    ReferenceRule(
        "data/master/source_versions.csv",
        "source_code",
        "data/master/sources.csv",
    ),
    ReferenceRule(
        "data/master/source_versions.csv",
        "version_code",
        "data/master/versions.csv",
    ),
    ReferenceRule(
        "data/master/source_models.csv",
        "source_code",
        "data/master/sources.csv",
    ),
    ReferenceRule(
        "data/master/source_models.csv",
        "model_code",
        "data/master/models.csv",
    ),
    ReferenceRule(
        "data/master/attributes.csv",
        "category",
        "data/master/attribute_categories.csv",
        target_column="name",
    ),
)


@dataclass
class CsvTable:
    """Parsed CSV header and rows with original row numbers."""

    columns: tuple[str, ...]
    rows: list[tuple[int, dict[str, str | None]]]


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _load_table(
    root: Path,
    path: Path,
    cache: dict[Path, CsvTable | None],
    errors: list[str],
) -> CsvTable | None:
    path = path.resolve()

    if path in cache:
        return cache[path]

    display_path = _display_path(root, path)

    if not path.is_file():
        errors.append(f"{display_path}: file not found")
        cache[path] = None
        return None

    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                errors.append(f"{display_path}: missing CSV header")
                cache[path] = None
                return None

            columns = tuple(
                column.strip() if column is not None else ""
                for column in reader.fieldnames
            )
            rows = [
                (row_number, row)
                for row_number, row in enumerate(reader, start=2)
            ]
    except UnicodeDecodeError:
        errors.append(f"{display_path}: file is not valid UTF-8")
        cache[path] = None
        return None
    except (OSError, csv.Error) as exc:
        errors.append(f"{display_path}: cannot read CSV: {exc}")
        cache[path] = None
        return None

    table = CsvTable(columns=columns, rows=rows)
    cache[path] = table
    return table


def _load_target_values(
    root: Path,
    target_path: Path,
    target_column: str,
    table_cache: dict[Path, CsvTable | None],
    target_cache: dict[tuple[Path, str], set[str] | None],
    errors: list[str],
) -> set[str] | None:
    cache_key = (target_path.resolve(), target_column)

    if cache_key in target_cache:
        return target_cache[cache_key]

    table = _load_table(root, target_path, table_cache, errors)

    if table is None:
        target_cache[cache_key] = None
        return None

    display_path = _display_path(root, target_path)

    if target_column not in table.columns:
        errors.append(
            f"{display_path}: missing target column '{target_column}'"
        )
        target_cache[cache_key] = None
        return None

    values: set[str] = set()
    first_rows: dict[str, int] = {}

    for row_number, row in table.rows:
        value = (row.get(target_column) or "").strip()

        if not value:
            errors.append(
                f"{display_path}: row {row_number}: "
                f"empty target key in '{target_column}'"
            )
            continue

        if value in values:
            errors.append(
                f"{display_path}: row {row_number}: duplicate target key "
                f"'{value}' in '{target_column}' "
                f"(first seen at row {first_rows[value]})"
            )
            continue

        values.add(value)
        first_rows[value] = row_number

    target_cache[cache_key] = values
    return values


def validate_reference_rules(
    root: Path,
    rules: Sequence[ReferenceRule],
) -> list[str]:
    """Validate the supplied CSV reference rules."""

    root = root.resolve()
    errors: list[str] = []
    table_cache: dict[Path, CsvTable | None] = {}
    target_cache: dict[tuple[Path, str], set[str] | None] = {}

    for rule in rules:
        source_path = root / rule.source_file
        target_path = root / rule.target_file

        source_table = _load_table(
            root,
            source_path,
            table_cache,
            errors,
        )
        target_values = _load_target_values(
            root,
            target_path,
            rule.target_column,
            table_cache,
            target_cache,
            errors,
        )

        if source_table is None or target_values is None:
            continue

        source_display = _display_path(root, source_path)
        target_display = _display_path(root, target_path)

        if rule.source_column not in source_table.columns:
            errors.append(
                f"{source_display}: missing source column "
                f"'{rule.source_column}'"
            )
            continue

        for row_number, row in source_table.rows:
            value = (row.get(rule.source_column) or "").strip()

            if not value:
                if not rule.allow_empty:
                    errors.append(
                        f"{source_display}: row {row_number}: "
                        f"empty reference in '{rule.source_column}' "
                        f"(expected {target_display}.{rule.target_column})"
                    )
                continue

            if value not in target_values:
                errors.append(
                    f"{source_display}: row {row_number}: "
                    f"value '{value}' in '{rule.source_column}' "
                    f"not found in {target_display}.{rule.target_column}"
                )

    return errors


def validate_references(root: Path) -> list[str]:
    """Validate declared references and enum-domain membership."""

    errors = validate_reference_rules(root, REFERENCE_RULES)
    _, enum_errors = validate_enum_domains(root)
    errors.extend(enum_errors)
    return errors
