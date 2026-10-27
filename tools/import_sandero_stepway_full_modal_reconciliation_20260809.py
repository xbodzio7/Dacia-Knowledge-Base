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
REPORT_JSON = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"
REPORT_MD = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.md"
SOURCE_CODE = "src_pl_sandero_stepway_full_modal_20260809"
DATE = "2026-08-09"

TECHNICAL_LABELS = {
    "pojemność zbiornika paliwa (l)": ("fuel_tank_capacity", "number"),
    "Liczba drzwi": ("door_count", "integer"),
    "Średnica zawracania (m)": ("turning_circle", "number"),
    "Liczba miejsc siedzących": ("number_of_seats", "integer"),
    "Liczba biegów do przodu": ("gear_count", "integer"),
    "Liczba cylindrów": ("cylinder_count", "integer"),
    "Pojemność skokowa (cm3)": ("engine_displacement", "integer"),
    "Prędkość maksymalna (km/h)": ("top_speed", "number"),
    "Maksymalna masa przyczepy bez hamulca (kg)": ("unbraked_trailer_weight", "number"),
    "Maksymalna masa całkowita zespołu pojazdów (kg)": ("gross_train_weight", "number"),
    "Maksymalna masa przyczepy z hamulcem (kg)": ("braked_trailer_weight", "number"),
    "Minimalna masa pojazdu gotowego do jazdy (bez opcji) (kg)": ("kerb_weight", "number"),
    "Maksymalna masa całkowita pojazdu (kg)": ("gross_vehicle_weight", "number"),
}


