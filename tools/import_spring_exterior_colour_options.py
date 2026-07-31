#!/usr/bin/env python3
"""Import source-bounded Spring exterior-colour commercial options."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
IMPORTS = ROOT / "data" / "imports"
SOURCE = ROOT / "PDF" / "Broszury" / "DACIA SPRING broszura 20260219.pdf"
SOURCE_CODE = "src_pl_spring_brochure_20260219"
SOURCE_SHA256 = "73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d"
DATE = "2026-02-19"
SOURCE_PAGE = "12"
SPEC = IMPORTS / "spring_exterior_colour_options_20260219.csv"
ITEMS_OUTPUT = MASTER / "commercial_items.csv"
ATTRIBUTES_OUTPUT = MASTER / "commercial_item_attributes.csv"
CONFIGURATIONS_OUTPUT = MASTER / "commercial_item_configurations.csv"

SPEC_FIELDS = ("code", "name", "finish_type", "source_label", "notes")
ITEM_FIELDS = (
    "id", "code", "name", "item_type", "observation_date", "source_code", "status", "notes"
)
ATTRIBUTE_FIELDS = (
    "id", "code", "commercial_item_code", "attribute_code", "source_text", "notes"
)
CONFIGURATION_FIELDS = (
    "id", "code", "commercial_item_code", "configuration_code", "availability_status",
    "amount", "currency_code", "price_date", "source_code", "notes"
)
CONFIGURATIONS = (
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
)
EXPECTED_COLOURS = {
    "spring_colour_czerwony_brick": ("Czerwony Brick", "non_metallic"),
    "spring_colour_seafoam": ("Seafoam", "non_metallic"),
    "spring_colour_szary_diamond": ("Szary Diamond", "metallic"),
    "spring_colour_lichen_khaki": ("Lichen Khaki", "non_metallic"),
    "spring_colour_niebieski_stonewash": ("Niebieski Stonewash", "non_metallic"),
    "spring_colour_biel_alpejska": ("Biel Alpejska", "non_metallic"),
}
EXPECTED_ITEM_IDS = (34, 39)
EXPECTED_ATTRIBUTE_IDS = (88, 93)
EXPECTED_CONFIGURATION_IDS = (150, 167)


class ContractError(RuntimeError):
    """Raised when the reviewed Spring colour contract cannot be reproduced."""


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


def semantic_payload(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def verify_source_and_scope() -> None:
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source SHA-256 mismatch: {SOURCE}")
    configurations = read_rows(MASTER / "configurations.csv")
    active_spring = {
        row["code"] for row in configurations
        if row.get("status") == "active" and row.get("code", "").startswith("spring_")
    }
    if active_spring != set(CONFIGURATIONS):
        raise ContractError("Spring colour package must target exactly the three existing active configurations")
    documented = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    missing = [code for code in CONFIGURATIONS if (SOURCE_CODE, code) not in documented]
    if missing:
        raise ContractError("source/configuration relationships missing: " + ", ".join(missing))
    attributes = {
        row["code"]: row for row in read_rows(MASTER / "attributes.csv")
    }
    colour = attributes.get("exterior_color")
    if colour is None or colour.get("status") != "active":
        raise ContractError("active exterior_color attribute is required")


def load_spec() -> list[dict[str, str]]:
    require_header(SPEC, SPEC_FIELDS)
    rows = read_rows(SPEC)
    if len(rows) != 6 or len({row["code"] for row in rows}) != 6:
        raise ContractError("expected six unique Spring colour rows")
    observed = {row["code"]: (row["name"], row["finish_type"]) for row in rows}
    if observed != EXPECTED_COLOURS:
        raise ContractError("Spring colour names or finish classifications differ from the reviewed page")
    for row in rows:
        if not row["source_label"].strip() or not row["notes"].strip():
            raise ContractError(f"missing source label or boundary note: {row['code']}")
        if "price is stated" not in row["notes"]:
            raise ContractError(f"blank-price boundary not explicit: {row['code']}")
    return rows


def generated_items() -> list[dict[str, str]]:
    verify_source_and_scope()
    return [
        {
            "code": row["code"],
            "name": row["name"],
            "item_type": "option",
            "observation_date": DATE,
            "source_code": SOURCE_CODE,
            "status": "active",
            "notes": (
                f"Official brochure page {SOURCE_PAGE} exterior-colour palette; "
                f"finish={row['finish_type']}. {row['notes']}"
            ),
        }
        for row in load_spec()
    ]


def generated_attributes() -> list[dict[str, str]]:
    verify_source_and_scope()
    return [
        {
            "code": f"{row['code']}__exterior_color",
            "commercial_item_code": row["code"],
            "attribute_code": "exterior_color",
            "source_text": row["source_label"],
            "notes": (
                f"Selectable exterior colour; finish={row['finish_type']}. "
                "This membership does not create a single scalar colour value for the configuration."
            ),
        }
        for row in load_spec()
    ]


def generated_configurations() -> list[dict[str, str]]:
    verify_source_and_scope()
    return [
        {
            "code": f"{row['code']}__{configuration}",
            "commercial_item_code": row["code"],
            "configuration_code": configuration,
            "availability_status": "optional",
            "amount": "",
            "currency_code": "PLN",
            "price_date": "",
            "source_code": SOURCE_CODE,
            "notes": (
                f"Source page {SOURCE_PAGE}. Palette entry {row['source_label']}; "
                "the page states no grade restriction and no price. PLN is only the required schema currency reference."
            ),
        }
        for row in load_spec()
        for configuration in CONFIGURATIONS
    ]


def selected(rows: list[dict[str, str]], predicate) -> list[dict[str, str]]:
    return [row for row in rows if predicate(row)]


def assert_payload(
    actual: list[dict[str, str]], expected: list[dict[str, str]], fields: Sequence[str], label: str
) -> None:
    if semantic_payload(actual, fields) != semantic_payload(expected, fields):
        raise ContractError(f"stored {label} differs from generated contract")


def assert_ids(rows: list[dict[str, str]], expected: tuple[int, int], label: str) -> None:
    try:
        ids = [int(row["id"]) for row in rows]
    except (KeyError, ValueError) as exc:
        raise ContractError(f"{label} IDs must be integers") from exc
    if ids != list(range(expected[0], expected[1] + 1)):
        raise ContractError(f"{label} IDs must be contiguous {expected[0]}-{expected[1]}")


def check() -> None:
    require_header(ITEMS_OUTPUT, ITEM_FIELDS)
    require_header(ATTRIBUTES_OUTPUT, ATTRIBUTE_FIELDS)
    require_header(CONFIGURATIONS_OUTPUT, CONFIGURATION_FIELDS)
    colour_codes = set(EXPECTED_COLOURS)

    items = selected(
        read_rows(ITEMS_OUTPUT),
        lambda row: row.get("source_code") == SOURCE_CODE and row.get("code") in colour_codes,
    )
    attributes = selected(
        read_rows(ATTRIBUTES_OUTPUT),
        lambda row: row.get("commercial_item_code") in colour_codes,
    )
    mappings = selected(
        read_rows(CONFIGURATIONS_OUTPUT),
        lambda row: row.get("source_code") == SOURCE_CODE and row.get("commercial_item_code") in colour_codes,
    )
    assert_payload(items, generated_items(), ITEM_FIELDS[1:], "Spring colour items")
    assert_payload(attributes, generated_attributes(), ATTRIBUTE_FIELDS[1:], "Spring colour memberships")
    assert_payload(mappings, generated_configurations(), CONFIGURATION_FIELDS[1:], "Spring colour mappings")
    assert_ids(items, EXPECTED_ITEM_IDS, "Spring colour item")
    assert_ids(attributes, EXPECTED_ATTRIBUTE_IDS, "Spring colour membership")
    assert_ids(mappings, EXPECTED_CONFIGURATION_IDS, "Spring colour mapping")
    print("Spring exterior colours: PASS (6 options, 6 memberships, 18 mappings)")


def append_contract(
    current: list[dict[str, str]], expected: list[dict[str, str]], fields: Sequence[str],
    predicate, first_id: int, label: str
) -> list[dict[str, str]]:
    actual = selected(current, predicate)
    if actual:
        assert_payload(actual, expected, fields, label)
        return current
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError(f"{label} IDs must be integers") from exc
    if maximum_id != first_id - 1:
        raise ContractError(f"expected {label} suffix after {first_id - 1}, found {maximum_id}")
    return current + [
        {"id": str(maximum_id + offset), **row}
        for offset, row in enumerate(expected, start=1)
    ]


def write_csv(path: Path, fields: Sequence[str], rows: list[dict[str, str]]) -> Path:
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
    verify_source_and_scope()
    require_header(ITEMS_OUTPUT, ITEM_FIELDS)
    require_header(ATTRIBUTES_OUTPUT, ATTRIBUTE_FIELDS)
    require_header(CONFIGURATIONS_OUTPUT, CONFIGURATION_FIELDS)
    colour_codes = set(EXPECTED_COLOURS)

    items = append_contract(
        read_rows(ITEMS_OUTPUT), generated_items(), ITEM_FIELDS[1:],
        lambda row: row.get("source_code") == SOURCE_CODE and row.get("code") in colour_codes,
        EXPECTED_ITEM_IDS[0], "Spring colour item",
    )
    attributes = append_contract(
        read_rows(ATTRIBUTES_OUTPUT), generated_attributes(), ATTRIBUTE_FIELDS[1:],
        lambda row: row.get("commercial_item_code") in colour_codes,
        EXPECTED_ATTRIBUTE_IDS[0], "Spring colour membership",
    )
    mappings = append_contract(
        read_rows(CONFIGURATIONS_OUTPUT), generated_configurations(), CONFIGURATION_FIELDS[1:],
        lambda row: row.get("source_code") == SOURCE_CODE and row.get("commercial_item_code") in colour_codes,
        EXPECTED_CONFIGURATION_IDS[0], "Spring colour mapping",
    )

    outputs = (
        (ITEMS_OUTPUT, ITEM_FIELDS, items),
        (ATTRIBUTES_OUTPUT, ATTRIBUTE_FIELDS, attributes),
        (CONFIGURATIONS_OUTPUT, CONFIGURATION_FIELDS, mappings),
    )
    temporaries: list[tuple[Path, Path]] = []
    try:
        for path, fields, rows in outputs:
            temporaries.append((path, write_csv(path, fields, rows)))
        for path, temporary in temporaries:
            temporary.replace(path)
    finally:
        for _, temporary in temporaries:
            temporary.unlink(missing_ok=True)
    print("Imported 6 Spring exterior-colour options, 6 memberships and 18 mappings.")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.apply:
            apply()
        check()
        return 0
    except ContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
