#!/usr/bin/env python3
"""Download, verify and extract one immutable public data-product release."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reporting.data_product_release_download import (
    ReleaseDownloadError,
    download_release,
)
from reporting.data_product_release_model import ReleaseError


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download, verify and safely extract one explicit immutable "
            "Dacia Knowledge Base data-product release."
        )
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Normalized immutable release version MAJOR.MINOR.PATCH.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        required=True,
        help="Create this new or empty local consumer workspace.",
    )
    return parser.parse_args(argv)


def _print_summary(result: dict[str, object], output: Path) -> None:
    raw_entry_points = result["entry_points"]
    assert isinstance(raw_entry_points, dict)
    print("Verified data product release download")
    print("--------------------------------------")
    print(f"Version                 : {result['release_version']}")
    print(f"Tag                     : {result['release_tag']}")
    print(f"Repository commit       : {result['repository_commit']}")
    print(
        "Selected configurations : "
        f"{result['selected_configuration_count']}"
    )
    print(f"Independent scopes      : {result['scope_group_count']}")
    print(f"Assets                  : {output / str(result['assets_directory'])}")
    print(f"Contents                : {output / str(result['contents_directory'])}")
    labels = {
        "shortlist_html": "Shortlist HTML",
        "comparison_workbook": "Comparison workbook",
        "comparison_bundle_manifest": "Bundle manifest",
        "release_notes": "Release notes",
    }
    for key in (
        "shortlist_html",
        "comparison_workbook",
        "comparison_bundle_manifest",
        "release_notes",
    ):
        print(
            f"{labels[key]:<24}: "
            f"{output / str(raw_entry_points[key])}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        result = download_release(
            arguments.version,
            arguments.output_directory,
        )
        _print_summary(result, arguments.output_directory)
    except (ReleaseDownloadError, ReleaseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
