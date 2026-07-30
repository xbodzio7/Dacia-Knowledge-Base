#!/usr/bin/env python3
"""Materialize the Duster mini page 20 exact scalar import closure review."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SOURCE = "src_pl_duster_mini_brochure_20251020"
SOURCE_SHA = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
PDF = ROOT / "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf"
RECONCILIATION = ROOT / "data/reporting/duster_mini_technical_page20_reviewed_fact_reconciliation.json"
REPORT_JSON = ROOT / "data/reporting/duster_mini_page20_exact_scalar_import_closure.json"
REPORT_MD = ROOT / "data/reporting/duster_mini_page20_exact_scalar_import_closure.md"
REVIEW_MD = ROOT / "project/reviews/duster-mini-page20-exact-scalar-import-closure-2026-07-30.md"

ECOG = [
    "duster_iii_essential_ecog120_4x2_manual",
    "duster_iii_expression_ecog120_4x2_manual",
    "duster_iii_extreme_ecog120_4x2_manual",
    "duster_iii_journey_ecog120_4x2_manual",
]
MHEV = [
    "duster_iii_expression_mildhybrid140_4x2_manual",
    "duster_iii_extreme_mildhybrid140_4x2_manual",
    "duster_iii_journey_mildhybrid140_4x2_manual",
]
TARGETS = ECOG + MHEV
EXPECTED_ATTRIBUTES = {
    "emission_standard": {code: "euro_6e_bis" for code in TARGETS},
    "particulate_filter": {code: "true" for code in TARGETS},
    "start_stop_system": {code: "true" for code in TARGETS},
    "eco_mode": {code: "true" for code in TARGETS},
    "gross_vehicle_weight": {
        **{code: "1805" for code in ECOG},
        **{code: "1830" for code in MHEV},
    },
}
SPECS = {
    "emission_standard": "duster-mini-page20-emission-standard-20251020.json",
    "particulate_filter": "duster-mini-page20-particulate-filter-20251020.json",
    "start_stop_system": "duster-mini-page20-start-stop-20251020.json",
    "eco_mode": "duster-mini-page20-eco-mode-20251020.json",
    "gross_vehicle_weight": "duster-mini-page20-gross-vehicle-weight-20251020.json",
}
EXPECTED_ID_RANGES = {
    "emission_standard": [3464, 3470],
    "particulate_filter": [3471, 3477],
    "start_stop_system": [3478, 3484],
    "eco_mode": [3485, 3491],
    "gross_vehicle_weight": [3492, 3498],
}
NEW_SLOTS = {
    ("eco_mode", ""),
    ("emission_standard", ""),
    ("gross_vehicle_weight", ""),
    ("particulate_filter", ""),
    ("start_stop_system", ""),
}


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: dict[str, object]) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def verify_source() -> dict[str, str]:
    if hashlib.sha256(PDF.read_bytes()).hexdigest() != SOURCE_SHA:
        raise RuntimeError("Duster mini brochure SHA-256 differs")
    sources = [row for row in read_csv(MASTER / "sources.csv") if row["code"] == SOURCE]
    if len(sources) != 1:
        raise RuntimeError("expected exactly one registered Duster mini source")
    row = sources[0]
    if row["sha256"] != SOURCE_SHA:
        raise RuntimeError("registered Duster mini source SHA-256 differs")
    if row["file_path"] != "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf":
        raise RuntimeError("registered Duster mini source path differs")
    return row


def verify_specs() -> list[dict[str, object]]:
    receipts: list[dict[str, object]] = []
    imports = ROOT / "data/imports/configuration_values"
    for attribute, filename in SPECS.items():
        path = imports / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected_start, expected_end = EXPECTED_ID_RANGES[attribute]
        if payload["id_start"] != expected_start:
            raise RuntimeError(f"{filename}: id_start differs")
        if payload["attribute_code"] != attribute:
            raise RuntimeError(f"{filename}: attribute differs")
        if payload["observation_date"] != "2025-10-20":
            raise RuntimeError(f"{filename}: observation date differs")
        if payload["source_page"] != 20:
            raise RuntimeError(f"{filename}: source page differs")
        actual = {row["configuration_code"]: row["value"] for row in payload["rows"]}
        if actual != EXPECTED_ATTRIBUTES[attribute]:
            raise RuntimeError(f"{filename}: exact row values differ")
        if {row["source_code"] for row in payload["rows"]} != {SOURCE}:
            raise RuntimeError(f"{filename}: source set differs")
        receipts.append(
            {
                "attribute": attribute,
                "spec_path": f"data/imports/configuration_values/{filename}",
                "id_range": [expected_start, expected_end],
                "observations": 7,
                "values": sorted(set(actual.values())),
            }
        )
    return receipts


def verify_master_receipt() -> list[dict[str, str]]:
    values = read_csv(MASTER / "configuration_attribute_values.csv")
    selected = sorted(
        [row for row in values if 3464 <= int(row["id"]) <= 3498],
        key=lambda row: int(row["id"]),
    )
    if [int(row["id"]) for row in selected] != list(range(3464, 3499)):
        raise RuntimeError("Duster page-20 closure ID receipt differs")
    if Counter(row["attribute_code"] for row in selected) != Counter(
        {attribute: 7 for attribute in EXPECTED_ATTRIBUTES}
    ):
        raise RuntimeError("Duster page-20 closure attribute distribution differs")
    if {row["configuration_code"] for row in selected} != set(TARGETS):
        raise RuntimeError("Duster page-20 closure target set differs")
    if {row["source_code"] for row in selected} != {SOURCE}:
        raise RuntimeError("Duster page-20 closure source set differs")
    if {row["observation_date"] for row in selected} != {"2025-10-20"}:
        raise RuntimeError("Duster page-20 closure observation date differs")
    by_attribute: dict[str, dict[str, str]] = {}
    for row in selected:
        by_attribute.setdefault(row["attribute_code"], {})[row["configuration_code"]] = row["value"]
    if by_attribute != EXPECTED_ATTRIBUTES:
        raise RuntimeError("Duster page-20 closure exact values differ")
    injection = [
        row
        for row in values
        if row["source_code"] == SOURCE
        and row["configuration_code"] in TARGETS
        and row["attribute_code"] == "injection_type"
    ]
    if injection:
        raise RuntimeError("unscoped injection entered the Duster page-20 source receipt")
    return selected


def verify_reconciliation() -> dict[str, object]:
    payload = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    if payload["partition_check"] != {
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
    }:
        raise RuntimeError("Duster reconciliation partition differs")
    handoff = payload["candidate_reconciliation"]["import_ready_exact_gap"]
    if handoff["candidate_count"] != 5 or handoff["planned_observation_count"] != 35:
        raise RuntimeError("Duster reconciliation import handoff differs")
    if set(handoff["attributes"]) != set(EXPECTED_ATTRIBUTES):
        raise RuntimeError("Duster reconciliation handoff attribute set differs")
    if set(handoff["target_configurations"]) != set(TARGETS):
        raise RuntimeError("Duster reconciliation handoff target set differs")
    context = payload["candidate_reconciliation"]["context_model_required"]
    context_codes = {row["code"] for row in context["groups"]}
    if context_codes != {"energy_source_columns", "injection_type_direct_for_dual_fuel_ecog"}:
        raise RuntimeError("Duster reconciliation context deferrals differ")
    return payload


def verify_reporting_scopes() -> dict[str, object]:
    scopes: dict[str, object] = {}
    expected = {
        "duster_ecog120_completeness.json": {"configurations": 4, "technical_slots": 42},
        "duster_mildhybrid140_4x2_completeness.json": {"configurations": 3, "technical_slots": 39},
    }
    for filename, contract in expected.items():
        payload = json.loads((ROOT / "data/reporting" / filename).read_text(encoding="utf-8"))
        actual_slots = {
            (row["attribute_code"], row.get("fuel_type_code", ""))
            for row in payload["technical_slots"]
        }
        if not NEW_SLOTS <= actual_slots:
            raise RuntimeError(f"{filename}: new technical slots are absent")
        if len(payload["configurations"]) != contract["configurations"]:
            raise RuntimeError(f"{filename}: configuration count differs")
        if len(payload["technical_slots"]) != contract["technical_slots"]:
            raise RuntimeError(f"{filename}: technical slot count differs")
        scopes[filename] = contract
    return scopes


def next_package() -> dict[str, object]:
    return {
        "package_id": "post_residual_verified_pdf_queue_reentry_review_002",
        "kind": "review_closure",
        "name": "Verified PDF Residual Queue Re-entry Review II",
        "status": "planned",
        "goal": "Rebuild the verified-PDF residual queue against current later reconciliation, import and closure evidence; exclude the completed Bigster, Jogger and Duster technical boundaries; and select the first remaining actionable stable source/model/domain/page boundary without reopening explicit non-import decisions.",
        "manifest_paths": [
            "data/reporting/verified_pdf_residual_queue_reentry_review.json",
            "data/reporting/verified_pdf_residual_queue_reentry_review.md",
            "project/reviews/verified-pdf-residual-queue-reentry-review-2026-07-31.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }


def build_report(spec_receipts: list[dict[str, object]], reporting_scopes: dict[str, object]) -> dict[str, object]:
    return {
        "version": 1,
        "kind": "duster_mini_page20_exact_scalar_import_closure",
        "reviewed_on": "2026-07-30",
        "status": "complete_with_preserved_boundaries",
        "package_id": "post_residual_duster_mini_page20_exact_scalar_gap_import_closure_001",
        "source": {
            "source_code": SOURCE,
            "file_path": "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf",
            "sha256": SOURCE_SHA,
            "page": 20,
            "observation_date": "2025-10-20",
        },
        "scope": {
            "reviewed_candidates": 65,
            "import_ready_candidate_decisions": 5,
            "imported_observations": 35,
            "target_configurations": 7,
            "import_specs": 5,
        },
        "completed_import_receipts": spec_receipts,
        "master_receipt": {
            "id_range": [3464, 3498],
            "observations": 35,
            "attribute_counts": {attribute: 7 for attribute in EXPECTED_ATTRIBUTES},
            "configuration_counts": {"ecog120_4x2_manual": 4, "mildhybrid140_4x2_manual": 3},
            "source_code": SOURCE,
            "observation_date": "2025-10-20",
        },
        "reporting_scope_receipts": reporting_scopes,
        "reconciliation_closure": {
            "candidate_partition_preserved": True,
            "import_ready_candidate_decisions_closed": 5,
            "planned_observations_materialized": 35,
            "remaining_context_model_required": 2,
            "remaining_explicit_non_import_or_context": 38,
            "remaining_import_ready_exact_gaps": 0,
        },
        "preserved_boundaries": [
            {
                "code": "energy_source_columns",
                "classification": "context_model_required",
                "decision": "preserve multi-column powertrain context without promoting a duplicate scalar",
            },
            {
                "code": "injection_type_direct_for_dual_fuel_ecog",
                "classification": "fuel_context_model_required",
                "decision": "do not import the unscoped direct-injection row for dual-fuel Eco-G configurations",
            },
            {
                "code": "explicit_non_import_or_context",
                "candidate_count": 38,
                "decision": "retain all authored dash, continuation, protocol, country-dependent and incomplete-row boundaries",
            },
        ],
        "closure_decision": {
            "safe_exact_scalar_import_complete": True,
            "master_values_overwritten": False,
            "automatic_promotion_used": False,
            "country_dependent_values_invented": False,
            "injection_context_inferred": False,
            "duster_page20_boundary_complete": True,
            "return_to_global_residual_queue": True,
        },
        "next_package": next_package(),
    }


def render_markdown(report: dict[str, object]) -> str:
    return """# Duster Mini Page 20 Exact Scalar Import Closure

