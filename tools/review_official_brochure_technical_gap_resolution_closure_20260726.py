#!/usr/bin/env python3
"""Verify closure of the official brochure technical gap priority queue."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
REPORT = REPORTING / "official_brochure_technical_gap_resolution_closure_review.json"
ORIGINAL = REPORTING / "official_brochure_technical_gap_review.json"

SOURCES = {
    "src_pl_sandero_brochure_20260202",
    "src_pl_sandero_stepway_brochure_20260202",
    "src_pl_jogger_brochure_20251217",
    "src_pl_bigster_brochure_20251210",
    "src_pl_duster_mini_brochure_20251020",
}
EXPECTED_SCALAR_BY_SOURCE = Counter(
    {
        "src_pl_sandero_brochure_20260202": 92,
        "src_pl_sandero_stepway_brochure_20260202": 72,
        "src_pl_jogger_brochure_20251217": 248,
        "src_pl_bigster_brochure_20251210": 180,
        "src_pl_duster_mini_brochure_20251020": 144,
    }
)
EXPECTED_RANGE_BY_SOURCE = Counter(
    {
        "src_pl_jogger_brochure_20251217": 58,
        "src_pl_duster_mini_brochure_20251020": 10,
    }
)
EXPECTED_CURRENT_RANGE_BY_SOURCE = EXPECTED_RANGE_BY_SOURCE + Counter(
    {"src_pl_bigster_brochure_20251210": 30}
)
EXPECTED_RESIDUAL_STATUS_COUNTS = Counter(
    {
        "covered_or_superseded": 5,
        "covered_or_explicitly_deferred": 4,
        "unmodeled_exact_configuration": 3,
        "no_observation": 2,
        "ambiguous_source_evidence": 1,
        "no_observation_or_generic_projection": 1,
    }
)
EXPECTED_RESOLVED = {
    "sandero_ecog120_automatic_exact_candidate",
    "bigster_gross_train_weight_candidate",
    "bigster_unbraked_trailer_weight_candidate",
    "duster_gross_train_weight_candidate",
    "duster_unbraked_trailer_weight_candidate",
    "jogger_hybrid155_acceleration_candidate",
    "jogger_hybrid_battery_capacity_candidate",
    "jogger_engine_speed_range_candidate",
    "bigster_chassis_measurement_modeling",
    "jogger_chassis_candidate_and_modeling",
    "sandero_chassis_and_maximum_mass_modeling",
    "stepway_chassis_and_maximum_mass_modeling",
    "duster_chassis_mass_and_payload_modeling",
}
EXPECTED_RESIDUAL = {
    "bigster_core_powertrain_covered_or_newer",
    "bigster_dimensions_covered_and_cargo_deferred",
    "jogger_core_powertrain_covered_or_newer",
    "jogger_mass_table_label_conflict",
    "jogger_blank_wltp_cells",
    "jogger_dimensions_and_cargo",
    "sandero_manual_core_covered",
    "sandero_tce100_without_exact_configuration",
    "sandero_wltp_placeholders",
    "sandero_dimensions_and_cargo",
    "stepway_core_covered",
    "stepway_tce110_without_exact_configuration",
    "stepway_dimensions_and_cargo",
    "duster_core_powertrain_covered_or_newer",
    "duster_hybridg150_without_exact_configuration",
    "duster_wltp_placeholders_and_dimensions",
}
CHECKERS = (
    ROOT / "tools" / "review_official_brochure_technical_gaps_20260726.py",
    ROOT / "tools" / "import_sandero_ecog120_automatic_brochure_technical_20260726.py",
    ROOT / "tools" / "import_bigster_duster_brochure_towing_masses_20260726.py",
    ROOT / "tools" / "import_jogger_brochure_hybrid_performance_20260726.py",
    ROOT / "tools" / "review_brochure_chassis_modeling_closure_20260726.py",
)


class ClosureError(RuntimeError):
    """Raised when the brochure gap closure contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported closure review version")
    ensure(payload.get("kind") == "official_brochure_technical_gap_resolution_closure_review", "unexpected closure review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "closure review is not complete")
    ensure(payload.get("source_review") == "official_brochure_technical_gap_review.json", "source review differs")

    inventory = payload.get("original_inventory")
    ensure(
        inventory
        == {
            "sources": 5,
            "classifications": 29,
            "priority_packages": 4,
            "priority_classifications": 13,
            "residual_classifications": 16,
        },
        "original inventory differs",
    )

    priorities = payload.get("priority_resolutions")
    ensure(isinstance(priorities, list) and len(priorities) == 4, "expected four priority resolutions")
    ensure([item.get("priority") for item in priorities] == [1, 2, 3, 4], "priority order differs")
    codes = {
        str(code)
        for item in priorities
        for code in item.get("classification_codes", [])
    }
    ensure(codes == EXPECTED_RESOLVED, "resolved classification set differs")
    ensure(sum(int(item.get("scalar_values", 0)) for item in priorities) == 379, "priority scalar total differs")
    ensure(sum(int(item.get("range_values", 0)) for item in priorities) == 68, "priority range total differs")
    ensure(sum(int(item.get("new_attributes", 0)) for item in priorities) == 4, "priority attribute total differs")

    ensure(
        payload.get("resolution_totals")
        == {"classifications": 13, "scalar_values": 379, "range_values": 68, "new_attributes": 4},
        "resolution totals differ",
    )

    coverage = payload.get("current_brochure_coverage")
    ensure(isinstance(coverage, dict), "current brochure coverage is missing")
    ensure(coverage.get("scalar_values") == 736, "coverage scalar total differs")
    ensure(coverage.get("range_values") == 68, "coverage range total differs")
    ensure(Counter(coverage.get("scalar_values_by_source", {})) == EXPECTED_SCALAR_BY_SOURCE, "reported source scalar totals differ")
    ensure(Counter(coverage.get("range_values_by_source", {})) == EXPECTED_RANGE_BY_SOURCE, "reported source range totals differ")
    ensure(coverage.get("priority_scalar_id_range") == [2189, 2567], "priority scalar ID range differs")
    ensure(coverage.get("priority_range_id_range") == [177, 244], "priority range ID range differs")

    residual = payload.get("residual_evidence")
    ensure(isinstance(residual, dict), "residual evidence is missing")
    ensure(residual.get("classifications") == 16, "residual classification total differs")
    ensure(Counter(residual.get("status_counts", {})) == EXPECTED_RESIDUAL_STATUS_COUNTS, "reported residual status counts differ")
    ensure(set(residual.get("classification_codes", [])) == EXPECTED_RESIDUAL, "reported residual classification set differs")

    rules = payload.get("non_inference_contract")
    ensure(isinstance(rules, list) and len(rules) == 5, "expected five non-inference rules")
    ensure(all(str(item).strip() for item in rules), "empty non-inference rule")
    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Official Brochure Residual Evidence Review", "next package differs")


def verify_original_review() -> None:
    original = load_json(ORIGINAL)
    classifications = {
        str(item.get("code", "")): item
        for item in original.get("classifications", [])
        if isinstance(item, dict)
    }
    ensure(len(classifications) == 29, "original classification inventory differs")
    ensure(set(classifications) == EXPECTED_RESOLVED | EXPECTED_RESIDUAL, "original classification partition differs")
    ensure(
        Counter(classifications[code].get("status", "") for code in EXPECTED_RESIDUAL)
        == EXPECTED_RESIDUAL_STATUS_COUNTS,
        "residual source statuses differ",
    )

    queue = original.get("priority_queue")
    ensure(isinstance(queue, list) and len(queue) == 4, "original priority queue differs")
    queue_codes = {
        str(code)
        for item in queue
        for code in item.get("classification_codes", [])
    }
    ensure(queue_codes == EXPECTED_RESOLVED, "original priority queue classification set differs")


def verify_current_coverage() -> None:
    scalar = [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("source_code") in SOURCES
    ]
    ranges = [
        row
        for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
        if row.get("source_code") in SOURCES
    ]
    follow_up = (REPORTING / "brochure_generic_dimensions_semantic_mapping_review.json")
    imported = False
    if follow_up.is_file():
        imported = load_json(follow_up).get("import_receipt", {}).get("status") == "imported"
    expected_scalar = Counter(EXPECTED_SCALAR_BY_SOURCE)
    expected_total = 736
    if imported:
        expected_scalar.update(
            {
                "src_pl_sandero_brochure_20260202": 40,
                "src_pl_jogger_brochure_20251217": 242,
                "src_pl_duster_mini_brochure_20251020": 100,
            }
        )
        expected_total = 1118
    eco_mode = [
        row
        for row in scalar
        if row.get("source_code") == "src_pl_bigster_brochure_20251210"
        and row.get("attribute_code") == "eco_mode"
    ]
    if eco_mode:
        ensure(len(eco_mode) == 14, "Bigster eco-mode receipt differs")
        expected_scalar.update({"src_pl_bigster_brochure_20251210": 14})
        expected_total += 14
    ensure(len(scalar) == expected_total, f"expected exactly {expected_total} brochure scalar values")
    ensure(len(ranges) == 98, "expected exactly 98 current brochure ranges")
    ensure(Counter(row.get("source_code", "") for row in scalar) == expected_scalar, "master source scalar totals differ")
    ensure(Counter(row.get("source_code", "") for row in ranges) == EXPECTED_CURRENT_RANGE_BY_SOURCE, "current master source range totals differ")

    priority_scalar = [row for row in scalar if 2189 <= int(row["id"]) <= 2567]
    priority_ranges = [row for row in ranges if 177 <= int(row["id"]) <= 244]
    ensure(len(priority_scalar) == 379, "priority scalar receipt differs")
    ensure([int(row["id"]) for row in priority_scalar] == list(range(2189, 2568)), "priority scalar IDs are not contiguous")
    ensure(len(priority_ranges) == 68, "priority range receipt differs")
    ensure([int(row["id"]) for row in priority_ranges] == list(range(177, 245)), "priority range IDs are not contiguous")
    if imported:
        dimensions = [row for row in scalar if 2568 <= int(row["id"]) <= 2949]
        ensure(len(dimensions) == 382, "generic dimension follow-up receipt differs")
        ensure([int(row["id"]) for row in dimensions] == list(range(2568, 2950)), "generic dimension IDs differ")

def verify_non_import_boundaries() -> None:
    scalar = [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("source_code") in SOURCES
    ]
    jogger_mass = {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"}
    ensure(
        not any(
            row.get("source_code") == "src_pl_jogger_brochure_20251217"
            and row.get("attribute_code") in jogger_mass
            for row in scalar
        ),
        "ambiguous Jogger mass evidence was imported",
    )
    placeholder_attributes = {"co2_emissions", "fuel_consumption_combined"}
    ensure(
        not any(
            row.get("source_code") in {"src_pl_jogger_brochure_20251217", "src_pl_sandero_brochure_20260202"}
            and row.get("attribute_code") in placeholder_attributes
            for row in scalar
        ),
        "blank or placeholder WLTP evidence was imported",
    )
    approved_attributes = {
        "overall_length", "overall_width", "overall_width_with_mirrors", "overall_height",
        "roof_height_with_rails", "wheelbase", "ground_clearance", "front_track",
        "rear_track", "front_overhang", "rear_overhang",
    }
    dimensions = [row for row in scalar if row.get("attribute_code") in approved_attributes]
    if dimensions:
        approved = [row for row in dimensions if 2568 <= int(row["id"]) <= 2949]
        ensure(len(dimensions) == 382 and len(approved) == 382, "unreviewed generic brochure dimension was imported")
        ensure(
            Counter(row.get("source_code", "") for row in approved)
            == Counter(
                {
                    "src_pl_sandero_brochure_20260202": 40,
                    "src_pl_jogger_brochure_20251217": 242,
                    "src_pl_duster_mini_brochure_20251020": 100,
                }
            ),
            "approved generic dimension source totals differ",
        )
        ensure(not any(row.get("attribute_code") in {"approach_angle", "departure_angle"} for row in approved), "seatback angle was imported as an off-road angle")

def verify_receipts() -> None:
    for checker in CHECKERS:
        ensure(checker.is_file(), f"checker missing: {checker}")
        completed = subprocess.run(
            [sys.executable, str(checker), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        ensure(completed.returncode == 0, completed.stderr or completed.stdout or f"checker failed: {checker}")


def check() -> None:
    verify_report(load_json(REPORT))
    verify_original_review()
    verify_current_coverage()
    verify_non_import_boundaries()
    verify_receipts()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        check()
    except (ClosureError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print("PASS: official brochure technical gap resolution closure review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
