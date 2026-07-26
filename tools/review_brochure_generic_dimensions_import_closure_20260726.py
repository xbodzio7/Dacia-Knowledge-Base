#!/usr/bin/env python3
"""Verify closure of the approved generic brochure dimension import."""

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
REPORT = REPORTING / "brochure_generic_dimensions_import_closure_review.json"
MAPPING = REPORTING / "brochure_generic_dimensions_semantic_mapping_review.json"
RESIDUAL = REPORTING / "official_brochure_residual_evidence_review.json"
EVIDENCE = REPORTING / "configuration_gap_evidence.json"
PLAN = REPORTING / "configuration_gap_resolution_plan.json"

SOURCE_COUNTS = Counter(
    {
        "src_pl_sandero_brochure_20260202": 40,
        "src_pl_jogger_brochure_20251217": 242,
        "src_pl_duster_mini_brochure_20251020": 100,
    }
)
ATTRIBUTE_COUNTS = Counter(
    {
        "overall_length": 36,
        "overall_width": 36,
        "overall_width_with_mirrors": 36,
        "wheelbase": 36,
        "ground_clearance": 36,
        "front_track": 36,
        "rear_track": 36,
        "front_overhang": 36,
        "rear_overhang": 36,
        "overall_height": 26,
        "roof_height_with_rails": 32,
    }
)
DIMENSIONS = set(ATTRIBUTE_COUNTS)
SANDERO_DIMENSIONS = DIMENSIONS - {"roof_height_with_rails"}
DUSTER_DIMENSIONS = DIMENSIONS - {"overall_height"}
REPORTING_SCOPES: dict[str, set[str]] = {
    "sandero_ecog120_manual_completeness.json": SANDERO_DIMENSIONS,
    "sandero_ecog120_automatic_completeness.json": SANDERO_DIMENSIONS,
    "jogger_ecog120_manual_completeness.json": DIMENSIONS,
    "jogger_ecog120_automatic_completeness.json": DIMENSIONS,
    "jogger_tce110_manual_completeness.json": DIMENSIONS,
    "jogger_hybrid155_automatic_completeness.json": DIMENSIONS,
    "duster_ecog120_completeness.json": DUSTER_DIMENSIONS,
    "duster_mildhybrid140_4x2_completeness.json": DUSTER_DIMENSIONS,
    "duster_hybrid155_completeness.json": DUSTER_DIMENSIONS,
}
LATER_SANDERO_CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_journey_ecog120_manual",
}
LATER_SANDERO_ATTRIBUTES = {
    "front_overhang",
    "overall_length",
    "overall_width",
    "rear_overhang",
    "wheelbase",
}
EXPECTED_REVIEW_KEYS = {
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|front_track|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|ground_clearance|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|overall_height|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|overall_width_with_mirrors|none",
    "technical|src_pl_sandero_stepway_extreme_ecog120_at_20260626|sandero_stepway_iii_extreme_ecog120_automatic|Dimensions|rear_track|none",
}
CHECKERS = (
    ROOT / "tools" / "import_brochure_generic_dimensions_20260726.py",
    ROOT / "tools" / "review_brochure_generic_dimensions_semantic_mapping_20260726.py",
    ROOT / "tools" / "review_official_brochure_residual_evidence_20260726.py",
    ROOT / "tools" / "review_official_brochure_technical_gap_resolution_closure_20260726.py",
)


class ClosureError(RuntimeError):
    """Raised when the generic-dimension closure contract drifts."""


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


def package_values() -> list[dict[str, str]]:
    return [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if 2568 <= int(row["id"]) <= 2949
    ]


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported closure review version")
    ensure(
        payload.get("kind") == "brochure_generic_dimensions_import_closure_review",
        "unexpected closure review kind",
    )
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "closure review is not complete")
    ensure(
        payload.get("import_package")
        == {
            "name": "Brochure Generic Dimensions Observation Import",
            "pull_request": 272,
            "merge_sha": "b46248d",
        },
        "import package receipt differs",
    )
    ensure(
        payload.get("totals")
        == {
            "sources": 3,
            "configurations": 36,
            "scalar_values": 382,
            "range_values": 0,
            "new_attributes": 0,
            "reporting_scopes": 9,
            "reporting_slot_entries": 94,
        },
        "closure totals differ",
    )
    ensure(
        Counter(payload.get("source_value_counts", {})) == SOURCE_COUNTS,
        "reported source counts differ",
    )
    ensure(
        Counter(payload.get("attribute_value_counts", {})) == ATTRIBUTE_COUNTS,
        "reported attribute counts differ",
    )
    identity = payload.get("identity_contract")
    ensure(isinstance(identity, dict), "identity contract is missing")
    ensure(
        (identity.get("scalar_id_start"), identity.get("scalar_id_end"))
        == (2568, 2949),
        "scalar ID boundary differs",
    )
    ensure(
        set(identity.get("observation_dates", []))
        == {"2025-10-20", "2025-12-17", "2026-02-02"},
        "observation date contract differs",
    )
    resolution = payload.get("classification_resolution")
    ensure(isinstance(resolution, dict), "classification resolution is missing")
    ensure(
        set(resolution.get("resolved", []))
        == {"sandero_dimensions_and_cargo", "jogger_dimensions_and_cargo"},
        "resolved classification set differs",
    )
    ensure(
        resolution.get("partially_resolved")
        == ["duster_wltp_placeholders_and_dimensions"],
        "partial classification set differs",
    )
    boundaries = payload.get("preserved_boundaries")
    ensure(isinstance(boundaries, list) and len(boundaries) == 4, "expected four boundaries")
    ensure(
        {str(item.get("code", "")) for item in boundaries}
        == {
            "duster_4x4_dimensions_without_exact_source_relationship",
            "duster_wltp_placeholders",
            "contextual_cargo_model",
            "excluded_diagram_measurements",
        },
        "preserved boundary set differs",
    )
    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(
        next_package.get("name") == "Post-Brochure Priority Selection Review",
        "next package differs",
    )


