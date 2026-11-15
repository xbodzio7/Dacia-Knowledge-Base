"""Fail-fast structural preflight for repository data files."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.validators.csv_validator import validate_csv



def validate_source_capture_manifests(repository: Path) -> list[str]:
    """Validate verified capture manifests against registry rows and archived bytes."""
    intake_root = repository / "data" / "source_intake"
    if not intake_root.is_dir():
        return []

    errors: list[str] = []
    registry_path = repository / "data" / "master" / "sources.csv"
    try:
        with registry_path.open("r", encoding="utf-8-sig", newline="") as handle:
            registry_rows = list(csv.DictReader(handle))
    except OSError as exc:
        return [f"{registry_path.relative_to(repository)}: cannot read source registry: {exc}"]

    repository_root = repository.resolve()
    for manifest_path in sorted(intake_root.glob("*_capture.json")):
        try:
            with manifest_path.open("r", encoding="utf-8") as handle:
                manifest = json.load(handle)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            # The general JSON preflight reports the parse/read error.
            continue

        if not isinstance(manifest, dict):
            errors.append(f"{manifest_path.relative_to(repository)}: capture manifest must be a JSON object")
            continue

        status = manifest.get("verification_status")
        if not isinstance(status, str) or not status:
            errors.append(f"{manifest_path.relative_to(repository)}: missing verification_status")
            continue
        if not status.startswith("verified_"):
            # Diagnostic/unverified captures are not canonical binary archives.
            continue

        source_code = manifest.get("source_code")
        source_url = manifest.get("source_url")
        file_path = manifest.get("file_path")
        digest = manifest.get("sha256")
        file_size = manifest.get("file_size_bytes")
        page_count = manifest.get("page_count")
        missing_markers = manifest.get("missing_markers")
        required = {
            "source_code": source_code,
            "source_url": source_url,
            "file_path": file_path,
            "sha256": digest,
        }
        for field, value in required.items():
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{manifest_path.relative_to(repository)}: {field} must be a non-empty string")
        if any(not isinstance(value, str) or not value.strip() for value in required.values()):
            continue

        if not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            errors.append(f"{manifest_path.relative_to(repository)}: sha256 must be 64 hexadecimal characters")
            continue
        digest = digest.lower()

        if type(file_size) is not int or file_size <= 0:
            errors.append(f"{manifest_path.relative_to(repository)}: file_size_bytes must be a positive integer")
        if type(page_count) is not int or page_count <= 0:
            errors.append(f"{manifest_path.relative_to(repository)}: page_count must be a positive integer")
        if not isinstance(missing_markers, list):
            errors.append(f"{manifest_path.relative_to(repository)}: missing_markers must be a list")
        elif missing_markers:
            errors.append(f"{manifest_path.relative_to(repository)}: missing_markers is not empty: {missing_markers}")

        expected_markers = manifest.get("expected_first_page_markers")
        first_page_text = manifest.get("first_page_text")
        if not isinstance(expected_markers, list) or not expected_markers or not isinstance(first_page_text, str):
            errors.append(f"{manifest_path.relative_to(repository)}: expected first-page markers/text are missing")
        else:
            absent = [
                marker for marker in expected_markers
                if not isinstance(marker, str) or not marker or marker not in first_page_text
            ]
            if absent:
                errors.append(f"{manifest_path.relative_to(repository)}: expected first-page markers absent from manifest text: {absent}")

        for expected_key, actual_value in (
            ("expected_sha256", digest),
            ("expected_file_size_bytes", file_size),
            ("expected_page_count", page_count),
        ):
            expected_value = manifest.get(expected_key)
            if expected_value is not None and expected_value != actual_value:
                errors.append(
                    f"{manifest_path.relative_to(repository)}: {expected_key} does not match its verified value"
                )

        relative_archive = Path(file_path)
        if relative_archive.is_absolute() or ".." in relative_archive.parts:
            errors.append(f"{manifest_path.relative_to(repository)}: file_path must stay inside the repository")
            continue
        try:
            archive_path = (repository / relative_archive).resolve()
            archive_path.relative_to(repository_root)
        except (OSError, ValueError):
            errors.append(f"{manifest_path.relative_to(repository)}: file_path resolves outside the repository")
            continue

        if not archive_path.is_file():
            errors.append(f"{manifest_path.relative_to(repository)}: archived binary is missing: {file_path}")
        else:
            actual_size = archive_path.stat().st_size
            if type(file_size) is int and actual_size != file_size:
                errors.append(
                    f"{manifest_path.relative_to(repository)}: byte-size mismatch "
                    f"(manifest {file_size}, archive {actual_size})"
                )
            hasher = hashlib.sha256()
            with archive_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    hasher.update(chunk)
            if hasher.hexdigest() != digest:
                errors.append(f"{manifest_path.relative_to(repository)}: SHA-256 mismatch for archived binary")

        sidecar_name = manifest_path.name.removesuffix("_capture.json") + ".sha256"
        sidecar_path = manifest_path.with_name(sidecar_name)
        if not sidecar_path.is_file():
            errors.append(f"{manifest_path.relative_to(repository)}: SHA-256 sidecar is missing: {sidecar_name}")
        else:
            try:
                sidecar_parts = sidecar_path.read_text(encoding="utf-8").strip().split(maxsplit=1)
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"{sidecar_path.relative_to(repository)}: cannot read SHA-256 sidecar: {exc}")
            else:
                if (
                    len(sidecar_parts) != 2
                    or sidecar_parts[0].lower() != digest
                    or sidecar_parts[1].strip() != file_path
                ):
                    errors.append(
                        f"{sidecar_path.relative_to(repository)}: SHA-256 sidecar does not match manifest digest/path"
                    )

        matching_sources = [row for row in registry_rows if row.get("code") == source_code]
        if len(matching_sources) != 1:
            errors.append(
                f"{manifest_path.relative_to(repository)}: source_code {source_code!r} "
                f"must match exactly one data/master/sources.csv row"
            )
        else:
            source = matching_sources[0]
            if source.get("sha256", "").lower() != digest:
                errors.append(f"{manifest_path.relative_to(repository)}: source registry SHA-256 differs from manifest")
            if source.get("external_reference", "") != source_url:
                errors.append(f"{manifest_path.relative_to(repository)}: source registry URL differs from manifest")
            registered_path = source.get("file_path", "").strip()
            if registered_path and registered_path != file_path:
                errors.append(f"{manifest_path.relative_to(repository)}: source registry archive path differs from manifest")

    return errors


def validate_data_tree(repository: Path) -> list[str]:
    """Validate every data CSV and JSON file without modifying repository data."""
    data_root = repository / "data"
    if not data_root.is_dir():
        return [f"Data directory not found: {data_root}"]

    errors: list[str] = []
    csv_paths = sorted(data_root.rglob("*.csv"))
    json_paths = sorted(data_root.rglob("*.json"))

    for path in csv_paths:
        valid, file_errors = validate_csv(path)
        if not valid:
            errors.extend(
                f"{path.relative_to(repository)}: {error}"
                for error in file_errors
            )

    for path in json_paths:
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except UnicodeDecodeError:
            errors.append(
                f"{path.relative_to(repository)}: file is not valid UTF-8"
            )
        except json.JSONDecodeError as exc:
            errors.append(
                f"{path.relative_to(repository)}: invalid JSON at line "
                f"{exc.lineno}, column {exc.colno}: {exc.msg}"
            )
        except OSError as exc:
            errors.append(
                f"{path.relative_to(repository)}: cannot read file: {exc}"
            )

    errors.extend(validate_source_capture_manifests(repository))
    return errors


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    errors = validate_data_tree(repository)
    if errors:
        print("Package preflight failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    csv_count = len(list((repository / "data").rglob("*.csv")))
    json_count = len(list((repository / "data").rglob("*.json")))
    manifest_root = repository / "data" / "source_intake"
    manifest_count = len(list(manifest_root.glob("*_capture.json"))) if manifest_root.is_dir() else 0
    print(
        "Package preflight passed: "
        f"{csv_count} CSV files, {json_count} JSON files and "
        f"{manifest_count} source capture manifests checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
