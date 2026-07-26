#!/usr/bin/env python3
"""Verify the Data Products v1.7.0 release-preparation contract."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
REPORT = REPORTING / "data_products_v1_7_0_release_preparation.json"
SELECTION = REPORTING / "post_brochure_priority_selection_review.json"
STATE = ROOT / "project" / "state.json"
PREVIOUS_RELEASE = ROOT / "project" / "releases" / "data-products-v1.6.1.md"
TARGET_RELEASE = ROOT / "project" / "releases" / "data-products-v1.7.0.md"
TARGET_AUDIT = (
    ROOT
    / "project"
    / "releases"
    / "data-products-v1.7.0-publication-audit.json"
)

sys.path.insert(0, str(ROOT / "tools"))

from reporting.configuration_comparison_bundle import discover_scopes  # noqa: E402

EXPECTED_ASSETS = [
    "dacia-knowledge-base-data-products-v1.7.0.zip",
    "data-product-release-manifest.json",
    "SHA256SUMS",
]
EXPECTED_FORMATS = {"JSON", "Markdown", "CSV", "HTML", "XLSX"}
EXPECTED_BOUNDARIES = {
    "cross_scope_pairs_generated": False,
    "ranking_generated": False,
    "recommendations_generated": False,
    "inferred_values_generated": False,
    "master_data_changed": False,
    "existing_evidence_states_preserved": True,
}
EXPECTED_STAGES = [
    "merge_preparation",
    "preflight",
    "publish",
    "audit",
    "record_publication",
]
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class ReviewError(RuntimeError):
    """Raised when the release-preparation contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "unsupported preparation version")
    ensure(
        payload.get("kind") == "data_products_v1_7_0_release_preparation",
        "unexpected preparation kind",
    )
    ensure(payload.get("prepared_on") == "2026-07-26", "unexpected preparation date")
    ensure(payload.get("status") == "complete", "preparation is not complete")
    ensure(
        payload.get("source_selection_review")
        == "post_brochure_priority_selection_review.json",
        "source selection review differs",
    )

    identity = payload.get("release_identity")
    ensure(isinstance(identity, dict), "release identity is missing")
    ensure(identity.get("release_version") == "1.7.0", "release version differs")
    ensure(identity.get("release_tag") == "data-products-v1.7.0", "release tag differs")
    ensure(identity.get("publication_status") == "not_published", "publication status differs")
    ensure(
        identity.get("publication_mode") == "manual_preflight_publish_audit",
        "publication mode differs",
    )
    ensure(
        identity.get("final_source_commit") == "assigned_after_squash_merge",
        "final source commit must remain deferred to merge",
    )
    ensure(
        identity.get("final_asset_identity") == "assigned_by_post_merge_preflight",
        "final asset identity must remain deferred to preflight",
    )

    baseline = payload.get("candidate_baseline")
    ensure(isinstance(baseline, dict), "candidate baseline is missing")
    ensure(baseline.get("snapshot_date") == "2026-07-24", "snapshot date differs")
    ensure(baseline.get("selected_configuration_count") == 72, "configuration count differs")
    ensure(baseline.get("scope_group_count") == 19, "scope count differs")
    ensure(baseline.get("comparable_scope_count") == 19, "comparable scope count differs")
    ensure(baseline.get("singleton_scope_count") == 0, "singleton scope count differs")
    ensure(baseline.get("pair_count") == 114, "pair count differs")
    ensure(baseline.get("difference_count") == 1695, "difference count differs")
    ensure(baseline.get("archive_member_count") == 83, "archive member count differs")
    ensure(set(baseline.get("formats", [])) == EXPECTED_FORMATS, "release formats differ")

    verification = payload.get("preparation_verification")
    ensure(isinstance(verification, dict), "preparation verification is missing")
    for key in (
        "deterministic_double_build",
        "release_asset_verification",
        "candidate_offline_workspace_verification",
        "previous_public_release_download_verification",
    ):
        ensure(verification.get(key) == "pass", f"verification did not pass: {key}")
    ensure(
        verification.get("previous_public_release") == "data-products-v1.6.1",
        "previous public release differs",
    )
    ensure(
        verification.get("previous_public_release_commit")
        == "4b77571c788b862a6543161b9343a35f464bd7c6",
        "previous release commit differs",
    )
    ensure(verification.get("publication_performed") is False, "preparation published a release")

    receipt = payload.get("diagnostic_candidate_receipt")
    ensure(isinstance(receipt, dict), "diagnostic receipt is missing")
    ensure(
        receipt.get("identity_status") == "diagnostic_only_not_publication_identity",
        "diagnostic receipt is presented as final",
    )
    ensure(isinstance(receipt.get("workflow_run"), int), "workflow run is missing")
    source_commit = str(receipt.get("source_commit", ""))
    ensure(SHA40.fullmatch(source_commit) is not None, "diagnostic source commit is invalid")
    assets = receipt.get("assets")
    ensure(isinstance(assets, dict), "diagnostic assets are missing")
    ensure(set(assets) == set(EXPECTED_ASSETS), "diagnostic asset inventory differs")
    for name, raw_record in assets.items():
        ensure(isinstance(raw_record, dict), f"diagnostic asset record is invalid: {name}")
        size = raw_record.get("size_bytes")
        ensure(isinstance(size, int) and not isinstance(size, bool) and size > 0, f"asset size is invalid: {name}")
        ensure(SHA256.fullmatch(str(raw_record.get("sha256", ""))) is not None, f"asset hash is invalid: {name}")
    ensure(
        SHA256.fullmatch(str(receipt.get("workspace_index_sha256", ""))) is not None,
        "workspace index hash is invalid",
    )
    ensure("not final" in str(receipt.get("reason_not_final", "")).lower(), "diagnostic receipt does not explain final identity deferral")

    ensure(payload.get("semantic_boundaries") == EXPECTED_BOUNDARIES, "semantic boundaries differ")
    ensure(payload.get("required_publication_assets") == EXPECTED_ASSETS, "required asset order differs")

    sequence = payload.get("publication_sequence")
    ensure(isinstance(sequence, list) and len(sequence) == 5, "publication sequence differs")
    ensure([item.get("order") for item in sequence] == [1, 2, 3, 4, 5], "publication order differs")
    ensure([item.get("stage") for item in sequence] == EXPECTED_STAGES, "publication stages differ")
    ensure(all(str(item.get("requirement", "")).strip() for item in sequence), "publication requirement is empty")

    next_package = payload.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(next_package.get("name") == "Data Products v1.7.0 Preflight", "next package differs")


