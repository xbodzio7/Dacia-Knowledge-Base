from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "project/sources/dacia-pl-sandero-stepway-full-technical-standard-equipment-20260809.json"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"
SOURCE = "src_pl_sandero_stepway_full_modal_20260809"
DATE = "2026-08-09"

MAPPING = {
    "1000 m ze startu zatrzymanego (s)": ("standing_km", "number"),
    "Długość całkowita": ("overall_length", "integer"),
    "Liczba drzwi": ("number_of_doors", "integer"),
    "Liczba zaworów": ("total_valve_count", "integer"),
    "Maksymalna ładowność (kg)": ("maximum_payload", "integer"),
    "Norma emisji spalin": ("emission_standard", "text"),
    "Opony standardowe": ("standard_tyre_specification", "text"),
    "Poziom hałasu przy 50 km/h (dB)": ("noise_level_at_50_kmh", "number"),
    "Procedura homologacji": ("homologation_procedure_code", "text"),
    "Protokół homologacji": ("homologation_protocol", "text"),
    "Przyspieszenie 0-100 km/h (s)": ("acceleration_0_100", "number"),
    "Rodzaj nadwozia": ("body_style_source_stated", "text"),
    "Rodzaj napędu": ("drive_layout", "text"),
    "Rodzaj paliwa": ("fuel_type", "text"),
    "Rodzaj skrzyni biegów": ("gearbox_source_description", "text"),
    "Rozstaw osi": ("wheelbase", "integer"),
    "Szerokość dolnej części bagażnika": ("cargo_floor_width", "integer"),
    "Typ techniczny": ("technical_type_code", "text"),
    "Wysokość całkowita": ("overall_height_source_stated", "text"),
    "Zwis przedni": ("front_overhang", "integer"),
    "Zwis tylny": ("rear_overhang", "integer"),
}


def parse(value: str, kind: str) -> str | None:
    value = value.strip()
    if kind == "text":
        return value or None
    value = value.replace(",", ".")
    if kind == "integer":
        return value if re.fullmatch(r"-?\d+", value) else None
    if kind == "number":
        return value if re.fullmatch(r"-?\d+(?:\.\d+)?", value) else None
    raise ValueError(kind)


def load_values() -> tuple[list[str], list[dict[str, str]]]:
    with VALUES.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def collect() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    _fields, existing = load_values()
    existing_slots = {
        (r["configuration_code"], r["attribute_code"], r.get("fuel_type_code", ""), r.get("gear_number", ""))
        for r in existing
    }
    next_id = max((int(r["id"]) for r in existing), default=0) + 1
    rows: list[dict[str, str]] = []
    deferred: list[dict[str, str]] = []
    for cfg in capture["configurations"]:
        code = cfg["configuration_code"]
        for group in cfg["technical"]:
            for item in group["items"]:
                mapping = MAPPING.get(item["label"])
                if not mapping:
                    continue
                attr, kind = mapping
                value = parse(item["value"], kind)
                if value is None:
                    deferred.append({"configuration_code": code, "label": item["label"], "value": item["value"], "reason": "composite_or_non_scalar_value"})
                    continue
                slot = (code, attr, "", "")
                if slot in existing_slots:
                    continue
                rows.append({
                    "id": str(next_id),
                    "code": f"{code}_{attr}_20260809_full_modal_residual",
                    "configuration_code": code,
                    "attribute_code": attr,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": value,
                    "observation_date": DATE,
                    "source_code": SOURCE,
                    "notes": f"Exact full-modal residual scalar/source-state mapping: {item['label']}: {item['value']}",
                })
                existing_slots.add(slot)
                next_id += 1
    return rows, deferred


def apply() -> dict[str, int]:
    fields, existing = load_values()
    rows, deferred = collect()
    if rows:
        existing.extend(rows)
        with VALUES.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(existing)
    return {"added": len(rows), "deferred_non_scalar": len(deferred)}


def verify() -> dict[str, int]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    candidates = 0
    for cfg in capture["configurations"]:
        for group in cfg["technical"]:
            for item in group["items"]:
                if item["label"] in MAPPING:
                    candidates += 1
    _fields, existing = load_values()
    materialized = sum(
        1 for r in existing
        if r.get("source_code") == SOURCE and r.get("code", "").endswith("_residual")
    )
    _rows, deferred = collect()
    return {"candidate_rows": candidates, "materialized_rows": materialized, "currently_deferred_non_scalar": len(deferred)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = apply() if args.apply else {}
    print(json.dumps({**result, **verify()}, ensure_ascii=False, sort_keys=True))
