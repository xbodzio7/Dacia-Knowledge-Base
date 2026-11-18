"""Validate registered analytical-report provenance and freshness."""

from __future__ import annotations

import argparse
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
        elif _git_blob_sha(data) != expected_blob:
            errors.append(f"{report_id}: input Git blob SHA changed: {relative}")
        if not isinstance(expected_sha256, str) or not SHA256_RE.fullmatch(expected_sha256):
            errors.append(f"{report_id}: invalid SHA-256 for {relative}")
        elif hashlib.sha256(data).hexdigest() != expected_sha256:
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
    seen: set[str] = set()
    for entry in reports:
        if not isinstance(entry, dict):
            errors.append("each report registry entry must be an object")
            continue
        report_id = entry.get("report_id")
        if not isinstance(report_id, str) or not report_id.strip():
            errors.append("report registry entry is missing report_id")
            continue
        if report_id in seen:
            errors.append(f"duplicate report registry id: {report_id}")
            continue
        seen.add(report_id)
        errors.extend(validate_report(repository, entry))
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
