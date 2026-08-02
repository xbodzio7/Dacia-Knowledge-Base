import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(path):
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

def test_charging_cable_attributes_are_semantically_separate_booleans():
    attributes = {row["code"]: row for row in rows("data/master/attributes.csv")}
    assert attributes["type2_charging_cable_supplied"]["data_type"] == "boolean"
    assert attributes["domestic_socket_charging_cable"]["data_type"] == "boolean"
    assert "connector" not in attributes["type2_charging_cable_supplied"]["code"]

def test_spring_cable_availability_respects_evidence_boundary():
    availability = rows("data/master/configuration_attribute_availability.csv")
    selected = {(r["configuration_code"], r["attribute_code"]): r for r in availability if r["attribute_code"] in {"type2_charging_cable_supplied", "domestic_socket_charging_cable"}}
    for cfg in {"cfg_spring_essential_electric_70", "cfg_spring_expression_electric_70", "cfg_spring_extreme_electric_100"}:
        assert selected[(cfg, "type2_charging_cable_supplied")]["availability_status"] == "standard"
    for cfg in {"cfg_spring_essential_electric_70", "cfg_spring_extreme_electric_100"}:
        row = selected[(cfg, "domestic_socket_charging_cable")]
        assert row["availability_status"] == "optional"
        assert "1500 PLN" in row["notes"]
    assert ("cfg_spring_expression_electric_70", "domestic_socket_charging_cable") not in selected

def test_every_new_availability_record_has_artifact_provenance():
    availability = [r for r in rows("data/master/configuration_attribute_availability.csv") if r["attribute_code"] in {"type2_charging_cable_supplied", "domestic_socket_charging_cable"}]
    sources = {r["code"]: r for r in rows("data/imports/configuration_attribute_availability_sources.csv")}
    links = {r["availability_code"]: r for r in rows("data/imports/configuration_attribute_availability_source_links.csv")}
    assert len(availability) == 5
    for row in availability:
        link = links[row["code"]]
        assert sources[link["availability_source_code"]]["source_artifact_id"].startswith("src_spring_")
