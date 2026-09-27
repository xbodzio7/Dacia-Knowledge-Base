import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def test_bigster_september_2026_price_list_delta():
    cfg = rows(ROOT / "data/master/configurations.csv")
    prices = rows(ROOT / "data/master/configuration_prices.csv")
    av = rows(ROOT / "data/master/configuration_attribute_availability.csv")
    vals = rows(ROOT / "data/master/configuration_attribute_values.csv")
    sources = rows(ROOT / "data/master/sources.csv")
    source = "src_pl_bigster_price_my26_20260901"
    new_cfgs = {
        "bigster_expression_mildhybridg140_4x2_automatic": 115600,
        "bigster_extreme_mildhybridg140_4x2_automatic": 124100,
        "bigster_journey_mildhybridg140_4x2_automatic": 123700,
    }
    assert {r["configuration_code"] for r in cfg if r["configuration_code"] in new_cfgs} == set(new_cfgs)
    p = {r["configuration_code"]: r for r in prices if r["source_code"] == source}
    for code, amount in new_cfgs.items():
        assert code in p and int(p[code]["amount"]) == amount
    assert any(r["code"] == source and r["document_date"] == "2026-09-01" for r in sources)
    for code in new_cfgs:
        assert sum(1 for r in av if r["configuration_code"] == code and r["source_code"] == source) > 50
        assert any(r["configuration_code"] == code and r["attribute_code"] == "gearbox_type" and r["value"] == "automatic" and r["source_code"] == source for r in vals)
        assert any(r["configuration_code"] == code and r["attribute_code"] == "fuel_consumption_combined" and r["fuel_type_code"] == "lpg" and r["value"] == "7.3" and r["source_code"] == source for r in vals)
