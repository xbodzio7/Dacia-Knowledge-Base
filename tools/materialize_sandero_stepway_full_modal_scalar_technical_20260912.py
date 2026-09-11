from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master/configuration_attribute_values.csv"
ATTRIBUTES = ROOT / "data/master/attributes.csv"
CAPTURE = ROOT / "project/sources/dacia-pl-sandero-stepway-full-technical-standard-equipment-20260809.json"
REPORT = ROOT / "data/reporting/sandero_stepway_full_modal_scalar_technical_20260912.json"
SOURCE_CODE = "src_pl_sandero_stepway_full_modal_20260809"
DATE = "2026-08-09"

MAPPINGS: dict[str, tuple[str, str]] = {
    "1000 m ze startu zatrzymanego (s)": ("standing_km", "decimal"),
    "Długość całkowita": ("overall_length", "integer"),
    "Liczba drzwi": ("number_of_doors", "integer"),
    "Liczba zaworów": ("total_valve_count", "integer"),
    "Maksymalna ładowność (kg)": ("maximum_payload", "integer"),
    "Norma emisji spalin": ("emission_standard", "string"),
    "Opony standardowe": ("standard_tyre_specification", "string"),
    "Poziom hałasu przy 50 km/h (dB)": ("noise_level_at_50_kmh", "decimal"),
    "Procedura homologacji": ("homologation_procedure_code", "string"),
    "Protokół homologacji": ("homologation_protocol", "string"),
    "Przyspieszenie 0-100 km/h (s)": ("acceleration_0_100", "decimal"),
    "Rodzaj nadwozia": ("body_style_source_stated", "string"),
    "Rodzaj napędu": ("drive_type", "enum"),
    "Rodzaj paliwa": ("fuel_type", "enum"),
    "Rodzaj skrzyni biegów": ("gearbox_type", "enum"),
    "Rozstaw osi": ("wheelbase", "integer"),
    "Szerokość dolnej części bagażnika": ("cargo_floor_width", "integer"),
    "Typ techniczny": ("technical_type_code", "string"),
    "Wysokość całkowita": ("overall_height_source_stated", "string"),
    "Zwis przedni": ("front_overhang", "integer"),
    "Zwis tylny": ("rear_overhang", "integer"),
}

EXCLUDED_CONTEXTUAL = {
    "Emisja CO2 cykl mieszany WLTP (g/km)": 15,
    "Emisja CO2 cykl mieszany WLTP*LPG (g/km)": 9,
    "Maksymalny moment obrotowy w Nm": 15,
    "Moc maksymalna kW (KM)": 15,
    "Pojemność przestrzeni bagażowej maks. po złożeniu kanapy (dm3)": 15,
    "Pojemność przestrzeni bagażowej min. (dm3)": 15,
    "Wysokość bez obciążenia z otwartą klapą tylną": 15,
    "Zużycie paliwa cykl mieszany WLTP (l/100 km)": 15,
    "Zużycie paliwa cykl mieszany WLTP*LPG (l/100km)": 10,
}

EXCLUDED_MODEL_QUALIFIED = {
    "Prześwit pojazdu": 15,
    "Szerokość całkowita": 15,
    "Szerokość całkowita z lusterkami zewnętrznymi": 15,
    "Wysokość pojazdu nieobciążonego z relingami (mm)": 15,
}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def first_number(text: str, *, integer: bool = False) -> str | None:
    match = re.search(r"-?\d+(?:[.,]\d+)?", text.replace("\u00a0", " "))
    if not match:
        return None
    value = match.group(0).replace(",", ".")
    if integer:
        return value.split(".", 1)[0]
    return value


def normalize_value(text: str, kind: str) -> str | None:
    value = " ".join(text.strip().split())
    if not value:
        return None
    if kind in {"string", "enum"}:
        return value
    if kind == "integer":
        return first_number(value, integer=True)
    if kind == "decimal":
        return first_number(value)
    raise ValueError(kind)


def next_id(rows: list[dict[str, str]]) -> int:
    return max((int(row["id"]) for row in rows), default=0) + 1


