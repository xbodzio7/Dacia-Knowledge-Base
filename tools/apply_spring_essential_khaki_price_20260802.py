#!/usr/bin/env python3
"""Apply the exact-current Spring Essential Lichen Khaki price."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "data/reporting/spring_exact_current_semantic_migration_review.json"
SOURCE_SNAPSHOT_PATH = ROOT / "project/sources/dacia-pl-spring-commercial-context-20260802.json"
SOURCES_PATH = ROOT / "data/master/sources.csv"
MAPPINGS_PATH = ROOT / "data/master/commercial_item_configurations.csv"
REPORT_JSON_PATH = ROOT / "data/reporting/spring_essential_khaki_price_apply.json"
REPORT_MD_PATH = ROOT / "data/reporting/spring_essential_khaki_price_apply.md"

SOURCE_CODE = "src_pl_spring_commercial_context_20260802"
MAPPING_CODE = "spring_colour_lichen_khaki__spring_essential_electric70_automatic"
EXPECTED_OLD_SOURCE = "src_pl_spring_brochure_20260219"
PRICE_DATE = "2026-08-02"
PRICE_PLN = 2300


def read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def read_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def render_table(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def source_row(snapshot: Mapping[str, Any], source_id: int, sha256: str) -> dict[str, str]:
    essential_url = snapshot["official_sources"][0]["source_url"]
    return {
        "id": str(source_id),
        "code": SOURCE_CODE,
        "source_type": "normalized_snapshot",
        "title": "Dacia Polska Spring commercial context review",
        "publisher": "Dacia",
        "market": "PL",
        "document_date": PRICE_DATE,
        "external_reference": essential_url,
        "file_path": "project/sources/dacia-pl-spring-commercial-context-20260802.json",
        "sha256": sha256,
        "status": "active",
        "notes": (
            "Bounded normalized review of exact-current Spring commercial context. "
            "Only the Essential Lichen Khaki 2300 PLN option price is imported; "
            "Type 2, standard-paint, Expression, Extreme-palette and home-cable "
            "semantic cases remain excluded."
        ),
    }


def validate_review(review: Mapping[str, Any]) -> None:
    safe = review.get("safe_in_place_updates")
    if not isinstance(safe, list) or len(safe) != 1:
        raise RuntimeError("expected exactly one safe Spring update")
    candidate = safe[0]
    if candidate.get("mapping_code") != MAPPING_CODE:
        raise RuntimeError("safe mapping code drifted")
    if candidate.get("approved_state") != {
        "availability_status": "optional",
        "amount_pln": PRICE_PLN,
        "price_date": PRICE_DATE,
        "source_code": SOURCE_CODE,
    }:
        raise RuntimeError("approved Essential Khaki state drifted")
    if review.get("classification_summary") != {
        "safe_in_place_update": 1,
        "verified_current_no_change": 2,
        "semantic_migration_required": 3,
        "unresolved_no_change": 19,
        "new_representation_required": 2,
    }:
        raise RuntimeError("Spring review classification drifted")


def build_expected(
    review: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    source_fields: list[str],
    source_rows: list[dict[str, str]],
    mapping_fields: list[str],
    mapping_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
    validate_review(review)
    if snapshot.get("source_code") != SOURCE_CODE or snapshot.get("status") != "complete":
        raise RuntimeError("Spring commercial-context source snapshot drifted")

    source_index = {row["code"]: row for row in source_rows}
    snapshot_sha256 = hashlib.sha256(SOURCE_SNAPSHOT_PATH.read_bytes()).hexdigest()
    expected_source = source_row(
        snapshot,
        max(int(row["id"]) for row in source_rows) + (0 if SOURCE_CODE in source_index else 1),
        snapshot_sha256,
    )
    if set(expected_source) != set(source_fields):
        raise RuntimeError("source schema drifted")

    next_sources = [dict(row) for row in source_rows]
    source_added = 0
    if SOURCE_CODE in source_index:
        existing = source_index[SOURCE_CODE]
        expected_source["id"] = existing["id"]
        if existing != expected_source:
            raise RuntimeError("registered Spring context source differs from expected state")
    else:
        next_sources.append(expected_source)
        source_added = 1

    next_mappings = [dict(row) for row in mapping_rows]
    target_rows = [row for row in next_mappings if row["code"] == MAPPING_CODE]
    if len(target_rows) != 1:
        raise RuntimeError("expected one Essential Khaki mapping")
    target = target_rows[0]
    before = dict(target)
    approved = (
        target["availability_status"] == "optional"
        and target["amount"] == str(PRICE_PLN)
        and target["currency_code"] == "PLN"
        and target["price_date"] == PRICE_DATE
        and target["source_code"] == SOURCE_CODE
    )
    if not approved:
        if target["availability_status"] != "optional":
            raise RuntimeError("Essential Khaki option semantics drifted")
        if target["amount"]:
            raise RuntimeError("Essential Khaki already has an unexpected amount")
        if target["source_code"] != EXPECTED_OLD_SOURCE:
            raise RuntimeError("Essential Khaki prior provenance drifted")
        target["amount"] = str(PRICE_PLN)
        target["currency_code"] = "PLN"
        target["price_date"] = PRICE_DATE
        target["source_code"] = SOURCE_CODE
        target["notes"] = (
            "Exact current Spring Essential electric 70 configurator state: "
            "Lichen Khaki is an optional paint priced at 2300 PLN. No transfer "
            "to Expression, Extreme or another paint mapping is authorized."
        )

    after = dict(target)
    report = {
        "version": 1,
        "generated_on": PRICE_DATE,
        "status": "complete",
        "scope": {
            "mapping_code": MAPPING_CODE,
            "configuration_code": "spring_essential_electric70_automatic",
            "commercial_item_code": "spring_colour_lichen_khaki",
            "source_code": SOURCE_CODE,
        },
        "source_registration": {
            "rows_added": source_added,
            "registered_source_count": 1,
            "source_sha256": snapshot_sha256,
            "file_path": "project/sources/dacia-pl-spring-commercial-context-20260802.json",
        },
        "mapping_update": {
            "rows_changed": 0 if before == after else 1,
            "before": {
                "availability_status": before["availability_status"],
                "amount": before["amount"] or None,
                "currency_code": before["currency_code"],
                "price_date": before["price_date"] or None,
                "source_code": before["source_code"],
            },
            "after": {
                "availability_status": after["availability_status"],
                "amount": int(after["amount"]),
                "currency_code": after["currency_code"],
                "price_date": after["price_date"],
                "source_code": after["source_code"],
            },
        },
        "preserved_boundaries": {
            "semantic_migrations_unchanged": 3,
            "unresolved_mappings_unchanged": 19,
            "new_representation_cases_unchanged": 2,
            "other_mapping_rows_changed": 0,
        },
        "master_data_delta": {
            "source_rows_added": source_added,
            "commercial_mapping_rows_added": 0,
            "commercial_mapping_rows_updated": 0 if before == after else 1,
            "commercial_items_added": 0,
            "attributes_added": 0,
        },
        "next_package": {
            "package_id": "spring_standard_equipment_representation_review_001",
            "goal": (
                "Review existing repository representation patterns for exact-current "
                "standard equipment and default paint before proposing any Spring Type 2, "
                "Biel Alpejska or home-charging-cable model change."
            ),
        },
    }
    if set(target) != set(mapping_fields):
        raise RuntimeError("commercial mapping schema drifted")
    return next_sources, next_mappings, report


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    after = report["mapping_update"]["after"]
    return f"""# Spring Essential Lichen Khaki Price Apply

