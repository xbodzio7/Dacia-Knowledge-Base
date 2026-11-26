#!/usr/bin/env python3
"""Verify the recorded public Data Products v1.8.1 release and audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / ".github" / "data-products-v1.8.1-publication.json"
AUDIT = ROOT / "data" / "reporting" / "data_products_v1_8_1_publication_audit.json"
RELEASE_RECORD = ROOT / "project" / "releases" / "data-products-v1.8.1.md"
STATE = ROOT / "project" / "state.json"
SOURCE_COMMIT = "0b7009fd1950693e347638a6b96756aeefb43b8a"


class PublicationError(RuntimeError):
    """Raised when the recorded v1.8.1 publication contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise PublicationError(message)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ensure(isinstance(payload, dict), f"expected JSON object: {path}")
    return payload


def verify_assets(publication: Mapping[str, Any], audit: Mapping[str, Any]) -> None:
    expected = {
        "dacia-knowledge-base-data-products-v1.8.1.zip": (490767591, 62141954, "3bb8ba7c48195651bbe24cae042560273c5e4083467c01b203bb07dab7401bc5"),
        "data-product-release-manifest.json": (490767592, 20607, "f4ed40ed7e469876c80ee95c6b1ad18fcf6c86f215934ab5942373f2889a54fd"),
        "SHA256SUMS": (490767593, 213, "ca59fb187c8fbdcbacf7c62d0c65559a8f604defc5634b1d7fe257df7f7e668e"),
    }
    ensure(set(publication.get("assets", {})) == set(expected), "publication asset set differs")
    ensure(set(audit.get("assets", {})) == set(expected), "audit asset set differs")
    for name, (asset_id, size, digest) in expected.items():
        for source, label in ((publication, "publication"), (audit, "audit")):
            item = source["assets"][name]
            ensure(item.get("asset_id") == asset_id, f"{label} asset ID differs: {name}")
            ensure(item.get("size_bytes") == size, f"{label} asset size differs: {name}")
            ensure(item.get("sha256") == digest, f"{label} asset hash differs: {name}")
            ensure(item.get("api_digest") == "sha256:" + digest, f"{label} API digest differs: {name}")


def verify() -> None:
    publication = load_json(PUBLICATION)
    audit = load_json(AUDIT)
    ensure(publication.get("kind") == "data_products_v1_8_1_publication", "publication kind differs")
    ensure(publication.get("status") == "PASS", "publication did not pass")
    ensure(audit.get("kind") == "data_products_v1_8_1_public_audit", "audit kind differs")
    ensure(audit.get("status") == "PASS", "audit did not pass")
    for payload, label in ((publication, "publication"), (audit, "audit")):
        ensure(payload.get("release_id") == 360138130, f"{label} release ID differs")
        ensure(payload.get("release_tag") == "data-products-v1.8.1", f"{label} tag differs")
        ensure(payload.get("source_commit") == SOURCE_COMMIT, f"{label} source commit differs")
    ensure(publication.get("draft") is False, "release is draft")
    ensure(publication.get("prerelease") is False, "release is prerelease")
    ensure(publication.get("asset_count") == 3, "publication asset count differs")
    ensure(publication.get("public_redownload_verification") == "PASS", "public redownload failed")
    ensure(audit.get("publication_workflow_run") == 30224467755, "publication run differs")
    ensure(audit.get("audit_workflow_run") == 30225040623, "audit run differs")
    ensure(audit.get("verification") == "PASS", "audit verification differs")
    verify_assets(publication, audit)

    workspace = audit.get("workspace", {})
    ensure(workspace.get("asset_count") == 3, "workspace asset count differs")
    ensure(workspace.get("content_file_count") == 85, "workspace content count differs")
    ensure(workspace.get("index_local_link_count") == 83, "workspace link count differs")
    ensure(workspace.get("index_sha256") == "653a505102a15dc66d770b82612e18da324c0299162f644b7192628911c54b80", "workspace index hash differs")
    contents = audit.get("release_contents", {})
    ensure(contents.get("selected_configuration_count") == 72, "configuration count differs")
    ensure(contents.get("scope_group_count") == 19, "scope count differs")
    ensure(contents.get("within_scope_pair_count") == 114, "pair count differs")
    ensure(contents.get("archive_member_count") == 85, "archive member count differs")
    ensure(contents.get("equipment_facet_count") == 110, "equipment facet count differs")

    equipment = audit.get("equipment_filter", {})
    ensure(equipment.get("visible_choices") == 108, "visible equipment count differs")
    ensure(equipment.get("camera_matches") == 66, "camera match count differs")
    ensure(equipment.get("missing_and_unknown_are_exclusions") is True, "missing-data boundary differs")
    order = audit.get("model_order", [])
    ensure([item.get("model_code") for item in order] == ["sandero_iii", "sandero_stepway_iii", "jogger", "duster_iii", "bigster"], "model order differs")
    ensure([item.get("minimum_catalog_price_pln") for item in order] == [68000, 71700, 77900, 82000, 101400], "model prices differ")
    ensure(all(value is False for value in audit.get("semantic_boundaries", {}).values()), "semantic boundary differs")

    record = RELEASE_RECORD.read_text(encoding="utf-8")
    for marker in ("Release ID: `360138130`", SOURCE_COMMIT, "62,141,954 bytes", "30225040623", "Publication audit result: `PASS`"):
        ensure(marker in record, f"release record marker missing: {marker}")
    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "project phase is missing")
    current = state.get("current_package", {})
    ensure(isinstance(current.get("name"), str) and bool(current["name"]), "current package is missing")
    ensure(current.get("status") in {"planned", "active", "blocked", "complete"}, "current package status differs")
    next_package = state.get("next_package", {})
    ensure(isinstance(next_package.get("name"), str) and bool(next_package["name"]), "next package is missing")
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests", 0) >= 1054, "test baseline regressed")
    ensure(baseline.get("csv_files", 0) >= 46, "CSV baseline regressed")
    ensure(baseline.get("rows", 0) >= 9688, "row baseline regressed")
    ensure(baseline.get("availability_records", 0) >= 4754, "availability baseline regressed")
    ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the publication contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, PublicationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Data Products v1.8.1 publication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
