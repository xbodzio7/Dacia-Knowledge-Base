#!/usr/bin/env python3
"""Verify Data Products v1.8.0 release preparation without publishing it."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from catalog_completion_history import completion_applied
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_8_0_release_preparation.json"
SELECTION = ROOT / "data" / "reporting" / "post_cross_model_priority_selection_review.json"
PUBLIC_RELEASE = ROOT / "project" / "releases" / "data-products-v1.7.0.md"
TARGET_RELEASE = ROOT / "project" / "releases" / "data-products-v1.8.0.md"
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import archive_name  # noqa: E402


class PreparationError(RuntimeError):
    """Raised when the release-preparation contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise PreparationError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "preparation version differs")
    ensure(
        payload.get("kind") == "data_products_v1_8_0_release_preparation",
        "preparation kind differs",
    )
    ensure(payload.get("prepared_on") == "2026-07-26", "preparation date differs")
    ensure(payload.get("status") == "complete", "preparation is not complete")
    ensure(
        payload.get("selected_by")
        == "post_cross_model_priority_selection_review.json",
        "selection source differs",
    )

    target = payload.get("target")
    ensure(isinstance(target, Mapping), "target is missing")
    ensure(target.get("version") == "1.8.0", "target version differs")
    ensure(target.get("tag") == "data-products-v1.8.0", "target tag differs")
    ensure(
        target.get("archive_name")
        == "dacia-knowledge-base-data-products-v1.8.0.zip",
        "target archive differs",
    )
    ensure(target.get("manifest_name") == "data-product-release-manifest.json", "manifest name differs")
    ensure(target.get("checksums_name") == "SHA256SUMS", "checksums name differs")

    public = payload.get("public_baseline")
    ensure(isinstance(public, Mapping), "public baseline is missing")
    ensure(public.get("version") == "1.7.0", "public version differs")
    ensure(public.get("release_id") == 360090447, "public release ID differs")
    ensure(
        public.get("source_commit")
        == "99e0e19b86cad6eae619f37702464e6a5a761cd8",
        "public source commit differs",
    )
    ensure(public.get("archive_members") == 83, "public archive count differs")
    ensure(public.get("verification") == "PASS", "public verification differs")

    candidate = payload.get("candidate_baseline")
    ensure(isinstance(candidate, Mapping), "candidate baseline is missing")
    expected = {
        "selected_configuration_count": 72,
        "scope_group_count": 19,
        "comparable_scope_count": 19,
        "singleton_scope_count": 0,
        "within_scope_pair_count": 114,
        "recorded_difference_count": 1695,
        "archive_member_count": 85,
        "technical_comparison_facet_count": 124,
        "equipment_facet_count": 110,
    }
    for key, value in expected.items():
        ensure(candidate.get(key) == value, f"candidate baseline differs: {key}")
    ensure(
        candidate.get("new_members_since_public_baseline")
        == [
            "cross-model/cross-model-comparison-view.json",
            "cross-model/cross-model-comparison-view.html",
        ],
        "candidate new members differ",
    )
    boundaries = candidate.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "candidate boundaries are missing")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        ensure(boundaries.get(key) is False, f"candidate boundary differs: {key}")

    cross_model = payload.get("cross_model_product_contract")
    ensure(isinstance(cross_model, Mapping), "cross-model contract is missing")
    cross_expected = {
        "model_family_count": 5,
        "reporting_scope_count": 19,
        "active_configuration_count": 72,
        "within_scope_pair_count": 114,
        "json_comparison_paths": 76,
        "json_navigation_paths": 2,
        "html_local_file_links": 57,
        "standalone_html": True,
        "javascript_used": False,
        "runtime_image_dependency": False,
        "unknown_state": "not_stated",
    }
    for key, value in cross_expected.items():
        ensure(cross_model.get(key) == value, f"cross-model contract differs: {key}")
    ensure(
        cross_model.get("unknown_seat_models") == ["bigster", "duster_iii"],
        "unknown-seat models differ",
    )

    lifecycle = payload.get("publication_lifecycle")
    ensure(
        lifecycle == [
            "preflight",
            "publish",
            "independent_public_audit",
            "record_publication",
        ],
        "publication lifecycle differs",
    )
    preflight = payload.get("preflight_contract")
    ensure(isinstance(preflight, Mapping), "preflight contract is missing")
    ensure(preflight.get("build_count") == 2, "preflight build count differs")
    ensure(
        preflight.get("source") == "exact squash-merged preparation commit",
        "preflight source differs",
    )

    publication = payload.get("publication_state")
    ensure(isinstance(publication, Mapping), "publication state is missing")
    ensure(publication.get("publication_performed") is False, "publication already performed")
    ensure(publication.get("tag_created") is False, "tag already recorded")
    ensure(publication.get("release_created") is False, "release already recorded")
    ensure(publication.get("final_source_commit") is None, "final commit was guessed")
    ensure(publication.get("final_asset_identity") is None, "final asset identity was guessed")
    ensure(
        payload.get("next_package", {}).get("name") == "Data Products v1.8.0 Preflight",
        "next package differs",
    )


