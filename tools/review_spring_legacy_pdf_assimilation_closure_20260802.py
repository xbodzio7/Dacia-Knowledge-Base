#!/usr/bin/env python3
"""Close the fully reviewed Spring legacy-PDF assimilation milestone."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "data/reporting/spring_legacy_pdf_assimilation_closure.json"
REPORT_MD = ROOT / "data/reporting/spring_legacy_pdf_assimilation_closure.md"
SOURCES = ROOT / "data/master/sources.csv"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
RANGES = ROOT / "data/master/configuration_attribute_value_ranges.csv"
AVAILABILITY = ROOT / "data/master/configuration_attribute_availability.csv"
PRICES = ROOT / "data/master/configuration_prices.csv"
ANALYSIS = ROOT / "data/reporting/existing_configuration_missing_data_analysis.json"
REVIEW = ROOT / "data/reporting/spring_nonconflicting_technical_observations_review.json"
MIGRATION = ROOT / "data/reporting/spring_nonconflicting_common_technical_migration.json"
LEDGER = ROOT / "project/source-audit/spring-evidence-ledger-20260802.md"
INTAKE = ROOT / "project/source-audit/spring-full-assimilation-intake-20260802.md"
CONFLICTS = ROOT / "project/source-audit/spring-source-conflicts-20260802.md"

SOURCE_RECEIPTS = {
    "src_pl_spring_brochure_20260219": {
        "repository_path": "PDF/Broszury/DACIA SPRING broszura 20260219.pdf",
        "sha256": "73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d",
        "document_date": "2026-02-19",
        "pages": 22,
        "inventory": "project/source-audit/spring-brochure-20260219-page-inventory.md",
    },
    "src_pl_spring_price_my25_stock_20260708": {
        "repository_path": "PDF/Cenniki/DACIA SPRING cennik MY25 stock 20260708.pdf",
        "sha256": "809d24ec3710aac02b3f3a2f33e1872689430a1d6887f387936a5ac3ff343ae0",
        "document_date": "2026-07-08",
        "pages": 6,
        "inventory": "project/source-audit/spring-price-my25-stock-20260708-page-inventory.md",
    },
}

CONFIGURATIONS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}

APPROVED_ATTRIBUTES = {
    "electric_motor_type",
    "traction_battery_type",
    "steering_type",
    "overall_height",
    "front_track",
    "overall_width",
    "overall_width_with_mirrors",
    "rear_track",
    "front_overhang",
    "wheelbase",
    "rear_overhang",
    "overall_length",
}

AREA_OUTCOMES = {
    "Document identity": ("represented", ["data/master/sources.csv", "project/source-audit/spring-full-assimilation-intake-20260802.md"]),
    "Stock prices": ("represented_with_model_year_boundary", ["data/master/configuration_prices.csv"]),
    "Charging cables": ("explicit_temporal_conflict", ["project/source-audit/spring-source-conflicts-20260802.md", "data/reporting/spring_charging_cable_commercial_semantics_migration.json"]),
    "DC charging": ("represented_with_context", ["data/reporting/spring_charging_cable_representation_migration.json"]),
    "V2L": ("explicit_dated_range_conflict", ["project/source-audit/spring-source-conflicts-20260802.md"]),
    "Multimedia": ("represented", ["data/master/configuration_attribute_availability.csv"]),
    "Exterior colours": ("represented_and_bounded_current_delta", ["data/reporting/spring_biel_alpejska_default_colour_migration.json"]),
    "Grade trims": ("represented", ["data/master/configuration_attribute_availability.csv"]),
    "Safety/ADAS": ("represented", ["data/master/configuration_attribute_availability.csv"]),
    "Parking": ("represented", ["data/master/configuration_attribute_availability.csv"]),
    "Powertrain": ("represented_and_materialized", ["data/reporting/spring_nonconflicting_common_technical_migration.json"]),
    "Battery": ("partly_materialized_with_explicit_deferrals", ["data/reporting/spring_nonconflicting_technical_observations_review.json", "data/reporting/spring_nonconflicting_common_technical_migration.json"]),
    "Charging times": ("explicit_contextual_deferral", ["data/reporting/spring_nonconflicting_common_technical_migration.json"]),
    "Range/energy": ("represented_or_explicitly_deferred", ["data/reporting/spring_nonconflicting_technical_observations_review.json"]),
    "Performance": ("represented", ["data/master/configuration_attribute_values.csv"]),
    "Passenger dimensions": ("materialized_with_wheel_qualified_deferral", ["data/reporting/spring_nonconflicting_common_technical_migration.json"]),
    "Passenger luggage": ("represented_with_measurement_context", ["data/master/configuration_attribute_values.csv"]),
    "Interior storage": ("explicit_accessory_context_deferral", ["project/source-audit/spring-evidence-ledger-20260802.md"]),
    "Cargo derivative": ("explicit_separate_configuration_deferral", ["project/source-audit/spring-evidence-ledger-20260802.md"]),
    "Accessories/YouClip": ("explicit_accessory_domain_deferral", ["project/source-audit/spring-evidence-ledger-20260802.md"]),
    "Marketing/design": ("out_of_scope", ["project/source-audit/spring-evidence-ledger-20260802.md"]),
    "Legal disclaimers": ("represented_as_evidence_boundary", ["project/source-audit/spring-evidence-ledger-20260802.md"]),
}

REQUIRED_COMPLETE_REPORTS = [
    "data/reporting/spring_official_pdf_source_registration.json",
    "data/reporting/spring_source_backed_data_import_review.json",
    "data/reporting/spring_current_grade_snapshot_capture.json",
    "data/reporting/spring_exact_current_semantic_migration_review.json",
    "data/reporting/spring_standard_equipment_representation_review.json",
    "data/reporting/spring_biel_alpejska_default_colour_migration.json",
    "data/reporting/spring_charging_cable_representation_migration.json",
    "data/reporting/spring_charging_cable_commercial_semantics_review.json",
    "data/reporting/spring_charging_cable_commercial_semantics_migration.json",
    "data/reporting/post_spring_charging_cable_priority_selection_review.json",
    "data/reporting/spring_nonconflicting_technical_observations_review.json",
    "data/reporting/spring_nonconflicting_common_technical_migration.json",
]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader)


def obj(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def inventory_pages(path: Path, expected: int) -> list[int]:
    text = path.read_text(encoding="utf-8")
    if f"Pages: {expected}" not in text:
        raise RuntimeError(f"page-count declaration drifted: {path}")
    found = []
    for line in text.splitlines():
        match = re.match(r"^\|\s*(\d+)\s*\|", line)
        if match:
            found.append(int(match.group(1)))
    pages = sorted(set(found))
    if pages != list(range(1, expected + 1)):
        raise RuntimeError(f"page inventory is incomplete: {path}")
    return pages


def ledger_rows() -> list[dict[str, str]]:
    result = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| ---") or "Evidence area" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 5:
            result.append({
                "area": cells[0],
                "pages": cells[1],
                "facts": cells[2],
                "initial_status": cells[3],
                "boundary": cells[4],
            })
    if len(result) != 22:
        raise RuntimeError("Spring evidence-ledger area count drifted")
    return result


def build(root: Path = ROOT) -> dict[str, Any]:
    sources = {row["code"]: row for row in rows(root / SOURCES.relative_to(ROOT))}
    receipts = []
    for code, expected in SOURCE_RECEIPTS.items():
        source = sources.get(code)
        if source is None:
            raise RuntimeError(f"missing registered source: {code}")
        for field in ("file_path", "sha256", "document_date"):
            expected_field = "repository_path" if field == "file_path" else field
            if source[field] != expected[expected_field]:
                raise RuntimeError(f"registered {field} drifted for {code}")
        source_path = root / expected["repository_path"]
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected["sha256"]:
            raise RuntimeError(f"source bytes drifted for {code}")
        pages = inventory_pages(root / expected["inventory"], expected["pages"])
        receipts.append({
            "source_code": code,
            "repository_path": expected["repository_path"],
            "sha256": expected["sha256"],
            "document_date": expected["document_date"],
            "page_count": expected["pages"],
            "reviewed_pages": pages,
            "inventory": expected["inventory"],
        })

    intake_text = (root / INTAKE.relative_to(ROOT)).read_text(encoding="utf-8")
    if "**Status:** `fully_reviewed`" not in intake_text:
        raise RuntimeError("Spring full-assimilation intake is not fully reviewed")
    conflict_text = (root / CONFLICTS.relative_to(ROOT)).read_text(encoding="utf-8")
    for code in ("C-001", "C-002", "C-003", "C-004"):
        if code not in conflict_text:
            raise RuntimeError(f"missing Spring conflict receipt: {code}")

    ledger = ledger_rows()
    if {row["area"] for row in ledger} != set(AREA_OUTCOMES):
        raise RuntimeError("closure outcome map does not cover every ledger area")

    report_receipts = []
    for relative in REQUIRED_COMPLETE_REPORTS:
        payload = obj(root / relative)
        if payload.get("status") != "complete":
            raise RuntimeError(f"downstream report is not complete: {relative}")
        report_receipts.append(relative)

    review = obj(root / REVIEW.relative_to(ROOT))
    migration = obj(root / MIGRATION.relative_to(ROOT))
    if review.get("summary", {}).get("approved_observations") != 36:
        raise RuntimeError("approved Spring observation count drifted")
    if migration.get("observation_count") != 36 or migration.get("value_id_range") != [3569, 3604]:
        raise RuntimeError("Spring migration receipt drifted")

    value_rows = rows(root / VALUES.relative_to(ROOT))
    migrated = [
        row for row in value_rows
        if row.get("source_code") == "src_pl_spring_brochure_20260219"
        and row.get("observation_date") == "2026-02-19"
        and row.get("configuration_code") in CONFIGURATIONS
        and row.get("attribute_code") in APPROVED_ATTRIBUTES
    ]
    if len(migrated) != 36:
        raise RuntimeError("not all approved Spring observations are materialized")
    if sorted(int(row["id"]) for row in migrated) != list(range(3569, 3605)):
        raise RuntimeError("Spring migration value-ID range drifted")
    if Counter(row["configuration_code"] for row in migrated) != Counter({code: 12 for code in CONFIGURATIONS}):
        raise RuntimeError("Spring migration configuration matrix drifted")
    if Counter(row["attribute_code"] for row in migrated) != Counter({code: 3 for code in APPROVED_ATTRIBUTES}):
        raise RuntimeError("Spring migration attribute matrix drifted")

    source_codes = set(SOURCE_RECEIPTS)
    surface_counts = {}
    for label, path in {
        "scalar_values": VALUES,
        "range_values": RANGES,
        "availability_records": AVAILABILITY,
        "configuration_prices": PRICES,
    }.items():
        selected = [row for row in rows(root / path.relative_to(ROOT)) if row.get("source_code") in source_codes]
        surface_counts[label] = {
            "total": len(selected),
            "by_source": dict(sorted(Counter(row["source_code"] for row in selected).items())),
        }

    analysis = obj(root / ANALYSIS.relative_to(ROOT))
    summary = analysis.get("summary", {})
    if summary.get("eligible_candidate_count") != 0 or analysis.get("selected_next_package") is not None:
        raise RuntimeError("eligible source-backed configuration candidates remain")

    deferrals = list(migration.get("preserved_deferrals", []))
    expected_deferrals = {
        "battery_mass_204_kg_my2025_stock_only",
        "battery_voltage_354_v_my2025_stock_only",
        "battery_capacity_24_3_kwh_measurement_basis_unqualified",
        "charging_times_context_dependent",
        "ground_clearance_15_inch_wheel_only",
        "range_and_maximum_speed_not_reimported",
    }
    if set(deferrals) != expected_deferrals:
        raise RuntimeError("Spring technical deferral set drifted")

    outcome_rows = []
    for row in ledger:
        classification, evidence = AREA_OUTCOMES[row["area"]]
        for relative in evidence:
            if not (root / relative).is_file():
                raise RuntimeError(f"missing closure evidence: {relative}")
        outcome_rows.append({
            "area": row["area"],
            "initial_status": row["initial_status"],
            "closure_classification": classification,
            "evidence": evidence,
        })

    return {
        "version": 1,
        "kind": "spring_legacy_pdf_assimilation_closure",
        "generated_on": "2026-08-02",
        "status": "complete",
        "package_id": "spring_legacy_pdf_assimilation_closure_001",
        "milestone": {
            "phase": "Legacy PDF Source Audit",
            "scope": "Spring brochure 2026-02-19 and MY2025 stock price list 2026-07-08",
            "closure_status": "closed",
            "master_mutations_in_closure_package": 0,
        },
        "source_receipts": receipts,
        "page_accounting": {
            "source_count": 2,
            "brochure_pages": 22,
            "price_list_pages": 6,
            "reviewed_pages": 28,
            "unreviewed_pages": 0,
        },
        "ledger_accounting": {
            "area_count": len(ledger),
            "initial_status_counts": dict(sorted(Counter(row["initial_status"] for row in ledger).items())),
            "closure_outcomes": outcome_rows,
            "unclassified_area_count": 0,
        },
        "downstream_receipts": report_receipts,
        "materialized_observations": {
            "approved_attribute_count": 12,
            "approved_configuration_count": 3,
            "approved_observation_count": 36,
            "materialized_observation_count": len(migrated),
            "value_id_range": [3569, 3604],
            "source_code": "src_pl_spring_brochure_20260219",
            "observation_date": "2026-02-19",
        },
        "represented_source_surfaces": surface_counts,
        "preserved_deferrals": deferrals,
        "preserved_conflicts": [
            "C-001_temporal_model_year_charging_cable_conflict",
            "C-002_internal_price_list_charging_cable_contradiction",
            "C-003_brochure_narrative_matrix_precision_hierarchy",
            "C-004_brochure_vs_saved_my2026_range_evolution",
        ],
        "source_candidate_closure": {
            "eligible_candidate_count": 0,
            "selected_next_source_package": None,
            "source_exhausted_candidate_count": summary.get("exhausted_source_candidate_count"),
        },
        "closure_checks": {
            "both_source_hashes_verified": True,
            "all_pages_inventoried": True,
            "every_ledger_area_classified": True,
            "all_downstream_reports_complete": True,
            "all_approved_observations_materialized": True,
            "all_technical_deferrals_explicit": True,
            "all_documentary_conflicts_preserved": True,
            "no_eligible_source_candidate_remains": True,
            "no_new_attribute_or_domain_decision_required": True,
        },
        "release_handoff": {
            "last_public_release": "data-products-v1.10.0",
            "source_backed_repository_delta_after_release": True,
            "selected_next_package": "data_products_v1_11_0_accelerated_release_preparation_001",
            "selection_reason": "The legacy-PDF source milestone is closed with new source-backed Spring data and zero eligible source candidates; the existing immutable-release architecture can publish the verified current dataset without expanding source scope or changing product semantics.",
        },
        "next_package": {
            "package_id": "data_products_v1_11_0_accelerated_release_preparation_001",
            "kind": "accelerated_release_preparation",
            "name": "Data Products v1.11.0 Accelerated Release Preparation",
            "status": "planned",
            "goal": "Prepare an immutable v1.11.0 data-product release from the closed legacy-PDF milestone, prove the exact source SHA through double-build byte identity, preserve current product semantics, and publish only after complete Quality and post-merge verification.",
        },
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    pages = report["page_accounting"]
    ledger = report["ledger_accounting"]
    materialized = report["materialized_observations"]
    candidates = report["source_candidate_closure"]
    return f"""# Spring Legacy PDF Assimilation Closure

