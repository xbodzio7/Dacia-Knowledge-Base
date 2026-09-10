from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
CAPTURE = ROOT / "project/sources/dacia-pl-sandero-stepway-full-technical-standard-equipment-20260809.json"
RECONCILIATION = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"
SOURCE_CODE = "src_pl_sandero_stepway_full_modal_20260809"
DATE = "2026-08-09"

SAFE_MARKERS = (
    "obręcze kół", "felgi aluminiowe", "esp z systemem", "tapicerka materiałowa",
    "płetwy rekina", "dwa światła cofania", "filtr cząstek stałych",
    "fotel kierowcy z regulacją wzdłużną", "kierownica pokryta skórą ekologiczną",
    "kierownica z pianki", "kluczyk z 3 przyciskami", "komunikaty w języku polskim",
    "lusterka boczne regulowane ręcznie", "relingi dachowe", "niska konsola środkowa",
    "normalny dach", "system multimedialny media", "ograniczenie prędkości do 180",
    "poduszki boczne z przodu", "regulator-ogranicznik", "system wspomagania parkowania przód/tył",
    "szyby tylne otwierane ręcznie", "tryb eco", "tylne oparcie kanapy nieskładane",
    "światła automatyczne, wycieraczki automatyczne",
)
NEGATIVE = {
    "bez automatycznego parkowania",
    "bez podłogi bagażnika ustawianej w dwóch płaszczyznach (góra i dół)",
    "brak świateł przeciwmgielnych",
    "kierownica nieogrzewana",
    "szyba przednia nieogrzewana",
}

# Explicit mappings are used instead of inferring from an unrelated prior literal.
# A tuple may contain more than one canonical attribute for a composite source literal.
LITERAL_MAPPINGS: dict[str, tuple[tuple[str, str], ...]] = {
    '15" stalowe obręcze kół - wzór ELMA': (("wheel_design", "standard"),),
    '16" felgi aluminiowe': (("wheel_material", "standard"),),
    '16" felgi aluminiowe TAMIA': (("wheel_design", "standard"),),
    '16" felgi aluminiowe TAMIA BI-TON': (("wheel_design", "standard"),),
    '16" felgi aluminiowe TAMIA BLACK': (("wheel_design", "standard"),),
    '16" stalowe obręcze kół typu Flexwheel - wzór ATARA': (("wheel_design", "standard"),),
    "ESP z systemem wspomagania ruszania pod górę": (("electronic_stability_control", "standard"), ("hill_start_assist", "standard")),
    "Tapicerka materiałowa z materiałów pochodzących z recyklingu": (("upholstery_variant", "standard"),),
    'antena w kształcie "płetwy rekina"': (("shark_fin_antenna", "standard"),),
    "dwa światła cofania": (("reversing_lights_count", "standard"),),
    "filtr cząstek stałych": (("particulate_filter", "standard"),),
    "fotel kierowcy z regulacją wzdłużną bez regulacji wysokości": (("driver_seat_adjustment", "standard"),),
    "kierownica pokryta skórą ekologiczną": (("eco_leather_steering_wheel", "standard"),),
    "kierownica z pianki": (("steering_wheel_material", "standard"),),
    "komunikaty w języku polskim": (("interface_language_source_stated", "standard"),),
    "lusterka boczne regulowane ręcznie od wewnątrz za pomocą pokrętła": (("side_mirrors_electric_adjustment", "not_available"),),
    "modułowe relingi dachowe": (("modular_roof_rails", "standard"),),
    "niska konsola środkowa z otwartym schowkiem": (("centre_console_variant", "standard"),),
    "normalny dach": (("roof_type_source_stated", "standard"),),
    'nowy system multimedialny Media Display (dotykowy ekran 10", bezprzewodowa replikacja smartfona)': (("media_display_system", "standard"), ("touchscreen", "standard"), ("wireless_smartphone_replication", "standard")),
    "ograniczenie prędkości do 180 km/h": (("factory_speed_limit", "standard"),),
    "poduszki boczne z przodu + poduszki kurtynowe": (("front_side_airbags", "standard"), ("curtain_airbags", "standard")),
    "regulator-ogranicznik prędkości": (("cruise_control", "standard"), ("speed_limiter", "standard")),
    "relingi dachowe": (("roof_rails", "standard"),),
    'stalowe obręcze kół 15"': (("wheel_material", "standard"),),
    'stalowe obręcze kół 16"': (("wheel_material", "standard"),),
    "system multimedialny Media Control (radio DAB, 2 głośniki, Bluetooth, 1xUSB, aplikacja DMC)": (("media_control_system", "standard"), ("bluetooth_connectivity", "standard")),
    "system wspomagania parkowania przód/tył": (("front_parking_sensors", "standard"), ("rear_parking_sensors", "standard")),
    "szyby tylne otwierane ręcznie": (("rear_windows_power", "not_available"),),
    "tapicerka materiałowa": (("upholstery_variant", "standard"),),
    "tapicerka materiałowa stepway": (("upholstery_variant", "standard"),),
    "tapicerka materiałowa w kolorze czarnym i wstawkami denim": (("upholstery_variant", "standard"),),
    "tapicerka materiałowa w kolorze denim i czarnymi wstawkami": (("upholstery_variant", "standard"),),
    "tryb ECO": (("eco_mode", "standard"),),
    "tylne oparcie kanapy nieskładane": (("rear_seat_folding", "not_available"),),
    "światła automatyczne, wycieraczki automatyczne": (("automatic_headlights", "standard"), ("rain_sensing_wipers", "standard")),
}


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def next_id(rows: list[dict[str, str]]) -> int:
    return max((int(row["id"]) for row in rows), default=0) + 1


