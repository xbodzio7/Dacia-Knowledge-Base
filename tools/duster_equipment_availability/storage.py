"""Storage operations for Duster equipment availability."""
from __future__ import annotations

import csv
import os

from .constants import (
    ContractError, OUTPUT, OUTPUT_FIELDS, read_rows, require_header,
)
from .model import generated_rows


def semantic_payload(rows: list[dict[str, str]]) -> list[tuple[str, ...]]:
    return sorted(
        tuple(row.get(field, "") for field in OUTPUT_FIELDS[1:])
        for row in rows
    )


def stored_duster_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(OUTPUT, OUTPUT_FIELDS)
    current = read_rows(OUTPUT)
    duster = [
        row for row in current
        if row.get("configuration_code", "").startswith("duster_iii_")
    ]
    return current, duster


def check() -> None:
    _, actual = stored_duster_rows()
    expected = generated_rows()
    if len(actual) != 1392 or semantic_payload(actual) != semantic_payload(expected):
        raise ContractError("stored Duster rows differ from generated contract")
    ids = [int(row["id"]) for row in actual]
    if len(ids) != len(set(ids)):
        raise ContractError("duplicate Duster availability IDs")
    print("Duster equipment availability: PASS (58 attributes, 1,392 rows)")


def apply() -> None:
    current, actual = stored_duster_rows()
    expected = generated_rows()
    if actual:
        if semantic_payload(actual) != semantic_payload(expected):
            raise ContractError("partial or conflicting Duster rows already exist")
        print("Duster equipment availability is already current.")
        return
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError("availability IDs must be integers") from exc
    output = list(current)
    for offset, row in enumerate(expected, start=1):
        output.append({"id": str(maximum_id + offset), **row})
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(output)
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    print("Imported 1,392 Duster equipment availability rows.")
