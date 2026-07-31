#!/usr/bin/env python3
"""Import source-bounded Spring commercial packages and charging options."""
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
SOURCE = ROOT / "PDF" / "Broszury" / "DACIA SPRING broszura 20260219.pdf"
SOURCE_CODE = "src_pl_spring_brochure_20260219"
SOURCE_SHA256 = "73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d"
DATE = "2026-02-19"

ITEMS_SPEC = IMPORTS / "spring_commercial_items_20260219.csv"
ATTRIBUTES_SPEC = IMPORTS / "spring_commercial_item_attributes_20260219.csv"
CONFIGURATIONS_SPEC = IMPORTS / "spring_commercial_item_configurations_20260219.csv"
ITEMS_OUTPUT = MASTER / "commercial_items.csv"
ATTRIBUTES_OUTPUT = MASTER / "commercial_item_attributes.csv"
CONFIGURATIONS_OUTPUT = MASTER / "commercial_item_configurations.csv"

ITEM_SPEC_FIELDS = ("code", "name", "item_type", "status", "notes")
ATTRIBUTE_SPEC_FIELDS = (
    "code",
    "commercial_item_code",
    "attribute_code",
    "source_text",
    "notes",
)
CONFIGURATION_SPEC_FIELDS = (
    "code",
    "commercial_item_code",
    "configuration_code",
    "availability_status",
    "amount",
    "currency_code",
    "source_page",
    "notes",
)
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
ATTRIBUTE_FIELDS = ("id",) + ATTRIBUTE_SPEC_FIELDS
CONFIGURATION_FIELDS = (
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

SELECTED_CONFIGURATIONS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}
EXPECTED_ITEMS = {
    "spring_type2_charging_cable_option",
    "spring_techno_package",
    "spring_dc40_charging_option",
    "spring_power_package",
    "spring_city_package",
}
EXPECTED_MEMBERSHIP_COUNTS = {
    "spring_type2_charging_cable_option": 1,
    "spring_techno_package": 7,
    "spring_dc40_charging_option": 3,
    "spring_power_package": 4,
    "spring_city_package": 3,
}
EXPECTED_MAPPING_COUNTS = {
    "spring_type2_charging_cable_option": 3,
    "spring_techno_package": 1,
    "spring_dc40_charging_option": 1,
    "spring_power_package": 1,
    "spring_city_package": 1,
}
EXPECTED_MAPPING_PAGES = {
    ("spring_type2_charging_cable_option", "spring_essential_electric70_automatic"): "13",
    ("spring_type2_charging_cable_option", "spring_expression_electric70_automatic"): "14",
    ("spring_type2_charging_cable_option", "spring_extreme_electric100_automatic"): "15",
    ("spring_techno_package", "spring_expression_electric70_automatic"): "14",
    ("spring_dc40_charging_option", "spring_expression_electric70_automatic"): "14",
    ("spring_power_package", "spring_extreme_electric100_automatic"): "15",
    ("spring_city_package", "spring_extreme_electric100_automatic"): "15",
}
EXPECTED_ITEM_IDS = (29, 33)
EXPECTED_ATTRIBUTE_IDS = (70, 87)
EXPECTED_CONFIGURATION_IDS = (143, 149)


class ContractError(RuntimeError):
    """Raised when the reviewed Spring commercial contract cannot be reproduced."""


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


def selected_configurations() -> set[str]:
    rows = read_rows(MASTER / "configurations.csv")
    selected = {
        row["code"]
        for row in rows
        if row.get("code") in SELECTED_CONFIGURATIONS and row.get("status") == "active"
    }
    if selected != SELECTED_CONFIGURATIONS:
        raise ContractError("the three reviewed active Spring configurations are not present")
    spring_codes = {row["code"] for row in rows if row.get("code", "").startswith("spring_")}
    if spring_codes != SELECTED_CONFIGURATIONS:
        raise ContractError("Spring package must not create or target any additional configuration")
    return selected


def verify_source_contract() -> None:
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source SHA-256 mismatch: {SOURCE}")
    selected_configurations()
    documented = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    missing = sorted(
        configuration
        for configuration in SELECTED_CONFIGURATIONS
        if (SOURCE_CODE, configuration) not in documented
    )
    if missing:
        raise ContractError("Spring brochure does not document: " + ", ".join(missing))


