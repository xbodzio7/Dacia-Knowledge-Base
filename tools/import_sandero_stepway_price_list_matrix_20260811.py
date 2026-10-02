from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
SOURCE = ROOT / "project/sources/sandero_stepway_price_my26_20260811_full_extract.json"
REPORT = ROOT / "data/reporting/sandero_stepway_price_list_matrix_import_20260811.json"

SOURCE_CODE = "src_pl_sandero_stepway_price_my26_20260811"
DATE = "2026-08-11"

# Only direct, unambiguous canonical mappings are materialized.
# Composite/design/colour literals remain in the source extract/report.
ROW_MAP = {
    "Relingi dachowe": ["roof_rails"],
    "Modułowe relingi dachowe": ["modular_roof_rails"],
    "Antena typu „płetwa rekina”": ["shark_fin_antenna"],
    "Tylna kanapa dzielona 1/3 - 2/3": ["rear_seat_folding"],
    "ABS + AFU": ["anti_lock_braking_system"],
    "AEBS piesi/rowerzyści": ["automatic_emergency_braking"],
    "ESC + HSA": ["electronic_stability_control", "hill_start_assist"],
    "LDWS": ["lane_departure_warning"],
    "LKA": ["lane_keep_assist"],
    "DDAM": ["driver_attention_monitoring"],
    "My Safety": ["my_safety_button"],
    "ISA": ["speed_limiter_intelligent"],
    "Isofix tylne boczne": ["isofix_rear"],
    "eCall": ["emergency_call_ecall"],
    "Regulator i ogranicznik prędkości": ["cruise_control", "speed_limiter"],
    "Wspomaganie parkowania tyłem": ["rear_parking_sensors"],
    "Wspomaganie parkowania przodem": ["front_parking_sensors"],
    "Kamera cofania": ["rear_view_camera"],
    "Multiview kamera": ["360_camera_system"],
    "Monitorowanie martwego pola": ["blind_spot_monitoring"],
    "Automatyczny hamulec postojowy": ["electronic_parking_brake"],
    "System kontroli ciśnienia": ["tyre_pressure_monitoring_system"],
    "Zestaw do naprawy opony": ["tyre_repair_kit"],
    "Światła przeciwmgłowe": ["fog_lights"],
    "Lusterka elektryczne i podgrzewane": ["side_mirrors_electric_adjustment", "side_mirrors_heated"],
    "Klimatyzacja manualna": ["manual_air_conditioning"],
    "Automatyczna klimatyzacja": ["automatic_climate_control"],
    "Szyby przednie elektryczne / impuls kierowcy": ["front_windows_power", "one_touch_windows"],
    "Szyby tylne elektryczne": ["rear_windows_power"],
    "Szklany dach elektrycznie otwierany": ["glass_sunroof"],
    "Kierownica regulowana wysokość / głębokość": ["steering_wheel_height_adjustment", "steering_wheel_reach_adjustment"],
    "Fotel kierowcy wysokość / podłokietnik": ["driver_seat_height_adjustment", "front_centre_armrest"],
    "Konsola centralna z podłokietnikiem": ["front_centre_armrest"],
    "Podgrzewane przednie fotele": ["heated_front_seats"],
    "Podgrzewana kierownica": ["heated_steering_wheel"],
    "Keyless Entry": ["keyless_entry"],
    "Media Control": ["media_control_system"],
    "Media Display 10\"": ["media_display_system"],
    "Media Nav Live": ["media_nav_live"],
    "Automatyczne światła / wycieraczki": ["automatic_headlights", "rain_sensing_wipers"],
    "USB 1x / 2x": [],
    "Koło zapasowe + podnośnik (nie dotyczy LPG)": ["spare_wheel_type"],
}

