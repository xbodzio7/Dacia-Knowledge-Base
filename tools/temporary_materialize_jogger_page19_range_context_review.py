#!/usr/bin/env python3
"""Materialize the Jogger page 19 range and context follow-up review."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
REPORT_JSON = ROOT / "data/reporting/jogger_page19_range_context_follow_up_review.json"
REPORT_MD = ROOT / "data/reporting/jogger_page19_range_context_follow_up_review.md"
REVIEW_MD = ROOT / "project/reviews/jogger-page19-range-context-follow-up-review-2026-07-30.md"
STATE = ROOT / "project/state.json"
SOURCE = "src_pl_jogger_brochure_20251217"
LATER_SOURCE = "src_pl_jogger_price_my26_20260401"


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: dict[str, object]) -> None:
    write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def queue_reentry_package() -> dict[str, object]:
    return {
        "package_id": "post_residual_verified_pdf_queue_reentry_review_001",
        "kind": "review_closure",
        "name": "Verified PDF Residual Queue Re-entry Review",
        "status": "planned",
        "goal": "Reconcile the remaining verified-PDF residual packages after complete Jogger page-19 closure, exclude already closed and explicit non-import boundaries, and select the next genuinely actionable package without reopening resolved work.",
        "manifest_paths": [
            "data/reporting/verified_pdf_residual_queue_reentry_review.json",
            "data/reporting/verified_pdf_residual_queue_reentry_review.md",
            "project/reviews/verified-pdf-residual-queue-reentry-review-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }


def verify_repository_receipts() -> dict[str, object]:
    ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
    values = rows(MASTER / "configuration_attribute_values.csv")

    brochure_ranges = [row for row in ranges if 177 <= int(row["id"]) <= 234]
    if len(brochure_ranges) != 58:
        raise RuntimeError(f"expected 58 page-19 RPM ranges, found {len(brochure_ranges)}")
    if [int(row["id"]) for row in brochure_ranges] != list(range(177, 235)):
        raise RuntimeError("page-19 RPM range IDs are not contiguous")
    if {row["source_code"] for row in brochure_ranges} != {SOURCE}:
        raise RuntimeError("page-19 RPM range source differs")
    if {row["observation_date"] for row in brochure_ranges} != {"2025-12-17"}:
        raise RuntimeError("page-19 RPM range observation date differs")
    expected_attributes = Counter({"max_power_rpm": 26, "max_torque_rpm": 32})
    if Counter(row["attribute_code"] for row in brochure_ranges) != expected_attributes:
        raise RuntimeError("page-19 RPM range attribute counts differ")

    max_power = [row for row in brochure_ranges if row["attribute_code"] == "max_power_rpm"]
    max_torque = [row for row in brochure_ranges if row["attribute_code"] == "max_torque_rpm"]
    if Counter(row["fuel_type_code"] for row in max_power) != Counter({"petrol": 16, "lpg": 10}):
        raise RuntimeError("max-power RPM fuel distribution differs")
    if Counter(row["fuel_type_code"] for row in max_torque) != Counter({"petrol": 16, "lpg": 10, "": 6}):
        raise RuntimeError("max-torque RPM fuel distribution differs")

    old_ecog_petrol_power = [
        row for row in max_power
        if row["fuel_type_code"] == "petrol" and "ecog120" in row["configuration_code"]
    ]
    later_ecog_petrol_power = [
        row for row in ranges
        if row["source_code"] == LATER_SOURCE
        and row["attribute_code"] == "max_power_rpm"
        and row["fuel_type_code"] == "petrol"
        and "ecog120" in row["configuration_code"]
    ]
    if len(old_ecog_petrol_power) != 10 or {
        (row["minimum_value"], row["maximum_value"]) for row in old_ecog_petrol_power
    } != {("4500", "5000")}:
        raise RuntimeError("brochure Eco-G petrol max-power range differs")
    if len(later_ecog_petrol_power) != 10 or {
        (row["minimum_value"], row["maximum_value"]) for row in later_ecog_petrol_power
    } != {("4500", "5750")}:
        raise RuntimeError("later Eco-G petrol max-power range differs")

    hybrid_power_rpm = [
        row for row in values
        if 2285 <= int(row["id"]) <= 2290
        and row["source_code"] == SOURCE
        and row["attribute_code"] == "max_power_rpm"
    ]
    if len(hybrid_power_rpm) != 6 or {row["value"] for row in hybrid_power_rpm} != {"5600"}:
        raise RuntimeError("Hybrid 155 max-power RPM receipt differs")

    later_hybrid_total = [
        row for row in values
        if row["source_code"] == LATER_SOURCE
        and row["attribute_code"] == "hybrid_system_power_total"
        and "hybrid155" in row["configuration_code"]
    ]
    brochure_hybrid_total = [
        row for row in values
        if row["source_code"] == SOURCE
        and row["attribute_code"] == "hybrid_system_power_total"
        and "hybrid155" in row["configuration_code"]
    ]
    if len(later_hybrid_total) != 6 or {row["value"] for row in later_hybrid_total} != {"116"}:
        raise RuntimeError("later Hybrid 155 total-power receipt differs")
    if brochure_hybrid_total:
        raise RuntimeError("conflicting brochure Hybrid 155 total power was imported")

    return {
        "rpm_range_count": 58,
        "max_power_range_count": 26,
        "max_torque_range_count": 32,
        "hybrid_max_power_rpm_scalar_count": 6,
        "ecog_petrol_power_conflict_configuration_count": 10,
        "hybrid_total_power_conflict_configuration_count": 6,
    }


def payload(receipts: dict[str, object]) -> dict[str, object]:
    return {
        "version": 1,
        "kind": "jogger_page19_range_context_follow_up_review",
        "reviewed_on": "2026-07-30",
        "status": "complete_with_existing_coverage_and_preserved_context",
        "package_id": "post_residual_jogger_page19_range_context_follow_up_review_001",
        "source": {
            "source_code": SOURCE,
            "file_path": "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf",
            "sha256": "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6",
            "page": 19,
            "observation_date": "2025-12-17",
        },
        "comparison_source": {
            "source_code": LATER_SOURCE,
            "observation_date": "2026-04-01",
        },
        "repository_receipts": receipts,
        "range_coverage": [
            {
                "attribute": "max_power_rpm",
                "status": "existing_source_specific_coverage",
                "range_ids": [177, 202],
                "observations": 26,
                "distribution": {
                    "tce110_petrol": 6,
                    "ecog120_lpg": 10,
                    "ecog120_petrol": 10,
                },
                "preserved_conflict": "Eco-G petrol brochure upper endpoint is 5000 rpm; the later official upper endpoint is 5750 rpm. Both dated source observations coexist and the later source remains current.",
            },
            {
                "attribute": "max_torque_rpm",
                "status": "existing_source_specific_coverage",
                "range_ids": [203, 234],
                "observations": 32,
                "distribution": {
                    "tce110_petrol": 6,
                    "ecog120_lpg": 10,
                    "ecog120_petrol": 10,
                    "hybrid155_combustion_unscoped": 6,
                },
                "preserved_context": "The Hybrid 155 range describes the combustion engine; no electric-motor speed is stated and none is inferred.",
            },
            {
                "attribute": "max_power_rpm",
                "status": "existing_scalar_coverage",
                "value_ids": [2285, 2290],
                "observations": 6,
                "value_rpm": 5600,
                "context": "Hybrid 155 combustion-engine maximum-power speed.",
            },
        ],
        "context_decisions": [
            {
                "code": "energy_source_columns",
                "decision": "no_new_scalar_attribute",
                "reason": "Petrol/LPG distinctions are already represented by fuel_type_code and Hybrid architecture is represented by separate governed component/system fields; the printed multi-column row is not one scalar fact.",
            },
            {
                "code": "homologation_protocol_wltp_footnote",
                "decision": "context_only",
                "reason": "WLTP(2) is explanatory protocol context and no approved governed homologation-protocol attribute exists in the current model.",
            },
            {
                "code": "electric_motor_speed_dash_cells",
                "decision": "explicit_non_import",
                "reason": "Dash cells do not state a numeric electric-motor speed and are not promoted to zero or not-applicable values by inference.",
            },
        ],
        "official_source_conflicts": [
            {
                "code": "hybrid155_total_power_105_vs_116",
                "attribute": "hybrid_system_power_total",
                "brochure_value_kw": 105,
                "later_official_value_kw": 116,
                "configuration_count": 6,
                "decision": "retain_later_current_value_without_importing_conflicting_brochure_total",
                "notes": "The brochure's 5600 rpm combustion-engine speed remains valid as its own observation and does not authorize promotion of the conflicting 105 kW total.",
            },
            {
                "code": "ecog120_petrol_max_power_rpm_5000_vs_5750",
                "attribute": "max_power_rpm",
                "brochure_range": [4500, 5000],
                "later_official_range": [4500, 5750],
                "configuration_count": 10,
                "decision": "preserve_both_dated_source_ranges_with_later_current_precedence",
            },
        ],
        "closure_decision": {
            "new_master_data_required": False,
            "new_range_import_required": False,
            "new_domain_attribute_required": False,
            "current_exact_values_overwritten": False,
            "context_promoted_by_inference": False,
            "page19_range_and_context_review_complete": True,
            "jogger_page19_follow_up_chain_complete": True,
        },
        "next_package": queue_reentry_package(),
    }


def render_markdown(data: dict[str, object]) -> str:
    return """# Jogger Page 19 Range and Context Follow-up Review\n\nStatus: **complete with existing coverage and preserved context**  \nReviewed: **2026-07-30**\n\n## Result\n\nNo new range or scalar import is required. The repository already contains **58 source-specific RPM ranges** from page 19 and six Hybrid 155 scalar values at **5600 rpm**.\n\n| Coverage | IDs | Count | Decision |\n|---|---:|---:|---|\n| Maximum-power RPM ranges | 177–202 | 26 | Existing coverage |\n| Maximum-torque RPM ranges | 203–234 | 32 | Existing coverage |\n| Hybrid 155 maximum-power RPM | 2285–2290 | 6 | Existing scalar coverage |\n\n## Preserved source differences\n\n- Eco-G 120 petrol maximum-power range is `4500–5000 rpm` in the brochure and `4500–5750 rpm` in the later official source for ten configurations. Both dated observations coexist; the later source keeps current precedence.\n- Hybrid 155 total system power is `105 kW` in the brochure and `116 kW` in the later official source. The six current `116 kW` values remain authoritative; no conflicting brochure total is imported.\n\n## Context boundaries\n\n- fuel and energy columns are represented through governed fuel context and separate Hybrid fields, not a synthetic combined scalar;\n- `WLTP(2)` remains explanatory protocol context because there is no approved homologation-protocol attribute;\n- dash cells for electric-motor speed remain non-values and are not converted by inference.\n\n## Closure\n\nThe Jogger page-19 follow-up chain is complete. No schema or master-data change is needed. Work returns to a verified-PDF residual queue re-entry review to select the next genuinely actionable package without reopening closed conflicts.\n"""


