#!/usr/bin/env python3
"""Import exact Sandero and Stepway brochure chassis observations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = ROOT / "data" / "imports" / "brochure_technical_values" / "sandero-stepway-chassis-20260202.json"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
VALUE_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "gear_number",
    "value",
    "observation_date",
    "source_code",
    "notes",
)
SOURCES = {
    "src_pl_sandero_brochure_20260202": (
        "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
        "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
    ),
    "src_pl_sandero_stepway_brochure_20260202": (
        "PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf",
        "800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48",
    ),
}
ATTRIBUTE_CONTRACTS = {
    "turning_circle_between_kerbs": ("decimal", "m", "active"),
    "maximum_kerb_weight": ("integer", "kg", "active"),
    "standard_tyre_specification": ("string", "", "active"),
    "front_suspension": ("string", "", "active"),
    "rear_suspension": ("string", "", "active"),
}
EXPECTED_CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_automatic",
}
EXPECTED_GROUPS = {
    "sandero_ecog120_manual": (2, "src_pl_sandero_brochure_20260202", "manual"),
    "sandero_ecog120_automatic": (2, "src_pl_sandero_brochure_20260202", "automatic"),
    "stepway_ecog120_manual": (3, "src_pl_sandero_stepway_brochure_20260202", "manual"),
    "stepway_ecog120_automatic": (2, "src_pl_sandero_stepway_brochure_20260202", "automatic"),
}
EXPECTED_ATTRIBUTE_COUNTS = Counter({code: 9 for code in ATTRIBUTE_CONTRACTS})


class ImportContractError(RuntimeError):
    """Raised when the reviewed chassis import contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ImportContractError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def write_rows_atomic(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_value(data_type: str, value: str, label: str) -> None:
    ensure(value != "", f"empty value: {label}")
    if data_type == "integer":
        ensure(re.fullmatch(r"(?:0|[1-9][0-9]*)", value) is not None, f"noncanonical integer: {label}")
    elif data_type == "decimal":
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ImportContractError(f"invalid decimal: {label}") from exc
        ensure(parsed.is_finite(), f"nonfinite decimal: {label}")
        ensure(str(parsed.normalize()) == str(Decimal(value).normalize()), f"noncanonical decimal: {label}")
    elif data_type == "string":
        ensure(value.strip() == value and value != "", f"invalid string: {label}")
    else:
        raise ImportContractError(f"unsupported data type: {data_type}")


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported package version")
    ensure(payload.get("kind") == "sandero_stepway_chassis_observations", "unexpected package kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "review date differs")
    ensure(payload.get("observation_date") == "2026-02-02", "observation date differs")
    ensure(payload.get("source_page") == 17, "source page differs")
    ensure(payload.get("value_id_start") == 2291, "value ID start differs")

    groups = payload.get("groups")
    ensure(isinstance(groups, list) and len(groups) == 4, "expected four chassis groups")
    seen_configurations: set[str] = set()
    for group in groups:
        ensure(isinstance(group, dict), "group must be an object")
        code = str(group.get("code", ""))
        ensure(code in EXPECTED_GROUPS, f"unexpected group: {code}")
        expected_count, expected_source, _ = EXPECTED_GROUPS[code]
        ensure(group.get("source_code") == expected_source, f"source differs: {code}")
        configurations = group.get("configurations")
        ensure(isinstance(configurations, list) and len(configurations) == expected_count, f"configuration count differs: {code}")
        for configuration in configurations:
            ensure(isinstance(configuration, str) and configuration not in seen_configurations, f"duplicate configuration: {configuration}")
            seen_configurations.add(configuration)
        observations = group.get("observations")
        ensure(isinstance(observations, list) and len(observations) == 5, f"observation count differs: {code}")
        ensure({str(item.get("attribute_code", "")) for item in observations if isinstance(item, dict)} == set(ATTRIBUTE_CONTRACTS), f"attribute set differs: {code}")
        for item in observations:
            ensure(isinstance(item, dict) and set(item) == {"attribute_code", "value", "source_text"}, f"observation fields differ: {code}")
            attribute = str(item["attribute_code"])
            value = str(item["value"])
            validate_value(ATTRIBUTE_CONTRACTS[attribute][0], value, f"{code}.{attribute}")
            ensure(str(item["source_text"]).strip(), f"empty source text: {code}.{attribute}")
    ensure(seen_configurations == EXPECTED_CONFIGURATIONS, "target configuration set differs")

    excluded = payload.get("excluded_evidence")
    ensure(isinstance(excluded, list) and {str(item.get("code", "")) for item in excluded if isinstance(item, dict)} == {
        "unmodeled_tce_columns",
        "legacy_turning_circle_not_rewritten",
        "later_configuration_values_remain_current",
        "unrelated_technical_rows_excluded",
    }, "exclusion boundary set differs")
    return payload


def verify_sources() -> None:
    registry = {row["code"]: row for row in read_rows(MASTER / "sources.csv")}
    for code, (file_path, expected_hash) in SOURCES.items():
        row = registry.get(code)
        ensure(row is not None and row.get("status") == "active", f"active source missing: {code}")
        ensure(row.get("source_type") == "brochure_pdf", f"source type differs: {code}")
        ensure(row.get("publisher") == "Dacia" and row.get("market") == "PL", f"source identity differs: {code}")
        ensure(row.get("document_date") == "2026-02-02", f"source date differs: {code}")
        ensure(row.get("file_path") == file_path and row.get("sha256") == expected_hash, f"source registry differs: {code}")
        archived = ROOT / file_path
        ensure(archived.is_file() and file_sha256(archived) == expected_hash, f"archived source hash differs: {code}")


def verify_references(spec: Mapping[str, Any]) -> None:
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for code, contract in ATTRIBUTE_CONTRACTS.items():
        row = attributes.get(code)
        ensure(row is not None, f"attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit"), row.get("status")) == contract, f"attribute contract differs: {code}")

    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    group_by_configuration = {
        str(configuration): str(group["code"])
        for group in spec["groups"]
        for configuration in group["configurations"]
    }
    for code in EXPECTED_CONFIGURATIONS:
        row = configurations.get(code)
        ensure(row is not None and row.get("status") == "active", f"active configuration missing: {code}")
        ensure(row.get("powertrain_label") == "Eco-G 120", f"powertrain differs: {code}")
        expected_transmission = EXPECTED_GROUPS[group_by_configuration[code]][2]
        ensure(row.get("transmission_type") == expected_transmission, f"transmission differs: {code}")

    relationships = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for group in spec["groups"]:
        source = str(group["source_code"])
        for configuration in group["configurations"]:
            ensure((source, str(configuration), "brochure_technical_data_for") in relationships, f"source relationship missing: {configuration}")


