#!/usr/bin/env python3
"""Create and validate quality receipts for manifest-driven packages."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import package_workflow
from package_workflow import GitCommandError, PackageManifest


RECEIPT_VERSION = 1
TOOL_VERSION = 1


@dataclass(frozen=True)
class PackageState:
    """Stable Git and byte-level fingerprints for one package state."""

    tree_sha: str
    byte_sha256: str


@dataclass(frozen=True)
class ReceiptValidation:
    """Validation result for a reusable quality receipt."""

    valid: bool
    reason: str
    tests: int | None = None


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def require_external_output(repository: Path, path: Path) -> Path:
    """Require generated workflow artifacts to live outside the repository."""
    resolved_repository = repository.resolve()
    resolved_path = path.expanduser().resolve()
    if _is_within(resolved_path, resolved_repository):
        raise GitCommandError(
            f"workflow output must be outside the repository: {path}"
        )
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Write stable UTF-8 JSON atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def package_tree_sha(
    repository: Path,
    manifest: PackageManifest,
) -> str:
    """Hash the package state through an isolated temporary Git index."""
    with tempfile.TemporaryDirectory(prefix="dkb-package-index-") as temp_dir:
        index_path = Path(temp_dir) / "index"
        extra_environment = {"GIT_INDEX_FILE": str(index_path)}
        package_workflow.run_git(
            repository,
            "read-tree",
            manifest.base_sha,
            extra_environment=extra_environment,
        )
        package_workflow.run_git(
            repository,
            "add",
            "-A",
            "--",
            *manifest.paths,
            extra_environment=extra_environment,
        )
        return package_workflow.run_git(
            repository,
            "write-tree",
            extra_environment=extra_environment,
        ).stdout.strip()


def package_byte_sha256(
    repository: Path,
    manifest: PackageManifest,
) -> str:
    """Hash exact working-tree bytes, paths and deletion markers."""
    digest = hashlib.sha256()
    for path in sorted(manifest.paths):
        path_bytes = path.encode("utf-8")
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        target = repository / path
        try:
            metadata = target.lstat()
        except FileNotFoundError:
            digest.update(b"MISSING\0")
            continue
        except OSError as exc:
            raise GitCommandError(
                f"cannot inspect package path {path!r}: {exc}"
            ) from exc

        if target.is_symlink():
            link_bytes = os.readlink(target).encode("utf-8")
            digest.update(b"SYMLINK\0")
            digest.update(len(link_bytes).to_bytes(8, "big"))
            digest.update(link_bytes)
            continue
        if not target.is_file():
            raise GitCommandError(
                f"manifest path is not a regular file or deletion: {path!r}"
            )
        try:
            content = target.read_bytes()
        except OSError as exc:
            raise GitCommandError(
                f"cannot read package path {path!r}: {exc}"
            ) from exc
        digest.update(b"FILE\0")
        digest.update(metadata.st_mode.to_bytes(8, "big", signed=False))
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def package_state(
    repository: Path,
    manifest: PackageManifest,
) -> PackageState:
    """Return stable Git-tree and raw-byte fingerprints."""
    return PackageState(
        tree_sha=package_tree_sha(repository, manifest),
        byte_sha256=package_byte_sha256(repository, manifest),
    )


def build_receipt(
    manifest: PackageManifest,
    state: PackageState,
    *,
    tests: int,
) -> dict[str, Any]:
    """Build the stable quality receipt payload."""
    return {
        "version": RECEIPT_VERSION,
        "tool_version": TOOL_VERSION,
        "branch": manifest.branch,
        "base_sha": manifest.base_sha,
        "commit_message": manifest.commit_message,
        "paths": list(manifest.paths),
        "tree_sha": state.tree_sha,
        "byte_sha256": state.byte_sha256,
        "quality": "PASS",
        "tests": tests,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
    }


def load_receipt(path: Path) -> dict[str, Any]:
    """Read one receipt JSON object."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GitCommandError(f"cannot read quality receipt {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise GitCommandError(f"invalid quality receipt JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GitCommandError("quality receipt root must be an object")
    return payload


def validate_receipt(
    path: Path,
    manifest: PackageManifest,
    state: PackageState,
) -> ReceiptValidation:
    """Validate a receipt against the exact current package state."""
    if not path.is_file():
        return ReceiptValidation(False, "receipt does not exist")
    try:
        payload = load_receipt(path)
    except GitCommandError as exc:
        return ReceiptValidation(False, str(exc))

    expected = {
        "version": RECEIPT_VERSION,
        "tool_version": TOOL_VERSION,
        "branch": manifest.branch,
        "base_sha": manifest.base_sha,
        "commit_message": manifest.commit_message,
        "paths": list(manifest.paths),
        "tree_sha": state.tree_sha,
        "byte_sha256": state.byte_sha256,
        "quality": "PASS",
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            return ReceiptValidation(False, f"receipt field differs: {field}")

    tests = payload.get("tests")
    if not isinstance(tests, int) or tests < 1:
        return ReceiptValidation(False, "receipt tests must be a positive integer")
    if not isinstance(payload.get("generated_at"), str):
        return ReceiptValidation(False, "receipt generated_at is missing")
    if not isinstance(payload.get("python_version"), str):
        return ReceiptValidation(False, "receipt python_version is missing")
    return ReceiptValidation(True, "receipt matches package state", tests=tests)


def _read_quality_summary(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GitCommandError(
            f"cannot read structured quality summary {path}: {exc}"
        ) from exc
    if not isinstance(payload, dict) or payload.get("status") != "PASS":
        raise GitCommandError("structured quality summary is not PASS")
    tests = payload.get("tests")
    if not isinstance(tests, int) or tests < 1:
        raise GitCommandError("structured quality summary has no test count")
    return tests


def run_quality_and_write_receipt(
    repository: Path,
    manifest: PackageManifest,
    *,
    base_ref: str,
    receipt_path: Path,
    log_path: Path | None,
    require_review_state: bool = True,
) -> int:
    """Run full quality once and bind its PASS result to exact package bytes."""
    receipt_path = require_external_output(repository, receipt_path)
    if log_path is None:
        log_path = receipt_path.with_name("quality.log")
    log_path = require_external_output(repository, log_path)

    package_workflow.verify_manifest_base(repository, manifest, base_ref)
    if package_workflow.current_branch(repository) != manifest.branch:
        raise GitCommandError(
            f"manifest branch is {manifest.branch!r}, current branch is "
            f"{package_workflow.current_branch(repository)!r}"
        )
    if require_review_state:
        package_workflow.verify_review_manifest(
            repository,
            manifest,
            base_ref,
            package_workflow.changed_paths(repository),
        )
    state_before = package_state(repository, manifest)

    with tempfile.TemporaryDirectory(prefix="dkb-quality-summary-") as temp_dir:
        summary_path = Path(temp_dir) / "quality-summary.json"
        command = [
            sys.executable,
            str(repository / "tools" / "dkb.py"),
            "quality",
            "--concise",
            "--log-file",
            str(log_path),
            "--summary-json",
            str(summary_path),
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=repository,
                env=package_workflow.git_environment(),
                check=False,
            )
        except OSError as exc:
            raise GitCommandError(f"cannot run quality checks: {exc}") from exc
        if completed.returncode != 0:
            return completed.returncode
        tests = _read_quality_summary(summary_path)

    if require_review_state:
        package_workflow.exact_paths(
            package_workflow.changed_paths(repository),
            manifest.paths,
            label="working tree after quality",
        )
    state_after = package_state(repository, manifest)
    if state_after != state_before:
        raise GitCommandError(
            "package state changed while quality checks were running"
        )

    write_json_atomic(
        receipt_path,
        build_receipt(manifest, state_after, tests=tests),
    )
    print(f"Quality receipt: {receipt_path}")
    print(f"Full quality log: {log_path}")
    return 0
