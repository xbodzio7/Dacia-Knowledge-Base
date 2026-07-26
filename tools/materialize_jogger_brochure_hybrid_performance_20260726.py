#!/usr/bin/env python3
"""Materialize Jogger hybrid-performance package integration."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "imports" / "brochure_technical_values" / "jogger-hybrid-performance-completion-20251217.json"


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def normalize_manifest_context() -> None:
    payload = json.loads(SPEC.read_text(encoding="utf-8"))
    for group in payload["scalar_groups"]:
        if group["attribute_code"] == "max_power_rpm":
            group["fuel_type_code"] = ""
    for group in payload["range_groups"]:
        if (
            group["attribute_code"] == "max_torque_rpm"
            and all("hybrid155" in code for code in group["configurations"])
        ):
            group["fuel_type_code"] = ""
    SPEC.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_hybrid_reporting_scope() -> None:
    path = ROOT / "data" / "reporting" / "jogger_hybrid155_automatic_completeness.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    slots = payload["technical_slots"]
    existing = {
        (str(item.get("attribute_code", "")), str(item.get("fuel_type_code", "")))
        for item in slots
    }
    for slot in (
        {"attribute_code": "hybrid_battery_capacity_source_stated", "fuel_type_code": ""},
        {"attribute_code": "max_power_rpm", "fuel_type_code": ""},
    ):
        key = (slot["attribute_code"], slot["fuel_type_code"])
        if key not in existing:
            slots.append(slot)
            existing.add(key)
    slots.sort(
        key=lambda item: (
            str(item.get("attribute_code", "")),
            str(item.get("fuel_type_code", "")),
        )
    )
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_towing_historical_state_test() -> None:
    path = ROOT / "tests" / "test_bigster_duster_brochure_towing_masses_20260726.py"
    text = path.read_text(encoding="utf-8")
    old_name = "test_project_state_advances_to_jogger_hybrid_completion"
    new_name = "test_project_state_preserves_towing_mass_baseline_after_follow_up_packages"
    if f"def {new_name}" in text:
        return
    pattern = re.compile(
        rf'^    def {old_name}\(self\) -> None:\n.*?(?=^\n\nif __name__)',
        re.MULTILINE | re.DOTALL,
    )
    replacement = f'''    def {new_name}(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 858)
        self.assertGreaterEqual(state["baseline"]["rows"], 8939)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2272)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 176)
        self.assertGreaterEqual(state["baseline"]["configuration_import_specs"], 117)
        self.assertGreaterEqual(state["baseline"]["configuration_range_import_specs"], 20)
'''
    text, count = pattern.subn(replacement, text, count=1)
    ensure(count == 1, "towing mass historical project-state method missing")
    path.write_text(text, encoding="utf-8")


def update_project_state_and_changelog() -> None:
    state_path = ROOT / "project" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Jogger Brochure Hybrid Performance Completion"
    state["current_package"] = {
        "name": "Jogger Brochure Hybrid Performance Completion",
        "status": "complete",
        "goal": (
            "Complete the exact Jogger hybrid 155 acceleration and source-stated battery "
            "capacity observations and import source engine-speed points or ranges without "
            "flattening five-/seven-seat or fuel-specific evidence."
        ),
    }
    state["next_package"] = {
        "name": "Brochure Chassis Measurement Context Modeling",
        "status": "planned",
        "goal": (
            "Model explicit measurement and specification context for turning circle, "
            "maximum kerb mass, payload and compound tyre, brake and suspension evidence "
            "before importing the remaining official brochure chassis observations."
        ),
    }
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    changelog_path = ROOT / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    entry = (
        "* Added 18 scalar and 58 closed-range historical Jogger brochure observations: "
        "exact five-/seven-seat hybrid 155 acceleration, neutral source-stated 1.4 kWh "
        "battery capacity, the hybrid combustion-engine power point, and fuel-preserving "
        "maximum-power/torque engine-speed intervals across all 22 configurations, while "
        "retaining later MY26 observations as current.\n"
    )
    if entry not in changelog:
        marker = "### Added\n\n"
        ensure(marker in changelog, "CHANGELOG Added marker missing")
        changelog = changelog.replace(marker, marker + entry, 1)
        changelog_path.write_text(changelog, encoding="utf-8")


def main() -> int:
    normalize_manifest_context()
    update_hybrid_reporting_scope()
    update_towing_historical_state_test()
    update_project_state_and_changelog()
    print("PASS: Jogger hybrid performance integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
