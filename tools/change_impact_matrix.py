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
SENSITIVE_PREFIXES = ("data/master/", "data/source_intake/", "PDF/")
REQUIRED_SECTIONS = (
    "## Package identity",
    "## Change inventory",
    "## Change-impact matrix",
    "## Test-contract review",
    "## Failure classification",
    "## Closure",
)


def requires_matrix(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith(SENSITIVE_PREFIXES) or (
        normalized.startswith("data/reporting/")
        and normalized.endswith("_completeness.json")
    )


def validate_matrix_text(content: str) -> list[str]:
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"matrix is missing required section: {section}")
    rows: dict[str, list[str]] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and cells[0] in REQUIRED_AREAS:
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
        if not cells[3]:
            errors.append(f"{area}: exact command or artifact evidence is required")
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
    return validate_matrix_text(matrix_path.read_text(encoding="utf-8"))


def changed_paths(base_ref: str, head_ref: str, repository: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", "-z", f"{base_ref}...{head_ref}"],
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
