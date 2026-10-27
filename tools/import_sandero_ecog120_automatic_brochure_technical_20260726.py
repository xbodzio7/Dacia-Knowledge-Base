#!/usr/bin/env python3
"""Import exact Sandero Eco-G 120 automatic technical brochure values."""

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
SPEC_PATH = ROOT / "data" / "imports" / "brochure_technical_values" / "sandero-ecog120-automatic-20260202.json"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
SOURCE_CODE = "src_pl_sandero_brochure_20260202"
SOURCE_FILE = "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf"
SOURCE_SHA256 = "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97"
TARGET_CONFIGURATIONS = (
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
)
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
ATTRIBUTE_CONTRACTS = {
    "engine_power": ("integer", "kW", "active"),
    "engine_torque": ("integer", "Nm", "active"),
    "engine_displacement": ("integer", "cm3", "active"),
    "cylinder_count": ("integer", "", "active"),
    "total_valve_count": ("integer", "", "active"),
    "emission_standard": ("enum", "", "active"),
    "gearbox_type": ("enum", "", "active"),
    "gear_count": ("integer", "", "active"),
    "top_speed": ("integer", "km/h", "active"),
    "acceleration_0_100": ("decimal", "s", "active"),
    "fuel_tank_capacity": ("decimal", "L", "active"),
    "minimum_kerb_weight": ("integer", "kg", "active"),
    "gross_vehicle_weight": ("integer", "kg", "active"),
    "gross_train_weight": ("integer", "kg", "active"),
    "braked_trailer_weight": ("integer", "kg", "active"),
}
EXPECTED_ATTRIBUTE_COUNTS = Counter(
    {
        "engine_power": 4,
        "engine_torque": 4,
        "acceleration_0_100": 4,
        "engine_displacement": 2,
        "cylinder_count": 2,
        "total_valve_count": 2,
        "emission_standard": 2,
        "gearbox_type": 2,
        "gear_count": 2,
        "top_speed": 2,
        "fuel_tank_capacity": 2,
        "minimum_kerb_weight": 2,
        "gross_vehicle_weight": 2,
        "gross_train_weight": 2,
        "braked_trailer_weight": 2,
    }
)
EXPECTED_FUEL_COUNTS = Counter({"": 24, "lpg": 6, "petrol": 6})
FORBIDDEN_ATTRIBUTES = {
    "co2_emissions",
    "fuel_consumption_combined",
    "turning_circle",
    "front_suspension_specification",
    "rear_suspension_specification",
    "injection_type",
}


