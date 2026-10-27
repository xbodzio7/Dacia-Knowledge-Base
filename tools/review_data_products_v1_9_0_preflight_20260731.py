#!/usr/bin/env python3
"""Verify the deterministic Data Products v1.9.0 preflight."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_9_0_preflight.json"
STATE = ROOT / "project" / "state.json"
PUBLIC_RECORD = ROOT / "project" / "releases" / "data-products-v1.8.1.md"
SOURCE_COMMIT = "6c8f6f68c21022fa3bd6b6248d06b87d5d484d5c"
VERSION = "1.9.0"
ARCHIVE_NAME = "dacia-knowledge-base-data-products-v1.9.0.zip"
MANIFEST_NAME = "data-product-release-manifest.json"
CHECKSUMS_NAME = "SHA256SUMS"
NEW_SCOPE = "sandero_tce100_stepway_tce110_manual"
NEW_CONFIGURATIONS = {
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_stepway_iii_essential_tce110_manual",
    "sandero_stepway_iii_expression_tce110_manual",
    "sandero_stepway_iii_extreme_tce110_manual",
}
EXPECTED_ASSETS = {
    ARCHIVE_NAME: {
        "size_bytes": 82612470,
        "sha256": "4e114f171a80445369f2439466d0d102e894145614d9a221a0390452309f453d",
    },
    MANIFEST_NAME: {
        "size_bytes": 21600,
        "sha256": "519f371be16251533befdeb8147caba30bdf2f3bd2c0122f474c03924574c7ad",
    },
    CHECKSUMS_NAME: {
        "size_bytes": 213,
        "sha256": "48c9b648d6a2e848f6e35118c9530024637f06e50ff71cea861acd1a0c7bd9cb",
    },
}

sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release import create_release_assets  # noqa: E402


class PreflightError(RuntimeError):
    """Raised when the v1.9.0 preflight contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_report(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "preflight version differs")
    ensure(
        payload.get("kind") == "data_products_v1_9_0_preflight",
        "preflight kind differs",
    )
    ensure(payload.get("verified_on") == "2026-07-31", "preflight date differs")
    ensure(payload.get("status") == "PASS", "preflight did not pass")
    ensure(payload.get("source_commit") == SOURCE_COMMIT, "source commit differs")
    ensure(payload.get("release_version") == VERSION, "release version differs")
    ensure(
        payload.get("release_tag") == "data-products-v1.9.0",
        "release tag differs",
    )
    ensure(payload.get("build_count") == 2, "build count differs")
    ensure(
        payload.get("byte_identical_rebuilds") is True,
        "rebuilds are not byte-identical",
    )
    ensure(payload.get("archive_member_count") == 89, "archive member count differs")
    ensure(
        payload.get("duplicate_archive_members") == 0,
        "archive contains duplicate members",
    )

    assets = payload.get("assets")
    ensure(isinstance(assets, Mapping), "asset identities are missing")
    ensure(set(assets) == set(EXPECTED_ASSETS), "asset set differs")
    for name, expected in EXPECTED_ASSETS.items():
        identity = assets.get(name)
        ensure(isinstance(identity, Mapping), f"asset identity is invalid: {name}")
        ensure(
            identity.get("size_bytes") == expected["size_bytes"],
            f"asset size differs: {name}",
        )
        ensure(
            identity.get("sha256") == expected["sha256"],
            f"asset hash differs: {name}",
        )

    candidate = payload.get("candidate_contract")
    ensure(isinstance(candidate, Mapping), "candidate contract is missing")
    expected_candidate = {
        "active_configuration_count": 78,
        "scope_group_count": 20,
        "comparable_scope_count": 20,
        "singleton_scope_count": 0,
        "within_scope_pair_count": 129,
        "recorded_difference_count": 2180,
        "technical_comparison_facet_count": 127,
        "equipment_facet_count": 110,
        "new_reporting_scope": NEW_SCOPE,
        "new_scope_pair_count": 15,
        "new_scope_difference_count": 467,
    }
    for key, value in expected_candidate.items():
        ensure(candidate.get(key) == value, f"candidate contract differs: {key}")
    ensure(
        set(candidate.get("new_configuration_codes", [])) == NEW_CONFIGURATIONS,
        "new configuration set differs",
    )

    checks = payload.get("verification_checks")
    ensure(isinstance(checks, Mapping), "verification checks are missing")
    ensure(
        set(checks.values()) == {"PASS"},
        "one or more verification checks did not pass",
    )

    controls = payload.get("publication_controls")
    ensure(isinstance(controls, Mapping), "publication controls are missing")
    ensure(controls.get("tag_absent") is True, "target tag already exists")
    ensure(controls.get("release_absent") is True, "target release already exists")
    ensure(
        controls.get("publication_performed") is False,
        "preflight performed publication",
    )

    boundaries = payload.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "semantic boundaries are missing")
    for key in (
        "new_source_backed_configurations",
        "new_reporting_scope",
        "new_within_scope_pairs",
    ):
        ensure(boundaries.get(key) is True, f"expected release expansion differs: {key}")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
        "older_public_releases_rewritten",
    ):
        ensure(boundaries.get(key) is False, f"forbidden semantic output differs: {key}")

    baseline = payload.get("repository_baseline")
    ensure(isinstance(baseline, Mapping), "repository baseline is missing")
    expected_baseline = {
        "tests": 1676,
        "csv_files": 46,
        "rows": 11380,
        "configuration_values": 3498,
        "configuration_import_specs": 138,
        "configuration_value_ranges": 298,
        "configuration_range_import_specs": 24,
        "availability_records": 5770,
        "attributes": 385,
        "attribute_categories": 30,
    }
    for key, value in expected_baseline.items():
        ensure(baseline.get(key) == value, f"repository baseline differs: {key}")
    ensure(
        payload.get("next_package", {}).get("name")
        == "Data Products v1.9.0 Publication",
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


def verify_build(output: Path) -> None:
    manifest = load_json(output / MANIFEST_NAME)
    ensure(manifest.get("release_version") == VERSION, "rebuilt version differs")
    ensure(
        manifest.get("release_tag") == "data-products-v1.9.0",
        "rebuilt tag differs",
    )
    ensure(
        manifest.get("repository_commit") == SOURCE_COMMIT,
        "rebuilt source commit differs",
    )
    ensure(
        manifest.get("selected_configuration_count") == 78,
        "rebuilt configuration count differs",
    )
    ensure(manifest.get("scope_group_count") == 20, "rebuilt scope count differs")
    ensure(
        manifest.get("comparable_scope_count") == 20,
        "rebuilt comparable scope count differs",
    )
    ensure(manifest.get("singleton_scope_count") == 0, "rebuilt singleton count differs")
    for key in (
        "cross_scope_pairs_generated",
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        ensure(manifest.get(key) is False, f"rebuilt semantic boundary differs: {key}")

    for name, expected in EXPECTED_ASSETS.items():
        path = output / name
        ensure(path.is_file(), f"rebuilt asset is missing: {name}")
        ensure(
            path.stat().st_size == expected["size_bytes"],
            f"rebuilt asset size differs: {name}",
        )
        ensure(sha256(path) == expected["sha256"], f"rebuilt asset hash differs: {name}")

    with ZipFile(output / ARCHIVE_NAME) as package:
        names = package.namelist()
        ensure(names == sorted(names), "archive member order differs")
        ensure(len(names) == 89, "rebuilt archive member count differs")
        ensure(len(set(names)) == 89, "rebuilt archive contains duplicate members")
        shortlist = json.loads(
            package.read("shortlist/configuration-shortlist.json")
        )
        bundle = json.loads(
            package.read("comparison-bundle/comparison-bundle-manifest.json")
        )
        html = package.read("shortlist/configuration-shortlist.html").decode("utf-8")
        notes = package.read("RELEASE_NOTES.md").decode("utf-8")

    results = shortlist.get("results", [])
    ensure(len(results) == 78, "release shortlist count differs")
    codes = {item.get("configuration_code") for item in results}
    ensure(NEW_CONFIGURATIONS <= codes, "new configurations are missing from shortlist")

    groups = bundle.get("groups", [])
    ensure(len(groups) == 20, "release group count differs")
    ensure(
        sum(int(group.get("pair_count", 0)) for group in groups) == 129,
        "release pair count differs",
    )
    ensure(
        sum(int(group.get("total_differences", 0)) for group in groups) == 2180,
        "release difference count differs",
    )
    matching = [group for group in groups if group.get("scope") == NEW_SCOPE]
    ensure(len(matching) == 1, "new reporting scope is missing or duplicated")
    ensure(
        set(matching[0].get("configuration_codes", [])) == NEW_CONFIGURATIONS,
        "new reporting scope membership differs",
    )
    ensure(matching[0].get("pair_count") == 15, "new scope pair count differs")
    ensure(
        matching[0].get("total_differences") == 467,
        "new scope difference count differs",
    )

    catalog = embedded_catalog(html)
    facets = catalog.get("facets", {})
    ensure(
        len(facets.get("comparison_values", [])) == 127,
        "technical comparison facet count differs",
    )
    ensure(len(facets.get("equipment", [])) == 110, "equipment facet count differs")

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


def verify_rebuilds() -> None:
    # Historical v1.9.0 assets can be rebuilt only from their
    # original 78-configuration source catalogue. Later
    # source-backed catalogue expansion retains report, hash
    # and public-release verification without rebuilding the
    # old release from newer master data.
    configurations_path = ROOT / "data" / "master" / "configurations.csv"
    with configurations_path.open(encoding="utf-8", newline="") as handle:
        active_count = sum(
            row.get("status") == "active"
            for row in csv.DictReader(handle)
        )
    if active_count != 78:
        return
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = root / "first"
        second = root / "second"
        create_release_assets(ROOT, first, VERSION, SOURCE_COMMIT)
        create_release_assets(ROOT, second, VERSION, SOURCE_COMMIT)
        for name in EXPECTED_ASSETS:
            ensure(
                (first / name).read_bytes() == (second / name).read_bytes(),
                f"rebuilds are not byte-identical: {name}",
            )
        verify_build(first)
        verify_build(second)


def verify_public_control() -> None:
    ensure(PUBLIC_RECORD.is_file(), "public v1.8.1 record is missing")
    text = PUBLIC_RECORD.read_text(encoding="utf-8")
    ensure("Data Products v1.8.1 Publication" in text, "public v1.8.1 record differs")
    ensure("Release ID: `360138130`" in text, "public v1.8.1 release ID differs")
    ensure(
        "0b7009fd1950693e347638a6b96756aeefb43b8a" in text,
        "public v1.8.1 source differs",
    )
    ensure(
        "3bb8ba7c48195651bbe24cae042560273c5e4083467c01b203bb07dab7401bc5"
        in text,
        "public v1.8.1 archive identity differs",
    )


def verify_state() -> None:
    state = load_json(STATE)
    ensure(
        state.get("phase") == "Data Products v1.9.0 Preflight",
        "project phase differs",
    )
    ensure(
        state.get("current_package", {}).get("name")
        == "Data Products v1.9.0 Preflight",
        "current package differs",
    )
    ensure(
        state.get("current_package", {}).get("status") == "complete",
        "current package is not complete",
    )
    ensure(
        state.get("next_package", {}).get("name")
        == "Data Products v1.9.0 Publication",
        "next state package differs",
    )
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests") == 1676, "state test baseline differs")
    ensure(baseline.get("rows") == 11380, "state row baseline differs")
    ensure(
        baseline.get("configuration_values") == 3498,
        "state value baseline differs",
    )
    ensure(
        baseline.get("configuration_value_ranges") == 298,
        "state range baseline differs",
    )
    ensure(
        baseline.get("availability_records") == 5770,
        "state availability baseline differs",
    )


def verify() -> None:
    verify_report(load_json(REPORT))
    verify_rebuilds()
    verify_public_control()
    verify_state()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the preflight contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, PreflightError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Data Products v1.9.0 preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
