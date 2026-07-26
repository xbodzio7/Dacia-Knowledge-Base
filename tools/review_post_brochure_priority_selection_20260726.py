#!/usr/bin/env python3
"""Verify the post-brochure priority selection review."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
REPORT = REPORTING / "post_brochure_priority_selection_review.json"
RESIDUAL = REPORTING / "official_brochure_residual_evidence_review.json"
DIMENSION_CLOSURE = REPORTING / "brochure_generic_dimensions_import_closure_review.json"
ROADMAP = ROOT / "project" / "ROADMAP.md"

sys.path.insert(0, str(ROOT / "tools"))

import configuration_comparison  # noqa: E402

WEIGHTS = {
    "consumer_value": 30,
    "evidence_readiness": 25,
    "existing_tooling_reuse": 20,
    "low_implementation_risk": 15,
    "dependency_clearance": 10,
}
EXPECTED_CANDIDATES = {
    "data_products_v1_7_0_release_preparation": (1, "selected", 100),
    "cross_model_comparison_view_review": (2, "follow_up_after_release", 82),
    "pdf_candidate_extraction_automation_review": (3, "strategic_later", 67),
    "exact_configuration_expansion_review": (4, "blocked_evidence", 57),
    "ambiguous_brochure_evidence_resolution": (5, "blocked_ambiguity", 39),
}
SCOPE_SPECS = {
    "bigster_hybrid155_4x2_automatic_completeness.json": "bigster_hybrid155_4x2_automatic_gap_evidence.spec",
    "bigster_hybridg150_4x4_automatic_completeness.json": "bigster_hybridg150_4x4_automatic_gap_evidence.spec",
    "bigster_mildhybrid140_4x2_manual_completeness.json": "bigster_mildhybrid140_4x2_manual_gap_evidence.spec",
    "bigster_mildhybridg140_4x2_manual_completeness.json": "bigster_mildhybridg140_4x2_manual_gap_evidence.spec",
    "duster_ecog100_completeness.json": "duster_ecog100_gap_evidence.spec",
    "duster_ecog120_automatic_completeness.json": "duster_ecog120_automatic_gap_evidence.spec",
    "duster_ecog120_completeness.json": "duster_ecog120_gap_evidence.spec",
    "duster_hybrid140_completeness.json": "duster_hybrid140_gap_evidence.spec",
    "duster_hybrid155_completeness.json": "duster_hybrid155_gap_evidence.spec",
    "duster_mildhybrid130_4x2_completeness.json": "duster_mildhybrid130_4x2_gap_evidence.spec",
    "duster_mildhybrid130_4x4_completeness.json": "duster_mildhybrid130_4x4_gap_evidence.spec",
    "duster_mildhybrid140_4x2_completeness.json": "duster_mildhybrid140_4x2_gap_evidence.spec",
    "jogger_ecog120_automatic_completeness.json": "jogger_ecog120_automatic_gap_evidence.spec",
    "jogger_ecog120_manual_completeness.json": "jogger_ecog120_manual_gap_evidence.spec",
    "jogger_hybrid155_automatic_completeness.json": "jogger_hybrid155_automatic_gap_evidence.spec",
    "jogger_tce110_manual_completeness.json": "jogger_tce110_manual_gap_evidence.spec",
    "sandero_ecog120_automatic_completeness.json": "sandero_ecog120_automatic_gap_evidence.json",
    "sandero_ecog120_manual_completeness.json": "sandero_ecog120_manual_gap_evidence.json",
    "sandero_stepway_ecog120_automatic_completeness.json": "sandero_stepway_ecog120_automatic_gap_evidence.json",
}
EXPECTED_EXACT_BLOCKERS = {
    "sandero_tce100_without_exact_configuration",
    "stepway_tce110_without_exact_configuration",
    "duster_hybridg150_without_exact_configuration",
    "duster_4x4_dimensions_without_exact_source_relationship",
}
EXPECTED_AMBIGUOUS_BLOCKERS = {"jogger_mass_table_label_conflict"}


class ReviewError(RuntimeError):
    """Raised when the priority selection contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def weighted_score(scores: Mapping[str, Any]) -> int:
    ensure(set(scores) == set(WEIGHTS), "candidate score dimensions differ")
    total = 0
    for key, weight in WEIGHTS.items():
        value = scores.get(key)
        ensure(isinstance(value, int) and not isinstance(value, bool), f"score must be an integer: {key}")
        ensure(1 <= value <= 5, f"score outside 1-5 scale: {key}")
        total += value * weight
    ensure(total % 5 == 0, "weighted score is not integral")
    return total // 5


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported review version")
    ensure(payload.get("kind") == "post_brochure_priority_selection_review", "unexpected review kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("status") == "complete", "priority review is not complete")
    ensure(payload.get("source_milestone") == "brochure_generic_dimensions_import_closure_review.json", "source milestone differs")

    policy = payload.get("selection_policy")
    ensure(isinstance(policy, dict), "selection policy is missing")
    ensure(policy.get("scale") == "1_to_5", "selection scale differs")
    ensure(policy.get("weights_percent") == WEIGHTS, "selection weights differ")
    ensure(sum(WEIGHTS.values()) == 100, "selection weights do not sum to 100")

    candidates = payload.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 5, "expected five candidates")
    indexed: dict[str, Mapping[str, Any]] = {}
    for item in candidates:
        ensure(isinstance(item, dict), "candidate must be an object")
        code = str(item.get("code", ""))
        ensure(code in EXPECTED_CANDIDATES, f"unexpected candidate: {code}")
        ensure(code not in indexed, f"duplicate candidate: {code}")
        rank, status, score = EXPECTED_CANDIDATES[code]
        ensure(item.get("rank") == rank, f"candidate rank differs: {code}")
        ensure(item.get("status") == status, f"candidate status differs: {code}")
        calculated = weighted_score(item.get("scores", {}))
        ensure(calculated == score, f"calculated score differs: {code}")
        ensure(item.get("weighted_score") == score, f"reported score differs: {code}")
        indexed[code] = item
    ensure([item["rank"] for item in candidates] == [1, 2, 3, 4, 5], "candidate order differs")

    selection = payload.get("selection")
    ensure(isinstance(selection, dict), "selection is missing")
    ensure(selection.get("code") == "data_products_v1_7_0_release_preparation", "selected candidate differs")
    ensure(selection.get("weighted_score") == 100, "selected score differs")
    ensure(max(int(item["weighted_score"]) for item in candidates) == 100, "selected candidate is not highest ranked")
    ensure(indexed[selection["code"]].get("status") == "selected", "selected candidate status differs")

    contract = payload.get("release_preparation_contract")
    ensure(isinstance(contract, dict), "release preparation contract is missing")
    ensure(contract.get("target_version") == "1.7.0", "target release version differs")
    ensure(contract.get("target_tag") == "data-products-v1.7.0", "target release tag differs")
    ensure(contract.get("publication_mode") == "manual_after_verified_preparation", "publication mode differs")
    ensure(
        contract.get("required_assets")
        == [
            "dacia-knowledge-base-data-products-v1.7.0.zip",
            "data-product-release-manifest.json",
            "SHA256SUMS",
        ],
        "required release assets differ",
    )
    ensure(
        set(contract.get("non_goals", []))
        == {"ranking", "recommendations", "cross_scope_pair_generation", "inferred_values", "new_data_imports"},
        "release non-goals differ",
    )
    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Data Products v1.7.0 Release Preparation", "next package differs")


