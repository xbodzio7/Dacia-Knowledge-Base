#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIORITIZATION = ROOT / "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
RECONCILIATION = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
PDF = ROOT / "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf"
PACKAGE_ID = "residual_gap_051"
SOURCE_CODE = "src_pl_sandero_brochure_20260202"
PDF_SHA = "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97"
PAGE = 19

REPORT_JSON = ROOT / "data/reporting/sandero_equipment_page19_unresolved_review_chunk1.json"
REPORT_MD = ROOT / "data/reporting/sandero_equipment_page19_unresolved_review_chunk1.md"
PROJECT_REVIEW = ROOT / "project/reviews/sandero-equipment-page19-unresolved-review-chunk1-2026-07-30.md"
STATE = ROOT / "project/state.json"
SUMMARY = ROOT / "project/STATE_SUMMARY.md"

GROUPS = [
    "instrument_cluster_3_5",
    "rain_and_light_sensors",
    "handsfree_card",
    "electric_power_steering",
    "stop_start",
    "trip_computer",
    "trip_computer",
    "trip_computer",
    "front_fog_lights",
    "manual_side_mirrors",
    "electric_side_mirrors",
    "folding_side_mirrors",
    "wireless_charger",
    "low_center_console",
    "low_center_console",
    "low_center_console",
    "high_center_console",
    "high_center_console",
    "high_center_console",
    "manual_climate",
    "automatic_climate",
    "automatic_climate",
    "automatic_climate",
    "central_lock",
    "central_lock",
    "central_lock",
    "automatic_door_lock",
    "front_power_windows",
    "driver_impulse_window",
    "driver_impulse_window",
    "driver_impulse_window",
    "driver_impulse_window",
    "driver_impulse_window",
    "rear_power_windows",
    "steering_column_adjustment",
    "steering_column_adjustment",
    "steering_column_adjustment",
    "front_ceiling_light",
    "rear_12v_socket",
    "heated_front_seats",
]


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"expected object: {path}")
    return payload


