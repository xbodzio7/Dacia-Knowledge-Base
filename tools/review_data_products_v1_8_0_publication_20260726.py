#!/usr/bin/env python3
"""Verify the durable Data Products v1.8.0 publication record."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "reporting" / "data_products_v1_8_0_publication_audit.json"
RELEASE_RECORD = ROOT / "project" / "releases" / "data-products-v1.8.0.md"
PREPARATION = ROOT / "data" / "reporting" / "data_products_v1_8_0_release_preparation.json"
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import archive_name  # noqa: E402

SOURCE_SHA = "becd218228e3f4f0cdd312b0ed836ade487422b1"
EXPECTED_ASSETS = {
    "dacia-knowledge-base-data-products-v1.8.0.zip": {
        "asset_id": 490686120,
        "size_bytes": 62141187,
        "sha256": "2af02fc148446eb3789ed4e19f32c52e54c484464ca1cdb2ba1048ae02b7cec9",
    },
    "data-product-release-manifest.json": {
        "asset_id": 490686121,
        "size_bytes": 20606,
        "sha256": "af9366e92543a8aadca5e0a94a43391d202bce71f684bf3d9583913764f0de3b",
    },
    "SHA256SUMS": {
        "asset_id": 490686122,
        "size_bytes": 213,
        "sha256": "8649769104a5b695c2b6e21177c032523fdc0a694ea11931ce95a6a5ae428596",
    },
}


class PublicationError(RuntimeError):
    """Raised when the publication record drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise PublicationError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_audit(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "audit version differs")
    ensure(
        payload.get("kind") == "data_products_v1_8_0_publication_audit",
        "audit kind differs",
    )
    ensure(payload.get("recorded_on") == "2026-07-26", "audit date differs")
    ensure(payload.get("status") == "PASS", "audit did not pass")

    release = payload.get("release")
    ensure(isinstance(release, Mapping), "release identity is missing")
    ensure(release.get("version") == "1.8.0", "release version differs")
    ensure(release.get("tag") == "data-products-v1.8.0", "release tag differs")
    ensure(release.get("release_id") == 360115681, "release ID differs")
    ensure(release.get("published_at") == "2026-07-26T20:50:24Z", "publication time differs")
    ensure(release.get("source_commit") == SOURCE_SHA, "source commit differs")
    ensure(release.get("draft") is False, "release is draft")
    ensure(release.get("prerelease") is False, "release is prerelease")
    ensure(release.get("asset_count") == 3, "asset count differs")

    workflow = payload.get("workflow_evidence")
    ensure(isinstance(workflow, Mapping), "workflow evidence is missing")
    ensure(workflow.get("preparation_pull_request") == 284, "preparation PR differs")
    ensure(workflow.get("preflight_pull_request") == 285, "preflight PR differs")
    ensure(workflow.get("preflight_run") == 30219704364, "preflight run differs")
    ensure(workflow.get("publication_pull_request") == 286, "publication PR differs")
    ensure(workflow.get("publication_run") == 30219809423, "publication run differs")
    ensure(workflow.get("independent_audit_pull_request") == 287, "audit PR differs")
    ensure(workflow.get("independent_audit_run") == 30220008441, "audit run differs")

    assets = payload.get("assets")
    ensure(isinstance(assets, Mapping), "asset records are missing")
    ensure(set(assets) == set(EXPECTED_ASSETS), "asset names differ")
    for name, expected in EXPECTED_ASSETS.items():
        record = assets.get(name)
        ensure(isinstance(record, Mapping), f"asset record is missing: {name}")
        ensure(record.get("asset_id") == expected["asset_id"], f"asset ID differs: {name}")
        ensure(record.get("size_bytes") == expected["size_bytes"], f"asset size differs: {name}")
        ensure(record.get("sha256") == expected["sha256"], f"asset hash differs: {name}")
        ensure(record.get("api_digest") == "sha256:" + expected["sha256"], f"API digest differs: {name}")

    contents = payload.get("release_contents")
    ensure(isinstance(contents, Mapping), "release contents are missing")
    expected_contents = {
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
    for key, value in expected_contents.items():
        ensure(contents.get(key) == value, f"release contents differ: {key}")

    cross_model = payload.get("cross_model_product")
    ensure(isinstance(cross_model, Mapping), "cross-model product is missing")
    expected_cross_model = {
        "model_family_count": 5,
        "reporting_scope_count": 19,
        "active_configuration_count": 72,
        "within_scope_pair_count": 114,
        "comparison_path_count": 76,
        "navigation_path_count": 2,
        "html_local_file_link_count": 57,
        "standalone_html": True,
        "javascript_used": False,
        "runtime_image_dependency": False,
        "unknown_state": "not_stated",
    }
    for key, value in expected_cross_model.items():
        ensure(cross_model.get(key) == value, f"cross-model audit differs: {key}")
    ensure(cross_model.get("unknown_seat_models") == ["bigster", "duster_iii"], "unknown-seat models differ")

    workspace = payload.get("offline_workspace")
    ensure(isinstance(workspace, Mapping), "workspace audit is missing")
    ensure(workspace.get("verification") == "PASS", "workspace verification differs")
    ensure(workspace.get("asset_count") == 3, "workspace asset count differs")
    ensure(workspace.get("content_file_count") == 85, "workspace content count differs")
    ensure(workspace.get("index_local_link_count") == 83, "workspace link count differs")
    ensure(
        workspace.get("index_sha256")
        == "ad2074a55e110ac11a518b441cbdc51864d5c7223cba75812c5b719facdf9b24",
        "workspace index hash differs",
    )

    boundaries = payload.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "semantic boundaries are missing")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
        "public_v1_7_0_rewritten",
    ):
        ensure(boundaries.get(key) is False, f"semantic boundary differs: {key}")
    verification = payload.get("verification")
    ensure(isinstance(verification, Mapping), "verification summary is missing")
    ensure(all(value == "PASS" for value in verification.values()), "verification summary contains failure")
    ensure(
        payload.get("next_package", {}).get("name")
        == "Cross-Model Navigation Usability Review",
        "next package differs",
    )


