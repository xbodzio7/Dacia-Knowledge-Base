from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def migrate_attributes() -> None:
    path = ROOT / "data/master/attributes.csv"
    rows = read_csv(path)
    fields = list(rows[0])
    codes = {row["code"] for row in rows}
    next_id = max(int(row["id"]) for row in rows) + 1
    additions = [
        (
            "type2_charging_cable_supplied",
            "Type 2 charging cable supplied",
            "Physical Type 2 charging cable supplied with the vehicle; distinct from the vehicle charging connector type and from a domestic-socket cable.",
        ),
        (
            "domestic_socket_charging_cable",
            "Domestic-socket charging cable",
            "Separate charging cable for a regular domestic socket; distinct from the Type 2 cable supplied with the vehicle.",
        ),
    ]
    for code, name, description in additions:
        if code in codes:
            continue
        rows.append(
            {
                "id": str(next_id),
                "code": code,
                "category": "Charging",
                "name": name,
                "data_type": "boolean",
                "unit": "",
                "description": description,
                "status": "active",
            }
        )
        next_id += 1
    write_csv(path, fields, rows)


def availability_specs() -> list[tuple[str, str, str, str, str]]:
    return [
        (
            "cfg_spring_essential_electric_70",
            "type2_charging_cable_supplied",
            "standard",
            "src_spring_essential_pricing_pdf_2026-08-02",
            "Official saved-configuration PDF confirms a Type 2 cable supplied as standard.",
        ),
        (
            "cfg_spring_expression_electric_70",
            "type2_charging_cable_supplied",
            "standard",
            "src_spring_expression_pricing_pdf_2026-08-02",
            "Official saved-configuration PDF confirms a Type 2 cable supplied as standard.",
        ),
        (
            "cfg_spring_extreme_electric_100",
            "type2_charging_cable_supplied",
            "standard",
            "src_spring_extreme_pricing_pdf_2026-08-02",
            "Official saved-configuration PDF confirms a Type 2 cable supplied as standard.",
        ),
        (
            "cfg_spring_essential_electric_70",
            "domestic_socket_charging_cable",
            "optional",
            "src_spring_essential_pricing_pdf_2026-08-02",
            "Official saved-configuration PDF confirms the domestic-socket charging cable as an optional item priced at 1500 PLN.",
        ),
        (
            "cfg_spring_extreme_electric_100",
            "domestic_socket_charging_cable",
            "optional",
            "src_spring_extreme_pricing_pdf_2026-08-02",
            "Official saved-configuration PDF confirms the domestic-socket charging cable as an optional item priced at 1500 PLN.",
        ),
    ]


def migrate_availability() -> None:
    path = ROOT / "data/master/configuration_attribute_availability.csv"
    rows = read_csv(path)
    fields = list(rows[0])
    existing = {row["code"] for row in rows}
    next_id = max(int(row["id"]) for row in rows) + 1
    for configuration, attribute, status, source, notes in availability_specs():
        code = f"{configuration}_{attribute}_20260802"
        if code in existing:
            continue
        rows.append(
            {
                "id": str(next_id),
                "code": code,
                "configuration_code": configuration,
                "attribute_code": attribute,
                "availability_status": status,
                "observation_date": "2026-08-02",
                "source_code": source,
                "notes": notes,
            }
        )
        next_id += 1
    write_csv(path, fields, rows)


def migrate_provenance() -> None:
    source_path = ROOT / "data/imports/configuration_attribute_availability_sources.csv"
    write_csv(
        source_path,
        ["id", "code", "source_artifact_id", "source_type", "observation_date", "notes"],
        [
            {
                "id": "1",
                "code": "spring_essential_charging_cable_evidence_20260802",
                "source_artifact_id": "src_spring_essential_pricing_pdf_2026-08-02",
                "source_type": "official_saved_configuration_pdf",
                "observation_date": "2026-08-02",
                "notes": "Type 2 standard cable and domestic-socket cable optional at 1500 PLN.",
            },
            {
                "id": "2",
                "code": "spring_expression_charging_cable_evidence_20260802",
                "source_artifact_id": "src_spring_expression_pricing_pdf_2026-08-02",
                "source_type": "official_saved_configuration_pdf",
                "observation_date": "2026-08-02",
                "notes": "Type 2 standard cable only; no negative inference for the unselected domestic cable.",
            },
            {
                "id": "3",
                "code": "spring_extreme_charging_cable_evidence_20260802",
                "source_artifact_id": "src_spring_extreme_pricing_pdf_2026-08-02",
                "source_type": "official_saved_configuration_pdf",
                "observation_date": "2026-08-02",
                "notes": "Type 2 standard cable and domestic-socket cable optional at 1500 PLN.",
            },
        ],
    )
    source_for_configuration = {
        "cfg_spring_essential_electric_70": "spring_essential_charging_cable_evidence_20260802",
        "cfg_spring_expression_electric_70": "spring_expression_charging_cable_evidence_20260802",
        "cfg_spring_extreme_electric_100": "spring_extreme_charging_cable_evidence_20260802",
    }
    links = []
    for index, (configuration, attribute, _status, _source, _notes) in enumerate(
        availability_specs(), start=1
    ):
        links.append(
            {
                "id": str(index),
                "availability_code": f"{configuration}_{attribute}_20260802",
                "availability_source_code": source_for_configuration[configuration],
                "notes": "Record-level provenance for accepted Spring charging-cable evidence.",
            }
        )
    write_csv(
        ROOT / "data/imports/configuration_attribute_availability_source_links.csv",
        ["id", "availability_code", "availability_source_code", "notes"],
        links,
    )