def canonical_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    prioritization = load_json(PRIORITIZATION)
    package = next(
        item for item in prioritization["packages"] if item["package_id"] == PACKAGE_ID
    )
    assert package["source_code"] == SOURCE_CODE
    assert package["model_code"] == "sandero_iii"
    assert package["domain"] == "equipment_matrix"
    assert package["page"] == PAGE
    assert package["coverage_status"] == "unresolved"
    assert package["group_candidate_count"] == 65
    assert package["chunk_index"] == 1
    assert package["chunk_count"] == 2
    assert package["candidate_count"] == 40
    candidate_ids = package["candidate_ids"]
    assert len(candidate_ids) == len(set(candidate_ids)) == len(GROUPS) == 40

    reconciliation = load_json(RECONCILIATION)
    by_id = {item["candidate_id"]: item for item in reconciliation["candidates"]}
    candidates = [by_id[identifier] for identifier in candidate_ids]
    assert all(item["source_code"] == SOURCE_CODE for item in candidates)
    assert all(item["page"] == PAGE for item in candidates)
    assert all(item["coverage_status"] == "unresolved" for item in candidates)
    assert all(item["evidence_signatures"] == [] for item in candidates)
    assert hashlib.sha256(PDF.read_bytes()).hexdigest() == PDF_SHA

    decisions = []
    for index, (candidate, group) in enumerate(zip(candidates, GROUPS), 1):
        kind = candidate["candidate_kind"]
        if kind == "table_row":
            decision = "unresolved_signature_mismatch"
        elif kind == "unclassified_text":
            decision = "context_only_non_import"
        else:
            raise SystemExit(f"unexpected candidate kind at {index}: {kind}")
        decisions.append(
            {
                "index": index,
                "candidate_id": candidate["candidate_id"],
                "line": candidate["line_start"],
                "group": group,
                "decision": decision,
                "exact_text": candidate["exact_text"],
            }
        )

    mismatch = sum(item["decision"] == "unresolved_signature_mismatch" for item in decisions)
    context = sum(item["decision"] == "context_only_non_import" for item in decisions)
    visual_groups = list(dict.fromkeys(item["group"] for item in decisions))
    assert mismatch == 24
    assert context == 16
    assert len(visual_groups) == 24

    report = {
        "version": 1,
        "kind": "sandero_equipment_page19_unresolved_review_chunk1",
        "reviewed_on": "2026-07-30",
        "status": "complete",
        "package_id": PACKAGE_ID,
        "source_receipt": {
            "source_code": SOURCE_CODE,
            "file_path": "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
            "sha256": PDF_SHA,
            "page": PAGE,
        },
        "scope": {
            "candidate_count": 40,
            "group_candidate_count": 65,
            "chunk_index": 1,
            "chunk_count": 2,
            "input_coverage_status": "unresolved",
            "attached_evidence_signature_count": 0,
            "attached_evidence_record_count": 0,
        },
        "summary": {
            "logical_group_count": 24,
            "decision_counts": {
                "context_only_non_import": context,
                "unresolved_signature_mismatch": mismatch,
            },
            "selected_evidence_signature_count": 0,
            "selected_evidence_record_count": 0,
            "candidate_ids_and_exact_text_reported_in": "data/reporting/sandero_equipment_page19_unresolved_review_chunk1.md",
        },
        "key_source_boundaries": {
            "grade_columns": ["essential", "expression", "journey"],
            "reviewed_sections": [
                "PROWADZENIE SAMOCHODU I PRZYRZĄDY",
                "WIDOCZNOŚĆ",
                "KOMFORT through heated front seats",
            ],
            "wrapped_rows_kept_as_single_visual_groups": [
                "trip_computer",
                "low_center_console",
                "high_center_console",
                "automatic_climate",
                "central_lock",
                "driver_impulse_window",
                "steering_column_adjustment",
            ],
            "manual_and_automatic_climate_kept_separate": True,
            "low_and_high_center_consoles_kept_separate": True,
            "literal_markers_preserved": True,
        },
        "policy": {
            "zero_attached_evidence_preserved": True,
            "grade_states_not_projected": True,
            "marker_lines_kept_with_visual_rows": True,
            "wrapped_label_fragments_not_promoted": True,
            "complete_rows_without_signatures_remain_unresolved": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "next_package": {
            "name": "Sandero Equipment Page 19 Unresolved Review — Chunk 2",
            "package_id": "residual_gap_052",
            "candidate_count": 25,
            "group_candidate_count": 65,
            "chunk_index": 2,
            "chunk_count": 2,
        },
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(canonical_json(report), encoding="utf-8")

    lines = [
        "# Sandero Equipment Page 19 Unresolved Review — Chunk 1",
        "",
        "Authored review of `residual_gap_051`. The first 40 of 65 unresolved candidates cover Sandero page-19 equipment rows from driving instruments through heated front seats. Source findings are review-only and do not approve imports.",
        "",
        "## Summary",
        "",
        "- candidates: 40 of 65 (chunk 1 of 2);",
        "- visual groups: 24;",
        f"- `unresolved_signature_mismatch`: {mismatch};",
        f"- `context_only_non_import`: {context};",
        "- attached evidence signatures: 0;",
        "- attached evidence records: 0.",
        "",
        "## Source boundary",
        "",
        f"- source: `{SOURCE_CODE}`;",
        "- archived file: `PDF/Broszury/DACIA SANDERO broszura 20260202.pdf`;",
        f"- SHA-256: `{PDF_SHA}`;",
        "- page: 19;",
        "- columns: `essential`, `expression`, `journey`.",
        "",
        "The review covers `PROWADZENIE SAMOCHODU I PRZYRZĄDY`, `WIDOCZNOŚĆ` and the first part of `KOMFORT`. Literal `•`, `-`, `o`, `¤` and slash-separated markers remain unchanged. Wrapped labels are interpreted only as visual grouping, not as import approval.",
        "",
        "## Candidate decisions",
        "",
        "| # | Line | Candidate | Group | Decision | Exact text |",
        "| ---: | ---: | --- | --- | --- | --- |",
    ]
    for item in decisions:
        text = item["exact_text"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {item['index']} | {item['line']} | `{item['candidate_id']}` | `{item['group']}` | `{item['decision']}` | `{text}` |"
        )
    lines.extend(
        [
            "",
            "## Decision boundary",
            "",
            "- Complete rows and aligned marker lines remain unresolved because no matching evidence signature is attached.",
            "- Wrapped label fragments remain non-importable context and are kept with the marker line of the same visual row.",
            "- Trip-computer text, both center-console rows, automatic climate, central locking, the driver impulse-window row and steering-column adjustment remain seven separate multi-line visual groups.",
            "- Manual and automatic climate remain separate rows; low and high center consoles remain separate rows.",
            "- Literal availability markers are preserved without translating them into master-data states.",
            "- No file under `data/master` or `data/imports` changes.",
            "",
            "## Next package",
            "",
            "`residual_gap_052` — Sandero Equipment Page 19 Unresolved Review — Chunk 2, covering the remaining 25 candidates.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    project_review = f"""# Review: Sandero Equipment Page 19 Unresolved — Chunk 1

Date: 2026-07-30  
Package: `{PACKAGE_ID}`  
Status: complete

## Purpose

Review the first 40 of 65 unresolved candidates from the Sandero page-19 equipment matrix against the canonical 200-DPI page render. Preserve exact candidate IDs, line text, three grade columns and literal availability markers without promoting unsupported equipment facts.

## Visual findings

- The candidates form 24 visual equipment rows.
- 16 candidates are wrapped label fragments belonging to seven multi-line rows.
- 24 complete or marker-bearing rows have no attached evidence signature and remain `unresolved_signature_mismatch`.
- Wrapped fragments remain `context_only_non_import`.
- Manual and automatic climate are distinct rows.
- Low and high center consoles are distinct rows.
- The driver impulse-window row and steering-column adjustment retain their full multi-line and slash-marker context.

## Safety decision

No candidate is approved for import. Zero attached evidence is preserved, literal markers are not converted into availability records, and no file under `data/master/**` or `data/imports/**` changes.

## Queue handoff

The next package is `residual_gap_052`, the remaining 25 Sandero page-19 unresolved candidates (chunk 2 of 2).
"""
    PROJECT_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    PROJECT_REVIEW.write_text(project_review, encoding="utf-8")

    state = {
        "version": 1,
        "updated_on": "2026-07-30",
        "repository": {
            "full_name": "xbodzio7/Dacia-Knowledge-Base",
            "default_branch": "main",
            "source_of_truth": "repository",
            "main_sha_tracking": "dynamic",
        },
        "phase": "Sandero Equipment Page 19 Unresolved Review — Chunk 1",
        "reference_delivery": {
            "name": "Post-Cross-Model Workspace Priority Selection Review",
            "pull_request": 297,
            "head_sha": "e7750b327f6a3bd7796cb4967dc00fc6a3401e6c",
            "quality_run": 2158,
        },
        "baseline": {
            "tests": 1626,
            "csv_files": 46,
            "rows": 11194,
            "configuration_values": 3335,
            "configuration_import_specs": 126,
            "configuration_value_ranges": 278,
            "configuration_range_import_specs": 22,
            "availability_records": 5770,
            "attributes": 385,
            "attribute_categories": 30,
        },
        "current_package": {
            "package_id": PACKAGE_ID,
            "kind": "review",
            "name": "Sandero Equipment Page 19 Unresolved Review — Chunk 1",
            "status": "complete",
            "goal": "Review the first 40 of 65 unresolved Sandero page-19 equipment-matrix candidates, preserving exact candidate IDs, source text, visual row grouping and literal grade markers without automatic promotion or master-data changes.",
            "manifest_paths": [
                "data/reporting/sandero_equipment_page19_unresolved_review_chunk1.json",
                "data/reporting/sandero_equipment_page19_unresolved_review_chunk1.md",
                "project/reviews/sandero-equipment-page19-unresolved-review-chunk1-2026-07-30.md",
                "project/state.json",
                "project/STATE_SUMMARY.md",
            ],
        },
        "next_package": {
            "package_id": "residual_gap_052",
            "kind": "review",
            "name": "Sandero Equipment Page 19 Unresolved Review — Chunk 2",
            "status": "planned",
            "goal": "Review the remaining 25 of 65 unresolved Sandero page-19 equipment-matrix candidates, preserving exact candidate IDs, source text and visual context without automatic promotion or master-data changes.",
            "manifest_paths": [
                "data/reporting/sandero_equipment_page19_unresolved_review_chunk2.json",
                "data/reporting/sandero_equipment_page19_unresolved_review_chunk2.md",
                "project/reviews/sandero-equipment-page19-unresolved-review-chunk2-2026-07-30.md",
                "project/state.json",
                "project/STATE_SUMMARY.md",
            ],
        },
        "autonomy": {
            "mode": "autonomous_until_action_required",
            "allowed_operations": [
                "create_package_branch",
                "modify_manifest_paths",
                "run_tests_and_quality",
                "create_package_commit",
                "push_package_branch",
                "create_and_update_pull_request",
                "repair_in_scope_ci_failures",
                "merge_green_pull_request",
                "update_project_state_and_generated_documentation",
            ],
            "stop_conditions": [
                "missing_source_file_or_local_access",
                "authentication_mfa_secret_or_new_permission",
                "ambiguous_source_evidence",
                "new_domain_or_architecture_decision",
                "scope_expansion_beyond_current_milestone",
                "destructive_costly_or_irreversible_operation",
                "manual_github_policy_block",
                "conflict_not_resolvable_from_repository_evidence",
            ],
            "action_required_fields": [
                "reason",
                "required_action",
                "options_and_consequences",
                "resume_stage",
            ],
        },
        "review_policy": {
            "review_only_pull_requests": "exception_only",
            "milestone_review_interval_packages": 5,
            "one_logical_package_per_pull_request": True,
            "delete_remote_branches_automatically": False,
        },
    }
    STATE.write_text(canonical_json(state), encoding="utf-8")

    summary = """# Project State Summary

> Generated from `project/state.json`. Do not edit manually.

## Repository

- Repository: `xbodzio7/Dacia-Knowledge-Base`
- Default branch: `main`
- Source of truth: repository
- Main SHA tracking: dynamic
- State updated: 2026-07-30

## Phase

**Sandero Equipment Page 19 Unresolved Review — Chunk 1**

## Reference delivery

- Package: Post-Cross-Model Workspace Priority Selection Review
- Pull Request: #297
- Verified head: `e7750b327f6a3bd7796cb4967dc00fc6a3401e6c`
- Quality run: #2158

## Verified baseline

- Tests: 1626
- Master CSV files: 46
- Master rows: 11194
- Configuration values: 3335
- Configuration import specifications: 126
- Configuration value ranges: 278
- Configuration range import specifications: 22
- Availability records: 5770
- Canonical attributes: 385
- Attribute categories: 30

## Current package

**Sandero Equipment Page 19 Unresolved Review — Chunk 1** — `complete`

Review the first 40 of 65 unresolved Sandero page-19 equipment-matrix candidates, preserving exact candidate IDs, source text, visual row grouping and literal grade markers without automatic promotion or master-data changes.

## Next package

**Sandero Equipment Page 19 Unresolved Review — Chunk 2** — `planned`

Review the remaining 25 of 65 unresolved Sandero page-19 equipment-matrix candidates, preserving exact candidate IDs, source text and visual context without automatic promotion or master-data changes.

## Autonomy

Mode: `autonomous_until_action_required`

Standing authorization covers package branches, manifest-scoped edits, tests and quality, package commits, pushes, Pull Requests, in-scope CI repairs, green merges, state updates and generated documentation.

Work stops only for a real source, access, authentication, policy, architecture, scope, destructive-operation or unresolved-evidence boundary. The stop message must begin with `ACTION_REQUIRED`.

## Review policy

- Review-only Pull Requests: exception only
- Milestone review interval: 5 logical packages
- One logical package per Pull Request: yes
- Automatic remote-branch deletion: no
"""
    SUMMARY.write_text(summary, encoding="utf-8")

    print(canonical_json(report))


if __name__ == "__main__":
    main()
