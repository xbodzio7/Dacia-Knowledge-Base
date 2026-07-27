#!/usr/bin/env python3
"""Verify the accepted brochure chassis measurement context model."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORT = ROOT / "data" / "reporting" / "brochure_chassis_measurement_context_model.json"
DECISIONS = ROOT / "project" / "DECISIONS.md"

EXPECTED_NEW_ATTRIBUTES = {
    "turning_circle_between_kerbs": {
        "id": "389",
        "category": "Performance",
        "data_type": "decimal",
        "unit": "m",
        "status": "active",
    },
    "turning_circle_wheel_track": {
        "id": "390",
        "category": "Performance",
        "data_type": "decimal",
        "unit": "m",
        "status": "active",
    },
    "maximum_kerb_weight": {
        "id": "391",
        "category": "Weights",
        "data_type": "integer",
        "unit": "kg",
        "status": "active",
    },
    "payload": {
        "id": "392",
        "category": "Weights",
        "data_type": "integer",
        "unit": "kg",
        "status": "active",
    },
}

EXPECTED_EXISTING_ATTRIBUTES = {
    "standard_tyre_specification": ("string", ""),
    "front_suspension": ("string", ""),
    "rear_suspension": ("string", ""),
    "front_brake_type": ("string", ""),
    "rear_brake_type": ("string", ""),
    "steering_type": ("string", ""),
    "turning_circle": ("decimal", "m"),
    "minimum_kerb_weight": ("integer", "kg"),
    "maximum_payload": ("integer", "kg"),
}

HISTORICAL_SCALAR_SOURCES = {
    "src_pl_bigster_brochure_20251210",
    "src_pl_duster_mini_brochure_20251020",
    "src_pl_jogger_brochure_20251217",
    "src_pl_sandero_brochure_20260202",
    "src_pl_sandero_stepway_brochure_20260202",
}

EXPECTED_CLASSIFICATIONS = {
    "bigster_chassis_measurement_modeling",
    "jogger_chassis_candidate_and_modeling",
    "sandero_chassis_and_maximum_mass_modeling",
    "stepway_chassis_and_maximum_mass_modeling",
    "duster_chassis_mass_and_payload_modeling",
}


class ModelError(RuntimeError):
    """Raised when the accepted model drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ModelError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def load_report() -> dict[str, Any]:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), "report must be a JSON object")
    return payload


def verify_report(payload: dict[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported model version")
    ensure(payload.get("kind") == "brochure_chassis_measurement_context_model", "unexpected report kind")
    ensure(payload.get("decided_on") == "2026-07-26", "unexpected decision date")
    ensure(payload.get("status") == "accepted", "model is not accepted")
    ensure(payload.get("decision_reference") == "D-016", "decision reference differs")
    ensure(payload.get("selected_variant") == "separate_unambiguous_attributes", "selected variant differs")

    scope = payload.get("scope")
    ensure(isinstance(scope, dict) and scope.get("sources") == 5, "scope must cover five brochure sources")
    ensure(set(scope.get("classification_codes", [])) == EXPECTED_CLASSIFICATIONS, "classification scope differs")

    attributes = payload.get("new_attributes")
    ensure(isinstance(attributes, list) and len(attributes) == 4, "model must define four new attributes")
    report_codes = {str(item.get("code", "")) for item in attributes if isinstance(item, dict)}
    ensure(report_codes == set(EXPECTED_NEW_ATTRIBUTES), "new attribute codes differ")

    rules = payload.get("rules")
    ensure(isinstance(rules, list) and len(rules) == 6, "model must define six semantic rules")
    ensure(len({str(item.get("code", "")) for item in rules if isinstance(item, dict)}) == 6, "rule codes differ")

    resolutions = payload.get("source_resolutions")
    ensure(isinstance(resolutions, list) and len(resolutions) == 5, "source resolution count differs")
    ensure({str(item.get("classification_code", "")) for item in resolutions if isinstance(item, dict)} == EXPECTED_CLASSIFICATIONS, "source resolutions differ")
    expected_statuses = {
        "bigster_chassis_measurement_modeling": "imported",
        "jogger_chassis_candidate_and_modeling": "imported",
        "sandero_chassis_and_maximum_mass_modeling": "imported",
        "stepway_chassis_and_maximum_mass_modeling": "imported",
        "duster_chassis_mass_and_payload_modeling": "imported",
    }
    ensure(
        {str(item.get("classification_code", "")): str(item.get("status", "")) for item in resolutions}
        == expected_statuses,
        "resolution status differs",
    )

    by_code = {str(item.get("classification_code", "")): item for item in resolutions}
    ensure(by_code["duster_chassis_mass_and_payload_modeling"].get("turning_attribute") == "turning_circle_wheel_track", "Duster turning basis differs")
    for code in EXPECTED_CLASSIFICATIONS - {"duster_chassis_mass_and_payload_modeling"}:
        ensure(by_code[code].get("turning_attribute") == "turning_circle_between_kerbs", f"between-kerbs mapping differs: {code}")
    ensure(by_code["duster_chassis_mass_and_payload_modeling"].get("range_attribute") == "payload", "Duster payload mapping differs")
    ensure(by_code["jogger_chassis_candidate_and_modeling"].get("blocked_related_classification") == "jogger_mass_table_label_conflict", "Jogger ambiguity boundary differs")

    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Brochure Chassis Modeling Closure Review", "next package differs")


def verify_attributes(payload: dict[str, Any]) -> None:
    catalogue = {row["code"]: row for row in rows(MASTER / "attributes.csv")}
    report_attributes = {str(item["code"]): item for item in payload["new_attributes"]}

    for code, expected in EXPECTED_NEW_ATTRIBUTES.items():
        row = catalogue.get(code)
        ensure(row is not None, f"new attribute missing: {code}")
        for field, value in expected.items():
            ensure(row.get(field) == value, f"{code}.{field} differs")
        report = report_attributes[code]
        for field in ("id", "category", "name", "data_type", "unit", "description", "status"):
            ensure(str(report.get(field, "")) == row.get(field, ""), f"report/catalogue mismatch: {code}.{field}")

    for code, (data_type, unit) in EXPECTED_EXISTING_ATTRIBUTES.items():
        row = catalogue.get(code)
        ensure(row is not None and row.get("status") == "active", f"active existing attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit")) == (data_type, unit), f"existing attribute contract differs: {code}")


