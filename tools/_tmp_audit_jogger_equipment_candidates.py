from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
CANDIDATES = (
    "led_daytime_running_lights",
    "led_headlights",
    "automatic_headlights",
    "anti_lock_braking_system",
    "automatic_emergency_braking",
    "electronic_stability_control",
    "hill_start_assist",
    "extended_grip",
    "lane_departure_warning",
    "lane_keep_assist",
    "driver_attention_monitoring",
    "traffic_sign_recognition",
    "blind_spot_monitoring",
    "emergency_call_ecall",
    "driver_front_airbag",
    "passenger_front_airbag",
    "front_side_airbags",
    "curtain_airbags",
    "front_seat_belt_pretensioners",
    "rear_seat_belt_pretensioners",
    "isofix_rear",
    "tyre_pressure_monitoring_system",
    "tyre_repair_kit",
    "fog_lights",
    "side_mirrors_electric_adjustment",
    "start_stop_system",
    "onboard_computer",
    "instrument_cluster_tft_3_5",
    "instrument_cluster_colour_7",
    "speed_limiter",
    "cruise_control",
    "rear_parking_sensors",
    "front_parking_sensors",
    "rear_view_camera",
    "360_camera_system",
    "electronic_parking_brake",
    "front_windows_power",
    "rear_windows_power",
    "central_locking",
    "keyless_entry",
    "manual_air_conditioning",
    "automatic_climate_control",
    "front_centre_armrest",
    "steering_wheel_height_adjustment",
    "steering_wheel_reach_adjustment",
    "driver_seat_height_adjustment",
    "heated_front_seats",
    "media_control_system",
    "media_display_system",
    "navigation_system",
    "heated_steering_wheel",
    "side_mirrors_folding",
    "side_mirrors_heated",
    "high_beam_assist",
)


def read(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


attributes = {row["code"]: row for row in read("attributes.csv")}
missing = [code for code in CANDIDATES if code not in attributes]
wrong_contract = [
    f"{code}:{attributes[code]['data_type']}:{attributes[code]['status']}"
    for code in CANDIDATES
    if code in attributes and (attributes[code]["data_type"] != "boolean" or attributes[code]["status"] != "active")
]
configurations = [
    row["code"] for row in read("configurations.csv")
    if row["code"].startswith("jogger_") and row["status"] == "active"
]
configuration_set = set(configurations)
scalar_overlaps = sorted({
    row["attribute_code"]
    for row in read("configuration_attribute_values.csv")
    if row["configuration_code"] in configuration_set and row["attribute_code"] in CANDIDATES
})
availability_overlaps = sorted({
    row["attribute_code"]
    for row in read("configuration_attribute_availability.csv")
    if row["configuration_code"] in configuration_set and row["attribute_code"] in CANDIDATES
})

lines = [
    f"candidate_attributes={len(CANDIDATES)}",
    f"active_jogger_configurations={len(configurations)}",
    f"candidate_records={len(CANDIDATES) * len(configurations)}",
    f"missing_attributes={','.join(missing) or '-'}",
    f"wrong_contract={','.join(wrong_contract) or '-'}",
    f"scalar_overlap_count={len(scalar_overlaps)}",
    f"scalar_overlaps={','.join(scalar_overlaps) or '-'}",
    f"availability_overlap_count={len(availability_overlaps)}",
    f"availability_overlaps={','.join(availability_overlaps) or '-'}",
    "candidate_codes:",
    *CANDIDATES,
]
output = ROOT / "project" / "audits" / "jogger-equipment-candidate-audit.txt"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("\n".join(lines) + "\n", encoding="utf-8")

if missing or wrong_contract or len(configurations) != 22 or availability_overlaps:
    raise SystemExit(1)
