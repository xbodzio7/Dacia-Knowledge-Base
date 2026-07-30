#!/usr/bin/env python3
"""Materialize the verified-PDF residual queue re-entry review."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "data/reporting/verified_pdf_residual_queue_reentry_review.json"
REPORT_MD = ROOT / "data/reporting/verified_pdf_residual_queue_reentry_review.md"
REVIEW_MD = ROOT / "project/reviews/verified-pdf-residual-queue-reentry-review-2026-07-30.md"
STATE = ROOT / "project/state.json"
PRIORITY = ROOT / "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
DUSTER_AMBIGUITY = ROOT / "data/reporting/duster_mini_technical_page20_ambiguity_review.json"
DUSTER_CHUNK1 = ROOT / "data/reporting/duster_mini_technical_page20_unresolved_review_chunk1.json"
DUSTER_CHUNK2 = ROOT / "data/reporting/duster_mini_technical_page20_unresolved_review_chunk2.json"


def run(*arguments: str) -> None:
    subprocess.run(arguments, cwd=ROOT, check=True)


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
        "package_id": "post_residual_duster_mini_technical_page20_reviewed_fact_reconciliation_001",
        "kind": "review_closure",
        "name": "Duster Mini Technical Page 20 Reviewed Fact Reconciliation",
        "status": "planned",
        "source_code": "src_pl_duster_mini_brochure_20251020",
        "source_page": 20,
        "goal": "Reconcile all 65 previously reviewed Duster page-20 technical candidates against the current exact master data, classify existing coverage, import-ready gaps, context-only evidence and deferred signature mismatches, without reopening source review or changing master data in the reconciliation package.",
        "source_review_packages": [
            "residual_gap_003",
            "residual_gap_020",
            "residual_gap_021",
        ],
        "manifest_paths": [
            "data/reporting/duster_mini_technical_page20_reviewed_fact_reconciliation.json",
            "data/reporting/duster_mini_technical_page20_reviewed_fact_reconciliation.md",
            "project/reviews/duster-mini-technical-page20-reviewed-fact-reconciliation-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }


def verify_inputs() -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    priority = load(PRIORITY)
    summary = priority.get("summary")
    if not isinstance(summary, dict):
        raise RuntimeError("priority summary missing")
    expected_summary = {
        "candidate_count": 1266,
        "package_count": 52,
        "boundary_group_count": 31,
        "maximum_package_size": 40,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise RuntimeError(f"priority summary differs: {key}={summary.get(key)!r}")
    if summary.get("coverage_status_counts") != {"ambiguous": 108, "unresolved": 1158}:
        raise RuntimeError("priority status counts differ")

    ambiguity = load(DUSTER_AMBIGUITY)
    chunk1 = load(DUSTER_CHUNK1)
    chunk2 = load(DUSTER_CHUNK2)
    for path, report in ((DUSTER_AMBIGUITY, ambiguity), (DUSTER_CHUNK1, chunk1), (DUSTER_CHUNK2, chunk2)):
        if report.get("status") != "complete":
            raise RuntimeError(f"source review incomplete: {path}")
        receipt = report.get("source_receipt")
        if not isinstance(receipt, dict) or receipt.get("source_code") != "src_pl_duster_mini_brochure_20251020" or receipt.get("page") != 20:
            raise RuntimeError(f"source receipt differs: {path}")
    if ambiguity.get("scope", {}).get("candidate_count") != 5:
        raise RuntimeError("Duster ambiguity count differs")
    if chunk1.get("scope", {}).get("candidate_count") != 40 or chunk2.get("scope", {}).get("candidate_count") != 20:
        raise RuntimeError("Duster unresolved chunk counts differ")
    if (ROOT / "data/reporting/duster_mini_technical_page20_reviewed_fact_reconciliation.json").exists():
        raise RuntimeError("Duster page-20 reconciliation already exists")
    return priority, ambiguity, chunk1, chunk2


def build_payload(priority: dict[str, object], ambiguity: dict[str, object], chunk1: dict[str, object], chunk2: dict[str, object]) -> dict[str, object]:
    return {
        "version": 1,
        "kind": "verified_pdf_residual_queue_reentry_review",
        "reviewed_on": "2026-07-30",
        "status": "complete_with_actionable_selection",
        "package_id": "post_residual_verified_pdf_queue_reentry_review_001",
        "raw_queue_snapshot": priority["summary"],
        "selection_policy": {
            "stable_boundary_key_used": True,
            "ordinal_package_id_not_treated_as_durable_identity": True,
            "completed_later_reviews_override_raw_priority": True,
            "explicit_non_import_boundaries_not_reopened": True,
            "existing_source_reviews_reused_without_reauthoring": True,
        },
        "excluded_leading_boundaries": [
            {
                "boundary": {
                    "source_code": "src_pl_bigster_brochure_20251210",
                    "model_code": "bigster",
                    "domain": "technical_tables",
                    "page": 20,
                },
                "raw_packages": ["residual_gap_001", "residual_gap_016", "residual_gap_017"],
                "decision": "closed_by_later_reconciliation_and_conflict_preservation",
                "evidence": [
                    "bigster_technical_page20_reviewed_fact_reconciliation.json",
                    "bigster_page20_deferred_import_gap_review.json",
                    "bigster_page20_remaining_conflict_boundary_review.json",
                    "bigster_page20_conflict_preservation_closure_review.json",
                ],
            },
            {
                "boundary": {
                    "source_code": "src_pl_jogger_brochure_20251217",
                    "model_code": "jogger",
                    "domain": "technical_tables",
                    "page": 19,
                },
                "raw_packages": ["residual_gap_002", "residual_gap_024", "residual_gap_025"],
                "decision": "closed_by_later_imports_and_explicit_conflict_boundaries",
                "evidence": [
                    "jogger_technical_page19_reviewed_fact_reconciliation.json",
                    "jogger_page19_source_observation_import_closure.json",
                    "jogger_page19_remaining_mass_conflict_closure.json",
                    "jogger_page19_range_context_follow_up_review.json",
                ],
            },
        ],
        "selected_boundary": {
            "source_code": "src_pl_duster_mini_brochure_20251020",
            "model_code": "duster_iii",
            "domain": "technical_tables",
            "page": 20,
            "raw_packages": ["residual_gap_003", "residual_gap_020", "residual_gap_021"],
            "reviewed_candidates": 65,
            "ambiguity_candidates": 5,
            "unresolved_candidates": 60,
            "review_receipts": {
                "ambiguity": {
                    "decision_counts": ambiguity["summary"]["decision_counts"],
                    "selected_evidence_signature_count": ambiguity["summary"]["selected_evidence_signature_count"],
                    "selected_evidence_record_count": ambiguity["summary"]["selected_evidence_record_count"],
                },
                "unresolved_chunk_1": chunk1["summary"],
                "unresolved_chunk_2": chunk2["summary"],
            },
            "combined_authored_decision_counts": {
                "covered_by_selected_evidence": 3,
                "partially_covered": 2,
                "context_only_non_import": 33,
                "unresolved_signature_mismatch": 27,
            },
            "selection_reason": "All three source-review packages are complete, but no current-master reviewed-fact reconciliation exists. This is the first raw-priority technical boundary not closed by a later reconciliation or permanent non-import closure.",
        },
        "next_package": next_package(),
    }


def render_markdown() -> str:
    return """# Verified PDF Residual Queue Re-entry Review\n\nStatus: **complete with actionable selection**  \nReviewed: **2026-07-30**\n\n## Raw queue\n\nThe generated queue contains **1266 candidates in 52 packages**: 108 ambiguous and 1158 unresolved. Raw ordinal package IDs are not durable workflow identities because later reconciliations and imports do not remove historical candidates automatically.\n\n## Leading boundaries excluded\n\n1. **Bigster page 20 technical tables** — raw packages `001`, `016`, `017`; closed by reviewed-fact reconciliation, deferred-gap review and conflict-preservation closure.\n2. **Jogger page 19 technical tables** — raw packages `002`, `024`, `025`; closed by reviewed-fact reconciliation, five scalar-import tranches, mass-conflict closure and range/context closure.\n\n## Selected actionable boundary\n\n`src_pl_duster_mini_brochure_20251020 / duster_iii / technical_tables / page 20`\n\nThe source review is complete across 65 candidates:\n\n- 5 ambiguity candidates: 3 covered and 2 partially covered;\n- 60 unresolved candidates: 33 context-only non-import and 27 unresolved signature mismatches.\n\nNo `duster_mini_technical_page20_reviewed_fact_reconciliation` artifact exists. The next package will reconcile these authored decisions against the current exact master data without redoing source review or changing master data.\n\n## Handoff\n\n**Duster Mini Technical Page 20 Reviewed Fact Reconciliation**\n"""


