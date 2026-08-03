from __future__ import annotations

from typing import Any

from reporting import data_product_release_download_base as _base
from reporting.data_product_workspace_index import (
    INDEX_NAME,
    write_workspace_index,
)

FAMILY_HTML_MEMBER = "model-families/portfolio_model_family_summary.html"
OPTIONAL_ENTRY_POINTS = {
    **_base.OPTIONAL_ENTRY_POINTS,
    "model_family_summary_html": FAMILY_HTML_MEMBER,
}

_base.OPTIONAL_ENTRY_POINTS = OPTIONAL_ENTRY_POINTS
_base.INDEX_NAME = INDEX_NAME
_base.write_workspace_index = write_workspace_index

REPOSITORY_FULL_NAME = _base.REPOSITORY_FULL_NAME
API_ROOT = _base.API_ROOT
USER_AGENT = _base.USER_AGENT
ASSETS_DIRECTORY_NAME = _base.ASSETS_DIRECTORY_NAME
CONTENTS_DIRECTORY_NAME = _base.CONTENTS_DIRECTORY_NAME
ENTRY_POINTS = _base.ENTRY_POINTS
ReleaseDownloadError = _base.ReleaseDownloadError
OpenUrl = _base.OpenUrl


def __getattr__(name: str) -> Any:
    return getattr(_base, name)


def _extract_verified_contents(*args: Any, **kwargs: Any) -> dict[str, str]:
    _base.OPTIONAL_ENTRY_POINTS = OPTIONAL_ENTRY_POINTS
    return _base._extract_verified_contents(*args, **kwargs)


def download_release(*args: Any, **kwargs: Any) -> dict[str, Any]:
    _base.OPTIONAL_ENTRY_POINTS = OPTIONAL_ENTRY_POINTS
    _base.write_workspace_index = write_workspace_index
    return _base.download_release(*args, **kwargs)