def verify_repository(payload: Mapping[str, Any]) -> None:
    selection = load_json(SELECTION)
    contract = selection.get("release_preparation_contract")
    ensure(isinstance(contract, dict), "selection release contract is missing")
    ensure(contract.get("target_version") == "1.7.0", "selected release version differs")
    ensure(contract.get("target_tag") == "data-products-v1.7.0", "selected release tag differs")

    active = [row for row in rows(MASTER / "configurations.csv") if row.get("status") == "active"]
    ensure(len(active) == 72, "active configuration count differs")
    active_codes = {row["code"] for row in active}

    scopes = discover_scopes(ROOT)
    ensure(len(scopes) == 19, "repository comparison scope count differs")
    scoped_codes = [code for scope in scopes for code in scope.configuration_codes]
    ensure(len(scoped_codes) == 72, "scope configuration count differs")
    ensure(len(scoped_codes) == len(set(scoped_codes)), "configuration appears in multiple scopes")
    ensure(set(scoped_codes) == active_codes, "scope union differs from active configurations")
    ensure(
        sum(len(scope.configuration_codes) * (len(scope.configuration_codes) - 1) // 2 for scope in scopes)
        == 114,
        "scope pair formula differs",
    )

    required_tools = (
        ROOT / "tools" / "reporting" / "data_product_release.py",
        ROOT / "tools" / "reporting" / "data_product_release_download.py",
        ROOT / "tools" / "reporting" / "data_product_workspace_verify.py",
        ROOT / "tools" / "reporting" / "data_product_workspace_index.py",
        ROOT / "tools" / "reporting" / "configuration_comparison_bundle.py",
    )
    ensure(all(path.is_file() for path in required_tools), "release tooling is incomplete")
    ensure(PREVIOUS_RELEASE.is_file(), "previous public release record is missing")

    publication_recorded = TARGET_RELEASE.is_file() or TARGET_AUDIT.is_file()
    ensure(
        TARGET_RELEASE.is_file() == TARGET_AUDIT.is_file(),
        "v1.7.0 publication records are incomplete",
    )
    if publication_recorded:
        audit = load_json(TARGET_AUDIT)
        ensure(audit.get("release_id") == 360090447, "v1.7.0 release ID differs")
        ensure(audit.get("tag") == "data-products-v1.7.0", "v1.7.0 release tag differs")
        ensure(
            audit.get("target_commit_sha")
            == "99e0e19b86cad6eae619f37702464e6a5a761cd8",
            "v1.7.0 target commit differs",
        )
        ensure(audit.get("verification") == "PASS", "v1.7.0 audit did not pass")

    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and state["phase"], "project phase is missing")
    current = state.get("current_package")
    ensure(isinstance(current, dict), "current package is missing")
    ensure(isinstance(current.get("name"), str) and current["name"], "current package name is missing")
    ensure(current.get("status") in {"planned", "active", "blocked", "complete"}, "current package status differs")
    next_package = state.get("next_package")
    ensure(isinstance(next_package, dict), "next package is missing")
    ensure(isinstance(next_package.get("name"), str) and next_package["name"], "next package name is missing")
    ensure(state.get("baseline", {}).get("rows") == 9688, "master row baseline changed")
    ensure(state.get("baseline", {}).get("configuration_values") == 2949, "configuration values changed")
    ensure(state.get("baseline", {}).get("configuration_value_ranges") == 244, "configuration ranges changed")
    ensure(state.get("baseline", {}).get("attributes") == 385, "attribute baseline changed")

    baseline = payload.get("candidate_baseline")
    ensure(isinstance(baseline, dict), "candidate baseline is missing")
    ensure(baseline.get("selected_configuration_count") == len(active), "report configuration count differs from repository")
    ensure(baseline.get("scope_group_count") == len(scopes), "report scope count differs from repository")


def verify() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_repository(payload)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the preparation contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, ReviewError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Data Products v1.7.0 release preparation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
