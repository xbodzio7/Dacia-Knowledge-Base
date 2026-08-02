#!/usr/bin/env python3
"""Verify the bounded official-configurator coverage reconciliation package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "project/sources/dacia-pl-official-configurator-coverage-20260802.json"
REPORT = ROOT / "data/reporting/official_configurator_coverage_reconciliation.json"
SOURCES = ROOT / "data/master/sources.csv"
STATE = ROOT / "project/state.json"
CODE = "src_pl_dacia_official_configurator_coverage_20260802"


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def verify(root: Path = ROOT) -> None:
    source_path = root / SOURCE.relative_to(ROOT)
    report = read_json(root / REPORT.relative_to(ROOT))
    source = read_json(source_path)

    if source["source_code"] != CODE:
        raise RuntimeError("configurator coverage source code drifted")
    if source["active_model_families"] != 6 or source["primary_configurator_surfaces"] != 7:
        raise RuntimeError("configurator coverage counts drifted")
    if len(source["model_surfaces"]) != 7:
        raise RuntimeError("configurator surface inventory drifted")
    if source["coverage_reconciliation"]["master_data_mutation_authorized"] is not False:
        raise RuntimeError("coverage package must remain registration-only")

    actual_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
    with (root / SOURCES.relative_to(ROOT)).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    matches = [row for row in rows if row["code"] == CODE]
    if len(matches) != 1:
        raise RuntimeError("configurator coverage source must be registered exactly once")
    if matches[0]["id"] != "35" or matches[0]["sha256"] != actual_sha or matches[0]["status"] != "active":
        raise RuntimeError("configurator coverage source registration drifted")
    if report["source_registration"]["snapshot_sha256"] != actual_sha:
        raise RuntimeError("coverage report hash drifted")

    expected_delta = {
        "source_rows_added": 1,
        "other_master_rows_added": 0,
        "configuration_values_changed": 0,
        "availability_rows_changed": 0,
        "commercial_mappings_changed": 0,
        "attributes_added": 0,
        "net_master_row_increase": 1,
    }
    if report["master_data_delta"] != expected_delta:
        raise RuntimeError("coverage package data boundary drifted")

    state = read_json(root / STATE.relative_to(ROOT))
    if state["current_package"]["package_id"] != "official_configurator_coverage_reconciliation_001":
        raise RuntimeError("canonical state did not advance to configurator coverage")
    if state["next_package"]["package_id"] != "official_configurator_exact_state_capture_001":
        raise RuntimeError("unexpected next configurator package")
    if state["baseline"]["rows"] != 11715 or state["baseline"]["configuration_values"] != 3567:
        raise RuntimeError("canonical baseline counts drifted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not args.verify:
        parser.error("--verify is required")
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
