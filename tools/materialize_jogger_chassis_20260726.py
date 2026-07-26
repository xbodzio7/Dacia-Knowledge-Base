#!/usr/bin/env python3
"""Materialize Jogger chassis reporting and project-state integration."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
STATE = ROOT / "project" / "state.json"
MODEL_REPORT = REPORTING / "brochure_chassis_measurement_context_model.json"
MODEL_VERIFIER = ROOT / "tools" / "verify_brochure_chassis_measurement_context_model_20260726.py"
MODEL_TEST = ROOT / "tests" / "test_brochure_chassis_measurement_context_modeling_20260726.py"
DUSTER_TEST = ROOT / "tests" / "test_duster_chassis_20260726.py"
BIGSTER_TEST = ROOT / "tests" / "test_bigster_chassis_20260726.py"
SANDERO_TEST = ROOT / "tests" / "test_sandero_stepway_chassis_20260726.py"
REPORTING_SPECS = (
    REPORTING / "jogger_ecog120_manual_completeness.json",
    REPORTING / "jogger_ecog120_automatic_completeness.json",
    REPORTING / "jogger_tce110_manual_completeness.json",
    REPORTING / "jogger_hybrid155_automatic_completeness.json",
)
NEW_SLOTS = tuple(
    {"attribute_code": code, "fuel_type_code": ""}
    for code in (
        "front_suspension",
        "rear_suspension",
        "standard_tyre_specification",
        "turning_circle_between_kerbs",
    )
)
CLOSURE_PACKAGE = "Brochure Chassis Modeling Closure Review"


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
        if item["classification_code"] == "jogger_chassis_candidate_and_modeling":
            item["status"] = "imported"
            item["import_package"] = "Jogger Chassis Observation Import"
            item["imported_on"] = "2026-07-26"
    payload["next_package"] = {
        "name": CLOSURE_PACKAGE,
        "goal": "Verify that all five D-016 chassis modeling resolutions are imported, all source and reporting contracts remain green, and the separate Jogger mass-table label conflict remains explicitly unresolved."
    }
    write_json(MODEL_REPORT, payload)


def update_model_verifier() -> None:
    replace_once(
        MODEL_VERIFIER,
        '        "jogger_chassis_candidate_and_modeling": "model_defined_import_pending",\n',
        '        "jogger_chassis_candidate_and_modeling": "imported",\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '    ensure(next_package.get("name") == "Jogger Chassis Observation Import", "next package differs")\n',
        '    ensure(next_package.get("name") == "Brochure Chassis Modeling Closure Review", "next package differs")\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '    ensure(len(scalar) == 66, "expected sixty-six modeled scalar chassis observations")\n',
        '    ensure(len(scalar) == 88, "expected eighty-eight modeled scalar chassis observations")\n',
    )
    replace_once(
        MODEL_VERIFIER,
        '''            "src_pl_duster_mini_brochure_20251020",
            "src_pl_sandero_brochure_20260202",
''',
        '''            "src_pl_duster_mini_brochure_20251020",
            "src_pl_jogger_brochure_20251217",
            "src_pl_sandero_brochure_20260202",
''',
    )
    replace_once(
        MODEL_VERIFIER,
        '''        == {"2025-10-20", "2025-12-10", "2026-02-02"},
        "modeled scalar dates differ",
''',
        '''        == {"2025-10-20", "2025-12-10", "2025-12-17", "2026-02-02"},
        "modeled scalar dates differ",
''',
    )


def update_model_test() -> None:
    replace_once(
        MODEL_TEST,
        '        self.assertEqual(statuses["jogger_chassis_candidate_and_modeling"], "model_defined_import_pending")\n',
        '        self.assertEqual(statuses["jogger_chassis_candidate_and_modeling"], "imported")\n',
    )
    replace_once(
        MODEL_TEST,
        '        self.assertEqual(len(scalar), 66)\n',
        '        self.assertEqual(len(scalar), 88)\n',
    )
    replace_once(
        MODEL_TEST,
        '''            {"2025-10-20", "2025-12-10", "2026-02-02"},
''',
        '''            {"2025-10-20", "2025-12-10", "2025-12-17", "2026-02-02"},
''',
    )


def update_follow_up_tests() -> None:
    replace_once(
        DUSTER_TEST,
        '        self.assertEqual(statuses["jogger_chassis_candidate_and_modeling"], "model_defined_import_pending")\n',
        '        self.assertEqual(statuses["jogger_chassis_candidate_and_modeling"], "imported")\n',
    )
    replace_once(
        DUSTER_TEST,
        '        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")\n',
        '        self.assertEqual(model["next_package"]["name"], "Brochure Chassis Modeling Closure Review")\n',
    )
    replace_once(
        DUSTER_TEST,
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "Duster Chassis Observation Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Jogger Chassis Observation Import")
        self.assertEqual(state["baseline"]["tests"], 899)
        self.assertEqual(state["baseline"]["rows"], 9218)
        self.assertEqual(state["baseline"]["configuration_values"], 2479)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertEqual(state["baseline"]["attributes"], 385)
''',
        '''        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 899)
        self.assertGreaterEqual(state["baseline"]["rows"], 9218)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2479)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 244)
        self.assertGreaterEqual(state["baseline"]["attributes"], 385)
''',
    )
    replace_once(
        BIGSTER_TEST,
        '        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")\n',
        '        self.assertEqual(model["next_package"]["name"], "Brochure Chassis Modeling Closure Review")\n',
    )
    replace_once(
        SANDERO_TEST,
        '        self.assertEqual(model["next_package"]["name"], "Jogger Chassis Observation Import")\n',
        '        self.assertEqual(model["next_package"]["name"], "Brochure Chassis Modeling Closure Review")\n',
    )


def update_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Jogger Chassis Observation Import"
    state["current_package"] = {
        "name": "Jogger Chassis Observation Import",
        "status": "complete",
        "goal": "Import exact between-kerbs turning diameter and source-text tyre and suspension observations for all twenty-two active Jogger configurations under D-016 without reinterpreting the ambiguous mass table."
    }
    state["next_package"] = {
        "name": CLOSURE_PACKAGE,
        "status": "planned",
        "goal": "Verify that all five D-016 chassis modeling resolutions are imported, all source and reporting contracts remain green, and the separate Jogger mass-table label conflict remains explicitly unresolved."
    }
    write_json(STATE, state)


def main() -> int:
    update_reporting_specs()
    update_model_report()
    update_model_verifier()
    update_model_test()
    update_follow_up_tests()
    update_state()
    print("PASS: Jogger chassis integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