def load_items_spec() -> list[dict[str, str]]:
    require_header(ITEMS_SPEC, ITEM_SPEC_FIELDS)
    rows = read_rows(ITEMS_SPEC)
    codes = {row["code"].strip() for row in rows}
    if len(rows) != 5 or codes != EXPECTED_ITEMS:
        raise ContractError("expected the five reviewed Spring commercial items")
    if {row["item_type"].strip() for row in rows} != {"package", "option"}:
        raise ContractError("Spring commercial item types differ from the review")
    if {row["status"].strip() for row in rows} != {"active"}:
        raise ContractError("Spring commercial items must be active")
    if any(not row["name"].strip() or not row["notes"].strip() for row in rows):
        raise ContractError("Spring commercial items require names and boundary notes")
    return rows


def load_attributes_spec() -> list[dict[str, str]]:
    require_header(ATTRIBUTES_SPEC, ATTRIBUTE_SPEC_FIELDS)
    rows = read_rows(ATTRIBUTES_SPEC)
    if len(rows) != 18 or len({row["code"] for row in rows}) != 18:
        raise ContractError("expected eighteen unique Spring commercial memberships")
    if dict(Counter(row["commercial_item_code"] for row in rows)) != EXPECTED_MEMBERSHIP_COUNTS:
        raise ContractError("Spring commercial membership distribution differs from review")
    active_attributes = {
        row["code"]
        for row in read_rows(MASTER / "attributes.csv")
        if row.get("status") == "active"
    }
    for row in rows:
        if row["commercial_item_code"] not in EXPECTED_ITEMS:
            raise ContractError(f"unknown Spring commercial item: {row['commercial_item_code']}")
        if row["attribute_code"] not in active_attributes:
            raise ContractError(f"unknown or inactive commercial attribute: {row['attribute_code']}")
        if not row["source_text"].strip():
            raise ContractError(f"missing exact source text: {row['code']}")
    return rows


def load_configurations_spec() -> list[dict[str, str]]:
    require_header(CONFIGURATIONS_SPEC, CONFIGURATION_SPEC_FIELDS)
    rows = read_rows(CONFIGURATIONS_SPEC)
    if len(rows) != 7 or len({row["code"] for row in rows}) != 7:
        raise ContractError("expected seven unique Spring commercial mappings")
    if dict(Counter(row["commercial_item_code"] for row in rows)) != EXPECTED_MAPPING_COUNTS:
        raise ContractError("Spring commercial mapping distribution differs from review")
    if {
        (row["commercial_item_code"], row["configuration_code"]): row["source_page"]
        for row in rows
    } != EXPECTED_MAPPING_PAGES:
        raise ContractError("Spring item/configuration/page boundary differs from review")
    for row in rows:
        if row["commercial_item_code"] not in EXPECTED_ITEMS:
            raise ContractError(f"unknown mapped Spring item: {row['commercial_item_code']}")
        if row["configuration_code"] not in SELECTED_CONFIGURATIONS:
            raise ContractError(f"mapping targets an unreviewed configuration: {row['configuration_code']}")
        if row["availability_status"] != "optional":
            raise ContractError(f"Spring mapping is not optional: {row['code']}")
        if row["amount"] or row["currency_code"] != "PLN":
            raise ContractError(
                f"Spring mapping must preserve a blank amount and required PLN currency: {row['code']}"
            )
        if not row["notes"].strip():
            raise ContractError(f"missing blank-price note: {row['code']}")
    return rows


def generated_items() -> list[dict[str, str]]:
    verify_source_contract()
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
        for row in load_items_spec()
    ]


def generated_attributes() -> list[dict[str, str]]:
    verify_source_contract()
    return [dict(row) for row in load_attributes_spec()]


def generated_configurations() -> list[dict[str, str]]:
    verify_source_contract()
    return [
        {
            "code": row["code"],
            "commercial_item_code": row["commercial_item_code"],
            "configuration_code": row["configuration_code"],
            "availability_status": row["availability_status"],
            "amount": "",
            "currency_code": row["currency_code"],
            "price_date": "",
            "source_code": SOURCE_CODE,
            "notes": f"Source page {row['source_page']}. {row['notes']}",
        }
        for row in load_configurations_spec()
    ]


def _selected(rows: list[dict[str, str]], predicate) -> list[dict[str, str]]:
    return [row for row in rows if predicate(row)]


def _assert_rows(
    actual: list[dict[str, str]],
    expected: list[dict[str, str]],
    fields: Sequence[str],
    label: str,
) -> None:
    if semantic_payload(actual, fields) != semantic_payload(expected, fields):
        raise ContractError(f"stored {label} rows differ from generated contract")


