#!/usr/bin/env python3
"""Verify Data Products v1.9.0 release preparation without publishing it."""

from __future__ import annotations

import argparse
import json
import re
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
NEW_SCOPE = "sandero_tce100_stepway_tce110_manual"
MODEL_CODES = [
    "sandero_iii",
    "sandero_stepway_iii",
    "jogger",
    "duster_iii",
    "bigster",
]
MODEL_PRICES = [63900, 71700, 77900, 82000, 101400]


class PreparationError(RuntimeError):
    """Raised when the v1.9.0 release-preparation contract drifts."""


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

    target = payload.get("target")
    ensure(isinstance(target, Mapping), "target is missing")
    ensure(target.get("version") == "1.9.0", "target version differs")
    ensure(target.get("tag") == "data-products-v1.9.0", "target tag differs")
    ensure(
        target.get("archive_name")
        == "dacia-knowledge-base-data-products-v1.9.0.zip",
        "target archive differs",
    )
    ensure(
        target.get("manifest_name") == "data-product-release-manifest.json",
        "manifest name differs",
    )
    ensure(target.get("checksums_name") == "SHA256SUMS", "checksums name differs")

    public = payload.get("public_baseline")
    ensure(isinstance(public, Mapping), "public baseline is missing")
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

    candidate = payload.get("candidate_baseline")
    ensure(isinstance(candidate, Mapping), "candidate baseline is missing")
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
    boundaries = candidate.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "candidate semantic boundaries are missing")
    ensure(boundaries.get("new_source_backed_configurations") is True, "new configuration boundary differs")
    ensure(boundaries.get("new_reporting_scope") is True, "new scope boundary differs")
    ensure(boundaries.get("new_within_scope_pairs") is True, "new pair boundary differs")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        ensure(boundaries.get(key) is False, f"forbidden semantic output differs: {key}")

    delta = payload.get("release_delta")
    ensure(isinstance(delta, Mapping), "release delta is missing")
    ensure(set(delta.get("new_configuration_codes", [])) == NEW_CONFIGURATIONS, "new configuration set differs")
    ensure(delta.get("new_reporting_scope") == NEW_SCOPE, "new reporting scope differs")
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

    shortlist = payload.get("shortlist_contract")
    ensure(isinstance(shortlist, Mapping), "shortlist contract is missing")
    ensure(shortlist.get("active_configuration_count") == 78, "shortlist count differs")
    ensure(shortlist.get("equipment_facet_count") == 110, "equipment facet count differs")
    ensure(shortlist.get("visible_equipment_choices") == 108, "visible equipment count differs")
    ensure(shortlist.get("rear_view_camera_matches") == 71, "camera result count differs")
    ensure(shortlist.get("missing_and_unknown_are_exclusions") is True, "unknown handling differs")
    order = shortlist.get("model_order")
    ensure(isinstance(order, list) and len(order) == 5, "model order is missing")
    ensure([item.get("model_code") for item in order] == MODEL_CODES, "model code order differs")
    ensure([item.get("minimum_catalog_price_pln") for item in order] == MODEL_PRICES, "model prices differ")

    ensure(
        payload.get("publication_lifecycle")
        == ["preflight", "publish", "independent_public_audit", "record_publication"],
        "publication lifecycle differs",
    )
    preflight = payload.get("preflight_contract")
    ensure(isinstance(preflight, Mapping), "preflight contract is missing")
    ensure(preflight.get("source") == "exact squash-merged preparation commit", "preflight source differs")
    ensure(preflight.get("build_count") == 2, "preflight build count differs")
    required = set(preflight.get("required_checks", []))
    ensure("byte_identical_rebuilds" in required, "byte-identity preflight is missing")
    ensure("public_v1_8_1_control_download" in required, "public control download is missing")
    ensure("tag_and_release_absence" in required, "tag-absence preflight is missing")

    publication = payload.get("publication_state")
    ensure(isinstance(publication, Mapping), "publication state is missing")
    ensure(publication.get("publication_performed") is False, "publication already performed")
    ensure(publication.get("tag_created") is False, "tag already recorded")
    ensure(publication.get("release_created") is False, "release already recorded")
    ensure(publication.get("final_source_commit") is None, "final commit was guessed")
    ensure(publication.get("final_asset_identity") is None, "final asset identity was guessed")
    ensure(
        payload.get("next_package", {}).get("name") == "Data Products v1.9.0 Preflight",
        "next package differs",
    )


