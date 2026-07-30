from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "data/reporting/verified_pdf_residual_queue_reentry_review.json"
REPORT_MD = ROOT / "data/reporting/verified_pdf_residual_queue_reentry_review.md"
REVIEW_MD = ROOT / "project/reviews/verified-pdf-residual-queue-reentry-review-2026-07-31.md"
STATE_JSON = ROOT / "project/state.json"
PRIORITIZATION = ROOT / "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def package_receipt(packages: list[dict], package_ids: list[str]) -> list[dict]:
    by_id = {package["package_id"]: package for package in packages}
    selected = []
    for package_id in package_ids:
        package = by_id[package_id]
        selected.append(
            {
                "package_id": package_id,
                "priority": package["priority"],
                "coverage_status": package["coverage_status"],
                "candidate_count": package["candidate_count"],
                "chunk_index": package["chunk_index"],
                "chunk_count": package["chunk_count"],
            }
        )
    return selected


def main() -> None:
    queue = load_json(PRIORITIZATION)
    packages = queue["packages"]
    summary = queue["summary"]
    assert summary["candidate_count"] == 1266
    assert summary["package_count"] == 52

    ambiguity = load_json(ROOT / "data/reporting/sandero_technical_page17_ambiguity_review.json")
    chunk1 = load_json(ROOT / "data/reporting/sandero_technical_page17_unresolved_review_chunk1.json")
    chunk2 = load_json(ROOT / "data/reporting/sandero_technical_page17_unresolved_review_chunk2.json")

    assert ambiguity["package_id"] == "residual_gap_004"
    assert ambiguity["summary"]["candidate_count"] == 5
    assert ambiguity["summary"]["decision_counts"] == {"covered_by_selected_evidence": 0, "partially_covered": 5}
    assert ambiguity["summary"]["selected_evidence_signature_count"] == 8
    assert ambiguity["summary"]["selected_evidence_record_count"] == 16

    assert chunk1["package_id"] == "residual_gap_026"
    assert chunk1["scope"]["candidate_count"] == 40
    assert chunk1["summary"]["logical_group_count"] == 20
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

    selected_ids = ["residual_gap_004", "residual_gap_026", "residual_gap_027"]
    selected_packages = package_receipt(packages, selected_ids)
    assert sum(item["candidate_count"] for item in selected_packages) == 46

    excluded = [
        {
            "boundary": {
                "source_code": "src_pl_bigster_brochure_20251210",
                "model_code": "bigster",
                "domain": "technical_tables",
                "page": 20,
            },
            "raw_packages": ["residual_gap_001", "residual_gap_016", "residual_gap_017"],
            "decision": "closed_by_later_reconciliation_imports_and_conflict_preservation",
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
            "decision": "closed_by_later_reconciliation_imports_and_explicit_conflict_boundaries",
            "evidence": [
                "jogger_technical_page19_reviewed_fact_reconciliation.json",
                "jogger_page19_source_observation_import_closure.json",
                "jogger_page19_remaining_mass_conflict_closure.json",
                "jogger_page19_range_context_follow_up_review.json",
            ],
        },
        {
            "boundary": {
                "source_code": "src_pl_duster_mini_brochure_20251020",
                "model_code": "duster_iii",
                "domain": "technical_tables",
                "page": 20,
            },
            "raw_packages": ["residual_gap_003", "residual_gap_020", "residual_gap_021"],
            "decision": "closed_by_later_reconciliation_exact_import_and_closure",
            "evidence": [
                "duster_mini_technical_page20_reviewed_fact_reconciliation.json",
                "duster_mini_page20_exact_scalar_import_closure.json",
            ],
        },
    ]
    for boundary in excluded:
        for filename in boundary["evidence"]:
            assert (ROOT / "data/reporting" / filename).exists(), filename

    next_package = {
        "package_id": "post_residual_sandero_technical_page17_reviewed_fact_reconciliation_001",
        "kind": "review_closure",
        "name": "Sandero Technical Page 17 Reviewed Fact Reconciliation",
        "status": "planned",
        "source_code": "src_pl_sandero_brochure_20260202",
        "source_page": 17,
        "goal": "Reconcile all 46 previously reviewed Sandero page-17 technical candidates against current exact master data, classify existing coverage, import-ready gaps, context-only evidence and deferred signature mismatches, without reopening source review or changing master data in the reconciliation package.",
        "source_review_packages": selected_ids,
        "manifest_paths": [
            "data/reporting/sandero_technical_page17_reviewed_fact_reconciliation.json",
            "data/reporting/sandero_technical_page17_reviewed_fact_reconciliation.md",
            "project/reviews/sandero-technical-page17-reviewed-fact-reconciliation-2026-07-31.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }

    report = {
        "version": 2,
        "kind": "verified_pdf_residual_queue_reentry_review",
        "reviewed_on": "2026-07-31",
        "status": "complete_with_actionable_selection",
        "package_id": "post_residual_verified_pdf_queue_reentry_review_002",
        "raw_queue_snapshot": summary,
        "selection_policy": {
            "stable_boundary_key_used": True,
            "ordinal_package_id_not_treated_as_durable_identity": True,
            "completed_later_reviews_override_raw_priority": True,
            "explicit_non_import_boundaries_not_reopened": True,
            "existing_source_reviews_reused_without_reauthoring": True,
        },
        "excluded_leading_boundaries": excluded,
        "selected_boundary": {
            "source_code": "src_pl_sandero_brochure_20260202",
            "model_code": "sandero_iii",
            "domain": "technical_tables",
            "page": 17,
            "raw_packages": selected_ids,
            "raw_package_receipts": selected_packages,
            "reviewed_candidates": 46,
            "ambiguity_candidates": 5,
            "unresolved_candidates": 41,
            "review_receipts": {
                "ambiguity": ambiguity["summary"],
                "unresolved_chunk_1": chunk1["summary"],
                "unresolved_chunk_2": chunk2["summary"],
            },
            "combined_authored_decision_counts": {
                "covered_by_selected_evidence": 0,
                "partially_covered": 5,
                "context_only_non_import": 27,
                "unresolved_signature_mismatch": 14,
            },
            "selection_reason": "The ambiguity review and both unresolved chunks are complete, but no current-master reviewed-fact reconciliation exists. This is the first raw-priority technical boundary not closed by later reconciliation, exact import or permanent conflict/non-import closure.",
        },
        "release_checkpoint_recommendation": {
            "evaluate_data_products_v1_9_0_after_this_review": True,
            "decision_rule": "Publish after this review unless the selected reconciliation yields one small exact import that can be completed and closed in no more than two additional pull requests.",
        },
        "next_package": next_package,
    }
    write_json(REPORT_JSON, report)

    REPORT_MD.write_text(
        "# Verified PDF Residual Queue Re-entry Review II\n\n"
        "## Result\n\n"
        "The current raw queue still contains 1,266 candidates in 52 historical packages. "
        "Stable source/model/domain/page boundaries are used instead of treating ordinal `residual_gap_*` identifiers as durable identity.\n\n"
        "The completed Bigster page 20, Jogger page 19 and Duster page 20 technical boundaries are excluded by later reconciliation, import and closure evidence.\n\n"
        "## Selected boundary\n\n"
        "- source: `src_pl_sandero_brochure_20260202`;\n"
        "- model: `sandero_iii`;\n"
        "- domain: `technical_tables`;\n"
        "- page: 17;\n"
        "- raw packages: `residual_gap_004`, `residual_gap_026`, `residual_gap_027`;\n"
        "- reviewed candidates: 46 (5 ambiguous and 41 unresolved).\n\n"
        "All three authored source reviews are complete: five partially covered ambiguity decisions, 27 context-only/non-import decisions and 14 unresolved signature mismatches. "
        "No current-master reconciliation exists, making this the first actionable stable boundary.\n\n"
        "## Handoff\n\n"
        "Next: `post_residual_sandero_technical_page17_reviewed_fact_reconciliation_001`. "
        "The reconciliation will classify current coverage and exact gaps without changing master data or reopening the authored source review.\n\n"
        "## Release checkpoint\n\n"
        "After this queue review, evaluate `data-products-v1.9.0`. Delay publication only when the Sandero reconciliation yields one small exact import that can be completed and closed in no more than two additional pull requests.\n",
        encoding="utf-8",
    )

    REVIEW_MD.write_text(
        "# Review — Verified PDF residual queue re-entry II\n\n"
        "Date: 2026-07-31  \n"
        "Package: `post_residual_verified_pdf_queue_reentry_review_002`\n\n"
        "## Decision\n\n"
        "The next actionable stable boundary is Sandero III technical tables, page 17. Its ambiguity review and both unresolved chunks are complete, covering 46 candidates, but no reconciliation against the current master exists.\n\n"
        "## Exclusions\n\n"
        "Bigster page 20, Jogger page 19 and Duster page 20 technical boundaries remain closed by their later reconciliation, exact imports and explicit conflict/non-import closures. Historical package ordinals are not reopened.\n\n"
        "## Handoff\n\n"
        "Proceed to `post_residual_sandero_technical_page17_reviewed_fact_reconciliation_001`. The package remains review-only and must not promote source fragments automatically.\n\n"
        "## Product release checkpoint\n\n"
        "Evaluate `data-products-v1.9.0` immediately after this review. Include one additional Sandero import only if reconciliation identifies a small exact package that can be completed and closed within two PRs.\n",
        encoding="utf-8",
    )

    state = load_json(STATE_JSON)
    state["updated_on"] = "2026-07-31"
    state["phase"] = "Verified PDF Residual Queue Re-entry Review II"
    state["current_package"] = {
        "package_id": "post_residual_verified_pdf_queue_reentry_review_002",
        "kind": "review_closure",
        "name": "Verified PDF Residual Queue Re-entry Review II",
        "status": "complete",
        "goal": "Rebuild the verified-PDF residual queue against later reconciliation, import and closure evidence; exclude completed technical boundaries; and select the first remaining actionable stable boundary without reopening explicit non-import decisions.",
        "manifest_paths": [
            "data/reporting/verified_pdf_residual_queue_reentry_review.json",
            "data/reporting/verified_pdf_residual_queue_reentry_review.md",
            "project/reviews/verified-pdf-residual-queue-reentry-review-2026-07-31.md",
            "project/state.json",
            "project/STATE_SUMMARY.md",
        ],
    }
    state["next_package"] = next_package
    write_json(STATE_JSON, state)

    run(sys.executable, "tools/dkb.py", "project-state", "--apply")
    run(sys.executable, "tools/dkb.py", "project-state", "--check")
    run(sys.executable, "tools/dkb.py", "documentation-baseline", "--check")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q")


if __name__ == "__main__":
    main()
