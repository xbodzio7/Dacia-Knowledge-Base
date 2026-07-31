#!/usr/bin/env python3
"""Materialize the exact five-file Sandero page-17 RPM closure package."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTING = ROOT / "data" / "reporting"
REVIEWS = ROOT / "project" / "reviews"
STATE = ROOT / "project" / "state.json"
PACKAGE_ID = "post_residual_sandero_page17_power_torque_rpm_range_import_closure_001"

NEXT_PACKAGE = {
    "package_id": "data_products_v1_9_0_release_preparation_001",
    "kind": "release_preparation",
    "name": "Data Products v1.9.0 Release Preparation",
    "status": "planned",
    "goal": "Prepare and verify an immutable minor-release candidate containing the completed Sandero page-17 RPM range coverage and all current source-backed data products, without publishing or changing source data.",
    "manifest_paths": [
        "data/reporting/data_products_v1_9_0_release_preparation.json",
        "project/packages/data-products-v1.9.0-release-preparation.md",
        "tests/test_data_products_v1_9_0_release_preparation.py",
        "tools/review_data_products_v1_9_0_release_preparation_20260731.py",
        "tools/reporting/data_product_release.py",
        "README.md",
        "CHANGELOG.md",
        "project/ROADMAP.md",
        "project/SESSION_STATE.md",
        "project/state.json",
        "project/STATE_SUMMARY.md",
    ],
}

CLOSURE = {
    "version": 1,
    "kind": "sandero_page17_power_torque_rpm_range_import_closure",
    "reviewed_on": "2026-07-31",
    "status": "complete_with_preserved_boundaries",
    "package_id": PACKAGE_ID,
    "source": {
        "source_code": "src_pl_sandero_brochure_20260202",
        "file_path": "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
        "sha256": "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
        "page": 17,
        "observation_date": "2026-02-02",
    },
    "scope": {
        "reviewed_candidates": 46,
        "import_ready_candidate_decisions": 2,
        "imported_range_observations": 20,
        "target_configurations": 7,
        "import_specs": 2,
    },
    "completed_import_receipts": [
        {
            "attribute": "max_power_rpm",
            "spec_path": "data/imports/configuration_value_ranges/sandero-page17-max-power-rpm-ranges-20260202.json",
            "id_range": [279, 289],
            "observations": 11,
            "fuel_context_counts": {"petrol": 7, "lpg": 4},
            "closed_intervals": [
                {"fuel_type_code": "petrol", "minimum_value": "5000", "maximum_value": "5250", "observations": 3},
                {"fuel_type_code": "lpg", "minimum_value": "4500", "maximum_value": "5000", "observations": 4},
                {"fuel_type_code": "petrol", "minimum_value": "4500", "maximum_value": "5750", "observations": 4},
            ],
        },
        {
            "attribute": "max_torque_rpm",
            "spec_path": "data/imports/configuration_value_ranges/sandero-page17-max-torque-rpm-ranges-20260202.json",
            "id_range": [290, 298],
            "observations": 9,
            "fuel_context_counts": {"petrol": 5, "lpg": 4},
            "closed_intervals": [
                {"fuel_type_code": "petrol", "minimum_value": "2900", "maximum_value": "3500", "observations": 3},
                {"fuel_type_code": "lpg", "minimum_value": "1750", "maximum_value": "3750", "observations": 4},
                {"fuel_type_code": "petrol", "minimum_value": "2000", "maximum_value": "4000", "observations": 2},
            ],
        },
    ],
    "master_receipt": {
        "id_range": [279, 298],
        "observations": 20,
        "attribute_counts": {"max_power_rpm": 11, "max_torque_rpm": 9},
        "fuel_context_counts": {"petrol": 12, "lpg": 8},
        "configuration_group_counts": {"tce100_manual": 6, "ecog120_manual": 8, "ecog120_automatic": 6},
        "source_code": "src_pl_sandero_brochure_20260202",
        "observation_date": "2026-02-02",
        "closed_intervals_only": True,
    },
    "reconciliation_closure": {
        "candidate_partition_preserved": True,
        "current_exact_scalar_coverage": 11,
        "current_configuration_or_fuel_identity_coverage": 2,
        "import_ready_candidate_decisions_closed": 2,
        "planned_range_observations_materialized": 20,
        "remaining_context_model_required": 1,
        "remaining_explicit_non_import_or_context": 30,
        "remaining_import_ready_exact_gaps": 0,
    },
    "preserved_boundaries": [
        {
            "code": "printed_tce_power_literal_conflict",
            "classification": "source_literal_preserved",
            "decision": "retain the printed 100 TCe / 74 (120 KM) inconsistency without creating or normalizing another scalar power value",
        },
        {
            "code": "automatic_petrol_ecog_torque_rpm",
            "classification": "not_stated_on_aligned_source_continuation",
            "decision": "do not infer a petrol torque-speed interval for the two Eco-G automatic configurations",
        },
        {
            "code": "direct_injection_dual_fuel_context",
            "classification": "fuel_context_model_required",
            "decision": "do not create an unscoped dual-fuel injection scalar from the shared brochure row",
        },
        {
            "code": "explicit_non_import_or_context",
            "candidate_count": 30,
            "decision": "retain all authored protocol, continuation, country-dependent and context-only boundaries",
        },
    ],
    "closure_decision": {
        "exact_range_import_complete": True,
        "master_values_overwritten": False,
        "automatic_promotion_used": False,
        "fuel_subcolumns_collapsed": False,
        "automatic_petrol_torque_range_inferred": False,
        "sandero_page17_import_ready_boundary_complete": True,
        "release_checkpoint_ready": True,
        "target_release": "data-products-v1.9.0",
    },
    "next_package": NEXT_PACKAGE,
}

REPORT_MD = """# Sandero Page 17 Power and Torque RPM Range Import Closure

