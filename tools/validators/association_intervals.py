"""Validation of duplicate and overlapping association intervals."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path


@dataclass(frozen=True)
class AssociationIntervalRule:
    path: str
    key_columns: tuple[str, ...]
    start_column: str = "available_from"
    end_column: str = "available_to"


@dataclass(frozen=True)
class _Interval:
    row_number: int
    start: int
    end: int | None


ASSOCIATION_INTERVAL_RULES: tuple[AssociationIntervalRule, ...] = (
    AssociationIntervalRule(
        "data/master/model_engines.csv",
        ("model_code", "engine_code"),
    ),
    AssociationIntervalRule(
        "data/master/model_gearboxes.csv",
        ("model_code", "gearbox_code"),
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
    value = value.strip()
    if not value:
        if required:
            return None, (
                f"{label}: row {row_number}: "
                f"empty required year in '{column}'"
            )
        return None, None

    if not (
        len(value) == 4
        and value.isascii()
        and value.isdigit()
    ):
        return None, (
            f"{label}: row {row_number}: "
            f"'{column}' must contain a four-digit year, "
            f"got '{value}'"
        )

    return int(value), None


def _format_interval(start: int, end: int | None) -> str:
    return f"{start}-{end if end is not None else 'open'}"


def _overlap(first: _Interval, second: _Interval) -> bool:
    return (
        (first.end is None or second.start <= first.end)
        and (second.end is None or first.start <= second.end)
    )


def validate_association_interval_file(
    path: Path,
    key_columns: tuple[str, ...],
    *,
    start_column: str = "available_from",
    end_column: str = "available_to",
    display_path: str | None = None,
) -> tuple[int, list[str]]:
    label = display_path or str(path)
    if not path.is_file():
        return 0, [f"{label}: file not found"]

    groups: dict[tuple[str, ...], list[_Interval]] = defaultdict(list)
    errors: list[str] = []

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                return 0, [f"{label}: missing CSV header"]

            required_columns = (
                *key_columns,
                start_column,
                end_column,
            )
            missing = [
                column
                for column in required_columns
                if column not in reader.fieldnames
            ]
            if missing:
                return 0, [
                    f"{label}: missing column '{column}'"
                    for column in missing
                ]

            checked = 0
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

                checked += 1
                key = tuple(
                    (row.get(column) or "").strip()
                    for column in key_columns
                )
                empty_columns = [
                    column
                    for column, value in zip(key_columns, key)
                    if not value
                ]
                if empty_columns:
                    errors.extend(
                        f"{label}: row {row_number}: empty '{column}'"
                        for column in empty_columns
                    )
                    continue

                start, start_error = _parse_year(
                    row.get(start_column) or "",
                    label=label,
                    row_number=row_number,
                    column=start_column,
                    required=True,
                )
                end, end_error = _parse_year(
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
                if start_error or end_error:
                    continue

                assert start is not None
                if end is not None and end < start:
                    errors.append(
                        f"{label}: row {row_number}: "
                        f"end year {end} precedes start year {start}"
                    )
                    continue

                groups[key].append(
                    _Interval(row_number, start, end)
                )

    except UnicodeDecodeError:
        return 0, [f"{label}: file is not valid UTF-8"]
    except csv.Error as exc:
        return 0, [f"{label}: CSV parse error: {exc}"]
    except OSError as exc:
        return 0, [f"{label}: cannot read file: {exc}"]

    for key, intervals in groups.items():
        key_text = ", ".join(
            f"{column}='{value}'"
            for column, value in zip(key_columns, key)
        )

        for first, second in combinations(intervals, 2):
            first_range = (first.start, first.end)
            second_range = (second.start, second.end)

            if first_range == second_range:
                errors.append(
                    f"{label}: rows {first.row_number} and "
                    f"{second.row_number}: duplicate interval "
                    f"{_format_interval(first.start, first.end)} "
                    f"for {key_text}"
                )
            elif _overlap(first, second):
                errors.append(
                    f"{label}: rows {first.row_number} and "
                    f"{second.row_number}: intervals "
                    f"{_format_interval(first.start, first.end)} and "
                    f"{_format_interval(second.start, second.end)} "
                    f"overlap for {key_text}"
                )

    return checked, errors


def validate_association_intervals(
    root: Path,
) -> tuple[int, list[str]]:
    checked = 0
    errors: list[str] = []

    for rule in ASSOCIATION_INTERVAL_RULES:
        file_checked, file_errors = (
            validate_association_interval_file(
                root.resolve() / rule.path,
                rule.key_columns,
                start_column=rule.start_column,
                end_column=rule.end_column,
                display_path=rule.path,
            )
        )
        checked += file_checked
        errors.extend(file_errors)

    return checked, errors
