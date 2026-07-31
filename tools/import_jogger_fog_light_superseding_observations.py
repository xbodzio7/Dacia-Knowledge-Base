#!/usr/bin/env python3
"""Import July 2026 Jogger Expression fog-light superseding observations."""
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
SPEC = IMPORTS / "jogger_fog_lights_20260703.csv"
OUTPUT = MASTER / "configuration_attribute_availability.csv"

APRIL_SOURCE_CODE = "src_pl_jogger_price_my26_20260401"
APRIL_SOURCE = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
APRIL_SHA256 = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"
APRIL_DATE = "2026-04-01"
APRIL_PAGE = "5"

JULY_SOURCE_CODE = "src_pl_jogger_price_my26_20260703"
JULY_SOURCE = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260703.pdf"
JULY_SHA256 = "92606411c4d8c10dd830b0d1c387fe663c4c9618422c5db639c13a23138f4a87"
JULY_DATE = "2026-07-03"
JULY_PAGE = "4"
ATTRIBUTE_CODE = "fog_lights"
SOURCE_LABEL = "Światła przeciwmgłowe"

CONFIGURATIONS = (
    "jogger_expression_5seat_ecog120_manual",
    "jogger_expression_5seat_tce110_manual",
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_expression_7seat_ecog120_manual",
    "jogger_expression_7seat_tce110_manual",
    "jogger_expression_7seat_hybrid155_automatic",
)

SPEC_FIELDS = (
    "configuration_code",
    "attribute_code",
    "availability_status",
    "source_page",
    "source_label",
    "source_symbol",
    "notes",
)
OUTPUT_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "availability_status",
    "observation_date",
    "source_code",
    "notes",
)
EXPECTED_FIRST_ID = 5897
EXPECTED_LAST_ID = 5902


class ContractError(RuntimeError):
    """Raised when the dated Jogger fog-light contract cannot be reproduced."""


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot read source {path}: {exc}") from exc
    return digest.hexdigest()


def semantic_payload(
    rows: Iterable[dict[str, str]], fields: Sequence[str] = OUTPUT_FIELDS[1:]
) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def verify_repository_contract() -> None:
    if sha256(APRIL_SOURCE) != APRIL_SHA256:
        raise ContractError(f"April source SHA-256 mismatch: {APRIL_SOURCE}")
    if sha256(JULY_SOURCE) != JULY_SHA256:
        raise ContractError(f"July source SHA-256 mismatch: {JULY_SOURCE}")

    configurations = {
        row["code"]: row for row in read_rows(MASTER / "configurations.csv")
    }
    for code in CONFIGURATIONS:
        row = configurations.get(code)
        if (
            row is None
            or row.get("status") != "active"
            or row.get("version_code") != "jogger_expression"
        ):
            raise ContractError(f"missing or incompatible active configuration: {code}")

    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    attribute = attributes.get(ATTRIBUTE_CODE)
    if (
        attribute is None
        or attribute.get("status") != "active"
        or attribute.get("data_type") != "boolean"
    ):
        raise ContractError("active boolean fog_lights attribute is required")

    links = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    for source_code in (APRIL_SOURCE_CODE, JULY_SOURCE_CODE):
        missing = [
            configuration
            for configuration in CONFIGURATIONS
            if (source_code, configuration) not in links
        ]
        if missing:
            raise ContractError(
                f"{source_code} does not document: " + ", ".join(missing)
            )


def load_spec() -> list[dict[str, str]]:
    require_header(SPEC, SPEC_FIELDS)
    rows = read_rows(SPEC)
    if len(rows) != 6:
        raise ContractError(f"expected six July observations, found {len(rows)}")
    if tuple(row["configuration_code"] for row in rows) != CONFIGURATIONS:
        raise ContractError("July observation configuration order or boundary differs")
    if len({row["configuration_code"] for row in rows}) != 6:
        raise ContractError("July observation configurations must be unique")
    for row in rows:
        if row["attribute_code"] != ATTRIBUTE_CODE:
            raise ContractError(f"unexpected attribute: {row['attribute_code']}")
        if row["availability_status"] != "not_available":
            raise ContractError(f"unexpected July status: {row['availability_status']}")
        if row["source_page"] != JULY_PAGE:
            raise ContractError(f"unexpected July page: {row['source_page']}")
        if row["source_label"] != SOURCE_LABEL or row["source_symbol"] != "-":
            raise ContractError("July source label or direct matrix symbol differs")
        if "April standard observation" not in row["notes"]:
            raise ContractError("history-preservation note is required")
    return rows


