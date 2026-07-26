#!/usr/bin/env python3
"""Synchronize Sandero reporting scopes and evidence after dimension observations."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_completeness as completeness  # noqa: E402

REPORTING = ROOT / "data" / "reporting"
ATTRIBUTES = {
    row["code"]: row
    for row in __import__("csv").DictReader(
        (ROOT / "data" / "master" / "attributes.csv").open(encoding="utf-8-sig", newline="")
    )
}
NEW_DEFAULT_SLOTS = {
    "front_track",
    "ground_clearance",
    "overall_height",
    "overall_width_with_mirrors",
    "rear_track",
}
SCOPES = (
    ("configuration_completeness.json", "configuration_gap_evidence.json"),
    ("sandero_ecog120_manual_completeness.json", "sandero_ecog120_manual_gap_evidence.json"),
    ("sandero_ecog120_automatic_completeness.json", "sandero_ecog120_automatic_gap_evidence.json"),
)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_default_slots() -> None:
    path = REPORTING / "configuration_completeness.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    slots = payload["technical_slots"]
    current = {(item["attribute_code"], item.get("fuel_type_code", "")) for item in slots}
    for attribute in NEW_DEFAULT_SLOTS:
        if (attribute, "") not in current:
            slots.append({"attribute_code": attribute, "fuel_type_code": ""})
    slots.sort(key=lambda item: (item["attribute_code"], item.get("fuel_type_code", "")))
    write_json(path, payload)


def gap_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(item.get("configuration_code", "")),
        str(item.get("attribute_code", "")),
        str(item.get("fuel_type_code", "")),
    )


def decision_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return gap_key(item)


def make_decision(template: dict[str, Any], key: tuple[str, str, str]) -> dict[str, Any]:
    configuration, attribute, fuel = key
    decision = deepcopy(template)
    category = ATTRIBUTES.get(attribute, {}).get("category", "")
    decision.update(
        {
            "attribute_code": attribute,
            "auto_import": False,
            "basis": None,
            "candidate_value": "",
            "category": category,
            "classification": "not_stated",
            "configuration_code": configuration,
            "domain": "technical",
            "fuel_type_code": fuel,
            "manual_source_review_required": False,
            "source_page": None,
            "source_section": "",
            "source_text": "",
        }
    )
    if not str(decision.get("reason_code", "")).startswith("not_stated"):
        decision["reason_code"] = "not_stated_on_relevant_pages"
    if not str(decision.get("review_note", "")).strip():
        decision["review_note"] = "No direct configured source statement was found on every reviewed relevant source page."
    context = fuel or "none"
    decision["triage_key"] = "|".join(
        [
            "technical",
            str(decision.get("source_code", "")),
            configuration,
            category,
            attribute,
            context,
        ]
    )
    return decision


def synchronize(spec_name: str, evidence_name: str) -> None:
    spec_path = REPORTING / spec_name
    evidence_path = REPORTING / evidence_name
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    report = completeness.collect_report(ROOT, spec_path, evidence.get("as_of"))
    missing = {gap_key(item) for item in report["gaps"]["technical"]}

    decisions = list(evidence.get("decisions", []))
    equipment = [item for item in decisions if item.get("domain") != "technical"]
    technical = [item for item in decisions if item.get("domain") == "technical"]
    templates: dict[str, dict[str, Any]] = {}
    for item in technical + equipment:
        configuration = str(item.get("configuration_code", ""))
        templates.setdefault(configuration, item)

    kept = {
        decision_key(item): item
        for item in technical
        if decision_key(item) in missing
    }
    for key in sorted(missing):
        if key in kept:
            continue
        template = templates.get(key[0])
        if template is None:
            raise RuntimeError(f"no evidence template for {key[0]} in {evidence_name}")
        kept[key] = make_decision(template, key)

    merged = [*equipment, *kept.values()]
    merged.sort(
        key=lambda item: (
            str(item.get("domain", "")),
            str(item.get("configuration_code", "")),
            str(item.get("attribute_code", "")),
            str(item.get("fuel_type_code", "")),
        )
    )
    evidence["decisions"] = merged
    write_json(evidence_path, evidence)
    print(f"PASS: {evidence_name}: technical gaps={len(missing)}, decisions={len(merged)}")


def main() -> int:
    add_default_slots()
    for spec_name, evidence_name in SCOPES:
        synchronize(spec_name, evidence_name)
    print("PASS: generic dimension reporting evidence synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
