from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

from reporting import (
    portfolio_model_family_comparison_release_integration as family_matrix_release,
)
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

VERSION_DIRECTORY = "model-versions"
VERSION_MATRIX_FILES = (
    "portfolio_model_version_comparison_matrix.json",
    "portfolio_model_version_comparison_matrix.csv",
    "portfolio_model_version_comparison_matrix.html",
)
VERSION_MATRIX_HTML = (
    f"{VERSION_DIRECTORY}/portfolio_model_version_comparison_matrix.html"
)


def repository_root() -> Path:
    return family_matrix_release.repository_root()


def _archive_record(path: Path, root: Path) -> dict[str, Any]:
    record = file_record(path, root)
    return {
        "path": record["path"],
        "media_type": record["media_type"],
        "size_bytes": record["size_bytes"],
        "sha256": record["sha256"],
    }


def _extract_verified_archive(
    output_directory: Path,
    payload: Path,
) -> dict[str, Any]:
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


def _copy_verified_version_outputs(repository: Path, payload: Path) -> None:
    source_directory = repository / "data" / "reporting"
    target_directory = payload / VERSION_DIRECTORY
    target_directory.mkdir(parents=True, exist_ok=True)
    for name in VERSION_MATRIX_FILES:
        source = source_directory / name
        if not source.is_file():
            raise ReleaseError(
                f"verified portfolio model-version matrix is missing: {source}"
            )
        shutil.copyfile(source, target_directory / name)

    try:
        matrix = json.loads(
            (target_directory / VERSION_MATRIX_FILES[0]).read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(
            f"portfolio model-version matrix JSON is invalid: {exc}"
        ) from exc
    if not isinstance(matrix, dict):
        raise ReleaseError("portfolio model-version matrix JSON must be an object")
    if matrix.get("kind") != "portfolio_model_version_comparison_matrix":
        raise ReleaseError("portfolio model-version matrix kind differs")
    if matrix.get("version") != 1:
        raise ReleaseError("portfolio model-version matrix version differs")

    summary = matrix.get("summary")
    if not isinstance(summary, dict):
        raise ReleaseError("portfolio model-version matrix summary is missing")
    expected = {
        "model_family_count": 6,
        "active_version_count": 22,
        "active_configuration_count": 81,
        "reporting_scope_count": 22,
        "provenance_source_count": 33,
        "source_configuration_relationship_count": 251,
        "configurations_without_provenance_count": 0,
        "configuration_pairs_generated": False,
        "cross_scope_pairs_generated": False,
        "ranking_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ReleaseError(
                f"portfolio model-version matrix differs for {key}: "
                f"{summary.get(key)!r}"
            )

    versions = matrix.get("versions")
    if not isinstance(versions, list) or len(versions) != 22:
        raise ReleaseError(
            "portfolio model-version matrix must contain 22 version rows"
        )
    configuration_codes: list[str] = []
    relationship_count = 0
    for index, raw_version in enumerate(versions):
        if not isinstance(raw_version, dict):
            raise ReleaseError(
                f"portfolio model-version row {index} must be an object"
            )
        raw_codes = raw_version.get("configuration_codes")
        if not isinstance(raw_codes, list) or not all(
            isinstance(code, str) and code for code in raw_codes
        ):
            raise ReleaseError(
                f"portfolio model-version row {index} has invalid configurations"
            )
        if raw_version.get("configuration_count") != len(raw_codes):
            raise ReleaseError(
                f"portfolio model-version row {index} count differs"
            )
        provenance = raw_version.get("provenance")
        if not isinstance(provenance, dict):
            raise ReleaseError(
                f"portfolio model-version row {index} provenance is missing"
            )
        if provenance.get("configuration_coverage_count") != len(raw_codes):
            raise ReleaseError(
                f"portfolio model-version row {index} provenance coverage differs"
            )
        if provenance.get("missing_configuration_count") != 0:
            raise ReleaseError(
                f"portfolio model-version row {index} has missing provenance"
            )
        try:
            relationship_count += int(provenance["relationship_count"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ReleaseError(
                f"portfolio model-version row {index} relationship count is invalid"
            ) from exc
        configuration_codes.extend(raw_codes)

    if len(configuration_codes) != 81 or len(set(configuration_codes)) != 81:
        raise ReleaseError(
            "portfolio model-version matrix must cover 81 configurations once"
        )
    if relationship_count != 251:
        raise ReleaseError(
            "portfolio model-version matrix relationship total differs"
        )


def create_release_assets(
    repository: Path,
    output_directory: Path,
    version: str,
    commit_sha: str,
) -> dict[str, Any]:
    family_matrix_release.create_release_assets(
        repository,
        output_directory,
        version,
        commit_sha,
    )
    build_root = Path(tempfile.mkdtemp(prefix=".version-matrix-release-"))
    payload = build_root / "payload"
    payload.mkdir()
    try:
        manifest = _extract_verified_archive(output_directory, payload)
        _copy_verified_version_outputs(repository, payload)

        archive = manifest["archive"]
        assert isinstance(archive, dict)
        archive_path = output_directory / str(archive["path"])
        files = write_deterministic_zip(payload, archive_path)
        manifest["files"] = files
        manifest["portfolio_model_version_comparison_matrix_generated"] = True
        manifest["portfolio_model_version_comparison_matrix_formats"] = [
            "JSON",
            "CSV",
            "HTML",
        ]
        manifest["portfolio_model_version_comparison_matrix_directory"] = (
            VERSION_DIRECTORY
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
            raise ReleaseError(
                "version-matrix-integrated manifest changed after verification"
            )
        return manifest
    finally:
        shutil.rmtree(build_root, ignore_errors=True)
