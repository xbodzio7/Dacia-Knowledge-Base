from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from urllib.parse import unquote, urlsplit

from reporting.data_product_release_model import (
    ReleaseError,
    safe_member_name,
    sha256_file,
    verify_release_assets,
)
from reporting.data_product_workspace_index import render_workspace_index


REPORT_SCHEMA_VERSION = 1
ASSETS_DIRECTORY_NAME = "assets"
CONTENTS_DIRECTORY_NAME = "contents"
INDEX_NAME = "index.html"
REPOSITORY_FULL_NAME = "xbodzio7/Dacia-Knowledge-Base"


class WorkspaceVerificationError(ReleaseError):
    """Raised when a local data-product workspace is not intact."""


class _IndexLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.runtime_urls: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        href = values.get("href")
        if href:
            self.hrefs.append(href)
        for attribute in ("src", "action"):
            value = values.get(attribute)
            if value:
                self.runtime_urls.append(value)


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise WorkspaceVerificationError(f"{label} must be an object")
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise WorkspaceVerificationError(
            f"{label} must be an integer greater than or equal to {minimum}"
        )
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise WorkspaceVerificationError(f"{label} must be a non-empty string")
    return value


def _require_directory(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_dir():
        raise WorkspaceVerificationError(f"{label} is not a regular directory: {path}")


def _require_file(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise WorkspaceVerificationError(f"{label} is not a regular file: {path}")


def _expected_content_records(
    manifest: Mapping[str, Any],
) -> tuple[tuple[str, Mapping[str, Any]], ...]:
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise WorkspaceVerificationError("release manifest file inventory is empty")
    records: list[tuple[str, Mapping[str, Any]]] = []
    for index, raw_record in enumerate(raw_files):
        record = _object(raw_record, f"release manifest file record {index}")
        name = safe_member_name(
            _string(record.get("path"), f"release manifest file {index}.path")
        )
        records.append((name, record))
    names = [name for name, _ in records]
    if names != sorted(names) or len(names) != len(set(names)):
        raise WorkspaceVerificationError(
            "release manifest file paths must be unique and sorted"
        )
    return tuple(records)


def _verify_contents(
    contents_directory: Path,
    records: tuple[tuple[str, Mapping[str, Any]], ...],
) -> None:
    expected_files = {name for name, _ in records}
    expected_directories: set[str] = set()
    for name in expected_files:
        parts = PurePosixPath(name).parts
        for index in range(1, len(parts)):
            expected_directories.add(PurePosixPath(*parts[:index]).as_posix())

    actual_files: set[str] = set()
    actual_directories: set[str] = set()
    for path in contents_directory.rglob("*"):
        relative = path.relative_to(contents_directory).as_posix()
        safe_member_name(relative)
        if path.is_symlink():
            raise WorkspaceVerificationError(
                f"workspace contents cannot contain symlinks: {relative}"
            )
        if path.is_file():
            actual_files.add(relative)
        elif path.is_dir():
            actual_directories.add(relative)
        else:
            raise WorkspaceVerificationError(
                f"workspace contents contain an unsupported entry: {relative}"
            )

    missing = sorted(expected_files - actual_files)
    extra = sorted(actual_files - expected_files)
    if missing or extra:
        raise WorkspaceVerificationError(
            f"workspace content inventory mismatch: missing={missing}, extra={extra}"
        )
    unexpected_directories = sorted(actual_directories - expected_directories)
    if unexpected_directories:
        raise WorkspaceVerificationError(
            "workspace contents contain unexpected directories: "
            + ", ".join(unexpected_directories)
        )

    for name, record in records:
        path = contents_directory.joinpath(*PurePosixPath(name).parts)
        _require_file(path, f"workspace content member {name}")
        expected_size = _integer(
            record.get("size_bytes"),
            f"release manifest file {name}.size_bytes",
        )
        if path.stat().st_size != expected_size:
            raise WorkspaceVerificationError(
                f"workspace content size mismatch: {name}"
            )
        expected_hash = _string(
            record.get("sha256"),
            f"release manifest file {name}.sha256",
        )
        if sha256_file(path) != expected_hash:
            raise WorkspaceVerificationError(
                f"workspace content hash mismatch: {name}"
            )


def _canonical_release_url(tag: str) -> str:
    return f"https://github.com/{REPOSITORY_FULL_NAME}/releases/tag/{tag}"


def _verify_index_links(
    workspace_directory: Path,
    content: str,
    canonical_release_url: str,
) -> int:
    parser = _IndexLinks()
    try:
        parser.feed(content)
        parser.close()
    except Exception as exc:
        raise WorkspaceVerificationError(f"workspace index is invalid HTML: {exc}") from exc
    if parser.runtime_urls:
        raise WorkspaceVerificationError(
            "workspace index contains runtime resource or form URLs"
        )

    local_count = 0
    external_urls: list[str] = []
    for href in parser.hrefs:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            external_urls.append(href)
            continue
        if parsed.query or parsed.fragment:
            raise WorkspaceVerificationError(
                f"workspace index local link contains query or fragment: {href}"
            )
        try:
            decoded = unquote(parsed.path, errors="strict")
            normalized = safe_member_name(decoded)
        except (UnicodeError, ReleaseError) as exc:
            raise WorkspaceVerificationError(
                f"workspace index contains an unsafe local link: {href}"
            ) from exc
        target = workspace_directory.joinpath(*PurePosixPath(normalized).parts)
        _require_file(target, f"workspace index target {href}")
        local_count += 1

    if external_urls != [canonical_release_url]:
        raise WorkspaceVerificationError(
            "workspace index must contain exactly the canonical GitHub Release link"
        )
    if local_count == 0:
        raise WorkspaceVerificationError("workspace index contains no local file links")
    return local_count


def verify_workspace(workspace_directory: Path) -> dict[str, Any]:
    _require_directory(workspace_directory, "workspace directory")
    expected_top_level = {
        ASSETS_DIRECTORY_NAME,
        CONTENTS_DIRECTORY_NAME,
        INDEX_NAME,
    }
    actual_top_level = {path.name for path in workspace_directory.iterdir()}
    if actual_top_level != expected_top_level:
        raise WorkspaceVerificationError(
            "workspace top-level inventory mismatch: "
            f"expected={sorted(expected_top_level)}, actual={sorted(actual_top_level)}"
        )

    assets_directory = workspace_directory / ASSETS_DIRECTORY_NAME
    contents_directory = workspace_directory / CONTENTS_DIRECTORY_NAME
    index_path = workspace_directory / INDEX_NAME
    _require_directory(assets_directory, "workspace assets directory")
    _require_directory(contents_directory, "workspace contents directory")
    _require_file(index_path, "workspace index")

    try:
        manifest = verify_release_assets(assets_directory)
    except ReleaseError as exc:
        raise WorkspaceVerificationError(str(exc)) from exc
    records = _expected_content_records(manifest)
    _verify_contents(contents_directory, records)

    version = _string(manifest.get("release_version"), "release version")
    tag = _string(manifest.get("release_tag"), "release tag")
    commit = _string(manifest.get("repository_commit"), "repository commit")
    release_url = _canonical_release_url(tag)
    metadata = {
        "release_version": version,
        "release_tag": tag,
        "repository_commit": commit,
        "release_url": release_url,
    }
    try:
        expected_index = render_workspace_index(
            workspace_directory,
            manifest,
            metadata,
        ).encode("utf-8")
    except ReleaseError as exc:
        raise WorkspaceVerificationError(str(exc)) from exc
    actual_index = index_path.read_bytes()
    if actual_index != expected_index:
        raise WorkspaceVerificationError(
            "workspace index bytes do not match the verified manifests"
        )
    try:
        index_text = actual_index.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WorkspaceVerificationError(
            "workspace index is not valid UTF-8"
        ) from exc
    local_link_count = _verify_index_links(
        workspace_directory,
        index_text,
        release_url,
    )

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "verified",
        "release_version": version,
        "release_tag": tag,
        "repository_commit": commit,
        "snapshot_date": _string(manifest.get("snapshot_date"), "snapshot date"),
        "asset_count": 3,
        "content_file_count": len(records),
        "selected_configuration_count": _integer(
            manifest.get("selected_configuration_count"),
            "selected_configuration_count",
            minimum=1,
        ),
        "scope_group_count": _integer(
            manifest.get("scope_group_count"),
            "scope_group_count",
            minimum=1,
        ),
        "index_local_link_count": local_link_count,
        "index_sha256": sha256_file(index_path),
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"
