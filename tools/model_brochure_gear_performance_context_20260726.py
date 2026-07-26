#!/usr/bin/env python3
"""Materialize and verify the selected-gear observation-context decision."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "data" / "reporting" / "brochure_gear_performance_context_model.json"
DECISIONS = ROOT / "project" / "DECISIONS.md"
VALUES = ROOT / "data" / "master" / "configuration_attribute_values.csv"
STATE = ROOT / "project" / "state.json"

DECISION_BLOCK = """

## D-024 — Observation-level selected-gear context

Status: Accepted
Date: 2026-07-26

### Decision

Gear-qualified performance observations remain numeric rows in
`configuration_attribute_values.csv` and reuse the neutral
`elasticity_80_120` attribute. The follow-up schema package shall add one
optional `gear_number` column after `fuel_type_code` and before `value`.

`gear_number` stores a canonical positive integer only when the source
explicitly qualifies the observation by one selected forward gear. Examples
include `4`, `5` and `6`. An empty field means that the source does not state a
selected-gear qualifier. It must not be interpreted as `unknown`, all gears,
top gear, the highest available gear or not applicable.

The existing observation and configuration dimensions remain authoritative:

- the 80–120 km/h speed interval is part of the canonical attribute meaning;
- LPG and petrol alternatives use the existing observation-level
  `fuel_type_code` from D-014;
- five- and seven-seat distinctions target exact configurations and reuse
  canonical `number_of_seats` data;
- powertrain and transmission are properties of the exact target
  configuration.

These dimensions shall not be duplicated in a new context relation or in
additional columns.

### Evidence

The reviewed official brochure tables contain:

- Sandero page 17: fourth- and fifth-gear elasticity, including separate LPG
  and petrol values for Eco-G 120;
- Sandero Stepway page 17: fourth-, fifth- and sixth-gear elasticity where
  stated, including separate LPG and petrol values;
- Jogger page 19: fourth-gear elasticity separated by exact five- and
  seven-seat variants and by fuel where the powertrain is bi-fuel.

The source may explicitly name a gear for an automatic transmission. Such a
value may use `gear_number` exactly as stated. Missing gear values are not
inferred from `gear_count`, transmission type or neighbouring table rows.

### Validation and reporting

The schema foundation shall enforce that:

- `gear_number` is empty or a canonical positive integer;
- a populated value is permitted only for an explicitly eligible performance
  attribute, initially `elasticity_80_120`;
- gear-distinct observations may share configuration, attribute, fuel, date
  and source;
- two rows with the same complete observation identity and date remain a
  semantic collision;
- latest-value selection, comparisons, shortlist exports and data products
  include `gear_number` in the technical observation key.

Existing values remain unchanged. During schema migration they receive an
empty `gear_number` unless their current source-backed meaning already
contains an explicitly modeled selected gear in a future reviewed import.

### Rejected alternatives

- Gear-specific attribute codes such as `elasticity_80_120_4th_gear` would
  duplicate one fact and fragment comparisons.
- A separate one-to-one context relation is disproportionate for one scalar
  qualifier already analogous to observation-level fuel context.
- A generic key-value measurement-context table would be untyped and is not
  justified by the reviewed evidence.
- Passenger layout, fuel, powertrain and transmission must not be duplicated
  because the current model already represents them.

### Scope boundary

This decision imports no elasticity values and changes no master-data schema.
Cargo measurement context remains governed independently by D-023. The next
package implements the optional column, validation, import-spec, SQLite,
data-dictionary and reporting support before any brochure performance values
are imported.
""".rstrip() + "\n"


class ModelError(RuntimeError):
    pass


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ModelError(message)


def apply() -> None:
    text = DECISIONS.read_text(encoding="utf-8")
    marker = "## D-024 — Observation-level selected-gear context"
    if marker not in text:
        DECISIONS.write_text(text.rstrip() + DECISION_BLOCK, encoding="utf-8")


def check() -> None:
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    ensure(model.get("status") == "accepted", "model is not accepted")
    ensure(model.get("canonical_attribute") == "elasticity_80_120", "canonical attribute differs")
    decision = model.get("decision")
    ensure(isinstance(decision, dict), "decision is missing")
    ensure(decision.get("storage") == "configuration_attribute_values_optional_column", "storage decision differs")
    ensure(decision.get("planned_column") == "gear_number", "planned column differs")
    ensure(decision.get("data_type") == "positive_integer", "gear type differs")
    evidence = model.get("source_evidence")
    ensure(isinstance(evidence, list) and len(evidence) == 3, "source evidence differs")
    ensure({tuple(item.get("gear_numbers", [])) for item in evidence} == {(4, 5), (4, 5, 6), (4,)}, "gear evidence differs")

    decisions = DECISIONS.read_text(encoding="utf-8")
    marker = "## D-024 — Observation-level selected-gear context"
    ensure(decisions.count(marker) == 1, "D-024 decision must occur exactly once")
    ensure("configuration_attribute_values.csv" in decisions and "gear_number" in decisions, "D-024 content is incomplete")

    with VALUES.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        count = sum(1 for _ in reader)
    ensure(
        header == [
            "id", "code", "configuration_code", "attribute_code",
            "fuel_type_code", "value", "observation_date", "source_code", "notes",
        ],
        "modeling package changed the master value schema",
    )
    ensure(count == 2118, "modeling package changed configuration values")

    state = json.loads(STATE.read_text(encoding="utf-8"))
    ensure(state.get("phase") == "Brochure Gear-Specific Performance Context Modeling", "state phase differs")
    ensure(state.get("baseline", {}).get("tests") == 813, "test baseline differs")
    ensure(state.get("baseline", {}).get("rows") == 8782, "master row baseline differs")
    ensure(state.get("next_package", {}).get("name") == "Brochure Gear-Specific Performance Schema Foundation", "next package differs")
    print("PASS: brochure gear-specific performance context model")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.apply:
            apply()
        check()
    except (ModelError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
