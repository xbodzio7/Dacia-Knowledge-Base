from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "project/sources/dacia-pl-sandero-stepway-full-technical-standard-equipment-20260809.json"
ATTRIBUTES = ROOT / "data/master/attributes.csv"
VALUES = ROOT / "data/master/configuration_attribute_values.csv"

MAPPING = {
    "1000 m ze startu zatrzymanego (s)": "standing_km",
    "Długość całkowita": "overall_length",
    "Liczba drzwi": "number_of_doors",
    "Liczba zaworów": "total_valve_count",
    "Maksymalna ładowność (kg)": "maximum_payload",
    "Norma emisji spalin": "emission_standard",
    "Opony standardowe": "standard_tyre_specification",
    "Poziom hałasu przy 50 km/h (dB)": "noise_level_at_50_kmh",
    "Procedura homologacji": "homologation_procedure_code",
    "Protokół homologacji": "homologation_protocol",
    "Przyspieszenie 0-100 km/h (s)": "acceleration_0_100",
    "Rodzaj nadwozia": "body_style_source_stated",
    "Rodzaj napędu": "drive_layout",
    "Rodzaj paliwa": "fuel_type",
    "Rodzaj skrzyni biegów": "gearbox_source_description",
    "Rozstaw osi": "wheelbase",
    "Szerokość dolnej części bagażnika": "cargo_floor_width",
    "Typ techniczny": "technical_type_code",
    "Wysokość całkowita": "overall_height_source_stated",
    "Zwis przedni": "front_overhang",
    "Zwis tylny": "rear_overhang",
}

# These mappings require explicit semantic reconciliation before promotion.
# In particular, drive_layout already caused a value-vocabulary failure in the
# abandoned partial attempt; this audit deliberately does not normalize values.
REVIEW_REQUIRED = {
    "Rodzaj napędu": "drive_layout_value_vocabulary_requires_reconciliation",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def collect_candidates() -> list[dict[str, str]]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    result: list[dict[str, str]] = []
    for cfg in capture["configurations"]:
        for group in cfg["technical"]:
            for item in group["items"]:
                if item["label"] in MAPPING:
                    result.append({
                        "configuration_code": cfg["configuration_code"],
                        "label": item["label"],
                        "attribute_code": MAPPING[item["label"]],
                        "value": item["value"],
                    })
    return result


def audit() -> dict[str, object]:
    candidates = collect_candidates()
    attributes = {row["code"] for row in load_csv(ATTRIBUTES)}
    existing = load_csv(VALUES)
    existing_slots = {
        (row["configuration_code"], row["attribute_code"], row.get("fuel_type_code", ""), row.get("gear_number", ""))
        for row in existing
    }
    missing_attributes = sorted({row["attribute_code"] for row in candidates} - attributes)
    collisions = [
        row for row in candidates
        if (row["configuration_code"], row["attribute_code"], "", "") in existing_slots
    ]
    by_label: dict[str, dict[str, object]] = {}
    for row in candidates:
        entry = by_label.setdefault(row["label"], {"attribute_code": row["attribute_code"], "count": 0, "values": []})
        entry["count"] = int(entry["count"]) + 1
        if row["value"] not in entry["values"]:
            entry["values"].append(row["value"])
    return {
        "package_id": "sandero_stepway_full_modal_residual_technical_reconciliation_001",
        "reviewed_on": "2026-09-13",
        "source": "src_pl_sandero_stepway_full_modal_20260809",
        "candidate_rows": len(candidates),
        "mapping_labels": len(MAPPING),
        "attributes_missing_from_current_dictionary": missing_attributes,
        "already_occupied_exact_slots": len(collisions),
        "review_required": REVIEW_REQUIRED,
        "promotion_allowed": False,
        "materialization_performed": False,
        "per_label": by_label,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2, sort_keys=True))
