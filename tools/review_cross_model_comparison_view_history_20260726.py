#!/usr/bin/env python3
"""Verify the completed cross-model review after later project phases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import review_cross_model_comparison_view_20260726 as review  # noqa: E402


def verify() -> None:
    review.verify()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the historical contract.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    try:
        verify()
    except (OSError, json.JSONDecodeError, review.ReviewError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: cross-model comparison view historical contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
