#!/usr/bin/env python3
"""Import source-backed Bigster MY26 equipment and commercial mappings."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
IMPORTS = ROOT / "data" / "imports"
SOURCE = ROOT / "PDF" / "Cenniki" / "DACIA BIGSTER cennik MY26 20260703.pdf"
SOURCE_CODE = "src_pl_bigster_price_my26_20260703"
SOURCE_SHA256 = "9528654fb3daf3767a2defbbc80e8a85abceecb11e04bb176aa0b76443be178a"
DATE = "2026-07-03"

EQUIPMENT_SPEC = IMPORTS / "bigster_equipment_availability_20260703.csv"
COMMERCIAL_ITEMS_SPEC = IMPORTS / "bigster_commercial_items_20260703.csv"
COMMERCIAL_ATTRIBUTES_SPEC = IMPORTS / "bigster_commercial_item_attributes_20260703.csv"
COMMERCIAL_CONFIGURATIONS_SPEC = IMPORTS / "bigster_commercial_item_configurations_20260703.csv"

AVAILABILITY_OUTPUT = MASTER / "configuration_attribute_availability.csv"
ITEMS_OUTPUT = MASTER / "commercial_items.csv"
ITEM_ATTRIBUTES_OUTPUT = MASTER / "commercial_item_attributes.csv"
ITEM_CONFIGURATIONS_OUTPUT = MASTER / "commercial_item_configurations.csv"

EQUIPMENT_FIELDS = (
    "configuration_code",
    "attribute_code",
    "availability_status",
    "source_page",
    "source_label",
    "normalization_notes",
)
AVAILABILITY_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "availability_status",
    "observation_date",
    "source_code",
    "notes",
)
ITEM_SPEC_FIELDS = ("code", "name", "item_type", "status", "notes")
ITEM_FIELDS = (
    "id",
    "code",
    "name",
    "item_type",
    "observation_date",
    "source_code",
    "status",
    "notes",
)
ITEM_ATTRIBUTE_SPEC_FIELDS = (
    "code",
    "commercial_item_code",
    "attribute_code",
    "source_text",
    "notes",
)
ITEM_ATTRIBUTE_FIELDS = ("id",) + ITEM_ATTRIBUTE_SPEC_FIELDS
ITEM_CONFIGURATION_SPEC_FIELDS = (
    "code",
    "commercial_item_code",
    "configuration_code",
    "availability_status",
    "amount",
    "currency_code",
    "notes",
)
ITEM_CONFIGURATION_FIELDS = (
    "id",
    "code",
    "commercial_item_code",
    "configuration_code",
    "availability_status",
    "amount",
    "currency_code",
    "price_date",
    "source_code",
    "notes",
)

STATUSES = frozenset({"standard", "optional", "not_available"})
STATUS_COUNTS = {"standard": 1045, "optional": 92, "not_available": 179}


class ContractError(RuntimeError):
    """Raised when the versioned source contract cannot be reproduced."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot read source {path}: {exc}") from exc
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ContractError(f"missing CSV header: {path}")
            return list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def require_header(path: Path, fields: Sequence[str]) -> None:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle), None)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot inspect {path}: {exc}") from exc
    if header != list(fields):
        raise ContractError(f"unexpected header in {path}: {header!r}")


def semantic_payload(
    rows: Iterable[dict[str, str]], fields: Sequence[str]
) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def bigster_configurations() -> list[dict[str, str]]:
    result = [
        row
        for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
        and row.get("code", "").startswith("bigster_")
    ]
    if len(result) != 14:
        raise ContractError(f"expected 14 active Bigster configurations, found {len(result)}")
    return result


def load_equipment_spec() -> list[dict[str, str]]:
    require_header(EQUIPMENT_SPEC, EQUIPMENT_FIELDS)
    rows = read_rows(EQUIPMENT_SPEC)
    if len(rows) != 1316:
        raise ContractError(f"expected 1,316 equipment rows, found {len(rows)}")

    keys: set[tuple[str, str]] = set()
    for row in rows:
        configuration = row["configuration_code"].strip()
        attribute = row["attribute_code"].strip()
        status = row["availability_status"].strip()
        key = (configuration, attribute)
        if not configuration or not attribute or key in keys:
            raise ContractError(f"blank or duplicate equipment key: {key!r}")
        keys.add(key)
        if status not in STATUSES:
            raise ContractError(f"invalid equipment status for {key}: {status!r}")
        if row["source_page"].strip() not in {"4", "5", "4/5"}:
            raise ContractError(f"invalid source page for {key}")
        if not row["source_label"].strip():
            raise ContractError(f"missing source label for {key}")
        row["configuration_code"] = configuration
        row["attribute_code"] = attribute
        row["availability_status"] = status

    configurations = {row["code"] for row in bigster_configurations()}
    spec_configurations = {row["configuration_code"] for row in rows}
    if spec_configurations != configurations:
        raise ContractError("equipment spec configuration coverage differs from active Bigster catalogue")

    counts = Counter(row["configuration_code"] for row in rows)
    if set(counts.values()) != {94}:
        raise ContractError("each Bigster configuration must receive 94 equipment attributes")
    attributes = {row["attribute_code"] for row in rows}
    if len(attributes) != 94:
        raise ContractError(f"expected 94 equipment attributes, found {len(attributes)}")
    if dict(Counter(row["availability_status"] for row in rows)) != STATUS_COUNTS:
        raise ContractError("unexpected Bigster equipment status distribution")
    return rows


