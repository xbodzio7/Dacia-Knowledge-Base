#!/usr/bin/env python3
"""Apply or verify declarative configuration-attribute range imports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from import_configuration_values import (
        ImportSpecError,
        _ensure,
        _require_positive_integer,
        _require_string,
        _strict_keys,
        _write_csv_atomic,
        read_csv,
        verify_registered_sources,
    )
except ModuleNotFoundError:  # package import in unit tests
    from tools.import_configuration_values import (
        ImportSpecError,
        _ensure,
        _require_positive_integer,
        _require_string,
        _strict_keys,
        _write_csv_atomic,
        read_csv,
        verify_registered_sources,
    )

SPEC_VERSION = 1
SPEC_KIND = "configuration_attribute_value_ranges"
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
TOP_LEVEL_KEYS = {
    "version",
    "kind",
    "id_start",
    "attribute_code",
    "attribute_contract",
    "observation_date",
    "fuel_type_code",
    "source_page",
    "source_section",
    "notes_template",
    "rows",
}
CONTRACT_KEYS = {"data_type", "unit", "status"}
ROW_REQUIRED_KEYS = {
    "configuration_code",
    "source_code",
    "minimum_value",
    "maximum_value",
    "lower_inclusive",
    "upper_inclusive",
    "source_text",
}
ROW_OPTIONAL_KEYS = {"fuel_type_code"}
ALLOWED_PLACEHOLDERS = {
    "page",
    "section",
    "source_text",
    "minimum_value",
    "maximum_value",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
}
INTEGER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)")


@dataclass(frozen=True)
class RangeImportRow:
    configuration_code: str
    source_code: str
    minimum_value: str
    maximum_value: str
    lower_inclusive: bool
    upper_inclusive: bool
    source_text: str
    fuel_type_code: str | None = None


@dataclass(frozen=True)
class RangeImportSpec:
    path: Path
    id_start: int
    attribute_code: str
    data_type: str
    unit: str
    status: str
    observation_date: str
    fuel_type_code: str
    source_page: int
    source_section: str
    notes_template: str
    rows: tuple[RangeImportRow, ...]


@dataclass(frozen=True)
class RangeImportPlan:
    expected_rows: tuple[dict[str, str], ...]
    existing_rows: tuple[dict[str, str], ...]
    missing_rows: tuple[dict[str, str], ...]


def _iso_date(value: str, label: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ImportSpecError(f"{label} must be an ISO date: {value!r}") from exc
    _ensure(parsed.isoformat() == value, f"{label} must use YYYY-MM-DD")
    return value


def _boolean(value: Any, label: str) -> bool:
    _ensure(isinstance(value, bool), f"{label} must be a boolean")
    return value


def _canonical_numeric(data_type: str, value: str, label: str) -> tuple[str, Decimal]:
    if data_type == "integer":
        _ensure(INTEGER_RE.fullmatch(value) is not None, f"{label} must be a canonical integer")
        parsed = Decimal(value)
        return value, parsed
    _ensure(data_type == "decimal", f"range attribute must be integer or decimal, found {data_type!r}")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ImportSpecError(f"{label} must be a decimal") from exc
    _ensure(parsed.is_finite(), f"{label} must be finite")
    canonical = format(parsed, "f")
    if "." in canonical:
        canonical = canonical.rstrip("0").rstrip(".")
    if canonical in {"-0", ""}:
        canonical = "0"
    _ensure(value == canonical, f"{label} must use canonical decimal form {canonical!r}")
    return value, parsed


def _validate_template(template: str) -> None:
    placeholders = set(re.findall(r"{([a-z_]+)}", template))
    _ensure(
        placeholders <= ALLOWED_PLACEHOLDERS,
        f"notes_template has unsupported placeholders: {sorted(placeholders - ALLOWED_PLACEHOLDERS)}",
    )
    _ensure(
        {"page", "section", "source_text"} <= placeholders,
        "notes_template must include {page}, {section} and {source_text}",
    )
    try:
        template.format(
            page=1,
            section="section",
            source_text="1-2",
            minimum_value="1",
            maximum_value="2",
            configuration_code="configuration",
            attribute_code="attribute",
            fuel_type_code="",
        )
    except (KeyError, ValueError) as exc:
        raise ImportSpecError(f"invalid notes_template: {exc}") from exc


def load_spec(path: Path) -> RangeImportSpec:
    """Load one strict versioned range-import specification."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ImportSpecError(f"cannot read spec {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ImportSpecError(f"invalid JSON in spec {path}: {exc}") from exc
    _ensure(isinstance(payload, dict), "spec root must be a JSON object")
    _strict_keys(payload, TOP_LEVEL_KEYS, label="spec")
    _ensure(payload["version"] == SPEC_VERSION, "unsupported spec version")
    _ensure(payload["kind"] == SPEC_KIND, "unsupported spec kind")

    contract = payload["attribute_contract"]
    _ensure(isinstance(contract, dict), "attribute_contract must be an object")
    _strict_keys(contract, CONTRACT_KEYS, label="attribute_contract")
    data_type = _require_string(contract["data_type"], "attribute_contract.data_type")
    _ensure(data_type in {"integer", "decimal"}, "range attribute must be integer or decimal")

    rows_payload = payload["rows"]
    _ensure(isinstance(rows_payload, list) and rows_payload, "rows must be a non-empty list")
    rows: list[RangeImportRow] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(rows_payload, start=1):
        label = f"rows[{index}]"
        _ensure(isinstance(item, dict), f"{label} must be an object")
        _strict_keys(item, ROW_REQUIRED_KEYS, optional=ROW_OPTIONAL_KEYS, label=label)
        configuration = _require_string(item["configuration_code"], f"{label}.configuration_code")
        row_fuel = item.get("fuel_type_code")
        if row_fuel is not None:
            row_fuel = _require_string(row_fuel, f"{label}.fuel_type_code", allow_empty=True)
        semantic = (configuration, "" if row_fuel is None else row_fuel)
        _ensure(semantic not in seen, f"{label} duplicates configuration and fuel context: {semantic}")
        seen.add(semantic)
        minimum = _require_string(item["minimum_value"], f"{label}.minimum_value")
        maximum = _require_string(item["maximum_value"], f"{label}.maximum_value")
        _, minimum_decimal = _canonical_numeric(data_type, minimum, f"{label}.minimum_value")
        _, maximum_decimal = _canonical_numeric(data_type, maximum, f"{label}.maximum_value")
        _ensure(minimum_decimal < maximum_decimal, f"{label} minimum_value must be less than maximum_value")
        rows.append(
            RangeImportRow(
                configuration_code=configuration,
                source_code=_require_string(item["source_code"], f"{label}.source_code"),
                minimum_value=minimum,
                maximum_value=maximum,
                lower_inclusive=_boolean(item["lower_inclusive"], f"{label}.lower_inclusive"),
                upper_inclusive=_boolean(item["upper_inclusive"], f"{label}.upper_inclusive"),
                source_text=_require_string(item["source_text"], f"{label}.source_text"),
                fuel_type_code=row_fuel,
            )
        )

    template = _require_string(payload["notes_template"], "notes_template")
    _validate_template(template)
    return RangeImportSpec(
        path=path.resolve(),
        id_start=_require_positive_integer(payload["id_start"], "id_start"),
        attribute_code=_require_string(payload["attribute_code"], "attribute_code"),
        data_type=data_type,
        unit=_require_string(contract["unit"], "attribute_contract.unit", allow_empty=True),
        status=_require_string(contract["status"], "attribute_contract.status"),
        observation_date=_iso_date(
            _require_string(payload["observation_date"], "observation_date"),
            "observation_date",
        ),
        fuel_type_code=_require_string(payload["fuel_type_code"], "fuel_type_code", allow_empty=True),
        source_page=_require_positive_integer(payload["source_page"], "source_page"),
        source_section=_require_string(payload["source_section"], "source_section"),
        notes_template=template,
        rows=tuple(rows),
    )


def _single(rows: list[dict[str, str]], code: str, label: str) -> dict[str, str]:
    matches = [row for row in rows if row.get("code") == code]
    _ensure(len(matches) == 1, f"expected exactly one {label} {code!r}")
    return matches[0]


def _row_code(spec: RangeImportSpec, configuration: str, fuel: str) -> str:
    parts = [configuration, spec.attribute_code]
    if fuel:
        parts.append(fuel)
    parts.extend(("range", spec.observation_date.replace("-", "")))
    return "_".join(parts)


def build_expected_rows(repository: Path, spec: RangeImportSpec) -> tuple[dict[str, str], ...]:
    """Build exact target rows after validating repository references."""

    master = repository / "data" / "master"
    _, attributes = read_csv(master / "attributes.csv")
    _, configurations = read_csv(master / "configurations.csv")
    _, sources = read_csv(master / "sources.csv")
    _, source_configurations = read_csv(master / "source_configurations.csv")
    _, fuels = read_csv(master / "enums" / "fuel_types.csv")
    _, scalar_values = read_csv(master / "configuration_attribute_values.csv")

    attribute = _single(attributes, spec.attribute_code, "attribute")
    actual_contract = {
        "data_type": attribute.get("data_type", ""),
        "unit": attribute.get("unit", ""),
        "status": attribute.get("status", ""),
    }
    expected_contract = {"data_type": spec.data_type, "unit": spec.unit, "status": spec.status}
    _ensure(actual_contract == expected_contract, f"attribute contract differs: expected {expected_contract}, found {actual_contract}")
    _ensure(spec.data_type in {"integer", "decimal"}, "range attribute must be numeric")

    configuration_codes = {row.get("code", "") for row in configurations}
    source_rows = {row.get("code", ""): row for row in sources}
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
        for row in scalar_values
    }

    result: list[dict[str, str]] = []
    for offset, row in enumerate(spec.rows):
        label = f"rows[{offset + 1}]"
        _ensure(row.configuration_code in configuration_codes, f"{label} references unknown configuration")
        source = source_rows.get(row.source_code)
        _ensure(source is not None, f"{label} references unknown source {row.source_code!r}")
        _ensure((row.source_code, row.configuration_code) in source_pairs, f"{label} source does not document configuration")
        _ensure(source.get("status") == "active", f"{label} source is not active")
        fuel = spec.fuel_type_code if row.fuel_type_code is None else row.fuel_type_code
        if fuel:
            _ensure(fuel in fuel_codes, f"{label} uses unknown fuel_type_code {fuel!r}")
        semantic = (row.configuration_code, spec.attribute_code, fuel, spec.observation_date)
        _ensure(semantic not in scalar_semantic, f"{label} conflicts with a scalar observation on the same date")
        notes = spec.notes_template.format(
            page=spec.source_page,
            section=spec.source_section,
            source_text=row.source_text,
            minimum_value=row.minimum_value,
            maximum_value=row.maximum_value,
            configuration_code=row.configuration_code,
            attribute_code=spec.attribute_code,
            fuel_type_code=fuel,
        )
        result.append(
            {
                "id": str(spec.id_start + offset),
                "code": _row_code(spec, row.configuration_code, fuel),
                "configuration_code": row.configuration_code,
                "attribute_code": spec.attribute_code,
                "fuel_type_code": fuel,
                "minimum_value": row.minimum_value,
                "maximum_value": row.maximum_value,
                "lower_inclusive": str(row.lower_inclusive).lower(),
                "upper_inclusive": str(row.upper_inclusive).lower(),
                "observation_date": spec.observation_date,
                "source_code": row.source_code,
                "notes": notes,
            }
        )
    _ensure(len({row["id"] for row in result}) == len(result), "spec generates duplicate IDs")
    _ensure(len({row["code"].casefold() for row in result}) == len(result), "spec generates duplicate codes")
    return tuple(result)


