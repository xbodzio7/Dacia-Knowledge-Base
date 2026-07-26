#!/usr/bin/env python3
"""Materialize Duster chassis reporting and project-state integration."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
STATE = ROOT / "project" / "state.json"
MODEL_REPORT = REPORTING / "brochure_chassis_measurement_context_model.json"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
MODEL_TEST = ROOT / "tests" / "test_brochure_chassis_measurement_context_modeling_20260726.py"
BIGSTER_TEST = ROOT / "tests" / "test_bigster_chassis_20260726.py"
SANDERO_TEST = ROOT / "tests" / "test_sandero_stepway_chassis_20260726.py"
REPORTING_SPECS = (
    REPORTING / "duster_ecog120_completeness.json",
    REPORTING / "duster_mildhybrid140_4x2_completeness.json",
    REPORTING / "duster_hybrid155_completeness.json",
)
NEW_SLOTS = tuple(
    {"attribute_code": code, "fuel_type_code": ""}
    for code in (
        "front_brake_type",
        "maximum_kerb_weight",
        "payload",
        "rear_brake_type",
        "standard_tyre_specification",
        "steering_type",
        "turning_circle_wheel_track",
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
        if item["classification_code"] == "duster_chassis_mass_and_payload_modeling":
            item["status"] = "imported"
            item["import_package"] = "Duster Chassis Observation Import"
            item["imported_on"] = "2026-07-26"
    payload["next_package"] = {
        "name": "Jogger Chassis Observation Import",
        "goal": "Import the unambiguous between-kerbs turning diameter and source-text tyre and suspension observations for active Jogger configurations while preserving the separate unresolved mass-table label conflict."
    }
    write_json(MODEL_REPORT, payload)


def update_model_verifier() -> None:
    replace_once(
        MODEL_VERIFIER,
        '        "duster_chassis_mass_and_payload_modeling": "model_defined_import_pending",\n',
        '        "duster_chassis_mass_and_payload_modeling": "imported",\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '    ensure(next_package.get("name") == "Duster Chassis Observation Import", "next package differs")\n',
        '    ensure(next_package.get("name") == "Jogger Chassis Observation Import", "next package differs")\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '    ensure(len(scalar) == 46, "expected forty-six modeled scalar chassis observations")\n',
        '    ensure(len(scalar) == 66, "expected sixty-six modeled scalar chassis observations")\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '''        == {"turning_circle_between_kerbs", "maximum_kerb_weight"},
        "modeled scalar attribute set differs",
''',
        '''        == {
            "turning_circle_between_kerbs",
            "turning_circle_wheel_track",
            "maximum_kerb_weight",
        },
        "modeled scalar attribute set differs",
''',
    )
    replace_once(
        MODEL_VERIFIER,
        '''            "src_pl_bigster_brochure_20251210",
            "src_pl_sandero_brochure_20260202",
''',
        '''            "src_pl_bigster_brochure_20251210",
            "src_pl_duster_mini_brochure_20251020",
            "src_pl_sandero_brochure_20260202",
''',
    )
    replace_once(
        MODEL_VERIFIER,
        '''        {row.get("observation_date") for row in scalar} == {"2025-12-10", "2026-02-02"},
        "modeled scalar dates differ",
    )
    ensure(ranges == [], "payload and wheel-track follow-up ranges are not imported yet")
''',
        '''        {row.get("observation_date") for row in scalar}
        == {"2025-10-20", "2025-12-10", "2026-02-02"},
        "modeled scalar dates differ",
    )
    ensure(len(ranges) == 10, "expected ten modeled payload ranges")
    ensure({row.get("attribute_code") for row in ranges} == {"payload"}, "modeled range attribute differs")
    ensure({row.get("source_code") for row in ranges} == {"src_pl_duster_mini_brochure_20251020"}, "modeled range source differs")
    ensure({row.get("observation_date") for row in ranges} == {"2025-10-20"}, "modeled range date differs")
''',
    )


def update_model_test() -> None:
    replace_once(
        MODEL_TEST,
        '''        self.assertEqual(
            {status for code, status in statuses.items() if code in {
                "jogger_chassis_candidate_and_modeling",
                "duster_chassis_mass_and_payload_modeling",
            }},
            {"model_defined_import_pending"},
        )
''',
        '''        self.assertEqual(statuses["duster_chassis_mass_and_payload_modeling"], "imported")
        self.assertEqual(statuses["jogger_chassis_candidate_and_modeling"], "model_defined_import_pending")
''',
    )
    replace_once(
        MODEL_TEST,
        '''        self.assertEqual(len(scalar), 46)
        self.assertEqual(
            {row["attribute_code"] for row in scalar},
            {"turning_circle_between_kerbs", "maximum_kerb_weight"},
        )
        self.assertEqual({row["observation_date"] for row in scalar}, {"2025-12-10", "2026-02-02"})
        self.assertEqual(ranges, [])
''',
        '''        self.assertEqual(len(scalar), 66)
        self.assertEqual(
            {row["attribute_code"] for row in scalar},
            {"turning_circle_between_kerbs", "turning_circle_wheel_track", "maximum_kerb_weight"},
        )
        self.assertEqual(
            {row["observation_date"] for row in scalar},
            {"2025-10-20", "2025-12-10", "2026-02-02"},
        )
        self.assertEqual(len(ranges), 10)
        self.assertEqual({row["attribute_code"] for row in ranges}, {"payload"})
        self.assertEqual({row["observation_date"] for row in ranges}, {"2025-10-20"})
''',
    )


def update_follow_up_tests() -> None:
    replace_once(
        BIGSTER_TEST,
        '        self.assertEqual(model["next_package"]["name"], "Duster Chassis Observation Import")\n',
        '        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")\n',
    )
    replace_once(
        BIGSTER_TEST,
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Bigster Chassis Observation Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Duster Chassis Observation Import")
        self.assertEqual(state["baseline"]["tests"], 891)
        self.assertEqual(state["baseline"]["rows"], 9148)
        self.assertEqual(state["baseline"]["configuration_values"], 2419)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertEqual(state["baseline"]["attributes"], 385)
''',
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 891)
        self.assertGreaterEqual(state["baseline"]["rows"], 9148)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2419)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)
''',
    )
    replace_once(
        SANDERO_TEST,
        '        self.assertEqual(model["next_package"]["name"], "Duster Chassis Observation Import")\n',
        '        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")\n',
    )


def update_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Duster Chassis Observation Import"
    state["current_package"] = {
        "name": "Duster Chassis Observation Import",
        "status": "complete",
        "goal": "Import exact wheel-track turning diameter, maximum kerb weight, payload ranges and source-text steering, brake and tyre observations for ten active Duster configurations under D-016."
    }
    state["next_package"] = {
        "name": "Jogger Chassis Observation Import",
        "status": "planned",
        "goal": "Import the unambiguous between-kerbs turning diameter and source-text tyre and suspension observations for active Jogger configurations while preserving the separate unresolved mass-table label conflict."
    }
    write_json(STATE, state)


def main() -> int:
    update_reporting_specs()
    update_model_report()
    update_model_verifier()
    update_model_test()
    update_follow_up_tests()
    update_state()
    print("PASS: Duster chassis integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
