#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = Path(os.environ["RELEASE_DIR"])
SOURCE_SHA = os.environ["SOURCE_SHA"]
RELEASE_ID = os.environ.get("RELEASE_ID", "")
PUBLICATION_PR = int(os.environ["PUBLICATION_PR"])
PUBLICATION_RUN_ID = int(os.environ["PUBLICATION_RUN_ID"])
TAG = "data-products-v1.11.0"
PUBLISHED_ON = "2026-08-02"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


assets = {}
for name in (
    "dacia-knowledge-base-data-products-v1.11.0.zip",
    "data-product-release-manifest.json",
    "SHA256SUMS",
):
    path = RELEASE_DIR / name
    assets[name] = {
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }

receipt = {
    "version": 1,
    "kind": "data_products_v1_11_0_publication",
    "published_on": PUBLISHED_ON,
    "status": "complete",
    "tag": TAG,
    "release_id": int(RELEASE_ID) if RELEASE_ID else None,
    "source_commit": SOURCE_SHA,
    "double_build_byte_identity": True,
    "offline_workspace_verification": "PASS",
    "source_backed_delta": {
        "spring_observations": 36,
        "spring_configurations": 3,
        "spring_attributes": 12,
        "value_id_range": [3569, 3604],
    },
    "preserved_deferrals": [
        "battery_mass_204_kg_my2025_stock_only",
        "battery_voltage_354_v_my2025_stock_only",
        "battery_capacity_24_3_kwh_measurement_basis_unqualified",
        "charging_times_context_dependent",
        "ground_clearance_15_inch_wheel_only",
        "range_and_maximum_speed_not_reimported",
    ],
    "assets": assets,
    "public_v1_10_0_immutable": True,
}
(ROOT / "data/reporting/data_products_v1_11_0_publication.json").write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["updated_on"] = PUBLISHED_ON
state["phase"] = "Data Products v1.11.0 Publication"
state["reference_delivery"] = {
    "name": "Data Products v1.11.0 Publication",
    "pull_request": PUBLICATION_PR,
    "head_sha": SOURCE_SHA,
    "quality_run": PUBLICATION_RUN_ID,
}
state["current_package"] = {
    "package_id": "data_products_v1_11_0_publication_001",
    "kind": "data_product_release",
    "name": "Data Products v1.11.0 Publication",
    "status": "complete",
    "goal": (
        "Publish the verified post-Spring-milestone data products from the "
        "exact publication merge commit without changing product semantics."
    ),
    "manifest_paths": [
        "data/reporting/data_products_v1_11_0_publication.json",
        "project/STATE_SUMMARY.md",
        "project/packages/data-products-v1.11.0-publication-20260802.md",
        "project/state.json",
        "tests/test_data_products_v1_11_0_release_contract.py",
        "tools/reporting/data_product_release.py",
    ],
}
state["next_package"] = {
    "package_id": "post_v1_11_0_release_priority_selection_review_001",
    "kind": "priority_selection_review",
    "name": "Post-v1.11.0 Release Priority Selection Review",
    "status": "planned",
    "goal": (
        "Inspect the canonical source registry, completeness reports and "
        "roadmap after the immutable v1.11.0 publication and select one "
        "bounded next package without reopening closed evidence or inferring "
        "a source candidate."
    ),
    "manifest_paths": [],
}
state_path.write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

publication_doc = f"""# Data Products v1.11.0 Publication

Date: {PUBLISHED_ON}

## Result

The immutable `data-products-v1.11.0` release was published from exact source commit `{SOURCE_SHA}`.

The release contains the fully verified repository state after closure of the Spring legacy-PDF assimilation milestone, including 36 common technical observations for three existing passenger Spring configurations. The observations cover permanent-magnet synchronous motor type, LFP traction-battery chemistry, electric steering and nine common body dimensions.

All six documented technical deferrals remain excluded. The assets were built twice and were byte-identical, the extracted offline workspace passed verification, and the downloaded public assets matched the verified build. Public `data-products-v1.10.0` remains immutable.

## Assets

- `dacia-knowledge-base-data-products-v1.11.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_11_0_publication.json`.

## Next package

`post_v1_11_0_release_priority_selection_review_001` will select one bounded next package from canonical repository evidence. If no source-backed or product candidate can be selected without a new scope decision, it will stop with `ACTION_REQUIRED`.
"""
(ROOT / "project/packages/data-products-v1.11.0-publication-20260802.md").write_text(
    publication_doc,
    encoding="utf-8",
)
