#!/usr/bin/env python3
"""Materialize the accepted brochure chassis measurement context decision."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTES = ROOT / "data" / "master" / "attributes.csv"
DECISIONS = ROOT / "project" / "DECISIONS.md"
STATE = ROOT / "project" / "state.json"
REPORT = ROOT / "data" / "reporting" / "brochure_chassis_measurement_context_model.json"

NEW_ATTRIBUTES = [
    {
        "id": "389",
        "code": "turning_circle_between_kerbs",
        "category": "Performance",
        "name": "Turning circle between kerbs",
        "data_type": "decimal",
        "unit": "m",
        "description": "Minimum turning-circle diameter explicitly measured between kerbs; distinct from wheel-track and unspecified turning-circle observations.",
        "status": "active",
    },
    {
        "id": "390",
        "code": "turning_circle_wheel_track",
        "category": "Performance",
        "name": "Turning circle by wheel track",
        "data_type": "decimal",
        "unit": "m",
        "description": "Minimum turning-circle diameter explicitly stated using the wheel-track basis; distinct from between-kerbs and unspecified observations.",
        "status": "active",
    },
    {
        "id": "391",
        "code": "maximum_kerb_weight",
        "category": "Weights",
        "name": "Maximum kerb weight",
        "data_type": "integer",
        "unit": "kg",
        "description": "Maximum vehicle kerb weight explicitly qualified as maximum by the source; distinct from minimum and unqualified kerb-weight observations.",
        "status": "active",
    },
    {
        "id": "392",
        "code": "payload",
        "category": "Weights",
        "name": "Payload",
        "data_type": "integer",
        "unit": "kg",
        "description": "Source-stated payload observation. Exact values use the scalar table and bounded intervals use the range table; distinct from an explicitly stated maximum payload.",
        "status": "active",
    },
]

DECISION = """

---

## D-016 — Brochure chassis measurement context

Status: Accepted

Date: 2026-07-26

### Decision

Basis-qualified brochure chassis measurements use separate, unambiguous
attributes instead of a new generic context table:

- `turning_circle_between_kerbs` stores a turning-circle diameter explicitly
  measured between kerbs;
- `turning_circle_wheel_track` stores a turning-circle diameter explicitly
  stated using the wheel-track basis;
- `maximum_kerb_weight` stores an explicitly maximum-qualified kerb mass and
  remains distinct from `minimum_kerb_weight` and unqualified `kerb_weight`;
- `payload` stores a neutral source-stated payload. A single value is written
  to `configuration_attribute_values.csv`; a bounded interval is written to
  `configuration_attribute_value_ranges.csv` without flattening. The existing
  `maximum_payload` remains reserved for an explicitly stated maximum.

Compound tyre, suspension, brake and steering specifications reuse the
existing string attributes `standard_tyre_specification`, `front_suspension`,
`rear_suspension`, `front_brake_type`, `rear_brake_type` and `steering_type`.
The complete source wording is preserved rather than decomposed without
controlled dictionaries.

The legacy `turning_circle` attribute remains active for existing observations
whose measurement basis was not modeled. New basis-qualified brochure evidence
must use one of the two dedicated attributes.

Model-wide or powertrain-wide evidence may be projected to exact active
configurations only when the source scope maps unambiguously. Ambiguous or
physically inconsistent source labels are not semantically reassigned without
corrected official evidence.

### Rationale

The reviewed brochures use at least two materially different turning-diameter
bases. They also distinguish minimum and maximum kerb mass and sometimes state
payload as an interval. Folding these observations into existing context-free
or maximum-only attributes would lose source meaning. A dedicated generic
context table would be disproportionate to the current evidence and would
require broad changes to validators, reporting, exports and comparisons.

### Consequences

- Four attributes are added without introducing a new table.
- Turning-circle values with different bases remain directly comparable only
  within the same attribute.
- Payload intervals reuse the existing range infrastructure.
- Existing source-text specification attributes remain canonical.
- The Jogger mass-table label conflict remains blocked until corrected official
  evidence is available.
"""


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def materialize_attributes() -> None:
    fieldnames, rows = read_csv(ATTRIBUTES)
    by_code = {row["code"]: row for row in rows}
    by_id = {row["id"]: row for row in rows}
    changed = False
    for expected in NEW_ATTRIBUTES:
        existing = by_code.get(expected["code"])
        if existing is not None:
            if existing != expected:
                raise RuntimeError(f"existing attribute differs: {expected['code']}")
            continue
        if expected["id"] in by_id:
            raise RuntimeError(f"attribute id already used: {expected['id']}")
        rows.append(expected)
        by_code[expected["code"]] = expected
        by_id[expected["id"]] = expected
        changed = True
    if changed:
        rows.sort(key=lambda row: int(row["id"]))
        write_csv(ATTRIBUTES, fieldnames, rows)


def materialize_decision() -> None:
    text = DECISIONS.read_text(encoding="utf-8")
    heading = "## D-016 — Brochure chassis measurement context"
    if heading in text:
        if text.count(heading) != 1:
            raise RuntimeError("D-016 is duplicated")
        return
    DECISIONS.write_text(text.rstrip() + DECISION + "\n", encoding="utf-8")


def materialize_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-26"
    state["phase"] = "Brochure Chassis Measurement Context Modeling"
    state["current_package"] = {
        "name": "Brochure Chassis Measurement Context Modeling",
        "status": "complete",
        "goal": "Define explicit turning-circle measurement bases, maximum kerb mass and scalar-or-range payload semantics while reusing existing source-text chassis specification attributes.",
    }
    state["next_package"] = {
        "name": "Sandero and Stepway Chassis Observation Import",
        "status": "planned",
        "goal": "Import the unambiguous between-kerbs turning diameter, maximum kerb weight and source-text tyre and suspension observations for the active Sandero and Sandero Stepway configurations under D-016.",
    }
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verify_report_contract() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    if payload.get("decision_reference") != "D-016":
        raise RuntimeError("report decision reference differs")
    report_attributes = {str(item.get("code", "")): item for item in payload.get("new_attributes", [])}
    if set(report_attributes) != {item["code"] for item in NEW_ATTRIBUTES}:
        raise RuntimeError("report attribute set differs")


def main() -> int:
    verify_report_contract()
    materialize_attributes()
    materialize_decision()
    materialize_state()
    print("PASS: brochure chassis measurement context modeling materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