**Status:** complete  
**Date:** {report['generated_on']}

## Applied change

- Mapping: `{report['scope']['mapping_code']}`
- Availability: `{after['availability_status']}`
- Price: **{after['amount']} {after['currency_code']}**
- Price date: `{after['price_date']}`
- Provenance: `{after['source_code']}`

## Source registration

The bounded normalized source `project/sources/dacia-pl-spring-commercial-context-20260802.json` is registered with its SHA-256 digest. It combines exact-current official grade evidence while preserving explicit transfer boundaries.

## Preserved boundaries

- 3 semantic migrations remain unchanged;
- 19 unresolved mappings remain unchanged;
- 2 new-representation cases remain unchanged;
- no other commercial mapping is changed;
- no commercial item or attribute is added.

## Next package

`{report['next_package']['package_id']}` will review existing standard/default representation patterns before any further Spring model mutation.
"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def build(root: Path = ROOT) -> tuple[str, str, dict[str, Any]]:
    review = read_object(root / REVIEW_PATH.relative_to(ROOT))
    snapshot = read_object(root / SOURCE_SNAPSHOT_PATH.relative_to(ROOT))
    source_fields, source_rows = read_table(root / SOURCES_PATH.relative_to(ROOT))
    mapping_fields, mapping_rows = read_table(root / MAPPINGS_PATH.relative_to(ROOT))
    next_sources, next_mappings, report = build_expected(
        review,
        snapshot,
        source_fields,
        source_rows,
        mapping_fields,
        mapping_rows,
    )
    return (
        render_table(source_fields, next_sources),
        render_table(mapping_fields, next_mappings),
        report,
    )


def apply(root: Path = ROOT) -> None:
    sources_content, mappings_content, report = build(root)
    write_atomic(root / SOURCES_PATH.relative_to(ROOT), sources_content)
    write_atomic(root / MAPPINGS_PATH.relative_to(ROOT), mappings_content)
    write_atomic(root / REPORT_JSON_PATH.relative_to(ROOT), render_json(report))
    write_atomic(root / REPORT_MD_PATH.relative_to(ROOT), render_markdown(report))


def verify(root: Path = ROOT) -> None:
    sources_content, mappings_content, report = build(root)
    if (root / SOURCES_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != sources_content:
        raise RuntimeError("sources.csv is not in the approved Spring Khaki state")
    if (root / MAPPINGS_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != mappings_content:
        raise RuntimeError("commercial_item_configurations.csv is not in the approved Spring Khaki state")
    if read_object(root / REPORT_JSON_PATH.relative_to(ROOT)) != report:
        raise RuntimeError("Spring Khaki apply JSON is stale")
    if (root / REPORT_MD_PATH.relative_to(ROOT)).read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("Spring Khaki apply Markdown is stale")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    if arguments.apply:
        apply()
    else:
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
