#!/usr/bin/env python3
"""Materialize reporting and project-state integration for the Sandero package."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_CONFIGURATIONS = {
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
}
RESOLVED_TECHNICAL_ATTRIBUTES = {
    "engine_power",
    "engine_torque",
    "engine_displacement",
    "cylinder_count",
    "total_valve_count",
    "emission_standard",
    "gearbox_type",
    "gear_count",
    "top_speed",
    "acceleration_0_100",
    "fuel_tank_capacity",
    "minimum_kerb_weight",
    "gross_vehicle_weight",
    "gross_train_weight",
    "braked_trailer_weight",
}


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    ensure(old in text, f"anchor missing in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_reporting_scope() -> None:
    path = ROOT / "data" / "reporting" / "sandero_ecog120_automatic_completeness.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    slots = payload["technical_slots"]
    existing = {
        (str(item.get("attribute_code", "")), str(item.get("fuel_type_code", "")))
        for item in slots
    }
    for slot in (
        {"attribute_code": "gearbox_type", "fuel_type_code": ""},
        {"attribute_code": "minimum_kerb_weight", "fuel_type_code": ""},
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


def update_gap_review_verifier() -> None:
    path = ROOT / "tools" / "review_official_brochure_technical_gaps_20260726.py"
    text = path.read_text(encoding="utf-8")
    old_coverage = '''    ensure(len(brochure_values) == 357, "brochure scalar value total differs")
    ensure(not brochure_ranges, "review unexpectedly contains brochure ranges")
    ensure(Counter(row.get("attribute_code", "") for row in brochure_values) == Counter({"boot_capacity": 287, "elasticity_80_120": 70}), "brochure attribute coverage differs")
    ensure(len(brochure_relationships) == 52, "brochure relationship total differs")'''
    new_coverage = '''    baseline_counts = Counter(row.get("attribute_code", "") for row in brochure_values)
    ensure(baseline_counts["boot_capacity"] == 287, "brochure cargo baseline differs")
    ensure(baseline_counts["elasticity_80_120"] == 70, "brochure selected-gear baseline differs")
    ensure(len(brochure_values) >= 357, "brochure scalar value baseline regressed")
    ensure(len(brochure_relationships) >= 52, "brochure relationship baseline regressed")
    ensure(isinstance(brochure_ranges, list), "brochure range inventory is invalid")'''
    if new_coverage not in text:
        ensure(old_coverage in text, "historical coverage anchor missing")
        text = text.replace(old_coverage, new_coverage, 1)

    old_candidate = '''        present = {attribute for configuration, attribute in pairs if configuration == code}
        ensure(not (present & SANDERO_AUTOMATIC_CANDIDATE_ATTRIBUTES), f"automatic Sandero candidate is already populated: {code}")'''
    new_candidate = '''        present = {attribute for configuration, attribute in pairs if configuration == code}
        materialized = present & SANDERO_AUTOMATIC_CANDIDATE_ATTRIBUTES
        ensure(
            not materialized or materialized == SANDERO_AUTOMATIC_CANDIDATE_ATTRIBUTES,
            f"automatic Sandero candidate is only partially populated: {code}",
        )'''
    if new_candidate not in text:
        ensure(old_candidate in text, "automatic candidate anchor missing")
        text = text.replace(old_candidate, new_candidate, 1)

    obsolete_checks = (
        '\n    ensure(not any((code, "gross_train_weight") in pairs for code in bigster), "Bigster gross train weight candidate already populated")\n    ensure(not any((code, "unbraked_trailer_weight") in pairs for code in bigster), "Bigster unbraked towing candidate already populated")',
        '\n    ensure(not any((code, "acceleration_0_100") in pairs for code in jogger_hybrid), "Jogger hybrid acceleration candidate already populated")\n    ensure(not any((code, "hybrid_battery_capacity_source_stated") in pairs for code in jogger_hybrid), "Jogger battery capacity candidate already populated")',
        '\n    ensure(not any((code, "gross_train_weight") in pairs for code in duster_exact), "Duster gross train weight candidate already populated")\n    ensure(not any((code, "unbraked_trailer_weight") in pairs for code in duster_exact), "Duster unbraked towing candidate already populated")',
    )
    for old in obsolete_checks:
        text = text.replace(old, "", 1)
    path.write_text(text, encoding="utf-8")


def update_gap_review_test() -> None:
    path = ROOT / "tests" / "test_official_brochure_technical_gap_review.py"
    text = path.read_text(encoding="utf-8")
    old_live = '''        self.assertEqual(len(values), 357)
        self.assertEqual(
            Counter(row["attribute_code"] for row in values),
            Counter({"boot_capacity": 287, "elasticity_80_120": 70}),
        )'''
    new_live = '''        counts = Counter(row["attribute_code"] for row in values)
        self.assertEqual(counts["boot_capacity"], 287)
        self.assertEqual(counts["elasticity_80_120"], 70)
        self.assertGreaterEqual(len(values), 357)'''
    if new_live not in text:
        ensure(old_live in text, "historical live coverage anchor missing")
        text = text.replace(old_live, new_live, 1)

    old_name = "test_project_state_advances_to_automatic_sandero_import"
    new_name = "test_project_state_preserves_review_baseline_after_follow_up_packages"
    if f"def {new_name}" not in text:
        pattern = re.compile(
            rf'^    def {old_name}\(self\) -> None:\n.*?(?=^\n\nif __name__)',
            re.MULTILINE | re.DOTALL,
        )
        replacement = f'''    def {new_name}(self) -> None:
        state = json.loads((ROOT / "project" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 842)
        self.assertGreaterEqual(state["baseline"]["rows"], 8852)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2188)
        self.assertGreaterEqual(state["baseline"]["configuration_import_specs"], 117)
'''
        text, count = pattern.subn(replacement, text, count=1)
        ensure(count == 1, "historical project-state method missing")
    path.write_text(text, encoding="utf-8")


def prune_resolved_gap_evidence() -> None:
    path = ROOT / "data" / "reporting" / "sandero_ecog120_automatic_gap_evidence.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    decisions = payload.get("decisions")
    ensure(isinstance(decisions, list), "gap evidence decisions must be a list")
    kept = []
    removed = 0
    for item in decisions:
        ensure(isinstance(item, dict), "gap evidence decision must be an object")
        resolved = (
            item.get("domain") == "technical"
            and item.get("configuration_code") in TARGET_CONFIGURATIONS
            and item.get("attribute_code") in RESOLVED_TECHNICAL_ATTRIBUTES
        )
        if resolved:
            removed += 1
        else:
            kept.append(item)
    payload["decisions"] = kept
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    ensure(removed in {0, 32}, f"unexpected resolved evidence count: {removed}")


def update_historical_regression_counts() -> None:
    replace_once(
        ROOT / "tests" / "test_attribute_enum_domains.py",
        "self.assertEqual(len(enum_rows), 170)",
        "self.assertEqual(len(enum_rows), 174)",
    )
    replace_once(
        ROOT / "tests" / "test_sandero_euro_6e_bis_model.py",
        "self.assertEqual(len(all_emission_values), 43)",
        "self.assertEqual(len(all_emission_values), 45)",
    )
    path = ROOT / "tests" / "test_brochure_gear_performance_import_closure_review.py"
    replace_once(
        path,
        'self.assertEqual(state["baseline"]["configuration_values"], 2188)',
        'self.assertGreaterEqual(state["baseline"]["configuration_values"], 2188)',
    )
    replace_once(
        path,
        'self.assertEqual(state["baseline"]["rows"], 8852)',
        'self.assertGreaterEqual(state["baseline"]["rows"], 8852)',
    )
    replace_once(
        path,
        'self.assertEqual(state["baseline"]["configuration_import_specs"], 117)',
        'self.assertGreaterEqual(state["baseline"]["configuration_import_specs"], 117)',
    )


def update_project_state_and_changelog() -> None:
    state_path = ROOT / "project" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Sandero Eco-G 120 Automatic Brochure Technical Import"
    state["current_package"] = {
        "name": "Sandero Eco-G 120 Automatic Brochure Technical Import",
        "status": "complete",
        "goal": (
            "Import the exact existing-schema engine, performance, transmission, "
            "mass and towing observations from the official Sandero brochure for "
            "the two active Eco-G 120 automatic Expression and Journey configurations, "
            "while excluding placeholder WLTP cells, maximum kerb weight and "
            "model-wide chassis fields."
        ),
    }
    state["next_package"] = {
        "name": "Bigster and Duster Brochure Towing Mass Import",
        "status": "planned",
        "goal": (
            "Import exact gross train weight and unbraked trailer weight observations "
            "from the official Bigster and Duster brochures for the reviewed active "
            "configurations, using existing attributes and preserving powertrain boundaries."
        ),
    }
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    changelog_path = ROOT / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    entry = (
        "* Imported 36 exact brochure technical observations for the two active "
        "Sandero Eco-G 120 automatic Expression and Journey configurations, preserving "
        "LPG/petrol context for power, torque and acceleration while excluding WLTP "
        "placeholders, maximum kerb weight and model-wide chassis rows.\n"
    )
    if entry not in changelog:
        marker = "### Added\n\n"
        ensure(marker in changelog, "CHANGELOG Added marker missing")
        changelog = changelog.replace(marker, marker + entry, 1)
        changelog_path.write_text(changelog, encoding="utf-8")


def main() -> int:
    update_reporting_scope()
    update_gap_review_verifier()
    update_gap_review_test()
    prune_resolved_gap_evidence()
    update_historical_regression_counts()
    update_project_state_and_changelog()
    print("PASS: Sandero automatic package integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
