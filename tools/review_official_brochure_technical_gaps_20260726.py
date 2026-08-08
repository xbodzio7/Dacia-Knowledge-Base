#!/usr/bin/env python3
"""Verify the classification of remaining official brochure technical evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

from catalog_completion_history import DUSTER_HYBRIDG150_CONFIGURATION_CODES

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "official_brochure_technical_gap_review.json"
CATALOG_COMPLETION = ROOT / "data" / "imports" / "catalog_completion" / "sandero-stepway-tce-20260703.json"
EXPECTED_CATALOG_CONFIGURATIONS = {
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_stepway_iii_essential_tce110_manual",
    "sandero_stepway_iii_expression_tce110_manual",
    "sandero_stepway_iii_extreme_tce110_manual",
}

SOURCE_CONTRACTS = {
    "src_pl_bigster_brochure_20251210": (
        "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf",
        "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74",
    ),
    "src_pl_jogger_brochure_20251217": (
        "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf",
        "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6",
    ),
    "src_pl_sandero_brochure_20260202": (
        "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
        "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
    ),
    "src_pl_sandero_stepway_brochure_20260202": (
        "PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf",
        "800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48",
    ),
    "src_pl_duster_mini_brochure_20251020": (
        "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf",
        "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8",
    ),
}

EXPECTED_CLASSIFICATION_CODES = {
    "bigster_core_powertrain_covered_or_newer",
    "bigster_gross_train_weight_candidate",
    "bigster_unbraked_trailer_weight_candidate",
    "bigster_chassis_measurement_modeling",
    "bigster_dimensions_covered_and_cargo_deferred",
    "jogger_core_powertrain_covered_or_newer",
    "jogger_hybrid155_acceleration_candidate",
    "jogger_hybrid_battery_capacity_candidate",
    "jogger_engine_speed_range_candidate",
    "jogger_chassis_candidate_and_modeling",
    "jogger_mass_table_label_conflict",
    "jogger_blank_wltp_cells",
    "jogger_dimensions_and_cargo",
    "sandero_manual_core_covered",
    "sandero_ecog120_automatic_exact_candidate",
    "sandero_tce100_without_exact_configuration",
    "sandero_wltp_placeholders",
    "sandero_chassis_and_maximum_mass_modeling",
    "sandero_dimensions_and_cargo",
    "stepway_core_covered",
    "stepway_tce110_without_exact_configuration",
    "stepway_chassis_and_maximum_mass_modeling",
    "stepway_dimensions_and_cargo",
    "duster_core_powertrain_covered_or_newer",
    "duster_gross_train_weight_candidate",
    "duster_unbraked_trailer_weight_candidate",
    "duster_hybridg150_without_exact_configuration",
    "duster_chassis_mass_and_payload_modeling",
    "duster_wltp_placeholders_and_dimensions",
}

EXPECTED_STATUS_COUNTS = Counter(
    {
        "covered_or_superseded": 5,
        "exact_import_candidate": 6,
        "requires_context_or_attribute_modeling": 5,
        "covered_or_explicitly_deferred": 4,
        "exact_range_candidate": 1,
        "ambiguous_source_evidence": 1,
        "no_observation": 2,
        "next_package_candidate": 1,
        "unmodeled_exact_configuration": 3,
        "no_observation_or_generic_projection": 1,
    }
)

SANDERO_AUTOMATICS = {
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
}
SANDERO_AUTOMATIC_CANDIDATE_ATTRIBUTES = {
    "engine_power",
    "engine_torque",
    "engine_displacement",
    "cylinder_count",
    "total_valve_count",
    "emission_standard",
    "gearbox_type",
    "gear_count",
    "top_speed",
    "acceleration_0_100",
    "fuel_tank_capacity",
    "minimum_kerb_weight",
    "gross_vehicle_weight",
    "gross_train_weight",
    "braked_trailer_weight",
}


class ReviewError(RuntimeError):
    """Raised when the reviewed technical-gap inventory drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classification_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    classifications = payload.get("classifications")
    ensure(isinstance(classifications, list), "classifications must be a list")
    ensure(all(isinstance(item, dict) for item in classifications), "classification must be an object")
    result = {str(item.get("code", "")): item for item in classifications}
    ensure(len(result) == len(classifications), "classification codes are empty or duplicated")
    return result


