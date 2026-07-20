#!/usr/bin/env python3
"""Verify one extracted data-product workspace fully offline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.data_product_workspace_verify import (
    WorkspaceVerificationError,
    render_json,
    verify_workspace,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify canonical release assets, extracted contents and the "
            "deterministic local index without network access or file changes."
        )
    )
    parser.add_argument(
        "--workspace-directory",
        type=Path,
        required=True,
        help="Existing workspace created by data-product-release-download.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a deterministic JSON report instead of the human summary.",
    )
    return parser.parse_args(argv)


def _print_summary(report: dict[str, object]) -> None:
    print("Verified local data product workspace")
    print("-------------------------------------")
    print(f"Version                 : {report['release_version']}")
    print(f"Tag                     : {report['release_tag']}")
    print(f"Repository commit       : {report['repository_commit']}")
    print(f"Snapshot date           : {report['snapshot_date']}")
    print(f"Canonical assets        : {report['asset_count']}")
    print(f"Extracted content files : {report['content_file_count']}")
    print(f"Selected configurations : {report['selected_configuration_count']}")
    print(f"Independent scopes      : {report['scope_group_count']}")
    print(f"Local index links       : {report['index_local_link_count']}")
    print(f"Index SHA-256           : {report['index_sha256']}")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        report = verify_workspace(arguments.workspace_directory)
    except (WorkspaceVerificationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if arguments.json:
        print(render_json(report), end="")
    else:
        _print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
