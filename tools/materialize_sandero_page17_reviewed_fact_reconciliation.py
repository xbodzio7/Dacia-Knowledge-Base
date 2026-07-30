from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMBIGUITY = ROOT / "data/reporting/sandero_technical_page17_ambiguity_review.json"
CHUNK1 = ROOT / "data/reporting/sandero_technical_page17_unresolved_review_chunk1.json"
CHUNK2 = ROOT / "data/reporting/sandero_technical_page17_unresolved_review_chunk2.json"
MATRIX = ROOT / "project/tmp/sandero-page17-coverage-matrix.json"
REPORT_JSON = ROOT / "data/reporting/sandero_technical_page17_reviewed_fact_reconciliation.json"
REPORT_MD = ROOT / "data/reporting/sandero_technical_page17_reviewed_fact_reconciliation.md"
REVIEW_MD = ROOT / "project/reviews/sandero-technical-page17-reviewed-fact-reconciliation-2026-07-31.md"
STATE_JSON = ROOT / "project/state.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def bucket(matrix: dict, attribute: str, key: str) -> dict:
    return matrix["latest_values"][attribute][key]


def assert_bucket(matrix: dict, attribute: str, key: str, value: str, count: int) -> None:
    item = bucket(matrix, attribute, key)
    assert item["configuration_count"] == count, (attribute, key, item)
    assert item["values"] == {value: count}, (attribute, key, item)