def generated_availability_rows() -> list[dict[str, str]]:
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source SHA-256 mismatch: {SOURCE}")
    spec = load_equipment_spec()

    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    invalid = sorted(
        attribute
        for attribute in {row["attribute_code"] for row in spec}
        if attribute not in attributes
        or attributes[attribute].get("status") != "active"
        or (
            attributes[attribute].get("data_type") != "boolean"
            and attribute != "rear_seat_folding"
        )
    )
    if invalid:
        raise ContractError("inactive, missing or incompatible attributes: " + ", ".join(invalid))

    active_statuses = {
        row["code"]
        for row in read_rows(MASTER / "enums" / "equipment_availability_statuses.csv")
        if row.get("status") == "active"
    }
    if not STATUSES <= active_statuses:
        raise ContractError("required availability statuses are not active")

    source_pairs = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    missing_pairs = sorted(
        configuration
        for configuration in {row["configuration_code"] for row in spec}
        if (SOURCE_CODE, configuration) not in source_pairs
    )
    if missing_pairs:
        raise ContractError("Bigster source does not document: " + ", ".join(missing_pairs))

    result: list[dict[str, str]] = []
    for row in spec:
        notes = (
            f"Source page {row['source_page']}: {row['source_label']}. "
            "Trim-level status expanded only to this source-backed configuration."
        )
        if row["normalization_notes"].strip():
            notes += f" {row['normalization_notes'].strip()}"
        result.append(
            {
                "code": (
                    f"{row['configuration_code']}_{row['attribute_code']}_20260703"
                ),
                "configuration_code": row["configuration_code"],
                "attribute_code": row["attribute_code"],
                "availability_status": row["availability_status"],
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": notes,
            }
        )
    return result


def load_commercial_items_spec() -> list[dict[str, str]]:
    require_header(COMMERCIAL_ITEMS_SPEC, ITEM_SPEC_FIELDS)
    rows = read_rows(COMMERCIAL_ITEMS_SPEC)
    if len(rows) != 7 or len({row["code"] for row in rows}) != 7:
        raise ContractError("expected seven unique Bigster commercial items")
    if {row["item_type"] for row in rows} - {"package", "option"}:
        raise ContractError("invalid Bigster commercial item type")
    if {row["status"] for row in rows} != {"active"}:
        raise ContractError("Bigster commercial items must be active")
    return rows


def generated_commercial_items() -> list[dict[str, str]]:
    return [
        {
            "code": row["code"],
            "name": row["name"],
            "item_type": row["item_type"],
            "observation_date": DATE,
            "source_code": SOURCE_CODE,
            "status": row["status"],
            "notes": row["notes"],
        }
        for row in load_commercial_items_spec()
    ]


def load_commercial_attributes_spec() -> list[dict[str, str]]:
    require_header(COMMERCIAL_ATTRIBUTES_SPEC, ITEM_ATTRIBUTE_SPEC_FIELDS)
    rows = read_rows(COMMERCIAL_ATTRIBUTES_SPEC)
    if len(rows) != 17 or len({row["code"] for row in rows}) != 17:
        raise ContractError("expected seventeen unique Bigster commercial memberships")
    item_codes = {row["code"] for row in load_commercial_items_spec()}
    attribute_codes = {row["code"] for row in read_rows(MASTER / "attributes.csv")}
    for row in rows:
        if row["commercial_item_code"] not in item_codes:
            raise ContractError(f"unknown commercial item: {row['commercial_item_code']}")
        if row["attribute_code"] not in attribute_codes:
            raise ContractError(f"unknown commercial attribute: {row['attribute_code']}")
        if not row["source_text"].strip():
            raise ContractError(f"missing source text for membership: {row['code']}")
    return rows


def generated_commercial_attributes() -> list[dict[str, str]]:
    return [dict(row) for row in load_commercial_attributes_spec()]


