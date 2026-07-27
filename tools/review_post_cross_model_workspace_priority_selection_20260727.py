#!/usr/bin/env python3
"""Verify the priority selected after the cross-model workspace entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "data"
    / "reporting"
    / "post_cross_model_workspace_priority_selection_review.json"
)
ENTRY_POINT = ROOT / "data" / "reporting" / "cross_model_workspace_entry_point.json"
BROCHURES = ROOT / "project" / "sources" / "official-dacia-brochures-20260725.json"
GAP_REVIEW = ROOT / "data" / "reporting" / "official_dacia_brochure_gap_review.json"
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"
DKB = ROOT / "tools" / "dkb.py"
STATE = ROOT / "project" / "state.json"


class ReviewError(RuntimeError):
    """Raised when the priority-selection contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def weighted_score(scores: Mapping[str, Any], weights: Mapping[str, Any]) -> int:
    total = 0.0
    for key, weight in weights.items():
        value = scores.get(key)
        ensure(
            isinstance(value, int) and 1 <= value <= 5,
            f"invalid score: {key}",
        )
        ensure(isinstance(weight, int), f"invalid weight: {key}")
        total += value * weight / 5
    return round(total)


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "review version differs")
    ensure(
        payload.get("kind")
        == "post_cross_model_workspace_priority_selection_review",
        "review kind differs",
    )
    ensure(payload.get("reviewed_on") == "2026-07-27", "review date differs")
    ensure(payload.get("status") == "complete", "review is not complete")
    ensure(
        payload.get("source_milestone") == "cross_model_workspace_entry_point.json",
        "source milestone differs",
    )

    policy = payload.get("selection_policy")
    ensure(isinstance(policy, Mapping), "selection policy is missing")
    weights = policy.get("weights_percent")
    ensure(isinstance(weights, Mapping), "selection weights are missing")
    expected_weights = {
        "consumer_value": 30,
        "evidence_readiness": 25,
        "existing_tooling_reuse": 20,
        "low_implementation_risk": 15,
        "dependency_clearance": 10,
    }
    ensure(dict(weights) == expected_weights, "selection weights differ")
    ensure(sum(int(value) for value in weights.values()) == 100, "weights differ")

    readiness = payload.get("repository_readiness")
    ensure(isinstance(readiness, Mapping), "repository readiness is missing")
    expected_readiness = {
        "latest_documented_public_release": "data-products-v1.8.1",
        "public_release_archive_members": 85,
        "offline_workspace_primary_cards": 5,
        "offline_workspace_local_links": 84,
        "active_configurations": 72,
        "model_families": 5,
        "independent_comparison_scopes": 19,
        "within_scope_pairs": 114,
        "recorded_differences": 1695,
        "registered_official_brochures": 5,
        "registered_brochure_pages": 114,
        "registered_brochure_bytes": 40608101,
        "registered_brochures_have_sha256": True,
        "pdf_text_backend_in_quality_ci": "pdftotext",
        "existing_pdf_review_command": "configuration-gap-source-review",
    }
    for key, expected in expected_readiness.items():
        ensure(readiness.get(key) == expected, f"readiness differs: {key}")

    candidates = payload.get("candidates")
    ensure(isinstance(candidates, list), "candidate list is missing")
    ensure(len(candidates) == 5, "candidate count differs")
    ensure(
        [candidate.get("rank") for candidate in candidates] == [1, 2, 3, 4, 5],
        "candidate ranks differ",
    )
    expected_scores = [81, 78, 76, 57, 46]
    for candidate, expected in zip(candidates, expected_scores, strict=True):
        ensure(isinstance(candidate, Mapping), "candidate is invalid")
        scores = candidate.get("scores")
        ensure(isinstance(scores, Mapping), "candidate scores are missing")
        ensure(
            weighted_score(scores, weights) == expected,
            f"calculated score differs: {candidate.get('code')}",
        )
        ensure(
            candidate.get("weighted_score") == expected,
            f"stored score differs: {candidate.get('code')}",
        )
    ensure(candidates[0].get("status") == "selected", "top candidate differs")
    ensure(
        candidates[0].get("code") == "pdf_candidate_extraction_automation_review",
        "selected candidate differs",
    )

    selection = payload.get("selection")
    ensure(isinstance(selection, Mapping), "selection is missing")
    ensure(
        selection.get("code") == "pdf_candidate_extraction_automation_review",
        "selected code differs",
    )
    ensure(selection.get("weighted_score") == 81, "selected score differs")

    contract = payload.get("pdf_candidate_extraction_review_contract")
    ensure(isinstance(contract, Mapping), "PDF review contract is missing")
    ensure(contract.get("registered_source_count") == 5, "source count differs")
    ensure(contract.get("registered_page_count") == 114, "page count differs")
    required = contract.get("required_verification")
    ensure(isinstance(required, list), "verification list is missing")
    for boundary in (
        "byte_deterministic_output",
        "source_hash_verification",
        "no_master_data_changes",
        "no_approved_import_spec_generation",
        "visual_diagrams_not_silently_parsed_as_text",
    ):
        ensure(boundary in required, f"verification boundary missing: {boundary}")
    non_goals = contract.get("non_goals")
    ensure(isinstance(non_goals, list), "non-goals are missing")
    for item in (
        "OCR implementation",
        "master data import",
        "automatic approval",
        "schema change",
        "resolving ambiguous evidence",
    ):
        ensure(item in non_goals, f"non-goal missing: {item}")
    ensure(
        payload.get("next_package", {}).get("name")
        == "PDF Candidate Extraction Automation Review",
        "next package differs",
    )


