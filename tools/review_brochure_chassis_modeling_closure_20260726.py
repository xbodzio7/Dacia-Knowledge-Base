#!/usr/bin/env python3
"""Verify closure of the D-016 official brochure chassis modeling milestone."""

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
REPORT = REPORTING / "brochure_chassis_modeling_closure_review.json"
MODEL = REPORTING / "brochure_chassis_measurement_context_model.json"
GAP_REVIEW = REPORTING / "official_brochure_technical_gap_review.json"
DECISIONS = ROOT / "project" / "DECISIONS.md"

SOURCE_CONTRACTS: dict[str, dict[str, Any]] = {
    "src_pl_sandero_brochure_20260202": {
        "configurations": 4,
        "scalar_values": 20,
        "attributes": {
            "turning_circle_between_kerbs",
            "maximum_kerb_weight",
            "standard_tyre_specification",
            "front_suspension",
            "rear_suspension",
        },
    },
    "src_pl_sandero_stepway_brochure_20260202": {
        "configurations": 5,
        "scalar_values": 25,
        "attributes": {
            "turning_circle_between_kerbs",
            "maximum_kerb_weight",
            "standard_tyre_specification",
            "front_suspension",
            "rear_suspension",
        },
    },
    "src_pl_bigster_brochure_20251210": {
        "configurations": 14,
        "scalar_values": 84,
        "attributes": {
            "turning_circle_between_kerbs",
            "maximum_kerb_weight",
            "steering_type",
            "front_brake_type",
            "rear_brake_type",
            "standard_tyre_specification",
        },
    },
    "src_pl_duster_mini_brochure_20251020": {
        "configurations": 10,
        "scalar_values": 60,
        "attributes": {
            "turning_circle_wheel_track",
            "maximum_kerb_weight",
            "steering_type",
            "front_brake_type",
            "rear_brake_type",
            "standard_tyre_specification",
        },
    },
    "src_pl_jogger_brochure_20251217": {
        "configurations": 22,
        "scalar_values": 88,
        "attributes": {
            "turning_circle_between_kerbs",
            "standard_tyre_specification",
            "front_suspension",
            "rear_suspension",
        },
    },
}

EXPECTED_SCALAR_COUNTS = Counter(
    {
        "turning_circle_between_kerbs": 45,
        "turning_circle_wheel_track": 10,
        "maximum_kerb_weight": 33,
        "standard_tyre_specification": 55,
        "front_suspension": 31,
        "rear_suspension": 31,
        "steering_type": 24,
        "front_brake_type": 24,
        "rear_brake_type": 24,
    }
)
EXPECTED_DATES = {"2025-10-20", "2025-12-10", "2025-12-17", "2026-02-02"}
EXPECTED_MODEL_CLASSIFICATIONS = {
    "bigster_chassis_measurement_modeling",
    "jogger_chassis_candidate_and_modeling",
    "sandero_chassis_and_maximum_mass_modeling",
    "stepway_chassis_and_maximum_mass_modeling",
    "duster_chassis_mass_and_payload_modeling",
}

