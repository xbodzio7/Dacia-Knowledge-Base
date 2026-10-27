from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any

from reporting import configuration_shortlist_v1_17_release_integration as previous
from reporting.data_product_release_model import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    ReleaseError,
    checksum_text,
    file_record,
    json_text,
    sha256_file,
    verify_release_assets,
    write_deterministic_zip,
    write_text,
)

EXPECTED_TECHNICAL_CATEGORIES = 162
EXPECTED_TECHNICAL_SOURCE_LINES = 349


def repository_root() -> Path:
    return previous.repository_root()


def _record(path: Path, root: Path) -> dict[str, Any]:
    record = file_record(path, root)
    return {
        key: record[key]
        for key in ("path", "media_type", "size_bytes", "sha256")
    }


def _exact_observations(repository: Path) -> list[dict[str, Any]]:
    observations = previous._exact_observations(repository)
    category_count = sum(
        len(item.get("technical_data_categories", []))
        for item in observations
    )
    line_count = sum(
        len(item.get("technical_data_source_lines", []))
        for item in observations
    )
    if category_count != EXPECTED_TECHNICAL_CATEGORIES:
        raise ReleaseError("exact technical-data category count differs")
    if line_count != EXPECTED_TECHNICAL_SOURCE_LINES:
        raise ReleaseError("exact technical-data source-line count differs")
    if any(
        item.get("semantic_technical_line_coercion_performed") is not False
        for item in observations
    ):
        raise ReleaseError("technical source-line semantic boundary differs")
    return observations


def _validate_shortlist(payload: Path, observations: list[dict[str, Any]]) -> None:
    previous._validate_shortlist(payload, observations)
    path = payload / "shortlist" / "configuration-shortlist.html"
    html = path.read_text(encoding="utf-8")
    for marker in (
        "Dokładne wiersze danych technicznych",
        "Szukaj w dokładnych wierszach danych technicznych",
        "technical_data_categories",
        "technical_data_source_lines",
        "Dane techniczne dotyczą wyłącznie dokładnie zapisanej konfiguracji",
    ):
        if marker not in html:
            raise ReleaseError(
                f"exact technical-observation shortlist marker is missing: {marker}"
            )


def create_release_assets(
    repository: Path,
    output_directory: Path,
    version: str,
    commit_sha: str,
) -> dict[str, Any]:
    previous.create_release_assets(
        repository,
        output_directory,
        version,
        commit_sha,
    )
    root = Path(tempfile.mkdtemp(prefix=".technical-observation-release-"))
    payload = root / "payload"
    payload.mkdir()
    try:
        manifest = previous._extract(output_directory, payload)
        observations = _exact_observations(repository)
        _validate_shortlist(payload, observations)

        archive = manifest.get("archive")
        if not isinstance(archive, dict):
            raise ReleaseError("release archive record is missing")
        archive_path = output_directory / str(archive.get("path", ""))
        manifest["files"] = write_deterministic_zip(payload, archive_path)
        manifest[
            "configuration_shortlist_exact_technical_observation_filters"
        ] = True
        manifest[
            "configurator_technical_category_count"
        ] = EXPECTED_TECHNICAL_CATEGORIES
        manifest[
            "configurator_technical_source_line_count"
        ] = EXPECTED_TECHNICAL_SOURCE_LINES
        manifest["configurator_technical_semantic_coercion_performed"] = False
        manifest["archive"] = _record(archive_path, output_directory)

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
                "technical-observation-integrated manifest changed after verification"
            )
        return manifest
    finally:
        shutil.rmtree(root, ignore_errors=True)