VALUE_ROWS = {
    "Stalowe obręcze 15\" ELMA": "wheel_design",
    "Flexwheel 16\" ATARA": "wheel_design",
    "Flexwheel 16\" ATARA DARK": "wheel_design",
    "Aluminiowe 16\" TAMIA": "wheel_design",
    "Aluminiowe 16\" TAMIA czarne": "wheel_design",
    "Tapicerka czarna ze wstawkami denim": "upholstery_variant",
    "Tapicerka denim": "upholstery_variant",
    "Tapicerka czarna z geometrycznymi wzorami i pomarańczowymi przeszyciami": "upholstery_variant",
    "Specjalna tapicerka extreme": "upholstery_variant",
}

OPTION_ITEMS = {
    "Kamera cofania": ("sandero_rear_view_camera_option", "rear_view_camera"),
    "Koło zapasowe + podnośnik (nie dotyczy LPG)": ("sandero_spare_wheel_option", "spare_wheel_type"),
    "Szklany dach elektrycznie otwierany": ("sandero_glass_sunroof_option", "glass_sunroof"),
    "Media Nav Live": ("sandero_media_nav_live_option", "navigation_system"),
}

PACKAGE_PRICES = {
    "sandero_comfort_auto_package": 2000,
    "sandero_thermo_package": 1900,
    "sandero_winter_package": 1200,
    "sandero_media_nav_live_package": 1600,
    "sandero_easy_package": 1600,
}

# Literal components whose source cell is explicitly composite.  A component is
# materialized only when the source cell explicitly contains that component.
COMPOSITE = {
    "Automatyczny hamulec postojowy": {"●": "standard"},
    "Szyby przednie elektryczne / impuls kierowcy": {"●": "standard", "-": "not_available", "P": "optional"},
    "Kierownica regulowana wysokość / głębokość": {"●": "standard", "-": "not_available"},
    "Fotel kierowcy wysokość / podłokietnik": {"●": "standard", "-": "not_available"},
    "Automatyczne światła / wycieraczki": {"●": "standard"},
    "USB 1x / 2x": {},
}

CONFIGS = {
    "sandero_essential": ["sandero_iii_essential_tce100_manual"],
    "sandero_expression": [
        "sandero_iii_expression_tce100_manual",
        "sandero_iii_expression_ecog120_manual",
        "sandero_iii_expression_ecog120_automatic",
        "sandero_iii_expression_hybrid155_automatic",
    ],
    "sandero_journey": [
        "sandero_iii_journey_tce100_manual",
        "sandero_iii_journey_ecog120_manual",
        "sandero_iii_journey_ecog120_automatic",
        "sandero_iii_journey_hybrid155_automatic",
    ],
    "stepway_essential": [
        "sandero_stepway_iii_essential_tce110_manual",
        "sandero_stepway_iii_essential_ecog120_manual",
    ],
    "stepway_expression": [
        "sandero_stepway_iii_expression_tce110_manual",
        "sandero_stepway_iii_expression_ecog120_manual",
        "sandero_stepway_iii_expression_ecog120_automatic",
        "sandero_stepway_iii_expression_hybrid155_automatic",
    ],
    "stepway_extreme": [
        "sandero_stepway_iii_extreme_tce110_manual",
        "sandero_stepway_iii_extreme_ecog120_manual",
        "sandero_stepway_iii_extreme_ecog120_automatic",
        "sandero_stepway_iii_extreme_hybrid155_automatic",
    ],
}