def verify_values(values: Sequence[dict[str, str]]) -> None:
    ensure(len(values) == 382, "expected exactly 382 package values")
    ensure([int(row["id"]) for row in values] == list(range(2568, 2950)), "IDs differ")
    ensure(len({row["code"] for row in values}) == 382, "value codes are not unique")
    ensure(Counter(row["source_code"] for row in values) == SOURCE_COUNTS, "source counts differ")
    ensure(
        Counter(row["attribute_code"] for row in values) == ATTRIBUTE_COUNTS,
        "attribute counts differ",
    )
    ensure(
        {row["observation_date"] for row in values}
        == {"2025-10-20", "2025-12-17", "2026-02-02"},
        "package dates differ",
    )
    ensure(len({row["configuration_code"] for row in values}) == 36, "configuration count differs")
    ensure({row["fuel_type_code"] for row in values} == {""}, "unexpected fuel context")
    ensure({row["gear_number"] for row in values} == {""}, "unexpected gear context")
    ensure(
        not any(row["attribute_code"] in {"approach_angle", "departure_angle"} for row in values),
        "seatback angle was imported as an off-road angle",
    )

    attributes = {row["code"]: row for row in rows(MASTER / "attributes.csv")}
    for code in DIMENSIONS:
        attribute = attributes.get(code)
        ensure(attribute is not None, f"missing dimension attribute: {code}")
        ensure(attribute.get("data_type") == "integer", f"dimension type differs: {code}")
        ensure(attribute.get("unit") == "mm", f"dimension unit differs: {code}")
        ensure(attribute.get("status") == "active", f"dimension status differs: {code}")

    configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}
    by_source: dict[str, set[str]] = {}
    for source in SOURCE_COUNTS:
        by_source[source] = {
            row["configuration_code"] for row in values if row["source_code"] == source
        }
    ensure(len(by_source["src_pl_sandero_brochure_20260202"]) == 4, "Sandero scope differs")
    ensure(len(by_source["src_pl_jogger_brochure_20251217"]) == 22, "Jogger scope differs")
    duster = by_source["src_pl_duster_mini_brochure_20251020"]
    ensure(len(duster) == 10, "Duster scope differs")
    ensure(
        all("4x2" in configurations[code].get("powertrain_label", "") for code in duster),
        "Duster 4x4 configuration entered the package",
    )


def verify_reporting() -> None:
    slot_entries = 0
    for filename, required in REPORTING_SCOPES.items():
        payload = load_json(REPORTING / filename)
        slots = {
            item.get("attribute_code", "")
            for item in payload.get("technical_slots", [])
            if isinstance(item, dict) and item.get("fuel_type_code", "") == ""
        }
        ensure(required <= slots, f"reporting scope is missing dimensions: {filename}")
        slot_entries += len(required)
    ensure(len(REPORTING_SCOPES) == 9, "reporting scope count differs")
    ensure(slot_entries == 94, "reporting slot entry total differs")


def verify_latest_precedence(values: Sequence[dict[str, str]]) -> None:
    master_values = rows(MASTER / "configuration_attribute_values.csv")
    historical = [
        row
        for row in values
        if row["configuration_code"] in LATER_SANDERO_CONFIGURATIONS
        and row["attribute_code"] in LATER_SANDERO_ATTRIBUTES
    ]
    later = [
        row
        for row in master_values
        if row["configuration_code"] in LATER_SANDERO_CONFIGURATIONS
        and row["attribute_code"] in LATER_SANDERO_ATTRIBUTES
        and row["observation_date"] == "2026-06-26"
    ]
    ensure(len(historical) == 10, "historical Sandero precedence rows differ")
    ensure(len(later) == 10, "later exact Sandero precedence rows differ")
    ensure({row["observation_date"] for row in historical} == {"2026-02-02"}, "historical date differs")
    ensure(
        {
            (row["configuration_code"], row["attribute_code"])
            for row in historical
        }
        == {
            (row["configuration_code"], row["attribute_code"])
            for row in later
        },
        "later exact Sandero semantic keys differ",
    )