def read_csv(name: str):
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(name: str, fields: list[str], rows: list[dict[str, str]]) -> None:
    with (MASTER / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def next_id(rows: list[dict[str, str]]) -> int:
    return max((int(row["id"]) for row in rows), default=0) + 1


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def note_literal(note: str) -> str | None:
    if not note or ": " not in note:
        return None
    return note.split(": ", 1)[1].strip()


def scalar(text: str, kind: str) -> str | None:
    value = text.strip().replace(",", ".")
    if kind == "integer":
        return value if re.fullmatch(r"-?\d+", value) else None
    if kind == "number":
        return value if re.fullmatch(r"-?\d+(?:\.\d+)?", value) else None
    return None


def append_unique(rows: list[dict[str, str]], row: dict[str, str]) -> bool:
    if any(existing["code"] == row["code"] for existing in rows):
        return False
    rows.append(row)
    return True


def canonical_value_exists(
    rows: list[dict[str, str]], configuration_code: str, attribute_code: str
) -> bool:
    return any(
        row.get("source_code") != SOURCE_CODE
        and row.get("configuration_code") == configuration_code
        and row.get("attribute_code") == attribute_code
        and not row.get("fuel_type_code", "")
        and not row.get("gear_number", "")
        for row in rows
    )


def build():
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    tables = {
        name: read_csv(name)
        for name in (
            "attributes.csv",
            "sources.csv",
            "source_configurations.csv",
            "configuration_attribute_values.csv",
            "configuration_attribute_availability.csv",
        )
    }
    attribute_codes = {row["code"] for row in tables["attributes.csv"][1]}
    sources = tables["sources.csv"][1]
    source_configs = tables["source_configurations.csv"][1]
    values = tables["configuration_attribute_values.csv"][1]
    availability = tables["configuration_attribute_availability.csv"][1]

    literal_candidates: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in availability:
        if row.get("source_code") == SOURCE_CODE:
            continue
        literal = note_literal(row.get("notes", ""))
        if literal:
            literal_candidates[norm(literal)].add(
                (row["attribute_code"], row["availability_status"])
            )
    literal_map: dict[str, tuple[str, str]] = {}
    for literal, pairs in literal_candidates.items():
        if len(pairs) == 1:
            attribute_code, status = next(iter(pairs))
            if status == "standard":
                literal_map[literal] = (attribute_code, status)

    if not any(row["code"] == SOURCE_CODE for row in sources):
        append_unique(
            sources,
            {
                "id": str(next_id(sources)),
                "code": SOURCE_CODE,
                "source_type": "web_snapshot",
                "title": "Dacia Polska Sandero and Sandero Stepway full technical and standard-equipment modals",
                "publisher": "Dacia",
                "market": "PL",
                "document_date": DATE,
                "external_reference": "https://www.dacia.pl/",
                "file_path": str(CAPTURE.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hashlib.sha256(CAPTURE.read_bytes()).hexdigest(),
                "status": "active",
                "notes": "Exact configuration-bounded full-modal snapshot; only proven standard equipment and missing simple scalar technical observations are normalized.",
            },
        )

    technical_rows = 0
    equipment_rows = 0
    technical_unresolved: dict[str, int] = defaultdict(int)
    equipment_unresolved: dict[str, int] = defaultdict(int)
    technical_resolved: dict[str, int] = defaultdict(int)
    equipment_resolved: dict[str, int] = defaultdict(int)
    technical_already_covered: dict[str, int] = defaultdict(int)

    for config in capture["configurations"]:
        configuration_code = config["configuration_code"]
        relationship_key = (SOURCE_CODE, configuration_code)
        if not any(
            (row["source_code"], row["configuration_code"]) == relationship_key
            for row in source_configs
        ):
            source_configs.append(
                {
                    "id": str(next_id(source_configs)),
                    "source_code": SOURCE_CODE,
                    "configuration_code": configuration_code,
                    "relationship": "documents",
                    "notes": "Exact configurator state; full standard-equipment and technical modals captured on 2026-08-09.",
                }
            )

        for group in config["equipment"]:
            for item in group["items"]:
                equipment_rows += 1
                mapped = literal_map.get(norm(item))
                if not mapped:
                    equipment_unresolved[item] += 1
                    continue
                attribute_code, status = mapped
                append_unique(
                    availability,
                    {
                        "id": str(next_id(availability)),
                        "code": f"{configuration_code}_{attribute_code}_20260809_full_modal",
                        "configuration_code": configuration_code,
                        "attribute_code": attribute_code,
                        "availability_status": status,
                        "observation_date": DATE,
                        "source_code": SOURCE_CODE,
                        "notes": f"Exact full-modal standard-equipment literal: {item}",
                    },
                )
                equipment_resolved[attribute_code] += 1

        for group in config["technical"]:
            for item in group["items"]:
                technical_rows += 1
                label = item["label"]
                mapping = TECHNICAL_LABELS.get(label)
                if not mapping:
                    technical_unresolved[label] += 1
                    continue
                attribute_code, kind = mapping
                if attribute_code not in attribute_codes:
                    technical_unresolved[label] += 1
                    continue
                value = scalar(item["value"], kind)
                if value is None:
                    technical_unresolved[label] += 1
                    continue
                if canonical_value_exists(values, configuration_code, attribute_code):
                    technical_already_covered[attribute_code] += 1
                    continue
                append_unique(
                    values,
                    {
                        "id": str(next_id(values)),
                        "code": f"{configuration_code}_{attribute_code}_20260809_full_modal",
                        "configuration_code": configuration_code,
                        "attribute_code": attribute_code,
                        "fuel_type_code": "",
                        "gear_number": "",
                        "value": value,
                        "observation_date": DATE,
                        "source_code": SOURCE_CODE,
                        "notes": f"Exact full-modal missing-value label/value: {label}: {item['value']}",
                    },
                )
                technical_resolved[attribute_code] += 1

    source_registered = any(row["code"] == SOURCE_CODE for row in sources)
    source_relationship_count = sum(row["source_code"] == SOURCE_CODE for row in source_configs)
    source_equipment_count = sum(row["source_code"] == SOURCE_CODE for row in availability)
    source_technical_count = sum(row["source_code"] == SOURCE_CODE for row in values)

    summary = {
        "observed_on": DATE,
        "configuration_surfaces": len(capture["configurations"]),
        "captured_rows": equipment_rows + technical_rows,
        "equipment_rows": equipment_rows,
        "technical_rows": technical_rows,
        "source_registered": int(source_registered),
        "source_configuration_relationships": source_relationship_count,
        "canonical_equipment_observations": source_equipment_count,
        "canonical_technical_observations": source_technical_count,
        "equipment_rows_safely_mapped": sum(equipment_resolved.values()),
        "technical_rows_safely_mapped": sum(technical_resolved.values()),
        "technical_rows_already_canonically_covered": sum(technical_already_covered.values()),
        "equipment_rows_preserved_unmatched_or_ambiguous": sum(equipment_unresolved.values()),
        "technical_rows_preserved_unmatched_or_ambiguous": sum(technical_unresolved.values()),
    }
    report = {
        "schema_version": 3,
        "package_id": "sandero_stepway_full_modal_canonical_reconciliation_001",
        "source_code": SOURCE_CODE,
        "summary": summary,
        "resolved_equipment_attributes": dict(sorted(equipment_resolved.items())),
        "resolved_technical_attributes": dict(sorted(technical_resolved.items())),
        "already_covered_technical_attributes": dict(sorted(technical_already_covered.items())),
        "unresolved_equipment_literals": [
            {"literal": key, "occurrences": count}
            for key, count in sorted(equipment_unresolved.items())
        ],
        "unresolved_technical_labels": [
            {"label": key, "occurrences": count}
            for key, count in sorted(technical_unresolved.items())
        ],
        "boundaries": [
            "Equipment is normalized only when the exact literal has one unique prior canonical mapping and that mapping proves status standard.",
            "Negative or base-state standard-equipment literals do not prove not_available or optional factory availability.",
            "Technical rows fill only previously missing unqualified canonical scalar slots; already covered slots remain source evidence only.",
            "Composite, model-qualified, mixed-fuel and otherwise ambiguous values remain literal source evidence and are not projected.",
            "Absence from a standard-equipment modal never implies not_available.",
        ],
    }
    return tables, report


def render_md(report: dict) -> str:
    s = report["summary"]
    return f"""# Sandero Stepway Full Modal Canonical Reconciliation\n\nDate: {DATE}\n\n## Result\n\n- reconciled all {s['captured_rows']} captured rows across {s['configuration_surfaces']} exact configurator states;\n- safely mapped {s['equipment_rows_safely_mapped']} equipment rows as proven standard equipment;\n- filled {s['technical_rows_safely_mapped']} previously missing scalar technical observations;\n- preserved {s['technical_rows_already_canonically_covered']} safe technical literals as already-covered source evidence instead of duplicating master observations;\n- preserved {s['equipment_rows_preserved_unmatched_or_ambiguous']} equipment rows and {s['technical_rows_preserved_unmatched_or_ambiguous']} technical rows as unmatched/ambiguous evidence;\n- materialized {s['canonical_equipment_observations']} dated standard-equipment observations and {s['canonical_technical_observations']} dated technical observations;\n- registered the full-modal snapshot and its {s['source_configuration_relationships']} exact source-to-configuration relationships.\n\n## Safety boundaries\n\nThe standard-equipment modal proves only `standard` status. Negative/base-state literals are not promoted to `not_available` or `optional`. Technical values are gap-fill only and do not duplicate already covered canonical slots. No inheritance is inferred between grades or powertrains. Composite/model-qualified dimensions and mixed petrol/LPG strings remain literal evidence.\n"""


def apply(tables, report) -> None:
    for name in (
        "sources.csv",
        "source_configurations.csv",
        "configuration_attribute_values.csv",
        "configuration_attribute_availability.csv",
    ):
        fields, _old = tables[name]
        write_csv(name, fields, tables[name][1])
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_md(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    tables, report = build()
    if args.apply:
        apply(tables, report)
    if args.verify:
        expected_json = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        if expected_json != report:
            raise SystemExit("reconciliation report is stale; run with --apply")
    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
