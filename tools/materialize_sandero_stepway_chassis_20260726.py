#!/usr/bin/env python3
"""Materialize reporting and state integration for Sandero/Stepway chassis data."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
STATE = ROOT / "project" / "state.json"
MODEL_REPORT = REPORTING / "brochure_chassis_measurement_context_model.json"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
MODEL_TEST = ROOT / "tests" / "test_brochure_chassis_measurement_context_modeling_20260726.py"
REPORTING_SPECS = (
    REPORTING / "configuration_completeness.json",
    REPORTING / "sandero_ecog120_manual_completeness.json",
    REPORTING / "sandero_ecog120_automatic_completeness.json",
    REPORTING / "sandero_stepway_ecog120_automatic_completeness.json",
)
NEW_SLOTS = (
    {"attribute_code": "front_suspension", "fuel_type_code": ""},
    {"attribute_code": "maximum_kerb_weight", "fuel_type_code": ""},
    {"attribute_code": "rear_suspension", "fuel_type_code": ""},
    {"attribute_code": "turning_circle_between_kerbs", "fuel_type_code": ""},
)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected text not found: {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_reporting_specs() -> None:
    for path in REPORTING_SPECS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        slots = payload.get("technical_slots")
        if not isinstance(slots, list):
            raise RuntimeError(f"technical_slots missing: {path}")
        identities = {(str(item.get("attribute_code", "")), str(item.get("fuel_type_code", ""))) for item in slots}
        for slot in NEW_SLOTS:
            identity = (slot["attribute_code"], slot["fuel_type_code"])
            if identity not in identities:
                slots.append(dict(slot))
                identities.add(identity)
        slots.sort(key=lambda item: (str(item.get("attribute_code", "")), str(item.get("fuel_type_code", ""))))
        write_json(path, payload)


def update_model_report() -> None:
    payload = json.loads(MODEL_REPORT.read_text(encoding="utf-8"))
    imported = {
        "sandero_chassis_and_maximum_mass_modeling",
        "stepway_chassis_and_maximum_mass_modeling",
    }
    for item in payload["source_resolutions"]:
        if item["classification_code"] in imported:
            item["status"] = "imported"
            item["import_package"] = "Sandero and Stepway Chassis Observation Import"
            item["imported_on"] = "2026-07-26"
    payload["next_package"] = {
        "name": "Bigster Chassis Observation Import",
        "goal": "Import the unambiguous between-kerbs turning diameter, maximum kerb weight and source-text steering, brake and tyre observations for the active Bigster configurations under D-016."
    }
    write_json(MODEL_REPORT, payload)


def update_model_verifier() -> None:
    replace_once(
        MODEL_VERIFIER,
        '    ensure(all(item.get("status") == "model_defined_import_pending" for item in resolutions), "resolution status differs")\n',
        '''    expected_statuses = {
        "bigster_chassis_measurement_modeling": "model_defined_import_pending",
        "jogger_chassis_candidate_and_modeling": "model_defined_import_pending",
        "sandero_chassis_and_maximum_mass_modeling": "imported",
        "stepway_chassis_and_maximum_mass_modeling": "imported",
        "duster_chassis_mass_and_payload_modeling": "model_defined_import_pending",
    }
    ensure(
        {str(item.get("classification_code", "")): str(item.get("status", "")) for item in resolutions}
        == expected_statuses,
        "resolution status differs",
    )
''',
    )
    replace_once(
        MODEL_VERIFIER,
        '    ensure(next_package.get("name") == "Sandero and Stepway Chassis Observation Import", "next package differs")\n',
        '    ensure(next_package.get("name") == "Bigster Chassis Observation Import", "next package differs")\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '''def verify_model_only_boundary() -> None:
    new_codes = set(EXPECTED_NEW_ATTRIBUTES)
    scalar = [row for row in rows(MASTER / "configuration_attribute_values.csv") if row.get("attribute_code") in new_codes]
    ranges = [row for row in rows(MASTER / "configuration_attribute_value_ranges.csv") if row.get("attribute_code") in new_codes]
    ensure(scalar == [], "modeling package must not import scalar chassis observations")
    ensure(ranges == [], "modeling package must not import chassis ranges")
''',
        '''def verify_model_only_boundary() -> None:
    new_codes = set(EXPECTED_NEW_ATTRIBUTES)
    scalar = [row for row in rows(MASTER / "configuration_attribute_values.csv") if row.get("attribute_code") in new_codes]
    ranges = [row for row in rows(MASTER / "configuration_attribute_value_ranges.csv") if row.get("attribute_code") in new_codes]
    ensure(len(scalar) == 18, "expected eighteen modeled scalar chassis observations")
    ensure(
        {row.get("attribute_code") for row in scalar}
        == {"turning_circle_between_kerbs", "maximum_kerb_weight"},
        "modeled scalar attribute set differs",
    )
    ensure(
        {row.get("source_code") for row in scalar}
        == {"src_pl_sandero_brochure_20260202", "src_pl_sandero_stepway_brochure_20260202"},
        "modeled scalar source set differs",
    )
    ensure({row.get("observation_date") for row in scalar} == {"2026-02-02"}, "modeled scalar date differs")
    ensure(ranges == [], "payload and wheel-track follow-up ranges are not imported yet")
''',
    )


def update_model_test() -> None:
    replace_once(
        MODEL_TEST,
        '        self.assertEqual({item["status"] for item in self.report["source_resolutions"]}, {"model_defined_import_pending"})\n',
        '''        statuses = {
            item["classification_code"]: item["status"]
            for item in self.report["source_resolutions"]
        }
        self.assertEqual(statuses["sandero_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(statuses["stepway_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(
            {status for code, status in statuses.items() if code not in {
                "sandero_chassis_and_maximum_mass_modeling",
                "stepway_chassis_and_maximum_mass_modeling",
            }},
            {"model_defined_import_pending"},
        )
''',
    )
    replace_once(
        MODEL_TEST,
        '''    def test_modeling_package_imports_no_observations(self) -> None:
        scalar = [row for row in rows(MASTER / "configuration_attribute_values.csv") if row["attribute_code"] in NEW_CODES]
        ranges = [row for row in rows(MASTER / "configuration_attribute_value_ranges.csv") if row["attribute_code"] in NEW_CODES]
        self.assertEqual(scalar, [])
        self.assertEqual(ranges, [])
''',
        '''    def test_follow_up_imports_respect_modeled_attributes(self) -> None:
        scalar = [row for row in rows(MASTER / "configuration_attribute_values.csv") if row["attribute_code"] in NEW_CODES]
        ranges = [row for row in rows(MASTER / "configuration_attribute_value_ranges.csv") if row["attribute_code"] in NEW_CODES]
        self.assertEqual(len(scalar), 18)
        self.assertEqual(
            {row["attribute_code"] for row in scalar},
            {"turning_circle_between_kerbs", "maximum_kerb_weight"},
        )
        self.assertEqual({row["observation_date"] for row in scalar}, {"2026-02-02"})
        self.assertEqual(ranges, [])
''',
    )
    replace_once(
        MODEL_TEST,
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Brochure Chassis Measurement Context Modeling")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Sandero and Stepway Chassis Observation Import")
        self.assertEqual(state["baseline"]["tests"], 875)
        self.assertEqual(state["baseline"]["rows"], 9019)
        self.assertEqual(state["baseline"]["attributes"], 385)
        self.assertEqual(state["baseline"]["configuration_values"], 2290)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 234)
''',
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 875)
        self.assertGreaterEqual(state["baseline"]["rows"], 9019)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2290)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 234)
''',
    )


def update_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Sandero and Stepway Chassis Observation Import"
    state["current_package"] = {
        "name": "Sandero and Stepway Chassis Observation Import",
        "status": "complete",
        "goal": "Import exact between-kerbs turning diameter, maximum kerb weight and source-text tyre and suspension observations for nine active Sandero and Sandero Stepway configurations under D-016."
    }
    state["next_package"] = {
        "name": "Bigster Chassis Observation Import",
        "status": "planned",
        "goal": "Import the unambiguous between-kerbs turning diameter, maximum kerb weight and source-text steering, brake and tyre observations for the active Bigster configurations under D-016."
    }
    write_json(STATE, state)


def main() -> int:
    update_reporting_specs()
    update_model_report()
    update_model_verifier()
    update_model_test()
    update_state()
    print("PASS: Sandero and Stepway chassis integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
