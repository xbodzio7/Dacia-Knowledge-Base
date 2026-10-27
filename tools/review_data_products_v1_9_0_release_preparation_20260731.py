#!/usr/bin/env python3
"""Verify Data Products v1.9.0 release preparation without publishing it."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence
from zipfile import ZipFile

from catalog_completion_history import completion_applied

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_9_0_release_preparation.json"
PUBLIC_RELEASE = ROOT / "project" / "releases" / "data-products-v1.8.1.md"
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import archive_name  # noqa: E402

NEW_CONFIGURATIONS = {
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_stepway_iii_essential_tce110_manual",
    "sandero_stepway_iii_expression_tce110_manual",
    "sandero_stepway_iii_extreme_tce110_manual",
}
MODEL_CODES = [
    "sandero_iii",
    "sandero_stepway_iii",
    "jogger",
    "duster_iii",
    "bigster",
]
MODEL_PRICES = [63900, 71700, 77900, 82000, 101400]


class PreparationError(RuntimeError):
    """Raised when the v1.9.0 preparation contract drifts."""


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
        payload.get("kind") == "data_products_v1_9_0_release_preparation",
        "preparation kind differs",
    )
    ensure(payload.get("prepared_on") == "2026-07-31", "preparation date differs")
    ensure(payload.get("status") == "complete", "preparation is not complete")
    ensure(
        payload.get("selected_by")
        == "sandero_page17_power_torque_rpm_range_import_closure.json",
        "selection source differs",
    )

    target = payload.get("target", {})
    ensure(target.get("version") == "1.9.0", "target version differs")
    ensure(target.get("tag") == "data-products-v1.9.0", "target tag differs")
    ensure(
        target.get("archive_name")
        == "dacia-knowledge-base-data-products-v1.9.0.zip",
        "target archive differs",
    )

    public = payload.get("public_baseline", {})
    expected_public = {
        "version": "1.8.1",
        "tag": "data-products-v1.8.1",
        "release_id": 360138130,
        "source_commit": "0b7009fd1950693e347638a6b96756aeefb43b8a",
        "archive_members": 85,
        "selected_configuration_count": 72,
        "scope_group_count": 19,
        "within_scope_pair_count": 114,
        "recorded_difference_count": 1695,
        "technical_comparison_facet_count": 124,
        "equipment_facet_count": 110,
        "verification": "PASS",
    }
    for key, value in expected_public.items():
        ensure(public.get(key) == value, f"public baseline differs: {key}")

    candidate = payload.get("candidate_baseline", {})
    expected_candidate = {
        "selected_configuration_count": 78,
        "scope_group_count": 20,
        "comparable_scope_count": 20,
        "singleton_scope_count": 0,
        "within_scope_pair_count": 129,
        "recorded_difference_count": 2180,
        "archive_member_count": 89,
        "technical_comparison_facet_count": 127,
        "equipment_facet_count": 110,
        "member_set_change_since_public_baseline": True,
    }
    for key, value in expected_candidate.items():
        ensure(candidate.get(key) == value, f"candidate baseline differs: {key}")
    semantic = candidate.get("semantic_boundaries", {})
    for key in (
        "new_source_backed_configurations",
        "new_reporting_scope",
        "new_within_scope_pairs",
    ):
        ensure(semantic.get(key) is True, f"expected release expansion differs: {key}")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        ensure(semantic.get(key) is False, f"forbidden semantic output differs: {key}")

    delta = payload.get("release_delta", {})
    ensure(
        set(delta.get("new_configuration_codes", [])) == NEW_CONFIGURATIONS,
        "new configuration set differs",
    )
    ensure(
        delta.get("new_reporting_scope")
        == "sandero_tce100_stepway_tce110_manual",
        "new reporting scope differs",
    )
    expected_delta = {
        "selected_configuration_delta": 6,
        "scope_group_delta": 1,
        "within_scope_pair_delta": 15,
        "recorded_difference_delta": 485,
        "archive_member_delta": 4,
        "technical_comparison_facet_delta": 3,
        "equipment_facet_delta": 0,
    }
    for key, value in expected_delta.items():
        ensure(delta.get(key) == value, f"release delta differs: {key}")

    shortlist = payload.get("shortlist_contract", {})
    ensure(shortlist.get("active_configuration_count") == 78, "shortlist count differs")
    ensure(shortlist.get("equipment_facet_count") == 110, "equipment count differs")
    ensure(shortlist.get("visible_equipment_choices") == 108, "visible equipment differs")
    ensure(shortlist.get("rear_view_camera_matches") == 71, "camera count differs")
    ensure(shortlist.get("missing_and_unknown_are_exclusions") is True, "unknown handling differs")
    order = shortlist.get("model_order", [])
    ensure([item.get("model_code") for item in order] == MODEL_CODES, "model order differs")
    ensure(
        [item.get("minimum_catalog_price_pln") for item in order] == MODEL_PRICES,
        "model prices differ",
    )

    ensure(
        payload.get("publication_lifecycle")
        == ["preflight", "publish", "independent_public_audit", "record_publication"],
        "publication lifecycle differs",
    )
    preflight = payload.get("preflight_contract", {})
    ensure(preflight.get("source") == "exact squash-merged preparation commit", "preflight source differs")
    ensure(preflight.get("build_count") == 2, "preflight build count differs")
    required = set(preflight.get("required_checks", []))
    ensure("byte_identical_rebuilds" in required, "byte-identity check is missing")
    ensure("public_v1_8_1_control_download" in required, "public control is missing")
    ensure("tag_and_release_absence" in required, "publication absence check is missing")

    publication = payload.get("publication_state", {})
    ensure(publication.get("publication_performed") is False, "publication already performed")
    ensure(publication.get("tag_created") is False, "tag already created")
    ensure(publication.get("release_created") is False, "release already created")
    ensure(publication.get("final_source_commit") is None, "final commit was guessed")
    ensure(publication.get("final_asset_identity") is None, "final assets were guessed")

    baseline = payload.get("repository_baseline", {})
    ensure(baseline.get("tests") == 1676, "test baseline differs")
    ensure(baseline.get("rows") == 11380, "master row baseline differs")
    ensure(baseline.get("configuration_values") == 3498, "value baseline differs")
    ensure(baseline.get("configuration_value_ranges") == 298, "range baseline differs")
    ensure(baseline.get("availability_records") == 5770, "availability baseline differs")
    ensure(
        payload.get("next_package", {}).get("name")
        == "Data Products v1.9.0 Preflight",
        "next package differs",
    )


def verify_repository() -> None:
    ensure(PUBLIC_RELEASE.is_file(), "v1.8.1 publication record is missing")
    public_text = PUBLIC_RELEASE.read_text(encoding="utf-8")
    ensure("Release ID: `360138130`" in public_text, "v1.8.1 release ID differs")
    ensure("85 deterministic archive members" in public_text, "v1.8.1 archive count differs")
    ensure(
        "0b7009fd1950693e347638a6b96756aeefb43b8a" in public_text,
        "v1.8.1 source differs",
    )

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release"
        manifest = create_release_assets(ROOT, output, "1.9.0", "6" * 40)
        ensure(manifest.get("release_version") == "1.9.0", "candidate version differs")
        ensure(manifest.get("selected_configuration_count") == 78, "candidate configuration count differs")
        ensure(manifest.get("scope_group_count") == 20, "candidate scope count differs")
        ensure(manifest.get("comparable_scope_count") == 20, "candidate comparable count differs")
        ensure(manifest.get("singleton_scope_count") == 0, "candidate singleton count differs")
        for key in (
            "cross_scope_pairs_generated",
            "ranking_generated",
            "recommendations_generated",
            "inferred_values_generated",
        ):
            ensure(manifest.get(key) is False, f"candidate semantic boundary differs: {key}")

        with ZipFile(output / archive_name("1.9.0")) as archive:
            names = archive.namelist()
            ensure(len(names) == 89, "candidate archive member count differs")
            ensure(len(set(names)) == 89, "candidate archive contains duplicates")
            shortlist = json.loads(
                archive.read("shortlist/configuration-shortlist.json")
            )
            bundle = json.loads(
                archive.read("comparison-bundle/comparison-bundle-manifest.json")
            )
            notes = archive.read("RELEASE_NOTES.md").decode("utf-8")

    results = shortlist.get("results", [])
    ensure(len(results) == 78, "release shortlist count differs")
    codes = {item.get("configuration_code") for item in results}
    ensure(NEW_CONFIGURATIONS <= codes, "new configurations are missing from shortlist")

    groups = bundle.get("groups", [])
    ensure(len(groups) == 20, "release group count differs")
    ensure(sum(int(group.get("pair_count", 0)) for group in groups) == 129, "release pair count differs")
    matching = [
        group
        for group in groups
        if set(group.get("configuration_codes", [])) == NEW_CONFIGURATIONS
    ]
    ensure(len(matching) == 1, "new reporting scope membership differs")
    ensure(matching[0].get("pair_count") == 15, "new reporting scope pair count differs")

    for fragment in (
        "six new source-backed manual configurations",
        "78 active configurations",
        "20 independent scopes",
        "129 within-scope pairs",
        "2,180 recorded differences",
        "89 deterministic archive members",
        "127 technical comparison facets",
        "110 equipment facets",
        "No cross-scope pairs, ranking, recommendations or inferred values",
        "v1.8.1 remains immutable",
    ):
        ensure(fragment in notes, f"release notes omit: {fragment}")

    state = load_json(STATE)
    ensure(
        state.get("current_package", {}).get("name")
        == "Data Products v1.9.0 Release Preparation",
        "current package differs",
    )
    ensure(state.get("current_package", {}).get("status") == "complete", "current package is not complete")
    ensure(
        state.get("next_package", {}).get("name")
        == "Data Products v1.9.0 Preflight",
        "next state package differs",
    )
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests") == 1676, "state test baseline differs")
    ensure(baseline.get("rows") == 11380, "state row baseline differs")
    ensure(baseline.get("configuration_values") == 3498, "state value baseline differs")
    ensure(baseline.get("configuration_value_ranges") == 298, "state range baseline differs")
    ensure(baseline.get("availability_records") == 5770, "state availability baseline differs")


def verify() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    if completion_applied(ROOT):
        state = load_json(STATE)
        ensure(isinstance(state.get("current_package"), dict), "current project state is missing")
        return
    verify_repository()


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
    print("PASS: Data Products v1.9.0 release preparation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
