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


def collect() -> tuple[list[dict[str, str]], list[dict[str, str]], int]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    fields, existing = load_values()
    required_fields = {
        "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
        "gear_number", "value", "observation_date", "source_code", "notes",
    }
    missing_fields = sorted(required_fields - set(fields))
    if missing_fields:
        raise ValueError(f"configuration_attribute_values.csv missing required fields: {missing_fields}")

    existing_by_slot: dict[tuple[str, str, str, str], set[str]] = {}
    existing_codes = {r.get("code", "") for r in existing}
    for row in existing:
        slot = (
            row["configuration_code"],
            row["attribute_code"],
            row.get("fuel_type_code", ""),
            row.get("gear_number", ""),
        )
        existing_by_slot.setdefault(slot, set()).add(row.get("value", "").strip())
    next_id = max((int(r["id"]) for r in existing if r.get("id", "").isdigit()), default=0) + 1

    source_drive_values = set()
    current_drive_values = {
        r.get("value", "").strip()
        for r in existing
        if r.get("attribute_code") == "drive_layout" and r.get("value", "").strip()
    }
    rows: list[dict[str, str]] = []
    deferred: list[dict[str, str]] = []
    occupied = 0
    conflicts: list[str] = []

    for cfg in capture["configurations"]:
        code = cfg["configuration_code"]
        for group in cfg["technical"]:
            for item in group["items"]:
                mapping = MAPPING.get(item["label"])
                if not mapping:
                    continue
                attr, kind = mapping
                raw_value = item["value"].strip()
                if attr == "drive_layout":
                    source_drive_values.add(raw_value)
                value = parse(raw_value, kind)
                if value is None:
                    deferred.append({
                        "configuration_code": code,
                        "label": item["label"],
                        "value": raw_value,
                        "reason": "composite_or_non_scalar_value",
                    })
                    continue
                slot = (code, attr, "", "")
                current_values = existing_by_slot.get(slot)
                if current_values is not None:
                    occupied += 1
                    if value not in current_values:
                        conflicts.append(
                            f"{code}/{attr}: source={value!r}, current={sorted(current_values)!r}"
                        )
                    continue
                candidate_code = f"{code}_{attr}_20260809_full_modal_residual"
                if candidate_code in existing_codes:
                    raise ValueError(f"duplicate materialization code: {candidate_code}")
                rows.append({
                    "id": str(next_id),
                    "code": candidate_code,
                    "configuration_code": code,
                    "attribute_code": attr,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": value,
                    "observation_date": DATE,
                    "source_code": SOURCE,
                    "notes": f"Exact full-modal residual scalar/source-state mapping: {item['label']}: {raw_value}",
                })
                existing_by_slot[slot] = {value}
                existing_codes.add(candidate_code)
                next_id += 1

    unresolved_drive_values = sorted(source_drive_values - current_drive_values)
    if unresolved_drive_values:
        raise ValueError(
            "drive_layout source vocabulary is not fully represented in current master data: "
            + ", ".join(unresolved_drive_values)
        )
    if conflicts:
        raise ValueError("occupied residual technical slots disagree with source values: " + "; ".join(conflicts))

    return rows, deferred, occupied


def apply() -> dict[str, int]:
    fields, existing = load_values()
    rows, deferred, occupied = collect()
    if rows:
        existing.extend(rows)
        with VALUES.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(existing)
    return {"added": len(rows), "deferred_non_scalar": len(deferred), "occupied_candidates": occupied}


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
    rows, deferred, occupied = collect()
    return {
        "candidate_rows": candidates,
        "materialized_rows": materialized,
        "pending_rows": len(rows),
        "occupied_candidates": occupied,
        "currently_deferred_non_scalar": len(deferred),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = apply() if args.apply else {}
    print(json.dumps({**result, **verify()}, ensure_ascii=False, sort_keys=True))