def row_code(configuration: str, attribute: str) -> str:
    return f"{configuration}_{attribute}_20260202"


def expected_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for group in spec["groups"]:
        for configuration in group["configurations"]:
            for observation in group["observations"]:
                attribute = str(observation["attribute_code"])
                value = str(observation["value"])
                validate_value(ATTRIBUTE_CONTRACTS[attribute][0], value, f"{configuration}.{attribute}")
                result.append({
                    "id": str(int(spec["value_id_start"]) + len(result)),
                    "code": row_code(str(configuration), attribute),
                    "configuration_code": str(configuration),
                    "attribute_code": attribute,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": value,
                    "observation_date": str(spec["observation_date"]),
                    "source_code": str(group["source_code"]),
                    "notes": f"Source page {spec['source_page']}, section {spec['source_section']}: {observation['source_text']}",
                })
    ensure(len(result) == 45, "expected 45 generated values")
    ensure([int(row["id"]) for row in result] == list(range(2291, 2336)), "generated IDs are not contiguous")
    ensure(len({row["code"] for row in result}) == 45, "generated codes are not unique")
    ensure(Counter(row["attribute_code"] for row in result) == EXPECTED_ATTRIBUTE_COUNTS, "attribute distribution differs")
    return result


def plan_import(expected: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(VALUE_PATH, VALUE_FIELDS)
    current = read_rows(VALUE_PATH)
    by_id = {row["id"]: row for row in current}
    by_code = {row["code"]: row for row in current}
    identities = {
        (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"]): row
        for row in current
    }
    missing: list[dict[str, str]] = []
    existing: list[dict[str, str]] = []
    for expected_row in expected:
        row = dict(expected_row)
        identity = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"])
        matched = by_code.get(row["code"])
        if matched is not None:
            ensure(matched == row, f"existing row differs: {row['code']}")
            existing.append(row)
            continue
        ensure(row["id"] not in by_id, f"value ID already used: {row['id']}")
        ensure(identity not in identities, f"observation identity already used: {identity}")
        missing.append(row)
    return missing, existing


def apply_import(expected: Sequence[Mapping[str, str]]) -> None:
    missing, _ = plan_import(expected)
    if not missing:
        return
    current = read_rows(VALUE_PATH)
    write_rows_atomic(VALUE_PATH, VALUE_FIELDS, [*current, *missing])
    missing_after, existing_after = plan_import(expected)
    ensure(not missing_after and len(existing_after) == 45, "post-apply verification failed")


def verify_package_rows(expected: Sequence[Mapping[str, str]]) -> None:
    package = [row for row in read_rows(VALUE_PATH) if 2291 <= int(row["id"]) <= 2335]
    ensure(package == [dict(row) for row in expected], "package ID slice differs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        spec = load_spec()
        verify_sources()
        verify_references(spec)
        expected = expected_rows(spec)
        if args.apply:
            apply_import(expected)
        missing, existing = plan_import(expected)
        ensure(not missing and len(existing) == 45, f"package incomplete: missing={len(missing)}, existing={len(existing)}")
        verify_package_rows(expected)
    except (ImportContractError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}")
        return 1
    print("PASS: Sandero and Stepway brochure chassis observations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
