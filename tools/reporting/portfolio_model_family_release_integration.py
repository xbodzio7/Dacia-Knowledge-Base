from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

from reporting import data_product_release as base_release
from reporting.data_product_release_model import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    ReleaseError,
    checksum_text,
    file_record,
    json_text,
    safe_member_name,
    sha256_file,
    verify_release_assets,
    write_deterministic_zip,
    write_text,
)

FAMILY_DIRECTORY = "model-families"
FAMILY_FILES = (
    "portfolio_model_family_summary.json",
    "portfolio_model_family_summary.md",
    "portfolio_model_family_summary.html",
)
CROSS_MODEL_HTML = "cross-model/cross-model-comparison-view.html"
FAMILY_HTML = f"{FAMILY_DIRECTORY}/portfolio_model_family_summary.html"
FAMILY_HTML_HREF = "../model-families/portfolio_model_family_summary.html"
RELEASE_NOTES = "RELEASE_NOTES.md"


def repository_root() -> Path:
    return base_release.repository_root()


def _archive_record(path: Path, root: Path) -> dict[str, Any]:
    record = file_record(path, root)
    return {
        "path": record["path"],
        "media_type": record["media_type"],
        "size_bytes": record["size_bytes"],
        "sha256": record["sha256"],
    }


def _copy_verified_family_outputs(repository: Path, payload: Path) -> None:
    source_directory = repository / "data" / "reporting"
    target_directory = payload / FAMILY_DIRECTORY
    for name in FAMILY_FILES:
        source = source_directory / name
        if not source.is_file():
            raise ReleaseError(f"verified portfolio family output is missing: {source}")
        target_directory.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target_directory / name)

    try:
        family = json.loads(
            (target_directory / FAMILY_FILES[0]).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"portfolio family JSON is invalid: {exc}") from exc
    summary = family.get("summary") if isinstance(family, dict) else None
    if not isinstance(summary, dict):
        raise ReleaseError("portfolio family JSON summary is missing")
    expected = {
        "model_family_count": 6,
        "active_configuration_count": 84,
        "reporting_scope_count": 23,
        "source_configuration_relationship_count": 284,
        "configurations_without_provenance_count": 0,
        "cross_scope_pairs_generated": False,
        "ranking_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ReleaseError(
                f"portfolio family summary differs for {key}: {summary.get(key)!r}"
            )


def _add_offline_navigation(payload: Path) -> None:
    path = payload / CROSS_MODEL_HTML
    if not path.is_file():
        raise ReleaseError("cross-model HTML is missing from the release payload")
    text = path.read_text(encoding="utf-8")
    marker = "</main>"
    if marker not in text:
        raise ReleaseError("cross-model HTML has no deterministic navigation marker")
    link = (
        '<nav class="family-summary-link" aria-label="Portfolio model families">'
        f'<a href="{FAMILY_HTML_HREF}">'
        "Open the complete model-family summary with exact source provenance"
        "</a></nav>"
    )
    if FAMILY_HTML_HREF not in text:
        text = text.replace(marker, link + marker, 1)
        write_text(path, text)


def _write_release_notes(payload: Path, version: str) -> None:
    additions = {
        "1.12.0": """

## v1.12.0 portfolio model-family product

This minor release adds the verified portfolio model-family summary in JSON,
Markdown and standalone HTML. It covers all six canonical families, 84 active
configurations and 23 existing reporting scopes, with 34 source records and
269 explicit source-to-configuration relationships.

The family product is copied byte-for-byte from the committed verified outputs,
and the existing cross-model offline page links to it using a relative path.
No source data, reporting scopes or comparison semantics change. No cross-scope
pairs, ranking, recommendations or inferred values are introduced.

The public `data-products-v1.11.0` release remains immutable. Version 1.12.0 is
built twice from the exact publication merge SHA, compared byte for byte and
verified again after public download before its publication receipt is accepted.
""",
        "1.12.1": """

## v1.12.1 corrective workspace interface

This patch release republishes the verified model-family data product from the
current exact source SHA so the downloaded consumer workspace includes the
previously agreed direct `model_family_summary_html` entry point and dedicated
**Model family summary** card.

The patch does not rewrite `data-products-v1.12.0` and does not change source
data, reporting scopes, comparison pairs, rankings, recommendations or inferred
values. Older immutable releases remain valid when the optional family member is
absent.

Version 1.12.1 is built twice in independent empty directories, compared byte
for byte, verified before publication and verified again after public download,
including the complete offline workspace navigation contract.
""",
    }
    addition = additions.get(version)
    if addition is None:
        return
    path = payload / RELEASE_NOTES
    if not path.is_file():
        raise ReleaseError("release notes are missing from the release payload")
    text = path.read_text(encoding="utf-8").rstrip()
    heading = f"## v{version}"
    if heading not in text:
        write_text(path, text + addition + "\n")


def _extract_verified_archive(output_directory: Path, payload: Path) -> dict[str, Any]:
    manifest = verify_release_assets(output_directory)
    archive = manifest.get("archive")
    if not isinstance(archive, dict):
        raise ReleaseError("release archive record is missing")
    archive_name = str(archive.get("path", ""))
    safe_member_name(archive_name)
    archive_path = output_directory / archive_name
    with ZipFile(archive_path) as source:
        for info in source.infolist():
            name = safe_member_name(info.filename)
            target = payload.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read(info.filename))
    return manifest


def create_release_assets(
    repository: Path,
    output_directory: Path,
    version: str,
    commit_sha: str,
) -> dict[str, Any]:
    base_release.create_release_assets(
        repository,
        output_directory,
        version,
        commit_sha,
    )
    build_root = Path(tempfile.mkdtemp(prefix=".portfolio-release-integration-"))
    payload = build_root / "payload"
    payload.mkdir()
    try:
        manifest = _extract_verified_archive(output_directory, payload)
        _copy_verified_family_outputs(repository, payload)
        _add_offline_navigation(payload)
        _write_release_notes(payload, version)

        archive = manifest["archive"]
        assert isinstance(archive, dict)
        archive_path = output_directory / str(archive["path"])
        files = write_deterministic_zip(payload, archive_path)
        manifest["files"] = files
        manifest["portfolio_model_family_summary_generated"] = True
        manifest["portfolio_model_family_summary_formats"] = [
            "JSON",
            "Markdown",
            "HTML",
        ]
        manifest["portfolio_model_family_summary_directory"] = FAMILY_DIRECTORY
        manifest["archive"] = _archive_record(archive_path, output_directory)

        manifest_path = output_directory / MANIFEST_NAME
        write_text(manifest_path, json_text(manifest))
        write_text(
            output_directory / CHECKSUMS_NAME,
            checksum_text(
                {
                    archive_path.name: sha256_file(archive_path),
                    manifest_path.name: sha256_file(manifest_path),
                }
            ),
        )
        verified = verify_release_assets(output_directory)
        if verified != manifest:
            raise ReleaseError("integrated release manifest changed after verification")
        return manifest
    finally:
        shutil.rmtree(build_root, ignore_errors=True)