Status: complete with preserved boundaries  
Package: `post_residual_duster_mini_page20_exact_scalar_gap_import_closure_001`  
Source: `src_pl_duster_mini_brochure_20251020`, page 20

## Exact receipt

- five strict import specifications are present and source-bounded;
- IDs `3464–3498` form one contiguous 35-row suffix;
- seven observations exist for each of `emission_standard`, `particulate_filter`, `start_stop_system`, `eco_mode` and `gross_vehicle_weight`;
- all rows target the seven exact manual Duster 4x2 configurations and retain observation date `2025-10-20`;
- Eco-G gross vehicle weight is `1805 kg`; mild hybrid 140 gross vehicle weight is `1830 kg`.

## Reconciliation closure

All five import-ready candidate decisions from the 65-candidate Duster page-20 reconciliation are materialized as 35 exact source observations. No import-ready exact gap remains in this boundary.

## Preserved boundaries

- energy-source columns remain powertrain context;
- the unscoped direct-injection row remains deferred because Eco-G injection requires fuel context;
- 38 dash, continuation, protocol, country-dependent and incomplete-row decisions remain explicit non-import/context;
- no current value was overwritten and no context was promoted by inference.

## Reporting integrity

The Duster Eco-G 120 and mild hybrid 140 4x2 completeness scopes include the five new technical slots and remain complete. The package changes no master data beyond the already merged 35-row import.