def verify_release_record() -> None:
    text = RELEASE_RECORD.read_text(encoding="utf-8")
    required = (
        "Data Products v1.8.0 Publication",
        "360115681",
        SOURCE_SHA,
        "62,141,187 bytes",
        EXPECTED_ASSETS["dacia-knowledge-base-data-products-v1.8.0.zip"]["sha256"],
        "85 deterministic archive members",
        "83 local links",
        "ad2074a55e110ac11a518b441cbdc51864d5c7223cba75812c5b719facdf9b24",
        "Cross-Model Navigation Usability Review",
    )
    for value in required:
        ensure(value in text, f"publication record omits: {value}")


def verify_deterministic_assets() -> None:
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release"
        manifest = create_release_assets(ROOT, output, "1.8.0", SOURCE_SHA)
        ensure(manifest.get("repository_commit") == SOURCE_SHA, "generated commit differs")
        ensure(manifest.get("selected_configuration_count") == 72, "generated configuration count differs")
        ensure(manifest.get("scope_group_count") == 19, "generated scope count differs")
        ensure(manifest.get("cross_scope_pairs_generated") is False, "generated cross-scope pairs")
        for name, expected in EXPECTED_ASSETS.items():
            path = output / name
            ensure(path.stat().st_size == expected["size_bytes"], f"generated size differs: {name}")
            ensure(sha256(path) == expected["sha256"], f"generated hash differs: {name}")
        archive_path = output / archive_name("1.8.0")
        with ZipFile(archive_path) as archive:
            names = archive.namelist()
            ensure(len(names) == 85, "generated archive count differs")
            view = json.loads(
                archive.read("cross-model/cross-model-comparison-view.json").decode("utf-8")
            )
            html = archive.read("cross-model/cross-model-comparison-view.html").decode("utf-8")
            bundle = json.loads(
                archive.read("comparison-bundle/comparison-bundle-manifest.json").decode("utf-8")
            )
        summary = view.get("summary", {})
        ensure(summary.get("model_family_count") == 5, "generated model count differs")
        ensure(summary.get("reporting_scope_count") == 19, "generated cross-model scope count differs")
        ensure(summary.get("within_scope_pair_count") == 114, "generated pair count differs")
        ensure("<script" not in html.lower(), "generated cross-model HTML contains JavaScript")
        groups = bundle.get("groups")
        ensure(isinstance(groups, list) and len(groups) == 19, "generated groups differ")
        ensure(sum(item.get("pair_count", 0) for item in groups) == 114, "generated bundle pairs differ")
        ensure(sum(item.get("total_differences", 0) for item in groups) == 1695, "generated differences differ")


def verify_state() -> None:
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
    ensure(baseline.get("tests", 0) >= 1022, "test baseline regressed")
    ensure(baseline.get("csv_files", 0) >= 46, "CSV baseline regressed")
    ensure(baseline.get("rows", 0) >= 9688, "master row baseline regressed")
    ensure(baseline.get("configuration_values", 0) >= 2949, "configuration values regressed")
    ensure(baseline.get("configuration_value_ranges", 0) >= 244, "configuration ranges regressed")
    ensure(baseline.get("availability_records", 0) >= 4754, "availability baseline regressed")
    ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")


def verify() -> None:
    preparation = load_json(PREPARATION)
    ensure(preparation.get("status") == "complete", "preparation record is missing")
    audit = load_json(AUDIT)
    verify_audit(audit)
    verify_release_record()
    verify_state()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the publication record.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, PublicationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Data Products v1.8.0 publication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
