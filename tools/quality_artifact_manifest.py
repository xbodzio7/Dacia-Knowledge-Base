#!/usr/bin/env python3
"""Generate or verify a deterministic manifest for a Quality artifact bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Any, Sequence

MANIFEST_VERSION = 1
HASH_ALGORITHM = "sha256"
DEFAULT_ARTIFACT_NAME = "dacia-knowledge-base-build"
CHUNK_SIZE = 1024 * 1024


class ManifestError(RuntimeError):
    """Raised when an artifact manifest cannot be generated or verified."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def media_type_for(name: str) -> str:
    guessed, _ = mimetypes.guess_type(name)
    return guessed or "application/octet-stream"


def _normalized_sources(paths: Sequence[Path], output: Path) -> list[Path]:
    if not paths:
        raise ManifestError("at least one --file is required")

    output_resolved = output.resolve(strict=False)
    names: dict[str, Path] = {}
    normalized: list[Path] = []
    for path in paths:
        if not path.is_file():
            raise ManifestError(f"artifact file does not exist: {path}")
        resolved = path.resolve()
        if resolved == output_resolved:
            raise ManifestError("manifest output cannot be included as an input file")
        name = path.name
        if name in names:
            raise ManifestError(
                f"duplicate artifact file name '{name}': {names[name]} and {path}"
            )
        names[name] = path
        normalized.append(path)
    return sorted(normalized, key=lambda item: item.name)


def build_manifest(
    paths: Sequence[Path],
    output: Path,
    artifact_name: str = DEFAULT_ARTIFACT_NAME,
) -> dict[str, Any]:
    if not artifact_name.strip():
        raise ManifestError("artifact name must not be empty")

    files: list[dict[str, Any]] = []
    total_size = 0
    for path in _normalized_sources(paths, output):
        size = path.stat().st_size
        total_size += size
        files.append(
            {
                "media_type": media_type_for(path.name),
                "name": path.name,
                "sha256": sha256_file(path),
                "size_bytes": size,
            }
        )

    return {
        "artifact_name": artifact_name,
        "file_count": len(files),
        "files": files,
        "hash_algorithm": HASH_ALGORITHM,
        "total_size_bytes": total_size,
        "version": MANIFEST_VERSION,
    }


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ManifestError(f"cannot read manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid manifest JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ManifestError("manifest root must be an object")
    return payload


def _expected_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("version") != MANIFEST_VERSION:
        raise ManifestError(
            f"unsupported manifest version: {payload.get('version')!r}"
        )
    if payload.get("hash_algorithm") != HASH_ALGORITHM:
        raise ManifestError("manifest hash_algorithm must be sha256")
    files = payload.get("files")
    if not isinstance(files, list):
        raise ManifestError("manifest files must be an array")
    if payload.get("file_count") != len(files):
        raise ManifestError("manifest file_count does not match files")

    names: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for entry in files:
        if not isinstance(entry, dict):
            raise ManifestError("manifest file entries must be objects")
        name = entry.get("name")
        size = entry.get("size_bytes")
        digest = entry.get("sha256")
        if not isinstance(name, str) or not name or Path(name).name != name:
            raise ManifestError(f"invalid manifest file name: {name!r}")
        if name in names:
            raise ManifestError(f"duplicate manifest file name: {name}")
        if not isinstance(size, int) or size < 0:
            raise ManifestError(f"invalid size for {name}")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(
                character not in "0123456789abcdef"
                for character in digest
            )
        ):
            raise ManifestError(f"invalid sha256 for {name}")
        names.add(name)
        normalized.append(entry)

    if [entry["name"] for entry in normalized] != sorted(names):
        raise ManifestError("manifest files must be sorted by name")
    if payload.get("total_size_bytes") != sum(
        entry["size_bytes"] for entry in normalized
    ):
        raise ManifestError("manifest total_size_bytes does not match files")
    return normalized


def verify_manifest(manifest_path: Path, root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise ManifestError(f"verification root is not a directory: {root}")
    payload = read_manifest(manifest_path)
    expected = _expected_entries(payload)

    manifest_resolved = manifest_path.resolve()
    actual_by_name: dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.resolve() == manifest_resolved:
            continue
        name = path.name
        if name in actual_by_name:
            raise ManifestError(
                f"duplicate file name in verification root '{name}': "
                f"{actual_by_name[name]} and {path}"
            )
        actual_by_name[name] = path

    expected_names = {entry["name"] for entry in expected}
    actual_names = set(actual_by_name)
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing:
        raise ManifestError("missing artifact files: " + ", ".join(missing))
    if unexpected:
        raise ManifestError(
            "unexpected artifact files: " + ", ".join(unexpected)
        )

    for entry in expected:
        path = actual_by_name[entry["name"]]
        if path.stat().st_size != entry["size_bytes"]:
            raise ManifestError(f"size mismatch for {entry['name']}")
        if sha256_file(path) != entry["sha256"]:
            raise ManifestError(f"sha256 mismatch for {entry['name']}")
    return payload


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate or verify a deterministic Quality artifact manifest."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path, help="Write a generated manifest.")
    mode.add_argument("--verify", type=Path, help="Verify an existing manifest.")
    parser.add_argument(
        "--file",
        action="append",
        type=Path,
        default=[],
        help="Artifact file to include; repeat for every file.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Extracted artifact directory used with --verify.",
    )
    parser.add_argument(
        "--artifact-name",
        default=DEFAULT_ARTIFACT_NAME,
        help="Logical artifact name stored in generated manifests.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        if arguments.output is not None:
            if arguments.root is not None:
                raise ManifestError("--root is only valid with --verify")
            payload = build_manifest(
                arguments.file,
                arguments.output,
                arguments.artifact_name,
            )
            write_manifest(arguments.output, payload)
            print(
                f"Artifact manifest written to {arguments.output}: "
                f"{payload['file_count']} files, "
                f"{payload['total_size_bytes']} bytes"
            )
            return 0

        if arguments.file:
            raise ManifestError("--file is only valid with --output")
        if arguments.root is None:
            raise ManifestError("--root is required with --verify")
        payload = verify_manifest(arguments.verify, arguments.root)
        print(
            f"Artifact manifest verified: {payload['file_count']} files, "
            f"{payload['total_size_bytes']} bytes"
        )
        return 0
    except ManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
