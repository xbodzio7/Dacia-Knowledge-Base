#!/usr/bin/env python3
"""Import direct Spring brochure equipment-availability matrix cells."""
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
SPEC = IMPORTS / "spring_equipment_availability_20260219.csv"
OUTPUT = MASTER / "configuration_attribute_availability.csv"
SOURCE_CONFIGURATION_OUTPUT = MASTER / "source_configurations.csv"

SPEC_FIELDS = (
    "configuration_code",
    "attribute_code",
    "availability_status",
    "source_page",
    "source_label",
    "normalization_notes",
)
SOURCE_CONFIGURATION_FIELDS = (
    "id",
    "source_code",
    "configuration_code",
    "relationship",
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
STATUSES = frozenset({"standard", "optional", "not_available"})
CONFIGURATION_VERSIONS = {
    "spring_essential_electric70_automatic": "spring_essential",
    "spring_expression_electric70_automatic": "spring_expression",
    "spring_extreme_electric100_automatic": "spring_extreme",
}
EXPECTED_ATTRIBUTES = 42
EXPECTED_ROWS = 126
EXPECTED_STATUS_COUNTS = {"standard": 106, "optional": 7, "not_available": 13}
EXPECTED_FIRST_ID = 5771
EXPECTED_LAST_ID = 5896
EXPECTED_SOURCE_CONFIGURATION_FIRST_ID = 248
EXPECTED_SOURCE_CONFIGURATION_LAST_ID = 250


class ContractError(RuntimeError):
    """Raised when the versioned Spring source contract cannot be reproduced."""


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
    rows: Iterable[dict[str, str]], fields: Sequence[str] = OUTPUT_FIELDS[1:]
) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def spring_configurations() -> list[dict[str, str]]:
    by_code = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    result = []
    for code, version in CONFIGURATION_VERSIONS.items():
        row = by_code.get(code)
        if row is None or row.get("status") != "active" or row.get("version_code") != version:
            raise ContractError(f"missing or incompatible active Spring configuration: {code}")
        result.append(row)
    if {row["code"] for row in result} != set(CONFIGURATION_VERSIONS):
        raise ContractError("Spring configuration contract differs from the selected source matrix")
    return result


def load_spec() -> list[dict[str, str]]:
    require_header(SPEC, SPEC_FIELDS)
    rows = read_rows(SPEC)
    if len(rows) != EXPECTED_ROWS:
        raise ContractError(f"expected {EXPECTED_ROWS} Spring equipment rows, found {len(rows)}")

    keys: set[tuple[str, str]] = set()
    for row in rows:
        configuration = row["configuration_code"].strip()
        attribute = row["attribute_code"].strip()
        status = row["availability_status"].strip()
        page = row["source_page"].strip()
        label = row["source_label"].strip()
        key = (configuration, attribute)
        if not configuration or not attribute or key in keys:
            raise ContractError(f"blank or duplicate Spring equipment key: {key!r}")
        keys.add(key)
        if configuration not in CONFIGURATION_VERSIONS:
            raise ContractError(f"configuration outside Spring matrix contract: {configuration}")
        if status not in STATUSES:
            raise ContractError(f"invalid Spring equipment status for {key}: {status!r}")
        if page not in {"19", "20"}:
            raise ContractError(f"invalid Spring source page for {key}: {page!r}")
        if not label:
            raise ContractError(f"missing Spring source label for {key}")
        row["configuration_code"] = configuration
        row["attribute_code"] = attribute
        row["availability_status"] = status
        row["source_page"] = page
        row["source_label"] = label

    counts = Counter(row["configuration_code"] for row in rows)
    if counts != Counter({code: EXPECTED_ATTRIBUTES for code in CONFIGURATION_VERSIONS}):
        raise ContractError("each selected Spring configuration must receive 42 attributes")
    attributes = {row["attribute_code"] for row in rows}
    if len(attributes) != EXPECTED_ATTRIBUTES:
        raise ContractError(f"expected {EXPECTED_ATTRIBUTES} Spring attributes, found {len(attributes)}")
    if dict(Counter(row["availability_status"] for row in rows)) != EXPECTED_STATUS_COUNTS:
        raise ContractError("unexpected Spring equipment status distribution")
    return rows


