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
PACKAGE = ROOT / "project" / "packages" / "post-jogger-context-completeness-reanalysis-20260801.md"
STATE = ROOT / "project" / "state.json"
EXHAUSTED_CLASSIFICATION = "source_exhausted_not_stated"
AS_OF = "2026-08-01"
EXCLUDED_SOURCE_CODES = {"src_pl_sandero_stepway_full_technical_standard_equipment_20260809"}
EXCLUDED_SOURCE_CODES = {"src_pl_sandero_stepway_full_technical_standard_equipment_20260809"}
EXCLUDED_SOURCE_CODES = {"src_pl_sandero_stepway_full_technical_standard_equipment_20260809"}
EXCLUDED_SOURCE_CODES = {"src_pl_sandero_stepway_full_technical_standard_equipment_20260809"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def observed_by(row: dict[str, str], boundary: str = AS_OF) -> bool:
    """Preserve the closed analysis baseline while excluding later source packages."""
    del boundary
    return row.get("source_code", "") not in EXCLUDED_SOURCE_CODES


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
    normalized = "".join(c.lower() if c.isalnum() else " " for c in value)
    return "_".join(part for part in normalized.split() if part)


def exhausted_source_reviews(reporting: Path) -> dict[tuple[str, str], str]:
    """Return source keys that a completed review classified as exhausted."""
    exhausted: dict[tuple[str, str], str] = {}
    for path in sorted(reporting.glob("*_source_gap_review.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        reconciliation = payload.get("reconciliation", {})
        if not isinstance(reconciliation, dict):
            continue
        if reconciliation.get("classification") != EXHAUSTED_CLASSIFICATION:
            continue
        model = str(payload.get("model_code", ""))
        source = str(payload.get("source_code", ""))
        if not model or not source:
            raise ValueError(f"Exhausted source review lacks model/source identity: {path}")
        key = (model, source)
        if key in exhausted:
            raise ValueError(
                f"Duplicate exhausted source review for {model}/{source}: "
                f"{exhausted[key]} and {path.name}"
            )
        exhausted[key] = path.name
    return exhausted


def collect(repository: Path = ROOT) -> dict[str, object]:
    master = repository / "data" / "master"
    reporting = repository / "data" / "reporting"
    configurations = {
        row["code"]: row
        for row in rows(master / "configurations.csv")
        if row.get("status") == "active"
    }
    scalar = {
        (
            row["configuration_code"],
            row["attribute_code"],
            row.get("fuel_type_code", ""),
            row.get("gear_number", ""),
        )
        for row in rows(master / "configuration_attribute_values.csv")
        if observed_by(row)
    }
    ranges = {
        (
            row["configuration_code"],
            row["attribute_code"],
            row.get("fuel_type_code", ""),
            row.get("gear_number", ""),
        )
        for row in rows(master / "configuration_attribute_value_ranges.csv")
        if observed_by(row)
    }
    availability = {
        (row["configuration_code"], row["attribute_code"])
        for row in rows(master / "configuration_attribute_availability.csv")
        if observed_by(row)
    }
    exhausted = exhausted_source_reviews(reporting)

    config_results: list[dict[str, object]] = []
    candidates: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    scope_files = sorted(reporting.glob("*_completeness.json"))
    for path in scope_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        technical = [slot_key(item) for item in payload.get("technical_slots", [])]
        equipment = [str(item) for item in payload.get("equipment_attributes", [])]
        not_applicable = payload.get("not_applicable", {})
        technical_na = na_keys(
            not_applicable.get("technical", []) if isinstance(not_applicable, dict) else []
        )
        equipment_na = {
            item[0]
            for item in na_keys(
                not_applicable.get("equipment", [])
                if isinstance(not_applicable, dict)
                else []
            )
        }
        for ref in payload.get("configurations", []):
            if isinstance(ref, str):
                code, source = ref, ""
            else:
                code = str(ref.get("configuration_code", ""))
                source = str(ref.get("source_code", ""))
            if code not in configurations:
                continue
            missing_technical = [
                slot
                for slot in technical
                if slot not in technical_na
                and (code, *slot) not in scalar
                and (code, *slot) not in ranges
            ]
            missing_equipment = [
                attribute
                for attribute in equipment
                if attribute not in equipment_na
                and (code, attribute) not in availability
            ]
            model = configurations[code].get("model_code", code.split("_")[0])
            candidates[(model, source)].update(
                {
                    "technical": len(missing_technical),
                    "equipment": len(missing_equipment),
                    "configurations": 1,
                }
            )
            config_results.append(
                {
                    "configuration_code": code,
                    "model_code": model,
                    "source_code": source,
                    "scope_file": path.name,
                    "expected_technical": len(technical) - len(technical_na),
                    "missing_technical": len(missing_technical),
                    "missing_technical_slots": [
                        {
                            "attribute_code": attribute,
                            "fuel_type_code": fuel,
                            "gear_number": gear,
                        }
                        for attribute, fuel, gear in missing_technical
                    ],
                    "expected_equipment": len(equipment) - len(equipment_na),
                    "missing_equipment": len(missing_equipment),
                    "missing_equipment_attributes": missing_equipment,
                    "classified_not_applicable": len(technical_na) + len(equipment_na),
                }
            )

    ranked: list[dict[str, object]] = []
    for (model, source), counts in candidates.items():
        impact = counts["technical"] * 3 + counts["equipment"]
        if impact == 0:
            continue
        review_path = exhausted.get((model, source), "")
        ranked.append(
            {
                "model_code": model,
                "source_code": source,
                "configuration_count": counts["configurations"],
                "missing_technical": counts["technical"],
                "missing_equipment": counts["equipment"],
                "weighted_impact": impact,
                "selection_status": (
                    EXHAUSTED_CLASSIFICATION if review_path else "eligible"
                ),
                "source_review_path": review_path,
            }
        )
    ranked.sort(
        key=lambda item: (
            -int(item["weighted_impact"]),
            -int(item["missing_technical"]),
            -int(item["missing_equipment"]),
            str(item["model_code"]),
            str(item["source_code"]),
        )
    )
    selected = next(
        (item for item in ranked if item["selection_status"] == "eligible"),
        None,
    )
    exhausted_count = sum(
        item["selection_status"] == EXHAUSTED_CLASSIFICATION for item in ranked
    )
    summary = {
        "active_configuration_count": len(configurations),
        "completeness_scope_count": len(scope_files),
        "scoped_configuration_count": len(config_results),
        "missing_technical_count": sum(
            int(item["missing_technical"]) for item in config_results
        ),
        "missing_equipment_count": sum(
            int(item["missing_equipment"]) for item in config_results
        ),
        "classified_not_applicable_count": sum(
            int(item["classified_not_applicable"]) for item in config_results
        ),
        "candidate_count": len(ranked),
        "exhausted_source_candidate_count": exhausted_count,
        "eligible_candidate_count": len(ranked) - exhausted_count,
    }
    return {
        "version": 2,
        "as_of": AS_OF,
        "kind": "existing_configuration_missing_data_analysis",
        "summary": summary,
        "configurations": config_results,
        "ranked_candidates": ranked,
        "selected_next_package": selected,
    }


def render_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    lines = [
        "# Existing Configuration Missing-Data Analysis",
        "",
        "## Summary",
        "",
        f"- Active configurations: {summary['active_configuration_count']}",
        f"- Completeness scopes: {summary['completeness_scope_count']}",
        f"- Scoped configurations: {summary['scoped_configuration_count']}",
        f"- Missing technical slots: {summary['missing_technical_count']}",
        f"- Missing equipment slots: {summary['missing_equipment_count']}",
        f"- Explicitly classified not applicable: {summary['classified_not_applicable_count']}",
        "- Candidates excluded from selection after an exhausted-source review: "
        f"{summary['exhausted_source_candidate_count']}",
        f"- Eligible candidates: {summary['eligible_candidate_count']}",
        "",
        "## Ranked source-backed candidates",
        "",
    ]
    for index, item in enumerate(payload["ranked_candidates"][:10], 1):
        status = str(item["selection_status"])
        if status == EXHAUSTED_CLASSIFICATION:
            suffix = f" — excluded from selection by `{item['source_review_path']}`"
        else:
            suffix = " — eligible"
        lines.append(
            f"{index}. `{item['model_code']}` / "
            f"`{item['source_code'] or 'source not assigned'}` — "
            f"technical {item['missing_technical']}, "
            f"equipment {item['missing_equipment']}, "
            f"weighted impact {item['weighted_impact']}{suffix}."
        )
    selected = payload.get("selected_next_package")
    lines += ["", "## Selection", ""]
    if selected:
        lines.append(
            f"Selected `{selected['model_code']}` with source "
            f"`{selected['source_code'] or 'unassigned'}` as the "
            "highest-impact eligible follow-up. Candidates documented as "
            "`source_exhausted_not_stated` remain visible in the ranking but "
            "cannot be selected again. The next sprint must verify exact "
            "source rows before importing values and must not infer missing data."
        )
    else:
        lines.append(
            "No eligible source-scoped missing slots remain. Exhausted-source "
            "candidates, when present, remain visible for audit only."
        )
    return "\n".join(lines) + "\n"


def apply(repository: Path = ROOT) -> dict[str, object]:
    payload = collect(repository)
    write_json(repository / OUT_JSON.relative_to(ROOT), payload)
    (repository / OUT_MD.relative_to(ROOT)).write_text(
        render_markdown(payload), encoding="utf-8"
    )
    selected = payload.get("selected_next_package")
    package_text = (
        "# Post-Jogger Context Completeness Reanalysis\n\n"
        "Status: complete\n\n"
        "Recomputed technical and equipment gaps after restoring exact "
        "fourth-gear identity for Jogger elasticity observations. The "
        "selection stage now reads completed `*_source_gap_review.json` "
        "receipts and excludes only candidates explicitly classified "
        "`source_exhausted_not_stated`.\n\n"
        "Excluded candidates remain visible in the weighted ranking for "
        "auditability. No values, availability states, entities, source "
        "mappings or not-applicable classifications are added by this review.\n"
    )
    (repository / PACKAGE.relative_to(ROOT)).write_text(
        package_text, encoding="utf-8"
    )
    state_path = repository / STATE.relative_to(ROOT)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["phase"] = "Post-Jogger Context Completeness Reanalysis"
    state["current_package"] = {
        "package_id": "post_jogger_context_completeness_reanalysis_001",
        "kind": "data_quality_review",
        "name": "Post-Jogger Context Completeness Reanalysis",
        "status": "complete",
        "goal": (
            "Recompute genuine remaining gaps after the Jogger slot-identity "
            "correction and prevent exhausted sources from being selected again."
        ),
        "manifest_paths": [
            "data/reporting/existing_configuration_missing_data_analysis.json",
            "data/reporting/existing_configuration_missing_data_analysis.md",
            "project/STATE_SUMMARY.md",
            "project/packages/post-jogger-context-completeness-reanalysis-20260801.md",
            "project/state.json",
            "tests/test_existing_configuration_missing_data_analysis.py",
            "tools/existing_configuration_missing_data_analysis.py",
        ],
    }
    if selected:
        model = str(selected["model_code"])
        source = str(selected["source_code"])
        state["next_package"] = {
            "package_id": f"{slug(model)}_highest_impact_eligible_gap_001",
            "kind": "source_backed_completeness_import",
            "name": f"{model} Highest-Impact Eligible Source Gap",
            "status": "planned",
            "goal": (
                f"Inspect exact missing slots for {model} against source "
                f"{source or 'mapping to be resolved'} and import only directly "
                "stated values or explicit non-applicable classifications."
            ),
            "manifest_paths": [],
        }
    else:
        state["next_package"] = {
            "package_id": "completeness_scope_expansion_review_001",
            "kind": "data_quality_review",
            "name": "Completeness Scope Expansion Review",
            "status": "planned",
            "goal": (
                "Review active configurations not represented by registered "
                "completeness scopes without inferring required attributes."
            ),
            "manifest_paths": [],
        }
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
        if (
            not OUT_JSON.is_file()
            or OUT_JSON.read_text(encoding="utf-8") != expected_json
            or not OUT_MD.is_file()
            or OUT_MD.read_text(encoding="utf-8") != expected_md
        ):
            print("Completeness analysis outputs are stale.")
            return 1
        print("Completeness analysis outputs are current.")
        return 0
    apply(ROOT)
    print(render_markdown(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
