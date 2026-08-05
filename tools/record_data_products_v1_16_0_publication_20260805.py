#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("REPOSITORY_ROOT", Path.cwd())).resolve()
RELEASE_DIR = Path(os.environ["RELEASE_DIR"])
SOURCE_SHA = os.environ["SOURCE_SHA"]
RELEASE_ID = os.environ.get("RELEASE_ID", "")
PUBLICATION_PR = int(os.environ["PUBLICATION_PR"])
PUBLICATION_RUN_ID = int(os.environ["PUBLICATION_RUN_ID"])
TAG = "data-products-v1.16.0"
PUBLISHED_ON = "2026-08-05"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


assets = {}
for name in (
    "dacia-knowledge-base-data-products-v1.16.0.zip",
    "data-product-release-manifest.json",
    "SHA256SUMS",
):
    path = RELEASE_DIR / name
    assets[name] = {"size_bytes": path.stat().st_size, "sha256": sha256(path)}

receipt = {
    "version": 1,
    "kind": "data_products_v1_16_0_publication",
    "published_on": PUBLISHED_ON,
    "status": "complete",
    "tag": TAG,
    "release_id": int(RELEASE_ID) if RELEASE_ID else None,
    "source_commit": SOURCE_SHA,
    "double_build_byte_identity": True,
    "offline_workspace_verification": "PASS",
    "public_download_byte_identity": True,
    "consumer_interface": {
        "model_family_summary_entry_point": "model_family_summary_html",
        "model_family_comparison_entry_point": "model_family_comparison_matrix_html",
        "model_version_comparison_entry_point": "model_version_comparison_matrix_html",
        "source_coverage_entry_point": "source_coverage_matrix_html",
        "powertrain_transmission_entry_point": "powertrain_transmission_matrix_html",
        "powertrain_transmission_workspace_card": "Powertrain and transmission matrix",
        "older_release_compatibility": True,
    },
    "portfolio_powertrain_transmission_matrix": {
        "active_configurations": 81,
        "formats": ["JSON", "CSV", "HTML"],
        "exact_recorded_grouping": True,
    },
    "semantic_boundaries": {
        "source_data_changed": False,
        "master_data_changed": False,
        "grouping_semantics_changed": False,
        "ranking_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    },
    "assets": assets,
    "public_v1_15_0_immutable": True,
}
(ROOT / "data/reporting/data_products_v1_16_0_publication.json").write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["updated_on"] = PUBLISHED_ON
state["phase"] = "Data Products v1.16.0 Publication"
state["reference_delivery"] = {
    "name": "Data Products v1.16.0 Publication",
    "pull_request": PUBLICATION_PR,
    "head_sha": SOURCE_SHA,
    "quality_run": PUBLICATION_RUN_ID,
}
state["current_package"] = {
    "package_id": "data_products_v1_16_0_publication_001",
    "kind": "data_product_release",
    "name": "Data Products v1.16.0 Publication",
    "status": "complete",
    "goal": "Publish immutable v1.16.0 assets from the exact source SHA after double-build, offline-workspace and public-download verification.",
    "manifest_paths": [
        "data/reporting/data_products_v1_16_0_publication.json",
        "project/STATE_SUMMARY.md",
        "project/packages/data-products-v1.16.0-publication-20260805.md",
        "project/state.json",
        "tools/reporting/portfolio_powertrain_transmission_matrix_release_integration.py",
        "tools/reporting/data_product_release_download.py",
        "tools/reporting/data_product_workspace_index.py",
    ],
}
state["next_package"] = {
    "package_id": "post_v1_16_0_release_priority_selection_review_001",
    "kind": "priority_selection_review",
    "name": "Post-v1.16.0 Release Priority Selection Review",
    "status": "planned",
    "goal": "Inspect canonical product, source and roadmap evidence after v1.16.0 publication and select one bounded next package.",
    "manifest_paths": [],
}
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(ROOT / "project/packages/data-products-v1.16.0-publication-20260805.md").write_text(
    f"""# Data Products v1.16.0 Publication

Date: {PUBLISHED_ON}

## Result

The immutable `data-products-v1.16.0` release was published from exact source commit `{SOURCE_SHA}`.

The release adds the verified powertrain and transmission matrix in JSON, CSV and standalone HTML. The offline workspace exposes `powertrain_transmission_matrix_html` and the dedicated **Powertrain and transmission matrix** card alongside the four existing portfolio products.

Both independent builds were byte-identical, the complete offline workspace passed verification, and the publicly downloaded assets matched the verified build byte for byte. Public `data-products-v1.15.0` remains immutable.

## Assets

- `dacia-knowledge-base-data-products-v1.16.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_16_0_publication.json`.

## Next package

`post_v1_16_0_release_priority_selection_review_001` selects one bounded next package from canonical repository evidence.
""",
    encoding="utf-8",
)