def _assert_contiguous_ids(
    rows: list[dict[str, str]], expected: tuple[int, int], label: str
) -> None:
    try:
        ids = [int(row["id"]) for row in rows]
    except (KeyError, ValueError) as exc:
        raise ContractError(f"{label} IDs must be integers") from exc
    if ids != list(range(expected[0], expected[1] + 1)):
        raise ContractError(
            f"{label} IDs must be the contiguous suffix {expected[0]}-{expected[1]}"
        )


def check() -> None:
    require_header(ITEMS_OUTPUT, ITEM_FIELDS)
    items = read_rows(ITEMS_OUTPUT)
    actual_items = _selected(
        items,
        lambda row: row.get("source_code") == SOURCE_CODE
        and row.get("code") in EXPECTED_ITEMS,
    )
    _assert_rows(actual_items, generated_items(), ITEM_FIELDS[1:], "Spring commercial items")
    _assert_contiguous_ids(actual_items, EXPECTED_ITEM_IDS, "Spring commercial item")

    require_header(ATTRIBUTES_OUTPUT, ATTRIBUTE_FIELDS)
    attributes = read_rows(ATTRIBUTES_OUTPUT)
    actual_attributes = _selected(
        attributes,
        lambda row: row.get("commercial_item_code") in EXPECTED_ITEMS,
    )
    _assert_rows(
        actual_attributes,
        generated_attributes(),
        ATTRIBUTE_FIELDS[1:],
        "Spring commercial memberships",
    )
    _assert_contiguous_ids(actual_attributes, EXPECTED_ATTRIBUTE_IDS, "Spring membership")

    require_header(CONFIGURATIONS_OUTPUT, CONFIGURATION_FIELDS)
    configurations = read_rows(CONFIGURATIONS_OUTPUT)
    actual_configurations = _selected(
        configurations,
        lambda row: row.get("source_code") == SOURCE_CODE
        and row.get("commercial_item_code") in EXPECTED_ITEMS,
    )
    _assert_rows(
        actual_configurations,
        generated_configurations(),
        CONFIGURATION_FIELDS[1:],
        "Spring commercial mappings",
    )
    _assert_contiguous_ids(
        actual_configurations,
        EXPECTED_CONFIGURATION_IDS,
        "Spring commercial mapping",
    )
    print("Spring commercial packages: PASS (5 items, 18 memberships, 7 mappings)")


def _append_contract(
    current: list[dict[str, str]],
    expected: list[dict[str, str]],
    fields: Sequence[str],
    predicate,
    first_id: int,
    label: str,
) -> list[dict[str, str]]:
    actual = _selected(current, predicate)
    if actual:
        _assert_rows(actual, expected, fields, label)
        return current
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError(f"{label} IDs must be integers") from exc
    if maximum_id != first_id - 1:
        raise ContractError(
            f"expected {label} suffix after {first_id - 1}, found {maximum_id}"
        )
    return current + [
        {"id": str(maximum_id + offset), **row}
        for offset, row in enumerate(expected, start=1)
    ]


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
    verify_source_contract()
    require_header(ITEMS_OUTPUT, ITEM_FIELDS)
    require_header(ATTRIBUTES_OUTPUT, ATTRIBUTE_FIELDS)
    require_header(CONFIGURATIONS_OUTPUT, CONFIGURATION_FIELDS)

    items = _append_contract(
        read_rows(ITEMS_OUTPUT),
        generated_items(),
        ITEM_FIELDS[1:],
        lambda row: row.get("source_code") == SOURCE_CODE
        and row.get("code") in EXPECTED_ITEMS,
        EXPECTED_ITEM_IDS[0],
        "Spring commercial item",
    )
    attributes = _append_contract(
        read_rows(ATTRIBUTES_OUTPUT),
        generated_attributes(),
        ATTRIBUTE_FIELDS[1:],
        lambda row: row.get("commercial_item_code") in EXPECTED_ITEMS,
        EXPECTED_ATTRIBUTE_IDS[0],
        "Spring commercial membership",
    )
    configurations = _append_contract(
        read_rows(CONFIGURATIONS_OUTPUT),
        generated_configurations(),
        CONFIGURATION_FIELDS[1:],
        lambda row: row.get("source_code") == SOURCE_CODE
        and row.get("commercial_item_code") in EXPECTED_ITEMS,
        EXPECTED_CONFIGURATION_IDS[0],
        "Spring commercial mapping",
    )

    outputs = (
        (ITEMS_OUTPUT, ITEM_FIELDS, items),
        (ATTRIBUTES_OUTPUT, ATTRIBUTE_FIELDS, attributes),
        (CONFIGURATIONS_OUTPUT, CONFIGURATION_FIELDS, configurations),
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
    print("Imported 5 Spring commercial items, 18 memberships and 7 mappings.")


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
