"Execution of declarative data validation rules."

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


RULES_PATH = "data/master/validation_rules.csv"
SUBJECT_PATH = "data/master/attributes.csv"
MASTER_PATH = "data/master"

ALLOWED_SEVERITIES = frozenset({"error", "warning"})

_EXISTS_PATTERN = re.compile(
    r"exists\((?P<file>[A-Za-z0-9_.-]+\.csv)"
    r"\.(?P<column>[A-Za-z_][A-Za-z0-9_]*)\)"
)
_IN_PATTERN = re.compile(r"in\((?P<options>[^()]*)\)")


@dataclass
class CsvTable:
    "Parsed CSV table with original row numbers."

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

    label = _display_path(root, path)

    if not path.is_file():
        errors.append(f"{label}: file not found")
        cache[path] = None
        return None

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                errors.append(f"{label}: missing CSV header")
                cache[path] = None
                return None

            columns = tuple(
                column.strip() if column is not None else ""
                for column in reader.fieldnames
            )
            rows = [
                (row_number, row)
                for row_number, row in enumerate(
                    reader,
                    start=2,
                )
            ]

    except UnicodeDecodeError:
        errors.append(f"{label}: file is not valid UTF-8")
        cache[path] = None
        return None
    except (OSError, csv.Error) as exc:
        errors.append(f"{label}: cannot read CSV: {exc}")
        cache[path] = None
        return None

    table = CsvTable(columns=columns, rows=rows)
    cache[path] = table
    return table


def _add_issue(
    severity: str,
    issue: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    if severity == "warning":
        warnings.append(issue)
    else:
        errors.append(issue)


def _base_issue(
    row_number: int,
    field: str,
    expression: str,
    message: str,
) -> str:
    return (
        f"{SUBJECT_PATH}: row {row_number}: "
        f"field '{field}' violates rule '{expression}': "
        f"{message}"
    )


def execute_data_rules(
    root: Path,
) -> tuple[int, int, list[str], list[str]]:
    "Execute validation_rules.csv against attributes.csv."

    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    table_cache: dict[Path, CsvTable | None] = {}

    rules_path = root / RULES_PATH
    subject_path = root / SUBJECT_PATH

    rules_table = _load_table(
        root,
        rules_path,
        table_cache,
        errors,
    )
    subject_table = _load_table(
        root,
        subject_path,
        table_cache,
        errors,
    )

    if rules_table is None or subject_table is None:
        return 0, 0, errors, warnings

    required_rule_columns = (
        "field",
        "rule",
        "severity",
        "message",
    )
    missing_rule_columns = [
        column
        for column in required_rule_columns
        if column not in rules_table.columns
    ]

    if missing_rule_columns:
        errors.extend(
            f"{RULES_PATH}: missing column '{column}'"
            for column in missing_rule_columns
        )
        return 0, len(subject_table.rows), errors, warnings

    checked_rules = 0

    for rule_row_number, rule_row in rules_table.rows:
        values = [
            value
            for value in rule_row.values()
            if value is not None
        ]

        if not values or all(
            not value.strip()
            for value in values
        ):
            continue

        field = (rule_row.get("field") or "").strip()
        expression = (rule_row.get("rule") or "").strip()
        severity = (rule_row.get("severity") or "").strip()
        message = (rule_row.get("message") or "").strip()

        if (
            not field
            or not expression
            or not message
            or severity not in ALLOWED_SEVERITIES
        ):
            errors.append(
                f"{RULES_PATH}: row {rule_row_number}: "
                "rule contract is not executable"
            )
            continue

        if field not in subject_table.columns:
            errors.append(
                f"{RULES_PATH}: row {rule_row_number}: "
                f"field '{field}' does not exist in "
                f"{SUBJECT_PATH}"
            )
            continue

        checked_rules += 1

        if expression == "unique":
            first_rows: dict[str, int] = {}

            for row_number, row in subject_table.rows:
                value = (row.get(field) or "").strip()

                if not value:
                    continue

                normalized = value.casefold()
                first_row = first_rows.get(normalized)

                if first_row is None:
                    first_rows[normalized] = row_number
                    continue

                issue = (
                    _base_issue(
                        row_number,
                        field,
                        expression,
                        message,
                    )
                    + f" (value '{value}', first seen "
                    f"at row {first_row})"
                )
                _add_issue(
                    severity,
                    issue,
                    errors,
                    warnings,
                )

            continue

        if expression == "not_empty":
            for row_number, row in subject_table.rows:
                value = (row.get(field) or "").strip()

                if value:
                    continue

                _add_issue(
                    severity,
                    _base_issue(
                        row_number,
                        field,
                        expression,
                        message,
                    ),
                    errors,
                    warnings,
                )

            continue

        exists_match = _EXISTS_PATTERN.fullmatch(expression)

        if exists_match is not None:
            target_file = exists_match.group("file")
            target_column = exists_match.group("column")
            target_path = root / MASTER_PATH / target_file
            target_table = _load_table(
                root,
                target_path,
                table_cache,
                errors,
            )

            if target_table is None:
                continue

            target_label = _display_path(root, target_path)

            if target_column not in target_table.columns:
                errors.append(
                    f"{target_label}: missing target column "
                    f"'{target_column}'"
                )
                continue

            allowed_values = {
                (row.get(target_column) or "").strip()
                for _, row in target_table.rows
                if (row.get(target_column) or "").strip()
            }

            for row_number, row in subject_table.rows:
                value = (row.get(field) or "").strip()

                # Empty values are optional for exists(...).
                # Presence must be expressed through not_empty.
                if not value or value in allowed_values:
                    continue

                issue = (
                    _base_issue(
                        row_number,
                        field,
                        expression,
                        message,
                    )
                    + f" (value '{value}' not found in "
                    f"{target_label}.{target_column})"
                )
                _add_issue(
                    severity,
                    issue,
                    errors,
                    warnings,
                )

            continue

        in_match = _IN_PATTERN.fullmatch(expression)

        if in_match is not None:
            allowed_values = {
                option.strip()
                for option in in_match.group(
                    "options"
                ).split("|")
            }

            for row_number, row in subject_table.rows:
                value = (row.get(field) or "").strip()

                if value in allowed_values:
                    continue

                issue = (
                    _base_issue(
                        row_number,
                        field,
                        expression,
                        message,
                    )
                    + f" (value '{value}')"
                )
                _add_issue(
                    severity,
                    issue,
                    errors,
                    warnings,
                )

            continue

        errors.append(
            f"{RULES_PATH}: row {rule_row_number}: "
            f"unsupported rule expression '{expression}'"
        )

    return (
        checked_rules,
        len(subject_table.rows),
        errors,
        warnings,
    )
