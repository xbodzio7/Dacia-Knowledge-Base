from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/reporting/sandero_stepway_full_modal_canonical_reconciliation_20260809.json"

NEGATIVE = {"bez automatycznego parkowania", "bez podłogi bagażnika ustawianej w dwóch płaszczyznach (góra i dół)", "brak świateł przeciwmgielnych", "kierownica nieogrzewana", "szyba przednia nieogrzewana"}
SAFE_MARKERS = ("obręcze kół", "felgi aluminiowe", "esp z systemem", "tapicerka materiałowa", "płetwy rekina", "dwa światła cofania", "filtr cząstek stałych", "fotel kierowcy z regulacją wzdłużną", "kierownica pokryta skórą ekologiczną", "kierownica z pianki", "kluczyk z 3 przyciskami", "komunikaty w języku polskim", "lusterka boczne regulowane ręcznie", "relingi dachowe", "niska konsola środkowa", "normalny dach", "system multimedialny media", "ograniczenie prędkości do 180", "poduszki boczne z przodu", "regulator-ogranicznik", "system wspomagania parkowania przód/tył", "szyby tylne otwierane ręcznie", "tryb eco", "tylne oparcie kanapy nieskładane", "światła automatyczne, wycieraczki automatyczne")
TECH_CONTEXT = {"Emisja CO2 cykl mieszany WLTP (g/km)", "Emisja CO2 cykl mieszany WLTP*LPG (g/km)", "Maksymalny moment obrotowy w Nm", "Moc maksymalna kW (KM)", "Pojemność przestrzeni bagażowej maks. po złożeniu kanapy (dm3)", "Pojemność przestrzeni bagażowej min. (dm3)", "Wysokość bez obciążenia z otwartą klapą tylną", "Zużycie paliwa cykl mieszany WLTP (l/100 km)", "Zużycie paliwa cykl mieszany WLTP*LPG (l/100km)"}
TECH_PRESERVE = {"Prześwit pojazdu", "Szerokość całkowita", "Szerokość całkowita z lusterkami zewnętrznymi", "Wysokość pojazdu nieobciążonego z relingami (mm)"}
TECHNICAL_TARGET_HINTS = {"Liczba drzwi": ["number_of_doors"]}


def build_report() -> dict:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    equipment = source["unresolved_equipment_literals"]
    technical = source["unresolved_technical_labels"]
    if (sum(x["occurrences"] for x in equipment), sum(x["occurrences"] for x in technical), len(equipment), len(technical)) != (441, 499, 51, 34):
        raise RuntimeError("residual vocabulary changed; review policy before continuing")
    counts = Counter()
    for row in equipment:
        literal = row["literal"]
        if literal in NEGATIVE:
            policy = "preserve_negative_or_base"
        elif any(marker in literal.casefold() for marker in SAFE_MARKERS):
            policy = "safe_equipment"
        else:
            policy = "preserve_equipment_unmapped"
        counts[policy] += row["occurrences"]
    for row in technical:
        label = row["label"]
        policy = "preserve_technical_context" if label in TECH_PRESERVE else "safe_technical_contextual" if label in TECH_CONTEXT else "safe_technical_scalar"
        counts[policy] += row["occurrences"]
    expected = {"safe_equipment": 286, "preserve_negative_or_base": 59, "preserve_equipment_unmapped": 96, "safe_technical_scalar": 315, "safe_technical_contextual": 124, "preserve_technical_context": 60}
    if dict(counts) != expected:
        raise RuntimeError(f"policy split changed: {dict(counts)!r}")
    return {"schema_version": 1, "package_id": "sandero_stepway_full_modal_residual_review_001", "reviewed_on": "2026-08-10", "summary": {"historical_planned_residual_rows": 873, "current_residual_rows": 940, "safe_normalization_candidate_rows": 725, "preserved_evidence_rows": 215}, "policy_counts": dict(sorted(counts.items())), "technical_target_hints": TECHNICAL_TARGET_HINTS}


if __name__ == "__main__":
    print(json.dumps(build_report(), ensure_ascii=False, indent=2))