## Next package

`post_residual_verified_pdf_queue_reentry_review_002` rebuilds the global residual queue from stable boundaries and current closure evidence.
"""


def render_review() -> str:
    return """# Review — Duster mini page 20 exact scalar import closure

Date: 2026-07-30  
Package: `post_residual_duster_mini_page20_exact_scalar_gap_import_closure_001`

## Inputs

- Duster page-20 reviewed-fact reconciliation for 65 candidates;
- five strict configuration-value import specifications;
- master observations `3464–3498`;
- current Duster Eco-G 120 and mild hybrid 140 4x2 reporting scopes.

## Result

The five import-ready reconciliation decisions are fully closed by 35 exact, append-only source observations. Every attribute has seven observations across the exact seven manual Duster 4x2 configurations. The reporting scopes include the new technical slots and remain complete.

## Safety boundary

The source-stated direct-injection row remains unimported because it lacks the fuel context required for dual-fuel Eco-G. Energy-source columns and all 38 authored non-import/context decisions remain unchanged. No master value is overwritten or inferred.

## Handoff

The completed Duster page-20 technical boundary returns to global verified-PDF residual queue selection through `post_residual_verified_pdf_queue_reentry_review_002`.
"""


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    if state["current_package"]["package_id"] != "post_residual_duster_mini_page20_exact_scalar_gap_import_001":
        raise RuntimeError("unexpected current package before Duster import closure")
    if state["next_package"]["package_id"] != "post_residual_duster_mini_page20_exact_scalar_gap_import_closure_001":
        raise RuntimeError("unexpected planned package before Duster import closure")
    expected_baseline = {
        "tests": 1669,
        "csv_files": 46,
        "rows": 11357,
        "configuration_values": 3498,
        "configuration_import_specs": 138,
        "configuration_value_ranges": 278,
        "configuration_range_import_specs": 22,
        "availability_records": 5770,
        "attributes": 385,
        "attribute_categories": 30,
    }
    if state["baseline"] != expected_baseline:
        raise RuntimeError("Duster import closure baseline differs")
    state["updated_on"] = "2026-07-31"
    state["phase"] = "Duster Mini Page 20 Exact Scalar Import Closure Review"
    state["current_package"] = {
        "package_id": "post_residual_duster_mini_page20_exact_scalar_gap_import_closure_001",
        "kind": "review_closure",
        "name": "Duster Mini Page 20 Exact Scalar Import Closure Review",
        "status": "complete",
        "goal": "Verify the 35-row exact scalar receipt, close every reconciliation import-ready gap, preserve injection and context deferrals, and return the completed Duster page-20 boundary to global residual-queue selection.",
        "manifest_paths": [
            "data/reporting/duster_mini_page20_exact_scalar_import_closure.json",
            "data/reporting/duster_mini_page20_exact_scalar_import_closure.md",
            "project/reviews/duster-mini-page20-exact-scalar-import-closure-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = next_package()
    write_json(path, state)


def main() -> int:
    verify_source()
    spec_receipts = verify_specs()
    verify_master_receipt()
    verify_reconciliation()
    reporting_scopes = verify_reporting_scopes()
    report = build_report(spec_receipts, reporting_scopes)
    write_json(REPORT_JSON, report)
    write_text(REPORT_MD, render_markdown(report))
    write_text(REVIEW_MD, render_review())
    update_state()
    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "tools/dkb.py", "pdf-candidate-coverage-reconciliation", "--verify")
    run(
        sys.executable,
        "-m",
        "unittest",
        "-v",
        "tests.test_duster_mini_page20_exact_scalar_gap_import",
        "tests.test_duster_ecog120_reporting_scope",
        "tests.test_official_brochure_technical_gap_resolution_closure",
        "tests.test_verified_pdf_candidate_coverage_reconciliation",
        "tests.test_verified_pdf_candidate_residual_gap_prioritization",
    )
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
