#!/usr/bin/env python3
"""Import exact Duster Eco-G 120 automatic stock-card observations."""
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
SNAPSHOT = ROOT / "project" / "sources" / "dacia-pl-duster-ecog120-automatic-stock-20260724.json"
SOURCE_CODE = "src_pl_duster_ecog120_automatic_stock_20260724"
DATE = "2026-07-24"
SNAPSHOT_SHA256 = "a25c2244699b463343879fb1d1fa995793666d3e5619da2021acd81404688e98"

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
    "configurations.csv": (
        "id", "code", "version_code", "powertrain_label", "transmission_type", "status", "notes",
    ),
    "configuration_prices.csv": (
        "id", "code", "configuration_code", "market", "price_type", "amount",
        "currency_code", "price_date", "source_code", "notes",
    ),
    "configuration_attribute_availability.csv": (
        "id", "code", "configuration_code", "attribute_code", "availability_status",
        "observation_date", "source_code", "notes",
    ),
}


class ContractError(RuntimeError):
    """Raised when the normalized source contract cannot be reproduced."""


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
    model = next(
        (row for row in read_rows(MASTER / "models.csv") if row["code"] == "duster_iii"),
        None,
    )
    if not model or model.get("status") != "current":
        raise ContractError("current Duster model missing")

    versions = {
        row["code"]: row
        for row in read_rows(MASTER / "versions.csv")
        if row.get("status") == "active"
    }
    attributes = {
        row["code"]: row
        for row in read_rows(MASTER / "attributes.csv")
        if row.get("status") == "active"
    }
    statuses = {
        row["code"]
        for row in read_rows(MASTER / "enums" / "equipment_availability_statuses.csv")
        if row.get("status") == "active"
    }

    observations = payload.get("configurations", [])
    if len(observations) != 3:
        raise ContractError("expected three exact stock-card observations")
    if {item["configuration_code"] for item in observations} != CONFIGURATION_CODES:
        raise ContractError("configuration coverage mismatch")

    configuration_rows: list[dict[str, str]] = []
    price_rows: list[dict[str, str]] = []
    availability_rows: list[dict[str, str]] = []
    source_version_rows: list[dict[str, str]] = []
    source_configuration_rows: list[dict[str, str]] = []
    seen_versions: set[str] = set()

    for item in observations:
        configuration_code = item["configuration_code"]
        version_code = item["version_code"]
        version = versions.get(version_code)
        if not version or version.get("model_code") != "duster_iii":
            raise ContractError(f"inactive or mismatched Duster version: {version_code}")
        if item.get("year") != "2026" or item.get("fuel") != "Benzyna/gaz":
            raise ContractError(f"stock-card identity mismatch: {configuration_code}")
        if item.get("transmission_source_label") != "AUTOMATYCZNA SKRZYNIA BIEGÓW":
            raise ContractError(f"automatic transmission not explicit: {configuration_code}")
        if int(item.get("power_kw", 0)) != 90 or int(item.get("power_hp", 0)) != 122:
            raise ContractError(f"power evidence mismatch: {configuration_code}")
        if not str(item.get("url", "")).startswith("https://kup.dacia.pl/"):
            raise ContractError(f"official stock URL missing: {configuration_code}")

        configuration_rows.append({
            "code": configuration_code,
            "version_code": version_code,
            "powertrain_label": "Eco-G 120 4x2",
            "transmission_type": "automatic",
            "status": "active",
            "notes": (
                f"Exact official Dacia Poland 2026 stock card {item['stock_id']} observed {DATE}; "
                "Eco-G 120, 90 kW/122 KM and automatic transmission explicitly stated."
            ),
        })
        price = int(item["catalog_gross_price"])
        if price <= 0 or "Cena katalogowa" not in item.get("price_source_label", ""):
            raise ContractError(f"catalogue price not explicit: {configuration_code}")
        price_rows.append({
            "code": f"{configuration_code}_pl_20260724",
            "configuration_code": configuration_code,
            "market": "PL",
            "price_type": "catalog_gross",
            "amount": str(price),
            "currency_code": "PLN",
            "price_date": DATE,
            "source_code": SOURCE_CODE,
            "notes": (
                f"Official Dacia Poland exact stock card {item['stock_id']}: "
                f"{item['price_source_label']}. Promotional and financing prices excluded."
            ),
        })

        if version_code not in seen_versions:
            seen_versions.add(version_code)
            source_version_rows.append({
                "source_code": SOURCE_CODE,
                "version_code": version_code,
                "relationship": "exact_stock_configuration_documents",
                "notes": f"Exact 2026 official Dacia stock card observed {DATE}.",
            })
        source_configuration_rows.append({
            "source_code": SOURCE_CODE,
            "configuration_code": configuration_code,
            "relationship": "exact_stock_configuration_documents",
            "notes": (
                f"Official stock card {item['stock_id']} explicitly identifies version, "
                "Eco-G 120 powertrain and automatic transmission."
            ),
        })

        for availability in item.get("availability", []):
            attribute_code = availability["attribute_code"]
            attribute = attributes.get(attribute_code)
            if attribute_code != "side_mirrors_folding" or not attribute:
                raise ContractError(f"unsupported availability attribute: {attribute_code}")
            if attribute.get("data_type") != "boolean":
                raise ContractError("folding-mirror attribute is not boolean")
            if availability.get("availability_status") != "standard":
                raise ContractError("only explicit standard mirror evidence is accepted")
            if availability["availability_status"] not in statuses:
                raise ContractError("availability status missing from canonical enum")
            availability_rows.append({
                "code": f"{configuration_code}_{attribute_code}_official_stock_20260724",
                "configuration_code": configuration_code,
                "attribute_code": attribute_code,
                "availability_status": "standard",
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": (
                    f"Official Dacia Poland exact stock card {item['stock_id']} basic/configured "
                    f"equipment: {availability['source_label']}."
                ),
            })

    if len(configuration_rows) != 3 or len(price_rows) != 3:
        raise ContractError("configuration or price row count mismatch")
    if len(availability_rows) != 2:
        raise ContractError("expected two explicit folding-mirror observations")
    if any(row["configuration_code"].endswith("expression_ecog120_4x2_automatic") for row in availability_rows):
        raise ContractError("Expression mirror state must remain unresolved")

    source_row = {
        "code": SOURCE_CODE,
        "source_type": "web_snapshot",
        "title": "Dacia Polska exact Duster Eco-G 120 automatic stock cards",
        "publisher": "Dacia",
        "market": "PL",
        "document_date": DATE,
        "external_reference": "https://kup.dacia.pl/",
        "file_path": SNAPSHOT.relative_to(ROOT).as_posix(),
        "sha256": SNAPSHOT_SHA256,
        "status": "active",
        "notes": (
            "Normalized snapshot of three exact official 2026 stock cards. Dynamic URLs may "
            "later expire or redirect; promotional prices, ambiguous Expression mirror state "
            "and unmentioned antenna states are explicit non-imports."
        ),
    }
    return {
        "sources.csv": [source_row],
        "source_models.csv": [{
            "source_code": SOURCE_CODE,
            "model_code": "duster_iii",
            "relationship": "exact_stock_configurations_for",
            "notes": "Three official 2026 Eco-G 120 automatic stock cards.",
        }],
        "source_versions.csv": sorted(source_version_rows, key=lambda row: row["version_code"]),
        "source_configurations.csv": sorted(
            source_configuration_rows, key=lambda row: row["configuration_code"]
        ),
        "configurations.csv": sorted(configuration_rows, key=lambda row: row["code"]),
        "configuration_prices.csv": sorted(price_rows, key=lambda row: row["code"]),
        "configuration_attribute_availability.csv": sorted(
            availability_rows, key=lambda row: row["code"]
        ),
    }


def owned(rows: list[dict[str, str]], name: str) -> list[dict[str, str]]:
    if name == "sources.csv":
        return [row for row in rows if row.get("code") == SOURCE_CODE]
    if name == "configurations.csv":
        return [row for row in rows if row.get("code") in CONFIGURATION_CODES]
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
    print("PASS: Duster Eco-G 120 automatic stock-card contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
