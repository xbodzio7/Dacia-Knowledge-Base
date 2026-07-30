#!/usr/bin/env python3
"""Materialize the Jogger page 19 remaining mass-conflict closure review."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "data/reporting/jogger_page19_remaining_mass_conflict_closure.json"
REPORT_MD = ROOT / "data/reporting/jogger_page19_remaining_mass_conflict_closure.md"
REVIEW_MD = ROOT / "project/reviews/jogger-page19-remaining-mass-conflict-closure-2026-07-30.md"
STATE = ROOT / "project/state.json"


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: dict[str, object]) -> None:
    write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def next_package() -> dict[str, object]:
    return {
        "package_id": "post_residual_jogger_page19_range_context_follow_up_review_001",
        "kind": "review_closure",
        "name": "Jogger Page 19 Range and Context Follow-up Review",
        "status": "planned",
        "source_code": "src_pl_jogger_brochure_20251217",
        "goal": "Review the remaining page-19 power-speed and torque-speed ranges, energy-source column semantics, homologation-protocol context and Hybrid 155 total-power conflict without changing current exact values or promoting context by inference.",
        "manifest_paths": [
            "data/reporting/jogger_page19_range_context_follow_up_review.json",
            "data/reporting/jogger_page19_range_context_follow_up_review.md",
            "project/reviews/jogger-page19-range-context-follow-up-review-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }


def payload() -> dict[str, object]:
    return {
        "version": 1,
        "kind": "jogger_page19_remaining_mass_conflict_closure",
        "reviewed_on": "2026-07-30",
        "status": "complete_with_preserved_boundaries",
        "package_id": "post_residual_jogger_page19_remaining_mass_conflict_closure_review_001",
        "source": {
            "source_code": "src_pl_jogger_brochure_20251217",
            "file_path": "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf",
            "sha256": "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6",
            "page": 19,
            "observation_date": "2025-12-17",
        },
        "comparison_source": {
            "source_code": "src_pl_jogger_price_my26_20260401",
            "observation_date": "2026-04-01",
        },
        "scope": {
            "current_jogger_configurations": 22,
            "completed_scalar_import_packages": 5,
            "completed_scalar_observations": 128,
            "preserved_mass_conflict_blocks": 2,
            "preserved_hybrid_trailer_conflict_configurations": 6,
        },
        "completed_import_receipts": [
            {
                "package_id": "post_residual_jogger_page19_acceleration_source_observation_import_001",
                "attribute": "acceleration_0_100",
                "id_range": [3336, 3361],
                "observations": 26,
            },
            {
                "package_id": "post_residual_jogger_page19_minimum_kerb_weight_source_observation_import_001",
                "attribute": "minimum_kerb_weight",
                "id_range": [3362, 3383],
                "observations": 22,
            },
            {
                "package_id": "post_residual_jogger_page19_fuel_lpg_capacity_source_observation_import_001",
                "attributes": [
                    "fuel_tank_capacity",
                    "lpg_vessel_capacity_total",
                    "lpg_vessel_filling_capacity",
                ],
                "id_range": [3384, 3425],
                "observations": 42,
            },
            {
                "package_id": "post_residual_jogger_page19_gross_vehicle_weight_source_observation_import_001",
                "attribute": "gross_vehicle_weight",
                "id_range": [3426, 3447],
                "observations": 22,
            },
            {
                "package_id": "post_residual_jogger_page19_braked_trailer_weight_non_hybrid_source_observation_import_001",
                "attribute": "braked_trailer_weight",
                "id_range": [3448, 3463],
                "observations": 16,
                "excluded_hybrid155_configurations": 6,
            },
        ],
        "existing_exact_coverage_preserved": [
            "maximum_torque",
            "gearbox",
            "injection",
            "engine_displacement",
            "cylinders_and_valves",
            "emission_standard",
            "front_suspension",
            "rear_suspension",
            "maximum_speed",
            "elasticity_80_120",
        ],
        "remaining_mass_boundaries": [
            {
                "code": "maximum_kerb_like_mislabeled_block",
                "printed_heading": "gross train weight",
                "source_values": {
                    "five_seat": [1230, 1312, 1335, 1373],
                    "seven_seat": [1261, 1342, 1364, 1405],
                },
                "classification": "ambiguous_source_label",
                "decision": "preserve_without_import_or_inferred_relabeling",
            },
            {
                "code": "gross_train_like_mislabeled_block",
                "printed_heading": "gross vehicle weight",
                "source_values": {
                    "five_seat": [2885, 2965, 2985, 2830],
                    "seven_seat": [3055, 3140, 3160, 3000],
                },
                "classification": "ambiguous_source_label",
                "decision": "preserve_without_import_or_inferred_relabeling",
            },
            {
                "code": "hybrid155_braked_trailer_source_conflict",
                "attribute": "braked_trailer_weight",
                "brochure_value_kg": 1200,
                "later_official_value_kg": 1000,
                "configuration_count": 6,
                "classification": "official_source_conflict",
                "decision": "retain_later_current_value_and_do_not_add_conflicting_brochure_observation",
            },
        ],
        "outside_mass_closure_follow_up": [
            {
                "code": "hybrid155_total_power_source_conflict",
                "brochure_value_kw": 105,
                "later_official_value_kw": 116,
            },
            {
                "code": "maximum_power_speed_ranges",
                "classification": "range_and_fuel_context_review_required",
            },
            {
                "code": "maximum_torque_speed_ranges",
                "classification": "range_context_review_required",
            },
            {
                "code": "energy_source_columns",
                "classification": "context_model_required",
            },
            {
                "code": "homologation_protocol",
                "classification": "context_model_required",
            },
        ],
        "closure_decision": {
            "safe_exact_scalar_imports_complete": True,
            "current_exact_values_overwritten": False,
            "printed_labels_corrected_by_inference": False,
            "official_source_conflicts_preserved": True,
            "mass_conflict_review_complete": True,
        },
        "next_package": next_package(),
    }


def render_markdown(data: dict[str, object]) -> str:
    return """# Jogger Page 19 Remaining Mass Conflict Closure\n\nStatus: **complete with preserved boundaries**  \nReviewed: **2026-07-30**\n\n## Closure result\n\nAll safe exact scalar imports selected from Jogger brochure page 19 are complete. Five append-only packages added **128 source-specific observations** without overwriting later official values.\n\n| Area | IDs | Observations | Result |\n|---|---:|---:|---|\n| 0–100 km/h acceleration | 3336–3361 | 26 | Imported |\n| Minimum kerb weight | 3362–3383 | 22 | Imported |\n| Petrol/LPG capacities | 3384–3425 | 42 | Imported |\n| Gross vehicle weight | 3426–3447 | 22 | Imported |\n| Non-Hybrid braked trailer weight | 3448–3463 | 16 | Imported |\n\n## Preserved mass boundaries\n\nTwo blocks remain unimported because the printed headings conflict with the magnitudes. The repository does not relabel source evidence by inference:\n\n- values `1230/1312/1335/1373` and `1261/1342/1364/1405` are printed under a gross-train heading but resemble maximum kerb weight;\n- values `2885/2965/2985/2830` and `3055/3140/3160/3000` are printed under a gross-vehicle heading but resemble gross vehicle plus trailer.\n\nHybrid 155 braked-trailer evidence also remains a deliberate non-import boundary: the brochure states **1200 kg**, while the later official MY26 source states **1000 kg** for all six current Hybrid 155 configurations.\n\n## Non-mass follow-up\n\nThe mass closure does not decide RPM range modeling, energy-source column semantics, homologation-protocol context or the Hybrid 155 total-power conflict. Those items move to **Jogger Page 19 Range and Context Follow-up Review**.\n\n## Decision\n\n- safe exact scalar imports complete;\n- no current value overwritten;\n- no inferred relabeling;\n- official conflicts remain visible;\n- page-19 mass review closed.\n"""