def generated_rows() -> list[dict[str, str]]:
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source SHA-256 mismatch: {SOURCE}")
    spring_configurations()
    spec = load_spec()

    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    invalid = sorted(
        code
        for code in {row["attribute_code"] for row in spec}
        if code not in attributes
        or attributes[code].get("status") != "active"
        or (attributes[code].get("data_type") != "boolean" and code != "rear_seat_folding")
    )
    if invalid:
        raise ContractError("inactive, missing or incompatible Spring attributes: " + ", ".join(invalid))

    active_statuses = {
        row["code"]
        for row in read_rows(MASTER / "enums" / "equipment_availability_statuses.csv")
        if row.get("status") == "active"
    }
    if not STATUSES <= active_statuses:
        raise ContractError("required Spring availability statuses are not active")

    documented_versions = {
        (row["source_code"], row["version_code"])
        for row in read_rows(MASTER / "source_versions.csv")
    }
    missing_versions = sorted(
        version
        for version in CONFIGURATION_VERSIONS.values()
        if (SOURCE_CODE, version) not in documented_versions
    )
    if missing_versions:
        raise ContractError("Spring brochure does not document versions: " + ", ".join(missing_versions))

    result: list[dict[str, str]] = []
    for row in spec:
        note = (
            f"Source page {row['source_page']}: {row['source_label']}. "
            "Direct grade-column matrix cell expanded only to the exact current configuration of that grade."
        )
        qualifier = row["normalization_notes"].strip()
        if qualifier:
            note += f" {qualifier}"
        result.append({
            "code": f"{row['configuration_code']}_{row['attribute_code']}_20260219",
            "configuration_code": row["configuration_code"],
            "attribute_code": row["attribute_code"],
            "availability_status": row["availability_status"],
            "observation_date": DATE,
            "source_code": SOURCE_CODE,
            "notes": note,
        })

    if len(result) != EXPECTED_ROWS:
        raise ContractError("generated Spring availability row count drifted")
    if dict(Counter(row["availability_status"] for row in result)) != EXPECTED_STATUS_COUNTS:
        raise ContractError("generated Spring status distribution drifted")
    return result


def generated_source_configuration_rows() -> list[dict[str, str]]:
    spring_configurations()
    documented_versions = {
        (row["source_code"], row["version_code"])
        for row in read_rows(MASTER / "source_versions.csv")
    }
    missing_versions = sorted(
        version
        for version in CONFIGURATION_VERSIONS.values()
        if (SOURCE_CODE, version) not in documented_versions
    )
    if missing_versions:
        raise ContractError(
            "Spring brochure does not document versions: " + ", ".join(missing_versions)
        )
    return [
        {
            "source_code": SOURCE_CODE,
            "configuration_code": configuration,
            "relationship": "documents",
            "notes": (
                "Official brochure pages 19-20 document the equipment matrix for "
                f"version {version}; observations are expanded only to this exact "
                "current configuration of the documented grade."
            ),
        }
        for configuration, version in CONFIGURATION_VERSIONS.items()
    ]


def stored_source_configuration_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(SOURCE_CONFIGURATION_OUTPUT, SOURCE_CONFIGURATION_FIELDS)
    current = read_rows(SOURCE_CONFIGURATION_OUTPUT)
    selected = [
        row for row in current
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code") in CONFIGURATION_VERSIONS
    ]
    return current, selected


def stored_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(OUTPUT, OUTPUT_FIELDS)
    current = read_rows(OUTPUT)
    selected = [
        row for row in current
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code") in CONFIGURATION_VERSIONS
    ]
    return current, selected


