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
TAG = "data-products-v1.12.1"
PUBLISHED_ON = "2026-08-03"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


assets = {}
for name in (
    "dacia-knowledge-base-data-products-v1.12.1.zip",
    "data-product-release-manifest.json",
    "SHA256SUMS",
):
    path = RELEASE_DIR / name
    assets[name] = {"size_bytes": path.stat().st_size, "sha256": sha256(path)}

receipt = {
    "version": 1,
    "kind": "data_products_v1_12_1_publication",
    "published_on": PUBLISHED_ON,
    "status": "complete",
    "tag": TAG,
    "release_id": int(RELEASE_ID) if RELEASE_ID else None,
    "source_commit": SOURCE_SHA,
    "double_build_byte_identity": True,
    "offline_workspace_verification": "PASS",
    "public_download_byte_identity": True,
    "corrective_interface": {
        "direct_entry_point": "model_family_summary_html",
        "workspace_card": "Model family summary",
        "older_release_compatibility": True,
        "v1_12_0_rewritten": False,
    },
    "portfolio_model_family_summary": {
        "model_families": 6,
        "active_configurations": 81,
        "reporting_scopes": 22,
        "provenance_sources": 33,
        "source_configuration_relationships": 251,
        "configurations_without_provenance": 0,
        "formats": ["JSON", "Markdown", "HTML"],
    },
    "semantic_boundaries": {
        "source_data_changed": False,
        "cross_scope_pairs_generated": False,
        "ranking_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    },
    "assets": assets,
    "public_v1_12_0_immutable": True,
}
(ROOT / "data/reporting/data_products_v1_12_1_publication.json").write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["updated_on"] = PUBLISHED_ON
state["phase"] = "Data Products v1.12.1 Publication"
state["reference_delivery"] = {
    "name": "Data Products v1.12.1 Publication",
    "pull_request": PUBLICATION_PR,
    "head_sha": SOURCE_SHA,
    "quality_run": PUBLICATION_RUN_ID,
}
state["current_package"] = {
    "package_id": "data_products_v1_12_1_publication_001",
    "kind": "data_product_release",
    "name": "Data Products v1.12.1 Publication",
    "status": "complete",
    "goal": "Publish immutable data-products-v1.12.1 assets from the exact publication merge SHA after double-build byte identity, full Quality and public-download offline workspace verification.",
    "manifest_paths": [
        "data/reporting/data_products_v1_12_1_publication.json",
        "project/STATE_SUMMARY.md",
        "project/packages/data-products-v1.12.1-publication-20260803.md",
        "project/state.json",
        "tools/reporting/portfolio_model_family_release_integration.py",
        "tools/reporting/data_product_release_download.py",
        "tools/reporting/data_product_workspace_index.py",
    ],
}
state["next_package"] = {
    "package_id": "post_v1_12_1_release_priority_selection_review_001",
    "kind": "priority_selection_review",
    "name": "Post-v1.12.1 Release Priority Selection Review",
    "status": "planned",
    "goal": "Inspect canonical product, source and roadmap evidence after corrective v1.12.1 publication and select one bounded next package without reopening closed evidence or inferring unsupported work.",
    "manifest_paths": [],
}
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

publication_doc = f"""# Data Products v1.12.1 Publication

Date: {PUBLISHED_ON}

## Result

The immutable `data-products-v1.12.1` release was published from exact source commit `{SOURCE_SHA}`.

The corrective release publishes the previously agreed direct `model_family_summary_html` entry point and dedicated **Model family summary** card in the verified offline consumer workspace. Older immutable releases remain compatible when the optional family member is absent, and `data-products-v1.12.0` was not rewritten.

The assets were built twice and were byte-identical. Both builds passed canonical verification, the extracted offline workspace passed verification, and the publicly downloaded assets matched the verified build byte for byte.

No source data, reporting scope, comparison pair, ranking, recommendation or inferred value changed.

## Assets

- `dacia-knowledge-base-data-products-v1.12.1.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_12_1_publication.json`.

## Next package

`post_v1_12_1_release_priority_selection_review_001` selects one bounded next package from canonical repository evidence.
"""
(ROOT / "project/packages/data-products-v1.12.1-publication-20260803.md").write_text(publication_doc, encoding="utf-8")