def existing_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row.get("configuration_code", ""),
        row.get("attribute_code", ""),
        row.get("fuel_type_code", ""),
        row.get("gear_number", ""),
    )


def build() -> tuple[list[str], list[dict[str, str]], dict]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    fields, rows = read_rows(MASTER)
    _, attribute_rows = read_rows(ATTRIBUTES)
    attributes = {row["code"] for row in attribute_rows}

    candidate_by_label = {label: 0 for label in MAPPINGS}
    generated_by_label = {label: 0 for label in MAPPINGS}
    generated_by_attribute = {attribute: 0 for attribute, _ in MAPPINGS.values()}
    skipped_existing_by_label = {label: 0 for label in MAPPINGS}
    generated: list[dict[str, str]] = []
    seen = {existing_key(row) for row in rows}

    for config in capture["configurations"]:
        configuration_code = config["configuration_code"]
        for group in config["technical"]:
            for item in group["items"]:
                label = item["label"]
                if label not in MAPPINGS:
                    continue
                candidate_by_label[label] += 1
                attribute_code, kind = MAPPINGS[label]
                if attribute_code not in attributes:
                    raise RuntimeError(f"canonical attribute missing: {attribute_code}")
                value = normalize_value(item["value"], kind)
                if value is None:
                    raise RuntimeError(f"cannot normalize scalar value: {label}: {item['value']}")
                key = (configuration_code, attribute_code, "", "")
                if key in seen:
                    skipped_existing_by_label[label] += 1
                    continue
                row = {
                    "id": str(next_id(rows + generated)),
                    "code": f"{configuration_code}_{attribute_code}_20260809_full_modal",
                    "configuration_code": configuration_code,
                    "attribute_code": attribute_code,
                    "fuel_type_code": "",
                    "gear_number": "",
                    "value": value,
                    "observation_date": DATE,
                    "source_code": SOURCE_CODE,
                    "notes": f"Exact full-modal scalar technical label/value: {label}: {item['value']}",
                }
                generated.append(row)
                seen.add(key)
                generated_by_label[label] += 1
                generated_by_attribute[attribute_code] += 1

    candidate_total = sum(candidate_by_label.values())
    generated_total = len(generated)
    skipped_total = sum(skipped_existing_by_label.values())
    if candidate_total != 315:
        raise RuntimeError(f"expected 315 scalar technical candidates, found {candidate_total}")
    if generated_total + skipped_total != candidate_total:
        raise RuntimeError("candidate accounting is inconsistent")
    if any(count == 0 for count in candidate_by_label.values()):
        missing = [label for label, count in candidate_by_label.items() if count == 0]
        raise RuntimeError(f"expected scalar labels are missing from capture: {missing}")

    report = {
        "schema_version": 1,
        "package_id": "sandero_stepway_full_modal_scalar_technical_001",
        "reviewed_on": "2026-09-12",
        "source_code": SOURCE_CODE,
        "source_capture": str(CAPTURE.relative_to(ROOT)).replace("\\", "/"),
        "candidate_rows": candidate_total,
        "generated_rows": generated_total,
        "already_covered_rows": skipped_total,
        "candidate_label_occurrences": dict(sorted(candidate_by_label.items())),
        "generated_label_occurrences": dict(sorted(generated_by_label.items())),
        "already_covered_label_occurrences": dict(sorted(skipped_existing_by_label.items())),
        "generated_attribute_occurrences": dict(sorted(generated_by_attribute.items())),
        "excluded_contextual_labels": dict(sorted(EXCLUDED_CONTEXTUAL.items())),
        "excluded_model_qualified_labels": dict(sorted(EXCLUDED_MODEL_QUALIFIED.items())),
        "policy": {
            "source_backed_only": True,
            "scalar_only": True,
            "composite_or_model_qualified_values_excluded": True,
            "mixed_fuel_context_excluded": True,
            "existing_canonical_values_are_not_duplicated": True,
            "availability_changes": False,
            "import_spec_changes": False,
        },
    }
    return fields, rows + generated, report


def main() -> None:
    fields, rows, report = build()
    with MASTER.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