def verify_repository(payload: Mapping[str, Any]) -> None:
    selection = load_json(SELECTION)
    ensure(
        selection.get("selection", {}).get("code")
        == "data_products_v1_8_0_release_preparation",
        "v1.8.0 preparation was not selected",
    )
    ensure(PUBLIC_RELEASE.is_file(), "v1.7.0 publication record is missing")

    public_text = PUBLIC_RELEASE.read_text(encoding="utf-8")
    ensure("83 deterministic archive members" in public_text, "v1.7.0 archive count differs")
    ensure("1,695 recorded differences" in public_text, "v1.7.0 difference count differs")

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release"
        manifest = create_release_assets(ROOT, output, "1.8.0", "4" * 40)
        archive_path = output / archive_name("1.8.0")
        ensure(manifest.get("release_version") == "1.8.0", "candidate version differs")
        ensure(manifest.get("release_tag") == "data-products-v1.8.0", "candidate tag differs")
        ensure(manifest.get("selected_configuration_count") == 72, "candidate configuration count differs")
        ensure(manifest.get("scope_group_count") == 19, "candidate scope count differs")
        ensure(manifest.get("comparable_scope_count") == 19, "candidate comparable count differs")
        ensure(manifest.get("singleton_scope_count") == 0, "candidate singleton count differs")
        ensure(manifest.get("cross_scope_pairs_generated") is False, "candidate created cross-scope pairs")
        ensure(manifest.get("ranking_generated") is False, "candidate created ranking")
        ensure(manifest.get("recommendations_generated") is False, "candidate created recommendations")
        ensure(manifest.get("inferred_values_generated") is False, "candidate created inferred values")

        with ZipFile(archive_path) as archive:
            names = archive.namelist()
            ensure(len(names) == 85, "candidate archive member count differs")
            ensure(len(set(names)) == 85, "candidate archive has duplicate members")
            for name in (
                "cross-model/cross-model-comparison-view.json",
                "cross-model/cross-model-comparison-view.html",
            ):
                ensure(name in names, f"candidate member is missing: {name}")
            cross_view = json.loads(
                archive.read("cross-model/cross-model-comparison-view.json").decode("utf-8")
            )
            cross_html = archive.read("cross-model/cross-model-comparison-view.html").decode("utf-8")
            notes = archive.read("RELEASE_NOTES.md").decode("utf-8")
            bundle = json.loads(
                archive.read("comparison-bundle/comparison-bundle-manifest.json").decode("utf-8")
            )
        summary = cross_view.get("summary", {})
        ensure(summary.get("model_family_count") == 5, "cross-model family count differs")
        ensure(summary.get("reporting_scope_count") == 19, "cross-model scope count differs")
        ensure(summary.get("active_configuration_count") == 72, "cross-model configuration count differs")
        ensure(summary.get("within_scope_pair_count") == 114, "cross-model pair count differs")
        ensure(summary.get("cross_scope_pairs_generated") is False, "cross-model created cross-scope pairs")
        ensure("<script" not in cross_html.lower(), "cross-model HTML contains JavaScript")
        ensure("nie podano" in cross_html, "cross-model unknown label is missing")
        ensure("scope-preserving cross-model navigation view" in notes, "release notes omit cross-model product")
        groups = bundle.get("groups")
        ensure(isinstance(groups, list) and len(groups) == 19, "bundle group count differs")
        ensure(sum(int(group.get("pair_count", 0)) for group in groups) == 114, "bundle pair count differs")
        ensure(
            sum(int(group.get("total_differences", 0)) for group in groups) == 1695,
            "bundle difference count differs",
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
    ensure(baseline.get("tests", 0) >= 1014, "test baseline regressed")
    ensure(baseline.get("csv_files", 0) >= 46, "CSV baseline regressed")
    ensure(baseline.get("rows", 0) >= 9688, "master row baseline regressed")
    ensure(baseline.get("configuration_values", 0) >= 2949, "configuration values regressed")
    ensure(baseline.get("configuration_value_ranges", 0) >= 244, "configuration ranges regressed")
    ensure(baseline.get("availability_records", 0) >= 4754, "availability baseline regressed")
    ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")

def verify() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    if completion_applied(ROOT):
        state = load_json(ROOT / "project" / "state.json")
        ensure(isinstance(state.get("current_package"), dict), "current project state is missing")
        return
    verify_repository(payload)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the preparation contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, PreparationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Data Products v1.8.0 release preparation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