def verify_decision() -> None:
    text = DECISIONS.read_text(encoding="utf-8")
    ensure(text.count("## D-016 — Brochure chassis measurement context") == 1, "D-016 heading missing or duplicated")
    for token in (
        "turning_circle_between_kerbs",
        "turning_circle_wheel_track",
        "maximum_kerb_weight",
        "payload",
        "configuration_attribute_value_ranges.csv",
    ):
        ensure(token in text, f"D-016 omits {token}")


def verify_model_only_boundary() -> None:
    new_codes = set(EXPECTED_NEW_ATTRIBUTES)
    scalar = [
        row
        for row in rows(MASTER / "configuration_attribute_values.csv")
        if row.get("attribute_code") in new_codes
        and row.get("source_code") in HISTORICAL_SCALAR_SOURCES
    ]
    ranges = [row for row in rows(MASTER / "configuration_attribute_value_ranges.csv") if row.get("attribute_code") in new_codes]
    ensure(len(scalar) == 88, "expected eighty-eight modeled scalar chassis observations")
    ensure(
        {row.get("attribute_code") for row in scalar}
        == {
            "turning_circle_between_kerbs",
            "turning_circle_wheel_track",
            "maximum_kerb_weight",
        },
        "modeled scalar attribute set differs",
    )
    ensure(
        {row.get("source_code") for row in scalar}
        == HISTORICAL_SCALAR_SOURCES,
        "modeled scalar source set differs",
    )
    ensure(
        {row.get("observation_date") for row in scalar}
        == {"2025-10-20", "2025-12-10", "2025-12-17", "2026-02-02"},
        "modeled scalar dates differ",
    )
    ensure(len(ranges) == 10, "expected ten modeled payload ranges")
    ensure({row.get("attribute_code") for row in ranges} == {"payload"}, "modeled range attribute differs")
    ensure({row.get("source_code") for row in ranges} == {"src_pl_duster_mini_brochure_20251020"}, "modeled range source differs")
    ensure({row.get("observation_date") for row in ranges} == {"2025-10-20"}, "modeled range date differs")


def verify() -> None:
    payload = load_report()
    verify_report(payload)
    verify_attributes(payload)
    verify_decision()
    verify_model_only_boundary()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the committed model")
    parser.parse_args()
    try:
        verify()
    except (ModelError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}")
        return 1
    print("PASS: brochure chassis measurement context model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
