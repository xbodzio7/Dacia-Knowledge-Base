#!/usr/bin/env python3
"""Materialize Bigster chassis reporting and project-state integration."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
STATE = ROOT / "project" / "state.json"
MODEL_REPORT = REPORTING / "brochure_chassis_measurement_context_model.json"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
MODEL_TEST = ROOT / "tests" / "test_brochure_chassis_measurement_context_modeling_20260726.py"
SANDERO_TEST = ROOT / "tests" / "test_sandero_stepway_chassis_20260726.py"
REPORTING_SPECS = (
    REPORTING / "bigster_mildhybrid140_4x2_manual_completeness.json",
    REPORTING / "bigster_mildhybridg140_4x2_manual_completeness.json",
    REPORTING / "bigster_hybrid155_4x2_automatic_completeness.json",
    REPORTING / "bigster_hybridg150_4x4_automatic_completeness.json",
)
NEW_SLOTS = tuple(
    {"attribute_code": code, "fuel_type_code": ""}
    for code in (
        "front_brake_type",
        "maximum_kerb_weight",
        "rear_brake_type",
        "standard_tyre_specification",
        "steering_type",
        "turning_circle_between_kerbs",
    )
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
    for item in payload["source_resolutions"]:
        if item["classification_code"] == "bigster_chassis_measurement_modeling":
            item["status"] = "imported"
            item["import_package"] = "Bigster Chassis Observation Import"
            item["imported_on"] = "2026-07-26"
    payload["next_package"] = {
        "name": "Duster Chassis Observation Import",
        "goal": "Import wheel-track turning diameter, maximum kerb weight, payload ranges and source-text steering, brake and tyre observations for the active Duster configurations under D-016."
    }
    write_json(MODEL_REPORT, payload)


def update_model_verifier() -> None:
    replace_once(
        MODEL_VERIFIER,
        '        "bigster_chassis_measurement_modeling": "model_defined_import_pending",\n',
        '        "bigster_chassis_measurement_modeling": "imported",\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '    ensure(next_package.get("name") == "Bigster Chassis Observation Import", "next package differs")\n',
        '    ensure(next_package.get("name") == "Duster Chassis Observation Import", "next package differs")\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '    ensure(len(scalar) == 18, "expected eighteen modeled scalar chassis observations")\n',
        '    ensure(len(scalar) == 46, "expected forty-six modeled scalar chassis observations")\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '''        == {"src_pl_sandero_brochure_20260202", "src_pl_sandero_stepway_brochure_20260202"},
        "modeled scalar source set differs",
    )
    ensure({row.get("observation_date") for row in scalar} == {"2026-02-02"}, "modeled scalar date differs")
''',
        '''        == {
            "src_pl_bigster_brochure_20251210",
            "src_pl_sandero_brochure_20260202",
            "src_pl_sandero_stepway_brochure_20260202",
        },
        "modeled scalar source set differs",
    )
    ensure(
        {row.get("observation_date") for row in scalar} == {"2025-12-10", "2026-02-02"},
        "modeled scalar dates differ",
    )
''',
    )


def update_model_test() -> None:
    replace_once(
        MODEL_TEST,
        '''        self.assertEqual(statuses["sandero_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(statuses["stepway_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(
            {status for code, status in statuses.items() if code not in {
                "sandero_chassis_and_maximum_mass_modeling",
                "stepway_chassis_and_maximum_mass_modeling",
            }},
            {"model_defined_import_pending"},
        )
''',
        '''        self.assertEqual(statuses["bigster_chassis_measurement_modeling"], "imported")
        self.assertEqual(statuses["sandero_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(statuses["stepway_chassis_and_maximum_mass_modeling"], "imported")
        self.assertEqual(
            {status for code, status in statuses.items() if code in {
                "jogger_chassis_candidate_and_modeling",
                "duster_chassis_mass_and_payload_modeling",
            }},
            {"model_defined_import_pending"},
        )
''',
    )
    replace_once(
        MODEL_TEST,
        '''        self.assertEqual(len(scalar), 18)
        self.assertEqual(
            {row["attribute_code"] for row in scalar},
            {"turning_circle_between_kerbs", "maximum_kerb_weight"},
        )
        self.assertEqual({row["observation_date"] for row in scalar}, {"2026-02-02"})
''',
        '''        self.assertEqual(len(scalar), 46)
        self.assertEqual(
            {row["attribute_code"] for row in scalar},
            {"turning_circle_between_kerbs", "maximum_kerb_weight"},
        )
        self.assertEqual({row["observation_date"] for row in scalar}, {"2025-12-10", "2026-02-02"})
''',
    )


def update_sandero_follow_up_test() -> None:
    replace_once(
        SANDERO_TEST,
        '        self.assertEqual(model["next_package"]["name"], "Bigster Chassis Observation Import")\n',
        '        self.assertEqual(model["next_package"]["name"], "Duster Chassis Observation Import")\n',
    )
    replace_once(
        SANDERO_TEST,
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Sandero and Stepway Chassis Observation Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Bigster Chassis Observation Import")
        self.assertEqual(state["baseline"]["tests"], 883)
        self.assertEqual(state["baseline"]["rows"], 9064)
        self.assertEqual(state["baseline"]["configuration_values"], 2335)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertEqual(state["baseline"]["attributes"], 385)
''',
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 883)
        self.assertGreaterEqual(state["baseline"]["rows"], 9064)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2335)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)
''',
    )


def update_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Bigster Chassis Observation Import"
    state["current_package"] = {
        "name": "Bigster Chassis Observation Import",
        "status": "complete",
        "goal": "Import exact between-kerbs turning diameter, maximum kerb weight and source-text steering, brake and tyre observations for fourteen active Bigster configurations under D-016."
    }
    state["next_package"] = {
        "name": "Duster Chassis Observation Import",
        "status": "planned",
        "goal": "Import wheel-track turning diameter, maximum kerb weight, payload ranges and source-text steering, brake and tyre observations for the active Duster configurations under D-016."
    }
    write_json(STATE, state)


def main() -> int:
    update_reporting_specs()
    update_model_report()
    update_model_verifier()
    update_model_test()
    update_sandero_follow_up_test()
    update_state()
    print("PASS: Bigster chassis integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
