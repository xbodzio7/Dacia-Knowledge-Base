#!/usr/bin/env python3
"""Import exact Jogger brochure chassis observations."""

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
SPEC_PATH = ROOT / "data" / "imports" / "brochure_technical_values" / "jogger-chassis-20251217.json"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
SOURCE_CODE = "src_pl_jogger_brochure_20251217"
SOURCE_PATH = ROOT / "PDF" / "Broszury" / "DACIA JOGGER broszura 20251217.pdf"
SOURCE_SHA = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
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
    "turning_circle_between_kerbs": ("decimal", "m", "active"),
    "standard_tyre_specification": ("string", "", "active"),
    "front_suspension": ("string", "", "active"),
    "rear_suspension": ("string", "", "active"),
}
EXPECTED_CONFIGURATIONS = {
    "jogger_essential_5seat_ecog120_manual",
    "jogger_expression_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "jogger_expression_5seat_tce110_manual",
    "jogger_extreme_5seat_tce110_manual",
    "jogger_journey_5seat_tce110_manual",
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_essential_7seat_ecog120_manual",
    "jogger_expression_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_automatic",
    "jogger_journey_7seat_ecog120_automatic",
    "jogger_expression_7seat_tce110_manual",
    "jogger_extreme_7seat_tce110_manual",
    "jogger_journey_7seat_tce110_manual",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
}
EXPECTED_POWERTRAINS = Counter({"Eco-G 120": 10, "TCe 110": 6, "hybrid 155": 6})
EXPECTED_TRANSMISSIONS = Counter({"manual": 12, "automatic": 10})
EXPECTED_EXCLUSIONS = {
    "ambiguous_mass_table_labels",
    "blank_wltp_cells",
    "powertrain_and_performance_rows_out_of_scope",
    "later_observations_remain_current",
    "generic_dimensions_and_cargo_out_of_scope",
}
MASS_ATTRIBUTES = {
    "kerb_weight",
    "minimum_kerb_weight",
    "maximum_kerb_weight",
    "gross_vehicle_weight",
    "gross_train_weight",
    "maximum_payload",
    "payload",
}


class ImportContractError(RuntimeError):
    """Raised when the reviewed Jogger chassis import contract drifts."""


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
    if data_type == "decimal":
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ImportContractError(f"invalid decimal: {label}") from exc
        ensure(parsed.is_finite(), f"nonfinite decimal: {label}")
        ensure(re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value) is not None, f"noncanonical decimal: {label}")
    elif data_type == "string":
        ensure(value.strip() == value and value != "", f"invalid string: {label}")
    else:
        raise ImportContractError(f"unsupported data type: {data_type}")


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported spec version")
    ensure(payload.get("kind") == "jogger_chassis_observations", "unexpected spec kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "review date differs")
    ensure(payload.get("observation_date") == "2025-12-17", "observation date differs")
    ensure(payload.get("source_code") == SOURCE_CODE, "source code differs")
    ensure(payload.get("source_page") == 19, "source page differs")
    ensure(payload.get("source_section") == "ZAWIESZENIE I UKŁAD KIEROWNICZY", "source section differs")
    ensure(payload.get("value_id_start") == 2480, "value ID start differs")

    configurations = payload.get("configurations")
    ensure(isinstance(configurations, list) and len(configurations) == 22, "expected 22 configurations")
    ensure(len(set(configurations)) == 22, "configuration list contains duplicates")
    ensure(set(configurations) == EXPECTED_CONFIGURATIONS, "configuration set differs")

    observations = payload.get("observations")
    ensure(isinstance(observations, list) and len(observations) == 4, "expected four observations")
    ensure({str(item.get("attribute_code", "")) for item in observations if isinstance(item, dict)} == set(ATTRIBUTE_CONTRACTS), "attribute set differs")
    for item in observations:
        ensure(isinstance(item, dict) and set(item) == {"attribute_code", "value", "source_text"}, "observation fields differ")
        attribute = str(item["attribute_code"])
        validate_value(ATTRIBUTE_CONTRACTS[attribute][0], str(item["value"]), attribute)
        ensure(str(item["source_text"]).strip(), f"source text missing: {attribute}")

    exclusions = payload.get("excluded_evidence")
    ensure(isinstance(exclusions, list), "excluded evidence is missing")
    ensure({str(item.get("code", "")) for item in exclusions if isinstance(item, dict)} == EXPECTED_EXCLUSIONS, "exclusion set differs")
    return payload


def verify_source() -> None:
    registry = {row["code"]: row for row in read_rows(MASTER / "sources.csv")}
    row = registry.get(SOURCE_CODE)
    ensure(row is not None and row.get("status") == "active", "active source missing")
    ensure(row.get("source_type") == "brochure_pdf", "source type differs")
    ensure(row.get("publisher") == "Dacia" and row.get("market") == "PL", "source identity differs")
    ensure(row.get("document_date") == "2025-12-17", "source date differs")
    ensure(row.get("file_path") == "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf", "source path differs")
    ensure(row.get("sha256") == SOURCE_SHA, "source registry hash differs")
    ensure(SOURCE_PATH.is_file() and file_sha256(SOURCE_PATH) == SOURCE_SHA, "archived source hash differs")


def verify_references(spec: Mapping[str, Any]) -> None:
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for code, contract in ATTRIBUTE_CONTRACTS.items():
        row = attributes.get(code)
        ensure(row is not None, f"attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit"), row.get("status")) == contract, f"attribute contract differs: {code}")

    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    selected = [configurations.get(str(code)) for code in spec["configurations"]]
    ensure(all(row is not None and row.get("status") == "active" for row in selected), "active target configuration missing")
    ensure(Counter(row["powertrain_label"] for row in selected if row is not None) == EXPECTED_POWERTRAINS, "powertrain distribution differs")
    ensure(Counter(row["transmission_type"] for row in selected if row is not None) == EXPECTED_TRANSMISSIONS, "transmission distribution differs")

    relationships = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for code in EXPECTED_CONFIGURATIONS:
        ensure((SOURCE_CODE, code, "brochure_technical_data_for") in relationships, f"source relationship missing: {code}")