def read_csv(name):
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def write_csv(name, fields, rows):
    with (MASTER / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def next_id(rows):
    return max((int(r["id"]) for r in rows), default=0) + 1


def norm(s):
    return re.sub(r"\s+", " ", s.strip().casefold())


def cell_parts(label, value):
    if " / " not in value:
        return [(label, value)]
    return [(label, x.strip()) for x in value.split(" / ")]


def status_for(value):
    if value == "●":
        return "standard"
    if value == "-":
        return "not_available"
    if value == "P":
        return "optional"
    if re.fullmatch(r"\d+(?: / \d+)?", value):
        return "optional"
    return None


def unique_append(rows, row):
    if any(r["code"] == row["code"] for r in rows):
        return False
    rows.append(row)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    capture = json.loads(SOURCE.read_text(encoding="utf-8"))
    av_fields, availability = read_csv("configuration_attribute_availability.csv")
    attr_fields, attributes = read_csv("attributes.csv")
    source_fields, sources = read_csv("sources.csv")
    rel_fields, relations = read_csv("source_configurations.csv")
    value_fields, values = read_csv("configuration_attribute_values.csv")
    item_fields, commercial_items = read_csv("commercial_items.csv")
    item_attr_fields, commercial_item_attributes = read_csv("commercial_item_attributes.csv")
    item_cfg_fields, commercial_item_configurations = read_csv("commercial_item_configurations.csv")

    known_attrs = {r["code"] for r in attributes}
    existing_value_keys = {(r["configuration_code"], r["attribute_code"], r["value"], r["observation_date"], r["source_code"]) for r in values}
    item_codes = {r["code"] for r in commercial_items}
    item_attr_keys = {(r["commercial_item_code"], r["attribute_code"]) for r in commercial_item_attributes}
    item_cfg_keys = {(r["commercial_item_code"], r["configuration_code"], r["price_date"], r["source_code"]) for r in commercial_item_configurations}
    existing = {
        (r["configuration_code"], r["attribute_code"], r["observation_date"], r["source_code"])
        for r in availability
    }
    source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

    if source_sha != capture["source"]["supplied_file_sha256"] and source_sha == "":
        raise SystemExit("unexpected source hash state")

    configs_by_column = CONFIGS
    rows = capture["equipment_matrix"]["rows"]
    columns = capture["equipment_matrix"]["columns"]

    added = 0
    skipped_existing = 0
    unresolved = []
    processed_configs = set()

    for column_index, column in enumerate(columns):
        for config in configs_by_column[column]:
            processed_configs.add(config)
            for row in rows:
                label, cells = row
                raw = str(cells[column_index])
                value_attr = {
                    'Stalowe obręcze 15" ELMA': 'wheel_design',
                    'Flexwheel 16" ATARA': 'wheel_design',
                    'Flexwheel 16" ATARA DARK': 'wheel_design',
                    'Aluminiowe 16" TAMIA': 'wheel_design',
                    'Aluminiowe 16" TAMIA czarne': 'wheel_design',
                    'Tapicerka czarna ze wstawkami denim': 'upholstery_variant',
                    'Tapicerka denim': 'upholstery_variant',
                    'Tapicerka czarna z geometrycznymi wzorami i pomarańczowymi przeszyciami': 'upholstery_variant',
                    'Specjalna tapicerka extreme': 'upholstery_variant',
                }.get(label)
                if value_attr:
                    if raw == '●' and value_attr in known_attrs:
                        key = (config, value_attr, label, DATE, SOURCE_CODE)
                        if key not in existing_value_keys:
                            values.append({
                                'id': str(next_id(values)),
                                'code': f'{config}_{value_attr}_20260811',
                                'configuration_code': config,
                                'attribute_code': value_attr,
                                'fuel_type_code': '',
                                'gear_number': '',
                                'value': label,
                                'observation_date': DATE,
                                'source_code': SOURCE_CODE,
                                'notes': 'Official Polish MY26 2026-08-11 price-list equipment matrix.',
                            })
                            existing_value_keys.add(key)
                    continue

                mapped_attrs = ROW_MAP.get(label, [])
                if not mapped_attrs:
                    unresolved.append((config, label, raw, 'no_canonical_mapping'))
                    continue

                parts = cell_parts(label, raw)
                if len(mapped_attrs) == len(parts):
                    pairs = zip(mapped_attrs, parts)
                elif len(mapped_attrs) > 1 and len(parts) == 1 and raw in {'●', '-', 'P'}:
                    pairs = ((attr, (label, raw)) for attr in mapped_attrs)
                else:
                    # Single-valued rows, including prices and package markers.
                    pairs = ((mapped_attrs[0], (label, raw)),)

                for attr, (_part_label, part_value) in pairs:
                    if attr not in known_attrs:
                        unresolved.append((config, label, raw, f"unknown_attribute:{attr}"))
                        continue
                    status = status_for(part_value)
                    if status is None:
                        # Text/colour/design values are retained as unresolved
                        # source evidence rather than projected into a boolean status.
                        unresolved.append((config, label, raw, "literal_value_requires_value_schema"))
                        continue
                    key = (config, attr, DATE, SOURCE_CODE)
                    if key in existing:
                        skipped_existing += 1
                        continue
                    note = (
                        "Official Polish MY26 2026-08-11 price-list equipment matrix. "
                        f"Source row: {label!r}; source cell: {raw!r}; normalized status: {status}."
                    )
                    if part_value not in {"●", "-", "P"}:
                        note += " Source cell contains an option price; commercial amount is preserved literally in source evidence."
                    code = f"{config}_{attr}_20260811"
                    unique_append(availability, {
                        "id": str(next_id(availability)),
                        "code": code,
                        "configuration_code": config,
                        "attribute_code": attr,
                        "availability_status": status,
                        "observation_date": DATE,
                        "source_code": SOURCE_CODE,
                        "notes": note,
                    })
                    existing.add(key)
                    added += 1

    # Register the documentary source and one relationship per catalogue configuration.
    if not any(r["code"] == SOURCE_CODE for r in sources):
        sources.append({
            "id": str(next_id(sources)),
            "code": SOURCE_CODE,
            "source_type": "price_list",
            "title": capture["source"]["title"],
            "publisher": capture["source"]["publisher"],
            "market": capture["source"]["market"],
            "document_date": DATE,
            "external_reference": capture["source"]["external_reference"],
            "file_path": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "sha256": source_sha,
            "status": "active",
            "notes": "Full official Polish MY26 price-list extract; equipment matrix is documentary source for dated availability observations.",
        })

    for config in sorted(processed_configs):
        if not any(r["source_code"] == SOURCE_CODE and r["configuration_code"] == config for r in relations):
            relations.append({
                "id": str(next_id(relations)),
                "source_code": SOURCE_CODE,
                "configuration_code": config,
                "relationship": "documents",
                "notes": "Configuration explicitly present in the 2026-08-11 official price-list matrix.",
            })

    summary = {
        "source_code": SOURCE_CODE,
        "source_date": DATE,
        "source_extract_sha256": source_sha,
        "source_document_sha256": capture["source"]["supplied_file_sha256"],
        "matrix_columns": len(columns),
        "matrix_rows": len(rows),
        "catalogue_configurations": len(processed_configs),
        "availability_added": added,
        "availability_existing_skipped": skipped_existing,
        "unresolved_source_cells": len(unresolved),
        "hybrid155_existing_rows_preserved": sum(
            r["source_code"] == SOURCE_CODE and "hybrid155" in r["configuration_code"]
            for r in availability
        ),
        "canonical_mapping_policy": "Only explicit, unambiguous mappings are materialized; unresolved literal/design/colour cells remain source evidence.",
    }
    report = {
        "schema_version": 1,
        "package_id": "sandero_stepway_price_list_matrix_import_20260811",
        "summary": summary,
        "unresolved_cells": [
            {"configuration_code": c, "source_row": l, "source_cell": v, "reason": reason}
            for c, l, v, reason in unresolved
        ],
    }

    if args.apply:
        write_csv("sources.csv", source_fields, sources)
        write_csv("source_configurations.csv", rel_fields, relations)
        write_csv("configuration_attribute_availability.csv", av_fields, availability)
        write_csv("configuration_attribute_values.csv", value_fields, values)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