Status: complete with preserved boundaries  
Package: `post_residual_sandero_page17_power_torque_rpm_range_import_closure_001`  
Source: `src_pl_sandero_brochure_20260202`, page 17

## Exact receipt

- two strict range specifications are present and source-bounded;
- IDs `279–298` form one contiguous 20-row suffix;
- `max_power_rpm` contains 11 observations and `max_torque_rpm` contains 9 observations;
- all intervals are closed, use `rpm`, retain observation date `2026-02-02` and target exactly seven active Sandero III configurations;
- fuel context remains explicit: 12 petrol observations and 8 LPG observations.

## Reconciliation closure

Both import-ready decisions from the 46-candidate Sandero page-17 reconciliation are fully materialized. The original partition remains exact: 11 scalar-coverage candidates, 2 configuration/fuel-identity candidates, 2 imported range candidates, 1 context-model boundary and 30 explicit non-import/context candidates. No import-ready exact gap remains.

## Preserved boundaries

- the printed `100 TCe` / `74 (120 KM)` inconsistency remains literal and does not create another scalar power value;
- no petrol torque-speed interval is inferred for the two Eco-G automatic configurations because the reviewed source has no aligned RPM continuation;
- petrol and LPG subcolumns remain separate source contexts;
- the shared direct-injection row remains deferred for dual-fuel Eco-G rather than becoming an unscoped scalar;
- protocol labels, country-dependent continuations and context-only fragments remain non-imports.

## Release checkpoint

The bounded Sandero page-17 import chain is complete. The next package prepares, but does not publish, `data-products-v1.9.0` from the current source-backed repository state.
"""

REVIEW_MD = """# Review — Sandero page 17 power and torque RPM range import closure

Date: 2026-07-31  
Package: `post_residual_sandero_page17_power_torque_rpm_range_import_closure_001`

## Inputs

- the 46-candidate Sandero page-17 reviewed-fact reconciliation;
- two strict configuration-value-range import specifications;
- master range observations `279–298`;
- current configuration, source-relationship and fuel-context contracts.

## Result

The two import-ready reconciliation decisions are fully closed by 20 exact, append-only, source-specific closed intervals. The receipt contains 11 maximum-power-speed and 9 maximum-torque-speed observations across the exact seven active Sandero III configurations. No import-ready exact gap remains in this source boundary.

## Safety boundary

The printed TCe power inconsistency remains literal. Petrol and LPG evidence is not collapsed. No petrol torque-speed interval is inferred for Eco-G automatic, and the shared direct-injection row remains deferred because dual-fuel context is required. All 30 explicit non-import/context decisions remain unchanged.

## Handoff

The completed Sandero page-17 chain releases the deferred checkpoint. The next package is `data_products_v1_9_0_release_preparation_001`, which prepares and verifies an immutable `data-products-v1.9.0` candidate without publishing it.
"""


def main() -> None:
    REPORTING.mkdir(parents=True, exist_ok=True)
    REVIEWS.mkdir(parents=True, exist_ok=True)
    (REPORTING / "sandero_page17_power_torque_rpm_range_import_closure.json").write_text(
        json.dumps(CLOSURE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (REPORTING / "sandero_page17_power_torque_rpm_range_import_closure.md").write_text(
        REPORT_MD, encoding="utf-8"
    )
    (REVIEWS / "sandero-page17-power-torque-rpm-range-import-closure-2026-07-31.md").write_text(
        REVIEW_MD, encoding="utf-8"
    )

    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["phase"] = "Sandero Page 17 Power and Torque RPM Range Import Closure"
    state["current_package"] = {
        "package_id": PACKAGE_ID,
        "kind": "review_closure",
        "name": "Sandero Page 17 Power and Torque RPM Range Import Closure",
        "status": "complete",
        "goal": "Verify the exact 20-range receipt, close the only import-ready Sandero page-17 gap, preserve scalar, fuel-context and non-import boundaries, and release the data-products-v1.9.0 preparation checkpoint.",
        "manifest_paths": [
            "data/reporting/sandero_page17_power_torque_rpm_range_import_closure.json",
            "data/reporting/sandero_page17_power_torque_rpm_range_import_closure.md",
            "project/reviews/sandero-page17-power-torque-rpm-range-import-closure-2026-07-31.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = NEXT_PACKAGE
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
