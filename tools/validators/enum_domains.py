"""Controlled domains for enum-valued configuration attributes."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

REGISTRY_PATH = Path("data/master/attribute_enum_domains.csv")
ENUM_DIRECTORY = Path("data/master/enums")
REGISTRY_FIELDS = ("attribute_code", "domain_file", "status")
DOMAIN_FIELDS = ("code", "name", "description", "status")
DOMAIN_FILE_PATTERN = re.compile(r"[a-z][a-z0-9_]*\.csv")


@dataclass(frozen=True)
class EnumDomainRule:
    """Map one enum attribute to one controlled-value CSV file."""

    attribute_code: str
    domain_file: str

    @property
    def relative_path(self) -> Path:
        return ENUM_DIRECTORY / self.domain_file


def _read_csv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]], list[str]]:
    label = path.as_posix()
    if not path.is_file():
        return (), [], [f"{label}: file not found"]
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                return (), [], [f"{label}: missing CSV header"]
            fields = tuple(reader.fieldnames)
            rows = [
                {key: (value or "").strip() for key, value in row.items()}
                for row in reader
                if any((value or "").strip() for value in row.values())
            ]
    except UnicodeDecodeError:
        return (), [], [f"{label}: file is not valid UTF-8"]
    except (OSError, csv.Error) as exc:
        return (), [], [f"{label}: cannot read CSV: {exc}"]
    return fields, rows, []


def load_enum_domain_rules(root: Path) -> tuple[tuple[EnumDomainRule, ...], list[str]]:
    """Load and validate the attribute-to-domain registry contract."""

    root = root.resolve()
    registry = root / REGISTRY_PATH
    fields, rows, errors = _read_csv(registry)
    if errors:
        return (), errors
    if fields != REGISTRY_FIELDS:
        return (), [
            f"{REGISTRY_PATH.as_posix()}: expected header {REGISTRY_FIELDS}, found {fields}"
        ]

    attributes_path = root / "data/master/attributes.csv"
    attribute_fields, attribute_rows, attribute_errors = _read_csv(attributes_path)
    errors.extend(attribute_errors)
    if attribute_errors:
        return (), errors
    if "code" not in attribute_fields or "data_type" not in attribute_fields:
        errors.append("data/master/attributes.csv: missing code or data_type column")
        return (), errors
    attributes = {row.get("code", ""): row for row in attribute_rows}

    rules: list[EnumDomainRule] = []
    seen_attributes: dict[str, int] = {}
    for row_number, row in enumerate(rows, start=2):
        attribute_code = row.get("attribute_code", "")
        domain_file = row.get("domain_file", "")
        status = row.get("status", "")
        if not attribute_code:
            errors.append(f"{REGISTRY_PATH.as_posix()}: row {row_number}: empty attribute_code")
            continue
        if attribute_code in seen_attributes:
            errors.append(
                f"{REGISTRY_PATH.as_posix()}: row {row_number}: duplicate attribute_code "
                f"'{attribute_code}' (first seen at row {seen_attributes[attribute_code]})"
            )
            continue
        seen_attributes[attribute_code] = row_number
        if DOMAIN_FILE_PATTERN.fullmatch(domain_file) is None:
            errors.append(
                f"{REGISTRY_PATH.as_posix()}: row {row_number}: invalid domain_file "
                f"'{domain_file}'"
            )
            continue
        if status != "active":
            errors.append(
                f"{REGISTRY_PATH.as_posix()}: row {row_number}: status must be active"
            )
        attribute = attributes.get(attribute_code)
        if attribute is None:
            errors.append(
                f"{REGISTRY_PATH.as_posix()}: row {row_number}: unknown attribute "
                f"'{attribute_code}'"
            )
            continue
        if attribute.get("data_type") != "enum":
            errors.append(
                f"{REGISTRY_PATH.as_posix()}: row {row_number}: attribute "
                f"'{attribute_code}' is not enum"
            )
            continue
        if attribute.get("status") != "active":
            errors.append(
                f"{REGISTRY_PATH.as_posix()}: row {row_number}: attribute "
                f"'{attribute_code}' is not active"
            )
        rules.append(EnumDomainRule(attribute_code, domain_file))

    return tuple(rules), errors


def load_enum_domain_values(
    root: Path,
) -> tuple[dict[str, frozenset[str]], tuple[EnumDomainRule, ...], list[str]]:
    """Resolve each registered attribute to its active controlled values."""

    root = root.resolve()
    rules, errors = load_enum_domain_rules(root)
    values_by_attribute: dict[str, frozenset[str]] = {}
    cache: dict[str, frozenset[str]] = {}

    for rule in rules:
        if rule.domain_file in cache:
            values_by_attribute[rule.attribute_code] = cache[rule.domain_file]
            continue
        relative = rule.relative_path
        fields, rows, file_errors = _read_csv(root / relative)
        errors.extend(file_errors)
        if file_errors:
            continue
        if fields != DOMAIN_FIELDS:
            errors.append(
                f"{relative.as_posix()}: expected header {DOMAIN_FIELDS}, found {fields}"
            )
            continue
        codes: set[str] = set()
        for row_number, row in enumerate(rows, start=2):
            code = row.get("code", "")
            if not code:
                errors.append(f"{relative.as_posix()}: row {row_number}: empty code")
                continue
            if code in codes:
                errors.append(
                    f"{relative.as_posix()}: row {row_number}: duplicate code '{code}'"
                )
                continue
            codes.add(code)
            if not row.get("name", ""):
                errors.append(f"{relative.as_posix()}: row {row_number}: empty name")
            if row.get("status") != "active":
                errors.append(
                    f"{relative.as_posix()}: row {row_number}: status must be active"
                )
        if not codes:
            errors.append(f"{relative.as_posix()}: domain must contain at least one code")
            continue
        resolved = frozenset(codes)
        cache[rule.domain_file] = resolved
        values_by_attribute[rule.attribute_code] = resolved

    return values_by_attribute, rules, errors


def validate_enum_domains(root: Path) -> tuple[int, list[str]]:
    """Validate registry files and all enum-valued configuration observations."""

    root = root.resolve()
    values_by_attribute, rules, errors = load_enum_domain_values(root)
    attributes_fields, attributes_rows, attribute_errors = _read_csv(
        root / "data/master/attributes.csv"
    )
    values_fields, value_rows, value_errors = _read_csv(
        root / "data/master/configuration_attribute_values.csv"
    )
    errors.extend(attribute_errors)
    errors.extend(value_errors)
    if attribute_errors or value_errors:
        return 0, errors
    if "code" not in attributes_fields or "data_type" not in attributes_fields:
        errors.append("data/master/attributes.csv: missing code or data_type column")
        return 0, errors
    if "attribute_code" not in values_fields or "value" not in values_fields:
        errors.append(
            "data/master/configuration_attribute_values.csv: missing attribute_code or value column"
        )
        return 0, errors

    attribute_types = {
        row.get("code", ""): row.get("data_type", "") for row in attributes_rows
    }
    checked = len(rules)
    for row_number, row in enumerate(value_rows, start=2):
        attribute_code = row.get("attribute_code", "")
        if attribute_types.get(attribute_code) != "enum":
            continue
        checked += 1
        domain_values = values_by_attribute.get(attribute_code)
        if domain_values is None:
            errors.append(
                "data/master/configuration_attribute_values.csv: row "
                f"{row_number}: enum attribute '{attribute_code}' has no registered domain"
            )
            continue
        value = row.get("value", "")
        if value not in domain_values:
            errors.append(
                "data/master/configuration_attribute_values.csv: row "
                f"{row_number}: value '{value}' is not in the registered domain for "
                f"'{attribute_code}'"
            )

    return checked, errors
