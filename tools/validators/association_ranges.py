"""
Validation of association availability against parent lifetimes.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AssociationRangeRule:
    """Describe one association-to-parent temporal constraint."""

    relation_path: str
    relation_code_column: str
    relation_start_column: str
    relation_end_column: str
    parent_path: str
    parent_code_column: str
    parent_start_column: str
    parent_end_column: str
    entity_label: str


ASSOCIATION_RANGE_RULES: tuple[AssociationRangeRule, ...] = (
    AssociationRangeRule(
        relation_path="data/master/model_engines.csv",
        relation_code_column="model_code",
        relation_start_column="available_from",
        relation_end_column="available_to",
        parent_path="data/master/models.csv",
        parent_code_column="code",
        parent_start_column="production_from",
        parent_end_column="production_to",
        entity_label="model",
    ),
    AssociationRangeRule(
        relation_path="data/master/model_engines.csv",
        relation_code_column="engine_code",
        relation_start_column="available_from",
        relation_end_column="available_to",
        parent_path="data/master/engines.csv",
        parent_code_column="code",
        parent_start_column="start_year",
        parent_end_column="end_year",
        entity_label="engine",
    ),
    AssociationRangeRule(
        relation_path="data/master/model_gearboxes.csv",
        relation_code_column="model_code",
        relation_start_column="available_from",
        relation_end_column="available_to",
        parent_path="data/master/models.csv",
        parent_code_column="code",
        parent_start_column="production_from",
        parent_end_column="production_to",
        entity_label="model",
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
    """Parse one required or optional four-digit year."""

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


def _format_range(
    start: int,
    end: int | None,
) -> str:
    return f"{start}-{end if end is not None else 'open'}"


def _is_contained(
    parent_start: int,
    parent_end: int | None,
    relation_start: int,
    relation_end: int | None,
) -> bool:
    if relation_start < parent_start:
        return False

    if parent_end is None:
        return True

    if relation_end is None:
        return False

    return relation_end <= parent_end


def _required_columns(
    fieldnames: list[str] | None,
    columns: tuple[str, ...],
    *,
    label: str,
) -> list[str]:
    if fieldnames is None:
        return [f"{label}: missing CSV header"]

    return [
        f"{label}: missing column '{column}'"
        for column in columns
        if column not in fieldnames
    ]


def validate_association_range_rule(
    root: Path,
    rule: AssociationRangeRule,
) -> tuple[int, list[str]]:
    """Validate one association range rule."""

    relation_path = root / rule.relation_path
    parent_path = root / rule.parent_path

    if not relation_path.is_file():
        return 0, [f"{rule.relation_path}: file not found"]

    if not parent_path.is_file():
        return 0, [f"{rule.parent_path}: file not found"]

    errors: list[str] = []
    parent_ranges: dict[str, tuple[int, int | None]] = {}

    try:
        with parent_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            column_errors = _required_columns(
                reader.fieldnames,
                (
                    rule.parent_code_column,
                    rule.parent_start_column,
                    rule.parent_end_column,
                ),
                label=rule.parent_path,
            )

            if column_errors:
                return 0, column_errors

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

                code = (
                    row.get(rule.parent_code_column) or ""
                ).strip()

                if not code:
                    errors.append(
                        f"{rule.parent_path}: row {row_number}: "
                        f"empty '{rule.parent_code_column}'"
                    )
                    continue

                start, start_error = _parse_year(
                    row.get(rule.parent_start_column) or "",
                    label=rule.parent_path,
                    row_number=row_number,
                    column=rule.parent_start_column,
                    required=True,
                )
                end, end_error = _parse_year(
                    row.get(rule.parent_end_column) or "",
                    label=rule.parent_path,
                    row_number=row_number,
                    column=rule.parent_end_column,
                    required=False,
                )

                if start_error:
                    errors.append(start_error)

                if end_error:
                    errors.append(end_error)

                if start_error or end_error:
                    continue

                if code in parent_ranges:
                    errors.append(
                        f"{rule.parent_path}: row {row_number}: "
                        f"duplicate '{rule.parent_code_column}' "
                        f"value '{code}'"
                    )
                    continue

                assert start is not None
                parent_ranges[code] = (start, end)

        with relation_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            column_errors = _required_columns(
                reader.fieldnames,
                (
                    rule.relation_code_column,
                    rule.relation_start_column,
                    rule.relation_end_column,
                ),
                label=rule.relation_path,
            )

            if column_errors:
                return 0, errors + column_errors

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
                code = (
                    row.get(rule.relation_code_column) or ""
                ).strip()

                if not code:
                    errors.append(
                        f"{rule.relation_path}: row {row_number}: "
                        f"empty '{rule.relation_code_column}'"
                    )
                    continue

                relation_start, start_error = _parse_year(
                    row.get(rule.relation_start_column) or "",
                    label=rule.relation_path,
                    row_number=row_number,
                    column=rule.relation_start_column,
                    required=True,
                )
                relation_end, end_error = _parse_year(
                    row.get(rule.relation_end_column) or "",
                    label=rule.relation_path,
                    row_number=row_number,
                    column=rule.relation_end_column,
                    required=False,
                )

                if start_error:
                    errors.append(start_error)

                if end_error:
                    errors.append(end_error)

                if start_error or end_error:
                    continue

                assert relation_start is not None

                if (
                    relation_end is not None
                    and relation_end < relation_start
                ):
                    errors.append(
                        f"{rule.relation_path}: row {row_number}: "
                        f"end year {relation_end} precedes "
                        f"start year {relation_start}"
                    )
                    continue

                parent_range = parent_ranges.get(code)

                if parent_range is None:
                    errors.append(
                        f"{rule.relation_path}: row {row_number}: "
                        f"{rule.entity_label} '{code}' "
                        f"not found in {rule.parent_path}"
                    )
                    continue

                parent_start, parent_end = parent_range

                if not _is_contained(
                    parent_start,
                    parent_end,
                    relation_start,
                    relation_end,
                ):
                    errors.append(
                        f"{rule.relation_path}: row {row_number}: "
                        f"{rule.entity_label} '{code}' availability "
                        f"{_format_range(relation_start, relation_end)} "
                        f"is outside parent lifetime "
                        f"{_format_range(parent_start, parent_end)}"
                    )

    except UnicodeDecodeError:
        return 0, errors + [
            "Association range input is not valid UTF-8"
        ]
    except csv.Error as exc:
        return 0, errors + [
            f"Association range CSV parse error: {exc}"
        ]
    except OSError as exc:
        return 0, errors + [
            f"Cannot read association range input: {exc}"
        ]

    return checked_records, errors


def validate_association_ranges(
    root: Path,
) -> tuple[int, list[str]]:
    """Validate all configured association range rules."""

    root = root.resolve()
    checked_records = 0
    errors: list[str] = []

    for rule in ASSOCIATION_RANGE_RULES:
        rule_records, rule_errors = (
            validate_association_range_rule(root, rule)
        )
        checked_records += rule_records
        errors.extend(rule_errors)

    return checked_records, errors
