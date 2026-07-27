#!/usr/bin/env python3
"""Apply or verify the source-bounded Sandero and Stepway catalogue completion."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable, Mapping, Sequence

OBSERVATION_DATE = "2026-07-03"
BROCHURE_DATE = "2026-02-02"
RAW_PRICE_SOURCE = "src_pl_sandero_stepway_price_my26_20260703"
RAW_SANDERO_BROCHURE_SOURCE = "src_pl_sandero_brochure_20260202"
RAW_STEPWAY_BROCHURE_SOURCE = "src_pl_sandero_stepway_brochure_20260202"
PRICE_SOURCE = "src_pl_sandero_stepway_catalog_tce_slice_20260703"
SANDERO_BROCHURE_SOURCE = "src_pl_sandero_catalog_tce_slice_20260202"
STEPWAY_BROCHURE_SOURCE = "src_pl_sandero_stepway_catalog_tce_slice_20260202"

SANDERO_ESSENTIAL_VERSION = {
    "code": "sandero_iii_essential",
    "model_code": "sandero_iii",
    "name": "Essential",
    "status": "active",
    "notes": "Source-backed trim from the official Polish Sandero MY26 price matrix effective 2026-07-03.",
}

CONFIGURATIONS = (
    {
        "code": "sandero_iii_essential_tce100_manual",
        "version_code": "sandero_iii_essential",
        "powertrain_label": "TCe 100",
        "transmission_type": "manual",
        "status": "active",
        "notes": "Official Polish MY26 catalogue effective 2026-07-03 lists Sandero Essential TCe 100 with a six-speed manual gearbox.",
        "model_family": "sandero",
        "grade": "essential",
        "price": "63900",
    },
    {
        "code": "sandero_iii_expression_tce100_manual",
        "version_code": "sandero_iii_expression",
        "powertrain_label": "TCe 100",
        "transmission_type": "manual",
        "status": "active",
        "notes": "Official Polish MY26 catalogue effective 2026-07-03 lists Sandero Expression TCe 100 with a six-speed manual gearbox.",
        "model_family": "sandero",
        "grade": "expression",
        "price": "68000",
    },
    {
        "code": "sandero_iii_journey_tce100_manual",
        "version_code": "sandero_iii_journey",
        "powertrain_label": "TCe 100",
        "transmission_type": "manual",
        "status": "active",
        "notes": "Official Polish MY26 catalogue effective 2026-07-03 lists Sandero Journey TCe 100 with a six-speed manual gearbox.",
        "model_family": "sandero",
        "grade": "journey",
        "price": "73600",
    },
    {
        "code": "sandero_stepway_iii_essential_tce110_manual",
        "version_code": "sandero_stepway_iii_essential",
        "powertrain_label": "TCe 110",
        "transmission_type": "manual",
        "status": "active",
        "notes": "Official Polish MY26 catalogue effective 2026-07-03 lists Sandero Stepway Essential TCe 110 with a six-speed manual gearbox.",
        "model_family": "stepway",
        "grade": "essential",
        "price": "71700",
    },
    {
        "code": "sandero_stepway_iii_expression_tce110_manual",
        "version_code": "sandero_stepway_iii_expression",
        "powertrain_label": "TCe 110",
        "transmission_type": "manual",
        "status": "active",
        "notes": "Official Polish MY26 catalogue effective 2026-07-03 lists Sandero Stepway Expression TCe 110 with a six-speed manual gearbox.",
        "model_family": "stepway",
        "grade": "expression",
        "price": "76400",
    },
    {
        "code": "sandero_stepway_iii_extreme_tce110_manual",
        "version_code": "sandero_stepway_iii_extreme",
        "powertrain_label": "TCe 110",
        "transmission_type": "manual",
        "status": "active",
        "notes": "Official Polish MY26 catalogue effective 2026-07-03 lists Sandero Stepway Extreme TCe 110 with a six-speed manual gearbox.",
        "model_family": "stepway",
        "grade": "extreme",
        "price": "82500",
    },
)

EXTRA_PRICE_OBSERVATIONS = (
    ("sandero_iii_expression_ecog120_automatic", "74900"),
    ("sandero_iii_journey_ecog120_automatic", "80500"),
)

EQUIPMENT_ATTRIBUTES = (
    "roof_rails",
    "modular_roof_rails",
    "shark_fin_antenna",
    "rear_seat_folding",
    "my_safety_button",
    "anti_lock_braking_system",
    "automatic_emergency_braking",
    "electronic_stability_control",
    "hill_start_assist",
    "emergency_call_ecall",
    "alcohol_interlock_preparation",
    "traffic_sign_recognition",
    "lane_departure_warning",
    "lane_keep_assist",
    "driver_attention_monitoring",
    "rescue_code",
    "driver_front_airbag",
    "passenger_front_airbag",
    "front_side_airbags",
    "curtain_airbags",
    "cruise_control",
    "speed_limiter",
    "rear_parking_sensors",
    "front_parking_sensors",
    "rear_view_camera",
    "360_camera_system",
    "blind_spot_monitoring",
    "electronic_parking_brake",
    "tyre_pressure_monitoring_system",
    "tyre_repair_kit",
    "fog_lights",
    "side_mirrors_electric_adjustment",
    "side_mirrors_heated",
    "manual_air_conditioning",
    "automatic_climate_control",
    "automatic_headlights",
    "rain_sensing_wipers",
    "central_locking",
    "automatic_door_locking",
    "front_windows_power",
    "one_touch_windows",
    "rear_windows_power",
    "glass_sunroof",
    "steering_wheel_height_adjustment",
    "steering_wheel_reach_adjustment",
    "driver_seat_height_adjustment",
    "front_centre_armrest",
    "heated_front_seats",
    "heated_steering_wheel",
    "keyless_entry",
    "media_control_system",
    "bluetooth_connectivity",
    "onboard_computer",
    "media_display_system",
    "wireless_smartphone_replication",
    "touchscreen",
    "navigation_system",
    "wireless_charging",
    "side_mirrors_folding",
    "high_beam_assist",
    "led_headlights",
    "led_daytime_running_lights",
    "instrument_cluster_tft_3_5",
    "instrument_cluster_colour_7",
    "extended_grip",
    "adjustable_boot_floor",
    "eco_leather_steering_wheel",
    "youclip_phone_holder",
    "rear_usb_c_ports",
    "boot_compartment_lighting",
)

MATRIX_CONFIGURATIONS = (
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_iii_expression_ecog120_manual",
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_manual",
    "sandero_iii_journey_ecog120_automatic",
    "sandero_stepway_iii_essential_tce110_manual",
    "sandero_stepway_iii_expression_tce110_manual",
    "sandero_stepway_iii_extreme_tce110_manual",
    "sandero_stepway_iii_essential_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_manual",
    "sandero_stepway_iii_expression_ecog120_automatic",
    "sandero_stepway_iii_extreme_ecog120_manual",
    "sandero_stepway_iii_extreme_ecog120_automatic",
)

CARGO_OBSERVATIONS = (
    {
        "suffix": "minimum_vda_iso3832",
        "value": "328",
        "text": "Minimalna pojemność bagażnika — 328 dm3 według normy ISO 3832",
        "measurement_basis_code": "vda_iso_3832",
        "second_row_state_code": "upright",
        "compartment_code": "main_luggage_compartment",
    },
    {
        "suffix": "minimum_ordinary_litre",
        "value": "410",
        "text": "Minimalna pojemność bagażnika — 410 litrów",
        "measurement_basis_code": "ordinary_litre",
        "second_row_state_code": "upright",
        "compartment_code": "main_luggage_compartment",
    },
    {
        "suffix": "maximum_vda_iso3832",
        "value": "1108",
        "text": "Maksymalna pojemność bagażnika — 1108 dm3 według normy ISO 3832",
        "measurement_basis_code": "vda_iso_3832",
        "second_row_state_code": "folded",
        "compartment_code": "source_stated_total",
    },
    {
        "suffix": "maximum_ordinary_litre",
        "value": "1455",
        "text": "Maksymalna pojemność bagażnika — 1455 litrów",
        "measurement_basis_code": "ordinary_litre",
        "second_row_state_code": "folded",
        "compartment_code": "source_stated_total",
    },
    {
        "suffix": "underfloor_vda_iso3832",
        "value": "78",
        "text": "Pojemność schowka pod podłogą — 78 dm3 według normy ISO 3832",
        "measurement_basis_code": "vda_iso_3832",
        "second_row_state_code": "",
        "compartment_code": "underfloor_compartment",
    },
)

TRIM_VALUES = {
    ("sandero", "essential"): {
        "wheel_size": '15"',
        "wheel_material": "steel",
        "wheel_design": "ELMA",
        "wheel_finish": "stalowe",
        "upholstery_variant": "materiałowa czarna ze wstawkami denim",
    },
    ("sandero", "expression"): {
        "wheel_size": '16"',
        "wheel_material": "steel",
        "wheel_design": "ATARA",
        "wheel_finish": "stalowe",
        "upholstery_variant": "materiałowa czarna ze wstawkami denim",
    },
    ("sandero", "journey"): {
        "wheel_size": '16"',
        "wheel_material": "alloy",
        "wheel_design": "TAMIA",
        "wheel_finish": "aluminiowe",
        "upholstery_variant": "materiałowa denim",
    },
    ("stepway", "essential"): {
        "wheel_size": '16"',
        "wheel_material": "steel",
        "wheel_design": "ERELIA",
        "wheel_finish": "ciemne stalowe",
        "upholstery_variant": "materiałowa czarna z geometrycznym wzorem i pomarańczowymi przeszyciami",
    },
    ("stepway", "expression"): {
        "wheel_size": '16"',
        "wheel_material": "steel",
        "wheel_design": "ATARA",
        "wheel_finish": "stalowe",
        "upholstery_variant": "materiałowa czarna z geometrycznym wzorem i pomarańczowymi przeszyciami",
    },
    ("stepway", "extreme"): {
        "wheel_size": '16"',
        "wheel_material": "alloy",
        "wheel_design": "TAMIA",
        "wheel_finish": "czarne aluminiowe",
        "upholstery_variant": "MicroCloud z elementami Copper Brown",
    },
}

MODEL_TECHNICAL = {
    "sandero": {
        "source": SANDERO_BROCHURE_SOURCE,
        "power": "74",
        "power_rpm": "5000",
        "torque": "200",
        "torque_rpm": "2900",
        "acceleration": "9.7",
        "elasticity": (("4", "7.4"), ("5", "10.7")),
        "consumption": "5.4",
        "co2": "122",
        "minimum_kerb_weight": "1059",
        "maximum_kerb_weight": "1132",
        "gross_vehicle_weight": "1570",
        "gross_train_weight": "2550",
        "braked_trailer_weight": "980",
        "tyres": "185/65 R15 88H - 195/55 R16 87H",
        "overall_height": "1496",
        "front_track": "1533",
        "rear_track": "1519",
        "overall_width": "1853",
        "overall_width_with_mirrors": "2012",
        "front_overhang": "833",
        "rear_overhang": "665",
        "wheelbase": "2604",
        "overall_length": "4102",
        "ground_clearance": "162",
    },
    "stepway": {
        "source": STEPWAY_BROCHURE_SOURCE,
        "power": "81",
        "power_rpm": "5000",
        "torque": "200",
        "torque_rpm": "2900",
        "acceleration": "10.0",
        "elasticity": (("4", "7.7"), ("5", "10.7"), ("6", "17.1")),
        "consumption": "5.7",
        "co2": "128",
        "minimum_kerb_weight": "1095",
        "maximum_kerb_weight": "1149",
        "gross_vehicle_weight": "1585",
        "gross_train_weight": "2685",
        "braked_trailer_weight": "1100",
        "tyres": "205/60 R16 92H",
        "front_track": "1520",
        "rear_track": "1509",
        "overall_width": "1853",
        "overall_width_with_mirrors": "2012",
        "front_overhang": "833",
        "rear_overhang": "665",
        "wheelbase": "2604",
        "overall_length": "4102",
        "ground_clearance": "201",
    },
}

FRONT_SUSPENSION = (
    "Typu McPherson z dolnym wahaczem, sprężynami śrubowymi, "
    "teleskopowymi amortyzatorami hydraulicznymi i stabilizatorem"
)
REAR_SUSPENSION = (
    "Belka skrętna ze sprężynami śrubowymi, teleskopowymi "
    "amortyzatorami hydraulicznymi i stabilizatorem"
)

FIELDS = {
    "sources.csv": (
        "id", "code", "source_type", "title", "publisher", "market",
        "document_date", "external_reference", "file_path", "sha256",
        "status", "notes",
    ),
    "versions.csv": (
        "id", "code", "model_code", "name", "status", "notes",
    ),
    "source_versions.csv": (
        "id", "source_code", "version_code", "relationship", "notes",
    ),
    "configurations.csv": (
        "id", "code", "version_code", "powertrain_label",
        "transmission_type", "status", "notes",
    ),
    "configuration_prices.csv": (
        "id", "code", "configuration_code", "market", "price_type",
        "amount", "currency_code", "price_date", "source_code", "notes",
    ),
    "source_configurations.csv": (
        "id", "source_code", "configuration_code", "relationship", "notes",
    ),
    "configuration_attribute_values.csv": (
        "id", "code", "configuration_code", "attribute_code",
        "fuel_type_code", "gear_number", "value", "observation_date",
        "source_code", "notes",
    ),
    "configuration_cargo_volume_contexts.csv": (
        "id", "code", "configuration_attribute_value_code",
        "measurement_basis_code", "second_row_state_code",
        "third_row_state_code", "compartment_code",
        "spare_wheel_state_code", "tyre_repair_kit_state_code",
        "double_floor_state_code", "notes",
    ),
    "configuration_attribute_availability.csv": (
        "id", "code", "configuration_code", "attribute_code",
        "availability_status", "observation_date", "source_code", "notes",
    ),
}


class CompletionError(RuntimeError):
    pass


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise CompletionError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def _write_csv(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _next_id(rows: Iterable[Mapping[str, str]]) -> int:
    return max((int(row["id"]) for row in rows if row.get("id", "").isdigit()), default=0) + 1


def _without_internal(configuration: Mapping[str, str]) -> dict[str, str]:
    return {field: str(configuration[field]) for field in FIELDS["configurations.csv"] if field != "id"}


def _row_code(
    configuration_code: str,
    attribute_code: str,
    observation_date: str,
    *,
    fuel_type_code: str = "",
    gear_number: str = "",
    suffix: str = "",
) -> str:
    parts = [configuration_code, attribute_code]
    if suffix:
        parts.append(suffix)
    if fuel_type_code:
        parts.append(fuel_type_code)
    if gear_number:
        parts.append(f"gear{gear_number}")
    parts.append(observation_date.replace("-", ""))
    return "_".join(parts)


def _technical_row(
    configuration_code: str,
    attribute_code: str,
    value: str,
    observation_date: str,
    source_code: str,
    page: int,
    section: str,
    source_text: str,
    *,
    fuel_type_code: str = "",
    gear_number: str = "",
    suffix: str = "",
) -> dict[str, str]:
    return {
        "code": _row_code(
            configuration_code,
            attribute_code,
            observation_date,
            fuel_type_code=fuel_type_code,
            gear_number=gear_number,
            suffix=suffix,
        ),
        "configuration_code": configuration_code,
        "attribute_code": attribute_code,
        "fuel_type_code": fuel_type_code,
        "gear_number": gear_number,
        "value": value,
        "observation_date": observation_date,
        "source_code": source_code,
        "notes": f"Official source page {page}, section {section}: {source_text}",
    }


def _technical_rows(configuration: Mapping[str, str]) -> list[dict[str, str]]:
    code = str(configuration["code"])
    family = str(configuration["model_family"])
    grade = str(configuration["grade"])
    model = MODEL_TECHNICAL[family]
    brochure_source = str(model["source"])
    rows: list[dict[str, str]] = []

    price_values = (
        ("fuel_type", "petrol", "", "", "Rodzaj paliwa: petrol"),
        ("aspiration_type", "turbocharged", "", "", "Rodzaj wtrysku: bezpośredni z turbodoładowaniem"),
        ("injection_type", "direct_injection", "", "", "Rodzaj wtrysku: bezpośredni"),
        ("engine_displacement", "999", "", "", "Pojemność skokowa: 999 cm³"),
        ("cylinder_count", "3", "", "", "Liczba cylindrów / zaworów: 3 / 12"),
        ("total_valve_count", "12", "", "", "Liczba cylindrów / zaworów: 3 / 12"),
        ("engine_power", str(model["power"]), "petrol", "", f"Maksymalna moc: {model['power']} kW przy 5000 obr./min."),
        ("max_power_rpm", str(model["power_rpm"]), "petrol", "", f"Maksymalna moc przy {model['power_rpm']} obr./min."),
        ("engine_torque", str(model["torque"]), "petrol", "", f"Maksymalny moment obrotowy: {model['torque']} Nm przy 2900 obr./min."),
        ("max_torque_rpm", str(model["torque_rpm"]), "petrol", "", f"Maksymalny moment obrotowy przy {model['torque_rpm']} obr./min."),
        ("emission_standard", "euro_6e_bis", "", "", "Norma emisji spalin: Euro 6e BIS"),
        ("gearbox_type", "manual", "", "", "Typ skrzyni biegów: manualna"),
        ("gear_count", "6", "", "", "Typ skrzyni biegów: 6-biegowa"),
        ("top_speed", "180", "", "", "Prędkość maksymalna: 180 km/h"),
        ("acceleration_0_100", str(model["acceleration"]), "petrol", "", f"0–100 km/h: {model['acceleration']} s"),
        ("fuel_tank_capacity", "50", "", "", "Pojemność zbiornika paliwa: 50 l"),
        ("fuel_consumption_combined", str(model["consumption"]), "petrol", "", f"Cykl mieszany: {model['consumption']} l/100 km"),
        ("co2_emissions", str(model["co2"]), "petrol", "", f"Emisja CO2: {model['co2']} g/km"),
        ("cargo_volume_vda", "328", "", "", "Pojemność bagażnika: 328 dm³ według normy VDA"),
        ("number_of_doors", "5", "", "", "Model pięciodrzwiowy"),
        ("number_of_seats", "5", "", "", "Konfiguracja pięciomiejscowa"),
        ("spare_wheel_type", "tyre repair kit", "", "", "Zestaw do naprawy opon"),
    )
    for attribute, value, fuel, gear, text in price_values:
        rows.append(
            _technical_row(
                code, attribute, value, OBSERVATION_DATE, PRICE_SOURCE, 6,
                "DANE TECHNICZNE", text,
                fuel_type_code=fuel, gear_number=gear,
            )
        )

    for gear_number, value in model["elasticity"]:
        rows.append(
            _technical_row(
                code,
                "elasticity_80_120",
                str(value),
                BROCHURE_DATE,
                brochure_source,
                17,
                "06. SILNIKI — OSIĄGI",
                f"Elastyczność 80–120 km/h na {gear_number}. biegu: {value} s (benzyna)",
                fuel_type_code="petrol",
                gear_number=str(gear_number),
            )
        )

    brochure_values = (
        ("minimum_kerb_weight", str(model["minimum_kerb_weight"]), f"Minimalna masa pojazdu gotowego do jazdy: {model['minimum_kerb_weight']} kg"),
        ("maximum_kerb_weight", str(model["maximum_kerb_weight"]), f"Maksymalna masa pojazdu gotowego do jazdy: {model['maximum_kerb_weight']} kg"),
        ("gross_vehicle_weight", str(model["gross_vehicle_weight"]), f"Dopuszczalna masa całkowita pojazdu: {model['gross_vehicle_weight']} kg"),
        ("gross_train_weight", str(model["gross_train_weight"]), f"Dopuszczalna masa całkowita zespołu pojazdów: {model['gross_train_weight']} kg"),
        ("braked_trailer_weight", str(model["braked_trailer_weight"]), f"Maksymalna masa przyczepy hamowanej: {model['braked_trailer_weight']} kg"),
        ("standard_tyre_specification", str(model["tyres"]), f"Wymiary opon: {model['tyres']}"),
        ("turning_circle_between_kerbs", "10.64", "Średnica zawracania między krawężnikami: 10,64 m"),
        ("front_suspension", FRONT_SUSPENSION, f"Zawieszenie przednie: {FRONT_SUSPENSION}"),
        ("rear_suspension", REAR_SUSPENSION, f"Tylne zawieszenie: {REAR_SUSPENSION}"),
    )
    for attribute, value, text in brochure_values:
        rows.append(
            _technical_row(
                code, attribute, value, BROCHURE_DATE, brochure_source, 17,
                "06. SILNIKI — ZAWIESZENIE / MASY I POJEMNOŚCI", text,
            )
        )

    dimension_names = {
        "overall_height": "wysokość całkowita",
        "front_track": "rozstaw kół przednich",
        "rear_track": "rozstaw kół tylnych",
        "overall_width": "szerokość nadwozia",
        "overall_width_with_mirrors": "szerokość z lusterkami",
        "front_overhang": "zwis przedni",
        "rear_overhang": "zwis tylny",
        "wheelbase": "rozstaw osi",
        "overall_length": "długość całkowita",
        "ground_clearance": "prześwit",
    }
    dimension_keys = (
        "overall_height",
        "front_track",
        "rear_track",
        "overall_width",
        "overall_width_with_mirrors",
        "front_overhang",
        "rear_overhang",
        "wheelbase",
        "overall_length",
        "ground_clearance",
    )
    if family == "stepway":
        dimension_keys = tuple(key for key in dimension_keys if key != "overall_height")
    for attribute in dimension_keys:
        value = str(model[attribute])
        rows.append(
            _technical_row(
                code,
                attribute,
                value,
                BROCHURE_DATE,
                brochure_source,
                20,
                "06. WYMIARY",
                f"{dimension_names[attribute]}: {value} mm",
            )
        )

    for cargo in CARGO_OBSERVATIONS:
        rows.append(
            _technical_row(
                code,
                "boot_capacity",
                str(cargo["value"]),
                BROCHURE_DATE,
                brochure_source,
                20,
                "06. WYMIARY — POJEMNOŚĆ BAGAŻNIKA",
                str(cargo["text"]),
                suffix=str(cargo["suffix"]),
            )
        )

    trim = TRIM_VALUES[(family, grade)]
    trim_text = {
        "wheel_size": f"Rozmiar obręczy: {trim['wheel_size']}",
        "wheel_material": f"Materiał obręczy: {trim['wheel_material']}",
        "wheel_design": f"Wzór obręczy: {trim['wheel_design']}",
        "wheel_finish": f"Wykończenie obręczy: {trim['wheel_finish']}",
        "upholstery_variant": f"Tapicerka: {trim['upholstery_variant']}",
    }
    for attribute in ("wheel_size", "wheel_material", "wheel_design", "wheel_finish", "upholstery_variant"):
        rows.append(
            _technical_row(
                code,
                attribute,
                str(trim[attribute]),
                OBSERVATION_DATE,
                PRICE_SOURCE,
                2,
                "WYPOSAŻENIE I OPCJE — NADWOZIE / WNĘTRZE",
                trim_text[attribute],
            )
        )

    if len(rows) != 53:
        raise CompletionError(f"{code}: expected 53 technical rows, built {len(rows)}")
    return rows


def _configuration_metadata(code: str) -> tuple[str, str, str]:
    stepway = code.startswith("sandero_stepway_")
    family = "stepway" if stepway else "sandero"
    if "_essential_" in code:
        grade = "essential"
    elif "_journey_" in code:
        grade = "journey"
    elif "_extreme_" in code:
        grade = "extreme"
    elif "_expression_" in code:
        grade = "expression"
    else:
        raise CompletionError(f"cannot resolve grade for {code}")
    transmission = "automatic" if code.endswith("_automatic") else "manual"
    return family, grade, transmission


_ALWAYS_STANDARD = {
    "rear_seat_folding",
    "my_safety_button",
    "anti_lock_braking_system",
    "automatic_emergency_braking",
    "electronic_stability_control",
    "hill_start_assist",
    "emergency_call_ecall",
    "alcohol_interlock_preparation",
    "traffic_sign_recognition",
    "lane_departure_warning",
    "lane_keep_assist",
    "driver_attention_monitoring",
    "rescue_code",
    "driver_front_airbag",
    "passenger_front_airbag",
    "front_side_airbags",
    "curtain_airbags",
    "cruise_control",
    "speed_limiter",
    "rear_parking_sensors",
    "tyre_pressure_monitoring_system",
    "tyre_repair_kit",
    "automatic_headlights",
    "rain_sensing_wipers",
    "central_locking",
    "automatic_door_locking",
    "front_windows_power",
    "steering_wheel_height_adjustment",
    "driver_seat_height_adjustment",
    "bluetooth_connectivity",
    "onboard_computer",
    "led_headlights",
    "led_daytime_running_lights",
    "youclip_phone_holder",
    "boot_compartment_lighting",
}


def _equipment_status(configuration_code: str, attribute: str) -> str:
    family, grade, transmission = _configuration_metadata(configuration_code)
    upper = grade in {"journey", "extreme"}
    expression = grade == "expression"
    essential = grade == "essential"

    if attribute in _ALWAYS_STANDARD:
        return "standard"
    if attribute == "roof_rails":
        return "standard" if family == "stepway" and essential else "not_available"
    if attribute == "modular_roof_rails":
        return "standard" if family == "stepway" and grade in {"expression", "extreme"} else "not_available"
    if attribute == "shark_fin_antenna":
        return "standard" if not essential else "optional"
    if attribute in {"one_touch_windows", "rear_windows_power", "steering_wheel_reach_adjustment", "front_centre_armrest", "side_mirrors_electric_adjustment", "side_mirrors_heated"}:
        return "not_available" if essential else "standard"
    if attribute == "manual_air_conditioning":
        return "not_available" if family == "sandero" and essential else "standard"
    if attribute == "automatic_climate_control":
        if upper:
            return "standard"
        return "optional" if expression else "not_available"
    if attribute in {"fog_lights", "front_parking_sensors", "blind_spot_monitoring"}:
        return "standard" if upper else "not_available"
    if attribute == "rear_view_camera":
        if upper or (family == "stepway" and expression):
            return "standard"
        return "optional" if expression else "not_available"
    if attribute == "360_camera_system":
        return "optional" if upper else "not_available"
    if attribute == "electronic_parking_brake":
        if upper or (expression and transmission == "automatic"):
            return "standard"
        return "not_available"
    if attribute == "glass_sunroof":
        return "optional" if family == "stepway" and grade == "extreme" else "not_available"
    if attribute == "heated_front_seats":
        return "optional" if not essential else "not_available"
    if attribute == "heated_steering_wheel":
        return "optional" if upper else "not_available"
    if attribute == "keyless_entry":
        if upper:
            return "standard"
        if expression and transmission == "automatic":
            return "optional"
        return "not_available"
    if attribute == "media_control_system":
        return "standard" if essential else "not_available"
    if attribute in {"media_display_system", "wireless_smartphone_replication", "touchscreen"}:
        return "not_available" if essential else "standard"
    if attribute == "navigation_system":
        return "optional" if not essential else "not_available"
    if attribute in {"wireless_charging", "side_mirrors_folding", "high_beam_assist"}:
        return "optional" if upper else "not_available"
    if attribute == "instrument_cluster_tft_3_5":
        return "standard" if grade in {"essential", "expression"} else "not_available"
    if attribute == "instrument_cluster_colour_7":
        return "standard" if upper else "not_available"
    if attribute == "extended_grip":
        return "standard" if grade == "extreme" else "not_available"
    if attribute == "adjustable_boot_floor":
        return "standard" if upper else "not_available"
    if attribute == "eco_leather_steering_wheel":
        return "optional" if essential else "standard"
    if attribute == "rear_usb_c_ports":
        return "standard" if upper or (expression and transmission == "automatic") else "not_available"
    raise CompletionError(f"missing equipment rule for {attribute}")


def _equipment_rows() -> list[dict[str, str]]:
    rows = []
    for configuration_code in MATRIX_CONFIGURATIONS:
        for attribute in EQUIPMENT_ATTRIBUTES:
            status = _equipment_status(configuration_code, attribute)
            rows.append(
                {
                    "code": f"{configuration_code}_{attribute}_20260703",
                    "configuration_code": configuration_code,
                    "attribute_code": attribute,
                    "availability_status": status,
                    "observation_date": OBSERVATION_DATE,
                    "source_code": PRICE_SOURCE,
                    "notes": (
                        "Official Polish MY26 price-list equipment matrix, "
                        f"normalized source state for {attribute}: {status}."
                    ),
                }
            )
    if len(rows) != 1050:
        raise CompletionError(f"expected 1050 matrix rows, built {len(rows)}")
    return rows


def _price_rows() -> list[dict[str, str]]:
    pairs = [(str(item["code"]), str(item["price"])) for item in CONFIGURATIONS]
    pairs.extend(EXTRA_PRICE_OBSERVATIONS)
    return [
        {
            "code": f"{configuration_code}_pl_catalog_gross_20260703",
            "configuration_code": configuration_code,
            "market": "PL",
            "price_type": "catalog_gross",
            "amount": amount,
            "currency_code": "PLN",
            "price_date": OBSERVATION_DATE,
            "source_code": PRICE_SOURCE,
            "notes": (
                "Official Polish MY26 catalogue gross price effective from "
                "2026-07-03; financing and promotional claims excluded."
            ),
        }
        for configuration_code, amount in pairs
    ]


def _source_relationship_rows() -> list[dict[str, str]]:
    rows = []
    price_codes = [str(item["code"]) for item in CONFIGURATIONS]
    price_codes.extend(code for code, _ in EXTRA_PRICE_OBSERVATIONS)
    for configuration_code in price_codes:
        rows.append(
            {
                "source_code": PRICE_SOURCE,
                "configuration_code": configuration_code,
                "relationship": "documents",
                "notes": (
                    "Non-empty page-1 price cell in the 2026-07-03 matrix; "
                    "observations are imported separately."
                ),
            }
        )
    for item in CONFIGURATIONS:
        family = str(item["model_family"])
        source = SANDERO_BROCHURE_SOURCE if family == "sandero" else STEPWAY_BROCHURE_SOURCE
        rows.append(
            {
                "source_code": source,
                "configuration_code": str(item["code"]),
                "relationship": "brochure_technical_data_for",
                "notes": (
                    "The model-level official brochure lists the represented "
                    "TCe powertrain and gives model-wide technical, dimension "
                    "and cargo observations; grade-specific commercial values "
                    "remain sourced from the 2026-07-03 price list."
                ),
            }
        )
    return rows


def _cargo_context_rows(technical_rows: Iterable[Mapping[str, str]]) -> list[dict[str, str]]:
    value_by_code = {row["code"]: row for row in technical_rows}
    rows = []
    for item in CONFIGURATIONS:
        configuration_code = str(item["code"])
        for cargo in CARGO_OBSERVATIONS:
            value_code = _row_code(
                configuration_code,
                "boot_capacity",
                BROCHURE_DATE,
                suffix=str(cargo["suffix"]),
            )
            if value_code not in value_by_code:
                raise CompletionError(f"missing cargo value for {value_code}")
            rows.append(
                {
                    "code": f"cargo_context_{value_code}",
                    "configuration_attribute_value_code": value_code,
                    "measurement_basis_code": str(cargo["measurement_basis_code"]),
                    "second_row_state_code": str(cargo["second_row_state_code"]),
                    "third_row_state_code": "",
                    "compartment_code": str(cargo["compartment_code"]),
                    "spare_wheel_state_code": "",
                    "tyre_repair_kit_state_code": "",
                    "double_floor_state_code": "",
                    "notes": (
                        "Official brochure page 20; exact context for "
                        f"{cargo['text']}. Empty optional fields mean not stated."
                    ),
                }
            )
    if len(rows) != 30:
        raise CompletionError(f"expected 30 cargo contexts, built {len(rows)}")
    return rows


def _append_expected(
    path: Path,
    expected: Sequence[Mapping[str, str]],
    *,
    key: str = "code",
    apply: bool,
) -> tuple[int, list[dict[str, str]]]:
    fields, rows = _read_csv(path)
    expected_fields = list(FIELDS[path.name])
    if fields != expected_fields:
        raise CompletionError(f"unexpected header for {path}: {fields}")
    indexed = {row[key]: row for row in rows}
    next_id = _next_id(rows)
    added = 0
    for payload in expected:
        code = str(payload[key])
        target = {field: str(payload.get(field, "")) for field in fields if field != "id"}
        current = indexed.get(code)
        if current is not None:
            actual = {field: current.get(field, "") for field in fields if field != "id"}
            if actual != target:
                raise CompletionError(f"existing row differs for {path.name}:{code}")
            continue
        if not apply:
            raise CompletionError(f"missing row {path.name}:{code}")
        row = {"id": str(next_id), **target}
        next_id += 1
        rows.append(row)
        indexed[code] = row
        added += 1
    if apply and added:
        _write_csv(path, fields, rows)
    return added, rows


def _apply_equipment(path: Path, *, apply: bool) -> int:
    fields, rows = _read_csv(path)
    if fields != list(FIELDS[path.name]):
        raise CompletionError(f"unexpected header for {path}")
    by_semantic = {
        (row["source_code"], row["configuration_code"], row["attribute_code"]): row
        for row in rows
    }
    by_code = {row["code"]: row for row in rows}
    next_id = _next_id(rows)
    added = 0
    for expected in _equipment_rows():
        semantic = (
            expected["source_code"],
            expected["configuration_code"],
            expected["attribute_code"],
        )
        current = by_semantic.get(semantic)
        if current is None:
            legacy = by_semantic.get(
                (
                    RAW_PRICE_SOURCE,
                    expected["configuration_code"],
                    expected["attribute_code"],
                )
            )
            if legacy is not None and legacy["observation_date"] == OBSERVATION_DATE:
                current = legacy
        if current is not None:
            if current["availability_status"] != expected["availability_status"]:
                raise CompletionError(
                    "existing equipment status differs for "
                    f"{expected['configuration_code']}:{expected['attribute_code']}: "
                    f"{current['availability_status']} != {expected['availability_status']}"
                )
            continue
        if expected["code"] in by_code:
            raise CompletionError(f"equipment code collision: {expected['code']}")
        if not apply:
            raise CompletionError(
                f"missing equipment row {expected['configuration_code']}:{expected['attribute_code']}"
            )
        row = {"id": str(next_id), **expected}
        next_id += 1
        rows.append(row)
        by_semantic[semantic] = row
        by_code[row["code"]] = row
        added += 1
    if apply and added:
        _write_csv(path, fields, rows)
    return added


def _update_cargo_spec(repository: Path, *, apply: bool) -> None:
    path = repository / "data/imports/configuration_cargo_values/sandero-stepway-brochure-cargo-20260202.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    configurations = payload.get("configurations")
    if not isinstance(configurations, list):
        raise CompletionError("invalid cargo import spec")
    existing = {
        item["configuration_code"]
        for item in configurations
        if isinstance(item, dict) and isinstance(item.get("configuration_code"), str)
    }
    for item in CONFIGURATIONS:
        code = str(item["code"])
        if code in existing:
            continue
        family = str(item["model_family"])
        configurations.append(
            {
                "configuration_code": code,
                "source_code": (
                    SANDERO_BROCHURE_SOURCE
                    if family == "sandero"
                    else STEPWAY_BROCHURE_SOURCE
                ),
            }
        )
        existing.add(code)
    payload["non_inference"] = [
        line
        for line in payload.get("non_inference", [])
        if "Do not import TCe 100 configurations" not in str(line)
    ]
    if not all(str(item["code"]) in existing for item in CONFIGURATIONS):
        raise CompletionError("cargo spec does not include all new configurations")
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if apply:
        path.write_text(rendered, encoding="utf-8")
    elif path.read_text(encoding="utf-8") != rendered:
        raise CompletionError("cargo import spec is not normalized for catalogue completion")


def _write_reporting_scope(repository: Path, *, apply: bool) -> None:
    path = repository / "data/reporting/sandero_tce100_stepway_tce110_manual_completeness.json"
    technical_rows = [row for item in CONFIGURATIONS for row in _technical_rows(item)]
    slots = sorted(
        {
            (row["attribute_code"], row["fuel_type_code"])
            for row in technical_rows
        }
    )
    payload = {
        "version": 1,
        "configuration_status": "active",
        "configurations": [
            {
                "configuration_code": str(item["code"]),
                "source_code": PRICE_SOURCE,
            }
            for item in CONFIGURATIONS
        ],
        "technical_slots": [
            {
                "attribute_code": attribute_code,
                "fuel_type_code": fuel_type_code,
            }
            for attribute_code, fuel_type_code in slots
        ],
        "equipment_attributes": list(EQUIPMENT_ATTRIBUTES),
        "not_applicable": {"technical": [], "equipment": []},
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if apply:
        path.write_text(rendered, encoding="utf-8")
    elif not path.exists() or path.read_text(encoding="utf-8") != rendered:
        raise CompletionError(f"reporting scope is missing or differs: {path}")


def _write_package_contract(repository: Path, *, apply: bool) -> None:
    path = repository / "data/imports/catalog_completion/sandero-stepway-tce-20260703.json"
    payload = {
        "version": 1,
        "kind": "sandero_stepway_catalog_completion",
        "observation_date": OBSERVATION_DATE,
        "price_source_code": PRICE_SOURCE,
        "source_slices": [
            PRICE_SOURCE,
            SANDERO_BROCHURE_SOURCE,
            STEPWAY_BROCHURE_SOURCE,
        ],
        "configuration_codes": [str(item["code"]) for item in CONFIGURATIONS],
        "expected_additions": {
            "sources": 3,
            "versions": 1,
            "source_version_relationships": 1,
            "configurations": 6,
            "prices": 8,
            "technical_values": 318,
            "equipment_availability": 1016,
            "cargo_contexts": 30,
            "source_configuration_relationships": 14,
            "reporting_scopes": 1,
        },
        "expected_repository_totals": {
            "active_configurations": 78,
            "reporting_scopes": 21,
            "unique_comparison_pairs": 120,
        },
        "non_inference": [
            "Only source-visible TCe 100 and TCe 110 configurations are added.",
            "Price observations exclude financing and promotional claims.",
            "Cargo context fields remain empty when the brochure does not state them.",
            "The equipment matrix preserves the 34 earlier observations from the same source and adds only missing states.",
            "No value is derived arithmetically from another technical observation.",
        ],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    elif not path.exists() or path.read_text(encoding="utf-8") != rendered:
        raise CompletionError(f"package contract is missing or differs: {path}")



def _source_slice_rows(repository: Path, *, apply: bool) -> list[dict[str, str]]:
    master = repository / "data/master"
    _, registered = _read_csv(master / "sources.csv")
    raw_by_code = {row["code"]: row for row in registered}
    definitions = (
        (
            PRICE_SOURCE,
            RAW_PRICE_SOURCE,
            "Sandero and Stepway MY26 TCe catalogue slice",
            sorted(
                {str(item["code"]) for item in CONFIGURATIONS}
                | {code for code, _ in EXTRA_PRICE_OBSERVATIONS}
            ),
            [1, 2, 3, 4, 5, 6],
            ["configuration", "price", "equipment", "technical", "trim"],
        ),
        (
            SANDERO_BROCHURE_SOURCE,
            RAW_SANDERO_BROCHURE_SOURCE,
            "Sandero TCe 100 brochure technical slice",
            sorted(
                str(item["code"])
                for item in CONFIGURATIONS
                if item["model_family"] == "sandero"
            ),
            [17, 20],
            ["technical", "performance", "chassis", "dimensions", "cargo"],
        ),
        (
            STEPWAY_BROCHURE_SOURCE,
            RAW_STEPWAY_BROCHURE_SOURCE,
            "Sandero Stepway TCe 110 brochure technical slice",
            sorted(
                str(item["code"])
                for item in CONFIGURATIONS
                if item["model_family"] == "stepway"
            ),
            [17, 20],
            ["technical", "performance", "chassis", "dimensions", "cargo"],
        ),
    )
    rows: list[dict[str, str]] = []
    for code, raw_code, title, configurations, pages, families in definitions:
        raw = raw_by_code.get(raw_code)
        if raw is None:
            raise CompletionError(f"raw source missing: {raw_code}")
        payload = {
            "version": 1,
            "kind": "official_source_slice",
            "slice_code": code,
            "raw_source_code": raw_code,
            "raw_source": {
                "title": raw["title"],
                "publisher": raw["publisher"],
                "market": raw["market"],
                "document_date": raw["document_date"],
                "external_reference": raw["external_reference"],
                "file_path": raw["file_path"],
                "sha256": raw["sha256"],
            },
            "selection": {
                "configuration_codes": configurations,
                "source_pages": pages,
                "observation_families": families,
            },
            "non_inference": [
                "The slice does not replace or alter the registered raw official document.",
                "Every imported observation retains raw page and section provenance in its notes.",
                "Only values directly visible in the selected official source are represented.",
            ],
        }
        relative = Path("project/sources") / f"{code.removeprefix('src_pl_')}.json"
        rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        target = repository / relative
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
        elif not target.exists() or target.read_text(encoding="utf-8") != rendered:
            raise CompletionError(f"source slice differs: {relative}")
        digest = __import__("hashlib").sha256(rendered.encode("utf-8")).hexdigest()
        rows.append(
            {
                "code": code,
                "source_type": "normalized_snapshot",
                "title": title,
                "publisher": raw["publisher"],
                "market": raw["market"],
                "document_date": raw["document_date"],
                "external_reference": raw["external_reference"],
                "file_path": relative.as_posix(),
                "sha256": digest,
                "status": "active",
                "notes": (
                    f"Versioned source slice of {raw_code}; the raw official "
                    "file remains canonical and hash-verified."
                ),
            }
        )
    return rows

def _validate_references(repository: Path) -> None:
    master = repository / "data/master"
    _, versions = _read_csv(master / "versions.csv")
    _, attributes = _read_csv(master / "attributes.csv")
    _, sources = _read_csv(master / "sources.csv")
    version_codes = {row["code"] for row in versions}
    attribute_codes = {row["code"] for row in attributes}
    source_codes = {row["code"] for row in sources}
    for item in CONFIGURATIONS:
        if item["version_code"] not in version_codes:
            raise CompletionError(f"unknown version: {item['version_code']}")
    expected_attributes = set(EQUIPMENT_ATTRIBUTES)
    expected_attributes.update(
        row["attribute_code"]
        for item in CONFIGURATIONS
        for row in _technical_rows(item)
    )
    missing_attributes = expected_attributes - attribute_codes
    if missing_attributes:
        raise CompletionError(f"unknown attributes: {sorted(missing_attributes)}")
    required_sources = {PRICE_SOURCE, SANDERO_BROCHURE_SOURCE, STEPWAY_BROCHURE_SOURCE}
    missing_sources = required_sources - source_codes
    if missing_sources:
        raise CompletionError(f"unknown sources: {sorted(missing_sources)}")


def _apply_source_versions(path: Path, *, apply: bool) -> int:
    fields, rows = _read_csv(path)
    if fields != list(FIELDS[path.name]):
        raise CompletionError(f"unexpected header for {path}")
    semantic = (PRICE_SOURCE, SANDERO_ESSENTIAL_VERSION["code"], "documents")
    index = {
        (row["source_code"], row["version_code"], row["relationship"]): row
        for row in rows
    }
    current = index.get(semantic)
    expected_notes = "Version column in the page-1 price matrix effective 2026-07-03."
    if current is not None:
        if current["notes"] != expected_notes:
            raise CompletionError(f"source version relationship differs: {semantic}")
        return 0
    if not apply:
        raise CompletionError(f"missing source version relationship: {semantic}")
    row = {
        "id": str(_next_id(rows)),
        "source_code": PRICE_SOURCE,
        "version_code": SANDERO_ESSENTIAL_VERSION["code"],
        "relationship": "documents",
        "notes": expected_notes,
    }
    rows.append(row)
    _write_csv(path, fields, rows)
    return 1


def _apply_source_relationships(path: Path, *, apply: bool) -> int:
    fields, rows = _read_csv(path)
    if fields != list(FIELDS[path.name]):
        raise CompletionError(f"unexpected header for {path}")
    semantic_index = {
        (row["source_code"], row["configuration_code"], row["relationship"]): row
        for row in rows
    }
    next_id = _next_id(rows)
    added = 0
    for payload in _source_relationship_rows():
        semantic = (
            payload["source_code"],
            payload["configuration_code"],
            payload["relationship"],
        )
        current = semantic_index.get(semantic)
        if current is not None:
            if current["notes"] != payload["notes"]:
                raise CompletionError(f"source relationship differs: {semantic}")
            continue
        if not apply:
            raise CompletionError(f"missing source relationship: {semantic}")
        row = {
            "id": str(next_id),
            "source_code": payload["source_code"],
            "configuration_code": payload["configuration_code"],
            "relationship": payload["relationship"],
            "notes": payload["notes"],
        }
        next_id += 1
        rows.append(row)
        semantic_index[semantic] = row
        added += 1
    if apply and added:
        _write_csv(path, fields, rows)
    return added


def complete(repository: Path, *, apply: bool) -> dict[str, int]:
    repository = repository.resolve()
    master = repository / "data/master"
    additions: dict[str, int] = {}
    source_slice_rows = _source_slice_rows(repository, apply=apply)
    additions["sources"], _ = _append_expected(
        master / "sources.csv",
        source_slice_rows,
        apply=apply,
    )
    additions["versions"], _ = _append_expected(
        master / "versions.csv",
        [SANDERO_ESSENTIAL_VERSION],
        apply=apply,
    )
    additions["source_version_relationships"] = _apply_source_versions(
        master / "source_versions.csv",
        apply=apply,
    )
    _validate_references(repository)
    technical_rows = [row for item in CONFIGURATIONS for row in _technical_rows(item)]
    cargo_context_rows = _cargo_context_rows(technical_rows)

    additions["configurations"], _ = _append_expected(
        master / "configurations.csv",
        [_without_internal(item) for item in CONFIGURATIONS],
        apply=apply,
    )
    additions["prices"], _ = _append_expected(
        master / "configuration_prices.csv",
        _price_rows(),
        apply=apply,
    )
    additions["source_configuration_relationships"] = _apply_source_relationships(
        master / "source_configurations.csv",
        apply=apply,
    )
    additions["technical_values"], _ = _append_expected(
        master / "configuration_attribute_values.csv",
        technical_rows,
        apply=apply,
    )
    additions["cargo_contexts"], _ = _append_expected(
        master / "configuration_cargo_volume_contexts.csv",
        cargo_context_rows,
        apply=apply,
    )
    additions["equipment_availability"] = _apply_equipment(
        master / "configuration_attribute_availability.csv",
        apply=apply,
    )
    _write_reporting_scope(repository, apply=apply)
    _write_package_contract(repository, apply=apply)

    if not apply and any(additions.values()):
        raise CompletionError(f"verification unexpectedly planned additions: {additions}")
    return additions


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        additions = complete(args.repository, apply=args.apply)
    except (CompletionError, OSError, csv.Error, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.apply:
        print(json.dumps({"applied": additions}, sort_keys=True))
    else:
        print(json.dumps({"verified": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
