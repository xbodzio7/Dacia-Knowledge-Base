"""
Validation of entity statuses and lifecycle consistency.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from validators.enum_domains import load_enum_domain_rules


@dataclass(frozen=True)
class StatusRule:
    """Describe allowed statuses for one CSV file."""

    path: str
    allowed_statuses: frozenset[str]
    end_column: str | None = None


ACTIVE_STATUSES = frozenset({"active"})
LIFECYCLE_STATUSES = frozenset({"current", "archived"})

# Static rules cover entity tables and the equipment-availability status domain,
# which is not the controlled domain of an attribute. Attribute enum-domain files
# are appended dynamically from data/master/attribute_enum_domains.csv.
STATUS_RULES: tuple[StatusRule, ...] = (
    StatusRule(
        "data/master/attributes.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/attribute_enum_domains.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/domains.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/sources.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/currencies.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/configurations.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/versions.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/engines.csv",
        LIFECYCLE_STATUSES,
        "end_year",
    ),
    StatusRule(
        "data/master/enums/equipment_availability_statuses.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/gearboxes.csv",
        LIFECYCLE_STATUSES,
    ),
    StatusRule(
        "data/master/models.csv",
        LIFECYCLE_STATUSES,
        "production_to",
    ),
)


def configured_status_rules(root: Path) -> tuple[tuple[StatusRule, ...], list[str]]:
    """Return static rules plus unique enum-domain files from the registry."""

    root = root.resolve()
    enum_rules, errors = load_enum_domain_rules(root)
    rules = list(STATUS_RULES)
    existing_paths = {rule.path for rule in rules}
    for enum_rule in enum_rules:
        path = enum_rule.relative_path.as_posix()
        if path in existing_paths:
            continue
        rules.append(StatusRule(path, ACTIVE_STATUSES))
        existing_paths.add(path)
    return tuple(rules), errors


def validate_status_file(
    path: Path,
    allowed_statuses: frozenset[str],
    *,
    end_column: str | None = None,
    display_path: str | None = None,
) -> tuple[int, list[str]]:
    """
    Validate statuses in one CSV file.

    When an end-year column is configured, current records must have an
    open range and archived records must have a closed range.
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

            errors: list[str] = []

            if "status" not in reader.fieldnames:
                errors.append(
                    f"{label}: missing column 'status'"
                )

            if (
                end_column is not None
                and end_column not in reader.fieldnames
            ):
                errors.append(
                    f"{label}: missing column '{end_column}'"
                )

            if errors:
                return 0, errors

            checked_records = 0
            allowed_text = ", ".join(
                sorted(allowed_statuses)
            )

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
                status = (row.get("status") or "").strip()

                if not status:
                    errors.append(
                        f"{label}: row {row_number}: "
                        "empty required status"
                    )
                    continue

                if status not in allowed_statuses:
                    errors.append(
                        f"{label}: row {row_number}: "
                        f"invalid status '{status}'; "
                        f"expected one of: {allowed_text}"
                    )
                    continue

                if end_column is None:
                    continue

                end_value = (
                    row.get(end_column) or ""
                ).strip()

                if status == "current" and end_value:
                    errors.append(
                        f"{label}: row {row_number}: "
                        f"status 'current' requires an empty "
                        f"'{end_column}', got '{end_value}'"
                    )

                if status == "archived" and not end_value:
                    errors.append(
                        f"{label}: row {row_number}: "
                        f"status 'archived' requires a non-empty "
                        f"'{end_column}'"
                    )

    except UnicodeDecodeError:
        return 0, [f"{label}: file is not valid UTF-8"]
    except csv.Error as exc:
        return 0, [f"{label}: CSV parse error: {exc}"]
    except OSError as exc:
        return 0, [f"{label}: cannot read file: {exc}"]

    return checked_records, errors


def validate_statuses(root: Path) -> tuple[int, list[str]]:
    """Validate all configured status columns."""

    root = root.resolve()
    checked_records = 0
    rules, errors = configured_status_rules(root)

    for rule in rules:
        file_records, file_errors = validate_status_file(
            root / rule.path,
            rule.allowed_statuses,
            end_column=rule.end_column,
            display_path=rule.path,
        )

        checked_records += file_records
        errors.extend(file_errors)

    return checked_records, errors