def main() -> None:
    ambiguity = load(AMBIGUITY)
    chunk1 = load(CHUNK1)
    chunk2 = load(CHUNK2)
    matrix = load(MATRIX)

    assert ambiguity["package_id"] == "residual_gap_004"
    assert ambiguity["summary"]["candidate_count"] == 5
    assert ambiguity["summary"]["decision_counts"] == {"covered_by_selected_evidence": 0, "partially_covered": 5}
    assert ambiguity["summary"]["selected_evidence_signature_count"] == 8
    assert ambiguity["summary"]["selected_evidence_record_count"] == 16
    assert chunk1["package_id"] == "residual_gap_026"
    assert chunk1["scope"]["candidate_count"] == 40
    assert chunk1["summary"]["decision_counts"] == {
        "context_only_non_import": 26,
        "unresolved_signature_mismatch": 14,
    }
    assert chunk2["package_id"] == "residual_gap_027"
    assert chunk2["scope"]["candidate_count"] == 1
    assert chunk2["summary"]["decision_counts"] == {
        "context_only_non_import": 1,
        "unresolved_signature_mismatch": 0,
    }

    assert matrix["group_sizes"] == {
        "tce100_manual": 3,
        "ecog120_automatic": 2,
        "ecog120_manual": 2,
    }
    assert matrix["same_source_page17_scalar_count"] == 72
    assert matrix["same_source_page17_range_count"] == 0
    assert matrix["latest_ranges"] == {}

    for attribute, contexts in {
        "engine_power": {
            "tce100_manual|petrol|none": ("74", 3),
            "ecog120_manual|lpg|none": ("90", 2),
            "ecog120_manual|petrol|none": ("84", 2),
            "ecog120_automatic|lpg|none": ("90", 2),
            "ecog120_automatic|petrol|none": ("84", 2),
        },
        "engine_torque": {
            "tce100_manual|petrol|none": ("200", 3),
            "ecog120_manual|lpg|none": ("197", 2),
            "ecog120_manual|petrol|none": ("190", 2),
            "ecog120_automatic|lpg|none": ("197", 2),
            "ecog120_automatic|petrol|none": ("190", 2),
        },
        "acceleration_0_100": {
            "tce100_manual|petrol|none": ("9.7", 3),
            "ecog120_manual|lpg|none": ("10.1", 2),
            "ecog120_manual|petrol|none": ("11.1", 2),
            "ecog120_automatic|lpg|none": ("9.8", 2),
            "ecog120_automatic|petrol|none": ("10.9", 2),
        },
    }.items():
        for key, (value, count) in contexts.items():
            assert_bucket(matrix, attribute, key, value, count)

    for key, value, count in [
        ("tce100_manual|petrol|4", "7.4", 3),
        ("tce100_manual|petrol|5", "10.7", 3),
        ("ecog120_manual|lpg|4", "7.4", 2),
        ("ecog120_manual|lpg|5", "11", 2),
        ("ecog120_manual|petrol|4", "8.4", 2),
        ("ecog120_manual|petrol|5", "11.7", 2),
        ("ecog120_automatic|lpg|4", "8", 2),
        ("ecog120_automatic|lpg|5", "8", 2),
        ("ecog120_automatic|petrol|4", "8.9", 2),
        ("ecog120_automatic|petrol|5", "8.9", 2),
    ]:
        assert_bucket(matrix, "elasticity_80_120", key, value, count)

    for attribute, expected in {
        "maximum_kerb_weight": {
            "tce100_manual|none|none": ("1132", 3),
            "ecog120_manual|none|none": ("1209", 2),
            "ecog120_automatic|none|none": ("1232", 2),
        },
        "gross_vehicle_weight": {
            "tce100_manual|none|none": ("1570", 3),
            "ecog120_manual|none|none": ("1640", 2),
            "ecog120_automatic|none|none": ("1665", 2),
        },
        "gross_train_weight": {
            "tce100_manual|none|none": ("2550", 3),
            "ecog120_manual|none|none": ("2740", 2),
            "ecog120_automatic|none|none": ("2765", 2),
        },
        "cylinder_count": {
            "tce100_manual|none|none": ("3", 3),
            "ecog120_manual|none|none": ("3", 2),
            "ecog120_automatic|none|none": ("3", 2),
        },
        "total_valve_count": {
            "tce100_manual|none|none": ("12", 3),
            "ecog120_manual|none|none": ("12", 2),
            "ecog120_automatic|none|none": ("12", 2),
        },
    }.items():
        for key, (value, count) in expected.items():
            assert_bucket(matrix, attribute, key, value, count)

    assert_bucket(matrix, "fuel_type", "tce100_manual|none|none", "petrol", 3)
    assert_bucket(matrix, "injection_type", "tce100_manual|none|none", "direct_injection", 3)

    tce = [
        "sandero_iii_essential_tce100_manual",
        "sandero_iii_expression_tce100_manual",
        "sandero_iii_journey_tce100_manual",
    ]
    manual = [
        "sandero_iii_expression_ecog120_manual",
        "sandero_iii_journey_ecog120_manual",
    ]
    automatic = [
        "sandero_iii_expression_ecog120_automatic",
        "sandero_iii_journey_ecog120_automatic",
    ]
    range_groups = [
        {"attribute_code": "max_power_rpm", "fuel_type_code": "petrol", "minimum_value": "5000", "maximum_value": "5250", "configurations": tce, "source_text": "100 TCe: 74 (120 KM) od 5000 do 5250 obr./min; printed power literal retained without normalization"},
        {"attribute_code": "max_power_rpm", "fuel_type_code": "lpg", "minimum_value": "4500", "maximum_value": "5000", "configurations": manual, "source_text": "120 Eco-G manual LPG: 90 (120 KM) od 4500 do 5000 obr./min"},
        {"attribute_code": "max_power_rpm", "fuel_type_code": "petrol", "minimum_value": "4500", "maximum_value": "5750", "configurations": manual, "source_text": "120 Eco-G manual benzyna: 84 (114 KM) od 4500 do 5750 obr./min"},
        {"attribute_code": "max_power_rpm", "fuel_type_code": "lpg", "minimum_value": "4500", "maximum_value": "5000", "configurations": automatic, "source_text": "120 Eco-G automatic LPG: 90 (120 KM) od 4500 do 5000 obr./min"},
        {"attribute_code": "max_power_rpm", "fuel_type_code": "petrol", "minimum_value": "4500", "maximum_value": "5750", "configurations": automatic, "source_text": "120 Eco-G automatic benzyna: 84 (114 KM) od 4500 do 5750 obr./min"},
        {"attribute_code": "max_torque_rpm", "fuel_type_code": "petrol", "minimum_value": "2900", "maximum_value": "3500", "configurations": tce, "source_text": "100 TCe: 200 Nm od 2900 do 3500 obr./min"},
        {"attribute_code": "max_torque_rpm", "fuel_type_code": "lpg", "minimum_value": "1750", "maximum_value": "3750", "configurations": manual, "source_text": "120 Eco-G manual LPG: 197 Nm od 1750 do 3750 obr./min"},
        {"attribute_code": "max_torque_rpm", "fuel_type_code": "petrol", "minimum_value": "2000", "maximum_value": "4000", "configurations": manual, "source_text": "120 Eco-G manual benzyna: 190 Nm od 2000 do 4000 obr./min"},
        {"attribute_code": "max_torque_rpm", "fuel_type_code": "lpg", "minimum_value": "1750", "maximum_value": "3750", "configurations": automatic, "source_text": "120 Eco-G automatic LPG: 197 Nm od 1750 do 3750 obr./min"},
    ]
    assert sum(len(group["configurations"]) for group in range_groups) == 20
    assert sum(len(group["configurations"]) for group in range_groups if group["attribute_code"] == "max_power_rpm") == 11
    assert sum(len(group["configurations"]) for group in range_groups if group["attribute_code"] == "max_torque_rpm") == 9

    partition = {
        "current_exact_scalar_coverage": 11,
        "current_configuration_or_fuel_identity_coverage": 2,
        "import_ready_range_gap": 2,
        "context_model_required": 1,
        "explicit_non_import_or_context": 30,
    }
    assert sum(partition.values()) == 46

    next_package = {
        "package_id": "post_residual_sandero_page17_power_torque_rpm_range_import_001",
        "kind": "configuration_value_range_import",
        "name": "Sandero Page 17 Power and Torque RPM Range Import",
        "status": "planned",
        "source_code": "src_pl_sandero_brochure_20260202",
        "source_page": 17,
        "goal": "Add 20 exact closed max-power and max-torque engine-speed ranges across the seven active Sandero III configurations, preserving fuel context, the printed TCe power-literal inconsistency and the missing automatic-petrol torque continuation.",
        "planned_range_id_start": 279,
        "planned_range_id_end": 298,
        "planned_observation_count": 20,
        "attribute_counts": {"max_power_rpm": 11, "max_torque_rpm": 9},
        "manifest_paths": [
            "data/imports/brochure_technical_values/sandero-page17-power-torque-rpm-ranges-20260202.json",
            "data/master/configuration_attribute_value_ranges.csv",
            "tests/test_sandero_page17_power_torque_rpm_ranges.py",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }

    report = {
        "version": 1,
        "kind": "sandero_technical_page17_reviewed_fact_reconciliation",
        "reviewed_on": "2026-07-31",
        "status": "complete_with_small_range_import_handoff",
        "package_id": "post_residual_sandero_technical_page17_reviewed_fact_reconciliation_001",
        "source": {
            "source_code": "src_pl_sandero_brochure_20260202",
            "file_path": "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
            "sha256": "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
            "page": 17,
            "observation_date": "2026-02-02",
        },
        "source_review_packages": ["residual_gap_004", "residual_gap_026", "residual_gap_027"],
        "scope": {
            "reviewed_candidates": 46,
            "ambiguity_candidates": 5,
            "unresolved_candidates": 41,
            "active_target_configurations": 7,
            "same_source_page17_scalar_observations": 72,
            "same_source_page17_range_observations": 0,
        },
        "authored_decision_receipts": {
            "ambiguity": ambiguity["summary"],
            "unresolved_chunk_1": chunk1["summary"],
            "unresolved_chunk_2": chunk2["summary"],
        },
        "candidate_reconciliation": {
            "current_exact_scalar_coverage": {
                "candidate_count": 11,
                "groups": [
                    "five ambiguity-row scalar facts: maximum power, maximum torque, maximum kerb weight, gross vehicle weight and gross train weight",
                    "six unresolved-row scalar facts: maximum power, maximum torque, cylinders/valves, acceleration and fourth-/fifth-gear elasticity",
                ],
                "decision": "current exact values exist across the seven active configurations; do not duplicate or overwrite them in reconciliation",
            },
            "current_configuration_or_fuel_identity_coverage": {
                "candidate_count": 2,
                "groups": ["fuel-type row", "manual/automatic six-speed gearbox row"],
                "decision": "existing configuration, transmission and fuel-context modeling already represents these boundaries",
            },
            "import_ready_range_gap": {
                "candidate_count": 2,
                "planned_range_observations": 20,
                "planned_range_id_start": 279,
                "planned_range_id_end": 298,
                "attribute_counts": {"max_power_rpm": 11, "max_torque_rpm": 9},
                "range_groups": range_groups,
                "excluded_automatic_petrol_torque_range": {
                    "configuration_count": 2,
                    "reason": "the source prints 190 Nm but no aligned rpm continuation in the reviewed extraction; no range is inferred",
                },
            },
            "context_model_required": {
                "candidate_count": 1,
                "group": "direct-injection row",
                "decision": "TCe direct injection is already covered, while the brochure's shared Eco-G row is not fuel-scoped; do not create an unscoped dual-fuel scalar",
            },
            "explicit_non_import_or_context": {
                "candidate_count": 30,
                "groups": [
                    "all 27 originally authored context-only candidates",
                    "WLTP protocol label",
                    "country-dependent CO2 continuation",
                    "country-dependent combined-consumption continuation",
                ],
            },
        },
        "partition_check": {
            "candidate_count": 46,
            "classified_once": True,
            "class_counts": partition,
        },
        "source_boundaries_preserved": {
            "printed_tce_heading_and_74_kw_parenthetical_conflict_not_normalized": True,
            "fuel_subcolumns_not_collapsed": True,
            "automatic_petrol_torque_rpm_not_inferred": True,
            "country_dependent_values_not_invented": True,
            "review_does_not_change_master_data": True,
        },
        "release_checkpoint": {
            "target_version": "data-products-v1.9.0",
            "decision": "defer_until_small_range_import_and_closure",
            "remaining_pr_count_before_release": 2,
            "reason": "the only import-ready gap is a bounded 20-range package that can be imported and closed within two pull requests",
        },
        "next_package": next_package,
    }
    dump(REPORT_JSON, report)

    REPORT_MD.write_text(
        "# Sandero Technical Page 17 Reviewed Fact Reconciliation\n\n"
        "## Result\n\n"
        "All 46 authored candidates are reconciled against the current master. Eleven candidates are closed by exact scalar coverage, two by existing configuration/fuel identity, one remains a fuel-context modeling boundary and 30 remain explicit context/non-import evidence.\n\n"
        "The only import-ready gap consists of two source rows representing 20 closed RPM ranges: 11 `max_power_rpm` observations and 9 `max_torque_rpm` observations across seven active Sandero III configurations.\n\n"
        "## Range handoff\n\n"
        "- TCe 100 power: 5000–5250 rpm for three configurations;\n"
        "- Eco-G 120 power: LPG 4500–5000 rpm and petrol 4500–5750 rpm for manual and automatic configurations;\n"
        "- TCe 100 torque: 2900–3500 rpm for three configurations;\n"
        "- Eco-G 120 torque: LPG 1750–3750 rpm for manual and automatic configurations, petrol 2000–4000 rpm for manual configurations only;\n"
        "- Eco-G automatic petrol torque range is excluded because the reviewed extraction has no aligned rpm continuation.\n\n"
        "## Release checkpoint\n\n"
        "Publish `data-products-v1.9.0` after the 20-range import and its closure. This is the one small exact package allowed by the queue-review decision rule.\n",
        encoding="utf-8",
    )

    REVIEW_MD.write_text(
        "# Review — Sandero technical page 17 reviewed-fact reconciliation\n\n"
        "Date: 2026-07-31  \n"
        "Package: `post_residual_sandero_technical_page17_reviewed_fact_reconciliation_001`\n\n"
        "## Decision\n\n"
        "The current master already covers every reviewed scalar fact for the seven active Sandero III configurations. The remaining exact gap is limited to 20 closed engine-speed ranges from two source rows.\n\n"
        "## Preserved boundaries\n\n"
        "The printed `100 TCe` / `74 (120 KM)` inconsistency is retained literally and does not create another power value. The shared Eco-G injection row remains fuel-context deferred. The missing automatic-petrol torque rpm continuation, country-dependent values and protocol/context fragments are not inferred.\n\n"
        "## Handoff and release\n\n"
        "Proceed to `post_residual_sandero_page17_power_torque_rpm_range_import_001`, then its closure. Publish `data-products-v1.9.0` immediately after both PRs are green and merged.\n",
        encoding="utf-8",
    )

    state = load(STATE_JSON)
    state["updated_on"] = "2026-07-31"
    state["phase"] = "Sandero Technical Page 17 Reviewed Fact Reconciliation"
    state["current_package"] = {
        "package_id": "post_residual_sandero_technical_page17_reviewed_fact_reconciliation_001",
        "kind": "review_closure",
        "name": "Sandero Technical Page 17 Reviewed Fact Reconciliation",
        "status": "complete",
        "goal": "Reconcile all 46 previously reviewed Sandero page-17 technical candidates against current exact master data and hand off the only exact remaining gap as a bounded 20-range import.",
        "manifest_paths": [
            "data/reporting/sandero_technical_page17_reviewed_fact_reconciliation.json",
            "data/reporting/sandero_technical_page17_reviewed_fact_reconciliation.md",
            "project/reviews/sandero-technical-page17-reviewed-fact-reconciliation-2026-07-31.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = next_package
    dump(STATE_JSON, state)

    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q")


if __name__ == "__main__":
    main()
