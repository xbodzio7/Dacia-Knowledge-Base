from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _eligible(value: str, as_of: str) -> bool:
    if not value:
        return True
    return date.fromisoformat(value) <= date.fromisoformat(as_of)


def collect_commercial_components(
    repository: Path,
    configuration_codes: Iterable[str],
    as_of: str,
) -> dict[str, list[dict[str, Any]]]:
    master = repository / "data" / "master"
    required = (
        master / "commercial_items.csv",
        master / "commercial_item_attributes.csv",
        master / "commercial_item_configurations.csv",
    )
    if not all(path.is_file() for path in required):
        return {}
    items = {
        row["code"]: row
        for row in read_csv(master / "commercial_items.csv")
        if row.get("status") == "active"
        and _eligible(row.get("observation_date", ""), as_of)
    }
    attributes: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(master / "commercial_item_attributes.csv"):
        if row.get("commercial_item_code") in items:
            attributes[row["commercial_item_code"]].append(row)
    requested = set(configuration_codes)
    latest: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv(master / "commercial_item_configurations.csv"):
        configuration_code = row.get("configuration_code", "")
        item_code = row.get("commercial_item_code", "")
        if configuration_code not in requested or item_code not in items:
            continue
        if not _eligible(row.get("price_date", ""), as_of):
            continue
        key = (configuration_code, item_code)
        previous = latest.get(key)
        if previous is None or row.get("price_date", "") > previous.get("price_date", ""):
            latest[key] = row

    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (configuration_code, item_code), mapping in sorted(latest.items()):
        item = items[item_code]
        member_rows = sorted(attributes.get(item_code, []), key=lambda row: row["attribute_code"])
        amount_text = mapping.get("amount", "")
        result[configuration_code].append(
            {
                "code": item_code,
                "name": item.get("name", item_code),
                "kind": item.get("item_type", "option"),
                "availability_status": mapping.get("availability_status", ""),
                "amount": float(amount_text) if amount_text else None,
                "currency_code": mapping.get("currency_code", "PLN"),
                "price_date": mapping.get("price_date", ""),
                "source_code": mapping.get("source_code", ""),
                "equipment_codes": [row["attribute_code"] for row in member_rows],
                "equipment_source_texts": {
                    row["attribute_code"]: row.get("source_text", "")
                    for row in member_rows
                },
            }
        )
    return dict(result)


def commercial_offer_rows(
    repository: Path,
    configuration_codes: Iterable[str],
    as_of: str,
) -> list[dict[str, Any]]:
    components = collect_commercial_components(repository, configuration_codes, as_of)
    rows: list[dict[str, Any]] = []
    for configuration_code in sorted(components):
        for item in components[configuration_code]:
            rows.append({"configuration_code": configuration_code, **item})
    return rows