def verify_repository_readiness(payload: Mapping[str, Any]) -> None:
    readiness = payload.get("repository_readiness")
    ensure(isinstance(readiness, dict), "repository readiness is missing")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    ensure("`data-products-v1.6.1`" in roadmap, "latest documented public release is missing")
    ensure(readiness.get("latest_documented_public_release") == "data-products-v1.6.1", "documented release baseline differs")

    active = [row for row in rows(MASTER / "configurations.csv") if row.get("status") == "active"]
    ensure(len(active) == 72, "active configuration count differs")
    ensure(readiness.get("active_configurations") == 72, "reported active configuration count differs")
    ensure(len(SCOPE_SPECS) == 19, "comparison scope registry differs")

    selected_codes: set[str] = set()
    total_pairs = 0
    total_differences = 0
    for completeness_name, evidence_name in SCOPE_SPECS.items():
        completeness = REPORTING / completeness_name
        evidence = REPORTING / evidence_name
        ensure(completeness.is_file(), f"missing completeness scope: {completeness_name}")
        ensure(evidence.is_file(), f"missing evidence scope: {evidence_name}")
        report = configuration_comparison.collect_report(ROOT, completeness, evidence)
        codes = report.get("scope", {}).get("reporting_configuration_codes", [])
        ensure(isinstance(codes, list) and len(codes) >= 2, f"scope is not comparable: {completeness_name}")
        overlap = selected_codes & set(codes)
        ensure(not overlap, f"configuration appears in multiple release scopes: {sorted(overlap)}")
        selected_codes.update(codes)
        total_pairs += len(report.get("pairs", []))
        total_differences += int(report.get("summary", {}).get("total_differences", 0))
    ensure(len(selected_codes) == 72, "release scope configuration union differs")
    ensure(total_pairs == 114, "release pair count differs")
    ensure(total_differences == 1695, "release difference count differs")
    ensure(readiness.get("independent_comparison_scopes") == 19, "reported scope count differs")
    ensure(readiness.get("candidate_release_pair_count") == 114, "reported pair count differs")
    ensure(readiness.get("candidate_release_difference_count") == 1695, "reported difference count differs")
    ensure(readiness.get("candidate_release_files") == 83, "candidate file count differs")
    ensure(readiness.get("candidate_release_files") == 19 * 4 + 2 + 4 + 1, "candidate file formula differs")
    ensure(readiness.get("candidate_release_archive_bytes") == 62077663, "candidate archive size receipt differs")
    ensure(set(readiness.get("candidate_release_formats", [])) == {"JSON", "Markdown", "CSV", "HTML", "XLSX"}, "candidate formats differ")
    boundaries = readiness.get("candidate_release_semantic_boundaries")
    ensure(
        boundaries
        == {
            "cross_scope_pairs_generated": False,
            "ranking_generated": False,
            "recommendations_generated": False,
            "inferred_values_generated": False,
        },
        "candidate semantic boundaries differ",
    )
    evidence = readiness.get("candidate_workflow_evidence")
    ensure(isinstance(evidence, dict), "candidate workflow evidence is missing")
    ensure(evidence.get("workflow_run") == 30212405338, "candidate workflow run differs")
    ensure(evidence.get("artifact_id") == 8634835255, "candidate artifact ID differs")
    digest = str(evidence.get("artifact_digest", ""))
    ensure(digest.startswith("sha256:") and len(digest) == 71, "candidate artifact digest differs")