def render_review() -> str:
    return """# Review — Jogger page 19 remaining mass conflicts\n\nDate: 2026-07-30  \nPackage: `post_residual_jogger_page19_remaining_mass_conflict_closure_review_001`\n\n## Evidence reviewed\n\n- archived brochure `src_pl_jogger_brochure_20251217`, page 19;\n- later official comparison source `src_pl_jogger_price_my26_20260401`;\n- reviewed-fact reconciliation from PR #392;\n- completed scalar-import receipts covering IDs `3336–3463`.\n\n## Findings\n\nThe five completed imports account for 128 safe brochure-source observations. Existing exact coverage for torque, gearbox, injection, displacement, cylinders/valves, emissions, suspension, maximum speed and elasticity remains unchanged.\n\nThe two mislabeled mass blocks cannot be assigned to governed attributes without correcting the printed headings by inference. They therefore remain explicit source conflicts. The Hybrid 155 trailer row is also excluded because the later official value is 1000 kg rather than 1200 kg.\n\n## Closure\n\nThe page-19 mass tranche is closed with preserved boundaries. No master-data change is authorized by this review. Remaining RPM-range, context and Hybrid-power questions are handed to the next review package.\n"""


def update_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-30"
    state["phase"] = "Jogger Page 19 Remaining Mass Conflict Closure Review"
    state["current_package"] = {
        "package_id": "post_residual_jogger_page19_remaining_mass_conflict_closure_review_001",
        "kind": "review_closure",
        "name": "Jogger Page 19 Remaining Mass Conflict Closure Review",
        "status": "complete",
        "goal": "Confirm that every safely importable exact page-19 scalar fact is covered while preserving the two mislabeled mass blocks and the Hybrid 155 trailer discrepancy as explicit non-import boundaries.",
        "manifest_paths": [
            "data/reporting/jogger_page19_remaining_mass_conflict_closure.json",
            "data/reporting/jogger_page19_remaining_mass_conflict_closure.md",
            "project/reviews/jogger-page19-remaining-mass-conflict-closure-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = next_package()
    write_json(STATE, state)


def main() -> int:
    data = payload()
    write_json(REPORT_JSON, data)
    write(REPORT_MD, render_markdown(data))
    write(REVIEW_MD, render_review())
    update_state()
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
