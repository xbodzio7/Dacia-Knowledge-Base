#!/usr/bin/env python3
"""Verify Data Products v1.8.1 release preparation without publishing it."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reporting" / "data_products_v1_8_1_release_preparation.json"
REGRESSION = ROOT / "data" / "reporting" / "equipment_filter_regression_model_price_order.json"
PUBLIC_RELEASE = ROOT / "project" / "releases" / "data-products-v1.8.0.md"
TARGET_RELEASE = ROOT / "project" / "releases" / "data-products-v1.8.1.md"
STATE = ROOT / "project" / "state.json"

sys.path.insert(0, str(ROOT / "tools"))

from reporting.data_product_release import create_release_assets  # noqa: E402
from reporting.data_product_release_model import archive_name  # noqa: E402


class PreparationError(RuntimeError):
    """Raised when the v1.8.1 release-preparation contract drifts."""


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
        payload.get("kind") == "data_products_v1_8_1_release_preparation",
        "preparation kind differs",
    )
    ensure(payload.get("prepared_on") == "2026-07-27", "preparation date differs")
    ensure(payload.get("status") == "complete", "preparation is not complete")
    ensure(
        payload.get("selected_by") == "equipment_filter_regression_model_price_order.json",
        "selection source differs",
    )

    target = payload.get("target")
    ensure(isinstance(target, Mapping), "target is missing")
    ensure(target.get("version") == "1.8.1", "target version differs")
    ensure(target.get("tag") == "data-products-v1.8.1", "target tag differs")
    ensure(
        target.get("archive_name") == "dacia-knowledge-base-data-products-v1.8.1.zip",
        "target archive differs",
    )
    ensure(target.get("manifest_name") == "data-product-release-manifest.json", "manifest name differs")
    ensure(target.get("checksums_name") == "SHA256SUMS", "checksums name differs")

    public = payload.get("public_baseline")
    ensure(isinstance(public, Mapping), "public baseline is missing")
    ensure(public.get("version") == "1.8.0", "public version differs")
    ensure(public.get("release_id") == 360115681, "public release ID differs")
    ensure(
        public.get("source_commit") == "becd218228e3f4f0cdd312b0ed836ade487422b1",
        "public source commit differs",
    )
    ensure(public.get("archive_members") == 85, "public archive count differs")
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
        "member_set_change_since_public_baseline": False,
    }
    for key, value in expected.items():
        ensure(candidate.get(key) == value, f"candidate baseline differs: {key}")
    boundaries = candidate.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "candidate boundaries are missing")
    ensure(all(value is False for value in boundaries.values()), "candidate semantic boundary differs")

    patch = payload.get("patch_contract")
    ensure(isinstance(patch, Mapping), "patch contract is missing")
    ensure(patch.get("visible_equipment_choices") == 108, "visible equipment count differs")
    ensure(patch.get("rear_view_camera_matches") == 66, "camera match count differs")
    ensure(patch.get("missing_and_unknown_are_exclusions") is True, "unknown handling differs")
    order = patch.get("model_order")
    ensure(isinstance(order, list) and len(order) == 5, "model order is missing")
    ensure(
        [item.get("model_code") for item in order]
        == ["sandero_iii", "sandero_stepway_iii", "jogger", "duster_iii", "bigster"],
        "model code order differs",
    )
    ensure(
        [item.get("minimum_catalog_price_pln") for item in order]
        == [68000, 71700, 77900, 82000, 101400],
        "model minimum prices differ",
    )

    ensure(
        payload.get("publication_lifecycle")
        == ["preflight", "publish", "independent_public_audit", "record_publication"],
        "publication lifecycle differs",
    )
    preflight = payload.get("preflight_contract")
    ensure(isinstance(preflight, Mapping), "preflight contract is missing")
    ensure(preflight.get("source") == "exact squash-merged preparation commit", "preflight source differs")
    ensure(preflight.get("build_count") == 2, "preflight build count differs")
    ensure(
        "real_chromium_filtering_smoke" in preflight.get("required_checks", []),
        "Chromium preflight check is missing",
    )

    publication = payload.get("publication_state")
    ensure(isinstance(publication, Mapping), "publication state is missing")
    ensure(publication.get("publication_performed") is False, "publication already performed")
    ensure(publication.get("tag_created") is False, "tag already recorded")
    ensure(publication.get("release_created") is False, "release already recorded")
    ensure(publication.get("final_source_commit") is None, "final commit was guessed")
    ensure(publication.get("final_asset_identity") is None, "final asset identity was guessed")
    ensure(
        payload.get("next_package", {}).get("name") == "Data Products v1.8.1 Preflight",
        "next package differs",
    )


def node_contract(catalog: Mapping[str, Any]) -> dict[str, Any]:
    script = ROOT / "tools" / "reporting" / "configuration_shortlist_browser.js"
    program = r"""
