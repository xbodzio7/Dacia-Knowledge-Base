import json
from pathlib import Path

PATH = Path("data/reporting/catalogue_gap_002_exact_colour_capture_20260923_batch_015.json")


def test_batch_015_exact_state():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    assert data["gap_id"] == "CAT-GAP-002"
    assert data["capture_method"].startswith("official_dacia_configurator")
    obs = data["observations"]
    assert len(obs) == 1
    item = obs[0]
    assert item["configuration_code"] == "duster_iii_extreme_ecog120_manual"
    assert item["model"] == "duster"
    assert item["grade"] == "extreme"
    assert item["powertrain"] == "Eco-G 120"
    assert item["transmission"] == "manual"
    assert item["drive_type"] == "4x2"
    assert item["observed_total_price_pln"] == 96000
    assert item["selected_colour"] == "biel alpejska"
    assert item["visible_colour_count"] == 7
    assert [x["name"] for x in item["colours"]] == [
        "biel alpejska",
        "szary schiste",
        "brązowy terracotta",
        "khaki lichen",
        "czarna perła",
        "sandstone",
        "zielony cedar",
    ]
    assert all(x["price_pln"] is None for x in item["colours"])
