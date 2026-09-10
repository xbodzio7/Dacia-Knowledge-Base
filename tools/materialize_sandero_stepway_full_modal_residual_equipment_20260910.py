from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
CAPTURE = ROOT / "project/sources/dacia-pl-sandero-stepway-full-technical-standard-equipment-20260809.json"
RECONCILIATION = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"
SOURCE_CODE = "src_pl_sandero_stepway_full_modal_20260809"
DATE = "2026-08-09"

SAFE_MARKERS = (
    "obręcze kół",
    "felgi aluminiowe",
    "esp z systemem",
    "tapicerka materiałowa",
    "płetwy rekina",
    "dwa światła cofania",
    "filtr cząstek stałych",
    "fotel kierowcy z regulacją wzdłużną",
    "kierownica pokryta skórą ekologiczną",
    "kierownica z pianki",
    "kluczyk z 3 przyciskami",
    "komunikaty w języku polskim",
    "lusterka boczne regulowane ręcznie",
    "relingi dachowe",
    "niska konsola środkowa",
    "normalny dach",
    "system multimedialny media",
    "ograniczenie prędkości do 180",
    "poduszki boczne z przodu",
    "regulator-ogranicznik",
    "system wspomagania parkowania przód/tył",
    "szyby tylne otwierane ręcznie",
    "tryb eco",
    "tylne oparcie kanapy nieskładane",
    "światła automatyczne, wycieraczki automatyczne",
)

NEGATIVE = {
    "bez automatycznego parkowania",
    "bez podłogi bagażnika ustawianej w dwóch płaszczyznach (góra i dół)",
    "brak świateł przeciwmgielnych",
    "kierownica nieogrzewana",
    "szyba przednia nieogrzewana",
}


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def note_literal(note: str) -> str | None:
    if not note or ": " not in note:
        return None
    return note.split(": ", 1)[1].strip()


def next_id(rows: list[dict[str, str]]) -> int:
    return max((int(row["id"]) for row in rows), default=0) + 1


def build() -> tuple[list[str], list[dict[str, str]], dict]:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    fields, availability = read_csv("configuration_attribute_availability.csv")

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

    safe_literals = {
        row["literal"]
        for row in reconciliation["unresolved_equipment_literals"]
        if row["literal"] not in NEGATIVE
        and any(marker in row["literal"].casefold() for marker in SAFE_MARKERS)
    }
    safe_occurrences = sum(
        row["occurrences"]
        for row in reconciliation["unresolved_equipment_literals"]
        if row["literal"] in safe_literals
    )
    if safe_occurrences != 286:
        raise RuntimeError(f"expected 286 safe equipment occurrences, got {safe_occurrences}")

    existing_codes = {row["code"] for row in availability}
    mapped_occurrences = 0
    added_rows = 0
    unresolved_safe: list[str] = []

    for config in capture["configurations"]:
        configuration_code = config["configuration_code"]
        for group in config["equipment"]:
            for item in group["items"]:
                if item not in safe_literals:
                    continue
                mapped = literal_map.get(norm(item))
                if not mapped:
                    unresolved_safe.append(item)
                    continue
                attribute_code, status = mapped
                code = f"{configuration_code}_{attribute_code}_20260809_full_modal"
                mapped_occurrences += 1
                if code in existing_codes:
                    continue
                availability.append(
                    {
                        "id": str(next_id(availability)),
                        "code": code,
                        "configuration_code": configuration_code,
                        "attribute_code": attribute_code,
                        "availability_status": status,
                        "observation_date": DATE,
                        "source_code": SOURCE_CODE,
                        "notes": f"Exact full-modal standard-equipment literal: {item}",
                    }
                )
                existing_codes.add(code)
                added_rows += 1

    if unresolved_safe:
        raise RuntimeError(
            "safe residual literals lack a unique prior standard mapping: "
            + repr(sorted(set(unresolved_safe)))
        )
    if mapped_occurrences != 286:
        raise RuntimeError(f"expected 286 mapped occurrences, got {mapped_occurrences}")

    report = {
        "schema_version": 1,
        "package_id": "sandero_stepway_full_modal_residual_equipment_001",
        "observed_on": DATE,
        "safe_equipment_occurrences": safe_occurrences,
        "mapped_occurrences": mapped_occurrences,
        "new_availability_rows": added_rows,
        "preserved_equipment_occurrences": 441 - safe_occurrences,
        "source_code": SOURCE_CODE,
    }
    return fields, availability, report


def apply(fields: list[str], rows: list[dict[str, str]]) -> None:
    with (MASTER / "configuration_attribute_availability.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
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