REPORTING_SCOPES: dict[str, set[str]] = {
    "configuration_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
    "sandero_ecog120_automatic_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
    "sandero_ecog120_manual_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
    "sandero_stepway_ecog120_automatic_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
    "bigster_hybrid155_4x2_automatic_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "steering_type",
        "front_brake_type",
        "rear_brake_type",
        "standard_tyre_specification",
    },
    "bigster_hybridg150_4x4_automatic_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "steering_type",
        "front_brake_type",
        "rear_brake_type",
        "standard_tyre_specification",
    },
    "bigster_mildhybrid140_4x2_manual_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "steering_type",
        "front_brake_type",
        "rear_brake_type",
        "standard_tyre_specification",
    },
    "bigster_mildhybridg140_4x2_manual_completeness.json": {
        "turning_circle_between_kerbs",
        "maximum_kerb_weight",
        "steering_type",
        "front_brake_type",
        "rear_brake_type",
        "standard_tyre_specification",
    },
    "duster_ecog120_completeness.json": {
        "turning_circle_wheel_track",
        "maximum_kerb_weight",
        "payload",
        "steering_type",
        "front_brake_type",
        "rear_brake_type",
        "standard_tyre_specification",
    },
    "duster_mildhybrid140_4x2_completeness.json": {
        "turning_circle_wheel_track",
        "maximum_kerb_weight",
        "payload",
        "steering_type",
        "front_brake_type",
        "rear_brake_type",
        "standard_tyre_specification",
    },
    "duster_hybrid155_completeness.json": {
        "turning_circle_wheel_track",
        "maximum_kerb_weight",
        "payload",
        "steering_type",
        "front_brake_type",
        "rear_brake_type",
        "standard_tyre_specification",
    },
    "jogger_ecog120_automatic_completeness.json": {
        "turning_circle_between_kerbs",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
    "jogger_ecog120_manual_completeness.json": {
        "turning_circle_between_kerbs",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
    "jogger_hybrid155_automatic_completeness.json": {
        "turning_circle_between_kerbs",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
    "jogger_tce110_manual_completeness.json": {
        "turning_circle_between_kerbs",
        "standard_tyre_specification",
        "front_suspension",
        "rear_suspension",
    },
}

CHECKERS = (
    ROOT / "tools" / "import_sandero_stepway_chassis_20260726.py",
    ROOT / "tools" / "import_bigster_chassis_20260726.py",
    ROOT / "tools" / "import_duster_chassis_20260726.py",
    ROOT / "tools" / "import_jogger_chassis_20260726.py",
    ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py",
)


class ClosureError(RuntimeError):
    """Raised when the chassis closure contract drifts."""


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


def reviewed_scalar_values() -> list[dict[str, str]]:
    source_attributes = {
        source: set(contract["attributes"])
        for source, contract in SOURCE_CONTRACTS.items()
    }
    return [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("source_code") in source_attributes
        and row.get("attribute_code") in source_attributes[row["source_code"]]
    ]


def reviewed_ranges() -> list[dict[str, str]]:
    return [
        row
        for row in rows(MASTER / "configuration_attribute_value_ranges.csv")
        if row.get("source_code") == "src_pl_duster_mini_brochure_20251020"
        and row.get("attribute_code") == "payload"
    ]


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported closure review version")
    ensure(payload.get("kind") == "brochure_chassis_modeling_closure_review", "unexpected closure review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "closure review is not complete")
    ensure(payload.get("decision_reference") == "D-016", "decision reference differs")
    ensure(payload.get("selected_variant") == "separate_unambiguous_attributes", "selected variant differs")

    packages = payload.get("packages")
    ensure(isinstance(packages, list) and len(packages) == 4, "expected four import packages")
    ensure(sum(int(item.get("configurations", 0)) for item in packages) == 55, "package configuration total differs")
    ensure(sum(int(item.get("scalar_values", 0)) for item in packages) == 277, "package scalar total differs")
    ensure(sum(int(item.get("range_values", 0)) for item in packages) == 10, "package range total differs")
    ensure({int(item.get("pull_request", 0)) for item in packages} == {264, 265, 266, 267}, "package PR set differs")

    totals = payload.get("totals")
    ensure(
        totals
        == {
            "sources": 5,
            "configurations": 55,
            "scalar_values": 277,
            "range_values": 10,
            "new_attributes": 4,
            "reporting_scopes": 15,
        },
        "closure totals differ",
    )
    ensure(Counter(payload.get("scalar_attribute_counts", {})) == EXPECTED_SCALAR_COUNTS, "reported scalar counts differ")
    ensure(payload.get("range_attribute_counts") == {"payload": 10}, "reported range counts differ")

    identity = payload.get("identity_contract")
    ensure(isinstance(identity, dict), "identity contract is missing")
    ensure((identity.get("scalar_id_start"), identity.get("scalar_id_end")) == (2291, 2567), "scalar ID boundary differs")
    ensure((identity.get("range_id_start"), identity.get("range_id_end")) == (235, 244), "range ID boundary differs")
    ensure(set(identity.get("observation_dates", [])) == EXPECTED_DATES, "reported observation dates differ")

    unresolved = payload.get("unresolved_evidence")
    ensure(isinstance(unresolved, list) and len(unresolved) == 1, "expected one unresolved evidence item")
    ensure(unresolved[0].get("code") == "jogger_mass_table_label_conflict", "unresolved evidence code differs")
    ensure(unresolved[0].get("status") == "ambiguous_source_evidence", "unresolved evidence status differs")

    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Official Brochure Technical Gap Resolution Closure Review", "next package differs")


def verify_scalar_values(values: Sequence[dict[str, str]]) -> None:
    ensure(len(values) == 277, "expected exactly 277 chassis scalar values")
    ensure(len({row.get("code", "") for row in values}) == 277, "chassis scalar codes are not unique")
    ensure([int(row["id"]) for row in values] == list(range(2291, 2568)), "chassis scalar IDs are not contiguous")
    ensure(Counter(row.get("attribute_code", "") for row in values) == EXPECTED_SCALAR_COUNTS, "master scalar counts differ")
    ensure({row.get("observation_date", "") for row in values} == EXPECTED_DATES, "master scalar dates differ")
    ensure(len({row.get("configuration_code", "") for row in values}) == 55, "expected 55 exact chassis configurations")

    configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}
    ensure(
        all(configurations.get(row.get("configuration_code", ""), {}).get("status") == "active" for row in values),
        "chassis scalar targets an inactive or unknown configuration",
    )

    for source_code, contract in SOURCE_CONTRACTS.items():
        selected = [row for row in values if row.get("source_code") == source_code]
        ensure(len(selected) == contract["scalar_values"], f"source scalar total differs: {source_code}")
        ensure(len({row.get("configuration_code", "") for row in selected}) == contract["configurations"], f"source configuration total differs: {source_code}")
        ensure({row.get("attribute_code", "") for row in selected} == contract["attributes"], f"source attribute set differs: {source_code}")


def verify_ranges(values: Sequence[dict[str, str]]) -> None:
    ensure(len(values) == 10, "expected exactly ten Duster payload ranges")
    ensure([int(row["id"]) for row in values] == list(range(235, 245)), "payload range IDs are not contiguous")
    ensure(len({row.get("configuration_code", "") for row in values}) == 10, "payload range configuration total differs")
    ensure({row.get("attribute_code", "") for row in values} == {"payload"}, "payload range attribute differs")
    ensure({row.get("observation_date", "") for row in values} == {"2025-10-20"}, "payload range date differs")
    ensure(all(row.get("lower_inclusive") == "true" and row.get("upper_inclusive") == "true" for row in values), "payload range is not closed")
    ensure(all(float(row["minimum_value"]) <= float(row["maximum_value"]) for row in values), "payload range endpoints are reversed")


def verify_source_relationships(values: Sequence[dict[str, str]]) -> None:
    relationships = rows(MASTER / "source_configurations.csv")
    by_source = {
        source_code: {
            row.get("configuration_code", "")
            for row in relationships
            if row.get("source_code") == source_code and row.get("relationship") == "brochure_technical_data_for"
        }
        for source_code in SOURCE_CONTRACTS
    }
    value_targets = {
        source_code: {
            row.get("configuration_code", "")
            for row in values
            if row.get("source_code") == source_code
        }
        for source_code in SOURCE_CONTRACTS
    }
    ensure(by_source == value_targets, "brochure source relationships differ from imported chassis targets")


def verify_model_and_decision() -> None:
    model = load_json(MODEL)
    ensure(model.get("decision_reference") == "D-016", "model decision reference differs")
    ensure(model.get("selected_variant") == "separate_unambiguous_attributes", "model variant differs")
    resolutions = model.get("source_resolutions")
    ensure(isinstance(resolutions, list) and len(resolutions) == 5, "model resolution count differs")
    by_code = {str(item.get("classification_code", "")): item for item in resolutions if isinstance(item, dict)}
    ensure(set(by_code) == EXPECTED_MODEL_CLASSIFICATIONS, "model classification set differs")
    ensure({str(item.get("status", "")) for item in by_code.values()} == {"imported"}, "not all model classifications are imported")
    jogger = by_code["jogger_chassis_candidate_and_modeling"]
    ensure(jogger.get("blocked_related_classification") == "jogger_mass_table_label_conflict", "Jogger conflict boundary differs")
    ensure(model.get("next_package", {}).get("name") == "Brochure Chassis Modeling Closure Review", "model handoff differs")

    text = DECISIONS.read_text(encoding="utf-8")
    ensure(text.count("## D-016 — Brochure chassis measurement context") == 1, "D-016 heading missing or duplicated")


def verify_ambiguous_boundary() -> None:
    gap = load_json(GAP_REVIEW)
    classifications = {
        str(item.get("code", "")): item
        for item in gap.get("classifications", [])
        if isinstance(item, dict)
    }
    conflict = classifications.get("jogger_mass_table_label_conflict")
    ensure(isinstance(conflict, dict), "Jogger mass conflict classification is missing")
    ensure(conflict.get("status") == "ambiguous_source_evidence", "Jogger mass conflict status differs")
    ensure(
        set(conflict.get("attributes", [])) == {"maximum_kerb_weight", "gross_train_weight", "gross_vehicle_weight"},
        "Jogger mass conflict attributes differ",
    )

    forbidden = {
        "maximum_kerb_weight",
        "gross_train_weight",
    }
    imported = [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("source_code") == "src_pl_jogger_brochure_20251217"
        and row.get("attribute_code") in forbidden
    ]
    ensure(imported == [], "ambiguous Jogger mass values were imported")


def verify_reporting_scopes() -> None:
    ensure(len(REPORTING_SCOPES) == 15, "expected fifteen reporting scopes")
    for filename, required in REPORTING_SCOPES.items():
        payload = load_json(REPORTING / filename)
        slots = {
            str(item.get("attribute_code", ""))
            for item in payload.get("technical_slots", [])
            if isinstance(item, dict)
        }
        ensure(required <= slots, f"chassis reporting slots missing: {filename}")


def verify_import_receipts() -> None:
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
    payload = load_json(REPORT)
    verify_report(payload)
    scalar = reviewed_scalar_values()
    ranges = reviewed_ranges()
    verify_scalar_values(scalar)
    verify_ranges(ranges)
    verify_source_relationships(scalar)
    verify_model_and_decision()
    verify_ambiguous_boundary()
    verify_reporting_scopes()
    verify_import_receipts()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        check()
    except (ClosureError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print("PASS: brochure chassis modeling closure review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