def build() -> tuple[list[str], list[dict[str, str]], dict]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    fields, availability = read_csv("configuration_attribute_availability.csv")
    attributes = {row["code"] for row in read_csv("attributes.csv")[1]}

    safe_literals = {
        row["literal"] for row in reconciliation["unresolved_equipment_literals"]
        if row["literal"] not in NEGATIVE
        and any(marker in row["literal"].casefold() for marker in SAFE_MARKERS)
    }
    safe_occurrences = sum(
        row["occurrences"] for row in reconciliation["unresolved_equipment_literals"]
        if row["literal"] in safe_literals
    )
    if safe_occurrences != 286:
        raise RuntimeError(f"expected 286 safe equipment occurrences, got {safe_occurrences}")

    missing_mappings = sorted(
        literal for literal in safe_literals
        if norm(literal) not in {norm(key) for key in LITERAL_MAPPINGS}
    )
    if missing_mappings:
        raise RuntimeError(f"safe literals without explicit mapping: {missing_mappings!r}")

    existing_codes = {row["code"] for row in availability}
    mapped_occurrences = 0
    mapped_rows = 0
    invalid_attributes: set[str] = set()

    for config in capture["configurations"]:
        configuration_code = config["configuration_code"]
        for group in config["equipment"]:
            for item in group["items"]:
                if item not in safe_literals:
                    continue
                mappings = LITERAL_MAPPINGS[item]
                for attribute_code, status in mappings:
                    if attribute_code not in attributes:
                        invalid_attributes.add(attribute_code)
                        continue
                    code = f"{configuration_code}_{attribute_code}_20260809_full_modal"
                    if code in existing_codes:
                        continue
                    availability.append({
                        "id": str(next_id(availability)),
                        "code": code,
                        "configuration_code": configuration_code,
                        "attribute_code": attribute_code,
                        "availability_status": status,
                        "observation_date": DATE,
                        "source_code": SOURCE_CODE,
                        "notes": f"Exact full-modal equipment literal: {item}",
                    })
                    existing_codes.add(code)
                    mapped_rows += 1
                mapped_occurrences += 1

    if invalid_attributes:
        raise RuntimeError(f"explicit mappings reference missing attributes: {sorted(invalid_attributes)!r}")
    if mapped_occurrences != 286:
        raise RuntimeError(f"expected 286 mapped occurrences, got {mapped_occurrences}")

    report = {
        "schema_version": 2,
        "package_id": "sandero_stepway_full_modal_residual_equipment_001",
        "observed_on": DATE,
        "safe_equipment_occurrences": safe_occurrences,
        "mapped_occurrences": mapped_occurrences,
        "materialized_availability_rows": mapped_rows,
        "preserved_equipment_occurrences": 441 - safe_occurrences,
        "source_code": SOURCE_CODE,
        "mapping_policy": "explicit_canonical_mapping",
    }
    return fields, availability, report


def apply(fields: list[str], rows: list[dict[str, str]]) -> None:
    with (MASTER / "configuration_attribute_availability.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    fields, rows, report = build()
    if args.apply:
        apply(fields, rows)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
