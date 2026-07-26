#!/usr/bin/env python3
"""Verify the deterministic Data Products v1.8.1 preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_8_1_preflight.json"
STATE = ROOT / "project" / "state.json"
PUBLIC_RECORD = ROOT / "project" / "releases" / "data-products-v1.8.1.md"
SOURCE_COMMIT = "0b7009fd1950693e347638a6b96756aeefb43b8a"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import archive_name  # noqa: E402


class PreflightError(RuntimeError):
    """Raised when the v1.8.1 preflight contract drifts."""


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
    ensure(payload.get("kind") == "data_products_v1_8_1_preflight", "preflight kind differs")
    ensure(payload.get("verified_on") == "2026-07-27", "preflight date differs")
    ensure(payload.get("status") == "PASS", "preflight did not pass")
    ensure(payload.get("source_commit") == SOURCE_COMMIT, "source commit differs")
    ensure(payload.get("release_version") == "1.8.1", "release version differs")
    ensure(payload.get("release_tag") == "data-products-v1.8.1", "release tag differs")
    ensure(payload.get("build_count") == 2, "build count differs")
    ensure(payload.get("byte_identical_rebuilds") is True, "rebuilds are not byte-identical")
    ensure(payload.get("archive_member_count") == 85, "archive member count differs")
    ensure(payload.get("duplicate_archive_members") == 0, "archive contains duplicate members")

    assets = payload.get("assets")
    ensure(isinstance(assets, Mapping), "asset identities are missing")
    expected_names = {
        "dacia-knowledge-base-data-products-v1.8.1.zip",
        "data-product-release-manifest.json",
        "SHA256SUMS",
    }
    ensure(set(assets) == expected_names, "asset set differs")
    for name, identity in assets.items():
        ensure(isinstance(identity, Mapping), f"asset identity is invalid: {name}")
        ensure(isinstance(identity.get("size_bytes"), int) and identity["size_bytes"] > 0, f"asset size is invalid: {name}")
        digest = identity.get("sha256")
        ensure(isinstance(digest, str) and len(digest) == 64, f"asset hash is invalid: {name}")

    chromium = payload.get("chromium_smoke")
    ensure(isinstance(chromium, Mapping), "Chromium smoke result is missing")
    ensure(chromium.get("visible_equipment_choices") == 108, "Chromium visible count differs")
    ensure(chromium.get("camera_search_visible_choices") == 1, "Chromium camera search differs")
    ensure(chromium.get("selection_count") == 1, "Chromium selection count differs")
    ensure(chromium.get("matched_configurations") == 66, "Chromium result count differs")
    ensure(chromium.get("javascript_errors") == 0, "Chromium JavaScript errors differ")

    controls = payload.get("publication_controls")
    ensure(isinstance(controls, Mapping), "publication controls are missing")
    ensure(controls.get("tag_absent") is True, "target tag already exists")
    ensure(controls.get("release_absent") is True, "target release already exists")
    ensure(controls.get("public_v1_8_0_control_download") == "PASS", "public control download failed")
    ensure(controls.get("publication_performed") is False, "preflight performed publication")
    ensure(payload.get("next_package", {}).get("name") == "Data Products v1.8.1 Publication", "next package differs")


def verify_rebuild(payload: Mapping[str, Any]) -> None:
    identities = payload["assets"]
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release"
        manifest = create_release_assets(ROOT, output, "1.8.1", SOURCE_COMMIT)
        ensure(manifest.get("release_version") == "1.8.1", "rebuilt version differs")
        ensure(manifest.get("release_tag") == "data-products-v1.8.1", "rebuilt tag differs")
        ensure(manifest.get("selected_configuration_count") == 72, "rebuilt configuration count differs")
        ensure(manifest.get("scope_group_count") == 19, "rebuilt scope count differs")
        ensure(manifest.get("cross_scope_pairs_generated") is False, "rebuilt package created cross-scope pairs")
        ensure(manifest.get("ranking_generated") is False, "rebuilt package created ranking")
        ensure(manifest.get("recommendations_generated") is False, "rebuilt package created recommendations")
        ensure(manifest.get("inferred_values_generated") is False, "rebuilt package created inferred values")
        for name, identity in identities.items():
            path = output / name
            ensure(path.is_file(), f"rebuilt asset is missing: {name}")
            ensure(path.stat().st_size == identity["size_bytes"], f"rebuilt asset size differs: {name}")
            ensure(sha256(path) == identity["sha256"], f"rebuilt asset hash differs: {name}")
        archive = output / archive_name("1.8.1")
        with ZipFile(archive) as package:
            names = package.namelist()
            ensure(len(names) == 85, "rebuilt archive member count differs")
            ensure(len(set(names)) == 85, "rebuilt archive contains duplicate members")
            html = package.read("shortlist/configuration-shortlist.html").decode("utf-8")
            notes = package.read("RELEASE_NOTES.md").decode("utf-8")
        ensure("Equipment filtering is restored" in notes, "release notes omit filter fix")
        ensure("Missing and unknown evidence remains excluded" in notes, "release notes omit evidence boundary")
        ensure("minimum current catalogue price" in notes, "release notes omit price ordering")
        ensure("v1.8.0 remains immutable" in notes, "release notes omit immutable baseline")
        marker = '<script id="configuration-catalog" type="application/json">'
        start = html.index(marker) + len(marker)
        end = html.index("</script>", start)
        catalog = json.loads(html[start:end])
        models = catalog.get("facets", {}).get("models", [])
        ensure([item.get("code") for item in models] == ["sandero_iii", "sandero_stepway_iii", "jogger", "duster_iii", "bigster"], "release model order differs")
        ensure([item.get("minimum_catalog_price_pln") for item in models] == [68000, 71700, 77900, 82000, 101400], "release model prices differ")


def verify_state() -> None:
    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "project phase is missing")
    ensure(state.get("current_package", {}).get("status") == "complete", "current package is not complete")
    baseline = state.get("baseline", {})
    ensure(isinstance(baseline.get("tests"), int) and baseline["tests"] >= 1046, "test baseline regressed")
    ensure(baseline.get("csv_files") == 46, "CSV baseline changed")
    ensure(baseline.get("rows") == 9688, "master row baseline changed")
    ensure(baseline.get("availability_records") == 4754, "availability baseline changed")
    ensure(baseline.get("attributes") == 385, "attribute baseline changed")


def verify() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
    verify_rebuild(payload)
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
    print("PASS: Data Products v1.8.1 preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