def verify_evidence() -> None:
    evidence = load_json(EVIDENCE)
    selected = {
        item["triage_key"]: item
        for item in evidence.get("decisions", [])
        if isinstance(item, dict) and item.get("triage_key") in EXPECTED_REVIEW_KEYS
    }
    ensure(set(selected) == EXPECTED_REVIEW_KEYS, "reviewed evidence key set differs")
    ensure(all(item.get("reviewed_pages") == [2] for item in selected.values()), "reviewed pages differ")
    ensure(all(item.get("classification") == "not_stated" for item in selected.values()), "evidence classification differs")

    plan = load_json(PLAN)
    planned = {
        item["triage_key"]: item
        for item in plan.get("decisions", [])
        if isinstance(item, dict) and item.get("triage_key") in EXPECTED_REVIEW_KEYS
    }
    ensure(set(planned) == EXPECTED_REVIEW_KEYS, "planned evidence key set differs")
    ensure(all(item.get("reviewed_pages") == [2] for item in planned.values()), "planned reviewed pages differ")
    ensure(
        all(item.get("resolution_state") == "closed_not_stated" for item in planned.values()),
        "planned resolution state differs",
    )


def verify_receipts_and_boundaries(values: Sequence[dict[str, str]]) -> None:
    mapping = load_json(MAPPING)
    receipt = mapping.get("import_receipt")
    ensure(isinstance(receipt, dict), "mapping import receipt is missing")
    ensure(receipt.get("status") == "imported", "mapping receipt status differs")
    ensure(receipt.get("scalar_values") == 382, "mapping receipt scalar count differs")
    ensure(
        receipt.get("duster_4x4_status") == "deferred_without_exact_source_relationship",
        "Duster 4x4 receipt boundary differs",
    )
    ensure(mapping.get("import_plan", {}).get("duster_4x4_scalar_values") == 0, "Duster 4x4 import plan differs")
    ensure(mapping.get("import_plan", {}).get("scalar_values") == 382, "mapping import plan total differs")
    ensure(len(mapping.get("excluded_visual_values", [])) == 3, "excluded visual source count differs")
    ensure(
        all(14 in item.get("values", []) for item in mapping.get("excluded_visual_values", [])),
        "seatback-angle exclusion differs",
    )

    residual = load_json(RESIDUAL)
    follow_up = residual.get("follow_up_import_receipt")
    ensure(isinstance(follow_up, dict), "residual follow-up receipt is missing")
    ensure(follow_up.get("scalar_values") == 382, "residual receipt scalar count differs")
    ensure(
        set(follow_up.get("resolved_classifications", []))
        == {"sandero_dimensions_and_cargo", "jogger_dimensions_and_cargo"},
        "residual resolved classification set differs",
    )
    ensure(
        follow_up.get("partially_resolved_classifications")
        == ["duster_wltp_placeholders_and_dimensions"],
        "residual partial classification set differs",
    )

    jogger_mass_attributes = {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"}
    all_values = rows(MASTER / "configuration_attribute_values.csv")
    ensure(
        not any(
            row["source_code"] == "src_pl_jogger_brochure_20251217"
            and row["attribute_code"] in jogger_mass_attributes
            for row in all_values
        ),
        "ambiguous Jogger mass evidence was imported",
    )
    ensure(len(values) == 382, "package value count changed during boundary checks")


def verify_checkers() -> None:
    for path in CHECKERS:
        completed = subprocess.run(
            [sys.executable, str(path), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        ensure(
            completed.returncode == 0,
            f"checker failed: {path.name}: {completed.stderr or completed.stdout}",
        )


def verify_state() -> None:
    state = load_json(ROOT / "project" / "state.json")
    ensure(state.get("phase") == "Brochure Generic Dimensions Import Closure Review", "project phase differs")
    current = state.get("current_package")
    ensure(isinstance(current, dict), "current package is missing")
    ensure(current.get("name") == "Brochure Generic Dimensions Import Closure Review", "current package differs")
    ensure(current.get("status") == "complete", "current package status differs")
    next_package = state.get("next_package")
    ensure(isinstance(next_package, dict), "next state package is missing")
    ensure(next_package.get("name") == "Post-Brochure Priority Selection Review", "next state package differs")
    baseline = state.get("baseline")
    ensure(isinstance(baseline, dict), "state baseline is missing")
    ensure(baseline.get("tests") == 955, "state test baseline differs")
    ensure(baseline.get("rows") == 9688, "state row baseline differs")
    ensure(baseline.get("configuration_values") == 2949, "state value baseline differs")
    ensure(baseline.get("configuration_value_ranges") == 244, "state range baseline differs")
    ensure(baseline.get("attributes") == 385, "state attribute baseline differs")


def check() -> None:
    payload = load_json(REPORT)
    values = package_values()
    verify_report(payload)
    verify_values(values)
    verify_reporting()
    verify_latest_precedence(values)
    verify_evidence()
    verify_receipts_and_boundaries(values)
    verify_checkers()
    verify_state()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the closure contract")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.check:
        raise ClosureError("only --check is supported")
    check()
    print("PASS: brochure generic dimensions import closure review")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ClosureError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
