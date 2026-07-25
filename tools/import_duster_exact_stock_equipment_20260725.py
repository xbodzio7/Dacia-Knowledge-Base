#!/usr/bin/env python3
"""Import exact Duster Eco-G 120 automatic stock equipment and selected packages."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SNAPSHOT = ROOT / "project" / "sources" / "dacia-pl-duster-exact-stock-equipment-20260724.json"
SOURCE_CODE = "src_pl_duster_exact_stock_equipment_20260724"
PRICE_SOURCE = "src_pl_duster_price_my26_20260703"
DATE = "2026-07-24"
SNAPSHOT_SHA256 = "e4428bcee5f7f1fe6bb9ae6152852667f552f9abee0c09b7215bd4c8fc3f050a"
CONFIGURATION_COUNTS = {
    "duster_iii_expression_ecog120_4x2_automatic": 54,
    "duster_iii_extreme_ecog120_4x2_automatic": 75,
    "duster_iii_journey_ecog120_4x2_automatic": 74,
}
TARGETS = {
    "sources.csv": ("id", "code", "source_type", "title", "publisher", "market", "document_date", "external_reference", "file_path", "sha256", "status", "notes"),
    "source_models.csv": ("id", "source_code", "model_code", "relationship", "notes"),
    "source_versions.csv": ("id", "source_code", "version_code", "relationship", "notes"),
    "source_configurations.csv": ("id", "source_code", "configuration_code", "relationship", "notes"),
    "configuration_attribute_availability.csv": ("id", "code", "configuration_code", "attribute_code", "availability_status", "observation_date", "source_code", "notes"),
    "commercial_item_configurations.csv": ("id", "code", "commercial_item_code", "configuration_code", "availability_status", "amount", "currency_code", "price_date", "source_code", "notes"),
}

class ContractError(RuntimeError):
    pass

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
    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv") if row.get("status") == "active"}
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv") if row.get("status") == "active"}
    statuses = {row["code"] for row in read_rows(MASTER / "enums" / "equipment_availability_statuses.csv") if row.get("status") == "active"}
    items = {row["code"]: row for row in read_rows(MASTER / "commercial_items.csv") if row.get("status") == "active"}
    memberships: dict[str, set[str]] = {}
    for row in read_rows(MASTER / "commercial_item_attributes.csv"):
        memberships.setdefault(row["commercial_item_code"], set()).add(row["attribute_code"])
    source_codes = {row["code"] for row in read_rows(MASTER / "sources.csv") if row.get("status") == "active"}
    prior_exact_availability = {
        (row["configuration_code"], row["attribute_code"]): row
        for row in read_rows(MASTER / "configuration_attribute_availability.csv")
        if row.get("source_code") == "src_pl_duster_ecog120_automatic_stock_20260724"
    }
    if PRICE_SOURCE not in source_codes:
        raise ContractError("official Duster MY26 price-list source is not active")

    availability: list[dict[str, str]] = []
    commercial: list[dict[str, str]] = []
    source_versions: list[dict[str, str]] = []
    source_configurations: list[dict[str, str]] = []
    seen_versions: set[str] = set()
    counts: Counter[str] = Counter()
    statuses_count: Counter[str] = Counter()

    cards = payload.get("cards", [])
    if len(cards) != 3:
        raise ContractError("expected three exact stock cards")
    if {card["configuration_code"] for card in cards} != set(CONFIGURATION_COUNTS):
        raise ContractError("exact configuration coverage mismatch")

    for card in cards:
        config = card["configuration_code"]
        version = card["version_code"]
        row = configurations.get(config)
        if row is None or row.get("version_code") != version or row.get("transmission_type") != "automatic":
            raise ContractError(f"active exact automatic configuration missing: {config}")
        if version not in seen_versions:
            seen_versions.add(version)
            source_versions.append({"source_code": SOURCE_CODE, "version_code": version, "relationship": "exact_stock_equipment_documents", "notes": f"Official exact stock equipment card observed {DATE}."})
        source_configurations.append({"source_code": SOURCE_CODE, "configuration_code": config, "relationship": "exact_stock_equipment_documents", "notes": f"Official Dacia Poland exact stock card {card['stock_id']} provides equipment and selected-package evidence."})

        seen_attributes: set[str] = set()
        card_status: dict[str, str] = {}
        for equipment in card.get("equipment", []):
            attribute = equipment["attribute_code"]
            status = equipment["availability_status"]
            if attribute in seen_attributes:
                raise ContractError(f"duplicate exact-card attribute: {config}/{attribute}")
            seen_attributes.add(attribute)
            definition = attributes.get(attribute)
            if definition is None or (
                definition.get("data_type") != "boolean"
                and attribute not in {"rear_seat_folding"}
            ):
                raise ContractError(f"inactive or unsupported equipment attribute: {attribute}")
            if status not in statuses:
                raise ContractError(f"invalid availability status: {status}")
            card_status[attribute] = status
            if attribute == "side_mirrors_folding" and config in {
                "duster_iii_extreme_ecog120_4x2_automatic",
                "duster_iii_journey_ecog120_4x2_automatic",
            }:
                prior = prior_exact_availability.get((config, attribute))
                if not prior or prior.get("availability_status") != "standard" or prior.get("observation_date") != DATE:
                    raise ContractError(f"reused exact folding-mirror observation missing: {config}")
                continue
            counts[config] += 1
            statuses_count[status] += 1
            availability.append({
                "code": f"{config}_{attribute}_exact_stock_20260724",
                "configuration_code": config,
                "attribute_code": attribute,
                "availability_status": status,
                "observation_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": f"Official Dacia Poland exact stock card {card['stock_id']}, section {equipment['source_section']}: {equipment['source_label']}.",
            })

        for package in card.get("selected_packages", []):
            item = package["commercial_item_code"]
            if item not in items or not memberships.get(item):
                raise ContractError(f"active commercial package or membership missing: {item}")
            component_aliases = {"passenger_seat_adjustment": "passenger_seat_height_adjustment"}
            missing_components = sorted(
                attr for attr in memberships[item]
                if card_status.get(component_aliases.get(attr, attr)) != "standard"
            )
            if missing_components:
                raise ContractError(f"selected package components are not exact-card standard for {config}/{item}: {missing_components}")
            amount = str(package["catalogue_price"])
            commercial.append({
                "code": f"{item}__{config}__exact_stock_offer_20260703",
                "commercial_item_code": item,
                "configuration_code": config,
                "availability_status": "optional",
                "amount": amount,
                "currency_code": "PLN",
                "price_date": "2026-07-03",
                "source_code": PRICE_SOURCE,
                "notes": f"Official Duster MY26 price list supplies package name, composition and {amount} PLN gross price; exact stock card {card['stock_id']} independently proves applicability to this automatic configuration.",
            })
            commercial.append({
                "code": f"{item}__{config}__selected_exact_stock_20260724",
                "commercial_item_code": item,
                "configuration_code": config,
                "availability_status": "standard",
                "amount": "",
                "currency_code": "PLN",
                "price_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": f"Selected in exact stock vehicle {card['stock_id']}: {package['source_label']}. Empty amount preserves selection without claiming that the stock card restates the standalone package price.",
            })

    if dict(counts) != CONFIGURATION_COUNTS:
        raise ContractError(f"unexpected per-configuration equipment counts: {dict(counts)}")
    if len(availability) != 203 or dict(statuses_count) != {"standard": 199, "not_available": 4}:
        raise ContractError(f"unexpected exact equipment distribution: total={len(availability)}, statuses={dict(statuses_count)}")
    if len(commercial) != 8:
        raise ContractError("expected four optional offers and four exact-stock selections")
    if any(row["attribute_code"] == "shark_fin_antenna" for row in availability):
        raise ContractError("Duster antenna type must remain unimported")
    if any(row["configuration_code"].endswith("expression_ecog120_4x2_automatic") and row["attribute_code"] == "side_mirrors_folding" for row in availability):
        raise ContractError("Expression folding-mirror conflict must remain unimported")

    source_row = {
        "code": SOURCE_CODE,
        "source_type": "web_snapshot",
        "title": "Dacia Polska exact Duster Eco-G 120 automatic stock equipment cards",
        "publisher": "Dacia",
        "market": "PL",
        "document_date": DATE,
        "external_reference": "https://kup.dacia.pl/",
        "file_path": SNAPSHOT.relative_to(ROOT).as_posix(),
        "sha256": SNAPSHOT_SHA256,
        "status": "active",
        "notes": "Normalized snapshot of exact Expression, Extreme and Journey automatic stock equipment, selected packages, expired-card evidence and explicit non-import boundaries.",
    }
    return {
        "sources.csv": [source_row],
        "source_models.csv": [{"source_code": SOURCE_CODE, "model_code": "duster_iii", "relationship": "exact_stock_equipment_for", "notes": "Three official 2026 Eco-G 120 automatic exact-stock equipment cards."}],
        "source_versions.csv": sorted(source_versions, key=lambda row: row["version_code"]),
        "source_configurations.csv": sorted(source_configurations, key=lambda row: row["configuration_code"]),
        "configuration_attribute_availability.csv": sorted(availability, key=lambda row: row["code"]),
        "commercial_item_configurations.csv": sorted(commercial, key=lambda row: row["code"]),
    }

def owned(rows: list[dict[str, str]], name: str, generated: list[dict[str, str]]) -> list[dict[str, str]]:
    if name == "sources.csv":
        return [row for row in rows if row.get("code") == SOURCE_CODE]
    if name == "commercial_item_configurations.csv":
        codes = {row["code"] for row in generated}
        return [row for row in rows if row.get("code") in codes]
    return [row for row in rows if row.get("source_code") == SOURCE_CODE]

def semantic(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    payload_fields = [field for field in fields if field != "id"]
    return sorted(tuple(row.get(field, "") for field in payload_fields) for row in rows)

def check() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        current = read_rows(path)
        if semantic(owned(current, name, contract[name]), fields) != semantic(contract[name], fields):
            raise ContractError(f"master data differs from normalized contract: {name}")

def apply() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        rows = read_rows(path)
        current_owned = owned(rows, name, contract[name])
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
    print("PASS: Duster exact stock equipment contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
