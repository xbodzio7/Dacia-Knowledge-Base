#!/usr/bin/env python3
"""Materialize the Duster mini page 20 reviewed-fact reconciliation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
REPORTING = ROOT / "data/reporting"
REPORT_JSON = REPORTING / "duster_mini_technical_page20_reviewed_fact_reconciliation.json"
REPORT_MD = REPORTING / "duster_mini_technical_page20_reviewed_fact_reconciliation.md"
REVIEW_MD = ROOT / "project/reviews/duster-mini-technical-page20-reviewed-fact-reconciliation-2026-07-30.md"
STATE = ROOT / "project/state.json"
SOURCE = "src_pl_duster_mini_brochure_20251020"
SOURCE_SHA = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
AMBIGUITY = REPORTING / "duster_mini_technical_page20_ambiguity_review.json"
CHUNK1 = REPORTING / "duster_mini_technical_page20_unresolved_review_chunk1.json"
CHUNK2 = REPORTING / "duster_mini_technical_page20_unresolved_review_chunk2.json"

ECOG = {
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
}
MHEV = {
    "duster_iii_expression_mildhybrid140_4x2_manual",
    "duster_iii_extreme_mildhybrid140_4x2_manual",
    "duster_iii_journey_mildhybrid140_4x2_manual",
}
TARGETS = ECOG | MHEV
SAFE_GAPS = {
    "emission_standard": {"value": "euro_6e_bis", "count": 7},
    "particulate_filter": {"value": "true", "count": 7},
    "start_stop_system": {"value": "true", "count": 7},
    "eco_mode": {"value": "true", "count": 7},
    "gross_vehicle_weight": {"ecog_value": "1805", "mhev_value": "1830", "count": 7},
}


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader)


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: dict[str, object]) -> None:
    write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def next_package() -> dict[str, object]:
    return {
        "package_id": "post_residual_duster_mini_page20_exact_scalar_gap_import_001",
        "kind": "configuration_value_import",
        "name": "Duster Mini Page 20 Exact Scalar Gap Import",
        "status": "planned",
        "source_code": SOURCE,
        "source_page": 20,
        "goal": "Add 35 append-only source-specific observations across the seven exact manual 4x2 Duster configurations: Euro 6E bis, particulate filter, Start & Stop, Eco mode and gross vehicle weight. Preserve injection type as a fuel-context modeling deferral and keep every context-only/non-import decision unchanged.",
        "target_configurations": sorted(TARGETS),
        "attribute_counts": {
            "emission_standard": 7,
            "particulate_filter": 7,
            "start_stop_system": 7,
            "eco_mode": 7,
            "gross_vehicle_weight": 7,
        },
        "planned_value_id_start": 3464,
        "planned_value_id_end": 3498,
        "manifest_paths": [
            "data/imports/configuration_values/duster-mini-page20-emission-standard-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-particulate-filter-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-start-stop-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-eco-mode-20251020.json",
            "data/imports/configuration_values/duster-mini-page20-gross-vehicle-weight-20251020.json",
            "data/master/configuration_attribute_values.csv",
            "tests/test_duster_mini_page20_exact_scalar_gap_import.py",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
            "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
            "tests/test_verified_pdf_candidate_coverage_reconciliation.py",
            "tests/test_verified_pdf_candidate_residual_gap_prioritization.py",
            "tools/review_official_brochure_technical_gap_resolution_closure_20260726.py",
            "tests/test_official_brochure_technical_gap_resolution_closure.py",
            "README.md",
            "CHANGELOG.md",
            "project/ROADMAP.md",
            "project/SESSION_STATE.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }


def verify_source_reviews() -> dict[str, object]:
    ambiguity = load(AMBIGUITY)
    chunk1 = load(CHUNK1)
    chunk2 = load(CHUNK2)
    reports = (ambiguity, chunk1, chunk2)
    for report in reports:
        if report.get("status") != "complete":
            raise RuntimeError("source review is not complete")
        receipt = report.get("source_receipt")
        if not isinstance(receipt, dict):
            raise RuntimeError("source receipt missing")
        if receipt.get("source_code") != SOURCE or receipt.get("sha256") != SOURCE_SHA or receipt.get("page") != 20:
            raise RuntimeError("source receipt differs")
    if ambiguity.get("scope", {}).get("candidate_count") != 5:
        raise RuntimeError("ambiguity candidate count differs")
    if chunk1.get("scope", {}).get("candidate_count") != 40:
        raise RuntimeError("chunk-1 candidate count differs")
    if chunk2.get("scope", {}).get("candidate_count") != 20:
        raise RuntimeError("chunk-2 candidate count differs")
    if ambiguity.get("summary", {}).get("decision_counts") != {
        "covered_by_selected_evidence": 3,
        "partially_covered": 2,
    }:
        raise RuntimeError("ambiguity decision counts differ")
    if chunk1.get("summary", {}).get("decision_counts") != {
        "context_only_non_import": 16,
        "unresolved_signature_mismatch": 24,
    }:
        raise RuntimeError("chunk-1 decision counts differ")
    if chunk2.get("summary", {}).get("decision_counts") != {
        "context_only_non_import": 17,
        "unresolved_signature_mismatch": 3,
    }:
        raise RuntimeError("chunk-2 decision counts differ")
    return {"ambiguity": ambiguity, "chunk1": chunk1, "chunk2": chunk2}


def verify_targets() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, dict[str, str]]]:
    values = rows(MASTER / "configuration_attribute_values.csv")
    ranges = rows(MASTER / "configuration_attribute_value_ranges.csv")
    configurations = {row["code"]: row for row in rows(MASTER / "configurations.csv")}
    versions = {row["code"]: row for row in rows(MASTER / "versions.csv")}
    attributes = {row["code"]: row for row in rows(MASTER / "attributes.csv")}

    for code in TARGETS:
        row = configurations.get(code)
        if row is None or row.get("status") != "active":
            raise RuntimeError(f"active target missing: {code}")
        if versions.get(row.get("version_code", ""), {}).get("model_code") != "duster_iii":
            raise RuntimeError(f"target model differs: {code}")
        if row.get("transmission_type") != "manual":
            raise RuntimeError(f"target transmission differs: {code}")
    if Counter(configurations[code]["powertrain_label"] for code in TARGETS) != Counter({
        "Eco-G 120 4x2": 4,
        "mild hybrid 140 4x2": 3,
    }):
        raise RuntimeError("target powertrain distribution differs")

    expected_contracts = {
        "emission_standard": ("enum", "", "active"),
        "particulate_filter": ("boolean", "", "active"),
        "start_stop_system": ("boolean", "", "active"),
        "eco_mode": ("boolean", "", "active"),
        "gross_vehicle_weight": ("integer", "kg", "active"),
        "injection_type": ("enum", "", "active"),
    }
    for code, expected in expected_contracts.items():
        row = attributes.get(code)
        if row is None or (row.get("data_type"), row.get("unit"), row.get("status")) != expected:
            raise RuntimeError(f"attribute contract differs: {code}")

    for attribute in SAFE_GAPS:
        existing = [row for row in values if row["configuration_code"] in TARGETS and row["attribute_code"] == attribute]
        if existing:
            raise RuntimeError(f"planned gap already covered: {attribute}")
    injection = [row for row in values if row["configuration_code"] in TARGETS and row["attribute_code"] == "injection_type"]
    if injection:
        raise RuntimeError("Duster injection context unexpectedly already modeled")
    return values, ranges, configurations


def verify_current_coverage(values: list[dict[str, str]], ranges: list[dict[str, str]]) -> dict[str, object]:
    source_values = [row for row in values if row["source_code"] == SOURCE]
    source_ranges = [row for row in ranges if row["source_code"] == SOURCE]
    expected_source_counts = Counter({
        "boot_capacity": 64,
        "front_brake_type": 10,
        "front_overhang": 10,
        "front_track": 10,
        "gross_train_weight": 10,
        "ground_clearance": 10,
        "maximum_kerb_weight": 10,
        "overall_length": 10,
        "overall_width": 10,
        "overall_width_with_mirrors": 10,
        "rear_brake_type": 10,
        "rear_overhang": 10,
        "rear_track": 10,
        "roof_height_with_rails": 10,
        "standard_tyre_specification": 10,
        "steering_type": 10,
        "turning_circle_wheel_track": 10,
        "unbraked_trailer_weight": 10,
        "wheelbase": 10,
    })
    if len(source_values) != 244 or Counter(row["attribute_code"] for row in source_values) != expected_source_counts:
        raise RuntimeError("same-source scalar receipt differs")
    if len(source_ranges) != 10 or Counter(row["attribute_code"] for row in source_ranges) != Counter({"payload": 10}):
        raise RuntimeError("same-source range receipt differs")

    target_values = [row for row in values if row["configuration_code"] in TARGETS]
    def selected(attribute: str) -> list[dict[str, str]]:
        return [row for row in target_values if row["attribute_code"] == attribute]

    coverage_rules = {
        "engine_power": (TARGETS, {"84", "90", "103"}),
        "engine_torque": (TARGETS, {"200", "230"}),
        "engine_displacement": (TARGETS, {"1199"}),
        "number_of_cylinders": (TARGETS, {"3"}),
        "total_valve_count": (TARGETS, {"12"}),
        "top_speed": (TARGETS, {"180"}),
        "acceleration_0_100": (TARGETS, {"11", "9.4"}),
        "braked_trailer_weight": (TARGETS, {"1500"}),
    }
    for attribute, (targets, allowed_values) in coverage_rules.items():
        current = selected(attribute)
        if {row["configuration_code"] for row in current} != targets:
            raise RuntimeError(f"later exact coverage target set differs: {attribute}")
        if not {row["value"] for row in current} <= allowed_values:
            raise RuntimeError(f"later exact coverage values differ: {attribute}")

    fuel_tanks = selected("fuel_tank_capacity")
    if {row["configuration_code"] for row in fuel_tanks} != TARGETS:
        raise RuntimeError("fuel-tank target coverage differs")
    if {row["value"] for row in fuel_tanks} != {"50"}:
        raise RuntimeError("fuel-tank values differ")
    if Counter(row["fuel_type_code"] for row in fuel_tanks) != Counter({"lpg": 4, "petrol": 4, "": 3}):
        raise RuntimeError("fuel-tank context distribution differs")

    same_source_target = [row for row in source_values if row["configuration_code"] in TARGETS]
    if {row["configuration_code"] for row in same_source_target if row["attribute_code"] == "unbraked_trailer_weight"} != TARGETS:
        raise RuntimeError("same-source unbraked trailer coverage differs")
    if {row["configuration_code"] for row in same_source_target if row["attribute_code"] == "front_brake_type"} != TARGETS:
        raise RuntimeError("same-source front-brake coverage differs")
    if {row["configuration_code"] for row in same_source_target if row["attribute_code"] == "maximum_kerb_weight"} != TARGETS:
        raise RuntimeError("same-source maximum-kerb coverage differs")
    if {row["configuration_code"] for row in source_ranges if row["configuration_code"] in TARGETS} != TARGETS:
        raise RuntimeError("same-source payload coverage differs")

    return {
        "same_source_scalar_values": 244,
        "same_source_range_values": 10,
        "same_source_candidate_decisions_closed": 10,
        "later_exact_candidate_decisions_closed": 8,
        "configuration_identity_candidate_decisions_closed": 2,
        "import_ready_candidate_decisions": 5,
        "context_model_required_candidate_decisions": 2,
        "explicit_non_import_or_context_candidate_decisions": 38,
    }


def build_payload(reviews: dict[str, object], coverage: dict[str, object]) -> dict[str, object]:
    return {
        "version": 1,
        "kind": "duster_mini_technical_page20_reviewed_fact_reconciliation",
        "reviewed_on": "2026-07-30",
        "status": "complete_with_import_handoff",
        "package_id": "post_residual_duster_mini_technical_page20_reviewed_fact_reconciliation_001",
        "source": {
            "source_code": SOURCE,
            "file_path": "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf",
            "sha256": SOURCE_SHA,
            "page": 20,
            "observation_date": "2025-10-20",
        },
        "source_review_packages": ["residual_gap_003", "residual_gap_020", "residual_gap_021"],
        "scope": {
            "reviewed_candidates": 65,
            "ambiguity_candidates": 5,
            "unresolved_candidates": 60,
            "exact_manual_target_configurations": 7,
        },
        "authored_decision_receipts": {
            "ambiguity": reviews["ambiguity"]["summary"],
            "unresolved_chunk_1": reviews["chunk1"]["summary"],
            "unresolved_chunk_2": reviews["chunk2"]["summary"],
        },
        "current_master_receipts": coverage,
        "candidate_reconciliation": {
            "current_exact_same_source_coverage": {
                "candidate_count": 10,
                "groups": [
                    "steering ratio and turning circle",
                    "maximum kerb weight",
                    "payload range",
                    "front brake specification",
                    "unbraked trailer weight",
                    "three cargo-capacity rows",
                ],
            },
            "current_exact_later_source_coverage": {
                "candidate_count": 8,
                "groups": [
                    "maximum power",
                    "maximum torque",
                    "engine displacement",
                    "cylinders and valves",
                    "maximum speed",
                    "0-100 km/h acceleration",
                    "fuel tank capacities",
                    "braked trailer weight",
                ],
            },
            "current_configuration_identity_coverage": {
                "candidate_count": 2,
                "groups": ["4x2 drivetrain", "manual six-speed gearbox"],
            },
            "import_ready_exact_gap": {
                "candidate_count": 5,
                "planned_observation_count": 35,
                "attributes": SAFE_GAPS,
                "target_configurations": sorted(TARGETS),
            },
            "context_model_required": {
                "candidate_count": 2,
                "groups": [
                    {
                        "code": "energy_source_columns",
                        "decision": "preserve_as_multi-column context; existing configuration/fuel modeling already represents the powertrain boundary",
                    },
                    {
                        "code": "injection_type_direct_for_dual_fuel_ecog",
                        "decision": "defer because the source row is unscoped while the repository governs injection_type by fuel context for dual-fuel configurations",
                    },
                ],
            },
            "explicit_non_import_or_context": {
                "candidate_count": 38,
                "groups": [
                    "all 33 originally authored context-only candidates",
                    "fully-electric-driving dash cells",
                    "traction-battery dash fragment",
                    "WLTP test-protocol label",
                    "country-dependent CO2 continuation",
                    "country-dependent combined-consumption continuation",
                ],
            },
        },
        "partition_check": {
            "candidate_count": 65,
            "classified_once": True,
            "class_counts": {
                "current_exact_same_source_coverage": 10,
                "current_exact_later_source_coverage": 8,
                "current_configuration_identity_coverage": 2,
                "import_ready_exact_gap": 5,
                "context_model_required": 2,
                "explicit_non_import_or_context": 38,
            },
        },
        "closure_decision": {
            "source_review_reopened": False,
            "master_data_changed": False,
            "automatic_promotion_used": False,
            "country_dependent_values_invented": False,
            "incomplete_rows_promoted": False,
            "safe_exact_import_handoff_created": True,
        },
        "next_package": next_package(),
    }


def render_markdown() -> str:
    return """# Duster Mini Technical Page 20 Reviewed Fact Reconciliation\n\nStatus: **complete with import handoff**  \nReviewed: **2026-07-30**\n\n## Scope\n\nThe reconciliation reuses all 65 authored decisions from ambiguity package `003` and unresolved packages `020–021`. It compares them with the current exact master data for the seven manual 4×2 Eco-G 120 and mild hybrid 140 configurations.\n\n## Candidate partition\n\n| Classification | Candidates | Result |\n|---|---:|---|\n| Current exact same-source coverage | 10 | Closed |\n| Current exact later-source coverage | 8 | Closed |\n| Current configuration identity | 2 | Closed |\n| Import-ready exact gap | 5 | Handoff: 35 observations |\n| Context model required | 2 | Deferred |\n| Explicit non-import or context | 38 | Preserved |\n| **Total** | **65** | Classified once |\n\n## Import-ready gaps\n\nEach exact row applies to the four Eco-G 120 manual and three mild hybrid 140 manual configurations:\n\n- emission standard: `euro_6e_bis`;\n- particulate filter: `true`;\n- Start & Stop: `true`;\n- Eco mode: `true`;\n- gross vehicle weight: `1805 kg` for Eco-G and `1830 kg` for mild hybrid 140.\n\nThe follow-up import will add **35 append-only observations**, planned as IDs `3464–3498`.\n\n## Preserved boundaries\n\nThe unscoped `Bezpośredni` injection row is not imported for dual-fuel Eco-G because the governed model distinguishes injection by fuel context. Energy-source columns remain powertrain context. Dash cells, country-dependent CO₂/consumption text, incomplete rows and explanatory footnotes remain non-values.\n\n## Handoff\n\n**Duster Mini Page 20 Exact Scalar Gap Import**\n"""


