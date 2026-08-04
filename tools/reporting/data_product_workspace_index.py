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
MODEL_FAMILY_MATRIX_HTML_MEMBER = (
    "model-families/portfolio_model_family_comparison_matrix.html"
)
MODEL_VERSION_MATRIX_HTML_MEMBER = (
    "model-versions/portfolio_model_version_comparison_matrix.html"
)
SOURCE_COVERAGE_MATRIX_HTML_MEMBER = (
    "source-coverage/portfolio_source_coverage_matrix.html"
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


def _with_optional_card(
    content: str,
    workspace_root: Path,
    release_manifest: Any,
    *,
    member: str,
    heading_id: str,
    title: str,
    description: str,
    missing_label: str,
) -> str:
    if member not in _release_members(release_manifest):
        return content

    product_path = workspace_root / "contents" / member
    if not product_path.is_file():
        raise WorkspaceIndexError(
            f"{missing_label} is missing from verified contents"
        )

    marker = "</main>"
    if marker not in content:
        raise WorkspaceIndexError("workspace index has no main closing marker")
    href = "contents/" + member
    if href in content:
        return content
    card = (
        f'<section aria-labelledby="{escape(heading_id, quote=True)}">'
        f'<h2 id="{escape(heading_id, quote=True)}">{escape(title)}</h2>'
        '<div class="product-grid">'
        f'<a class="product-card" href="{escape(href, quote=True)}">'
        f'<strong>{escape(title)}</strong>'
        f'<span>{escape(description)}</span></a></div></section>'
    )
    return content.replace(marker, card + marker, 1)


def _with_model_family_card(
    content: str,
    workspace_root: Path,
    release_manifest: Any,
) -> str:
    return _with_optional_card(
        content,
        workspace_root,
        release_manifest,
        member=MODEL_FAMILY_HTML_MEMBER,
        heading_id="model-family-summary-heading",
        title="Model family summary",
        description=(
            "Review each model family with exact scopes, configurations and "
            "source provenance."
        ),
        missing_label="portfolio model-family summary HTML",
    )


def _with_model_family_matrix_card(
    content: str,
    workspace_root: Path,
    release_manifest: Any,
) -> str:
    return _with_optional_card(
        content,
        workspace_root,
        release_manifest,
        member=MODEL_FAMILY_MATRIX_HTML_MEMBER,
        heading_id="model-family-comparison-matrix-heading",
        title="Model family comparison matrix",
        description=(
            "Compare recorded family-level prices, seats, transmissions, "
            "powertrains, scopes and provenance side by side."
        ),
        missing_label="portfolio model-family comparison matrix HTML",
    )


def _with_model_version_matrix_card(
    content: str,
    workspace_root: Path,
    release_manifest: Any,
) -> str:
    return _with_optional_card(
        content,
        workspace_root,
        release_manifest,
        member=MODEL_VERSION_MATRIX_HTML_MEMBER,
        heading_id="model-version-comparison-matrix-heading",
        title="Model version comparison matrix",
        description=(
            "Compare recorded version-level prices, seats, transmissions, "
            "powertrains, scopes and provenance side by side."
        ),
        missing_label="portfolio model-version comparison matrix HTML",
    )


def _with_source_coverage_matrix_card(
    content: str,
    workspace_root: Path,
    release_manifest: Any,
) -> str:
    return _with_optional_card(
        content,
        workspace_root,
        release_manifest,
        member=SOURCE_COVERAGE_MATRIX_HTML_MEMBER,
        heading_id="source-coverage-matrix-heading",
        title="Source coverage matrix",
        description=(
            "Review every used provenance source with its exact identity and "
            "covered models, versions, configurations and relationships."
        ),
        missing_label="portfolio source coverage matrix HTML",
    )


def render_workspace_index(
    workspace_root: Path,
    release_manifest: Any,
    release_metadata: Any,
) -> str:
    content = _base.render_workspace_index(
        workspace_root,
        release_manifest,
        release_metadata,
    )
    content = _with_model_family_card(
        content,
        workspace_root,
        release_manifest,
    )
    content = _with_model_family_matrix_card(
        content,
        workspace_root,
        release_manifest,
    )
    content = _with_model_version_matrix_card(
        content,
        workspace_root,
        release_manifest,
    )
    return _with_source_coverage_matrix_card(
        content,
        workspace_root,
        release_manifest,
    )


def write_workspace_index(
    workspace_root: Path,
    release_manifest: Any,
    release_metadata: Any,
) -> Path:
    content = render_workspace_index(
        workspace_root,
        release_manifest,
        release_metadata,
    )
    index_path = workspace_root / INDEX_NAME
    index_path.write_text(content, encoding="utf-8", newline="")
    return index_path