def plan_import(repository: Path, spec: RangeImportSpec) -> RangeImportPlan:
    expected = build_expected_rows(repository, spec)
    path = repository / "data" / "master" / "configuration_attribute_value_ranges.csv"
    fields, current = read_csv(path)
    _ensure(tuple(fields) == RANGE_FIELDS, "configuration value range CSV header differs")
    by_id = {row["id"]: row for row in current}
    by_code = {row["code"].casefold(): row for row in current}
    by_semantic = {
        (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"]): row
        for row in current
    }
    exact: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    for row in expected:
        semantic = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"])
        present = [candidate for candidate in (by_id.get(row["id"]), by_code.get(row["code"].casefold()), by_semantic.get(semantic)) if candidate is not None]
        if not present:
            missing.append(row)
        else:
            _ensure(all(candidate == row for candidate in present), f"existing range conflicts with spec: {row['code']}")
            exact.append(row)
    if missing:
        current_max = max((int(row["id"]) for row in current), default=0)
        first = int(missing[0]["id"])
        _ensure(first == current_max + 1, f"first missing ID must be {current_max + 1}, found {first}")
        _ensure([int(row["id"]) for row in missing] == list(range(first, first + len(missing))), "missing IDs must form a contiguous suffix")
    return RangeImportPlan(expected, tuple(exact), tuple(missing))


def apply_import(repository: Path, spec: RangeImportSpec) -> RangeImportPlan:
    plan = plan_import(repository, spec)
    if not plan.missing_rows:
        return plan
    path = repository / "data" / "master" / "configuration_attribute_value_ranges.csv"
    fields, current = read_csv(path)
    _write_csv_atomic(path, fields, [*current, *plan.missing_rows])
    verified = plan_import(repository, spec)
    _ensure(not verified.missing_rows, "ranges remain missing after apply")
    return verified


def verify_import(repository: Path, spec: RangeImportSpec) -> RangeImportPlan:
    plan = plan_import(repository, spec)
    _ensure(not plan.missing_rows, f"spec has {len(plan.missing_rows)} missing ranges")
    return plan


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate, apply or verify one configuration-value range import.")
    parser.add_argument("--spec", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--skip-source-text", action="store_true")
    parser.add_argument("--skip-source-files", action="store_true")
    parser.add_argument("--repository", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repository = args.repository.expanduser().resolve() if args.repository else Path(__file__).resolve().parents[1]
    try:
        spec = load_spec(args.spec.expanduser().resolve())
        if not args.skip_source_files:
            verify_registered_sources(repository, spec, verify_text=not args.skip_source_text)
        if args.apply:
            plan, mode = apply_import(repository, spec), "apply"
        elif args.verify:
            plan, mode = verify_import(repository, spec), "verify"
        else:
            plan, mode = plan_import(repository, spec), "plan"
        print(f"Spec     : {spec.path}")
        print(f"Attribute: {spec.attribute_code}")
        print(f"Ranges   : {len(plan.expected_rows)}")
        print(f"Existing : {len(plan.existing_rows)}")
        print(f"Missing  : {len(plan.missing_rows)}")
        print(f"Mode     : {mode}")
        print("PASS")
        return 0
    except ImportSpecError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