def check() -> None:
    _, actual = stored_rows()
    expected = generated_rows()
    if len(actual) != EXPECTED_ROWS or semantic_payload(actual) != semantic_payload(expected):
        raise ContractError("stored Spring rows differ from the generated direct-matrix contract")
    try:
        ids = [int(row["id"]) for row in actual]
    except (KeyError, ValueError) as exc:
        raise ContractError("Spring availability IDs must be integers") from exc
    if ids != list(range(EXPECTED_FIRST_ID, EXPECTED_LAST_ID + 1)):
        raise ContractError(
            f"Spring availability IDs must be the contiguous suffix "
            f"{EXPECTED_FIRST_ID}-{EXPECTED_LAST_ID}"
        )

    _, actual_links = stored_source_configuration_rows()
    expected_links = generated_source_configuration_rows()
    if semantic_payload(
        actual_links, SOURCE_CONFIGURATION_FIELDS[1:]
    ) != semantic_payload(expected_links, SOURCE_CONFIGURATION_FIELDS[1:]):
        raise ContractError("stored Spring source/configuration links differ from contract")
    try:
        link_ids = [int(row["id"]) for row in actual_links]
    except (KeyError, ValueError) as exc:
        raise ContractError("Spring source/configuration IDs must be integers") from exc
    if link_ids != list(
        range(
            EXPECTED_SOURCE_CONFIGURATION_FIRST_ID,
            EXPECTED_SOURCE_CONFIGURATION_LAST_ID + 1,
        )
    ):
        raise ContractError(
            "Spring source/configuration IDs must be the contiguous suffix "
            f"{EXPECTED_SOURCE_CONFIGURATION_FIRST_ID}-"
            f"{EXPECTED_SOURCE_CONFIGURATION_LAST_ID}"
        )
    print(
        "Spring equipment availability: PASS "
        "(42 attributes, 126 direct matrix rows, 3 source links)"
    )


def _write_csv(
    path: Path, fields: Sequence[str], rows: list[dict[str, str]]
) -> Path:
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
    current, actual = stored_rows()
    expected = generated_rows()
    if actual:
        if len(actual) != EXPECTED_ROWS or semantic_payload(actual) != semantic_payload(expected):
            raise ContractError("partial or conflicting Spring availability rows already exist")
        availability_output = current
    else:
        try:
            maximum_id = max(int(row["id"]) for row in current)
        except (KeyError, ValueError) as exc:
            raise ContractError("availability IDs must be integers") from exc
        if maximum_id != EXPECTED_FIRST_ID - 1:
            raise ContractError(
                f"expected Spring availability suffix after {EXPECTED_FIRST_ID - 1}, "
                f"found {maximum_id}"
            )
        availability_output = current + [
            {"id": str(maximum_id + offset), **row}
            for offset, row in enumerate(expected, start=1)
        ]

    link_current, actual_links = stored_source_configuration_rows()
    expected_links = generated_source_configuration_rows()
    if actual_links:
        if semantic_payload(
            actual_links, SOURCE_CONFIGURATION_FIELDS[1:]
        ) != semantic_payload(expected_links, SOURCE_CONFIGURATION_FIELDS[1:]):
            raise ContractError("partial or conflicting Spring source links already exist")
        link_output = link_current
    else:
        try:
            maximum_link_id = max(int(row["id"]) for row in link_current)
        except (KeyError, ValueError) as exc:
            raise ContractError("source/configuration IDs must be integers") from exc
        if maximum_link_id != EXPECTED_SOURCE_CONFIGURATION_FIRST_ID - 1:
            raise ContractError(
                "expected Spring source/configuration suffix after "
                f"{EXPECTED_SOURCE_CONFIGURATION_FIRST_ID - 1}, "
                f"found {maximum_link_id}"
            )
        link_output = link_current + [
            {"id": str(maximum_link_id + offset), **row}
            for offset, row in enumerate(expected_links, start=1)
        ]

    temporaries: list[tuple[Path, Path]] = []
    try:
        temporaries.append((OUTPUT, _write_csv(OUTPUT, OUTPUT_FIELDS, availability_output)))
        temporaries.append(
            (
                SOURCE_CONFIGURATION_OUTPUT,
                _write_csv(
                    SOURCE_CONFIGURATION_OUTPUT,
                    SOURCE_CONFIGURATION_FIELDS,
                    link_output,
                ),
            )
        )
        for path, temporary in temporaries:
            temporary.replace(path)
    finally:
        for _, temporary in temporaries:
            temporary.unlink(missing_ok=True)
    print("Imported 126 direct Spring availability rows and 3 source links.")


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
