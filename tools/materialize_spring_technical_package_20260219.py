#!/usr/bin/env python3
"""Materialize documentation, reporting scope and state for Spring technical import."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CODE = "src_pl_spring_brochure_20260219"
PACKAGE_ID = "spring_brochure_technical_observations_20260219_001"
MANIFEST = [
    "CHANGELOG.md",
    "README.md",
    "data/imports/spring_technical_20260219.csv",
    "data/master/configuration_attribute_value_ranges.csv",
    "data/master/configuration_attribute_values.csv",
    "data/master/configuration_cargo_volume_contexts.csv",
    "data/reporting/spring_electric70_automatic_completeness.json",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
    "project/ROADMAP.md",
    "project/SESSION_STATE.md",
    "project/STATE_SUMMARY.md",
    "project/packages/spring-brochure-technical-observations-20260219.md",
    "project/state.json",
    "tests/test_spring_technical_20260219.py",
    "tools/import_spring_technical_20260219.py",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def insert_once(path: Path, marker: str, text: str, *, before: bool = False) -> None:
    current = path.read_text(encoding="utf-8")
    if text.strip() in current:
        return
    if marker not in current:
        raise RuntimeError(f"marker not found in {path}: {marker!r}")
    replacement = text + marker if before else marker + text
    path.write_text(current.replace(marker, replacement, 1), encoding="utf-8", newline="\n")


def build_completeness_scope() -> None:
    specification = read_csv(ROOT / "data/imports/spring_technical_20260219.csv")
    technical_slots: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in specification:
        attribute = row["attribute_code"]
        if attribute in seen:
            continue
        seen.add(attribute)
        technical_slots.append({"attribute_code": attribute, "fuel_type_code": ""})
    if len(technical_slots) != 19:
        raise RuntimeError(f"expected 19 Spring technical slots, found {len(technical_slots)}")

    equipment_rows = read_csv(ROOT / "data/imports/spring_equipment_availability_20260219.csv")
    electric70 = {
        "spring_essential_electric70_automatic",
        "spring_expression_electric70_automatic",
    }
    equipment_attributes = sorted({
        row["attribute_code"]
        for row in equipment_rows
        if row["configuration_code"] in electric70
    })
    if len(equipment_attributes) != 42:
        raise RuntimeError(f"expected 42 Spring equipment attributes, found {len(equipment_attributes)}")

    payload = {
        "version": 1,
        "configuration_status": "active",
        "configurations": [
            {
                "configuration_code": "spring_essential_electric70_automatic",
                "source_code": SOURCE_CODE,
            },
            {
                "configuration_code": "spring_expression_electric70_automatic",
                "source_code": SOURCE_CODE,
            },
        ],
        "technical_slots": technical_slots,
        "equipment_attributes": equipment_attributes,
        "not_applicable": {"technical": [], "equipment": []},
    }
    write_json(ROOT / "data/reporting/spring_electric70_automatic_completeness.json", payload)


def update_reconciliation() -> None:
    path = ROOT / "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    counts = payload["summary"]["active_evidence_record_counts"]
    expected = {
        "configuration_attribute_values": 3421,
        "configuration_attribute_value_ranges": 298,
        "configuration_attribute_availability": 5902,
    }
    if counts not in (expected, {
        "configuration_attribute_values": 3475,
        "configuration_attribute_value_ranges": 301,
        "configuration_attribute_availability": 5902,
    }):
        raise RuntimeError(f"unexpected reconciliation baseline: {counts}")
    counts["configuration_attribute_values"] = 3475
    counts["configuration_attribute_value_ranges"] = 301
    write_json(path, payload)


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-08-01"
    state["phase"] = "Spring Brochure Technical Observations"
    state["baseline"].update({
        "tests": 1715,
        "csv_files": 46,
        "rows": 11660,
        "configuration_values": 3552,
        "configuration_import_specs": 138,
        "configuration_value_ranges": 301,
        "configuration_range_import_specs": 24,
        "availability_records": 5902,
        "attributes": 385,
        "attribute_categories": 30,
    })
    state["current_package"] = {
        "package_id": PACKAGE_ID,
        "kind": "configuration_technical_import",
        "name": "Spring Brochure Technical Observations",
        "status": "complete",
        "goal": "Import 54 exact scalar observations, three maximum-power RPM ranges and three ISO 3832 cargo-context rows for the three existing passenger Spring configurations from the registered 2026-02-19 brochure without adding or inferring entities.",
        "manifest_paths": MANIFEST,
    }
    state["next_package"] = {
        "package_id": "existing_configuration_completeness_reanalysis_001",
        "kind": "data_quality_review",
        "name": "Existing Configuration Completeness Reanalysis",
        "status": "planned",
        "goal": "Recompute configuration- and attribute-level missing-data impact after the Spring import, classify non-applicable fields, and select the next small source-backed package that most reduces visible missing data without adding entities.",
        "manifest_paths": [
            "data/reporting/existing_configuration_missing_data_analysis.json",
            "data/reporting/existing_configuration_missing_data_analysis.md",
            "project/STATE_SUMMARY.md",
            "project/packages/existing-configuration-completeness-reanalysis-20260801.md",
            "project/state.json",
            "tests/test_existing_configuration_missing_data_analysis.py",
            "tools/existing_configuration_missing_data_analysis.py",
        ],
    }
    write_json(path, state)


def update_documents() -> None:
    changelog_entry = (
        "* Added 54 exact Spring brochure technical observations, three closed maximum-power RPM ranges and three one-to-one ISO 3832 cargo contexts across the existing Essential Electric 70, Expression Electric 70 and Extreme Electric 100 configurations, prioritizing core comparison completeness over the previously planned Bigster paint package and importing no new entities or inferred values.\n"
    )
    insert_once(ROOT / "CHANGELOG.md", "### Added\n\n", changelog_entry)

    readme_text = (
        "Broszura Spring z 19 lutego 2026 r. dostarcza również bezpośrednie dane techniczne dla trzech istniejących konfiguracji pasażerskich. Import obejmuje 54 wartości skalarnych i trzy domknięte zakresy obrotów mocy: po 18 wartości oraz jednym zakresie dla Essential Electric 70, Expression Electric 70 i Extreme Electric 100. Trzy minimalne pojemności bagażnika mają osobne konteksty ISO 3832 z kanapą w pozycji normalnej i główną komorą bagażową. Nie przeniesiono wartości między napędami ani wersjami.\n\nPakiet został wykonany przed wcześniej planowanymi lakierami Bigstera, ponieważ bezpośrednio zmniejsza liczbę pól „brak danych” w porównaniach Springa. Poza zakresem pozostały niejednoznaczne jednostki momentu i zużycia energii, ładowanie zależne od opcji, wymiary rozpoznawalne tylko z układu rysunku oraz dane Cargo.\n\n"
    )
    insert_once(ROOT / "README.md", "Dwa cenniki Joggera MY26", readme_text, before=True)

    roadmap_text = (
        "## Completeness-first package ordering\n\n"
        "Pakiet Spring z 1 sierpnia 2026 r. świadomie wyprzedził planowany import lakierów Bigstera: trzy istniejące konfiguracje Springa nie miały wartości technicznych, a oficjalna broszura pozwalała bezpiecznie uzupełnić 54 wartości, trzy zakresy i trzy konteksty bagażnika. Kolejność dalszych pakietów ma być ponownie wyznaczana z aktualnej analizy wpływu na pola „brak danych”, a nie z historycznego `next_package`.\n\n"
    )
    insert_once(ROOT / "project/ROADMAP.md", "## Verified tooling baseline", roadmap_text, before=True)


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> int:
    build_completeness_scope()
    update_reconciliation()
    update_state()
    update_documents()
    run("tools/dkb.py", "project-state", "--apply")
    run("tools/dkb.py", "documentation-baseline", "--apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
