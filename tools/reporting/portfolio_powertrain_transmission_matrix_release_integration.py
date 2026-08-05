from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

from reporting import portfolio_source_coverage_matrix_release_integration as previous
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

DIRECTORY = "powertrains"
FILES = (
    "portfolio-powertrain-transmission-matrix.json",
    "portfolio-powertrain-transmission-matrix.csv",
    "portfolio-powertrain-transmission-matrix.html",
)
HTML = f"{DIRECTORY}/{FILES[2]}"
RELEASE_NOTES = previous.RELEASE_NOTES


def repository_root() -> Path:
    return previous.repository_root()


def _record(path: Path, root: Path) -> dict[str, Any]:
    record = file_record(path, root)
    return {
        key: record[key]
        for key in ("path", "media_type", "size_bytes", "sha256")
    }


def _extract(output_directory: Path, payload: Path) -> dict[str, Any]:
    manifest = verify_release_assets(output_directory)
    archive = manifest.get("archive")
    if not isinstance(archive, dict):
        raise ReleaseError("release archive record is missing")
    archive_path = output_directory / str(archive.get("path", ""))
    safe_member_name(archive_path.name)
    with ZipFile(archive_path) as source:
        for info in source.infolist():
            name = safe_member_name(info.filename)
            target = payload.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read(info.filename))
    return manifest


def _copy(repository: Path, payload: Path) -> None:
    source = repository / "output" / "portfolio-powertrain-transmission-matrix"
    target = payload / DIRECTORY
    target.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        if not (source / name).is_file():
            raise ReleaseError(f"verified matrix missing: {source / name}")
        shutil.copyfile(source / name, target / name)

    matrix = json.loads((target / FILES[0]).read_text(encoding="utf-8"))
    summary = matrix.get("summary", {})
    records = matrix.get("records", [])
    codes = [
        code
        for row in records
        for code in row.get("configuration_codes", [])
    ]
    if (
        matrix.get("matrix_version") != 1
        or summary.get("active_configuration_count") != 81
        or len(codes) != 81
        or len(set(codes)) != 81
    ):
        raise ReleaseError("powertrain matrix coverage differs")
    for key in (
        "ranking_generated",
        "recommendations_generated",
        "inferred_values_generated",
    ):
        if summary.get(key) is not False:
            raise ReleaseError(f"matrix boundary differs: {key}")


def _write_v1_16_0_release_notes(payload: Path, version: str) -> None:
    if version != "1.16.0":
        return
    path = payload / RELEASE_NOTES
    if not path.is_file():
        raise ReleaseError("release notes are missing from the release payload")
    text = path.read_text(encoding="utf-8").rstrip()
    heading = "## v1.16.0 powertrain and transmission matrix"
    if heading in text:
        return
    addition = """

## v1.16.0 powertrain and transmission matrix

This minor release adds the verified portfolio powertrain and transmission
matrix in JSON, CSV and standalone HTML. It groups all 81 active configurations
only by their exact recorded powertrain label and transmission type and exposes
the covered model, version and configuration identities for every group.

The downloaded offline workspace adds the optional
`powertrain_transmission_matrix_html` entry point and a separate **Powertrain
and transmission matrix** card alongside the existing family-summary,
family-comparison, model-version and source-coverage products. Older immutable
releases remain valid when the optional powertrain member is absent.

No source data, master data, grouping semantics, reporting scope, ranking,
recommendation or inferred value changes. Public `data-products-v1.15.0`
remains immutable.

Version 1.16.0 is built twice from the exact publication merge SHA, compared
byte for byte and verified as a complete offline workspace before publication.
The three public assets are downloaded and verified again before the
publication receipt and canonical state transition are accepted.
"""
    write_text(path, text + addition + "\n")


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
    root = Path(tempfile.mkdtemp(prefix=".powertrain-release-"))
    payload = root / "payload"
    payload.mkdir()
    try:
        manifest = _extract(output_directory, payload)
        _copy(repository, payload)
        _write_v1_16_0_release_notes(payload, version)
        archive = manifest["archive"]
        assert isinstance(archive, dict)
        archive_path = output_directory / str(archive["path"])
        manifest["files"] = write_deterministic_zip(payload, archive_path)
        manifest["portfolio_powertrain_transmission_matrix_generated"] = True
        manifest["portfolio_powertrain_transmission_matrix_formats"] = [
            "JSON",
            "CSV",
            "HTML",
        ]
        manifest["portfolio_powertrain_transmission_matrix_directory"] = DIRECTORY
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
                "powertrain-integrated manifest changed after verification"
            )
        return manifest
    finally:
        shutil.rmtree(root, ignore_errors=True)