def render_review() -> str:
    return """# Review — verified PDF residual queue re-entry\n\nDate: 2026-07-30  \nPackage: `post_residual_verified_pdf_queue_reentry_review_001`\n\n## Method\n\nThe generated 52-package queue was interpreted using stable source/model/domain/page boundaries. Later reconciliation and closure artifacts were treated as authoritative over stale raw priority positions.\n\n## Decision\n\nBigster page 20 and Jogger page 19 are excluded because their later closure chains are complete. Duster mini-brochure page 20 is the first remaining technical boundary with complete authored source reviews but no current-master reconciliation.\n\nThe selected handoff covers 65 candidates from ambiguity package `003` and unresolved packages `020–021`. The reconciliation must preserve the existing authored decisions, classify current coverage and produce follow-up imports only through later dedicated packages.\n"""


def update_state() -> None:
    state = load(STATE)
    state["updated_on"] = "2026-07-30"
    state["phase"] = "Verified PDF Residual Queue Re-entry Review"
    state["current_package"] = {
        "package_id": "post_residual_verified_pdf_queue_reentry_review_001",
        "kind": "review_closure",
        "name": "Verified PDF Residual Queue Re-entry Review",
        "status": "complete",
        "goal": "Exclude raw-priority boundaries already closed by later work and select the first genuinely actionable verified-PDF residual boundary using stable source/model/domain/page identity.",
        "manifest_paths": [
            "data/reporting/verified_pdf_residual_queue_reentry_review.json",
            "data/reporting/verified_pdf_residual_queue_reentry_review.md",
            "project/reviews/verified-pdf-residual-queue-reentry-review-2026-07-30.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = next_package()
    write_json(STATE, state)


def main() -> int:
    priority, ambiguity, chunk1, chunk2 = verify_inputs()
    write_json(REPORT_JSON, build_payload(priority, ambiguity, chunk1, chunk2))
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
