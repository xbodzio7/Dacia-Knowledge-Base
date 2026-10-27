"""
Repository-wide uniqueness validation for CSV key columns.
"""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path


KEY_COLUMNS: tuple[str, ...] = ("id", "code")


def validate_unique_columns(
    path: Path,
    key_columns: Sequence[str] = KEY_COLUMNS,
    *,
    display_path: str | None = None,
) -> tuple[int, list[str]]:
    """
    Validate non-empty and unique values in existing key columns.

    Only columns that actually exist in the CSV file are checked. Values are
    compared case-insensitively after trimming surrounding whitespace.

    Return the number of checked columns and a list of validation errors.
    """

    label = display_path or str(path)

    if not path.is_file():
        return 0, [f"{label}: file not found"]

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                return 0, [f"{label}: missing CSV header"]

            header_lookup = {
                header.strip().casefold(): header
                for header in reader.fieldnames
                if header is not None and header.strip()
            }

            active_columns = [
                (
                    column.casefold(),
                    header_lookup[column.casefold()],
                )
                for column in key_columns
                if column.casefold() in header_lookup
            ]

            seen: dict[str, dict[str, tuple[str, int]]] = {
                column: {}
                for column, _ in active_columns
            }
            errors: list[str] = []

            for row_number, row in enumerate(reader, start=2):
                row_values = [
                    value
                    for value in row.values()
                    if value is not None
                ]

                if not row_values or all(
                    not value.strip()
                    for value in row_values
                ):
                    continue

                for canonical_column, actual_header in active_columns:
                    value = (row.get(actual_header) or "").strip()

                    if not value:
                        errors.append(
                            f"{label}: row {row_number}: "
                            f"empty key in '{canonical_column}'"
                        )
                        continue

                    normalized_value = value.casefold()
                    first_occurrence = seen[canonical_column].get(
                        normalized_value
                    )

                    if first_occurrence is not None:
                        first_value, first_row = first_occurrence
                        errors.append(
                            f"{label}: row {row_number}: "
                            f"duplicate {canonical_column} '{value}' "
                            f"(first seen as '{first_value}' "
                            f"at row {first_row})"
                        )
                        continue

                    seen[canonical_column][normalized_value] = (
                        value,
                        row_number,
                    )

    except UnicodeDecodeError:
        return 0, [f"{label}: file is not valid UTF-8"]
    except csv.Error as exc:
        return 0, [f"{label}: CSV parse error: {exc}"]
    except OSError as exc:
        return 0, [f"{label}: cannot read file: {exc}"]

    return len(active_columns), errors


def validate_unique_keys(root: Path) -> tuple[int, list[str]]:
    """
    Validate every existing id and code column under data/master.
    """

    root = root.resolve()
    master_directory = root / "data" / "master"

    if not master_directory.is_dir():
        return 0, [
            "data/master: master data directory not found"
        ]

    csv_files = sorted(master_directory.rglob("*.csv"))

    if not csv_files:
        return 0, ["data/master: no CSV files found"]

    checked_columns = 0
    errors: list[str] = []

    for path in csv_files:
        relative_path = path.relative_to(root).as_posix()
        file_column_count, file_errors = validate_unique_columns(
            path,
            display_path=relative_path,
        )

        checked_columns += file_column_count
        errors.extend(file_errors)

    return checked_columns, errors


def validate_attributes(path: Path) -> tuple[bool, list[str]]:
    """
    Preserve the former attributes.csv-specific public interface.
    """

    _, errors = validate_unique_columns(
        path,
        key_columns=("id", "code"),
    )
    return not errors, errors
