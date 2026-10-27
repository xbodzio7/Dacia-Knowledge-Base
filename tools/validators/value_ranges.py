"""Validation for source-backed numeric configuration value ranges."""

from __future__ import annotations

import csv
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

RANGE_PATH = Path("data/master/configuration_attribute_value_ranges.csv")
RANGE_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "minimum_value",
    "maximum_value",
    "lower_inclusive",
    "upper_inclusive",
    "observation_date",
    "source_code",
    "notes",
)
INTEGER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)")
SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _read(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]], list[str]]:
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


def _canonical_numeric(data_type: str, value: str) -> tuple[Decimal | None, str | None]:
    if data_type == "integer":
        if INTEGER_RE.fullmatch(value) is None:
            return None, "must be a canonical integer"
        return Decimal(value), None
    if data_type != "decimal":
        return None, "attribute must be integer or decimal"
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        return None, "must be a decimal"
    if not parsed.is_finite():
        return None, "must be finite"
    canonical = format(parsed, "f")
    if "." in canonical:
        canonical = canonical.rstrip("0").rstrip(".")
    if canonical in {"-0", ""}:
        canonical = "0"
    if value != canonical:
        return None, f"must use canonical decimal form {canonical!r}"
    return parsed, None


def validate_configuration_value_ranges(root: Path) -> tuple[int, list[str]]:
    """Validate the range table, references, endpoints and scalar separation."""

    root = root.resolve()
    master = root / "data" / "master"
    fields, ranges, errors = _read(master / "configuration_attribute_value_ranges.csv")
    if errors:
        return 0, errors
    if fields != RANGE_FIELDS:
        return 0, [
            f"{RANGE_PATH.as_posix()}: expected header {RANGE_FIELDS}, found {fields}"
        ]

    _, attributes, attribute_errors = _read(master / "attributes.csv")
    _, configurations, configuration_errors = _read(master / "configurations.csv")
    _, sources, source_errors = _read(master / "sources.csv")
    _, source_configurations, source_configuration_errors = _read(
        master / "source_configurations.csv"
    )
    _, fuels, fuel_errors = _read(master / "enums" / "fuel_types.csv")
    _, scalars, scalar_errors = _read(master / "configuration_attribute_values.csv")
    errors.extend(attribute_errors)
    errors.extend(configuration_errors)
    errors.extend(source_errors)
    errors.extend(source_configuration_errors)
    errors.extend(fuel_errors)
    errors.extend(scalar_errors)
    if errors:
        return 0, errors

    attributes_by_code = {row.get("code", ""): row for row in attributes}
    configuration_codes = {row.get("code", "") for row in configurations}
    sources_by_code = {row.get("code", ""): row for row in sources}
    source_pairs = {
        (row.get("source_code", ""), row.get("configuration_code", ""))
        for row in source_configurations
    }
    fuel_codes = {row.get("code", "") for row in fuels}
    scalar_semantic = {
        (
            row.get("configuration_code", ""),
            row.get("attribute_code", ""),
            row.get("fuel_type_code", ""),
            row.get("observation_date", ""),
        )
        for row in scalars
    }

    ids: dict[int, int] = {}
    codes: dict[str, int] = {}
    semantic_keys: dict[tuple[str, str, str, str], int] = {}
    for row_number, row in enumerate(ranges, start=2):
        prefix = f"{RANGE_PATH.as_posix()}: row {row_number}"
        try:
            row_id = int(row.get("id", ""))
            if row_id < 1 or str(row_id) != row.get("id", ""):
                raise ValueError
        except ValueError:
            errors.append(f"{prefix}: id must be a canonical positive integer")
            row_id = -1
        if row_id in ids:
            errors.append(f"{prefix}: duplicate id {row_id} (first seen at row {ids[row_id]})")
        elif row_id > 0:
            ids[row_id] = row_number

        code = row.get("code", "")
        normalized_code = code.casefold()
        if not code:
            errors.append(f"{prefix}: empty code")
        elif normalized_code in codes:
            errors.append(f"{prefix}: duplicate code {code!r} (first seen at row {codes[normalized_code]})")
        else:
            codes[normalized_code] = row_number

        configuration = row.get("configuration_code", "")
        attribute_code = row.get("attribute_code", "")
        fuel = row.get("fuel_type_code", "")
        observed = row.get("observation_date", "")
        source_code = row.get("source_code", "")
        semantic = (configuration, attribute_code, fuel, observed)
        if semantic in semantic_keys:
            errors.append(f"{prefix}: duplicate semantic range (first seen at row {semantic_keys[semantic]})")
        else:
            semantic_keys[semantic] = row_number
        if semantic in scalar_semantic:
            errors.append(f"{prefix}: conflicts with a scalar observation on the same date")

        if configuration not in configuration_codes:
            errors.append(f"{prefix}: unknown configuration {configuration!r}")
        attribute = attributes_by_code.get(attribute_code)
        if attribute is None:
            errors.append(f"{prefix}: unknown attribute {attribute_code!r}")
            data_type = ""
        else:
            data_type = attribute.get("data_type", "")
            if attribute.get("status") != "active":
                errors.append(f"{prefix}: attribute {attribute_code!r} is not active")
            if data_type not in {"integer", "decimal"}:
                errors.append(f"{prefix}: attribute {attribute_code!r} is not numeric")
        if fuel and fuel not in fuel_codes:
            errors.append(f"{prefix}: unknown fuel_type_code {fuel!r}")

        source = sources_by_code.get(source_code)
        if source is None:
            errors.append(f"{prefix}: unknown source {source_code!r}")
        else:
            if source.get("status") != "active":
                errors.append(f"{prefix}: source {source_code!r} is not active")
            if SHA256_RE.fullmatch(source.get("sha256", "")) is None:
                errors.append(f"{prefix}: source {source_code!r} has invalid SHA-256")
            if not source.get("file_path", ""):
                errors.append(f"{prefix}: source {source_code!r} has empty file_path")
        if (source_code, configuration) not in source_pairs:
            errors.append(f"{prefix}: source does not document configuration")

        try:
            if date.fromisoformat(observed).isoformat() != observed:
                raise ValueError
        except ValueError:
            errors.append(f"{prefix}: observation_date must use YYYY-MM-DD")
        for flag in ("lower_inclusive", "upper_inclusive"):
            if row.get(flag) not in {"true", "false"}:
                errors.append(f"{prefix}: {flag} must be true or false")
        if not row.get("notes", ""):
            errors.append(f"{prefix}: notes must not be empty")

        minimum, minimum_error = _canonical_numeric(data_type, row.get("minimum_value", ""))
        maximum, maximum_error = _canonical_numeric(data_type, row.get("maximum_value", ""))
        if minimum_error:
            errors.append(f"{prefix}: minimum_value {minimum_error}")
        if maximum_error:
            errors.append(f"{prefix}: maximum_value {maximum_error}")
        if minimum is not None and maximum is not None and minimum >= maximum:
            errors.append(f"{prefix}: minimum_value must be less than maximum_value")

    if ids and sorted(ids) != list(range(1, len(ids) + 1)):
        errors.append(f"{RANGE_PATH.as_posix()}: ids must form a contiguous sequence starting at 1")
    return len(ranges), errors