def render_review() -> str:
    return """# Review — Jogger page 19 ranges and context\n\nDate: 2026-07-30  \nPackage: `post_residual_jogger_page19_range_context_follow_up_review_001`\n\n## Evidence\n\n- page-19 reviewed-fact reconciliation;\n- range receipts `177–234`;\n- Hybrid maximum-power-speed values `2285–2290`;\n- later official MY26 RPM ranges and Hybrid system-power values.\n\n## Findings\n\nAll reviewed RPM observations already exist. The only material RPM source difference is the Eco-G petrol maximum-power upper endpoint (`5000` versus later `5750`), which is correctly preserved as two dated observations. Hybrid 155 maximum-power speed `5600 rpm` is independently covered and does not resolve the total-power conflict.\n\nEnergy-source columns and WLTP footnotes are context, not missing scalar values. The brochure's Hybrid 155 total of `105 kW` conflicts with six later `116 kW` observations and remains unimported.\n\n## Closure\n\nNo import, schema change or new domain decision is required. The Jogger page-19 chain is closed and control returns to global residual-queue selection.\n"""


def update_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-30"
    state["phase"] = "Jogger Page 19 Range and Context Follow-up Review"
    state["current_package"] = {
        "package_id": "post_residual_jogger_page19_range_context_follow_up_review_001",
        "kind": "review_closure",
        "name": "Jogger Page 19 Range and Context Follow-up Review",
        "status": "complete",
        "goal": "Close remaining page-19 RPM-range and context questions by verifying existing range/scalar coverage, preserving official-source conflicts and refusing inference-based context promotion.",
        "manifest_paths": [
            "data/reporting/jogger_page19_range_context_follow_up_review.json",
            "data/reporting/jogger_page19_range_context_follow_up_review.md",
            "project/reviews/jogger-page19-range-context-follow-up-review-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = queue_reentry_package()
    write_json(STATE, state)


def main() -> int:
    receipts = verify_repository_receipts()
    data = payload(receipts)
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
