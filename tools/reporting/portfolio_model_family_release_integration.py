from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
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
        "active_configuration_count": 81,
        "reporting_scope_count": 22,
        "source_relationship_count": 251,
        "configurations_without_source": 0,
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
        '<a href="../model-families/portfolio_model_family_summary.html">'
        "Open the complete model-family summary with exact source provenance"
        "</a></nav>"
    )
    if FAMILY_HTML not in text:
        text = text.replace(marker, link + marker, 1)
        write_text(path, text)


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
            target = payload.joinpath(*Path(name).parts)
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
