#!/usr/bin/env python3
"""
Normalize Dacia Knowledge Base CSV files to UTF-8.

By default, the script only reports files that require conversion.
Use --apply to convert Windows-1250 CSV files to UTF-8.

Files that are already valid UTF-8 are never rewritten.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence


SOURCE_ENCODING = "cp1250"
TARGET_ENCODING = "utf-8"


class EncodingNormalizationError(RuntimeError):
    """Raised when a CSV file cannot be normalized safely."""


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def discover_csv_files(root: Path) -> list[Path]:
    data_dir = root / "data"

    if not data_dir.is_dir():
        raise EncodingNormalizationError(
            f"data directory does not exist: {data_dir}"
        )

    return sorted(data_dir.rglob("*.csv"))


def detect_encoding(path: Path) -> str:
    raw_data = path.read_bytes()

    try:
        raw_data.decode(TARGET_ENCODING)
        return TARGET_ENCODING
    except UnicodeDecodeError:
        pass

    try:
        raw_data.decode(SOURCE_ENCODING)
        return SOURCE_ENCODING
    except UnicodeDecodeError as exc:
        raise EncodingNormalizationError(
            f"{path}: file is neither UTF-8 nor Windows-1250"
        ) from exc


def convert_to_utf8(path: Path) -> None:
    raw_data = path.read_bytes()

    try:
        text = raw_data.decode(SOURCE_ENCODING)
    except UnicodeDecodeError as exc:
        raise EncodingNormalizationError(
            f"{path}: cannot decode as Windows-1250"
        ) from exc

    temporary_path = path.with_name(f"{path.name}.encoding.tmp")

    try:
        temporary_path.write_text(
            text,
            encoding=TARGET_ENCODING,
            newline="",
        )
        temporary_path.replace(path)
    except OSError as exc:
        temporary_path.unlink(missing_ok=True)
        raise EncodingNormalizationError(
            f"{path}: cannot write normalized file: {exc}"
        ) from exc


def normalize_csv_files(root: Path, apply: bool = False) -> int:
    csv_files = discover_csv_files(root)

    if not csv_files:
        print("No CSV files found.")
        return 0

    utf8_files = 0
    conversion_candidates: list[Path] = []
    failures: list[str] = []

    for csv_file in csv_files:
        try:
            encoding = detect_encoding(csv_file)
        except (EncodingNormalizationError, OSError) as exc:
            failures.append(str(exc))
            continue

        if encoding == TARGET_ENCODING:
            utf8_files += 1
        else:
            conversion_candidates.append(csv_file)

    print(f"CSV files checked : {len(csv_files)}")
    print(f"Already UTF-8     : {utf8_files}")
    print(f"Windows-1250      : {len(conversion_candidates)}")
    print(f"Unreadable        : {len(failures)}")

    if conversion_candidates:
        print("\nFiles requiring conversion:")

        for path in conversion_candidates:
            print(f"  {path.relative_to(root)}")

    if failures:
        print("\nFiles requiring manual review:", file=sys.stderr)

        for failure in failures:
            print(f"  {failure}", file=sys.stderr)

        return 1

    if not apply:
        if conversion_candidates:
            print("\nDry run only. Run again with --apply to convert files.")
        else:
            print("\nAll CSV files are already valid UTF-8.")

        return 0

    converted = 0

    for csv_file in conversion_candidates:
        try:
            convert_to_utf8(csv_file)
        except (EncodingNormalizationError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

        converted += 1
        print(f"Converted: {csv_file.relative_to(root)}")

    print(f"\nConverted {converted} file(s) to UTF-8.")
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize DKB CSV files from Windows-1250 to UTF-8."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Convert detected Windows-1250 files. Default is dry-run.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        return normalize_csv_files(repository_root(), apply=args.apply)
    except EncodingNormalizationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
