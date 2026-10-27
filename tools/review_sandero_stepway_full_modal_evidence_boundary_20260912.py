from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"
OUTPUT = ROOT / "data/reporting/sandero_stepway_full_modal_evidence_boundary_20260912.json"

SOURCE_CODE = "src_pl_sandero_stepway_full_modal_20260809"

TECH_CONTEXT = {
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

TECH_PRESERVE = {
    "Prześwit pojazdu": 15,
    "Szerokość całkowita": 15,
    "Szerokość całkowita z lusterkami zewnętrznymi": 15,
    "Wysokość pojazdu nieobciążonego z relingami (mm)": 15,
}

EQUIPMENT_NEGATIVE = {
    "bez automatycznego parkowania": 7,
    "bez podłogi bagażnika ustawianej w dwóch płaszczyznach (góra i dół)": 13,
    "brak świateł przeciwmgielnych": 9,
    "kierownica nieogrzewana": 15,
    "szyba przednia nieogrzewana": 15,
}

EQUIPMENT_UNMAPPED = {
    "elektryczne lusterka boczne z funkcją rozmrażania, z czujnikiem temperatury": 12,
    "klapka wlewu paliwa otwierana ręcznie (wymaga Karty Keyless Entry)": 6,
    "korek wlewu paliwa (bez keyless entry)": 9,
    "kryterium techniczne niezbędne do zamówienia klimatyzacji": 14,
    "pas bezpieczeństwa kierowcy bez regulacji wysokości": 15,
    "right content": 15,
    "system ogrzewania z cyrkulacją powietrza": 1,
    "wymóg termiczny wnętrza pojazdu": 9,
    "zestaw ochronny ANTIGRAVIL": 15,
}

KEY_SCHEMA_GAP = {"kluczyk z 3 przyciskami": 9}


def _sum(mapping: dict[str, int]) -> int:
    return sum(mapping.values())


def build_report() -> dict:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    summary = source["summary"]
    equipment = {row["literal"]: row["occurrences"] for row in source["unresolved_equipment_literals"]}
    technical = {row["label"]: row["occurrences"] for row in source["unresolved_technical_labels"]}

    if _sum(TECH_CONTEXT) != 124 or _sum(TECH_PRESERVE) != 60:
        raise RuntimeError("hard-coded technical boundary counts are inconsistent")
    if _sum(EQUIPMENT_NEGATIVE) != 59 or _sum(EQUIPMENT_UNMAPPED) != 96:
        raise RuntimeError("hard-coded equipment boundary counts are inconsistent")
    if _sum(KEY_SCHEMA_GAP) != 9:
        raise RuntimeError("schema-gap count is inconsistent")

    for mapping, source_mapping in (
        (TECH_CONTEXT, technical),
        (TECH_PRESERVE, technical),
        (EQUIPMENT_NEGATIVE, equipment),
        (EQUIPMENT_UNMAPPED, equipment),
        (KEY_SCHEMA_GAP, equipment),
    ):
        for key, count in mapping.items():
            if source_mapping.get(key) != count:
                raise RuntimeError(f"source reconciliation changed for {key!r}")

    return {
        "schema_version": 1,
        "package_id": "sandero_stepway_full_modal_evidence_boundary_001",
        "reviewed_on": "2026-09-12",
        "source_code": SOURCE_CODE,
        "source_reconciliation": "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json",
        "scope": {
            "captured_rows": summary["captured_rows"],
            "current_residual_rows": summary["equipment_rows_preserved_unmatched_or_ambiguous"]
            + summary["technical_rows_preserved_unmatched_or_ambiguous"],
        },
        "decisions": {
            "preserve_negative_or_base_equipment": EQUIPMENT_NEGATIVE,
            "preserve_unmapped_equipment": EQUIPMENT_UNMAPPED,
            "preserve_schema_gap_equipment": KEY_SCHEMA_GAP,
            "preserve_contextual_technical": TECH_CONTEXT,
            "preserve_model_qualified_technical": TECH_PRESERVE,
        },
        "counts": {
            "preserved_negative_or_base_equipment": _sum(EQUIPMENT_NEGATIVE),
            "preserved_unmapped_equipment": _sum(EQUIPMENT_UNMAPPED),
            "preserved_schema_gap_equipment": _sum(KEY_SCHEMA_GAP),
            "preserved_contextual_technical": _sum(TECH_CONTEXT),
            "preserved_model_qualified_technical": _sum(TECH_PRESERVE),
            "preserved_evidence_boundary_total": _sum(EQUIPMENT_NEGATIVE)
            + _sum(EQUIPMENT_UNMAPPED)
            + _sum(KEY_SCHEMA_GAP)
            + _sum(TECH_CONTEXT)
            + _sum(TECH_PRESERVE),
        },
        "policy": {
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
            "negative_evidence_is_not_inferred": True,
            "composite_or_model_qualified_values_are_not_projected": True,
            "parser_artifacts_are_not_promoted": True,
        },
        "reason": "These residual observations are retained as exact source evidence because their wording is negative/base-state, composite, model-qualified, schema-incomplete, accessory/contextual, or otherwise lacks a unique canonical mapping. The separate scalar technical materialization work remains outside this package.",
    }


def main() -> None:
    report = build_report()
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
