"""
Validation of production and availability year ranges.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class YearRangeRule:
    """Describe one pair of CSV year columns."""

    path: str
    start_column: str
    end_column: str


YEAR_RANGE_RULES: tuple[YearRangeRule, ...] = (
    YearRangeRule(
        "data/master/models.csv",
        "production_from",
        "production_to",
    ),
    YearRangeRule(
        "data/master/engines.csv",
        "start_year",
        "end_year",
    ),
    YearRangeRule(
        "data/master/model_engines.csv",
        "available_from",
        "available_to",
    ),
    YearRangeRule(
        "data/master/model_gearboxes.csv",
        "available_from",
        "available_to",
    ),
)


def _parse_year(
    value: str,
    *,
    label: str,
    row_number: int,
    column: str,
    required: bool,
) -> tuple[int | None, str | None]:
    """Parse one optional or required four-digit year."""

    normalized = value.strip()

    if not normalized:
        if required:
            return (
                None,
                f"{label}: row {row_number}: "
                f"empty required year in '{column}'",
            )

        return None, None

    if not (
        len(normalized) == 4
        and normalized.isascii()
        and normalized.isdigit()
    ):
        return (
            None,
            f"{label}: row {row_number}: "
            f"'{column}' must contain a four-digit year, "
            f"got '{normalized}'",
        )

    return int(normalized), None


def validate_year_range_file(
    path: Path,
    start_column: str,
    end_column: str,
    *,
    display_path: str | None = None,
) -> tuple[int, list[str]]:
    """
    Validate one CSV file containing a start and optional end year.

    Return the number of non-empty records checked and all errors.
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

            errors = [
                f"{label}: missing column '{column}'"
                for column in (start_column, end_column)
                if column not in reader.fieldnames
            ]

            if errors:
                return 0, errors

            checked_records = 0

            for row_number, row in enumerate(reader, start=2):
                values = [
                    value
                    for value in row.values()
                    if value is not None
                ]

                if not values or all(
                    not value.strip()
                    for value in values
                ):
                    continue

                checked_records += 1

                start_year, start_error = _parse_year(
                    row.get(start_column) or "",
                    label=label,
                    row_number=row_number,
                    column=start_column,
                    required=True,
                )
                end_year, end_error = _parse_year(
                    row.get(end_column) or "",
                    label=label,
                    row_number=row_number,
                    column=end_column,
                    required=False,
                )

                if start_error:
                    errors.append(start_error)

                if end_error:
                    errors.append(end_error)

                if (
                    start_year is not None
                    and end_year is not None
                    and end_year < start_year
                ):
                    errors.append(
                        f"{label}: row {row_number}: "
                        f"end year {end_year} in '{end_column}' "
                        f"precedes start year {start_year} "
                        f"in '{start_column}'"
                    )

    except UnicodeDecodeError:
        return 0, [f"{label}: file is not valid UTF-8"]
    except csv.Error as exc:
        return 0, [f"{label}: CSV parse error: {exc}"]
    except OSError as exc:
        return 0, [f"{label}: cannot read file: {exc}"]

    return checked_records, errors


def validate_year_ranges(root: Path) -> tuple[int, list[str]]:
    """Validate all configured production and availability ranges."""

    root = root.resolve()
    checked_records = 0
    errors: list[str] = []

    for rule in YEAR_RANGE_RULES:
        file_records, file_errors = validate_year_range_file(
            root / rule.path,
            rule.start_column,
            rule.end_column,
            display_path=rule.path,
        )

        checked_records += file_records
        errors.extend(file_errors)

    return checked_records, errors