def load_commercial_configurations_spec() -> list[dict[str, str]]:
    require_header(COMMERCIAL_CONFIGURATIONS_SPEC, ITEM_CONFIGURATION_SPEC_FIELDS)
    rows = read_rows(COMMERCIAL_CONFIGURATIONS_SPEC)
    if len(rows) != 48 or len({row["code"] for row in rows}) != 48:
        raise ContractError("expected forty-eight unique Bigster commercial mappings")
    items = {row["code"] for row in load_commercial_items_spec()}
    configurations = {row["code"] for row in bigster_configurations()}
    for row in rows:
        if row["commercial_item_code"] not in items:
            raise ContractError(f"unknown mapped commercial item: {row['commercial_item_code']}")
        if row["configuration_code"] not in configurations:
            raise ContractError(f"unknown mapped Bigster configuration: {row['configuration_code']}")
        if row["availability_status"] != "optional":
            raise ContractError(f"mapping is not optional: {row['code']}")
        if row["currency_code"] != "PLN":
            raise ContractError(f"mapping currency is not PLN: {row['code']}")
        try:
            amount = int(row["amount"])
        except ValueError as exc:
            raise ContractError(f"mapping amount is not an integer: {row['code']}") from exc
        if amount <= 0:
            raise ContractError(f"mapping amount is not positive: {row['code']}")
    return rows


def generated_commercial_configurations() -> list[dict[str, str]]:
    return [
        {
            "code": row["code"],
            "commercial_item_code": row["commercial_item_code"],
            "configuration_code": row["configuration_code"],
            "availability_status": row["availability_status"],
            "amount": row["amount"],
            "currency_code": row["currency_code"],
            "price_date": DATE,
            "source_code": SOURCE_CODE,
            "notes": row["notes"],
        }
        for row in load_commercial_configurations_spec()
    ]


def _assert_subset(
    actual: list[dict[str, str]],
    expected: list[dict[str, str]],
    fields: Sequence[str],
    label: str,
) -> None:
    if semantic_payload(actual, fields) != semantic_payload(expected, fields):
        raise ContractError(f"stored {label} rows differ from generated contract")


def _assert_contiguous_ids(rows: list[dict[str, str]], start: int, end: int, label: str) -> None:
    try:
        ids = [int(row["id"]) for row in rows]
    except (KeyError, ValueError) as exc:
        raise ContractError(f"{label} IDs must be integers") from exc
    if ids != list(range(start, end + 1)):
        raise ContractError(f"{label} IDs must be the contiguous suffix {start}-{end}")


def check() -> None:
    expected_availability = generated_availability_rows()
    require_header(AVAILABILITY_OUTPUT, AVAILABILITY_FIELDS)
    actual_availability = [
        row
        for row in read_rows(AVAILABILITY_OUTPUT)
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code", "").startswith("bigster_")
    ]
    _assert_subset(
        actual_availability,
        expected_availability,
        AVAILABILITY_FIELDS[1:],
        "Bigster equipment availability",
    )
    _assert_contiguous_ids(actual_availability, 3157, 4472, "Bigster availability")

    expected_items = generated_commercial_items()
    require_header(ITEMS_OUTPUT, ITEM_FIELDS)
    actual_items = [
        row for row in read_rows(ITEMS_OUTPUT) if row.get("source_code") == SOURCE_CODE
    ]
    _assert_subset(actual_items, expected_items, ITEM_FIELDS[1:], "Bigster commercial items")
    _assert_contiguous_ids(actual_items, 22, 28, "Bigster commercial item")

    expected_attributes = generated_commercial_attributes()
    require_header(ITEM_ATTRIBUTES_OUTPUT, ITEM_ATTRIBUTE_FIELDS)
    actual_attributes = [
        row
        for row in read_rows(ITEM_ATTRIBUTES_OUTPUT)
        if row.get("commercial_item_code", "").startswith("bigster_")
    ]
    _assert_subset(
        actual_attributes,
        expected_attributes,
        ITEM_ATTRIBUTE_FIELDS[1:],
        "Bigster commercial membership",
    )
    _assert_contiguous_ids(actual_attributes, 53, 69, "Bigster commercial membership")

    expected_configurations = generated_commercial_configurations()
    require_header(ITEM_CONFIGURATIONS_OUTPUT, ITEM_CONFIGURATION_FIELDS)
    actual_configurations = [
        row
        for row in read_rows(ITEM_CONFIGURATIONS_OUTPUT)
        if row.get("source_code") == SOURCE_CODE
    ]
    _assert_subset(
        actual_configurations,
        expected_configurations,
        ITEM_CONFIGURATION_FIELDS[1:],
        "Bigster commercial mapping",
    )
    _assert_contiguous_ids(actual_configurations, 87, 134, "Bigster commercial mapping")

    print(
        "Bigster equipment and commercial mapping: PASS "
        "(94 attributes, 1,316 availability rows, 7 items, 48 mappings)"
    )


