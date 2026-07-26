#!/usr/bin/env python3
"""Import exact intrinsic engine values for Duster Eco-G 120 automatic."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SNAPSHOT = ROOT / "project" / "sources" / "dacia-pl-duster-ecog120-automatic-engine-20260724.json"
SOURCE_CODE = "src_pl_duster_ecog120_automatic_engine_20260724"
DATE = "2026-07-24"
SNAPSHOT_SHA256 = "9914402753c100f9a9ecb65c01bf454d90d6f18d6e09df00b74342377cba9ebc"
CONFIGURATION_CODES = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
TARGETS = {
    "sources.csv": (
        "id", "code", "source_type", "title", "publisher", "market",
        "document_date", "external_reference", "file_path", "sha256", "status", "notes",
    ),
    "source_models.csv": ("id", "source_code", "model_code", "relationship", "notes"),
    "source_versions.csv": ("id", "source_code", "version_code", "relationship", "notes"),
    "source_configurations.csv": ("id", "source_code", "configuration_code", "relationship", "notes"),
    "configuration_attribute_values.csv": (
        "id", "code", "configuration_code", "attribute_code", "fuel_type_code", "gear_number", "value",
        "observation_date", "source_code", "notes",
    ),
}


class ContractError(RuntimeError):
    """Raised when the normalized technical source cannot be reproduced."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ContractError(f"missing CSV header: {path}")
        return list(reader)


def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    if header != list(fields):
        raise ContractError(f"unexpected header in {path}: {header!r}")


def write_rows(path: Path, fields: Sequence[str], rows: Iterable[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_snapshot() -> dict:
    if file_sha256(SNAPSHOT) != SNAPSHOT_SHA256:
        raise ContractError("normalized snapshot SHA-256 mismatch")
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if payload.get("source_code") != SOURCE_CODE or payload.get("observed_on") != DATE:
        raise ContractError("snapshot identity mismatch")
    return payload


def normalized_contract() -> dict[str, list[dict[str, str]]]:
    payload = load_snapshot()
    configurations = {
        row["code"]: row
        for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    attributes = {
        row["code"]: row
        for row in read_rows(MASTER / "attributes.csv")
        if row.get("status") == "active"
    }
    units = {
        row["symbol"]
        for row in read_rows(MASTER / "units.csv")
    }
    scope_codes = set(payload.get("scope", {}).get("configuration_codes", []))
    if scope_codes != CONFIGURATION_CODES:
        raise ContractError("configuration coverage mismatch")
    for code in sorted(CONFIGURATION_CODES):
        configuration = configurations.get(code)
        if not configuration:
            raise ContractError(f"active configuration missing: {code}")
        if configuration.get("powertrain_label") != "Eco-G 120 4x2":
            raise ContractError(f"powertrain mismatch: {code}")
        if configuration.get("transmission_type") != "automatic":
            raise ContractError(f"transmission mismatch: {code}")

    intrinsic = payload.get("intrinsic_engine_values", [])
    expected = {
        ("engine_displacement", "", "1199", "cm3"),
        ("cylinder_count", "", "3", ""),
        ("total_valve_count", "", "12", ""),
    }
    actual = {
        (
            item.get("attribute_code", ""),
            item.get("fuel_type_code", ""),
            str(item.get("value", "")),
            item.get("unit", ""),
        )
        for item in intrinsic
    }
    if actual != expected:
        raise ContractError("intrinsic engine-value contract mismatch")
    for attribute_code, _, _, unit in sorted(expected):
        attribute = attributes.get(attribute_code)
        if not attribute or attribute.get("unit") != unit:
            raise ContractError(f"attribute unit mismatch: {attribute_code}")
        if unit and unit not in units:
            raise ContractError(f"inactive unit: {unit}")

    value_rows: list[dict[str, str]] = []
    for configuration_code in sorted(CONFIGURATION_CODES):
        for attribute_code, fuel_type_code, value, _ in sorted(expected):
            value_rows.append({
                "code": f"{configuration_code}_{attribute_code}_official_web_20260724",
                "configuration_code": configuration_code,
                "attribute_code": attribute_code,
                "fuel_type_code": fuel_type_code,
                "gear_number": "",
                "value": value,
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": (
                    "Official Dacia Eco-G 120 engine payload; intrinsic engine architecture "
                    "expanded only to exact automatic configurations independently proven by "
                    "official Dacia stock cards. Homologation-dependent values are excluded."
                ),
            })
    if len(value_rows) != 9:
        raise ContractError("expected nine intrinsic engine observations")

    version_codes = sorted({configurations[code]["version_code"] for code in CONFIGURATION_CODES})
    source_row = {
        "code": SOURCE_CODE,
        "source_type": "web_snapshot",
        "title": "Dacia Polska Duster Eco-G 120 automatic intrinsic engine data",
        "publisher": "Dacia",
        "market": "PL",
        "document_date": DATE,
        "external_reference": "https://www.dacia.pl/hybrydy-i-elektryczne/duster-suv/silniki.html",
        "file_path": SNAPSHOT.relative_to(ROOT).as_posix(),
        "sha256": SNAPSHOT_SHA256,
        "status": "active",
        "notes": (
            "Official dynamic engine and technical-page snapshot. Only 1199 cm3, three "
            "cylinders and 12 valves are imported; manual towing, cargo, WLTP and performance "
            "values remain explicit non-imports for automatic configurations."
        ),
    }
    return {
        "sources.csv": [source_row],
        "source_models.csv": [{
            "source_code": SOURCE_CODE,
            "model_code": "duster_iii",
            "relationship": "intrinsic_engine_data_for",
            "notes": "Official Dacia Eco-G 120 engine architecture observed 2026-07-24.",
        }],
        "source_versions.csv": [
            {
                "source_code": SOURCE_CODE,
                "version_code": version_code,
                "relationship": "intrinsic_engine_data_for",
                "notes": "Applied only to the exact registered Eco-G 120 automatic configuration.",
            }
            for version_code in version_codes
        ],
        "source_configurations.csv": [
            {
                "source_code": SOURCE_CODE,
                "configuration_code": code,
                "relationship": "intrinsic_engine_data_for",
                "notes": "Exact automatic configuration independently proven by official stock card.",
            }
            for code in sorted(CONFIGURATION_CODES)
        ],
        "configuration_attribute_values.csv": value_rows,
    }


def owned(rows: list[dict[str, str]], name: str) -> list[dict[str, str]]:
    if name == "sources.csv":
        return [row for row in rows if row.get("code") == SOURCE_CODE]
    return [row for row in rows if row.get("source_code") == SOURCE_CODE]


def semantic(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    payload_fields = [field for field in fields if field != "id"]
    return sorted(tuple(row.get(field, "") for field in payload_fields) for row in rows)


def check() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        if semantic(owned(read_rows(path), name), fields) != semantic(contract[name], fields):
            raise ContractError(f"master data differs from normalized contract: {name}")


def apply() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        rows = read_rows(path)
        current_owned = owned(rows, name)
        retained = [row for row in rows if row not in current_owned]
        next_id = max((int(row["id"]) for row in retained), default=0) + 1
        generated = [{"id": str(next_id + index), **row} for index, row in enumerate(contract[name])]
        write_rows(path, fields, [*retained, *generated])
    check()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        apply() if args.apply else check()
    except (ContractError, OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Duster Eco-G 120 automatic intrinsic-engine contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