def expected_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for configuration in spec["configurations"]:
        for observation in spec["observations"]:
            attribute = str(observation["attribute_code"])
            result.append({
                "id": str(int(spec["value_id_start"]) + len(result)),
                "code": f"{configuration}_{attribute}_20251217",
                "configuration_code": str(configuration),
                "attribute_code": attribute,
                "fuel_type_code": "",
                "gear_number": "",
                "value": str(observation["value"]),
                "observation_date": str(spec["observation_date"]),
                "source_code": SOURCE_CODE,
                "notes": f"Source page {spec['source_page']}, section {spec['source_section']}: {observation['source_text']}",
            })
    ensure(len(result) == 88, "expected 88 generated values")
    ensure([int(row["id"]) for row in result] == list(range(2480, 2568)), "generated IDs differ")
    ensure(len({row["code"] for row in result}) == 88, "generated codes are not unique")
    ensure(Counter(row["attribute_code"] for row in result) == Counter({code: 22 for code in ATTRIBUTE_CONTRACTS}), "attribute distribution differs")
    ensure(not ({row["attribute_code"] for row in result} & MASS_ATTRIBUTES), "mass-table evidence entered the package")
    return result


def plan(expected: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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
        matched = by_code.get(row["code"])
        if matched is not None:
            ensure(matched == row, f"existing row differs: {row['code']}")
            existing.append(row)
            continue
        identity = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"])
        ensure(row["id"] not in by_id, f"ID already used: {row['id']}")
        ensure(identity not in identities, f"observation identity already used: {identity}")
        missing.append(row)
    return missing, existing


def apply(expected: Sequence[Mapping[str, str]]) -> None:
    missing, _ = plan(expected)
    if missing:
        write_rows_atomic(VALUE_PATH, VALUE_FIELDS, [*read_rows(VALUE_PATH), *missing])


def verify_package(expected: Sequence[Mapping[str, str]]) -> None:
    missing, existing = plan(expected)
    ensure(not missing and len(existing) == 88, f"package incomplete: missing={len(missing)}, existing={len(existing)}")
    package = [row for row in read_rows(VALUE_PATH) if 2480 <= int(row["id"]) <= 2567]
    ensure(package == [dict(row) for row in expected], "package ID slice differs")
    ensure(not any(row["source_code"] == SOURCE_CODE and row["attribute_code"] in MASS_ATTRIBUTES and row["observation_date"] == "2025-12-17" for row in read_rows(VALUE_PATH)), "ambiguous Jogger mass evidence was imported")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        spec = load_spec()
        verify_source()
        verify_references(spec)
        expected = expected_rows(spec)
        if args.apply:
            apply(expected)
        verify_package(expected)
    except (ImportContractError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}")
        return 1
    print("PASS: Jogger brochure chassis observations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
