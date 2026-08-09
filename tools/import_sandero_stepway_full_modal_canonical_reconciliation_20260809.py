from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
CAPTURE = ROOT / "project/sources/dacia-pl-sandero-stepway-full-technical-standard-equipment-20260809.json"
REPORT = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"
SOURCE_CODE = "src_pl_sandero_stepway_full_technical_standard_equipment_20260809"
DATE = "2026-08-09"

# Only unambiguous scalar labels are normalized. Enum-like, compound/model-qualified,
# and otherwise semantically ambiguous source rows remain literal evidence in CAPTURE.
TECHNICAL_MAP = {
    "pojemność zbiornika paliwa (l)": ("fuel_tank_capacity", "decimal"),
    "Liczba drzwi": ("number_of_doors", "integer"),
    "Średnica zawracania (m)": ("turning_circle", "decimal"),
    "Opony standardowe": ("standard_tyre_specification", "string"),
    "Zwis przedni": ("front_overhang", "integer"),
    "Długość całkowita": ("vehicle_length", "integer"),
    "Zwis tylny": ("rear_overhang", "integer"),
    "Rozstaw osi": ("wheelbase", "integer"),
    "Liczba miejsc siedzących": ("number_of_seats", "integer"),
    "Liczba biegów do przodu": ("gear_count", "integer"),
    "Poziom hałasu przy 50 km/h (dB)": ("noise_level_at_50_kmh", "decimal"),
    "Liczba zaworów": ("total_valve_count", "integer"),
    "Moc maksymalna kW (KM)": ("engine_power", "first_integer"),
    "Maksymalny moment obrotowy w Nm": ("engine_torque", "first_integer"),
    "Liczba cylindrów": ("cylinder_count", "integer"),
    "Pojemność skokowa (cm3)": ("engine_displacement", "integer"),
    "Emisja CO2 cykl mieszany WLTP (g/km)": ("co2_emissions", "decimal"),
    "Zużycie paliwa cykl mieszany WLTP (l/100 km)": ("fuel_consumption_combined", "decimal"),
    "Prędkość maksymalna (km/h)": ("top_speed", "integer"),
    "1000 m ze startu zatrzymanego (s)": ("standing_km", "decimal"),
    "Przyspieszenie 0-100 km/h (s)": ("acceleration_0_100", "decimal"),
    "Maksymalna masa przyczepy bez hamulca (kg)": ("unbraked_trailer_weight", "integer"),
    "Maksymalna masa całkowita zespołu pojazdów (kg)": ("gross_train_weight", "integer"),
    "Maksymalna masa przyczepy z hamulcem (kg)": ("braked_trailer_weight", "integer"),
    "Maksymalna ładowność (kg)": ("maximum_payload", "integer"),
    "Minimalna masa pojazdu gotowego do jazdy (bez opcji) (kg)": ("minimum_kerb_weight", "integer"),
    "Maksymalna masa całkowita pojazdu (kg)": ("gross_vehicle_weight", "integer"),
}

NEGATIVE_EQUIPMENT_MARKERS = (
    "nieogrzewan",
    "nieskładane",
    "bez automatycznego",
    "brak świateł",
    "bez podłogi bagażnika",
    "bez keyless entry",
)


