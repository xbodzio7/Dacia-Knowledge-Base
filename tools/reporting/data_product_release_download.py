from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from zipfile import ZipFile

from reporting.data_product_release_model import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    ReleaseError,
    archive_name,
    normalize_commit_sha,
    normalize_version,
    release_tag,
    safe_member_name,
    verify_release_assets,
)
from reporting.data_product_workspace_index import (
    INDEX_NAME,
    write_workspace_index,
)


REPOSITORY_FULL_NAME = "xbodzio7/Dacia-Knowledge-Base"
API_ROOT = "https://api.github.com"
USER_AGENT = "Dacia-Knowledge-Base-data-product-release-download"
ASSETS_DIRECTORY_NAME = "assets"
CONTENTS_DIRECTORY_NAME = "contents"
ENTRY_POINTS = {
    "shortlist_html": "shortlist/configuration-shortlist.html",
    "comparison_workbook": (
        "comparison-bundle/configuration-comparison-workbook.xlsx"
    ),
    "comparison_bundle_manifest": (
        "comparison-bundle/comparison-bundle-manifest.json"
    ),
    "release_notes": "RELEASE_NOTES.md",
}

OpenUrl = Callable[[Request], Any]


class ReleaseDownloadError(ReleaseError):
    """Raised when a public release cannot be downloaded safely."""


def _api_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _read_json(
    path: str,
    *,
    token: str | None,
    opener: OpenUrl,
) -> Mapping[str, Any]:
    request = Request(API_ROOT + path, headers=_api_headers(token))
    try:
        with opener(request) as response:
            payload = response.read()
    except (HTTPError, URLError, OSError) as exc:
        raise ReleaseDownloadError(
            f"cannot read GitHub API resource {path}: {exc}"
        ) from exc
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseDownloadError(
            f"GitHub API resource is not valid UTF-8 JSON: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ReleaseDownloadError(
            f"GitHub API resource must contain an object: {path}"
        )
    return value


def _release_metadata(
    version: str,
    *,
    token: str | None,
    opener: OpenUrl,
) -> tuple[Mapping[str, Any], tuple[Mapping[str, Any], ...]]:
    tag = release_tag(version)
    release = _read_json(
        f"/repos/{REPOSITORY_FULL_NAME}/releases/tags/{quote(tag, safe='')}",
        token=token,
        opener=opener,
    )
    if release.get("tag_name") != tag:
        raise ReleaseDownloadError("GitHub release tag does not match version")
    if release.get("draft") is not False:
        raise ReleaseDownloadError("GitHub release must not be a draft")
    if release.get("prerelease") is not False:
        raise ReleaseDownloadError("GitHub release must not be a prerelease")

    raw_assets = release.get("assets")
    if not isinstance(raw_assets, list):
        raise ReleaseDownloadError("GitHub release assets must be a list")
    expected_names = {
        archive_name(version),
        MANIFEST_NAME,
        CHECKSUMS_NAME,
    }
    by_name: dict[str, Mapping[str, Any]] = {}
    for raw_asset in raw_assets:
        if not isinstance(raw_asset, dict):
            raise ReleaseDownloadError(
                "GitHub release asset metadata must be an object"
            )
        name = raw_asset.get("name")
        if not isinstance(name, str) or not name:
            raise ReleaseDownloadError("GitHub release asset has no name")
        if name in by_name:
            raise ReleaseDownloadError(f"duplicate GitHub release asset: {name}")
        by_name[name] = raw_asset
    if set(by_name) != expected_names:
        raise ReleaseDownloadError(
            "GitHub release must contain exactly the three canonical assets"
        )

    prefix = (
        f"https://github.com/{REPOSITORY_FULL_NAME}/releases/download/"
        f"{tag}/"
    )
    ordered: list[Mapping[str, Any]] = []
    for name in sorted(expected_names):
        asset = by_name[name]
        url = asset.get("browser_download_url")
        if url != prefix + name:
            raise ReleaseDownloadError(
                f"unexpected public download URL for release asset: {name}"
            )
        size = asset.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ReleaseDownloadError(
                f"invalid public release asset size: {name}"
            )
        ordered.append(asset)
    return release, tuple(ordered)


def _tag_object(value: Mapping[str, Any], label: str) -> Mapping[str, Any]:
    raw_object = value.get("object")
    if not isinstance(raw_object, dict):
        raise ReleaseDownloadError(f"{label} has no Git object")
    return raw_object


def _resolve_tag_commit(
    version: str,
    *,
    token: str | None,
    opener: OpenUrl,
) -> str:
    tag = release_tag(version)
    ref = _read_json(
        f"/repos/{REPOSITORY_FULL_NAME}/git/ref/tags/{quote(tag, safe='')}",
        token=token,
        opener=opener,
    )
    current = _tag_object(ref, "Git tag reference")
    seen: set[str] = set()
    for _ in range(8):
        object_type = current.get("type")
        raw_sha = current.get("sha")
        if not isinstance(raw_sha, str):
            raise ReleaseDownloadError("Git tag object has no SHA")
        sha = normalize_commit_sha(raw_sha)
        if object_type == "commit":
            return sha
        if object_type != "tag":
            raise ReleaseDownloadError(
                f"Git tag resolves to unsupported object type: {object_type!r}"
            )
        if sha in seen:
            raise ReleaseDownloadError("Git tag object chain contains a cycle")
        seen.add(sha)
        tag_object = _read_json(
            f"/repos/{REPOSITORY_FULL_NAME}/git/tags/{sha}",
            token=token,
            opener=opener,
        )
        current = _tag_object(tag_object, "annotated Git tag")
    raise ReleaseDownloadError("Git tag object chain is too deep")