def write_regression_test() -> None:
    path = ROOT / "tests/test_spring_charging_cable_representation_migration_20260802.py"
    path.write_text(
        '''import csv\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\ndef rows(path):\n    with (ROOT / path).open(encoding="utf-8", newline="") as handle:\n        return list(csv.DictReader(handle))\n\ndef test_charging_cable_attributes_are_semantically_separate_booleans():\n    attributes = {row["code"]: row for row in rows("data/master/attributes.csv")}\n    assert attributes["type2_charging_cable_supplied"]["data_type"] == "boolean"\n    assert attributes["domestic_socket_charging_cable"]["data_type"] == "boolean"\n    assert "connector" not in attributes["type2_charging_cable_supplied"]["code"]\n\ndef test_spring_cable_availability_respects_evidence_boundary():\n    availability = rows("data/master/configuration_attribute_availability.csv")\n    selected = {(r["configuration_code"], r["attribute_code"]): r for r in availability if r["attribute_code"] in {"type2_charging_cable_supplied", "domestic_socket_charging_cable"}}\n    for cfg in {"cfg_spring_essential_electric_70", "cfg_spring_expression_electric_70", "cfg_spring_extreme_electric_100"}:\n        assert selected[(cfg, "type2_charging_cable_supplied")]["availability_status"] == "standard"\n    for cfg in {"cfg_spring_essential_electric_70", "cfg_spring_extreme_electric_100"}:\n        row = selected[(cfg, "domestic_socket_charging_cable")]\n        assert row["availability_status"] == "optional"\n        assert "1500 PLN" in row["notes"]\n    assert ("cfg_spring_expression_electric_70", "domestic_socket_charging_cable") not in selected\n\ndef test_every_new_availability_record_has_artifact_provenance():\n    availability = [r for r in rows("data/master/configuration_attribute_availability.csv") if r["attribute_code"] in {"type2_charging_cable_supplied", "domestic_socket_charging_cable"}]\n    sources = {r["code"]: r for r in rows("data/imports/configuration_attribute_availability_sources.csv")}\n    links = {r["availability_code"]: r for r in rows("data/imports/configuration_attribute_availability_source_links.csv")}\n    assert len(availability) == 5\n    for row in availability:\n        link = links[row["code"]]\n        assert sources[link["availability_source_code"]]["source_artifact_id"].startswith("src_spring_")\n''',
        encoding="utf-8",
    )


def advance_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    state["summary"] = "Pakiet `spring_charging_cable_representation_migration_001` został przygotowany w PR #460: rozdzielono przewód Type 2 od przewodu do gniazdka domowego, wpisano wyłącznie potwierdzoną dostępność Spring i dodano provenance na poziomie rekordów."
    candidates = [candidate for candidate in state.get("candidate_next_work_packages", []) if candidate.get("id") != "spring_charging_cable_representation_migration_001"]
    state["candidate_next_work_packages"] = candidates
    next_candidate = sorted(candidates, key=lambda candidate: candidate.get("priority", 999))[0]
    state["next_work_package"] = {
        "id": next_candidate["id"],
        "objective": next_candidate["objective"],
        "acceptance_criteria": [
            "Zdefiniować jawny scoring wiarygodności źródeł zgodny z governance i lifecycle obserwacji.",
            "Wdrożyć model danych i walidację bez zmiany znaczenia istniejących obserwacji.",
            "Dodać testy regresji, uruchomić `make check` oraz `python3 tools/project_state.py --check`.",
        ],
        "recommended_context": [
            "project/SCHEMA_GOVERNANCE.md",
            "project/DATA_ARCHITECTURE.md",
            "project/SOURCE_INTAKE_CHECKLIST.md",
            "data/master/sources.csv",
        ],
    }
    recent = state.setdefault("context", {}).setdefault("recently_merged", [])
    if "PR #460" not in recent:
        recent.append("PR #460")
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["python3", str(ROOT / "tools/project_state.py")], cwd=ROOT, check=True)


def main() -> None:
    migrate_attributes()
    migrate_availability()
    migrate_provenance()
    write_regression_test()
    advance_state()


if __name__ == "__main__":
    main()
