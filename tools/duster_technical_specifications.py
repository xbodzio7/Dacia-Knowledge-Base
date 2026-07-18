#!/usr/bin/env python3
"""Generate and verify source-backed Duster technical-value specifications."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import import_configuration_values as importer

SOURCE_CODE = "src_pl_duster_price_my26_py25_20260206"
SOURCE_DATE = "2026-02-06"
FIRST_ID = 311
SPEC_PREFIX = "duster-page"

SECTIONS = {
    "engine_displacement": "SILNIKI",
    "cylinder_count": "SILNIKI",
    "total_valve_count": "SILNIKI",
    "engine_power": "SILNIKI",
    "max_power_rpm": "SILNIKI",
    "engine_torque": "SILNIKI",
    "max_torque_rpm": "SILNIKI",
    "traction_motor_power": "SILNIKI",
    "starter_generator_power": "SILNIKI",
    "top_speed": "OSIĄGI",
    "acceleration_0_100": "OSIĄGI",
    "standing_km": "OSIĄGI",
    "fuel_tank_capacity": "ZUŻYCIE PALIWA I EMISJA CO2",
    "co2_emissions": "ZUŻYCIE PALIWA I EMISJA CO2",
    "fuel_consumption_combined": "ZUŻYCIE PALIWA I EMISJA CO2",
    "cargo_volume_vda": "POJEMNOŚĆ BAGAŻNIKA",
    "braked_trailer_weight": "MASY",
}

DATA: dict[int, dict[str, dict[str, list[tuple[str, str, str, str | None]]]]] = {
    8: {
        "Eco-G 100 4x2": {
            "engine_displacement": [("999", "", "999", None)],
            "cylinder_count": [("3", "", "3 / 12", None)],
            "total_valve_count": [("12", "", "3 / 12", None)],
            "engine_power": [("74", "", "74 (100)", None)],
            "max_power_rpm": [("5000", "", "przy 5 000", None)],
            "engine_torque": [("170", "", "170", None)],
            "max_torque_rpm": [("2000", "", "przy 2 000", None)],
            "top_speed": [("163", "petrol", "163 / 168 (LPG)", None), ("168", "lpg", "163 / 168 (LPG)", None)],
            "acceleration_0_100": [("14", "petrol", "14 / 13,2 (LPG)", None), ("13.2", "lpg", "14 / 13,2 (LPG)", None)],
            "standing_km": [("37.2", "petrol", "37,2 / 36 (LPG)", None), ("36", "lpg", "37,2 / 36 (LPG)", None)],
            "fuel_tank_capacity": [("50", "petrol", "50 / 51 (LPG)", None), ("51", "lpg", "50 / 51 (LPG)", None)],
            "co2_emissions": [("148", "petrol", "148 / 128 (LPG)", None), ("128", "lpg", "148 / 128 (LPG)", None)],
            "fuel_consumption_combined": [("6.5", "petrol", "6,5 / 7,9 (LPG)", None), ("7.9", "lpg", "6,5 / 7,9 (LPG)", None)],
            "cargo_volume_vda": [("453", "", "453", None)],
            "braked_trailer_weight": [("1200", "", "1200", None)],
        },
        "mild hybrid 130 4x2": {
            "engine_displacement": [("1199", "", "1 199", None)],
            "cylinder_count": [("3", "", "3 / 12", None)],
            "total_valve_count": [("12", "", "3 / 12", None)],
            "engine_power": [("96", "", "96 (130)", None)],
            "max_power_rpm": [("4600", "", "przy 4 600", None)],
            "engine_torque": [("230", "", "230", None)],
            "max_torque_rpm": [("2250", "", "przy 2 250", None)],
            "top_speed": [("174", "", "174", None)],
            "acceleration_0_100": [("9.9", "", "9,9", None)],
            "standing_km": [("31.3", "", "31,3", None)],
            "fuel_tank_capacity": [("48.5", "", "48,5", None)],
            "co2_emissions": [("124", "", "124", None)],
            "fuel_consumption_combined": [("5.5", "", "5,5", None)],
            "cargo_volume_vda": [("517", "", "517", None)],
            "braked_trailer_weight": [("1500", "", "1500", None)],
        },
        "mild hybrid 130 4x4": {
            "engine_displacement": [("1199", "", "1 199", None)],
            "cylinder_count": [("3", "", "3 / 12", None)],
            "total_valve_count": [("12", "", "3 / 12", None)],
            "engine_power": [("96", "", "96 (130)", None)],
            "max_power_rpm": [("4600", "", "przy 4 600", None)],
            "engine_torque": [("230", "", "230", None)],
            "max_torque_rpm": [("2250", "", "przy 2 250", None)],
            "top_speed": [("174", "", "174", None)],
            "acceleration_0_100": [("11.0", "", "11,0", None)],
            "standing_km": [("32.6", "", "32,6", None)],
            "fuel_tank_capacity": [("48.5", "", "48,5", None)],
            "co2_emissions": [("137", "", "137", None)],
            "fuel_consumption_combined": [("6.1", "", "6,1", None)],
            "cargo_volume_vda": [("456", "", "456", None)],
            "braked_trailer_weight": [("1500", "", "1500", None)],
        },
        "hybrid 140 4x2": {
            "engine_displacement": [("1598", "", "1 598", None)],
            "cylinder_count": [("4", "", "4 / 16", None)],
            "total_valve_count": [("16", "", "4 / 16", None)],
            "engine_power": [("69", "", "69 (90)", None)],
            "max_power_rpm": [("5600", "", "przy 5600", None)],
            "top_speed": [("160", "", "160", None)],
            "acceleration_0_100": [("10.1", "", "10,1", None)],
            "standing_km": [("32.3", "", "32,3", None)],
            "fuel_tank_capacity": [("48.5", "", "48,5", None)],
            "co2_emissions": [("113", "", "113", None)],
            "fuel_consumption_combined": [("5.0", "", "5,0", None)],
            "cargo_volume_vda": [("430", "", "430", None)],
            "braked_trailer_weight": [("750", "", "750", None)],
            "traction_motor_power": [("36", "", "E-Motor = 36 kW", None)],
            "starter_generator_power": [("15", "", "HSG = 15 kW", None)],
        },
    },
    9: {
        "Eco-G 120 4x2": {
            "engine_displacement": [("1199", "", "1 199", None)],
            "cylinder_count": [("3", "", "3 / 12", None)],
            "total_valve_count": [("12", "", "3 / 12", None)],
            "engine_power": [("90", "lpg", "LPG: 90 (120), PB: 84 (114)", None), ("84", "petrol", "LPG: 90 (120), PB: 84 (114)", None)],
            "max_power_rpm": [("5500", "", "przy 5 500", None)],
            "engine_torque": [("197", "lpg", "197 (LPG), 190 (PB)", None), ("190", "petrol", "197 (LPG), 190 (PB)", None)],
            "max_torque_rpm": [("1750", "", "przy 1 750", None)],
            "top_speed": [("180", "", "180", None)],
            "acceleration_0_100": [("11", "", "11", None)],
            "fuel_tank_capacity": [("50", "petrol", "benzyna: 50L, LPG: 50L", None), ("50", "lpg", "benzyna: 50L, LPG: 50L", None)],
            "co2_emissions": [("122", "", "122", "2025-10-01")],
            "fuel_consumption_combined": [("7.7", "", "7,7", "2025-10-01")],
            "cargo_volume_vda": [("453", "", "453", None)],
            "braked_trailer_weight": [("1500", "", "1500", None)],
        },
        "mild hybrid 140 4x2": {
            "engine_displacement": [("1199", "", "1 199", None)],
            "cylinder_count": [("3", "", "3 / 12", None)],
            "total_valve_count": [("12", "", "3 / 12", None)],
            "engine_power": [("103", "", "103 (140)", None)],
            "max_power_rpm": [("4500", "", "przy 4 500", None)],
            "engine_torque": [("230", "", "230", None)],
            "max_torque_rpm": [("1900", "", "przy 1900", None)],
            "top_speed": [("180", "", "180", None)],
            "acceleration_0_100": [("9.4", "", "9,4", None)],
            "fuel_tank_capacity": [("50", "", "50", None)],
            "co2_emissions": [("125", "", "125", "2025-10-01")],
            "fuel_consumption_combined": [("5.5", "", "5,5", "2025-10-01")],
            "cargo_volume_vda": [("517", "", "517", None)],
            "braked_trailer_weight": [("1500", "", "1500", None)],
        },
        "hybrid 155 4x2": {
            "engine_displacement": [("1789", "", "1 789", None)],
            "cylinder_count": [("4", "", "4 / 16", None)],
            "total_valve_count": [("16", "", "4 / 16", None)],
            "engine_power": [("80", "", "80 (109)", None)],
            "max_power_rpm": [("5300", "", "przy 5300", None)],
            "engine_torque": [("172", "", "172", None)],
            "max_torque_rpm": [("3000", "", "przy 3000", None)],
            "top_speed": [("180", "", "180", None)],
            "acceleration_0_100": [("9.4", "", "9,4", None)],
            "fuel_tank_capacity": [("50", "", "50", None)],
            "co2_emissions": [("109", "", "109", "2025-10-01")],
            "fuel_consumption_combined": [("4.8", "", "4,8", "2025-10-01")],
            "cargo_volume_vda": [("430", "", "430", None)],
            "braked_trailer_weight": [("750", "", "750", None)],
            "traction_motor_power": [("35", "", "E-Motor = 35 kW", None)],
            "starter_generator_power": [("15", "", "HSG = 15 kW", None)],
        },
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def expected_specs(repository: Path) -> list[tuple[Path, dict[str, Any]]]:
    master = repository / "data" / "master"
    spec_dir = repository / "data" / "imports" / "configuration_values"
    groups: dict[str, list[str]] = {}
    for row in read_csv(master / "configurations.csv"):
        if row["code"].startswith("duster_iii_"):
            groups.setdefault(row["powertrain_label"], []).append(row["code"])
    for codes in groups.values():
        codes.sort()
    attributes = {row["code"]: row for row in read_csv(master / "attributes.csv")}

    result: list[tuple[Path, dict[str, Any]]] = []
    next_id = FIRST_ID
    for page in sorted(DATA):
        page_attributes = sorted({code for group in DATA[page].values() for code in group})
        for attribute_code in page_attributes:
            by_date: dict[str, list[dict[str, str]]] = {}
            for group, attribute_map in DATA[page].items():
                for value, fuel, source_text, date_override in attribute_map.get(attribute_code, []):
                    for configuration_code in groups[group]:
                        item = {
                            "configuration_code": configuration_code,
                            "source_code": SOURCE_CODE,
                            "value": value,
                            "source_text": source_text,
                        }
                        if fuel:
                            item["fuel_type_code"] = fuel
                        by_date.setdefault(date_override or SOURCE_DATE, []).append(item)
            for observation_date, rows in sorted(by_date.items()):
                rows.sort(key=lambda row: (row["configuration_code"], row.get("fuel_type_code", "")))
                contract = attributes[attribute_code]
                suffix = "" if observation_date == SOURCE_DATE else f"-asof-{observation_date.replace('-', '')}"
                name = f"duster-page{page}-{attribute_code.replace('_', '-')}-20260206{suffix}.json"
                payload = {
                    "version": 1,
                    "kind": "configuration_attribute_values",
                    "id_start": next_id,
                    "attribute_code": attribute_code,
                    "attribute_contract": {
                        "data_type": contract["data_type"],
                        "unit": contract["unit"],
                        "status": "active",
                    },
                    "observation_date": observation_date,
                    "fuel_type_code": "",
                    "source_page": page,
                    "source_section": SECTIONS[attribute_code],
                    "notes_template": "Source page {page}, section {section}: {source_text}",
                    "rows": rows,
                }
                result.append((spec_dir / name, payload))
                next_id += len(rows)
    if len(result) != 33 or next_id != 703:
        raise RuntimeError(f"unexpected generated scope: {len(result)} specs, next ID {next_id}")
    return result


def verify_source(repository: Path, payloads: Sequence[dict[str, Any]]) -> None:
    sources = {row["code"]: row for row in read_csv(repository / "data" / "master" / "sources.csv")}
    source = sources[SOURCE_CODE]
    path = repository / source["file_path"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != source["sha256"]:
        raise RuntimeError("registered Duster source SHA-256 differs")
    page_texts = {
        page: [importer._compact_text(text) for _, text in importer.extract_page_candidates(path, page)]
        for page in (8, 9)
    }
    for payload in payloads:
        section = importer._compact_text(payload["source_section"])
        for row in payload["rows"]:
            source_text = importer._compact_text(row["source_text"])
            if not any(section in text and source_text in text for text in page_texts[payload["source_page"]]):
                raise RuntimeError(f"source text not found: {payload['source_page']} {row['source_text']}")


def run(repository: Path, *, apply: bool) -> None:
    expected = expected_specs(repository)
    expected_paths = {path for path, _ in expected}
    existing_paths = set((repository / "data" / "imports" / "configuration_values").glob(f"{SPEC_PREFIX}*.json"))
    if existing_paths - expected_paths:
        raise RuntimeError(f"unexpected Duster specs: {sorted(existing_paths - expected_paths)}")

    payloads = []
    for path, payload in expected:
        rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if apply:
            path.write_text(rendered, encoding="utf-8")
        elif not path.is_file() or path.read_text(encoding="utf-8") != rendered:
            raise RuntimeError(f"specification differs: {path}")
        payloads.append(payload)

    verify_source(repository, payloads)
    total = 0
    for path, _ in expected:
        spec = importer.load_spec(path)
        plan = importer.apply_import(repository, spec) if apply else importer.verify_import(repository, spec)
        total += len(plan.expected_rows)
    if total != 392:
        raise RuntimeError(f"unexpected observation count: {total}")
    print(f"Duster technical specifications: PASS ({len(expected)} specs, {total} rows)")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--apply", action="store_true", help="write specifications and append missing rows")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run(args.repository.resolve(), apply=args.apply)
    except (OSError, RuntimeError, importer.ImportSpecError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
