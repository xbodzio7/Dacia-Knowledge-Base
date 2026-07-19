#!/usr/bin/env python3
"""Build or verify deterministic versioned data-product release assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.data_product_release import (
    create_release_assets,
    repository_root,
)
from reporting.data_product_release_model import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    ReleaseError,
    verify_release_assets,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build one deterministic offline data-product release archive, "
            "manifest and checksum file."
        )
    )
    parser.add_argument(
        "--version",
        help="Normalized semantic release version MAJOR.MINOR.PATCH.",
    )
    parser.add_argument(
        "--commit-sha",
        help="Exact 40-character lowercase repository commit SHA.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        required=True,
        help="Build into a new or empty directory, or verify this directory.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing release assets without rebuilding them.",
    )
    return parser.parse_args(argv)


def _print_summary(manifest: dict[str, object], output: Path) -> None:
    archive = manifest["archive"]
    assert isinstance(archive, dict)
    print("Versioned data product release")
    print("------------------------------")
    print(f"Version                 : {manifest['release_version']}")
    print(f"Tag                     : {manifest['release_tag']}")
    print(f"Repository commit       : {manifest['repository_commit']}")
    print(
        "Selected configurations : "
        f"{manifest['selected_configuration_count']}"
    )
    print(f"Independent scopes      : {manifest['scope_group_count']}")
    print(f"Archive                 : {output / str(archive['path'])}")
    print(f"Manifest                : {output / MANIFEST_NAME}")
    print(f"Checksums               : {output / CHECKSUMS_NAME}")


def main(
    argv: Sequence[str] | None = None,
    repository: Path | None = None,
) -> int:
    arguments = parse_args(argv)
    selected_repository = (
        repository if repository is not None else repository_root()
    )
    try:
        if arguments.verify:
            manifest = verify_release_assets(arguments.output_directory)
            if (
                arguments.version is not None
                and manifest["release_version"] != arguments.version
            ):
                raise ReleaseError(
                    "verified release version does not match --version"
                )
            if (
                arguments.commit_sha is not None
                and manifest["repository_commit"] != arguments.commit_sha
            ):
                raise ReleaseError(
                    "verified repository commit does not match --commit-sha"
                )
        else:
            if arguments.version is None or arguments.commit_sha is None:
                raise ReleaseError(
                    "--version and --commit-sha are required when building"
                )
            manifest = create_release_assets(
                selected_repository,
                arguments.output_directory,
                arguments.version,
                arguments.commit_sha,
            )
        _print_summary(manifest, arguments.output_directory)
    except (ReleaseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