class ImportError(RuntimeError):
    """Raised when the reviewed automatic-Sandero import contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ImportError(message)


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
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported package version")
    ensure(
        payload.get("kind") == "sandero_ecog120_automatic_brochure_technical_values",
        "unexpected package kind",
    )
    ensure(payload.get("value_id_start") == 2189, "unexpected value ID start")
    ensure(payload.get("source_code") == SOURCE_CODE, "unexpected source code")
    ensure(payload.get("observation_date") == "2026-02-02", "unexpected observation date")
    ensure(payload.get("source_page") == 17, "unexpected source page")
    ensure(tuple(payload.get("configurations", [])) == TARGET_CONFIGURATIONS, "target configurations differ")

    observations = payload.get("observations")
    ensure(isinstance(observations, list) and len(observations) == 18, "expected 18 source observations")
    seen: set[tuple[str, str]] = set()
    for item in observations:
        ensure(isinstance(item, dict), "observation must be an object")
        ensure(set(item) == {"attribute_code", "fuel_type_code", "value", "source_text"}, "unexpected observation fields")
        attribute = str(item.get("attribute_code", ""))
        fuel = str(item.get("fuel_type_code", ""))
        ensure(attribute in ATTRIBUTE_CONTRACTS, f"unexpected attribute: {attribute}")
        ensure(attribute not in FORBIDDEN_ATTRIBUTES, f"forbidden attribute: {attribute}")
        ensure(fuel in {"", "lpg", "petrol"}, f"unexpected fuel context: {fuel}")
        ensure(str(item.get("value", "")) != "", f"empty value: {attribute}")
        ensure(str(item.get("source_text", "")).strip(), f"empty source text: {attribute}")
        key = (attribute, fuel)
        ensure(key not in seen, f"duplicate source observation: {key}")
        seen.add(key)

    ensure(
        Counter(str(item["attribute_code"]) for item in observations)
        == Counter(
            {
                "engine_power": 2,
                "engine_torque": 2,
                "acceleration_0_100": 2,
                **{
                    attribute: 1
                    for attribute in ATTRIBUTE_CONTRACTS
                    if attribute not in {"engine_power", "engine_torque", "acceleration_0_100"}
                },
            }
        ),
        "source observation attribute distribution differs",
    )
    excluded = payload.get("excluded_evidence")
    ensure(isinstance(excluded, list) and len(excluded) == 4, "expected four exclusion groups")
    ensure(
        {str(item.get("code", "")) for item in excluded if isinstance(item, dict)}
        == {
            "maximum_kerb_weight_requires_explicit_attribute",
            "wltp_country_placeholders_are_not_observations",
            "model_wide_chassis_rows_outside_exact_import",
            "tce100_column_without_exact_configuration",
        },
        "exclusion boundary set differs",
    )
    return payload


def validate_scalar(data_type: str, value: str, label: str) -> None:
    if data_type == "integer":
        ensure(re.fullmatch(r"-?(?:0|[1-9][0-9]*)", value) is not None, f"{label} is not a canonical integer")
        return
    if data_type == "decimal":
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ImportError(f"{label} is not a decimal") from exc
        ensure(parsed.is_finite(), f"{label} is not finite")
        return
    if data_type == "enum":
        ensure(value != "", f"{label} enum value is empty")
        return
    raise ImportError(f"unsupported data type: {data_type}")


def verify_source() -> None:
    sources = {row.get("code", ""): row for row in read_rows(MASTER / "sources.csv")}
    source = sources.get(SOURCE_CODE)
    ensure(source is not None and source.get("status") == "active", "active Sandero brochure source missing")
    ensure(source.get("source_type") == "brochure_pdf", "source type differs")
    ensure(source.get("publisher") == "Dacia" and source.get("market") == "PL", "source identity differs")
    ensure(source.get("document_date") == "2026-02-02", "source date differs")
    ensure(source.get("file_path") == SOURCE_FILE, "source path differs")
    ensure(source.get("sha256") == SOURCE_SHA256, "source registry hash differs")
    archived = ROOT / SOURCE_FILE
    ensure(archived.is_file() and file_sha256(archived) == SOURCE_SHA256, "archived source hash differs")


def verify_references() -> None:
    attributes = {row.get("code", ""): row for row in read_rows(MASTER / "attributes.csv")}
    for code, contract in ATTRIBUTE_CONTRACTS.items():
        row = attributes.get(code)
        ensure(row is not None, f"attribute missing: {code}")
        ensure(
            (row.get("data_type", ""), row.get("unit", ""), row.get("status", "")) == contract,
            f"attribute contract differs: {code}",
        )

    enum_domains = {
        row.get("attribute_code", ""): row.get("domain_file", "")
        for row in read_rows(MASTER / "attribute_enum_domains.csv")
        if row.get("status") == "active"
    }
    for attribute, expected in {
        "emission_standard": "euro_6e_bis",
        "gearbox_type": "dct",
    }.items():
        domain_file = enum_domains.get(attribute)
        ensure(domain_file, f"enum domain missing: {attribute}")
        values = {
            row.get("code", "")
            for row in read_rows(MASTER / "enums" / domain_file)
            if row.get("status") == "active"
        }
        ensure(expected in values, f"enum value missing: {attribute}={expected}")

    configurations = {row.get("code", ""): row for row in read_rows(MASTER / "configurations.csv")}
    for code in TARGET_CONFIGURATIONS:
        row = configurations.get(code)
        ensure(row is not None and row.get("status") == "active", f"active configuration missing: {code}")
        ensure(row.get("powertrain_label") == "Eco-G 120", f"powertrain differs: {code}")
        ensure(row.get("transmission_type") == "automatic", f"transmission differs: {code}")

    relationships = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for code in TARGET_CONFIGURATIONS:
        ensure(
            (SOURCE_CODE, code, "brochure_technical_data_for") in relationships,
            f"source relationship missing: {code}",
        )


def row_code(configuration: str, attribute: str, fuel: str) -> str:
    parts = [configuration, attribute]
    if fuel:
        parts.append(fuel)
    parts.append("20260202")
    return "_".join(parts)


def expected_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    observations = spec["observations"]
    for configuration in spec["configurations"]:
        for observation in observations:
            attribute = str(observation["attribute_code"])
            fuel = str(observation["fuel_type_code"])
            value = str(observation["value"])
            data_type = ATTRIBUTE_CONTRACTS[attribute][0]
            validate_scalar(data_type, value, f"{configuration}.{attribute}.{fuel}")
            result.append(
                {
                    "id": str(int(spec["value_id_start"]) + len(result)),
                    "code": row_code(str(configuration), attribute, fuel),
                    "configuration_code": str(configuration),
                    "attribute_code": attribute,
                    "fuel_type_code": fuel,
                    "gear_number": "",
                    "value": value,
                    "observation_date": str(spec["observation_date"]),
                    "source_code": SOURCE_CODE,
                    "notes": (
                        f"Source page {spec['source_page']}, section {spec['source_section']}: "
                        f"{observation['source_text']}"
                    ),
                }
            )

    ensure(len(result) == 36, "expected 36 generated values")
    ensure([int(row["id"]) for row in result] == list(range(2189, 2225)), "generated IDs are not contiguous")
    ensure(len({row["code"] for row in result}) == 36, "generated codes are not unique")
    ensure(Counter(row["attribute_code"] for row in result) == EXPECTED_ATTRIBUTE_COUNTS, "attribute counts differ")
    ensure(Counter(row["fuel_type_code"] for row in result) == EXPECTED_FUEL_COUNTS, "fuel counts differ")
    ensure(not ({row["attribute_code"] for row in result} & FORBIDDEN_ATTRIBUTES), "forbidden evidence was generated")
    return result


def merge_exact(existing: list[dict[str, str]], expected: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id = {row.get("id", ""): row for row in existing}
    by_code = {row.get("code", "").casefold(): row for row in existing}
    by_semantic = {
        (
            row.get("configuration_code", ""),
            row.get("attribute_code", ""),
            row.get("fuel_type_code", ""),
            row.get("gear_number", ""),
            row.get("observation_date", ""),
        ): row
        for row in existing
    }
    additions: list[dict[str, str]] = []
    for row in expected:
        semantic = (
            row["configuration_code"],
            row["attribute_code"],
            row["fuel_type_code"],
            row["gear_number"],
            row["observation_date"],
        )
        candidates = [
            by_id.get(row["id"]),
            by_code.get(row["code"].casefold()),
            by_semantic.get(semantic),
        ]
        present = [item for item in candidates if item is not None]
        if present:
            ensure(all(item == row for item in present), f"existing value differs: {row['code']}")
        else:
            additions.append(row)
    if additions:
        current_max = max((int(row["id"]) for row in existing), default=0)
        ensure(int(additions[0]["id"]) == current_max + 1, "first added ID is not append-only")
        ensure(
            [int(row["id"]) for row in additions]
            == list(range(current_max + 1, current_max + 1 + len(additions))),
            "added IDs are not a contiguous suffix",
        )
    return [*existing, *additions]


def apply(spec: Mapping[str, Any]) -> None:
    require_header(VALUE_PATH, VALUE_FIELDS)
    existing = read_rows(VALUE_PATH)
    merged = merge_exact(existing, expected_rows(spec))
    if merged != existing:
        write_rows_atomic(VALUE_PATH, VALUE_FIELDS, merged)


def check(spec: Mapping[str, Any]) -> None:
    require_header(VALUE_PATH, VALUE_FIELDS)
    expected = expected_rows(spec)
    existing = read_rows(VALUE_PATH)
    exact = {
        row.get("code", ""): row
        for row in existing
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code") in TARGET_CONFIGURATIONS
        and row.get("attribute_code") in ATTRIBUTE_CONTRACTS
    }
    ensure(len(exact) == 36, "master data does not contain exactly 36 package values")
    ensure(exact == {row["code"]: row for row in expected}, "master package values differ")

    target_rows = [row for row in existing if row.get("configuration_code") in TARGET_CONFIGURATIONS]
    ensure(
        not any(
            row.get("source_code") == SOURCE_CODE
            and row.get("attribute_code") in FORBIDDEN_ATTRIBUTES
            for row in target_rows
        ),
        "excluded brochure evidence was imported",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        verify_source()
        verify_references()
        spec = load_spec()
        if args.apply:
            apply(spec)
        check(spec)
    except (ImportError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("PASS: Sandero Eco-G 120 automatic brochure technical values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