def _merge_by_code(
    current: list[dict[str, str]],
    expected: list[dict[str, str]],
    fields: Sequence[str],
    selector,
    expected_previous_maximum_id: int,
    label: str,
) -> list[dict[str, str]]:
    selected = [row for row in current if selector(row)]
    expected_by_code = {row["code"]: row for row in expected}
    selected_by_code = {row["code"]: row for row in selected}
    if len(selected_by_code) != len(selected):
        raise ContractError(f"duplicate existing {label} code")
    extra = sorted(set(selected_by_code) - set(expected_by_code))
    if extra:
        raise ContractError(f"unexpected existing {label}: " + ", ".join(extra))
    for code, row in selected_by_code.items():
        if tuple(row.get(field, "") for field in fields) != tuple(
            expected_by_code[code].get(field, "") for field in fields
        ):
            raise ContractError(f"conflicting existing {label}: {code}")

    result = list(current)
    missing = [row for row in expected if row["code"] not in selected_by_code]
    if not missing:
        return result
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError(f"{label} IDs must be integers") from exc
    if maximum_id != expected_previous_maximum_id:
        raise ContractError(
            f"expected {label} suffix after {expected_previous_maximum_id}, found {maximum_id}"
        )
    for offset, row in enumerate(missing, start=1):
        result.append({"id": str(maximum_id + offset), **row})
    return result


def _write_csv(path: Path, fields: Sequence[str], rows: list[dict[str, str]]) -> Path:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise ContractError(f"cannot write temporary CSV for {path}: {exc}") from exc
    return temporary


def apply() -> None:
    require_header(AVAILABILITY_OUTPUT, AVAILABILITY_FIELDS)
    availability = read_rows(AVAILABILITY_OUTPUT)
    existing_availability = [
        row
        for row in availability
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code", "").startswith("bigster_")
    ]
    expected_availability = generated_availability_rows()
    if existing_availability:
        _assert_subset(
            existing_availability,
            expected_availability,
            AVAILABILITY_FIELDS[1:],
            "Bigster equipment availability",
        )
        new_availability = availability
    else:
        try:
            maximum_id = max(int(row["id"]) for row in availability)
        except (KeyError, ValueError) as exc:
            raise ContractError("availability IDs must be integers") from exc
        if maximum_id != 3156:
            raise ContractError(
                f"expected Bigster availability suffix after 3156, found {maximum_id}"
            )
        new_availability = availability + [
            {"id": str(maximum_id + offset), **row}
            for offset, row in enumerate(expected_availability, start=1)
        ]

    require_header(ITEMS_OUTPUT, ITEM_FIELDS)
    items = read_rows(ITEMS_OUTPUT)
    new_items = _merge_by_code(
        items,
        generated_commercial_items(),
        ITEM_FIELDS[1:],
        lambda row: row.get("source_code") == SOURCE_CODE,
        27,
        "Bigster commercial item",
    )

    require_header(ITEM_ATTRIBUTES_OUTPUT, ITEM_ATTRIBUTE_FIELDS)
    item_attributes = read_rows(ITEM_ATTRIBUTES_OUTPUT)
    new_item_attributes = _merge_by_code(
        item_attributes,
        generated_commercial_attributes(),
        ITEM_ATTRIBUTE_FIELDS[1:],
        lambda row: row.get("commercial_item_code", "").startswith("bigster_"),
        68,
        "Bigster commercial membership",
    )

    require_header(ITEM_CONFIGURATIONS_OUTPUT, ITEM_CONFIGURATION_FIELDS)
    item_configurations = read_rows(ITEM_CONFIGURATIONS_OUTPUT)
    new_item_configurations = _merge_by_code(
        item_configurations,
        generated_commercial_configurations(),
        ITEM_CONFIGURATION_FIELDS[1:],
        lambda row: row.get("source_code") == SOURCE_CODE,
        86,
        "Bigster commercial mapping",
    )

    outputs = (
        (AVAILABILITY_OUTPUT, AVAILABILITY_FIELDS, new_availability),
        (ITEMS_OUTPUT, ITEM_FIELDS, new_items),
        (ITEM_ATTRIBUTES_OUTPUT, ITEM_ATTRIBUTE_FIELDS, new_item_attributes),
        (ITEM_CONFIGURATIONS_OUTPUT, ITEM_CONFIGURATION_FIELDS, new_item_configurations),
    )
    temporaries: list[tuple[Path, Path]] = []
    try:
        for path, fields, rows in outputs:
            temporaries.append((path, _write_csv(path, fields, rows)))
        for path, temporary in temporaries:
            temporary.replace(path)
    finally:
        for _, temporary in temporaries:
            temporary.unlink(missing_ok=True)

    print("Imported Bigster equipment availability and commercial mappings.")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    try:
        if arguments.apply:
            apply()
        check()
        return 0
    except ContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
