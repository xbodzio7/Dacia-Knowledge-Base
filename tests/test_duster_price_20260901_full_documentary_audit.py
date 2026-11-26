import csv
from pathlib import Path

SRC = "src_pl_duster_price_my26_20260901"
SOURCE_URL = "https://cdn.group.renault.com/dac/pl/pdf/cenniki/duster-price.pdf.asset.pdf/46301fd879.pdf"


def rows(path):
    return list(csv.DictReader(Path(path).open(encoding="utf-8", newline="")))


sources = [r for r in rows("data/master/sources.csv") if r["code"] == SRC]
assert len(sources) == 1
assert sources[0]["external_reference"] == SOURCE_URL


prices = [r for r in rows("data/master/configuration_prices.csv") if r["source_code"] == SRC]
assert len(prices) == 16
assert len({r["configuration_code"] for r in prices}) == 16


availability = [
    r for r in rows("data/master/configuration_attribute_availability.csv")
    if r["source_code"] == SRC
]
assert len(availability) == 1152
assert len({(r["configuration_code"], r["attribute_code"]) for r in availability}) == 1152


values = [r for r in rows("data/master/configuration_attribute_values.csv") if r["source_code"] == SRC]

hybrid_system = [
    r for r in values
    if r["attribute_code"] == "hybrid_system_type"
]
assert len(hybrid_system) == 9
assert {r["value"] for r in hybrid_system} == {"mhev", "hev"}

engine_types = [
    r for r in values
    if r["attribute_code"] == "engine_type"
]
assert "mild_hybrid" not in {r["value"] for r in engine_types}
assert "full_hybrid" not in {r["value"] for r in engine_types}
assert {"mhev", "hev"} <= {r["value"] for r in engine_types}


conflict = [
    r for r in values
    if r["configuration_code"] == "duster_iii_expression_hybrid155_4x2_automatic"
    and r["attribute_code"] in {"hybrid_battery_voltage", "hybrid_system_voltage"}
]
assert {(r["attribute_code"], r["value"]) for r in conflict} == {
    ("hybrid_battery_voltage", "260"),
    ("hybrid_system_voltage", "230"),
}
assert len(conflict) == 2


ranges = [
    r for r in rows("data/master/configuration_attribute_value_ranges.csv")
    if r["source_code"] == SRC
]
assert len(ranges) == 16