const fs = require("fs");
const api = require(process.argv[1]);
const catalog = JSON.parse(fs.readFileSync(0, "utf8"));
const initial = api.reconcileEquipmentSelection(catalog, {
  models: [], versions: [], transmissions: [], powertrains: [],
  required_equipment: [], required_standard_equipment: []
});
const camera = api.filterCatalog(catalog, {
  required_equipment: ["rear_view_camera"],
  required_standard_equipment: []
});
const missing = {
  configuration_code: "missing", model_code: "m", version_code: "v",
  transmission_type: "manual", powertrain_label: "p",
  catalog_price: {state: "missing"}, number_of_seats: {state: "missing"},
  equipment: {}
};
process.stdout.write(JSON.stringify({
  visible: initial.available_equipment.length,
  camera_matches: camera.results.length,
  missing_reasons: api.evaluate(missing, {
    required_equipment: ["rear_view_camera"], required_standard_equipment: []
  })
}));
"""
    completed = subprocess.run(
        ["node", "-e", program, str(script)],
        input=json.dumps(catalog, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        cwd=ROOT,
    )
    ensure(completed.returncode == 0, completed.stderr or completed.stdout)
    result = json.loads(completed.stdout)
    ensure(isinstance(result, dict), "Node contract returned invalid JSON")
    return result


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
    regression = load_json(REGRESSION)
    ensure(regression.get("status") == "complete", "regression package is not complete")
    ensure(PUBLIC_RELEASE.is_file(), "v1.8.0 publication record is missing")
    ensure(not TARGET_RELEASE.exists(), "v1.8.1 publication record already exists")
    public_text = PUBLIC_RELEASE.read_text(encoding="utf-8")
    ensure("Release ID: `360115681`" in public_text, "v1.8.0 release ID differs")
    ensure("85 deterministic archive members" in public_text, "v1.8.0 archive count differs")
    ensure("becd218228e3f4f0cdd312b0ed836ade487422b1" in public_text, "v1.8.0 source differs")

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "release"
        manifest = create_release_assets(ROOT, output, "1.8.1", "5" * 40)
        archive_path = output / archive_name("1.8.1")
        ensure(manifest.get("release_version") == "1.8.1", "candidate version differs")
        ensure(manifest.get("release_tag") == "data-products-v1.8.1", "candidate tag differs")
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
            rendered = archive.read("shortlist/configuration-shortlist.html").decode("utf-8")
            notes = archive.read("RELEASE_NOTES.md").decode("utf-8")

    catalog = embedded_catalog(rendered)
    configurations = catalog.get("configurations")
    facets = catalog.get("facets")
    ensure(isinstance(configurations, list) and len(configurations) == 72, "embedded configuration count differs")
    ensure(isinstance(facets, Mapping), "embedded facets are missing")
    equipment = facets.get("equipment")
    models = facets.get("models")
    ensure(isinstance(equipment, list) and len(equipment) == 110, "embedded equipment count differs")
    ensure(isinstance(models, list) and len(models) == 5, "embedded model count differs")
    ensure(
        [item.get("code") for item in models]
        == ["sandero_iii", "sandero_stepway_iii", "jogger", "duster_iii", "bigster"],
        "embedded model order differs",
    )
    ensure(
        [item.get("minimum_catalog_price_pln") for item in models]
        == [68000, 71700, 77900, 82000, 101400],
        "embedded model minimum prices differ",
    )

    contract = node_contract(catalog)
    ensure(contract.get("visible") == 108, "release equipment visibility differs")
    ensure(contract.get("camera_matches") == 66, "release camera result count differs")
    ensure(
        "equipment_missing:rear_view_camera" in contract.get("missing_reasons", []),
        "release treated missing camera evidence as available",
    )
    ensure("Equipment filtering is restored" in notes, "release notes omit equipment-filter fix")
    ensure("Missing and unknown evidence remains excluded" in notes, "release notes omit missing-data boundary")
    ensure("minimum current catalogue price" in notes, "release notes omit model ordering")
    ensure("v1.8.0 remains immutable" in notes, "release notes omit immutability boundary")

    state = load_json(STATE)
    ensure(isinstance(state.get("phase"), str) and bool(state["phase"]), "project phase is missing")
    current = state.get("current_package")
    ensure(isinstance(current, Mapping), "current package is missing")
    ensure(
        isinstance(current.get("name"), str) and bool(current["name"]),
        "current package name is missing",
    )
    ensure(
        current.get("status") in {"planned", "active", "blocked", "complete"},
        "current package status differs",
    )
    next_package = state.get("next_package")
    ensure(isinstance(next_package, Mapping), "next package is missing")
    ensure(
        isinstance(next_package.get("name"), str) and bool(next_package["name"]),
        "next package name is missing",
    )
    baseline = state.get("baseline", {})
    ensure(baseline.get("tests", 0) >= 1038, "test baseline regressed")
    ensure(baseline.get("csv_files", 0) >= 46, "CSV baseline regressed")
    ensure(baseline.get("rows", 0) >= 9688, "master row baseline regressed")
    ensure(baseline.get("configuration_values", 0) >= 2949, "configuration values regressed")
    ensure(baseline.get("configuration_value_ranges", 0) >= 244, "configuration ranges regressed")
    ensure(baseline.get("availability_records", 0) >= 4754, "availability baseline regressed")
    ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")


def verify() -> None:
    payload = load_json(REPORT)
    verify_report(payload)
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
    print("PASS: Data Products v1.8.1 release preparation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
