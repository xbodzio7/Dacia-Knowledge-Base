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
TAG = "data-products-v1.10.0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


assets = {}
for name in (
    "dacia-knowledge-base-data-products-v1.10.0.zip",
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
    "kind": "data_products_v1_10_0_publication",
    "published_on": "2026-08-01",
    "status": "complete",
    "tag": TAG,
    "release_id": int(RELEASE_ID) if RELEASE_ID else None,
    "source_commit": SOURCE_SHA,
    "double_build_byte_identity": True,
    "offline_workspace_verification": "PASS",
    "interface_repairs": {
        "forced_dark_theme": True,
        "grouped_commercial_grade_choices": True,
        "two_axis_sticky_comparison_grid": True,
        "deterministic_column_widths": True,
    },
    "assets": assets,
    "public_v1_9_0_immutable": True,
}
(ROOT / "data/reporting/data_products_v1_10_0_publication.json").write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

state_path = ROOT / "project/state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["updated_on"] = "2026-08-01"
state["phase"] = "Data Products v1.10.0 Publication"
state["current_package"] = {
    "package_id": "data_products_v1_10_0_publication_001",
    "kind": "data_product_release",
    "name": "Data Products v1.10.0 Publication",
    "status": "complete",
    "goal": (
        "Publish the current source-backed data products and the interactive "
        "shortlist interface repairs from the exact verified merge commit."
    ),
    "manifest_paths": [
        "data/reporting/data_products_v1_10_0_publication.json",
        "project/STATE_SUMMARY.md",
        "project/packages/data-products-v1.10.0-publication-20260801.md",
        "project/state.json",
        "tools/reporting/data_product_release.py",
    ],
}
state["next_package"] = {
    "package_id": "sandero_residual_source_closure_006",
    "kind": "source_backed_completeness_import",
    "name": "Sandero Residual Source Closure",
    "status": "planned",
    "goal": (
        "Close the three remaining eligible Sandero source candidates as one "
        "logical evidence-bounded package, without cross-configuration or "
        "cross-powertrain inference."
    ),
    "manifest_paths": [],
}
state_path.write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

publication_doc = f"""# Data Products v1.10.0 Publication

Date: 2026-08-01

## Result

The immutable `data-products-v1.10.0` release was published from exact source commit `{SOURCE_SHA}`.

The release contains the current source-backed portfolio and the interactive shortlist repairs introduced by Pull Request #427:

- forced dark theme;
- grouped commercial grade choices with exact version codes retained;
- two-axis sticky comparison grid;
- deterministic comparison-column widths.

The assets were built twice and were byte-identical. The extracted offline workspace passed verification. Public `data-products-v1.9.0` remains immutable.

## Assets

- `dacia-knowledge-base-data-products-v1.10.0.zip`;
- `data-product-release-manifest.json`;
- `SHA256SUMS`.

Exact sizes and SHA-256 values are stored in `data/reporting/data_products_v1_10_0_publication.json`.

## Next package

The next package is `sandero_residual_source_closure_006`, combining only the three remaining eligible Sandero source candidates into one evidence-bounded closure package.
"""
(ROOT / "project/packages/data-products-v1.10.0-publication-20260801.md").write_text(
    publication_doc,
    encoding="utf-8",
)