def embedded_catalog(rendered: str) -> dict[str, Any]:
    match = re.search(
        r'<script id="configuration-catalog" type="application/json">(.*?)</script>',
        rendered,
        flags=re.DOTALL,
    )
    ensure(match is not None, "embedded shortlist catalog is missing")
    payload = json.loads(match.group(1))
    ensure(isinstance(payload, dict), "embedded shortlist catalog is invalid")
    return payload


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
        archive_path = output / archive_name("1.9.0")
        ensure(manifest.get("release_version") == "1.9.0", "candidate version differs")
        ensure(manifest.get("release_tag") == "data-products-v1.9.0", "candidate tag differs")
        ensure(manifest.get("selected_configuration_count") == 78, "candidate configuration count differs")
        ensure(manifest.get("scope_group_count") == 20, "candidate scope count differs")
        ensure(manifest.get("comparable_scope_count") == 20, "candidate comparable count differs")
        ensure(manifest.get("singleton_scope_count") == 0, "candidate singleton count differs")
        ensure(manifest.get("cross_scope_pairs_generated") is False, "candidate created cross-scope pairs")
        ensure(manifest.get("ranking_generated") is False, "candidate created ranking")
        ensure(manifest.get("recommendations_generated") is False, "candidate created recommendations")
        ensure(manifest.get("inferred_values_generated") is False, "candidate created inferred values")

        with ZipFile(archive_path) as archive:
            names = archive.namelist()
            ensure(len(names) == 89, "candidate archive member count differs")
            ensure(len(set(names)) == 89, "candidate archive has duplicate members")
            bundle = json.loads(
                archive.read("comparison-bundle/comparison-bundle-manifest.json")
            )
            rendered = archive.read("shortlist/configuration-shortlist.html").decode("utf-8")
            notes = archive.read("RELEASE_NOTES.md").decode("utf-8")

    ensure(bundle.get("selected_configuration_count") == 78, "bundle configuration count differs")
    ensure(bundle.get("scope_group_count") == 20, "bundle scope count differs")
    ensure(bundle.get("comparable_scope_count") == 20, "bundle comparable count differs")
    ensure(bundle.get("singleton_scope_count") == 0, "bundle singleton count differs")
    codes = set(bundle.get("selected_configuration_codes", []))
    ensure(NEW_CONFIGURATIONS <= codes, "new configurations are missing from the bundle")
    groups = bundle.get("groups")
    ensure(isinstance(groups, list), "bundle groups are missing")
    ensure(sum(int(group.get("pair_count", 0)) for group in groups) == 129, "bundle pair count differs")
    ensure(sum(int(group.get("total_differences", 0)) for group in groups) == 2180, "bundle difference count differs")
    new_groups = [group for group in groups if group.get("scope") == NEW_SCOPE]
    ensure(len(new_groups) == 1, "new reporting scope is missing or duplicated")
    ensure(set(new_groups[0].get("configuration_codes", [])) == NEW_CONFIGURATIONS, "new scope membership differs")
    ensure(new_groups[0].get("pair_count") == 15, "new scope pair count differs")

    catalog = embedded_catalog(rendered)
    configurations = catalog.get("configurations")
    facets = catalog.get("facets")
    ensure(isinstance(configurations, list) and len(configurations) == 78, "embedded configuration count differs")
    ensure(isinstance(facets, Mapping), "embedded facets are missing")
    embedded_codes = {item.get("configuration_code") for item in configurations}
    ensure(NEW_CONFIGURATIONS <= embedded_codes, "new configurations are missing from shortlist")
    equipment = facets.get("equipment")
    comparison_values = facets.get("comparison_values")
    models = facets.get("models")
    ensure(isinstance(equipment, list) and len(equipment) == 110, "embedded equipment count differs")
    ensure(isinstance(comparison_values, list) and len(comparison_values) == 127, "technical facet count differs")
    ensure(isinstance(models, list) and len(models) == 5, "embedded model count differs")
    ensure([item.get("code") for item in models] == MODEL_CODES, "embedded model order differs")
    ensure([item.get("minimum_catalog_price_pln") for item in models] == MODEL_PRICES, "embedded model prices differ")
    visible = sum(
        1
        for item in equipment
        if int(item.get("states", {}).get("standard", 0))
        + int(item.get("states", {}).get("optional", 0))
        > 0
    )
    ensure(visible == 108, "embedded visible equipment count differs")
    camera = next((item for item in equipment if item.get("code") == "rear_view_camera"), None)
    ensure(isinstance(camera, Mapping), "rear-view camera facet is missing")
    camera_matches = int(camera.get("states", {}).get("standard", 0)) + int(
        camera.get("states", {}).get("optional", 0)
    )
    ensure(camera_matches == 71, "embedded camera match count differs")

    required_note_fragments = (
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
    )
    for fragment in required_note_fragments:
        ensure(fragment in notes, f"release notes omit: {fragment}")

    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "project phase is missing")
    current = state.get("current_package")
    ensure(isinstance(current, Mapping), "current package is missing")
    ensure(current.get("status") in {"planned", "active", "blocked", "complete"}, "current status differs")
    next_package = state.get("next_package")
    ensure(isinstance(next_package, Mapping), "next package is missing")
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests", 0) >= 1684, "test baseline regressed")
    ensure(baseline.get("csv_files", 0) >= 46, "CSV baseline regressed")
    ensure(baseline.get("rows", 0) >= 11380, "master row baseline regressed")
    ensure(baseline.get("configuration_values", 0) >= 3498, "configuration values regressed")
    ensure(baseline.get("configuration_value_ranges", 0) >= 298, "configuration ranges regressed")
    ensure(baseline.get("availability_records", 0) >= 5770, "availability baseline regressed")
    ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")


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
