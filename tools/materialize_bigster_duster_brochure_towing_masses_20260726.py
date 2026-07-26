#!/usr/bin/env python3
"""Materialize reporting and project integration for towing mass observations."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING_SPECS = (
    "bigster_hybrid155_4x2_automatic_completeness.json",
    "bigster_hybridg150_4x4_automatic_completeness.json",
    "bigster_mildhybrid140_4x2_manual_completeness.json",
    "bigster_mildhybridg140_4x2_manual_completeness.json",
    "duster_ecog120_completeness.json",
    "duster_hybrid155_completeness.json",
    "duster_mildhybrid140_4x2_completeness.json",
)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def update_reporting_specs() -> None:
    reporting = ROOT / "data" / "reporting"
    for filename in REPORTING_SPECS:
        path = reporting / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        slots = payload["technical_slots"]
        existing = {
            (str(item.get("attribute_code", "")), str(item.get("fuel_type_code", "")))
            for item in slots
        }
        for slot in (
            {"attribute_code": "gross_train_weight", "fuel_type_code": ""},
            {"attribute_code": "unbraked_trailer_weight", "fuel_type_code": ""},
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


def update_sandero_historical_state_test() -> None:
    path = ROOT / "tests" / "test_sandero_ecog120_automatic_brochure_technical_20260726.py"
    text = path.read_text(encoding="utf-8")
    old_name = "test_project_state_advances_to_towing_mass_package"
    new_name = "test_project_state_preserves_automatic_sandero_baseline_after_follow_up_packages"
    if f"def {new_name}" in text:
        return
    pattern = re.compile(
        rf'^    def {old_name}\(self\) -> None:\n.*?(?=^\n\nif __name__)',
        re.MULTILINE | re.DOTALL,
    )
    replacement = f'''    def {new_name}(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 850)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2224)
        self.assertGreaterEqual(state["baseline"]["rows"], 8888)
        self.assertGreaterEqual(state["baseline"]["configuration_import_specs"], 117)
'''
    text, count = pattern.subn(replacement, text, count=1)
    ensure(count == 1, "Sandero historical project-state test anchor missing")
    path.write_text(text, encoding="utf-8")


def update_project_state_and_changelog() -> None:
    state_path = ROOT / "project" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Bigster and Duster Brochure Towing Mass Import"
    state["current_package"] = {
        "name": "Bigster and Duster Brochure Towing Mass Import",
        "status": "complete",
        "goal": (
            "Import exact gross train weight and unbraked trailer weight observations "
            "from the official Bigster and Duster brochures for the reviewed active "
            "configurations, using existing attributes and preserving powertrain boundaries."
        ),
    }
    state["next_package"] = {
        "name": "Jogger Brochure Hybrid Performance Completion",
        "status": "planned",
        "goal": (
            "Complete the exact Jogger hybrid 155 acceleration and source-stated battery "
            "capacity observations and import source engine-speed points or ranges without "
            "flattening five-/seven-seat or fuel-specific evidence."
        ),
    }
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    changelog_path = ROOT / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    entry = (
        "* Imported 48 exact gross-train and unbraked-trailer mass observations from "
        "the official Bigster and Duster brochures across 24 active configurations, "
        "preserving exact powertrain boundaries and retaining newer Duster Eco-G 120 "
        "automatic homologation evidence.\n"
    )
    if entry not in changelog:
        marker = "### Added\n\n"
        ensure(marker in changelog, "CHANGELOG Added marker missing")
        changelog = changelog.replace(marker, marker + entry, 1)
        changelog_path.write_text(changelog, encoding="utf-8")


def main() -> int:
    update_reporting_specs()
    update_sandero_historical_state_test()
    update_project_state_and_changelog()
    print("PASS: Bigster and Duster towing mass integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
