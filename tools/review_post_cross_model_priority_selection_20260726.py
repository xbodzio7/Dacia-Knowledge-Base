#!/usr/bin/env python3
"""Verify the priority selected after cross-model navigation closure."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "post_cross_model_priority_selection_review.json"
CLOSURE = ROOT / "data" / "reporting" / "cross_model_comparison_view_closure_review.json"
PUBLIC_RELEASE = ROOT / "project" / "releases" / "data-products-v1.7.0.md"
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import archive_name  # noqa: E402


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
        ensure(isinstance(value, int) and 1 <= value <= 5, f"invalid score: {key}")
        ensure(isinstance(weight, int), f"invalid weight: {key}")
        total += value * weight / 5
    return round(total)


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "review version differs")
    ensure(
        payload.get("kind") == "post_cross_model_priority_selection_review",
        "review kind differs",
    )
    ensure(payload.get("reviewed_on") == "2026-07-26", "review date differs")
    ensure(payload.get("status") == "complete", "review is not complete")
    ensure(
        payload.get("source_milestone")
        == "cross_model_comparison_view_closure_review.json",
        "source milestone differs",
    )

    policy = payload.get("selection_policy")
    ensure(isinstance(policy, Mapping), "selection policy is missing")
    weights = policy.get("weights_percent")
    ensure(isinstance(weights, Mapping), "selection weights are missing")
    ensure(
        dict(weights)
        == {
            "consumer_value": 30,
            "evidence_readiness": 25,
            "existing_tooling_reuse": 20,
            "low_implementation_risk": 15,
            "dependency_clearance": 10,
        },
        "selection weights differ",
    )
    ensure(sum(int(value) for value in weights.values()) == 100, "weights do not total 100")

    readiness = payload.get("repository_readiness")
    ensure(isinstance(readiness, Mapping), "repository readiness is missing")
    expected_readiness = {
        "latest_documented_public_release": "data-products-v1.7.0",
        "public_release_archive_members": 83,
        "current_candidate_archive_members": 85,
        "active_configurations": 72,
        "independent_comparison_scopes": 19,
        "within_scope_pairs": 114,
        "recorded_differences": 1695,
        "technical_comparison_facets": 124,
        "equipment_facets": 110,
    }
    for key, value in expected_readiness.items():
        ensure(readiness.get(key) == value, f"repository readiness differs: {key}")
    ensure(
        readiness.get("unpublished_products")
        == [
            "cross-model/cross-model-comparison-view.json",
            "cross-model/cross-model-comparison-view.html",
        ],
        "unpublished product list differs",
    )
    boundaries = readiness.get("candidate_release_semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "candidate boundaries are missing")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        ensure(boundaries.get(key) is False, f"candidate boundary differs: {key}")

    candidates = payload.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 5, "candidate list differs")
    ensure([item.get("rank") for item in candidates] == [1, 2, 3, 4, 5], "candidate ranks differ")
    expected_scores = [100, 84, 67, 57, 46]
    for item, expected in zip(candidates, expected_scores, strict=True):
        ensure(isinstance(item, Mapping), "candidate is invalid")
        scores = item.get("scores")
        ensure(isinstance(scores, Mapping), "candidate scores are missing")
        calculated = weighted_score(scores, weights)
        ensure(calculated == expected, f"calculated score differs: {item.get('code')}")
        ensure(item.get("weighted_score") == expected, f"stored score differs: {item.get('code')}")
    ensure(candidates[0].get("status") == "selected", "top candidate is not selected")
    ensure(
        candidates[0].get("code") == "data_products_v1_8_0_release_preparation",
        "top candidate differs",
    )
    ensure(candidates[1].get("status") == "follow_up_after_release", "UI follow-up status differs")
    ensure(candidates[2].get("status") == "strategic_later", "PDF status differs")
    ensure(candidates[3].get("status") == "blocked_evidence", "configuration status differs")
    ensure(candidates[4].get("status") == "blocked_source", "Spring status differs")

    selection = payload.get("selection")
    ensure(isinstance(selection, Mapping), "selection is missing")
    ensure(
        selection.get("code") == "data_products_v1_8_0_release_preparation",
        "selected code differs",
    )
    ensure(selection.get("weighted_score") == 100, "selected score differs")

    contract = payload.get("release_preparation_contract")
    ensure(isinstance(contract, Mapping), "release preparation contract is missing")
    ensure(contract.get("target_version") == "1.8.0", "target version differs")
    ensure(contract.get("target_tag") == "data-products-v1.8.0", "target tag differs")
    ensure(contract.get("expected_archive_members") == 85, "archive target differs")
    ensure(
        contract.get("required_new_members")
        == [
            "cross-model/cross-model-comparison-view.json",
            "cross-model/cross-model-comparison-view.html",
        ],
        "required new members differ",
    )
    ensure(
        contract.get("required_assets")
        == [
            "dacia-knowledge-base-data-products-v1.8.0.zip",
            "data-product-release-manifest.json",
            "SHA256SUMS",
        ],
        "required assets differ",
    )
    ensure(
        payload.get("next_package", {}).get("name")
        == "Data Products v1.8.0 Release Preparation",
        "next package differs",
    )


def verify_repository(payload: Mapping[str, Any]) -> None:
    closure = load_json(CLOSURE)
    ensure(closure.get("status") == "complete", "cross-model closure is not complete")
    ensure(
        closure.get("closure_decision", {}).get("result") == "closed",
        "cross-model milestone is not closed",
    )
    ensure(PUBLIC_RELEASE.is_file(), "v1.7.0 publication record is missing")
    public_text = PUBLIC_RELEASE.read_text(encoding="utf-8")
    ensure("data-products-v1.7.0" in public_text, "public release tag is missing")
    ensure("83 deterministic archive members" in public_text, "public archive count differs")
    ensure("1,695 recorded differences" in public_text, "public difference count differs")

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release"
        manifest = create_release_assets(ROOT, output, "1.8.0", "3" * 40)
        archive_path = output / archive_name("1.8.0")
        ensure(manifest.get("selected_configuration_count") == 72, "candidate configuration count differs")
        ensure(manifest.get("scope_group_count") == 19, "candidate scope count differs")
        ensure(manifest.get("cross_scope_pairs_generated") is False, "candidate created cross-scope pairs")
        ensure(manifest.get("ranking_generated") is False, "candidate created ranking")
        ensure(manifest.get("recommendations_generated") is False, "candidate created recommendations")
        ensure(manifest.get("inferred_values_generated") is False, "candidate created inferred values")
        with ZipFile(archive_path) as archive:
            names = archive.namelist()
            ensure(len(names) == 85, "candidate archive member count differs")
            ensure(
                "cross-model/cross-model-comparison-view.json" in names,
                "candidate cross-model JSON is missing",
            )
            ensure(
                "cross-model/cross-model-comparison-view.html" in names,
                "candidate cross-model HTML is missing",
            )
            bundle = json.loads(
                archive.read(
                    "comparison-bundle/comparison-bundle-manifest.json"
                ).decode("utf-8")
            )
        groups = bundle.get("groups")
        ensure(isinstance(groups, list) and len(groups) == 19, "candidate bundle groups differ")
        ensure(
            sum(int(group.get("pair_count", 0)) for group in groups) == 114,
            "candidate pair count differs",
        )
        ensure(
            sum(int(group.get("total_differences", 0)) for group in groups) == 1695,
            "candidate difference count differs",
        )

    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "project phase is missing")
    current = state.get("current_package")
    ensure(isinstance(current, Mapping), "current package is missing")
    ensure(isinstance(current.get("name"), str) and bool(current["name"]), "current package name is missing")
    ensure(current.get("status") in {"planned", "active", "blocked", "complete"}, "current package status differs")
    next_package = state.get("next_package")
    ensure(isinstance(next_package, Mapping), "next package is missing")
    ensure(isinstance(next_package.get("name"), str) and bool(next_package["name"]), "next package name is missing")
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests", 0) >= 1006, "test baseline regressed")
    ensure(baseline.get("rows", 0) >= 9688, "master row baseline regressed")
    ensure(baseline.get("configuration_values", 0) >= 2949, "configuration values regressed")
    ensure(baseline.get("configuration_value_ranges", 0) >= 244, "configuration ranges regressed")
    ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")

def verify() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_repository(payload)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the priority-selection contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ReviewError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: post-cross-model priority selection review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
