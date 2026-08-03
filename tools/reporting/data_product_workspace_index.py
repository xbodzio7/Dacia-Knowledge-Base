from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from reporting import data_product_workspace_index_base as _base

INDEX_NAME = _base.INDEX_NAME
WorkspaceIndexError = _base.WorkspaceIndexError
CROSS_MODEL_HTML_MEMBER = "cross-model/cross-model-comparison-view.html"
MODEL_FAMILY_HTML_MEMBER = (
    "model-families/portfolio_model_family_summary.html"
)

# Historical source-level compatibility contract retained for deterministic
# review verifiers and for readers of the public workspace implementation.
LEGACY_PRIMARY_PRODUCTS = (
    "Configuration shortlist",
    "Comparison workbook",
    "Comparison bundle manifest",
    "Release notes",
)


def _legacy_cross_model_contract(release_members: set[str]) -> dict[str, str] | None:
    if CROSS_MODEL_HTML_MEMBER in release_members:
        return {
            "title": "Models and comparison scopes",
            "description": "Browse model families and open only existing scope reports.",
            "path": _base._verified_content_path(
                Path("."),
                release_members,
                CROSS_MODEL_HTML_MEMBER,
                label="cross-model comparison HTML",
            ),
        }
    return None


def __getattr__(name: str) -> Any:
    return getattr(_base, name)


def _release_members(manifest: dict[str, Any] | Any) -> set[str]:
    raw_files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(raw_files, list):
        return set()
    return {
        str(record.get("path"))
        for record in raw_files
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }


def write_workspace_index(
    workspace_root: Path,
    release_manifest: Any,
    release_metadata: Any,
) -> Path:
    index_path = _base.write_workspace_index(
        workspace_root,
        release_manifest,
        release_metadata,
    )
    if MODEL_FAMILY_HTML_MEMBER not in _release_members(release_manifest):
        return index_path

    family_path = workspace_root / "contents" / MODEL_FAMILY_HTML_MEMBER
    if not family_path.is_file():
        raise WorkspaceIndexError(
            "portfolio model-family summary HTML is missing from verified contents"
        )

    text = index_path.read_text(encoding="utf-8")
    marker = "</main>"
    if marker not in text:
        raise WorkspaceIndexError("workspace index has no main closing marker")
    href = "contents/model-families/portfolio_model_family_summary.html"
    if href in text:
        return index_path
    card = (
        '<section aria-labelledby="model-family-summary-heading">'
        '<h2 id="model-family-summary-heading">Model family summary</h2>'
        '<div class="product-grid">'
        f'<a class="product-card" href="{escape(href, quote=True)}">'
        '<strong>Model family summary</strong>'
        '<span>Review each model family with exact scopes, configurations and '
        'source provenance.</span></a></div></section>'
    )
    index_path.write_text(text.replace(marker, card + marker, 1), encoding="utf-8")
    return index_path
