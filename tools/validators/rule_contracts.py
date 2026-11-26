"""Validation of declarative data-rule contracts."""

from __future__ import annotations

import csv
import re
from pathlib import Path


RULES_PATH = "data/master/validation_rules.csv"
SUBJECT_PATH = "data/master/attributes.csv"

ALLOWED_SEVERITIES = frozenset({"error", "warning"})
SIMPLE_RULES = frozenset({"unique", "not_empty"})

_EXISTS_PATTERN = re.compile(
    r"exists\((?P<file>[A-Za-z0-9_.-]+\.csv)"
    r"\.(?P<column>[A-Za-z_][A-Za-z0-9_]*)\)"
)
_IN_PATTERN = re.compile(r"in\((?P<options>[^()]*)\)")


def _read_header(
    path: Path,
    *,
    label: str,
) -> tuple[list[str] | None, str | None]:
    """Read one CSV header using repository encoding rules."""

    if not path.is_file():
        return None, f"{label}: file not found"

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.reader(handle)

            try:
                header = next(reader)
            except StopIteration:
                return None, f"{label}: missing CSV header"

    except UnicodeDecodeError:
        return None, f"{label}: file is not valid UTF-8"
    except csv.Error as exc:
        return None, f"{label}: CSV parse error: {exc}"
    except OSError as exc:
        return None, f"{label}: cannot read file: {exc}"

    return header, None


def _validate_exists_rule(
    root: Path,
    expression: str,
    *,
    label: str,
    row_number: int,
) -> list[str] | None:
    match = _EXISTS_PATTERN.fullmatch(expression)

    if match is None:
        return None

    target_file = match.group("file")
    target_column = match.group("column")
    target_label = f"data/master/{target_file}"
    target_path = root / target_label

    header, header_error = _read_header(
        target_path,
        label=target_label,
    )

    if header_error:
        return [
            f"{label}: row {row_number}: "
            f"rule '{expression}' references {header_error}"
        ]

    assert header is not None

    if target_column not in header:
        return [
            f"{label}: row {row_number}: "
            f"rule '{expression}' references missing column "
            f"'{target_column}' in {target_label}"
        ]

    return []


def _validate_in_rule(
    expression: str,
    *,
    label: str,
    row_number: int,
) -> list[str] | None:
    match = _IN_PATTERN.fullmatch(expression)

    if match is None:
        return None

    options = [
        option.strip()
        for option in match.group("options").split("|")
    ]

    if not options or any(not option for option in options):
        return [
            f"{label}: row {row_number}: "
            f"rule '{expression}' contains an empty option"
        ]

    normalized = [option.casefold() for option in options]

    if len(normalized) != len(set(normalized)):
        return [
            f"{label}: row {row_number}: "
            f"rule '{expression}' contains duplicate options"
        ]

    return []


def _validate_rule_expression(
    root: Path,
    expression: str,
    *,
    label: str,
    row_number: int,
) -> list[str]:
    if expression in SIMPLE_RULES:
        return []

    exists_errors = _validate_exists_rule(
        root,
        expression,
        label=label,
        row_number=row_number,
    )

    if exists_errors is not None:
        return exists_errors

    in_errors = _validate_in_rule(
        expression,
        label=label,
        row_number=row_number,
    )

    if in_errors is not None:
        return in_errors

    return [
        f"{label}: row {row_number}: "
        f"unsupported rule expression '{expression}'"
    ]


def validate_rule_contracts(
    root: Path,
) -> tuple[int, list[str]]:
    """Validate validation_rules.csv against attributes.csv."""

    root = root.resolve()
    rules_path = root / RULES_PATH
    subject_path = root / SUBJECT_PATH

    subject_header, subject_error = _read_header(
        subject_path,
        label=SUBJECT_PATH,
    )

    if subject_error:
        return 0, [subject_error]

    assert subject_header is not None
    subject_fields = set(subject_header)

    if not rules_path.is_file():
        return 0, [f"{RULES_PATH}: file not found"]

    required_columns = (
        "field",
        "rule",
        "severity",
        "message",
    )
    checked_rules = 0
    errors: list[str] = []
    seen_rules: set[tuple[str, str]] = set()

    try:
        with rules_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                return 0, [f"{RULES_PATH}: missing CSV header"]

            missing_columns = [
                column
                for column in required_columns
                if column not in reader.fieldnames
            ]

            if missing_columns:
                return 0, [
                    f"{RULES_PATH}: missing column '{column}'"
                    for column in missing_columns
                ]

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

                checked_rules += 1
                field = (row.get("field") or "").strip()
                rule = (row.get("rule") or "").strip()
                severity = (row.get("severity") or "").strip()
                message = (row.get("message") or "").strip()

                if not field:
                    errors.append(
                        f"{RULES_PATH}: row {row_number}: "
                        "empty required field"
                    )
                elif field not in subject_fields:
                    errors.append(
                        f"{RULES_PATH}: row {row_number}: "
                        f"field '{field}' does not exist in "
                        f"{SUBJECT_PATH}"
                    )

                if not rule:
                    errors.append(
                        f"{RULES_PATH}: row {row_number}: "
                        "empty required rule"
                    )
                else:
                    errors.extend(
                        _validate_rule_expression(
                            root,
                            rule,
                            label=RULES_PATH,
                            row_number=row_number,
                        )
                    )

                if not severity:
                    errors.append(
                        f"{RULES_PATH}: row {row_number}: "
                        "empty required severity"
                    )
                elif severity not in ALLOWED_SEVERITIES:
                    allowed = ", ".join(
                        sorted(ALLOWED_SEVERITIES)
                    )
                    errors.append(
                        f"{RULES_PATH}: row {row_number}: "
                        f"invalid severity '{severity}'; "
                        f"expected one of: {allowed}"
                    )

                if not message:
                    errors.append(
                        f"{RULES_PATH}: row {row_number}: "
                        "empty required message"
                    )

                if field and rule:
                    key = (field, rule)

                    if key in seen_rules:
                        errors.append(
                            f"{RULES_PATH}: row {row_number}: "
                            f"duplicate rule '{rule}' "
                            f"for field '{field}'"
                        )
                    else:
                        seen_rules.add(key)

    except UnicodeDecodeError:
        return 0, [f"{RULES_PATH}: file is not valid UTF-8"]
    except csv.Error as exc:
        return 0, [f"{RULES_PATH}: CSV parse error: {exc}"]
    except OSError as exc:
        return 0, [f"{RULES_PATH}: cannot read file: {exc}"]

    return checked_rules, errors
