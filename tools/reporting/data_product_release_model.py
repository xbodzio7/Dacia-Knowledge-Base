from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from zipfile import ZIP_STORED, ZipFile, ZipInfo

RELEASE_SCHEMA_VERSION = 1
TAG_PREFIX = "data-products-v"
MANIFEST_NAME = "data-product-release-manifest.json"
CHECKSUMS_NAME = "SHA256SUMS"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)

_VERSION_PATTERN = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z"
)
_SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")

MEDIA_TYPES = {
    ".csv": "text/csv",
    ".html": "text/html",
    ".json": "application/json",
    ".md": "text/markdown",
    ".sqlite": "application/vnd.sqlite3",
    ".txt": "text/plain",
    ".xlsx": (
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    ".zip": "application/zip",
}


class ReleaseError(ValueError):
    """Raised when deterministic release assets are invalid."""


def normalize_version(value: str) -> str:
    if value != value.strip() or not _VERSION_PATTERN.fullmatch(value):
        raise ReleaseError(
            "release version must be normalized MAJOR.MINOR.PATCH"
        )
    return value


def normalize_commit_sha(value: str) -> str:
    if not _SHA_PATTERN.fullmatch(value):
        raise ReleaseError(
            "repository commit must be a 40-character lowercase SHA-1"
        )
    return value


def release_tag(version: str) -> str:
    return TAG_PREFIX + normalize_version(version)


def archive_name(version: str) -> str:
    normalized = normalize_version(version)
    return f"dacia-knowledge-base-data-products-v{normalized}.zip"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def media_type(path: str | Path) -> str:
    suffix = PurePosixPath(str(path)).suffix.lower()
    return MEDIA_TYPES.get(suffix, "application/octet-stream")


def safe_member_name(value: str) -> str:
    if not value or "\\" in value:
        raise ReleaseError(f"unsafe archive member path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ReleaseError(f"unsafe archive member path: {value!r}")
    normalized = path.as_posix()
    if normalized != value:
        raise ReleaseError(f"archive member path is not normalized: {value!r}")
    return normalized


def json_text(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


def file_record(path: Path, root: Path) -> dict[str, Any]:
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ReleaseError(f"file is outside release root: {path}") from exc
    safe_member_name(relative)
    return {
        "path": relative,
        "media_type": media_type(relative),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _zip_info(name: str) -> ZipInfo:
    info = ZipInfo(safe_member_name(name), FIXED_ZIP_TIME)
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def write_deterministic_zip(source: Path, output: Path) -> list[dict[str, Any]]:
    if not source.is_dir():
        raise ReleaseError(f"release payload directory does not exist: {source}")
    files = sorted(
        (
            path
            for path in source.rglob("*")
            if path.is_file() or path.is_symlink()
        ),
        key=lambda path: path.relative_to(source).as_posix(),
    )
    if not files:
        raise ReleaseError("release payload is empty")
    records: list[dict[str, Any]] = []
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_STORED, allowZip64=True) as archive:
        for path in files:
            if path.is_symlink():
                raise ReleaseError(f"release payload cannot contain symlinks: {path}")
            record = file_record(path, source)
            archive.writestr(_zip_info(record["path"]), path.read_bytes())
            records.append(record)
    return records


def checksum_text(records: Mapping[str, str]) -> str:
    lines = [f"{digest}  {name}" for name, digest in sorted(records.items())]
    return "\n".join(lines) + "\n"


def parse_checksums(path: Path) -> dict[str, str]:
    output: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise ReleaseError(
                f"invalid checksum line {line_number} in {path.name}"
            )
        name = safe_member_name(parts[1])
        if name in output:
            raise ReleaseError(f"duplicate checksum entry: {name}")
        output[name] = parts[0]
    return output


def _manifest_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot read release manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseError("release manifest must contain a JSON object")
    return value


def verify_release_assets(output_directory: Path) -> dict[str, Any]:
    manifest_path = output_directory / MANIFEST_NAME
    checksums_path = output_directory / CHECKSUMS_NAME
    if not manifest_path.is_file() or not checksums_path.is_file():
        raise ReleaseError("release manifest and SHA256SUMS are required")
    manifest = _manifest_object(manifest_path)
    if manifest.get("schema_version") != RELEASE_SCHEMA_VERSION:
        raise ReleaseError("unsupported release manifest schema version")
    version = normalize_version(str(manifest.get("release_version", "")))
    normalize_commit_sha(str(manifest.get("repository_commit", "")))
    if manifest.get("release_tag") != release_tag(version):
        raise ReleaseError("release tag does not match release version")

    archive = manifest.get("archive")
    if not isinstance(archive, dict):
        raise ReleaseError("release manifest archive record is missing")
    expected_archive_name = archive_name(version)
    if archive.get("path") != expected_archive_name:
        raise ReleaseError("release archive name does not match release version")
    archive_path = output_directory / expected_archive_name
    if not archive_path.is_file():
        raise ReleaseError("release archive is missing")
    if archive.get("size_bytes") != archive_path.stat().st_size:
        raise ReleaseError("release archive size does not match manifest")
    if archive.get("sha256") != sha256_file(archive_path):
        raise ReleaseError("release archive hash does not match manifest")

    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise ReleaseError("release manifest file inventory is empty")
    expected_paths = [str(item.get("path", "")) for item in raw_files if isinstance(item, dict)]
    if len(expected_paths) != len(raw_files):
        raise ReleaseError("release manifest file records must be objects")
    if expected_paths != sorted(expected_paths) or len(expected_paths) != len(set(expected_paths)):
        raise ReleaseError("release manifest file paths must be unique and sorted")

    with ZipFile(archive_path) as archive_file:
        infos = archive_file.infolist()
        names = [safe_member_name(info.filename) for info in infos]
        if names != expected_paths:
            raise ReleaseError("release archive inventory does not match manifest")
        for info, record in zip(infos, raw_files, strict=True):
            if info.compress_type != ZIP_STORED or info.date_time != FIXED_ZIP_TIME:
                raise ReleaseError(f"archive metadata is not deterministic: {info.filename}")
            content = archive_file.read(info.filename)
            if record.get("media_type") != media_type(info.filename):
                raise ReleaseError(f"media type mismatch: {info.filename}")
            if record.get("size_bytes") != len(content):
                raise ReleaseError(f"size mismatch: {info.filename}")
            if record.get("sha256") != sha256_bytes(content):
                raise ReleaseError(f"hash mismatch: {info.filename}")

    checksums = parse_checksums(checksums_path)
    expected_checksums = {
        expected_archive_name: sha256_file(archive_path),
        MANIFEST_NAME: sha256_file(manifest_path),
    }
    if checksums != expected_checksums:
        raise ReleaseError("SHA256SUMS does not match release assets")

    expected_top_level = sorted(
        [expected_archive_name, MANIFEST_NAME, CHECKSUMS_NAME]
    )
    actual_top_level = sorted(path.name for path in output_directory.iterdir())
    if actual_top_level != expected_top_level:
        raise ReleaseError("release output contains unexpected top-level assets")
    return manifest
