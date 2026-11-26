#!/usr/bin/env python3
"""Verify the scope-preserving cross-model comparison-view review."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from catalog_completion_history import completion_applied

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "cross_model_comparison_view_review.json"
STATE = ROOT / "project" / "state.json"
PUBLICATION_AUDIT = (
    ROOT
    / "project"
    / "releases"
    / "data-products-v1.7.0-publication-audit.json"
)

sys.path.insert(0, str(ROOT / "tools"))

from reporting.configuration_comparison_bundle import discover_scopes  # noqa: E402
from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402
from reporting.configuration_shortlist_html import collect_browser_catalog  # noqa: E402

EXPECTED_MODELS = {
    "bigster": {
        "name": "Bigster",
        "generation": "I",
        "body": "suv",
        "segment": "SUV-C",
        "configurations": 14,
        "versions": 4,
        "exclusive_scopes": 4,
        "shared_scopes": 0,
        "price_min": 101400,
        "price_max": 137600,
        "seat_values": [],
    },
    "duster_iii": {
        "name": "Duster",
        "generation": "III",
        "body": "suv",
        "segment": "SUV-C",
        "configurations": 27,
        "versions": 5,
        "exclusive_scopes": 8,
        "shared_scopes": 0,
        "price_min": 82000,
        "price_max": 123600,
        "seat_values": [],
    },
    "jogger": {
        "name": "Jogger",
        "generation": "I",
        "body": "estate",
        "segment": "C",
        "configurations": 22,
        "versions": 4,
        "exclusive_scopes": 4,
        "shared_scopes": 0,
        "price_min": 77900,
        "price_max": 118050,
        "seat_values": [5, 7],
    },
    "sandero_iii": {
        "name": "Sandero",
        "generation": "III",
        "body": "hatchback",
        "segment": "B",
        "configurations": 4,
        "versions": 2,
        "exclusive_scopes": 1,
        "shared_scopes": 1,
        "price_min": 68000,
        "price_max": 80500,
        "seat_values": [5],
    },
    "sandero_stepway_iii": {
        "name": "Sandero Stepway",
        "generation": "III",
        "body": "crossover",
        "segment": "B",
        "configurations": 5,
        "versions": 3,
        "exclusive_scopes": 1,
        "shared_scopes": 1,
        "price_min": 71700,
        "price_max": 89400,
        "seat_values": [5],
    },
}


class ReviewError(RuntimeError):
    """Raised when the review contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def repository_inventory() -> dict[str, Any]:
    models = {row["code"]: row for row in rows(MASTER / "models.csv")}
    versions = {row["code"]: row for row in rows(MASTER / "versions.csv")}
    configurations = {
        row["code"]: row
        for row in rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    catalog = collect_browser_catalog(ROOT, ShortlistCriteria())
    catalog_items = {
        item["configuration_code"]: item
        for item in catalog["configurations"]
    }
    scopes = discover_scopes(ROOT)

    configuration_model = {
        code: versions[row["version_code"]]["model_code"]
        for code, row in configurations.items()
    }
    model_codes = sorted(set(configuration_model.values()))
    scope_models: dict[str, set[str]] = {
        scope.slug: {configuration_model[code] for code in scope.configuration_codes}
        for scope in scopes
    }

    model_records: dict[str, dict[str, Any]] = {}
    for model_code in model_codes:
        codes = sorted(
            code for code, code_model in configuration_model.items()
            if code_model == model_code
        )
        items = [catalog_items[code] for code in codes]
        prices = [
            int(item["catalog_price"]["amount"])
            for item in items
            if item["catalog_price"].get("state") == "recorded"
        ]
        seat_values = sorted({
            int(item["number_of_seats"]["value"])
            for item in items
            if item["number_of_seats"].get("state") == "recorded"
        })
        scope_slugs = sorted(
            slug for slug, members in scope_models.items()
            if model_code in members
        )
        exclusive = sum(scope_models[slug] == {model_code} for slug in scope_slugs)
        shared = len(scope_slugs) - exclusive
        model = models[model_code]
        model_records[model_code] = {
            "model_name": model.get("name", ""),
            "generation": model.get("generation", ""),
            "body_type_code": model.get("body_type_code", ""),
            "segment_code": model.get("segment_code", ""),
            "configuration_count": len(codes),
            "version_count": len({configurations[code]["version_code"] for code in codes}),
            "exclusive_scope_count": exclusive,
            "shared_scope_count": shared,
            "catalog_price_min_pln": min(prices) if prices else None,
            "catalog_price_max_pln": max(prices) if prices else None,
            "catalog_price_coverage": f"{len(prices)}/{len(codes)}",
            "recorded_seat_values": seat_values,
            "scope_slugs": scope_slugs,
        }

    scope_records = []
    for scope in scopes:
        members = sorted(scope_models[scope.slug])
        scope_records.append({
            "slug": scope.slug,
            "model_codes": members,
            "configuration_count": len(scope.configuration_codes),
            "pair_count": len(scope.configuration_codes) * (len(scope.configuration_codes) - 1) // 2,
            "technical_slot_count": len(scope.completeness_spec.get("technical_slots", [])),
            "configuration_codes": list(scope.configuration_codes),
        })

    return {
        "as_of": catalog["as_of"],
        "configurations": configurations,
        "models": model_records,
        "scopes": scope_records,
        "scope_count": len(scopes),
        "pair_count": sum(record["pair_count"] for record in scope_records),
        "mixed_scopes": [record for record in scope_records if len(record["model_codes"]) > 1],
        "technical_facets": len(catalog["facets"]["comparison_values"]),
        "equipment_facets": len(catalog["facets"]["equipment"]),
        "price_recorded_count": sum(
            item["catalog_price"].get("state") == "recorded"
            for item in catalog["configurations"]
        ),
    }


def verify_report(payload: Mapping[str, Any], inventory: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported review version")
    ensure(payload.get("kind") == "cross_model_comparison_view_review", "unexpected review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "review is not complete")

    source = payload.get("source_release")
    ensure(isinstance(source, dict), "source release is missing")
    ensure(source.get("tag") == "data-products-v1.7.0", "source release tag differs")
    ensure(
        source.get("target_commit")
        == "99e0e19b86cad6eae619f37702464e6a5a761cd8",
        "source release commit differs",
    )
    ensure(source.get("verification") == "PASS", "source release is not verified")
    audit = load_json(PUBLICATION_AUDIT)
    ensure(audit.get("release_id") == 360090447, "publication audit release ID differs")
    ensure(audit.get("verification") == "PASS", "publication audit did not pass")

    reported = payload.get("inventory")
    ensure(isinstance(reported, dict), "review inventory is missing")
    expected_counts = {
        "as_of": inventory["as_of"],
        "active_configuration_count": 72,
        "model_family_count": 5,
        "reporting_scope_count": 19,
        "single_model_scope_count": 18,
        "mixed_model_scope_count": 1,
        "within_scope_pair_count": 114,
        "price_recorded_count": 72,
        "technical_comparison_facet_count": 124,
        "equipment_facet_count": 110,
        "one_scope_per_configuration": True,
    }
    ensure(reported == expected_counts, "review inventory counters differ")

    raw_models = payload.get("model_families")
    ensure(isinstance(raw_models, list) and len(raw_models) == 5, "model-family inventory differs")
    report_models = {item.get("model_code"): item for item in raw_models if isinstance(item, dict)}
    ensure(set(report_models) == set(EXPECTED_MODELS), "model-family codes differ")
    for model_code, expected in EXPECTED_MODELS.items():
        item = report_models[model_code]
        actual = inventory["models"][model_code]
        ensure(item.get("model_name") == expected["name"] == actual["model_name"], f"model name differs: {model_code}")
        ensure(item.get("generation") == expected["generation"] == actual["generation"], f"generation differs: {model_code}")
        ensure(item.get("body_type_code") == expected["body"] == actual["body_type_code"], f"body differs: {model_code}")
        ensure(item.get("segment_code") == expected["segment"] == actual["segment_code"], f"segment differs: {model_code}")
        for report_key, expected_key in (
            ("configuration_count", "configurations"),
            ("version_count", "versions"),
            ("exclusive_scope_count", "exclusive_scopes"),
            ("shared_scope_count", "shared_scopes"),
            ("catalog_price_min_pln", "price_min"),
            ("catalog_price_max_pln", "price_max"),
        ):
            ensure(item.get(report_key) == expected[expected_key] == actual[report_key], f"{report_key} differs: {model_code}")
        ensure(item.get("catalog_price_coverage") == actual["catalog_price_coverage"], f"price coverage differs: {model_code}")
        ensure(item.get("recorded_seat_values") == expected["seat_values"] == actual["recorded_seat_values"], f"seat values differ: {model_code}")
        ensure(set(item.get("scope_slugs", [])) == set(actual["scope_slugs"]), f"scope membership differs: {model_code}")

    mixed = payload.get("existing_mixed_model_scope")
    ensure(isinstance(mixed, dict), "mixed-model scope record is missing")
    ensure(len(inventory["mixed_scopes"]) == 1, "repository mixed-scope count differs")
    actual_mixed = inventory["mixed_scopes"][0]
    ensure(mixed.get("slug") == actual_mixed["slug"] == "sandero_ecog120_manual", "mixed scope slug differs")
    ensure(mixed.get("model_codes") == actual_mixed["model_codes"] == ["sandero_iii", "sandero_stepway_iii"], "mixed scope models differ")
    ensure(mixed.get("configuration_count") == actual_mixed["configuration_count"] == 5, "mixed scope configuration count differs")
    ensure(mixed.get("pair_count") == actual_mixed["pair_count"] == 10, "mixed scope pair count differs")
    ensure(mixed.get("technical_slot_count") == actual_mixed["technical_slot_count"] == 56, "mixed scope slot count differs")

    options = payload.get("design_options")
    ensure(isinstance(options, list) and len(options) == 4, "design options differ")
    statuses = {item.get("code"): item.get("status") for item in options if isinstance(item, dict)}
    ensure(statuses == {
        "scope_preserving_navigation": "selected",
        "global_common_attribute_matrix": "rejected",
        "unrestricted_cross_model_pairs": "rejected",
        "normalized_model_ranking": "rejected",
    }, "design option decisions differ")

    selection = payload.get("selection")
    ensure(isinstance(selection, dict), "selection is missing")
    ensure(selection.get("code") == "scope_preserving_navigation", "selected design differs")
    ensure(selection.get("layers") == [
        "model_family_overview",
        "reporting_scope_directory",
        "existing_scope_comparison_launch",
    ], "selected layers differ")
    ensure("Never synthesize a pair" in str(selection.get("pair_generation_rule", "")), "pair-generation prohibition is missing")
    ensure("sandero_ecog120_manual" in str(selection.get("mixed_scope_rule", "")), "mixed-scope rule is missing")

    contract = payload.get("implementation_contract")
    ensure(isinstance(contract, dict), "implementation contract is missing")
    ensure(contract.get("next_package") == "Cross-Model Comparison View Foundation", "implementation package differs")
    ensure(contract.get("outputs") == ["deterministic_json", "standalone_html"], "implementation outputs differ")
    ensure(contract.get("model_card_count") == 5, "model-card count differs")
    ensure(contract.get("scope_card_count") == 19, "scope-card count differs")
    ensure(contract.get("configuration_count") == 72, "implementation configuration count differs")
    ensure(contract.get("master_data_changes") is False, "implementation changes master data")
    ensure(contract.get("new_schema") is False, "implementation introduces schema")
    ensure(contract.get("new_comparison_engine") is False, "implementation introduces comparison engine")
    ensure(len(contract.get("acceptance_criteria", [])) == 7, "acceptance criteria differ")

    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Cross-Model Comparison View Foundation", "next package differs")


def verify_state() -> None:
    state = load_json(STATE)
    ensure(state.get("phase") == "Cross-Model Comparison View Review", "project phase differs")
    ensure(
        state.get("current_package", {}).get("name")
        == "Cross-Model Comparison View Review",
        "current package differs",
    )
    ensure(state.get("current_package", {}).get("status") == "complete", "current package is not complete")
    ensure(
        state.get("next_package", {}).get("name")
        == "Cross-Model Comparison View Foundation",
        "state next package differs",
    )
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests") == 979, "test baseline differs")
    ensure(baseline.get("rows") == 9688, "master row baseline changed")
    ensure(baseline.get("configuration_values") == 2949, "configuration values changed")
    ensure(baseline.get("configuration_value_ranges") == 244, "configuration ranges changed")
    ensure(baseline.get("attributes") == 385, "attribute baseline changed")


def verify() -> None:
    payload = load_json(REPORT)
    if completion_applied(ROOT):
        inventory = {
            "as_of": payload.get("inventory", {}).get("as_of"),
            "configurations": [None] * 72,
            "models": {},
            "scopes": [],
            "scope_count": 19,
            "pair_count": 114,
            "mixed_scopes": [],
            "technical_facets": 124,
            "equipment_facets": 110,
            "price_recorded_count": 72,
        }
        reported = payload.get("inventory")
        ensure(isinstance(reported, dict), "review inventory is missing")
        ensure(reported.get("active_configuration_count") == 72, "historical configuration count differs")
        ensure(reported.get("reporting_scope_count") == 19, "historical scope count differs")
        ensure(reported.get("within_scope_pair_count") == 114, "historical pair count differs")
        state = load_json(STATE)
        ensure(isinstance(state.get("current_package"), dict), "current project state is missing")
        return
    inventory = repository_inventory()
    ensure(len(inventory["configurations"]) == 72, "active configuration count differs")
    ensure(inventory["scope_count"] == 19, "scope count differs")
    ensure(inventory["pair_count"] == 114, "within-scope pair count differs")
    ensure(inventory["technical_facets"] == 124, "technical facet count differs")
    ensure(inventory["equipment_facets"] == 110, "equipment facet count differs")
    ensure(inventory["price_recorded_count"] == 72, "price coverage differs")
    verify_report(payload, inventory)
    verify_state()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the review contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ReviewError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: cross-model comparison view review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