def render_review() -> str:
    return """# Review — Duster mini page 20 reviewed facts\n\nDate: 2026-07-30  \nPackage: `post_residual_duster_mini_technical_page20_reviewed_fact_reconciliation_001`\n\n## Inputs\n\n- `residual_gap_003`: five ambiguity candidates;\n- `residual_gap_020`: first forty unresolved candidates;\n- `residual_gap_021`: final twenty unresolved candidates;\n- current source-specific scalar/range receipts and later official Duster observations.\n\n## Result\n\nAll 65 candidates are classified exactly once. Twenty are closed by existing exact values or configuration identity. Thirty-eight remain context/non-import. Two require context modeling rather than an unscoped import. Five exact candidate rows remain import-ready and expand to 35 source-specific observations across seven exact manual configurations.\n\n## Safety boundary\n\nThe reconciliation changes no master data and generates no import spec. The next package may import only Euro 6E bis, particulate filter, Start & Stop, Eco mode and gross vehicle weight. Injection type remains deferred because the page row does not distinguish petrol and LPG injection semantics.\n"""


def update_state() -> None:
    state = load(STATE)
    state["updated_on"] = "2026-07-30"
    state["phase"] = "Duster Mini Technical Page 20 Reviewed Fact Reconciliation"
    state["current_package"] = {
        "package_id": "post_residual_duster_mini_technical_page20_reviewed_fact_reconciliation_001",
        "kind": "review_closure",
        "name": "Duster Mini Technical Page 20 Reviewed Fact Reconciliation",
        "status": "complete",
        "goal": "Reconcile all 65 authored Duster page-20 technical candidates against current exact master data and produce a narrow 35-observation import handoff without changing master data in the reconciliation package.",
        "manifest_paths": [
            "data/reporting/duster_mini_technical_page20_reviewed_fact_reconciliation.json",
            "data/reporting/duster_mini_technical_page20_reviewed_fact_reconciliation.md",
            "project/reviews/duster-mini-technical-page20-reviewed-fact-reconciliation-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = next_package()
    write_json(STATE, state)


def main() -> int:
    reviews = verify_source_reviews()
    values, ranges, _ = verify_targets()
    coverage = verify_current_coverage(values, ranges)
    report = build_payload(reviews, coverage)
    if sum(report["partition_check"]["class_counts"].values()) != 65:
        raise RuntimeError("candidate partition does not sum to 65")
    write_json(REPORT_JSON, report)
    write(REPORT_MD, render_markdown())
    write(REVIEW_MD, render_review())
    update_state()
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
