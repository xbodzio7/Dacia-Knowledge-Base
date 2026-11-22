#!/usr/bin/env python3
"""Require a completed change-impact matrix for source and master-data PRs."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

REQUIRED_AREAS = (
    "Canonical registries",
    "Configuration inventory",
    "Portfolio summaries",
    "Comparison scopes",
    "Reports",
    "Exports and release assets",
    "Historical tests",
    "Tooling",
    "Generated documentation",
    "CI",
)
MATRIX_PREFIX = "project/packages/CHANGE_IMPACT_MATRIX_"
SENSITIVE_PREFIXES = ("data/imports/", "data/master/", "data/source_intake/", "PDF/", "owner_supplied/")
REQUIRED_SECTIONS = (
    "## Package identity",
    "## Change inventory",
    "## Change-impact matrix",
    "## Test-contract review",
    "## Failure classification",
    "## Closure",
)
REQUIRED_TEST_CONTRACT_ITEMS = (
    "Mutable portfolio-wide counts are derived from canonical registries, not copied into tests as unexplained literals.",
    "Exact counts are limited to immutable fixtures or explicitly frozen, versioned contracts.",
    "Existing package tests remain bounded to their own manifests and source/configuration scopes.",
    "New package records are asserted exactly once, with explicit negative checks for duplicates/out-of-scope records.",
    "Aggregate counts are reconciled independently against emitted records.",
    "Historical snapshots and release baselines were not regenerated from current live data.",
    "Changed report dependencies are reviewed; stale reports remain needs_review until re-evaluated.",
    "Package lifecycle tests use fresh temporary repositories/staging areas and a local bare remote if push behavior is tested.",
    "Negative-path fixtures cannot contaminate success-path tests.",
    "The final diff was reviewed against the exact base SHA.",
)


def requires_matrix(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith(SENSITIVE_PREFIXES) or (
        normalized.startswith("data/reporting/")
        and normalized.endswith("_completeness.json")
    )


def validate_matrix_text(content: str, repository: Path | None = None) -> list[str]:
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"matrix is missing required section: {section}")
    lines = content.splitlines()
    checklist_start = next(
        (index for index, line in enumerate(lines) if line.strip() == "## Test-contract review"),
        None,
    )
    if checklist_start is None:
        checklist_lines: list[str] = []
    else:
        checklist_lines = []
        for line in lines[checklist_start + 1:]:
            if line.strip().startswith("## "):
                break
            if line.strip().startswith("- ["):
                checklist_lines.append(line.strip())
    expected_checklist = [f"- [x] {item}" for item in REQUIRED_TEST_CONTRACT_ITEMS]
    if checklist_lines != expected_checklist:
        errors.append(
            "Test-contract review must contain the ten exact template items, in order, "
            "and every item must be checked"
        )

    rows: dict[str, list[str]] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and cells[0] in REQUIRED_AREAS:
            if cells[0] in rows:
                errors.append(f"{cells[0]}: duplicate matrix row")
            rows[cells[0]] = cells
    for area in REQUIRED_AREAS:
        cells = rows.get(area)
        if cells is None:
            errors.append(f"matrix is missing required area: {area}")
            continue
        if len(cells) < 5:
            errors.append(f"{area}: matrix row must contain five columns")
            continue
        result = cells[2].upper()
        if result not in {"PASS", "N/A"}:
            errors.append(f"{area}: result must be PASS or justified N/A, got {cells[2]!r}")
        evidence = cells[3]
        if evidence.startswith("command: "):
            if not evidence.removeprefix("command: ").strip():
                errors.append(f"{area}: command evidence must not be empty")
        elif evidence.startswith("artifact: "):
            artifact = evidence.removeprefix("artifact: ").strip()
            artifact_path = Path(artifact)
            if not artifact or artifact_path.is_absolute() or ".." in artifact_path.parts:
                errors.append(f"{area}: artifact evidence must be a safe repository-relative path")
            elif repository is not None:
                repository_root = repository.resolve()
                resolved_artifact = (repository_root / artifact_path).resolve()
                if not resolved_artifact.is_relative_to(repository_root):
                    errors.append(f"{area}: artifact evidence resolves outside the repository")
                elif not resolved_artifact.is_file():
                    errors.append(f"{area}: referenced evidence artifact does not exist: {artifact}")
        else:
            errors.append(
                f"{area}: evidence must use 'command: <exact command>' or "
                "'artifact: <repository-relative file path>'"
            )
        if result == "N/A" and not cells[4]:
            errors.append(f"{area}: N/A requires a reason in Notes / unresolved items")
    return errors


def validate_change_impact(changed_paths: Sequence[str], repository: Path) -> list[str]:
    sensitive = sorted(path for path in changed_paths if requires_matrix(path))
    if not sensitive:
        return []
    matrices = sorted(
        path for path in changed_paths
        if path.startswith(MATRIX_PREFIX) and path.endswith(".md")
    )
    if len(matrices) != 1:
        return [
            "source/master-data changes require exactly one added or updated "
            f"{MATRIX_PREFIX}<package>.md in the same PR; found {len(matrices)}",
            "triggering paths: " + ", ".join(sensitive),
        ]
    matrix_path = repository / matrices[0]
    if not matrix_path.is_file():
        return [f"change-impact matrix file does not exist: {matrices[0]}"]
    return validate_matrix_text(matrix_path.read_text(encoding="utf-8"), repository)


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
        raise RuntimeError(f"cannot determine PR changed paths: {detail}")
    return [path for path in completed.stdout.split("\0") if path]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    try:
        paths = changed_paths(args.base_ref, args.head_ref, args.repository)
        errors = validate_change_impact(paths, args.repository)
    except (OSError, RuntimeError) as exc:
        print(f"CHANGE-IMPACT MATRIX: FAIL\n{exc}", file=sys.stderr)
        return 1
    if errors:
        print("CHANGE-IMPACT MATRIX: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("CHANGE-IMPACT MATRIX: PASS")
    if not any(requires_matrix(path) for path in paths):
        print("No source/master-data/reporting-scope changes require a matrix.")
    else:
        print("One complete, evidence-backed matrix covers the changed package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
