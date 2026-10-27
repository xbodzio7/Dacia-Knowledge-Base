#!/usr/bin/env python3
"""Generate scope-safe comparison reports from explicit selections."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.configuration_comparison_bundle import (
    BundleError,
    create_bundle,
    manifest_path,
    repository_root,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Group selected configurations by independent reporting scope "
            "and generate existing comparison formats without cross-scope "
            "pairs."
        )
    )
    parser.add_argument(
        "--configuration-code",
        action="append",
        default=[],
        help=(
            "Select an exact active configuration code. Repeat values are "
            "deduplicated."
        ),
    )
    parser.add_argument(
        "--shortlist-json",
        action="append",
        type=Path,
        default=[],
        help=(
            "Read selected codes from results[].configuration_code in an "
            "existing configuration shortlist JSON report."
        ),
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        required=True,
        help=(
            "Write the bundle to a new or empty directory. Publication is "
            "transactional."
        ),
    )
    return parser.parse_args(argv)


def _print_summary(manifest: dict[str, object], output: Path) -> None:
    print("Configuration comparison bundle")
    print("-------------------------------")
    print(
        "Selected configurations : "
        f"{manifest['selected_configuration_count']}"
    )
    print(f"Scope groups            : {manifest['scope_group_count']}")
    print(
        "Comparable scopes       : "
        f"{manifest['comparable_scope_count']}"
    )
    print(
        "Singleton scopes        : "
        f"{manifest['singleton_scope_count']}"
    )
    print("Cross-scope pairs       : none")
    groups = manifest["groups"]
    assert isinstance(groups, list)
    for group in groups:
        assert isinstance(group, dict)
        codes = group["configuration_codes"]
        assert isinstance(codes, list)
        print(
            f"- {group['scope']} | {group['status']} | "
            f"configurations={len(codes)} | "
            f"pairs={group['pair_count']} | "
            f"differences={group['total_differences']}"
        )
    print(f"Manifest               : {manifest_path(output)}")


def main(
    argv: Sequence[str] | None = None,
    repository: Path | None = None,
) -> int:
    arguments = parse_args(argv)
    selected_repository = (
        repository if repository is not None else repository_root()
    )
    try:
        manifest = create_bundle(
            selected_repository,
            arguments.output_directory,
            direct_codes=arguments.configuration_code,
            shortlist_paths=arguments.shortlist_json,
        )
        _print_summary(manifest, arguments.output_directory)
    except (BundleError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
