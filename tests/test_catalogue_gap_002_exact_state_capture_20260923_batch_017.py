import json
from pathlib import Path

PATH = Path("data/reporting/catalogue_gap_002_exact_state_capture_20260923_batch_017.json")


def test_batch_017_exact_state_capture():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    assert data["gap_id"] == "CAT-GAP-002"
    assert data["capture_method"].startswith("official_dacia_configurator")
    obs = data["observations"]
    assert len(obs) == 7

    expected = {
        "duster_iii_expression_ecog120_automatic": (True, 96900, 7),
        "sandero_iii_journey_tce100_manual": (False, 73600, 7),
        "bigster_extreme_mildhybridg140_manual": (True, 118900, 5),
        "bigster_journey_mildhybridg140_manual": (True, 118500, 5),
        "jogger_essential_7seat_ecog120_manual": (False, 82400, 3),
        "jogger_expression_5seat_tce110_manual": (False, 84050, 7),
        "jogger_expression_5seat_ecog120_manual": (False, 82050, 7),
    }
    for item in obs:
        code = item["configuration_code"]
        assert code in expected
        is_new, price, colour_count = expected[code]
        assert item["new_exact_surface"] is is_new
        assert item["observed_total_price_pln"] == price
        assert item["visible_colour_count"] == colour_count
        assert item["selected_colour"] == "biel alpejska"
        assert len(item["colours"]) == colour_count
        assert all(c["price_pln"] is None for c in item["colours"])

    assert sum(1 for x in obs if x["new_exact_surface"]) == 3
    assert sum(1 for x in obs if not x["new_exact_surface"]) == 4

    duster = next(x for x in obs if x["configuration_code"] == "duster_iii_expression_ecog120_automatic")
    assert duster["technical_observations"]["co2_wltp_mixed_g_km"] == 140
    assert duster["technical_observations"]["fuel_consumption_wltp_mixed_l_100km"] == 6.2
    assert duster["technical_observations"]["co2_wltp_mixed_lpg_g_km"] == 123
    assert duster["technical_observations"]["fuel_consumption_wltp_mixed_lpg_l_100km"] == 7.6
