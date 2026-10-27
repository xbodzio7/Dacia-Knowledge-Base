from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

from reporting import (
    portfolio_powertrain_transmission_matrix_release_integration as previous,
)
from reporting.commercial_offers import (
    CONFIGURATOR_OBSERVATION_KIND,
    collect_commercial_components,
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

RELEASE_NOTES = previous.RELEASE_NOTES
OBSERVED_ON = "2026-08-04"
EXPECTED_OBSERVATIONS = 18
EXPECTED_STANDARD_EQUIPMENT_LINES = 1355


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


def _exact_observations(repository: Path) -> list[dict[str, Any]]:
    closure_path = (
        repository
        / "data"
        / "reporting"
        / "cross_model_configurator_conflict_closure.json"
    )
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    rows = closure.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_OBSERVATIONS:
        raise ReleaseError("configurator identity closure does not contain 18 rows")
    canonical_codes = [
        row.get("canonical_configuration_code")
        for row in rows
        if isinstance(row, dict)
    ]
    if (
        len(canonical_codes) != EXPECTED_OBSERVATIONS
        or any(not isinstance(code, str) or not code for code in canonical_codes)
        or len(set(canonical_codes)) != EXPECTED_OBSERVATIONS
    ):
        raise ReleaseError("configurator canonical identity closure differs")

    components = collect_commercial_components(
        repository,
        canonical_codes,
        OBSERVED_ON,
    )
    observations = [
        item
        for items in components.values()
        for item in items
        if item.get("kind") == CONFIGURATOR_OBSERVATION_KIND
    ]
    if len(observations) != EXPECTED_OBSERVATIONS:
        raise ReleaseError("exact configurator observation count differs")
    exact_codes = [
        item.get("exact_configuration_code")
        for item in observations
    ]
    if (
        any(not isinstance(code, str) or not code for code in exact_codes)
        or len(set(exact_codes)) != EXPECTED_OBSERVATIONS
    ):
        raise ReleaseError("exact saved configuration codes differ")
    line_count = sum(
        len(item.get("standard_equipment_source_lines", []))
        for item in observations
    )
    if line_count != EXPECTED_STANDARD_EQUIPMENT_LINES:
        raise ReleaseError("exact standard-equipment source-line count differs")
    if any(item.get("exact_saved_configuration_only") is not True for item in observations):
        raise ReleaseError("saved-state evidence boundary differs")
    return observations


def _validate_shortlist(payload: Path, observations: list[dict[str, Any]]) -> None:
    path = payload / "shortlist" / "configuration-shortlist.html"
    if not path.is_file():
        raise ReleaseError("configuration shortlist HTML is missing")
    html = path.read_text(encoding="utf-8")
    for marker in (
        "spring-my26",
        "Dane potwierdzone konfiguracją producenta",
        "Tylko konfiguracje potwierdzone dokładnym zapisem producenta",
        "Wybrany kolor zapisanej konfiguracji",
        "Wybrane koła zapisanej konfiguracji",
        "Wybrana tapicerka zapisanej konfiguracji",
        "Dokładne wiersze wyposażenia standardowego",
        "Nie oznaczają dostępności innych kolorów",
    ):
        if marker not in html:
            raise ReleaseError(f"v1.17 shortlist marker is missing: {marker}")
    for forbidden in (
        "https://3dv2.renault.com/",
        "vehicle-photo-frame-spring",
    ):
        if forbidden in html:
            raise ReleaseError(f"obsolete Spring media marker remains: {forbidden}")


def _write_v1_17_0_release_notes(payload: Path, version: str) -> None:
    if version != "1.17.0":
        return
    path = payload / RELEASE_NOTES
    if not path.is_file():
        raise ReleaseError("release notes are missing from the release payload")
    text = path.read_text(encoding="utf-8").rstrip()
    heading = "## v1.17.0 shortlist media and exact configurator observations"
    if heading in text:
        return
    addition = """

## v1.17.0 shortlist media and exact configurator observations

This minor release publishes the completed post-v1.16.0 shortlist repairs. The
Spring result card now uses the normalized official Dacia Polska model image and
no longer relies on the separate 3dv2 parking-scene source or Spring-only crop
and framing behavior.

The interactive shortlist adds a separate producer-confirmed section for 18
exact saved configurator states observed on 2026-08-04. It can filter by exact
confirmation, selected colour, selected wheels, selected upholstery and the
1,355 preserved standard-equipment source lines.

These saved states are dated evidence, not an availability catalogue. No
alternative colour, wheel, upholstery or equipment availability is inferred;
wrapped source lines are not semantically joined, and observations are not
promoted across phase, grade, powertrain, transmission or seat count.

No source data or master data is mutated by this release. No ranking,
recommendation or inferred value is generated. Public `data-products-v1.16.0`
remains immutable.

Version 1.17.0 is built twice from the exact publication merge SHA, compared
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
    root = Path(tempfile.mkdtemp(prefix=".v1-17-shortlist-release-"))
    payload = root / "payload"
    payload.mkdir()
    try:
        manifest = _extract(output_directory, payload)
        observations = _exact_observations(repository)
        _validate_shortlist(payload, observations)
        _write_v1_17_0_release_notes(payload, version)

        archive = manifest.get("archive")
        if not isinstance(archive, dict):
            raise ReleaseError("release archive record is missing")
        archive_path = output_directory / str(archive.get("path", ""))
        manifest["files"] = write_deterministic_zip(payload, archive_path)
        manifest["configuration_shortlist_spring_media_normalized"] = True
        manifest["configuration_shortlist_configurator_observation_filters"] = True
        manifest["configurator_observation_date"] = OBSERVED_ON
        manifest["configurator_saved_state_count"] = EXPECTED_OBSERVATIONS
        manifest[
            "configurator_standard_equipment_source_line_count"
        ] = EXPECTED_STANDARD_EQUIPMENT_LINES
        manifest["configurator_observations_are_availability_catalogue"] = False
        manifest["configurator_semantic_line_joining_performed"] = False
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
                "v1.17 shortlist-integrated manifest changed after verification"
            )
        return manifest
    finally:
        shutil.rmtree(root, ignore_errors=True)
