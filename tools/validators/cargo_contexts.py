"""Semantic validation for contextual cargo-volume observations."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


CONTEXT_RELATIVE_PATH = Path(
    "data/master/configuration_cargo_volume_contexts.csv"
)
VALUES_RELATIVE_PATH = Path(
    "data/master/configuration_attribute_values.csv"
)
ELIGIBLE_ATTRIBUTE_CODE = "boot_capacity"


@dataclass(frozen=True)
class CsvTable:
    columns: tuple[str, ...]
    rows: tuple[tuple[int, dict[str, str | None]], ...]


def _display(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _load_table(
    root: Path,
    path: Path,
    errors: list[str],
) -> CsvTable | None:
    label = _display(root, path)
    if not path.is_file():
        errors.append(f"{label}: file not found")
        return None

    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                errors.append(f"{label}: missing CSV header")
                return None
            columns = tuple(
                column.strip() if column is not None else ""
                for column in reader.fieldnames
            )
            rows = tuple(
                (row_number, row)
                for row_number, row in enumerate(reader, start=2)
            )
    except UnicodeDecodeError:
        errors.append(f"{label}: file is not valid UTF-8")
        return None
    except (OSError, csv.Error) as exc:
        errors.append(f"{label}: cannot read CSV: {exc}")
        return None

    return CsvTable(columns=columns, rows=rows)


def _require_columns(
    root: Path,
    path: Path,
    table: CsvTable,
    required: set[str],
    errors: list[str],
) -> bool:
    missing = sorted(required - set(table.columns))
    if not missing:
        return True
    label = _display(root, path)
    for column in missing:
        errors.append(f"{label}: missing column '{column}'")
    return False


def _is_blank(row: dict[str, str | None]) -> bool:
    return not any((value or "").strip() for value in row.values())


def validate_configuration_cargo_volume_contexts(
    root: Path,
) -> tuple[int, list[str]]:
    """Validate one-to-one cardinality and cargo-attribute eligibility."""
    root = root.resolve()
    context_path = root / CONTEXT_RELATIVE_PATH
    values_path = root / VALUES_RELATIVE_PATH
    errors: list[str] = []

    contexts = _load_table(root, context_path, errors)
    values = _load_table(root, values_path, errors)
    if contexts is None or values is None:
        return 0, errors

    contexts_ok = _require_columns(
        root,
        context_path,
        contexts,
        {"configuration_attribute_value_code"},
        errors,
    )
    values_ok = _require_columns(
        root,
        values_path,
        values,
        {"code", "attribute_code"},
        errors,
    )
    if not contexts_ok or not values_ok:
        return 0, errors

    values_by_code: dict[str, dict[str, str | None]] = {}
    for _, row in values.rows:
        code = (row.get("code") or "").strip()
        if code and code not in values_by_code:
            values_by_code[code] = row

    checked_records = 0
    first_context_rows: dict[str, int] = {}
    context_label = _display(root, context_path)

    for row_number, row in contexts.rows:
        if _is_blank(row):
            continue
        checked_records += 1
        value_code = (
            row.get("configuration_attribute_value_code") or ""
        ).strip()
        if not value_code:
            continue

        first_row = first_context_rows.get(value_code)
        if first_row is not None:
            errors.append(
                f"{context_label}: row {row_number}: duplicate cargo context "
                f"for configuration attribute value '{value_code}' "
                f"(first seen at row {first_row})"
            )
        else:
            first_context_rows[value_code] = row_number

        value_row = values_by_code.get(value_code)
        if value_row is None:
            continue
        attribute_code = (value_row.get("attribute_code") or "").strip()
        if attribute_code != ELIGIBLE_ATTRIBUTE_CODE:
            errors.append(
                f"{context_label}: row {row_number}: value '{value_code}' "
                f"uses attribute '{attribute_code}'; expected "
                f"'{ELIGIBLE_ATTRIBUTE_CODE}'"
            )

    return checked_records, errors
