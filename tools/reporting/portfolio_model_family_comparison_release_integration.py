from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

from reporting import portfolio_model_family_release_integration as family_release
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

MATRIX_FILES = (
    "portfolio_model_family_comparison_matrix.json",
    "portfolio_model_family_comparison_matrix.csv",
    "portfolio_model_family_comparison_matrix.html",
)
MATRIX_HTML = (
    f"{family_release.FAMILY_DIRECTORY}/"
    "portfolio_model_family_comparison_matrix.html"
)


def repository_root() -> Path:
    return family_release.repository_root()


def _archive_record(path: Path, root: Path) -> dict[str, Any]:
    record = file_record(path, root)
    return {
        "path": record["path"],
        "media_type": record["media_type"],
        "size_bytes": record["size_bytes"],
        "sha256": record["sha256"],
    }


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


def _copy_verified_matrix_outputs(repository: Path, payload: Path) -> None:
    source_directory = repository / "data" / "reporting"
    target_directory = payload / family_release.FAMILY_DIRECTORY
    target_directory.mkdir(parents=True, exist_ok=True)
    for name in MATRIX_FILES:
        source = source_directory / name
        if not source.is_file():
            raise ReleaseError(f"verified portfolio family matrix is missing: {source}")
        shutil.copyfile(source, target_directory / name)

    try:
        matrix = json.loads(
            (target_directory / MATRIX_FILES[0]).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"portfolio family matrix JSON is invalid: {exc}") from exc
    if not isinstance(matrix, dict):
        raise ReleaseError("portfolio family matrix JSON must be an object")
    if matrix.get("kind") != "portfolio_model_family_comparison_matrix":
        raise ReleaseError("portfolio family matrix kind differs")
    if matrix.get("version") != 1:
        raise ReleaseError("portfolio family matrix version differs")
    source_product = matrix.get("source_product")
    if not isinstance(source_product, dict):
        raise ReleaseError("portfolio family matrix source product is missing")
    expected_source = {
        "kind": "portfolio_model_family_summary",
        "version": 1,
        "path": "data/reporting/portfolio_model_family_summary.json",
    }
    if source_product != expected_source:
        raise ReleaseError("portfolio family matrix source product differs")
    summary = matrix.get("summary")
    if not isinstance(summary, dict):
        raise ReleaseError("portfolio family matrix summary is missing")
    expected = {
        "model_family_count": 6,
        "active_configuration_count": 81,
        "reporting_scope_count": 22,
        "provenance_source_count": 33,
        "source_configuration_relationship_count": 251,
        "configurations_without_provenance_count": 0,
        "cross_scope_pairs_generated": False,
        "ranking_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ReleaseError(
                f"portfolio family matrix differs for {key}: {summary.get(key)!r}"
            )
    families = matrix.get("families")
    if not isinstance(families, list) or len(families) != 6:
        raise ReleaseError("portfolio family matrix must contain six family rows")


def create_release_assets(
    repository: Path,
    output_directory: Path,
    version: str,
    commit_sha: str,
) -> dict[str, Any]:
    family_release.create_release_assets(
        repository,
        output_directory,
        version,
        commit_sha,
    )
    build_root = Path(tempfile.mkdtemp(prefix=".family-matrix-release-integration-"))
    payload = build_root / "payload"
    payload.mkdir()
    try:
        manifest = _extract_verified_archive(output_directory, payload)
        _copy_verified_matrix_outputs(repository, payload)

        archive = manifest["archive"]
        assert isinstance(archive, dict)
        archive_path = output_directory / str(archive["path"])
        files = write_deterministic_zip(payload, archive_path)
        manifest["files"] = files
        manifest["portfolio_model_family_comparison_matrix_generated"] = True
        manifest["portfolio_model_family_comparison_matrix_formats"] = [
            "JSON",
            "CSV",
            "HTML",
        ]
        manifest["portfolio_model_family_comparison_matrix_directory"] = (
            family_release.FAMILY_DIRECTORY
        )
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
            raise ReleaseError("matrix-integrated manifest changed after verification")
        return manifest
    finally:
        shutil.rmtree(build_root, ignore_errors=True)