def verify_blockers(payload: Mapping[str, Any]) -> None:
    candidates = {item["code"]: item for item in payload["candidates"]}
    ensure(
        set(candidates["exact_configuration_expansion_review"].get("blockers", []))
        == EXPECTED_EXACT_BLOCKERS,
        "exact-configuration blocker set differs",
    )
    ensure(
        set(candidates["ambiguous_brochure_evidence_resolution"].get("blockers", []))
        == EXPECTED_AMBIGUOUS_BLOCKERS,
        "ambiguous blocker set differs",
    )

    residual = load_json(RESIDUAL)
    stable_codes = {
        item.get("code")
        for item in residual.get("stable_non_import", [])
        if isinstance(item, dict)
    }
    ensure(
        {
            "sandero_tce100_without_exact_configuration",
            "stepway_tce110_without_exact_configuration",
            "duster_hybridg150_without_exact_configuration",
            "jogger_mass_table_label_conflict",
        }
        <= stable_codes,
        "residual evidence blockers differ",
    )
    closure = load_json(DIMENSION_CLOSURE)
    boundary_codes = {
        item.get("code")
        for item in closure.get("preserved_boundaries", [])
        if isinstance(item, dict)
    }
    ensure(
        "duster_4x4_dimensions_without_exact_source_relationship" in boundary_codes,
        "Duster 4x4 boundary is missing",
    )


def verify_release_tooling() -> None:
    required = (
        ROOT / "tools" / "reporting" / "data_product_release.py",
        ROOT / "tools" / "reporting" / "data_product_release_download.py",
        ROOT / "tools" / "reporting" / "data_product_workspace_verify.py",
        ROOT / "tools" / "reporting" / "configuration_comparison_bundle.py",
        ROOT / "tools" / "configuration_shortlist.py",
    )
    ensure(all(path.is_file() for path in required), "required release tooling is missing")


def verify_state() -> None:
    state = load_json(ROOT / "project" / "state.json")
    ensure(state.get("phase") == "Post-Brochure Priority Selection Review", "project phase differs")
    current = state.get("current_package")
    ensure(isinstance(current, dict), "current package is missing")
    ensure(current.get("name") == "Post-Brochure Priority Selection Review", "current package differs")
    ensure(current.get("status") == "complete", "current package status differs")
    next_package = state.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Data Products v1.7.0 Release Preparation", "next state package differs")
    baseline = state.get("baseline")
    ensure(isinstance(baseline, dict), "state baseline is missing")
    ensure(baseline.get("tests") == 963, "state test baseline differs")
    ensure(baseline.get("rows") == 9688, "state row baseline differs")
    ensure(baseline.get("configuration_values") == 2949, "state value baseline differs")
    ensure(baseline.get("configuration_value_ranges") == 244, "state range baseline differs")
    ensure(baseline.get("attributes") == 385, "state attribute baseline differs")


def check() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_repository_readiness(payload)
    verify_blockers(payload)
    verify_release_tooling()
    verify_state()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the priority selection contract")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.check:
        raise ReviewError("only --check is supported")
    check()
    print("PASS: post-brochure priority selection review")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
