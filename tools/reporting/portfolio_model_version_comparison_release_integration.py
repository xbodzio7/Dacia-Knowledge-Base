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
RELEASE_NOTES = family_matrix_release.RELEASE_NOTES


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
        "active_configuration_count": 84,
        "reporting_scope_count": 23,
        "provenance_source_count": 35,
        "source_configuration_relationship_count": 284,
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

    if len(configuration_codes) != 84 or len(set(configuration_codes)) != 84:
        raise ReleaseError(
            "portfolio model-version matrix must cover 84 configurations once"
        )
    if relationship_count != 269:
        raise ReleaseError(
            "portfolio model-version matrix relationship total differs"
        )


def _write_v1_14_0_release_notes(payload: Path, version: str) -> None:
    if version != "1.14.0":
        return
    path = payload / RELEASE_NOTES
    if not path.is_file():
        raise ReleaseError("release notes are missing from the release payload")
    text = path.read_text(encoding="utf-8").rstrip()
    addition = """

## v1.14.0 portfolio model-version comparison matrix

This minor release adds the verified portfolio model-version comparison matrix
in JSON, CSV and standalone HTML. It presents all 22 active canonical versions
and all 84 active configurations side by side using only recorded version-bounded
fields: prices, seat states, transmissions, powertrains, existing reporting-scope
memberships and explicit source provenance.

The three model-version matrix files, the three family-comparison files and the
three family-summary files are copied byte for byte from committed verified
outputs. The downloaded offline workspace adds the optional
`model_version_comparison_matrix_html` entry point and a separate **Model version
comparison matrix** card. Older immutable releases remain valid when the optional
model-version member is absent.

No source data, master data, reporting scope or comparison semantics change. No
new configuration pair, cross-scope pair, ranking, recommendation or inferred
value is introduced. Public `data-products-v1.13.0` remains immutable.

Version 1.14.0 is built twice from the exact publication merge SHA, compared byte
for byte and verified as a complete offline workspace before publication. The
three public assets are downloaded and verified again before the publication
receipt and canonical state transition are accepted.
"""
    heading = "## v1.14.0 portfolio model-version comparison matrix"
    if heading not in text:
        write_text(path, text + addition + "\n")


def _write_v1_14_1_release_notes(payload: Path, version: str) -> None:
    if version != "1.14.1":
        return
    path = payload / RELEASE_NOTES
    if not path.is_file():
        raise ReleaseError("release notes are missing from the release payload")
    text = path.read_text(encoding="utf-8").rstrip()
    addition = """

## v1.14.1 corrected interactive shortlist package

This patch release corrects the release assembly path so the archived interactive
shortlist is generated by the same canonical interface pipeline as the direct
`configuration-shortlist --html` command.

The package now includes the official Spring model image with the verified local
fallback, reviewed commercial-price and technical-gap states, non-overlapping
comparison navigation, per-group and global parameter-group controls, and
session-scoped collapse persistence. The already present forced dark theme,
grouped commercial grade choices with exact version codes, deterministic column
widths and two-axis sticky comparison grid remain unchanged.

No source data, master data, configuration identity, reporting scope, comparison
pair, ranking, recommendation or inferred value changes. Public
`data-products-v1.14.0` remains immutable.
"""
    heading = "## v1.14.1 corrected interactive shortlist package"
    if heading not in text:
        write_text(path, text + addition + "\n")


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
        _write_v1_14_0_release_notes(payload, version)
        _write_v1_14_1_release_notes(payload, version)

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