def generated_rows() -> list[dict[str, str]]:
    verify_repository_contract()
    return [
        {
            "code": f"{row['configuration_code']}_{ATTRIBUTE_CODE}_20260703",
            "configuration_code": row["configuration_code"],
            "attribute_code": ATTRIBUTE_CODE,
            "availability_status": "not_available",
            "observation_date": JULY_DATE,
            "source_code": JULY_SOURCE_CODE,
            "notes": (
                f"Source page {JULY_PAGE}: {SOURCE_LABEL}. Direct Expression-column "
                "'-' cell expanded only to this exact source-backed configuration. "
                "The earlier 2026-04-01 standard observation remains preserved."
            ),
        }
        for row in load_spec()
    ]


def selected_july_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    configuration_set = set(CONFIGURATIONS)
    return [
        row
        for row in rows
        if row.get("source_code") == JULY_SOURCE_CODE
        and row.get("observation_date") == JULY_DATE
        and row.get("configuration_code") in configuration_set
        and row.get("attribute_code") == ATTRIBUTE_CODE
    ]


def april_history(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    configuration_set = set(CONFIGURATIONS)
    return [
        row
        for row in rows
        if row.get("source_code") == APRIL_SOURCE_CODE
        and row.get("observation_date") == APRIL_DATE
        and row.get("configuration_code") in configuration_set
        and row.get("attribute_code") == ATTRIBUTE_CODE
    ]


def verify_april_history(rows: list[dict[str, str]]) -> None:
    history = april_history(rows)
    if len(history) != 6:
        raise ContractError(f"expected six preserved April observations, found {len(history)}")
    if {row["configuration_code"] for row in history} != set(CONFIGURATIONS):
        raise ContractError("April history configuration boundary differs")
    for row in history:
        if row["availability_status"] != "standard":
            raise ContractError(f"April history is not standard: {row['code']}")
        if f"Source page {APRIL_PAGE}: {SOURCE_LABEL}." not in row["notes"]:
            raise ContractError(f"April source page or label differs: {row['code']}")


def check() -> None:
    require_header(OUTPUT, OUTPUT_FIELDS)
    current = read_rows(OUTPUT)
    verify_april_history(current)
    actual = selected_july_rows(current)
    expected = generated_rows()
    if semantic_payload(actual) != semantic_payload(expected):
        raise ContractError("stored July fog-light rows differ from generated contract")
    try:
        ids = [int(row["id"]) for row in actual]
    except (KeyError, ValueError) as exc:
        raise ContractError("July fog-light IDs must be integers") from exc
    if ids != list(range(EXPECTED_FIRST_ID, EXPECTED_LAST_ID + 1)):
        raise ContractError(
            f"July fog-light IDs must be contiguous {EXPECTED_FIRST_ID}-{EXPECTED_LAST_ID}"
        )
    print("Jogger fog-light history: PASS (6 April standard + 6 July not_available)")


def write_csv(path: Path, rows: list[dict[str, str]]) -> Path:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise ContractError(f"cannot write temporary CSV: {exc}") from exc
    return temporary


def apply() -> None:
    require_header(OUTPUT, OUTPUT_FIELDS)
    current = read_rows(OUTPUT)
    verify_april_history(current)
    expected = generated_rows()
    actual = selected_july_rows(current)
    if actual:
        if semantic_payload(actual) != semantic_payload(expected):
            raise ContractError("partial or conflicting July observations already exist")
        output_rows = current
    else:
        try:
            maximum_id = max(int(row["id"]) for row in current)
        except (KeyError, ValueError) as exc:
            raise ContractError("availability IDs must be integers") from exc
        if maximum_id != EXPECTED_FIRST_ID - 1:
            raise ContractError(
                f"expected July suffix after {EXPECTED_FIRST_ID - 1}, found {maximum_id}"
            )
        output_rows = current + [
            {"id": str(maximum_id + offset), **row}
            for offset, row in enumerate(expected, start=1)
        ]

    temporary = write_csv(OUTPUT, output_rows)
    try:
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    print("Imported six July Jogger Expression fog-light observations.")


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