**Status:** complete  
**Date:** {report['generated_on']}  
**Package:** `{report['package_id']}`

## Milestone result

The Spring legacy-PDF source milestone is closed. Both exact registered files were hash-verified and every one of their **{pages['reviewed_pages']} pages** was inventoried and reviewed: {pages['brochure_pages']} brochure pages and {pages['price_list_pages']} price-list pages.

The complete evidence ledger contains **{ledger['area_count']} material areas**. Every area now has a durable closure outcome: represented data, a bounded migration receipt, an explicit dated conflict, an explicit deferral or a deliberate out-of-scope classification. No area remains unclassified.

## Materialized technical observations

The bounded technical sequence approved and materialized exactly **{materialized['materialized_observation_count']} observations** across three passenger Spring configurations and twelve canonical attributes. They occupy IDs **{materialized['value_id_range'][0]}–{materialized['value_id_range'][1]}** and retain exact brochure provenance dated {materialized['observation_date']}.

The closure does not import the MY2025-only 204 kg or 354 V values, the unqualified 24.3 kWh capacity, contextual charging times, wheel-qualified ground clearance, or replacement range/maximum-speed observations.

## Preserved conflicts and exclusions

- charging-cable states remain separated by source date, model year and exact matrix context;
- the internal page-2/page-4 price-list contradiction remains visible;
- brochure prose never overrides the exact equipment matrix;
- MY2026 saved configurations do not rewrite the February brochure;
- Cargo, accessory and interior-storage facts remain outside passenger configuration data until their missing context is modelled.

## Source-backed queue

The repository-wide missing-data analysis now reports **{candidates['eligible_candidate_count']} eligible source candidate** and no selected next source package. The seven exhausted candidates remain audit evidence rather than guessed negative data.

## Handoff

The next package is `{report['next_package']['package_id']}`. It will prepare immutable `data-products-v1.11.0` assets from the verified post-milestone repository state using the established exact-SHA and double-build publication contract.
"""


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    tmp.replace(path)


def apply(root: Path = ROOT) -> None:
    report = build(root)
    write_atomic(root / REPORT_JSON.relative_to(ROOT), render_json(report))
    write_atomic(root / REPORT_MD.relative_to(ROOT), render_markdown(report))


def verify(root: Path = ROOT) -> None:
    expected = build(root)
    actual = obj(root / REPORT_JSON.relative_to(ROOT))
    if actual != expected:
        raise RuntimeError("Spring legacy-PDF closure JSON is stale")
    markdown = (root / REPORT_MD.relative_to(ROOT)).read_text(encoding="utf-8")
    if markdown != render_markdown(expected):
        raise RuntimeError("Spring legacy-PDF closure Markdown is stale")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.apply:
        apply()
    else:
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
