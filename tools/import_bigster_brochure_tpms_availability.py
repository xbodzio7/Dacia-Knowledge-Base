#!/usr/bin/env python3
"""Import the visually verified TPMS row from the 2025-12-10 Bigster brochure."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SOURCE_SHA256 = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
DATE = "2025-12-10"
SPEC = ROOT / "data" / "imports" / "bigster_brochure_equipment_availability_20251210.csv"
OUTPUT = MASTER / "configuration_attribute_availability.csv"
FIELDS = ("id", "code", "configuration_code", "attribute_code", "availability_status", "observation_date", "source_code", "notes")
SPEC_FIELDS = ("configuration_code", "attribute_code", "availability_status", "source_page", "source_label", "normalization_notes")
EXPECTED_CONFIGS = {
    "bigster_essential_mildhybridg140_4x2_manual",
    "bigster_expression_mildhybridg140_4x2_manual",
    "bigster_extreme_mildhybridg140_4x2_manual",
    "bigster_journey_mildhybridg140_4x2_manual",
    "bigster_essential_mildhybrid140_4x2_manual",
    "bigster_expression_mildhybrid140_4x2_manual",
    "bigster_extreme_mildhybrid140_4x2_manual",
    "bigster_journey_mildhybrid140_4x2_manual",
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}


class ContractError(RuntimeError):
    """Raised when source or master data does not satisfy the import contract."""


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                raise ContractError(f"missing CSV header: {path}")
            return list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def require_header(path: Path, expected: tuple[str, ...]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream), None)
    if header != list(expected):
        raise ContractError(f"unexpected CSV header in {path}: {header!r}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generated_rows() -> list[dict[str, str]]:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError("Bigster brochure source SHA-256 mismatch")
    require_header(SPEC, SPEC_FIELDS)
    spec = [row for row in read_csv(SPEC) if row["attribute_code"] == "tyre_pressure_monitoring_system"]
    if len(spec) != len(EXPECTED_CONFIGS):
        raise ContractError(f"expected {len(EXPECTED_CONFIGS)} matrix cells, found {len(spec)}")
    if {row["configuration_code"] for row in spec} != EXPECTED_CONFIGS:
        raise ContractError("spec configuration set differs from the visually verified brochure scope")
    if any(row["attribute_code"] != "tyre_pressure_monitoring_system" or row["availability_status"] != "standard" or row["source_page"] != "21" or not row["source_label"].strip() for row in spec):
        raise ContractError("spec contains a cell outside the verified TPMS standard row")
    if len({row["configuration_code"] for row in spec}) != len(spec):
        raise ContractError("duplicate Bigster TPMS configuration cell")

    configurations = {row["code"]: row for row in read_csv(MASTER / "configurations.csv")}
    if any(code not in configurations or configurations[code].get("status") != "active" for code in EXPECTED_CONFIGS):
        raise ContractError("one or more exact Bigster configurations are missing or inactive")
    attributes = {row["code"]: row for row in read_csv(MASTER / "attributes.csv")}
    attribute = attributes.get("tyre_pressure_monitoring_system")
    if not attribute or attribute.get("status") != "active" or attribute.get("data_type") != "boolean":
        raise ContractError("TPMS attribute is missing, inactive or not boolean")
    links = {(row["source_code"], row["configuration_code"]) for row in read_csv(MASTER / "source_configurations.csv")}
    if any((SOURCE_CODE, code) not in links for code in EXPECTED_CONFIGS):
        raise ContractError("one or more exact source-to-configuration links are missing")

    result = []
    for row in spec:
        code = row["configuration_code"]
        note = f"Official Bigster brochure, printed page 21: {row['source_label']}; standard marker in the exact {configurations[code]['version_code']} grade column."
        qualifier = row["normalization_notes"].strip()
        if qualifier:
            note += " " + qualifier
        result.append({
            "code": f"{code}_tyre_pressure_monitoring_system_20251210",
            "configuration_code": code,
            "attribute_code": "tyre_pressure_monitoring_system",
            "availability_status": "standard",
            "observation_date": DATE,
            "source_code": SOURCE_CODE,
            "notes": note,
        })
    return result


def semantic(rows: list[dict[str, str]]) -> list[tuple[str, ...]]:
    fields = FIELDS[1:]
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    current = read_csv(OUTPUT)
    expected = generated_rows()
    actual = [row for row in current if row.get("source_code") == SOURCE_CODE and row.get("attribute_code") == "tyre_pressure_monitoring_system" and row.get("observation_date") == DATE]
    if args.check:
        if len(actual) != len(expected) or semantic(actual) != semantic(expected):
            raise ContractError("stored Bigster TPMS observations differ from the dated brochure matrix contract")
        print("Bigster brochure TPMS availability: PASS (14 direct matrix observations)")
        return 0
    if actual:
        if len(actual) != len(expected) or semantic(actual) != semantic(expected):
            raise ContractError("partial or conflicting Bigster TPMS observations already exist")
        print("Bigster brochure TPMS observations already match the contract.")
        return 0
    ids = [int(row["id"]) for row in current]
    maximum = max(ids, default=0)
    additions = []
    for offset, row in enumerate(expected, start=1):
        additions.append({"id": str(maximum + offset), **row})
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(current + additions)
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Imported {len(additions)} direct Bigster brochure TPMS observations.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, OSError, ValueError, KeyError) as exc:
        raise SystemExit(f"Bigster brochure TPMS import failed: {exc}")
