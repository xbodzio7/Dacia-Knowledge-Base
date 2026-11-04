from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "duster_mini_equipment_page21_22_gap_import_20261104_001"
SPEC_PATH = ROOT / "data/imports/configuration_attribute_availability/duster_mini_equipment_page21_22_20251020.json"
MASTER_PATH = ROOT / "data/master/configuration_attribute_availability.csv"
SOURCES_PATH = ROOT / "data/master/sources.csv"
SOURCE_CONFIGS_PATH = ROOT / "data/master/source_configurations.csv"
EXPECTED_SOURCE = "src_pl_duster_mini_brochure_20251020"


def test_duster_mini_page_21_22_gap_import_matches_master_and_registered_source() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    with SOURCES_PATH.open(encoding="utf-8-sig", newline="") as handle:
        sources = {row["code"]: row for row in csv.DictReader(handle)}
    source = sources[EXPECTED_SOURCE]
    assert source["sha256"] == spec["source"]["sha256"]
    assert source["external_reference"] == spec["source"]["url"]
    assert source["document_date"] == "2025-10-20"

    with MASTER_PATH.open(encoding="utf-8-sig", newline="") as handle:
        master = {row["code"]: row for row in csv.DictReader(handle)}
    records = spec["records"]
    assert len(records) == 12
    assert [row["id"] for row in records] == list(range(10101, 10113))
    assert len({(row["configuration_code"], row["attribute_code"]) for row in records}) == 12
    for row in records:
        assert row["code"] in master
        assert all(master[row["code"]][key] == str(row[key]) for key in (
            "id", "configuration_code", "attribute_code", "availability_status",
            "observation_date", "source_code",
        ))
    with SOURCE_CONFIGS_PATH.open(encoding="utf-8-sig", newline="") as handle:
        source_configs = {(row["source_code"], row["configuration_code"]) for row in csv.DictReader(handle)}
    assert all((EXPECTED_SOURCE, row["configuration_code"]) in source_configs for row in records)
    camera = [row for row in records if row["attribute_code"] == "360_camera_system"]
    seats = [row for row in records if row["attribute_code"] == "passenger_seat_height_adjustment"]
    assert [row["availability_status"] for row in camera].count("not_available") == 5
    assert [row["availability_status"] for row in camera].count("optional") == 4
    assert [row["availability_status"] for row in seats].count("optional") == 2
    assert [row["availability_status"] for row in seats].count("standard") == 1