def verify_report(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    ensure(payload.get("version") == 1, "unsupported review version")
    ensure(payload.get("kind") == "official_brochure_technical_gap_review", "unexpected review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "review is not complete")

    scope = payload.get("scope")
    ensure(isinstance(scope, dict) and scope.get("sources") == 5, "review scope must contain five sources")
    pages = scope.get("technical_table_pages")
    ensure(isinstance(pages, list) and len(pages) == 5, "technical page inventory differs")
    ensure({str(item.get("source_code", "")) for item in pages if isinstance(item, dict)} == set(SOURCE_CONTRACTS), "technical page source set differs")

    coverage = payload.get("current_brochure_coverage")
    ensure(
        coverage
        == {
            "scalar_values": 357,
            "ranges": 0,
            "attributes": {"boot_capacity": 287, "elasticity_80_120": 70},
            "source_configuration_relationships": 52,
        },
        "current brochure coverage receipt differs",
    )

    by_code = classification_index(payload)
    ensure(set(by_code) == EXPECTED_CLASSIFICATION_CODES, "classification code set differs")
    ensure(Counter(str(item.get("status", "")) for item in by_code.values()) == EXPECTED_STATUS_COUNTS, "classification status distribution differs")
    for code, item in by_code.items():
        ensure(item.get("source_code") in SOURCE_CONTRACTS, f"unknown source in classification: {code}")
        ensure(isinstance(item.get("page"), int) and item["page"] > 0, f"invalid source page: {code}")
        ensure(isinstance(item.get("configuration_count"), int) and item["configuration_count"] >= 0, f"invalid configuration count: {code}")
        ensure(isinstance(item.get("attributes"), list) and item["attributes"], f"classification attributes missing: {code}")
        ensure(str(item.get("reason", "")).strip(), f"classification reason missing: {code}")

    queue = payload.get("priority_queue")
    ensure(isinstance(queue, list) and len(queue) == 4, "priority queue must contain four packages")
    ensure([item.get("priority") for item in queue] == [1, 2, 3, 4], "priority order differs")
    ensure(all(set(item.get("classification_codes", [])) <= set(by_code) for item in queue), "priority queue references unknown classification")

    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Sandero Eco-G 120 Automatic Brochure Technical Import", "next package differs")
    ensure("two active Eco-G 120 automatic" in str(next_package.get("goal", "")), "next package goal is incomplete")
    return by_code


def verify_sources() -> None:
    sources = {row.get("code", ""): row for row in read_rows(MASTER / "sources.csv")}
    for code, (relative_path, sha256) in SOURCE_CONTRACTS.items():
        source = sources.get(code)
        ensure(source is not None and source.get("status") == "active", f"active source missing: {code}")
        ensure(source.get("source_type") == "brochure_pdf", f"source type differs: {code}")
        ensure(source.get("file_path") == relative_path, f"source path differs: {code}")
        ensure(source.get("sha256") == sha256, f"source registry hash differs: {code}")
        archived = ROOT / relative_path
        ensure(archived.is_file(), f"archived brochure missing: {relative_path}")
        ensure(file_sha256(archived) == sha256, f"archived brochure hash differs: {code}")


def verify_current_coverage() -> None:
    values = read_rows(MASTER / "configuration_attribute_values.csv")
    ranges = read_rows(MASTER / "configuration_attribute_value_ranges.csv")
    relationships = read_rows(MASTER / "source_configurations.csv")
    brochure_values = [row for row in values if row.get("source_code") in SOURCE_CONTRACTS]
    brochure_ranges = [row for row in ranges if row.get("source_code") in SOURCE_CONTRACTS]
    brochure_relationships = [row for row in relationships if row.get("source_code") in SOURCE_CONTRACTS]
    baseline_counts = Counter(row.get("attribute_code", "") for row in brochure_values)
    ensure(baseline_counts["boot_capacity"] == 287, "brochure cargo baseline differs")
    ensure(baseline_counts["elasticity_80_120"] == 70, "brochure selected-gear baseline differs")
    ensure(len(brochure_values) >= 357, "brochure scalar value baseline regressed")
    ensure(len(brochure_relationships) >= 52, "brochure relationship baseline regressed")
    ensure(isinstance(brochure_ranges, list), "brochure range inventory is invalid")


def active_configurations() -> dict[str, dict[str, str]]:
    return {
        row.get("code", ""): row
        for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }


def current_scalar_pairs() -> set[tuple[str, str]]:
    return {
        (row.get("configuration_code", ""), row.get("attribute_code", ""))
        for row in read_rows(MASTER / "configuration_attribute_values.csv")
    }


def verify_priority_candidates(by_code: dict[str, dict[str, Any]]) -> None:
    configurations = active_configurations()
    pairs = current_scalar_pairs()

    ensure(SANDERO_AUTOMATICS <= set(configurations), "two active automatic Sandero configurations are missing")
    for code in SANDERO_AUTOMATICS:
        row = configurations[code]
        ensure(row.get("powertrain_label") == "Eco-G 120", f"automatic Sandero powertrain differs: {code}")
        ensure(row.get("transmission_type") == "automatic", f"automatic Sandero transmission differs: {code}")
        present = {attribute for configuration, attribute in pairs if configuration == code}
        materialized = present & SANDERO_AUTOMATIC_CANDIDATE_ATTRIBUTES
        ensure(
            not materialized or materialized == SANDERO_AUTOMATIC_CANDIDATE_ATTRIBUTES,
            f"automatic Sandero candidate is only partially populated: {code}",
        )
    ensure(by_code["sandero_ecog120_automatic_exact_candidate"]["configuration_count"] == 2, "automatic Sandero candidate count differs")
    ensure(set(by_code["sandero_ecog120_automatic_exact_candidate"]["attributes"]) == SANDERO_AUTOMATIC_CANDIDATE_ATTRIBUTES, "automatic Sandero candidate attributes differ")

    bigster = {code for code in configurations if code.startswith("bigster_")}
    ensure(len(bigster) == 14, "active Bigster scope differs")

    jogger_hybrid = {
        code
        for code, row in configurations.items()
        if code.startswith("jogger_") and row.get("powertrain_label") == "hybrid 155"
    }
    ensure(len(jogger_hybrid) == 6, "Jogger hybrid 155 scope differs")

    duster_exact = {
        code
        for code, row in configurations.items()
        if code.startswith("duster_iii_")
        and (
            (row.get("powertrain_label") == "Eco-G 120 4x2" and row.get("transmission_type") == "manual")
            or row.get("powertrain_label") in {"mild hybrid 140 4x2", "hybrid 155 4x2"}
        )
    }
    ensure(len(duster_exact) == 10, "exact Duster brochure candidate scope differs")


def verify_non_import_boundaries() -> None:
    configurations = active_configurations()
    exact_catalog = {
        code
        for code in configurations
        if (code.startswith("sandero_iii_") and "tce100" in code)
        or (code.startswith("sandero_stepway_iii_") and "tce110" in code)
    }
    if CATALOG_COMPLETION.exists():
        contract = json.loads(CATALOG_COMPLETION.read_text(encoding="utf-8"))
        ensure(
            set(contract.get("configuration_codes", [])) == EXPECTED_CATALOG_CONFIGURATIONS,
            "catalogue completion configuration scope differs",
        )
        ensure(
            exact_catalog == EXPECTED_CATALOG_CONFIGURATIONS,
            "exact TCe catalogue configurations differ from the bounded completion package",
        )
    else:
        ensure(not exact_catalog, "an exact Sandero or Stepway TCe catalogue configuration now exists")
    later_duster_configurations = {
        code
        for code in configurations
        if code.startswith("duster_iii_") and "hybridg150" in code
    }
    ensure(
        later_duster_configurations == DUSTER_HYBRIDG150_CONFIGURATION_CODES,
        "later exact Duster hybrid-G 150 catalogue scope differs",
    )


def check() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    by_code = verify_report(payload)
    verify_sources()
    verify_current_coverage()
    verify_priority_candidates(by_code)
    verify_non_import_boundaries()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        check()
    except (ReviewError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("PASS: official brochure technical gap review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