def _prepare_output_directory(output_directory: Path) -> Path:
    parent = output_directory.parent
    parent.mkdir(parents=True, exist_ok=True)
    if output_directory.exists():
        if not output_directory.is_dir():
            raise ReleaseDownloadError(
                f"download output path is not a directory: {output_directory}"
            )
        if any(output_directory.iterdir()):
            raise ReleaseDownloadError(
                "download output directory must not exist or must be empty: "
                f"{output_directory}"
            )
    return Path(
        tempfile.mkdtemp(
            prefix=f".{output_directory.name}.download-",
            dir=parent,
        )
    )


def _download_asset(
    asset: Mapping[str, Any],
    destination: Path,
    *,
    opener: OpenUrl,
) -> None:
    name = str(asset["name"])
    request = Request(
        str(asset["browser_download_url"]),
        headers={
            "Accept": "application/octet-stream",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with opener(request) as response, destination.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
    except (HTTPError, URLError, OSError) as exc:
        raise ReleaseDownloadError(
            f"cannot download public release asset {name}: {exc}"
        ) from exc
    if destination.stat().st_size != asset["size"]:
        raise ReleaseDownloadError(
            f"downloaded asset size does not match GitHub metadata: {name}"
        )


def _extract_verified_contents(
    assets_directory: Path,
    contents_directory: Path,
    manifest: Mapping[str, Any],
) -> dict[str, str]:
    raw_archive = manifest.get("archive")
    if not isinstance(raw_archive, dict):
        raise ReleaseDownloadError("verified release manifest has no archive")
    archive_path = assets_directory / str(raw_archive["path"])
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list):
        raise ReleaseDownloadError("verified release manifest has no files")

    contents_directory.mkdir()
    with ZipFile(archive_path) as archive:
        for raw_record in raw_files:
            if not isinstance(raw_record, dict):
                raise ReleaseDownloadError(
                    "verified release manifest file record is invalid"
                )
            name = safe_member_name(str(raw_record.get("path", "")))
            relative = PurePosixPath(name)
            destination = contents_directory.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(name))

    entry_points: dict[str, str] = {}
    for key, relative_name in ENTRY_POINTS.items():
        path = contents_directory.joinpath(
            *PurePosixPath(relative_name).parts
        )
        if not path.is_file():
            raise ReleaseDownloadError(
                f"release is missing consumer entry point: {relative_name}"
            )
        entry_points[key] = (
            Path(CONTENTS_DIRECTORY_NAME) / relative_name
        ).as_posix()
    return entry_points


def download_release(
    version: str,
    output_directory: Path,
    *,
    token: str | None = None,
    opener: OpenUrl = urlopen,
) -> dict[str, Any]:
    try:
        normalized_version = normalize_version(version)
    except ReleaseError as exc:
        raise ReleaseDownloadError(str(exc)) from exc
    selected_token = token if token is not None else os.environ.get("GITHUB_TOKEN")
    build_root = _prepare_output_directory(output_directory)
    assets_directory = build_root / ASSETS_DIRECTORY_NAME
    contents_directory = build_root / CONTENTS_DIRECTORY_NAME
    assets_directory.mkdir()
    try:
        release, assets = _release_metadata(
            normalized_version,
            token=selected_token,
            opener=opener,
        )
        tag_commit = _resolve_tag_commit(
            normalized_version,
            token=selected_token,
            opener=opener,
        )
        for asset in assets:
            _download_asset(
                asset,
                assets_directory / str(asset["name"]),
                opener=opener,
            )
        manifest = verify_release_assets(assets_directory)
        if manifest["release_version"] != normalized_version:
            raise ReleaseDownloadError(
                "downloaded manifest version does not match requested version"
            )
        if manifest["repository_commit"] != tag_commit:
            raise ReleaseDownloadError(
                "release tag commit does not match downloaded manifest"
            )
        entry_points = _extract_verified_contents(
            assets_directory,
            contents_directory,
            manifest,
        )
        release_metadata = {
            "release_version": normalized_version,
            "release_tag": release_tag(normalized_version),
            "repository_commit": tag_commit,
            "release_id": release.get("id"),
            "release_url": release.get("html_url"),
            "published_at": release.get("published_at"),
        }
        index_path = write_workspace_index(
            build_root,
            manifest,
            release_metadata,
        )
        entry_points = {
            "workspace_index": index_path.relative_to(build_root).as_posix(),
            **entry_points,
        }
        result = {
            **release_metadata,
            "selected_configuration_count": manifest.get(
                "selected_configuration_count"
            ),
            "scope_group_count": manifest.get("scope_group_count"),
            "assets_directory": ASSETS_DIRECTORY_NAME,
            "contents_directory": CONTENTS_DIRECTORY_NAME,
            "entry_points": entry_points,
        }
        if output_directory.exists():
            output_directory.rmdir()
        build_root.replace(output_directory)
        return result
    except ReleaseDownloadError:
        shutil.rmtree(build_root, ignore_errors=True)
        raise
    except ReleaseError as exc:
        shutil.rmtree(build_root, ignore_errors=True)
        raise ReleaseDownloadError(str(exc)) from exc
    except Exception as exc:
        shutil.rmtree(build_root, ignore_errors=True)
        raise ReleaseDownloadError(
            f"cannot download data product release: {exc}"
        ) from exc
