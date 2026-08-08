from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

from reporting import (
    portfolio_model_version_comparison_release_integration as version_matrix_release,
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

SOURCE_DIRECTORY = "source-coverage"
SOURCE_MATRIX_FILES = (
    "portfolio_source_coverage_matrix.json",
    "portfolio_source_coverage_matrix.csv",
    "portfolio_source_coverage_matrix.html",
)
SOURCE_MATRIX_HTML = f"{SOURCE_DIRECTORY}/portfolio_source_coverage_matrix.html"
RELEASE_NOTES = version_matrix_release.RELEASE_NOTES


def repository_root() -> Path:
    return version_matrix_release.repository_root()


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


def _string_list(
    source: dict[str, Any],
    key: str,
    *,
    row_index: int,
) -> list[str]:
    raw = source.get(key)
    if not isinstance(raw, list) or not all(
        isinstance(value, str) and value for value in raw
    ):
        raise ReleaseError(
            f"portfolio source coverage row {row_index} has invalid {key}"
        )
    if len(raw) != len(set(raw)):
        raise ReleaseError(
            f"portfolio source coverage row {row_index} duplicates {key}"
        )
    return raw


def _copy_verified_source_outputs(repository: Path, payload: Path) -> None:
    source_directory = repository / "data" / "reporting"
    target_directory = payload / SOURCE_DIRECTORY
    target_directory.mkdir(parents=True, exist_ok=True)
    for name in SOURCE_MATRIX_FILES:
        source = source_directory / name
        if not source.is_file():
            raise ReleaseError(
                f"verified portfolio source coverage matrix is missing: {source}"
            )
        shutil.copyfile(source, target_directory / name)

    try:
        matrix = json.loads(
            (target_directory / SOURCE_MATRIX_FILES[0]).read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(
            f"portfolio source coverage matrix JSON is invalid: {exc}"
        ) from exc
    if not isinstance(matrix, dict):
        raise ReleaseError("portfolio source coverage matrix JSON must be an object")
    if matrix.get("kind") != "portfolio_source_coverage_matrix":
        raise ReleaseError("portfolio source coverage matrix kind differs")
    if matrix.get("version") != 1:
        raise ReleaseError("portfolio source coverage matrix version differs")

    summary = matrix.get("summary")
    if not isinstance(summary, dict):
        raise ReleaseError("portfolio source coverage matrix summary is missing")
    expected = {
        "provenance_source_count": 34,
        "source_configuration_relationship_count": 269,
        "active_configuration_count": 84,
        "active_version_count": 22,
        "model_family_count": 6,
        "configurations_without_provenance_count": 0,
        "source_quality_scores_generated": False,
        "source_rankings_generated": False,
        "recommendations_generated": False,
        "inferred_values_generated": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ReleaseError(
                f"portfolio source coverage matrix differs for {key}: "
                f"{summary.get(key)!r}"
            )

    sources = matrix.get("sources")
    if not isinstance(sources, list) or len(sources) != 34:
        raise ReleaseError(
            "portfolio source coverage matrix must contain 34 source rows"
        )

    source_codes: list[str] = []
    configuration_codes: set[str] = set()
    version_codes: set[str] = set()
    model_codes: set[str] = set()
    relationship_count = 0
    for index, raw_source in enumerate(sources):
        if not isinstance(raw_source, dict):
            raise ReleaseError(
                f"portfolio source coverage row {index} must be an object"
            )
        source_code = raw_source.get("source_code")
        if not isinstance(source_code, str) or not source_code:
            raise ReleaseError(
                f"portfolio source coverage row {index} has invalid source code"
            )
        source_codes.append(source_code)
        if raw_source.get("status") != "active":
            raise ReleaseError(
                f"portfolio source coverage row {index} is not active"
            )

        sha256 = raw_source.get("sha256")
        if (
            not isinstance(sha256, str)
            or len(sha256) != 64
            or any(character not in "0123456789abcdef" for character in sha256)
        ):
            raise ReleaseError(
                f"portfolio source coverage row {index} has invalid SHA-256"
            )
        if not raw_source.get("external_reference") and not raw_source.get(
            "file_path"
        ):
            raise ReleaseError(
                f"portfolio source coverage row {index} has no source identity"
            )

        relationships = _string_list(
            raw_source,
            "relationship_types",
            row_index=index,
        )
        configurations = _string_list(
            raw_source,
            "configuration_codes",
            row_index=index,
        )
        versions = _string_list(
            raw_source,
            "version_codes",
            row_index=index,
        )
        models = _string_list(
            raw_source,
            "model_codes",
            row_index=index,
        )
        model_names = _string_list(
            raw_source,
            "model_names",
            row_index=index,
        )
        if raw_source.get("configuration_count") != len(configurations):
            raise ReleaseError(
                f"portfolio source coverage row {index} configuration count differs"
            )
        if raw_source.get("version_count") != len(versions):
            raise ReleaseError(
                f"portfolio source coverage row {index} version count differs"
            )
        if raw_source.get("model_family_count") != len(models):
            raise ReleaseError(
                f"portfolio source coverage row {index} model count differs"
            )
        if len(model_names) != len(models):
            raise ReleaseError(
                f"portfolio source coverage row {index} model names differ"
            )
        try:
            row_relationship_count = int(raw_source["relationship_count"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ReleaseError(
                f"portfolio source coverage row {index} relationship count is invalid"
            ) from exc
        if row_relationship_count < len(configurations) or not relationships:
            raise ReleaseError(
                f"portfolio source coverage row {index} relationship coverage differs"
            )

        relationship_count += row_relationship_count
        configuration_codes.update(configurations)
        version_codes.update(versions)
        model_codes.update(models)

    if len(source_codes) != len(set(source_codes)):
        raise ReleaseError("portfolio source coverage matrix duplicates source codes")
    if relationship_count != 269:
        raise ReleaseError(
            "portfolio source coverage matrix relationship total differs"
        )
    if len(configuration_codes) != 84:
        raise ReleaseError(
            "portfolio source coverage matrix must cover 84 configurations"
        )
    if len(version_codes) != 22:
        raise ReleaseError(
            "portfolio source coverage matrix must cover 22 versions"
        )
    if len(model_codes) != 6:
        raise ReleaseError(
            "portfolio source coverage matrix must cover six model families"
        )


def _write_v1_15_0_release_notes(payload: Path, version: str) -> None:
    if version != "1.15.0":
        return
    path = payload / RELEASE_NOTES
    if not path.is_file():
        raise ReleaseError("release notes are missing from the release payload")
    text = path.read_text(encoding="utf-8").rstrip()
    addition = """

## v1.15.0 portfolio source coverage matrix

This minor release adds the verified portfolio source coverage matrix in JSON,
CSV and standalone HTML. It exposes all 34 active provenance sources used by the
current portfolio and preserves all 269 explicit source-to-configuration
relationships, together with exact registered external or local identities,
SHA-256 values and covered model-family, version and configuration codes.

The three source-coverage files, the three model-version matrix files, the three
family-comparison files and the three family-summary files are copied byte for
byte from committed verified outputs. The downloaded offline workspace adds the
optional `source_coverage_matrix_html` entry point and a separate **Source
coverage matrix** card. Older immutable releases remain valid when the optional
source-coverage member is absent.

No source data, master data, reporting scope or comparison semantics change. No
source quality score, ranking, recommendation or inferred value is introduced.
Public `data-products-v1.14.1` remains immutable.

Version 1.15.0 is built twice from the exact publication merge SHA, compared byte
for byte and verified as a complete offline workspace before publication. The
three public assets are downloaded and verified again before the publication
receipt and canonical state transition are accepted.
"""
    heading = "## v1.15.0 portfolio source coverage matrix"
    if heading not in text:
        write_text(path, text + addition + "\n")


def create_release_assets(
    repository: Path,
    output_directory: Path,
    version: str,
    commit_sha: str,
) -> dict[str, Any]:
    version_matrix_release.create_release_assets(
        repository,
        output_directory,
        version,
        commit_sha,
    )
    build_root = Path(tempfile.mkdtemp(prefix=".source-coverage-release-"))
    payload = build_root / "payload"
    payload.mkdir()
    try:
        manifest = _extract_verified_archive(output_directory, payload)
        _copy_verified_source_outputs(repository, payload)
        _write_v1_15_0_release_notes(payload, version)

        archive = manifest["archive"]
        assert isinstance(archive, dict)
        archive_path = output_directory / str(archive["path"])
        files = write_deterministic_zip(payload, archive_path)
        manifest["files"] = files
        manifest["portfolio_source_coverage_matrix_generated"] = True
        manifest["portfolio_source_coverage_matrix_formats"] = [
            "JSON",
            "CSV",
            "HTML",
        ]
        manifest["portfolio_source_coverage_matrix_directory"] = (
            SOURCE_DIRECTORY
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
                "source-coverage-integrated manifest changed after verification"
            )
        return manifest
    finally:
        shutil.rmtree(build_root, ignore_errors=True)
