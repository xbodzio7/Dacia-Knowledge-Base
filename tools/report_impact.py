#!/usr/bin/env python3
"""Report direct and transitive analytical-report impacts for a proposed Git change."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Sequence


REVIEWABLE_STATUSES = {"needs_review", "historical", "blocked"}


def _safe_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path.as_posix()


def _safe_dependency_glob(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    normalized = path.as_posix()
    if (
        not normalized.startswith("data/reporting/")
        or normalized.count("/") != 2
        or not normalized.endswith(".json")
        or not any(char in normalized for char in "*?[")
    ):
        return None
    return normalized


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def changed_paths(base_ref: str, head_ref: str, repository: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--no-renames", "--name-only", "-z", f"{base_ref}...{head_ref}"],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"cannot determine changed paths: {detail}")
    return sorted({path.replace("\\", "/") for path in completed.stdout.split("\0") if path})


def analyze_report_impact(
    repository: Path,
    registry_path: Path,
    changed: Sequence[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return affected reports and fail-closed findings for unreviewed current reports."""
    try:
        registry = _read_json(registry_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], [f"cannot read report registry: {exc}"]
    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        return [], ["report registry must be an object with schema_version=1"]
    entries = registry.get("reports")
    if not isinstance(entries, list):
        return [], ["report registry must contain a reports list"]

    by_id: dict[str, dict[str, Any]] = {}
    by_json_path: dict[str, str] = {}
    consumers: dict[str, set[str]] = defaultdict(set)
    direct_reasons: dict[str, set[str]] = defaultdict(set)
    changed_paths_set = {path.replace("\\", "/") for path in changed}

    for entry in entries:
        if not isinstance(entry, dict):
            return [], ["report registry entries must be objects"]
        report_id = entry.get("report_id")
        json_path = _safe_path(entry.get("json_path"))
        markdown_path = _safe_path(entry.get("markdown_path"))
        metadata_value = entry.get("metadata_path")
        metadata_path = _safe_path(metadata_value) if metadata_value is not None else None
        if not isinstance(report_id, str) or not report_id.strip():
            return [], ["report registry entry is missing report_id"]
        if report_id in by_id:
            return [], [f"duplicate report registry id: {report_id}"]
        if json_path is None or markdown_path is None:
            return [], [f"{report_id}: report paths must be safe repository-relative paths"]
        if metadata_value is not None and metadata_path is None:
            return [], [f"{report_id}: metadata_path must be a safe repository-relative path"]
        if metadata_path is not None and metadata_path in {json_path, markdown_path}:
            return [], [f"{report_id}: metadata_path must be distinct from JSON and Markdown outputs"]
        by_id[report_id] = entry
        by_json_path[json_path] = report_id
        if metadata_path is not None:
            by_json_path[metadata_path] = report_id

    for report_id, entry in by_id.items():
        json_path = repository / entry["json_path"]
        try:
            document = _read_json(json_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return [], [f"{report_id}: cannot read report metadata: {exc}"]
        metadata_relative = entry.get("metadata_path")
        if isinstance(metadata_relative, str):
            try:
                metadata = _read_json(repository / metadata_relative)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                return [], [f"{report_id}: cannot read provenance metadata sidecar: {exc}"]
        else:
            metadata = document.get("report_metadata") if isinstance(document, dict) else None
        input_files = metadata.get("input_files", []) if isinstance(metadata, dict) else []
        if not isinstance(input_files, list):
            return [], [f"{report_id}: report_metadata.input_files must be a list"]

        dependencies = entry.get("depends_on", [])
        if not isinstance(dependencies, list):
            return [], [f"{report_id}: depends_on must be a list"]
        for dependency in dependencies:
            if isinstance(dependency, str) and dependency in by_id:
                consumers[dependency].add(report_id)

        dependency_paths = entry.get("depends_on_paths", [])
        if not isinstance(dependency_paths, list):
            return [], [f"{report_id}: depends_on_paths must be a list"]
        for value in dependency_paths:
            normalized = _safe_path(value)
            if normalized is None:
                return [], [f"{report_id}: unsafe depends_on_paths entry {value!r}"]
            upstream_id = by_json_path.get(normalized)
            if upstream_id:
                consumers[upstream_id].add(report_id)
            if normalized in changed_paths_set:
                direct_reasons[report_id].add(normalized)

        dependency_globs = entry.get("depends_on_globs", [])
        if not isinstance(dependency_globs, list):
            return [], [f"{report_id}: depends_on_globs must be a list"]
        if any(not isinstance(value, str) or not value.strip() for value in dependency_globs):
            return [], [f"{report_id}: depends_on_globs entries must be non-empty patterns"]
        if len(dependency_globs) != len(set(dependency_globs)):
            return [], [f"{report_id}: depends_on_globs contains duplicate patterns"]
        for value in dependency_globs:
            pattern = _safe_dependency_glob(value)
            if pattern is None:
                return [], [f"{report_id}: unsafe depends_on_globs entry {value!r}"]
            for changed_path in changed_paths_set:
                if changed_path.count("/") == 2 and fnmatch.fnmatchcase(changed_path, pattern):
                    direct_reasons[report_id].add(changed_path)

        for item in input_files:
            if not isinstance(item, dict):
                continue
            normalized = _safe_path(item.get("path"))
            if normalized is None:
                continue
            upstream_id = by_json_path.get(normalized)
            if upstream_id and upstream_id != report_id:
                consumers[upstream_id].add(report_id)
            if normalized in changed_paths_set:
                direct_reasons[report_id].add(normalized)

    changed_report_ids: set[str] = set()
    for report_id, entry in by_id.items():
        output_paths = [entry["json_path"], entry["markdown_path"]]
        metadata_path = entry.get("metadata_path")
        if isinstance(metadata_path, str):
            output_paths.append(metadata_path)
        if any(path in changed_paths_set for path in output_paths):
            changed_report_ids.add(report_id)

    impacted = set(direct_reasons)
    queue = deque(sorted(impacted | changed_report_ids))
    visited_upstream = set(queue)
    while queue:
        upstream = queue.popleft()
        for consumer in sorted(consumers.get(upstream, set())):
            if consumer not in impacted:
                impacted.add(consumer)
            if consumer not in visited_upstream:
                visited_upstream.add(consumer)
                queue.append(consumer)

    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for report_id in sorted(impacted):
        entry = by_id[report_id]
        document = _read_json(repository / entry["json_path"])
        metadata = document.get("report_metadata", {}) if isinstance(document, dict) else {}
        status = metadata.get("status") if isinstance(metadata, dict) else None
        output_paths = [entry["json_path"], entry["markdown_path"]]
        metadata_path = entry.get("metadata_path")
        if isinstance(metadata_path, str):
            output_paths.append(metadata_path)
        outputs_changed = all(path in changed_paths_set for path in output_paths)
        reasons = sorted(direct_reasons.get(report_id, set()))
        results.append({
            "report_id": report_id,
            "status": status or "missing",
            "direct_inputs_changed": reasons,
            "report_outputs_changed": outputs_changed,
            "json_path": entry["json_path"],
            "markdown_path": entry["markdown_path"],
            "metadata_path": metadata_path if isinstance(metadata_path, str) else None,
        })
        if status not in REVIEWABLE_STATUSES and not outputs_changed:
            cause = ", ".join(reasons) if reasons else "an upstream report changed"
            if isinstance(metadata_path, str):
                output_description = ", ".join(output_paths)
                requirement = f"regenerate all report outputs ({output_description})"
            else:
                requirement = (
                    f"regenerate both {entry['json_path']} and {entry['markdown_path']}"
                )
            errors.append(
                f"{report_id}: current report is affected by {cause}; {requirement}, or explicitly set "
                "report_metadata.status to needs_review with a documented deferral"
            )
    return results, errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--registry", default="data/reporting/report_registry.json")
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    repository = args.repository.resolve()
    safe_registry = _safe_path(args.registry)
    if safe_registry is None:
        print("REPORT IMPACT: FAIL\\nregistry path must stay inside the repository", file=sys.stderr)
        return 2
    registry_path = repository / safe_registry
    try:
        paths = changed_paths(args.base_ref, args.head_ref, repository)
        reports, errors = analyze_report_impact(repository, registry_path, paths)
    except (OSError, RuntimeError) as exc:
        print(f"REPORT IMPACT: FAIL\n{exc}", file=sys.stderr)
        return 1

    print(f"Changed paths inspected: {len(paths)}")
    if reports:
        print("Direct and transitive analytical-report impact:")
        for report in reports:
            direct = ", ".join(report["direct_inputs_changed"]) or "upstream dependency"
            print(
                f"- {report['report_id']} [{report['status']}]: {direct}; "
                f"outputs updated together={str(report['report_outputs_changed']).lower()}"
            )
    else:
        print("No registered analytical reports depend on the changed paths.")

    if errors:
        print("REPORT IMPACT: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("REPORT IMPACT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
