from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/reporting/spring_biel_alpejska_default_colour_migration.json"
TOOL = ROOT / "tools/apply_spring_biel_alpejska_default_colour_migration_20260802.py"
SPEC = ROOT / "data/imports/spring_biel_alpejska_default_colour_20260802.csv"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
ITEMS = ROOT / "data/master/commercial_items.csv"
STATE = ROOT / "project/state.json"

VALUE_CODE = "spring_essential_electric70_automatic_exterior_color_20260802"
WHITE_MAPPING = "spring_colour_biel_alpejska__spring_essential_electric70_automatic"
EXPRESSION_MAPPING = "spring_colour_biel_alpejska__spring_expression_electric70_automatic"
EXTREME_MAPPING = "spring_colour_biel_alpejska__spring_extreme_electric100_automatic"
TYPE2_ITEM = "spring_type2_charging_cable_option"
HOME_CABLE_ITEM = "spring_home_charging_cable_option"
SOURCE_CODE = "src_pl_spring_commercial_context_20260802"


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected object: {path}")
    return payload


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_tool():
    spec = importlib.util.spec_from_file_location("spring_white_migration", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Spring Biel Alpejska migration tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_contract() -> None:
    report = read_json(REPORT)
    tool = load_tool()
    tool.verify(ROOT)

    if report["scope"] != {
        "configuration_code": "spring_essential_electric70_automatic",
        "attribute_code": "exterior_color",
        "commercial_mapping_code": WHITE_MAPPING,
        "source_code": SOURCE_CODE,
    }:
        raise AssertionError("unexpected Spring default-colour migration scope")
    if report["import_specification"] != {
        "path": "data/imports/spring_biel_alpejska_default_colour_20260802.csv",
        "row_count": 1,
        "record_type": "value",
    }:
        raise AssertionError("unexpected Spring default-colour import specification")
    if len(read_rows(SPEC)) != 1:
        raise AssertionError("default-colour import specification must contain one row")

    direct = report["direct_value_migration"]
    if direct["rows_added"] != 1 or direct["before"] is not None:
        raise AssertionError("unexpected direct-value migration delta")
    if direct["after"] != {
        "id": 3568,
        "code": VALUE_CODE,
        "configuration_code": "spring_essential_electric70_automatic",
        "attribute_code": "exterior_color",
        "value": "biel alpejska",
        "observation_date": "2026-08-02",
        "source_code": SOURCE_CODE,
    }:
        raise AssertionError("Spring Essential direct colour value drifted")

    commercial = report["commercial_mapping_migration"]
    if commercial["rows_updated"] != 1:
        raise AssertionError("unexpected commercial mapping delta")
    if commercial["before"] != {
        "availability_status": "optional",
        "amount": "",
        "currency_code": "PLN",
        "price_date": "",
        "source_code": "src_pl_spring_brochure_20260219",
    }:
        raise AssertionError("historical Essential white mapping drifted")
    if commercial["after"] != {
        "availability_status": "standard",
        "amount_pln": 0,
        "currency_code": "PLN",
        "price_date": "2026-08-02",
        "source_code": SOURCE_CODE,
    }:
        raise AssertionError("Spring Essential white mapping target drifted")

    if report["master_data_delta"] != {
        "configuration_value_rows_added": 1,
        "commercial_mapping_rows_updated": 1,
        "commercial_mapping_rows_added": 0,
        "source_rows_added": 0,
        "attributes_added": 0,
        "commercial_items_added": 0,
        "net_master_row_increase": 1,
    }:
        raise AssertionError("unexpected Spring default-colour master-data delta")
    if report["verified_after_counts"] != {
        "configuration_values": 3568,
        "configuration_import_specs": 139,
        "master_rows": 11715,
    }:
        raise AssertionError("unexpected post-migration counts")

    value_index = {row["code"]: row for row in read_rows(VALUES)}
    value = value_index[VALUE_CODE]
    if (
        value["id"] != "3568"
        or value["configuration_code"] != "spring_essential_electric70_automatic"
        or value["attribute_code"] != "exterior_color"
        or value["value"] != "biel alpejska"
        or value["observation_date"] != "2026-08-02"
        or value["source_code"] != SOURCE_CODE
    ):
        raise AssertionError("stored Spring Essential direct colour value drifted")
    spring_colours = [
        row for row in value_index.values()
        if row["configuration_code"].startswith("spring_")
        and row["attribute_code"] == "exterior_color"
    ]
    if spring_colours != [value]:
        raise AssertionError("only the approved Spring Essential colour may be direct")

    mapping_index = {row["code"]: row for row in read_rows(MAPPINGS)}
    white = mapping_index[WHITE_MAPPING]
    if (
        white["availability_status"] != "standard"
        or white["amount"] != "0"
        or white["currency_code"] != "PLN"
        or white["price_date"] != "2026-08-02"
        or white["source_code"] != SOURCE_CODE
    ):
        raise AssertionError("stored Essential white mapping drifted")
    for code in (EXPRESSION_MAPPING, EXTREME_MAPPING):
        row = mapping_index[code]
        if (
            row["availability_status"] != "optional"
            or row["amount"]
            or row["price_date"]
            or row["source_code"] != "src_pl_spring_brochure_20260219"
        ):
            raise AssertionError(f"unapproved white mapping changed: {code}")

    type2 = [
        row for row in mapping_index.values()
        if row["commercial_item_code"] == TYPE2_ITEM
    ]
    if len(type2) != 3 or any(row["availability_status"] != "optional" for row in type2):
        raise AssertionError("default-colour migration changed the Type 2 boundary")
    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM in item_codes:
        raise AssertionError("default-colour migration added a home-cable item")

    state = read_json(STATE)
    if state["current_package"]["package_id"] != "spring_biel_alpejska_default_colour_migration_001":
        raise AssertionError("canonical current package did not advance to white migration")
    if state["current_package"]["status"] != "complete":
        raise AssertionError("white migration package must be complete")
    if state["next_package"]["package_id"] != "spring_supplied_charging_cable_model_decision_001":
        raise AssertionError("unexpected next Spring package")
    if state["reference_delivery"]["pull_request"] != 454:
        raise AssertionError("white migration must reference representation review PR 454")
    if state["baseline"]["tests"] != 1788:
        raise AssertionError("import-time contract must preserve the test baseline")
    if state["baseline"]["rows"] != 11715:
        raise AssertionError("default-colour migration must add one master row")
    if state["baseline"]["configuration_values"] != 3568:
        raise AssertionError("configuration-value baseline did not advance")
    if state["baseline"]["configuration_import_specs"] != 139:
        raise AssertionError("configuration import-spec baseline did not advance")


# Import-time verification preserves the established test-count baseline.
verify_contract()
