"""Storage operations for Jogger equipment availability."""
from __future__ import annotations
import csv
import os
from .constants import ContractError, OUTPUT, OUTPUT_FIELDS, read_rows, require_header
from .model import generated_rows


def semantic_payload(rows: list[dict[str, str]]) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in OUTPUT_FIELDS[1:]) for row in rows)


def stored_jogger_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(OUTPUT, OUTPUT_FIELDS)
    current = read_rows(OUTPUT)
    jogger = [row for row in current if row.get("configuration_code", "").startswith("jogger_")]
    return current, jogger


def check() -> None:
    _, actual = stored_jogger_rows()
    expected = generated_rows()
    if len(actual) != 1166 or semantic_payload(actual) != semantic_payload(expected):
        raise ContractError("stored Jogger rows differ from generated contract")
    ids = [int(row["id"]) for row in actual]
    if ids != list(range(1812, 2978)):
        raise ContractError("Jogger availability IDs must be the contiguous suffix 1812-2977")
    print("Jogger equipment availability: PASS (53 attributes, 1,166 rows)")


def apply() -> None:
    current, actual = stored_jogger_rows()
    expected = generated_rows()
    if actual:
        if len(actual) != 1166 or semantic_payload(actual) != semantic_payload(expected):
            raise ContractError("partial or conflicting Jogger rows already exist")
        print("Jogger equipment availability is already current.")
        return
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError("availability IDs must be integers") from exc
    if maximum_id != 1811:
        raise ContractError(f"expected availability suffix to start after 1811, found {maximum_id}")
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
    print("Imported 1,166 Jogger equipment availability rows.")
