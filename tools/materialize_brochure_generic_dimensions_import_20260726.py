#!/usr/bin/env python3
"""Materialize reporting receipts and project state for generic brochure dimensions."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTING = ROOT / "data" / "reporting"
STATE = ROOT / "project" / "state.json"
MAPPING_REPORT = REPORTING / "brochure_generic_dimensions_semantic_mapping_review.json"
RESIDUAL_REPORT = REPORTING / "official_brochure_residual_evidence_review.json"

SANDERO_ATTRIBUTES = {
    "overall_height",
    "front_track",
    "overall_width",
    "overall_width_with_mirrors",
    "rear_track",
    "front_overhang",
    "wheelbase",
    "rear_overhang",
    "overall_length",
    "ground_clearance",
}
JOGGER_ATTRIBUTES = {
    "roof_height_with_rails",
    "overall_height",
    "front_track",
    "overall_width",
    "overall_width_with_mirrors",
    "rear_track",
    "front_overhang",
    "wheelbase",
    "rear_overhang",
    "overall_length",
    "ground_clearance",
}
DUSTER_ATTRIBUTES = {
    "roof_height_with_rails",
    "front_track",
    "overall_width",
    "overall_width_with_mirrors",
    "rear_track",
    "ground_clearance",
    "front_overhang",
    "wheelbase",
    "rear_overhang",
    "overall_length",
}
REPORTING_SPECS = {
    "sandero_ecog120_manual_completeness.json": SANDERO_ATTRIBUTES,
    "sandero_ecog120_automatic_completeness.json": SANDERO_ATTRIBUTES,
    "jogger_ecog120_manual_completeness.json": JOGGER_ATTRIBUTES,
    "jogger_ecog120_automatic_completeness.json": JOGGER_ATTRIBUTES,
    "jogger_tce110_manual_completeness.json": JOGGER_ATTRIBUTES,
    "jogger_hybrid155_automatic_completeness.json": JOGGER_ATTRIBUTES,
    "duster_ecog120_completeness.json": DUSTER_ATTRIBUTES,
    "duster_mildhybrid140_4x2_completeness.json": DUSTER_ATTRIBUTES,
    "duster_hybrid155_completeness.json": DUSTER_ATTRIBUTES,
}


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_mapping_report() -> None:
    payload = json.loads(MAPPING_REPORT.read_text(encoding="utf-8"))
    payload["import_receipt"] = {
        "status": "imported",
        "package": "Brochure Generic Dimensions Observation Import",
        "imported_on": "2026-07-26",
        "scalar_id_start": 2568,
        "scalar_id_end": 2949,
        "scalar_values": 382,
        "configurations": 36,
        "source_values": {
            "src_pl_sandero_brochure_20260202": 40,
            "src_pl_jogger_brochure_20251217": 242,
            "src_pl_duster_mini_brochure_20251020": 100,
        },
        "duster_4x4_status": "deferred_without_exact_source_relationship",
    }
    payload["next_package"] = {
        "name": "Brochure Generic Dimensions Import Closure Review",
        "goal": "Verify all 382 approved dimension observations, nine reporting integrations, latest-value precedence and the continuing Duster 4x4 and excluded-diagram boundaries.",
    }
    write_json(MAPPING_REPORT, payload)


def update_residual_report() -> None:
    payload = json.loads(RESIDUAL_REPORT.read_text(encoding="utf-8"))
    payload["follow_up_import_receipt"] = {
        "status": "imported_with_documented_deferral",
        "package": "Brochure Generic Dimensions Observation Import",
        "imported_on": "2026-07-26",
        "resolved_classifications": [
            "sandero_dimensions_and_cargo",
            "jogger_dimensions_and_cargo",
        ],
        "partially_resolved_classifications": [
            "duster_wltp_placeholders_and_dimensions"
        ],
        "scalar_values": 382,
        "remaining_boundaries": [
            "Duster 4x4 diagram values lack an exact active source-related configuration.",
            "Duster WLTP placeholders remain no-observation evidence.",
            "Cargo remains governed by the contextual cargo model."
        ],
    }
    payload["next_package"] = {
        "name": "Brochure Generic Dimensions Import Closure Review",
        "goal": "Verify all 382 approved dimension observations, nine reporting integrations, latest-value precedence and the continuing Duster 4x4 and excluded-diagram boundaries.",
    }
    write_json(RESIDUAL_REPORT, payload)


def update_reporting_specs() -> None:
    for filename, attributes in REPORTING_SPECS.items():
        path = REPORTING / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        slots = payload["technical_slots"]
        current = {(item["attribute_code"], item.get("fuel_type_code", "")) for item in slots}
        for attribute in attributes:
            if (attribute, "") not in current:
                slots.append({"attribute_code": attribute, "fuel_type_code": ""})
        slots.sort(key=lambda item: (item["attribute_code"], item.get("fuel_type_code", "")))
        write_json(path, payload)


def update_state() -> None:
    payload = json.loads(STATE.read_text(encoding="utf-8"))
    payload["updated_on"] = "2026-07-26"
    payload["phase"] = "Brochure Generic Dimensions Observation Import"
    payload["current_package"] = {
        "name": "Brochure Generic Dimensions Observation Import",
        "status": "complete",
        "goal": "Materialize the 382 approved historical exterior-dimension observations for exact source-related Sandero, Jogger and Duster 4x2 configurations, integrate reporting slots, and preserve all deferred or excluded diagram values.",
    }
    payload["next_package"] = {
        "name": "Brochure Generic Dimensions Import Closure Review",
        "status": "planned",
        "goal": "Verify all 382 approved dimension observations, nine reporting integrations, latest-value precedence and the continuing Duster 4x4 and excluded-diagram boundaries.",
    }
    write_json(STATE, payload)


def main() -> int:
    update_mapping_report()
    update_residual_report()
    update_reporting_specs()
    update_state()
    print("PASS: generic brochure dimension import integration materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
