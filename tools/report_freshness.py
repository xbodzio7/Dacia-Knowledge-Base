"""Validate registered analytical-report provenance and freshness."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


STATUSES = {"current", "historical", "needs_review", "blocked"}
FINDING_STATES = {"open", "resolved", "not_reproducible", "out_of_scope", "needs_review"}
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _safe_repo_path(repository: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (repository / candidate).resolve()
    try:
        resolved.relative_to(repository.resolve())
    except ValueError:
        return None
    return resolved


def _safe_repo_glob(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    normalized = candidate.as_posix()
    if not normalized.startswith("data/reporting/") or not any(char in normalized for char in "*?["):
        return None
    return normalized


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _is_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_report(repository: Path, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    report_id = entry.get("report_id", "<unknown>")
    json_path = _safe_repo_path(repository, entry.get("json_path"))
    markdown_path = _safe_repo_path(repository, entry.get("markdown_path"))
    if json_path is None or markdown_path is None:
        return [f"{report_id}: report paths must be safe repository-relative paths"]
    if not json_path.is_file():
        return [f"{report_id}: JSON report is missing: {entry.get('json_path')}"]
    if not markdown_path.is_file():
        return [f"{report_id}: Markdown companion is missing: {entry.get('markdown_path')}"]

    try:
        document = _read_json(json_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"{report_id}: cannot parse JSON report: {exc}"]
    if not isinstance(document, dict):
        return [f"{report_id}: JSON report root must be an object"]

    if entry.get("legacy") is True:
        # Legacy reports remain available but cannot be advertised as current.
        metadata = document.get("report_metadata")
        if isinstance(metadata, dict) and metadata.get("status") == "current":
            errors.append(f"{report_id}: legacy registry entry cannot claim current status")
        return errors

    metadata = document.get("report_metadata")
    if not isinstance(metadata, dict):
        return [f"{report_id}: missing report_metadata (new reports must fail closed)"]

    required = {
        "schema_version": type(metadata.get("schema_version")) is int and metadata.get("schema_version") == 1,
        "report_id": metadata.get("report_id") == report_id,
        "generated_at": _is_timestamp(metadata.get("generated_at")),
        "repository": isinstance(metadata.get("repository"), str) and bool(metadata.get("repository", "").strip()),
        "base_commit_sha": isinstance(metadata.get("base_commit_sha"), str) and bool(SHA1_RE.fullmatch(metadata.get("base_commit_sha", ""))),
        "input_files": isinstance(metadata.get("input_files"), list) and bool(metadata.get("input_files")),
        "scope": isinstance(metadata.get("scope"), str) and bool(metadata.get("scope", "").strip()),
        "status": metadata.get("status") in STATUSES,
    }
    for field, valid in required.items():
        if not valid:
            errors.append(f"{report_id}: invalid or missing report_metadata.{field}")
    expected_repository = os.environ.get("DKB_EXPECTED_REPOSITORY") or os.environ.get("GITHUB_REPOSITORY")
    if expected_repository and metadata.get("repository") != expected_repository:
        errors.append(
            f"{report_id}: report repository {metadata.get('repository')!r} "
            f"does not match execution repository {expected_repository!r}"
        )
    if errors:
        return errors

    input_files = metadata["input_files"]
    seen_paths: set[str] = set()
    for item in input_files:
        if not isinstance(item, dict):
            errors.append(f"{report_id}: each input_files entry must be an object")
            continue
        relative = item.get("path")
        path = _safe_repo_path(repository, relative)
        if path is None:
            errors.append(f"{report_id}: unsafe or missing input path {relative!r}")
            continue
        if relative in seen_paths:
            errors.append(f"{report_id}: duplicate input path {relative}")
            continue
        seen_paths.add(relative)
        if not path.is_file():
            errors.append(f"{report_id}: input file is missing: {relative}")
            continue
        data = path.read_bytes()
        expected_blob = item.get("git_blob_sha")
        expected_sha256 = item.get("sha256")
        if not isinstance(expected_blob, str) or not SHA1_RE.fullmatch(expected_blob):
            errors.append(f"{report_id}: invalid git_blob_sha for {relative}")
            continue
        if not isinstance(expected_sha256, str) or not SHA256_RE.fullmatch(expected_sha256):
            errors.append(f"{report_id}: invalid SHA-256 for {relative}")
            continue
        blob_changed = _git_blob_sha(data) != expected_blob
        sha256_changed = hashlib.sha256(data).hexdigest() != expected_sha256
        if blob_changed or sha256_changed:
            # Keep original immutable fingerprints for reports explicitly awaiting
            # review; never silently rebase their provenance onto unreviewed inputs.
            if metadata.get("status") != "needs_review":
                if blob_changed:
                    errors.append(f"{report_id}: input Git blob SHA changed: {relative}")
                if sha256_changed:
                    errors.append(f"{report_id}: input SHA-256 changed: {relative}")

    findings = document.get("findings", [])
    if not isinstance(findings, list):
        errors.append(f"{report_id}: findings must be a list")
    else:
        finding_ids: set[str] = set()
        for finding in findings:
            if not isinstance(finding, dict):
                errors.append(f"{report_id}: each finding must be an object")
                continue
            finding_id = finding.get("finding_id")
            if not isinstance(finding_id, str) or not finding_id.strip():
                errors.append(f"{report_id}: finding is missing finding_id")
            elif finding_id in finding_ids:
                errors.append(f"{report_id}: duplicate finding_id {finding_id}")
            else:
                finding_ids.add(finding_id)
            if not isinstance(finding.get("status"), str) or finding.get("status") not in FINDING_STATES:
                errors.append(f"{report_id}: finding {finding_id!r} has invalid status")
            if not isinstance(finding.get("evidence_refs"), list) or not finding.get("evidence_refs"):
                errors.append(f"{report_id}: finding {finding_id!r} needs evidence_refs")
            if not _is_timestamp(finding.get("last_verified_at")):
                errors.append(f"{report_id}: finding {finding_id!r} needs timezone-aware last_verified_at")

    try:
        markdown = markdown_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return errors + [f"{report_id}: cannot read Markdown companion: {exc}"]
    parity = {
        "Report ID": report_id,
        "Generated": metadata["generated_at"],
        "Analysed commit": metadata["base_commit_sha"],
        "Status": metadata["status"],
        "Scope": metadata["scope"],
    }
    for label, value in parity.items():
        if f"{label}: {value}" not in markdown:
            errors.append(f"{report_id}: Markdown companion does not match {label}")
    return errors


def validate_registry(repository: Path, registry_path: Path) -> list[str]:
    try:
        registry = _read_json(registry_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"cannot read report registry: {exc}"]
    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        return ["report registry must be an object with schema_version=1"]
    reports = registry.get("reports")
    if not isinstance(reports, list) or not reports:
        return ["report registry must contain a non-empty reports list"]

    errors: list[str] = []
    entries: dict[str, dict[str, Any]] = {}
    errors_by_id: dict[str, list[str]] = {}
    for entry in reports:
        if not isinstance(entry, dict):
            errors.append("each report registry entry must be an object")
            continue
        report_id = entry.get("report_id")
        if not isinstance(report_id, str) or not report_id.strip():
            errors.append("report registry entry is missing report_id")
            continue
        if report_id in entries:
            errors.append(f"duplicate report registry id: {report_id}")
            continue
        entries[report_id] = entry
        errors_by_id[report_id] = validate_report(repository, entry)

    graph: dict[str, list[str]] = {}
    for report_id, entry in entries.items():
        if "depends_on" not in entry:
            errors_by_id[report_id].append(
                f"{report_id}: depends_on must be explicitly declared (use [] when none)"
            )
        dependencies = entry.get("depends_on", [])
        if not isinstance(dependencies, list):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on must be an array of report IDs"
            )
            graph[report_id] = []
            continue
        if any(not isinstance(item, str) or not item.strip() for item in dependencies):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on entries must be non-empty report IDs"
            )
        valid_dependencies = [
            item for item in dependencies
            if isinstance(item, str) and item.strip()
        ]
        if len(valid_dependencies) != len(set(valid_dependencies)):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on contains duplicate report IDs"
            )
        for dependency in valid_dependencies:
            if dependency == report_id:
                errors_by_id[report_id].append(
                    f"{report_id}: report cannot depend on itself"
                )
            elif dependency not in entries:
                errors_by_id[report_id].append(
                    f"{report_id}: unknown report dependency {dependency}"
                )
        graph[report_id] = [
            dependency for dependency in valid_dependencies
            if dependency in entries and dependency != report_id
        ]

    json_path_to_id = {
        str(entry["json_path"]): report_id
        for report_id, entry in entries.items()
        if isinstance(entry.get("json_path"), str)
    }
    for report_id, entry in entries.items():
        if "depends_on_paths" not in entry:
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_paths must be explicitly declared (use [] when none)"
            )
        dependency_paths = entry.get("depends_on_paths", [])
        if not isinstance(dependency_paths, list):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_paths must be an array of report JSON paths"
            )
            continue
        if any(not isinstance(item, str) or not item.strip() for item in dependency_paths):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_paths entries must be non-empty paths"
            )
        valid_paths = [
            item for item in dependency_paths
            if isinstance(item, str) and item.strip()
        ]
        if len(valid_paths) != len(set(valid_paths)):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_paths contains duplicate paths"
            )
        for relative in valid_paths:
            path = _safe_repo_path(repository, relative)
            if path is None:
                errors_by_id[report_id].append(
                    f"{report_id}: unsafe report dependency path {relative!r}"
                )
            elif not path.is_file():
                errors_by_id[report_id].append(
                    f"{report_id}: report dependency file is missing: {relative}"
                )
            if relative in json_path_to_id:
                errors_by_id[report_id].append(
                    f"{report_id}: registered report dependency {relative} must use depends_on report ID"
                )

        raw_globs = entry.get("depends_on_globs", [])
        glob_matches: dict[str, set[str]] = {}
        if not isinstance(raw_globs, list):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_globs must be an array of repository-relative patterns"
            )
            raw_globs = []
        if any(not isinstance(item, str) or not item.strip() for item in raw_globs):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_globs entries must be non-empty patterns"
            )
        valid_globs = [
            item for item in raw_globs
            if isinstance(item, str) and item.strip()
        ]
        if len(valid_globs) != len(set(valid_globs)):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_globs contains duplicate patterns"
            )
        for value in valid_globs:
            pattern = _safe_repo_glob(value)
            if pattern is None:
                errors_by_id[report_id].append(
                    f"{report_id}: unsafe report dependency glob {value!r}"
                )
                continue
            matches = {
                path.relative_to(repository).as_posix()
                for path in repository.glob(pattern)
                if path.is_file()
            }
            if not matches:
                errors_by_id[report_id].append(
                    f"{report_id}: report dependency glob matches no files: {pattern}"
                )
            for relative in matches:
                if relative in json_path_to_id:
                    errors_by_id[report_id].append(
                        f"{report_id}: registered report dependency {relative} must use depends_on report ID, not a glob"
                    )
            glob_matches[pattern] = matches

        json_path = _safe_repo_path(repository, entry.get("json_path"))
        if json_path is None or not json_path.is_file():
            continue
        try:
            document = _read_json(json_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        metadata = document.get("report_metadata") if isinstance(document, dict) else None
        if not isinstance(metadata, dict):
            if entry.get("legacy") is True:
                continue
            continue
        input_files = metadata.get("input_files")
        if not isinstance(input_files, list):
            continue
        input_paths = {
            item.get("path")
            for item in input_files
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        }
        for pattern, matches in glob_matches.items():
            for relative in sorted(matches - input_paths):
                errors_by_id[report_id].append(
                    f"{report_id}: report dependency glob {pattern} matched {relative}, which is missing from report_metadata.input_files"
                )
        direct_report_inputs = {
            relative
            for relative in input_paths
            if relative.startswith("data/reporting/") and relative.endswith(".json")
        }
        expected_registered = {
            json_path_to_id[relative]
            for relative in direct_report_inputs
            if relative in json_path_to_id and json_path_to_id[relative] != report_id
        }
        declared_registered = set(
            item for item in entry.get("depends_on", [])
            if isinstance(item, str)
        )
        for dependency in sorted(expected_registered - declared_registered):
            errors_by_id[report_id].append(
                f"{report_id}: registered report input {dependency} is missing from depends_on"
            )
        expected_paths = direct_report_inputs - set(json_path_to_id)
        declared_paths = set(valid_paths)
        glob_declared_paths = set().union(*glob_matches.values()) if glob_matches else set()
        for relative in sorted(expected_paths - declared_paths - glob_declared_paths):
            errors_by_id[report_id].append(
                f"{report_id}: unregistered report input {relative} is missing from depends_on_paths"
            )
        for relative in sorted(declared_paths - expected_paths):
            errors_by_id[report_id].append(
                f"{report_id}: depends_on_paths entry is not a direct report input: {relative}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(report_id: str, trail: list[str]) -> None:
        if report_id in visiting:
            cycle = trail[trail.index(report_id):] + [report_id]
            message = "report dependency cycle: " + " -> ".join(cycle)
            for member in set(cycle):
                errors_by_id[member].append(message)
            return
        if report_id in visited:
            return
        visiting.add(report_id)
        for dependency in graph.get(report_id, []):
            visit(dependency, trail + [dependency])
        visiting.remove(report_id)
        visited.add(report_id)

    for report_id in graph:
        visit(report_id, [report_id])

    # A consumer is stale whenever any direct or transitive dependency is invalid.
    changed = True
    while changed:
        changed = False
        for report_id, dependencies in graph.items():
            if any(errors_by_id.get(dependency) for dependency in dependencies):
                message = f"{report_id}: one or more report dependencies are invalid or stale"
                if message not in errors_by_id[report_id]:
                    errors_by_id[report_id].append(message)
                    changed = True

    for report_errors in errors_by_id.values():
        errors.extend(report_errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="data/reporting/report_registry.json")
    args = parser.parse_args(argv)
    repository = Path(__file__).resolve().parents[1]
    registry_path = _safe_repo_path(repository, args.registry)
    if registry_path is None:
        print("ERROR: registry path must stay inside the repository", file=sys.stderr)
        return 2
    errors = validate_registry(repository, registry_path)
    if errors:
        print("Report freshness validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Report freshness validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
