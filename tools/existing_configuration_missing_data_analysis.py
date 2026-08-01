#!/usr/bin/env python3
"""Recompute source-scoped missing-data impact for existing configurations."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
OUT_JSON = REPORTING / "existing_configuration_missing_data_analysis.json"
OUT_MD = REPORTING / "existing_configuration_missing_data_analysis.md"
PACKAGE = ROOT / "project" / "packages" / "existing-configuration-completeness-reanalysis-20260801.md"
STATE = ROOT / "project" / "state.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slot_key(slot: object) -> tuple[str, str, str]:
    if isinstance(slot, str):
        return slot, "", ""
    if not isinstance(slot, dict):
        raise ValueError(f"unsupported slot: {slot!r}")
    return (
        str(slot.get("attribute_code", "")),
        str(slot.get("fuel_type_code", "")),
        str(slot.get("gear_number", "")),
    )


def na_keys(value: object) -> set[tuple[str, str, str]]:
    if not isinstance(value, list):
        return set()
    return {slot_key(item) for item in value}


def slug(value: str) -> str:
    return "_".join(part for part in "".join(c.lower() if c.isalnum() else " " for c in value).split() if part)


def collect(repository: Path = ROOT) -> dict[str, object]:
    master = repository / "data" / "master"
    reporting = repository / "data" / "reporting"
    configurations = {r["code"]: r for r in rows(master / "configurations.csv") if r.get("status") == "active"}
    scalar = {(r["configuration_code"], r["attribute_code"], r.get("fuel_type_code", ""), r.get("gear_number", "")) for r in rows(master / "configuration_attribute_values.csv")}
    ranges = {(r["configuration_code"], r["attribute_code"], r.get("fuel_type_code", ""), r.get("gear_number", "")) for r in rows(master / "configuration_attribute_value_ranges.csv")}
    availability = {(r["configuration_code"], r["attribute_code"]) for r in rows(master / "configuration_attribute_availability.csv")}

    config_results: list[dict[str, object]] = []
    candidates: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    scope_files = sorted(reporting.glob("*_completeness.json"))
    for path in scope_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        technical = [slot_key(item) for item in payload.get("technical_slots", [])]
        equipment = [str(item) for item in payload.get("equipment_attributes", [])]
        not_applicable = payload.get("not_applicable", {})
        technical_na = na_keys(not_applicable.get("technical", []) if isinstance(not_applicable, dict) else [])
        equipment_na = {item[0] for item in na_keys(not_applicable.get("equipment", []) if isinstance(not_applicable, dict) else [])}
        for ref in payload.get("configurations", []):
            if isinstance(ref, str):
                code, source = ref, ""
            else:
                code, source = str(ref.get("configuration_code", "")), str(ref.get("source_code", ""))
            if code not in configurations:
                continue
            missing_technical = [s for s in technical if s not in technical_na and (code, *s) not in scalar and (code, *s) not in ranges]
            missing_equipment = [a for a in equipment if a not in equipment_na and (code, a) not in availability]
            model = configurations[code].get("model_code", code.split("_")[0])
            candidates[(model, source)].update({"technical": len(missing_technical), "equipment": len(missing_equipment), "configurations": 1})
            config_results.append({
                "configuration_code": code,
                "model_code": model,
                "source_code": source,
                "scope_file": path.name,
                "expected_technical": len(technical) - len(technical_na),
                "missing_technical": len(missing_technical),
                "missing_technical_slots": [dict(attribute_code=a, fuel_type_code=f, gear_number=g) for a, f, g in missing_technical],
                "expected_equipment": len(equipment) - len(equipment_na),
                "missing_equipment": len(missing_equipment),
                "missing_equipment_attributes": missing_equipment,
                "classified_not_applicable": len(technical_na) + len(equipment_na),
            })

    ranked = []
    for (model, source), counts in candidates.items():
        impact = counts["technical"] * 3 + counts["equipment"]
        if impact == 0:
            continue
        ranked.append({
            "model_code": model,
            "source_code": source,
            "configuration_count": counts["configurations"],
            "missing_technical": counts["technical"],
            "missing_equipment": counts["equipment"],
            "weighted_impact": impact,
        })
    ranked.sort(key=lambda x: (-x["weighted_impact"], -x["missing_technical"], -x["missing_equipment"], x["model_code"], x["source_code"]))
    selected = ranked[0] if ranked else None
    summary = {
        "active_configuration_count": len(configurations),
        "completeness_scope_count": len(scope_files),
        "scoped_configuration_count": len(config_results),
        "missing_technical_count": sum(int(x["missing_technical"]) for x in config_results),
        "missing_equipment_count": sum(int(x["missing_equipment"]) for x in config_results),
        "classified_not_applicable_count": sum(int(x["classified_not_applicable"]) for x in config_results),
        "candidate_count": len(ranked),
    }
    return {"version": 1, "as_of": "2026-08-01", "kind": "existing_configuration_missing_data_analysis", "summary": summary, "configurations": config_results, "ranked_candidates": ranked, "selected_next_package": selected}


def render_markdown(payload: dict[str, object]) -> str:
    s = payload["summary"]
    lines = ["# Existing Configuration Missing-Data Analysis", "", "## Summary", "", f"- Active configurations: {s['active_configuration_count']}", f"- Completeness scopes: {s['completeness_scope_count']}", f"- Scoped configurations: {s['scoped_configuration_count']}", f"- Missing technical slots: {s['missing_technical_count']}", f"- Missing equipment slots: {s['missing_equipment_count']}", f"- Explicitly classified not applicable: {s['classified_not_applicable_count']}", "", "## Ranked source-backed candidates", ""]
    for i, item in enumerate(payload["ranked_candidates"][:10], 1):
        lines.append(f"{i}. `{item['model_code']}` / `{item['source_code'] or 'source not assigned'}` — technical {item['missing_technical']}, equipment {item['missing_equipment']}, weighted impact {item['weighted_impact']}.")
    selected = payload.get("selected_next_package")
    lines += ["", "## Selection", ""]
    if selected:
        lines.append(f"Selected `{selected['model_code']}` with source `{selected['source_code'] or 'unassigned'}` as the highest-impact bounded follow-up. The next sprint must verify exact source rows before importing values and must not infer missing data.")
    else:
        lines.append("No source-scoped missing slots remain in registered completeness scopes.")
    return "\n".join(lines) + "\n"


def apply(repository: Path = ROOT) -> dict[str, object]:
    payload = collect(repository)
    write_json(repository / OUT_JSON.relative_to(ROOT), payload)
    (repository / OUT_MD.relative_to(ROOT)).write_text(render_markdown(payload), encoding="utf-8")
    selected = payload.get("selected_next_package")
    package_text = "# Existing Configuration Completeness Reanalysis\n\nStatus: complete\n\nRecomputed missing technical and equipment slots from registered completeness scopes after the Spring technical import. Explicit `not_applicable` classifications are excluded from missing-data impact. Candidates are ranked with technical slots weighted three times equipment slots because they affect core comparison output more strongly.\n\nNo values, availability states, entities or source mappings are added by this review.\n"
    (repository / PACKAGE.relative_to(ROOT)).write_text(package_text, encoding="utf-8")
    state_path = repository / STATE.relative_to(ROOT)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["phase"] = "Existing Configuration Completeness Reanalysis"
    state["current_package"] = {"package_id": "existing_configuration_completeness_reanalysis_001", "kind": "data_quality_review", "name": "Existing Configuration Completeness Reanalysis", "status": "complete", "goal": "Recompute configuration- and attribute-level missing-data impact after the Spring import and select the next bounded source-backed package.", "manifest_paths": ["data/reporting/existing_configuration_missing_data_analysis.json", "data/reporting/existing_configuration_missing_data_analysis.md", "project/STATE_SUMMARY.md", "project/packages/existing-configuration-completeness-reanalysis-20260801.md", "project/state.json", "tests/test_existing_configuration_missing_data_analysis.py", "tools/existing_configuration_missing_data_analysis.py"]}
    if selected:
        model = str(selected["model_code"])
        source = str(selected["source_code"])
        state["next_package"] = {"package_id": f"{slug(model)}_highest_impact_source_gap_001", "kind": "source_backed_completeness_import", "name": f"{model} Highest-Impact Source Gap", "status": "planned", "goal": f"Inspect exact missing slots for {model} against source {source or 'mapping to be resolved'} and import only directly stated values or explicit non-applicable classifications.", "manifest_paths": []}
    else:
        state["next_package"] = {"package_id": "completeness_scope_expansion_review_001", "kind": "data_quality_review", "name": "Completeness Scope Expansion Review", "status": "planned", "goal": "Review active configurations not represented by registered completeness scopes without inferring required attributes.", "manifest_paths": []}
    write_json(state_path, state)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = collect(ROOT)
    if args.check:
        expected_json = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        expected_md = render_markdown(payload)
        if not OUT_JSON.is_file() or OUT_JSON.read_text(encoding="utf-8") != expected_json or not OUT_MD.is_file() or OUT_MD.read_text(encoding="utf-8") != expected_md:
            print("Completeness analysis outputs are stale.")
            return 1
        print("Completeness analysis outputs are current.")
        return 0
    apply(ROOT)
    print(render_markdown(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