def read_csv(name: str):
    path = MASTER / name
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(name: str, fields, rows):
    with (MASTER / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def next_id(rows):
    return max((int(row["id"]) for row in rows), default=0) + 1


def normalize_value(value: str, kind: str) -> str:
    text = value.strip()
    if kind == "string":
        return text
    if kind == "first_integer":
        match = re.search(r"-?\d+", text)
        if not match:
            raise ValueError(text)
        return str(int(match.group(0)))
    normalized = text.replace(",", ".")
    if kind == "integer":
        if not re.fullmatch(r"-?\d+", normalized):
            raise ValueError(text)
        return str(int(normalized))
    if kind == "decimal":
        if not re.fullmatch(r"-?\d+(?:\.\d+)?", normalized):
            raise ValueError(text)
        number = float(normalized)
        return str(int(number)) if number.is_integer() else (f"{number:.6f}".rstrip("0").rstrip("."))
    raise ValueError(kind)


def exact_reviewed_equipment_map(existing_rows):
    mapping = defaultdict(set)
    note_pattern = re.compile(r"^Source page \d+:\s*(.+)$")
    for row in existing_rows:
        if row["availability_status"] != "standard":
            continue
        match = note_pattern.match(row.get("notes", "").strip())
        if match:
            mapping[match.group(1)].add(row["attribute_code"])
    return mapping


def negative_equipment(text: str) -> bool:
    lowered = text.casefold()
    return any(marker in lowered for marker in NEGATIVE_EQUIPMENT_MARKERS)


def build():
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    tables = {
        name: read_csv(name)
        for name in (
            "sources.csv",
            "source_configurations.csv",
            "configuration_attribute_values.csv",
            "configuration_attribute_availability.csv",
        )
    }
    sources = tables["sources.csv"][1]
    source_configurations = tables["source_configurations.csv"][1]
    values = tables["configuration_attribute_values.csv"][1]
    availability = tables["configuration_attribute_availability.csv"][1]

    if not any(row["code"] == SOURCE_CODE for row in sources):
        sources.append({
            "id": str(next_id(sources)),
            "code": SOURCE_CODE,
            "source_type": "web_snapshot",
            "title": "Dacia Polska full Sandero and Sandero Stepway technical and standard-equipment configurator snapshot",
            "publisher": "Dacia",
            "market": "PL",
            "document_date": DATE,
            "external_reference": ";".join(configuration["observed_url"] for configuration in capture["configurations"]),
            "file_path": CAPTURE.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
            "status": "active",
            "notes": "Literal full-modal configurator snapshot. Canonical reconciliation imports only exact safe matches; ambiguous evidence remains in the source artifact.",
        })

    sc_next = next_id(source_configurations)
    sc_added = 0
    for configuration in capture["configurations"]:
        code = configuration["configuration_code"]
        if any(row["source_code"] == SOURCE_CODE and row["configuration_code"] == code for row in source_configurations):
            continue
        source_configurations.append({
            "id": str(sc_next + sc_added),
            "source_code": SOURCE_CODE,
            "configuration_code": code,
            "relationship": "documents",
            "notes": f"Exact full technical and standard-equipment configurator state observed {DATE}; literal URL retained in source snapshot.",
        })
        sc_added += 1

    equipment_map = exact_reviewed_equipment_map(availability)
    value_next = next_id(values)
    availability_next = next_id(availability)
    value_added = 0
    availability_added = 0
    technical_total = 0
    equipment_total = 0
    unresolved_technical = []
    unresolved_equipment = []
    negative_evidence = []

    for configuration in capture["configurations"]:
        configuration_code = configuration["configuration_code"]
        for group in configuration["technical"]:
            for item in group["items"]:
                technical_total += 1
                label = item["label"]
                raw_value = item["value"]
                mapping = TECHNICAL_MAP.get(label)
                if mapping is None:
                    unresolved_technical.append({"configuration_code": configuration_code, "group": group["group"], "label": label, "value": raw_value, "reason": "no_explicit_safe_mapping"})
                    continue
                attribute_code, kind = mapping
                # Compound/model-qualified values must remain literal evidence.
                if "(Sandero)" in raw_value or "(Stepway)" in raw_value or ("/" in raw_value and kind != "string"):
                    unresolved_technical.append({"configuration_code": configuration_code, "group": group["group"], "label": label, "value": raw_value, "reason": "compound_or_model_qualified_value"})
                    continue
                try:
                    normalized = normalize_value(raw_value, kind)
                except ValueError:
                    unresolved_technical.append({"configuration_code": configuration_code, "group": group["group"], "label": label, "value": raw_value, "reason": "value_not_safe_for_declared_type"})
                    continue
                row_code = f"{configuration_code}_{attribute_code}_20260809_full_configurator"
                if any(row["code"] == row_code for row in values):
                    continue
                values.append({
                    "id": str(value_next + value_added),
                    "code": row_code,
                    "configuration_code": configuration_code,
                    "attribute_code": attribute_code,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": normalized,
                    "observation_date": DATE,
                    "source_code": SOURCE_CODE,
                    "notes": f"Exact full-modal configurator technical row: {label} = {raw_value}. No cross-configuration projection.",
                })
                value_added += 1

        for group in configuration["equipment"]:
            for text in group["items"]:
                equipment_total += 1
                if negative_equipment(text):
                    negative_evidence.append({"configuration_code": configuration_code, "group": group["group"], "text": text, "reason": "negative_base_description_not_availability"})
                    continue
                attributes = sorted(equipment_map.get(text, ()))
                if not attributes:
                    unresolved_equipment.append({"configuration_code": configuration_code, "group": group["group"], "text": text, "reason": "no_exact_previously_reviewed_standard_mapping"})
                    continue
                for attribute_code in attributes:
                    row_code = f"{configuration_code}_{attribute_code}_20260809_full_configurator"
                    if any(row["code"] == row_code for row in availability):
                        continue
                    availability.append({
                        "id": str(availability_next + availability_added),
                        "code": row_code,
                        "configuration_code": configuration_code,
                        "attribute_code": attribute_code,
                        "availability_status": "standard",
                        "observation_date": DATE,
                        "source_code": SOURCE_CODE,
                        "notes": f"Exact current full-modal equipment text matched to an already reviewed standard mapping: {text}",
                    })
                    availability_added += 1

    report = {
        "schema_version": 1,
        "package_id": "sandero_stepway_full_modal_canonical_reconciliation_001",
        "observed_on": DATE,
        "source_code": SOURCE_CODE,
        "source_rows": {"technical": technical_total, "equipment": equipment_total},
        "imported_rows": {"configuration_attribute_values": value_added, "configuration_attribute_availability": availability_added},
        "preserved_evidence": {
            "technical_unresolved": len(unresolved_technical),
            "equipment_unresolved": len(unresolved_equipment),
            "negative_equipment_descriptions": len(negative_evidence),
        },
        "rules": [
            "Technical normalization uses only the explicit label map in this importer.",
            "Compound or model-qualified technical values are not reduced to scalars.",
            "Equipment normalization requires an exact literal match to a previously reviewed standard mapping already present in canonical availability data.",
            "Negative base-equipment descriptions are evidence only and never become not_available rows in this package.",
            "No cross-grade, engine, transmission, or model inheritance is inferred.",
        ],
        "unresolved_technical": unresolved_technical,
        "unresolved_equipment": unresolved_equipment,
        "negative_equipment_evidence": negative_evidence,
    }
    return tables, report


def apply():
    tables, report = build()
    for name, (fields, rows) in tables.items():
        write_csv(name, fields, rows)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["imported_rows"], ensure_ascii=False))
    print(json.dumps(report["preserved_evidence"], ensure_ascii=False))


def verify():
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if capture["summary"] != {"exact_configuration_surfaces": 15, "standard_equipment_rows": 1029, "technical_rows": 679}:
        raise RuntimeError("capture summary differs from reviewed boundary")
    if report["source_rows"] != {"technical": 679, "equipment": 1029}:
        raise RuntimeError("reconciliation source-row totals differ")
    _, sources = read_csv("sources.csv")
    source = next(row for row in sources if row["code"] == SOURCE_CODE)
    if source["sha256"] != hashlib.sha256(CAPTURE.read_bytes()).hexdigest():
        raise RuntimeError("registered source hash differs from capture")
    _, source_configurations = read_csv("source_configurations.csv")
    documented = {row["configuration_code"] for row in source_configurations if row["source_code"] == SOURCE_CODE}
    expected = {row["configuration_code"] for row in capture["configurations"]}
    if documented != expected:
        raise RuntimeError("source/configuration coverage differs")
    print("Sandero/Stepway full-modal canonical reconciliation: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply == args.verify:
        parser.error("choose exactly one of --apply or --verify")
    if args.apply:
        apply()
    else:
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
