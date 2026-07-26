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
    payload = review.load_json(review.REPORT)
    inventory = review.repository_inventory()
    review.ensure(
        len(inventory["configurations"]) == 72,
        "active configuration count differs",
    )
    review.ensure(inventory["scope_count"] == 19, "scope count differs")
    review.ensure(
        inventory["pair_count"] == 114,
        "within-scope pair count differs",
    )
    review.ensure(
        inventory["technical_facets"] == 124,
        "technical facet count differs",
    )
    review.ensure(
        inventory["equipment_facets"] == 110,
        "equipment facet count differs",
    )
    review.ensure(
        inventory["price_recorded_count"] == 72,
        "price coverage differs",
    )
    review.verify_report(payload, inventory)

    state = review.load_json(review.STATE)
    review.ensure(
        isinstance(state.get("phase"), str) and bool(state["phase"]),
        "project phase is missing",
    )
    current = state.get("current_package")
    review.ensure(isinstance(current, dict), "current package is missing")
    review.ensure(
        isinstance(current.get("name"), str) and bool(current["name"]),
        "current package name is missing",
    )
    review.ensure(
        current.get("status") in {"planned", "active", "blocked", "complete"},
        "current package status differs",
    )
    next_package = state.get("next_package")
    review.ensure(isinstance(next_package, dict), "next package is missing")
    review.ensure(
        isinstance(next_package.get("name"), str) and bool(next_package["name"]),
        "next package name is missing",
    )
    baseline = state.get("baseline", {})
    review.ensure(baseline.get("tests", 0) >= 979, "test baseline regressed")
    review.ensure(baseline.get("rows", 0) >= 9688, "master row baseline regressed")
    review.ensure(
        baseline.get("configuration_values", 0) >= 2949,
        "configuration values regressed",
    )
    review.ensure(
        baseline.get("configuration_value_ranges", 0) >= 244,
        "configuration ranges regressed",
    )
    review.ensure(baseline.get("attributes", 0) >= 385, "attribute baseline regressed")


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