def verify_repository() -> None:
    entry_point = load_json(ENTRY_POINT)
    ensure(entry_point.get("status") == "complete", "entry point is not complete")
    implementation = entry_point.get("implementation", {})
    ensure(
        implementation.get("member_present_primary_card_count") == 5,
        "workspace primary-card count differs",
    )
    ensure(
        implementation.get("public_v1_8_1_local_link_count") == 84,
        "workspace local-link count differs",
    )

    brochures = load_json(BROCHURES)
    sources = brochures.get("sources")
    ensure(isinstance(sources, list) and len(sources) == 5, "brochure set differs")
    ensure(sum(int(source["pages"]) for source in sources) == 114, "page total differs")
    ensure(
        sum(int(source["bytes"]) for source in sources) == 40608101,
        "brochure byte total differs",
    )
    for source in sources:
        sha256 = source.get("sha256")
        ensure(isinstance(sha256, str) and len(sha256) == 64, "source SHA differs")
        path = ROOT / str(source.get("file_path"))
        ensure(path.is_file(), f"registered PDF is missing: {path}")

    gap_review = load_json(GAP_REVIEW)
    policy = gap_review.get("policy", {})
    ensure(
        policy.get("registration_does_not_import_observations") is True,
        "registration/import boundary differs",
    )
    ensure(
        policy.get("missing_source_statements_are_not_negative_values") is True,
        "missing-statement boundary differs",
    )
    summary = gap_review.get("summary", {})
    ensure(summary.get("registered_sources") == 5, "gap-review source count differs")
    ensure(summary.get("master_observations_imported") == 0, "gap review imported data")

    workflow = QUALITY_WORKFLOW.read_text(encoding="utf-8")
    ensure("Install PDF text extraction backend" in workflow, "PDF CI step missing")
    ensure("poppler-utils" in workflow, "PDF backend package missing")
    ensure("pdftotext -v" in workflow, "PDF backend verification missing")

    cli = DKB.read_text(encoding="utf-8")
    for command in (
        '"configuration-gap-source-review"',
        '"import-configuration-values"',
        '"import-configuration-value-ranges"',
    ):
        ensure(command in cli, f"adjacent CLI command missing: {command}")

    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "phase missing")
    ensure(
        state.get("baseline", {}).get("tests", 0) >= 1078,
        "test baseline regressed",
    )
    ensure(state.get("baseline", {}).get("rows") == 9688, "row baseline changed")
    ensure(
        state.get("baseline", {}).get("configuration_values") == 2949,
        "configuration values changed",
    )
    ensure(
        state.get("baseline", {}).get("availability_records") == 4754,
        "availability baseline changed",
    )


def verify() -> None:
    verify_report(load_json(REPORT))
    verify_repository()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the priority-selection contract.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ReviewError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: post-cross-model workspace priority selection review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
