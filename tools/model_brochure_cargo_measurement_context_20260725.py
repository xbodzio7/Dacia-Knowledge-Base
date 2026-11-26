#!/usr/bin/env python3
"""Materialize and verify the brochure cargo measurement-context decision."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "project" / "DECISIONS.md"
STATE = ROOT / "project" / "state.json"
CHANGELOG = ROOT / "CHANGELOG.md"
REVIEW = ROOT / "project" / "reviews" / "brochure-cargo-measurement-context-model-2026-07-25.md"
PACKAGE = ROOT / "project" / "packages" / "brochure-cargo-measurement-context-model-20260725.md"
REPORT = ROOT / "data" / "reporting" / "brochure_cargo_measurement_context_model.json"

DECISION_HEADING = "## D-023 — Contextual cargo-volume observations"
CHANGELOG_ENTRY = (
    "* Accepted a context-preserving cargo-volume model that keeps numeric observations in "
    "`configuration_attribute_values.csv` and defines a separate one-to-one cargo context "
    "relation for measurement basis, seat state, compartment and equipment qualifiers."
)

DECISION = r"""## D-023 — Contextual cargo-volume observations

Status: Accepted

Date: 2026-07-25

### Decision

Context-rich luggage-capacity observations remain numeric configuration values in
`configuration_attribute_values.csv`. New brochure imports use the existing neutral
`boot_capacity` attribute rather than creating further attribute codes that embed VDA,
seat, spare-wheel, floor or compartment qualifiers.

A follow-up schema package shall add an optional one-to-one relation named
`configuration_cargo_volume_contexts.csv`. Each row shall reference exactly one
`configuration_attribute_values.code` through
`configuration_attribute_value_code`. A value may have zero or one cargo-context row;
a context row without its referenced value is invalid.

The planned relation shall contain:

- `id`;
- `code`;
- `configuration_attribute_value_code`;
- required `measurement_basis_code`;
- optional `second_row_state_code`;
- optional `third_row_state_code`;
- required `compartment_code`;
- optional `spare_wheel_state_code`;
- optional `tyre_repair_kit_state_code`;
- optional `double_floor_state_code`;
- `notes`.

The schema shall use controlled dictionaries for:

- measurement basis: `vda_iso_3832` and `ordinary_litre`;
- seat-row state: `upright`, `folded`, `removed` and
  `folded_or_removed` when the source explicitly groups those alternatives;
- compartment: `main_luggage_compartment`, `underfloor_compartment` and
  `source_stated_total`;
- presence state: `present` and `absent`.

Empty optional context fields mean that the source did not qualify that dimension. They
must not be interpreted as `absent`, `unknown` or a default state. Spare-wheel,
tyre-repair-kit and double-floor states are independent facts and must not be inferred
from one another.

Passenger layout and drive type are stable properties of the target configuration and
shall not be duplicated in the cargo-context relation. A brochure value split by five
or seven seats, or by 4x2 or 4x4, may be imported only into exact configurations whose
canonical seat count and drive data match the source group. If an exact target is not
modeled, the value remains unimported.

The `boot_capacity` unit remains litres. A VDA figure stated in cubic decimetres may be
stored at the numerically identical litre value because one cubic decimetre equals one
litre, while `measurement_basis_code = vda_iso_3832` and source notes preserve the
measurement method and original wording.

Minimum and maximum cargo capacities are not separate future attributes. They are
observations of the same `boot_capacity` fact under different explicit seat-row,
compartment and equipment states. Separate underfloor capacity is a separate value row
with `compartment_code = underfloor_compartment`; it must not be added to a main or
total value unless the source explicitly supplies that total.

### Existing data

Existing observations and attributes that encode historical cargo qualifiers remain
unchanged, including:

- `cargo_volume_vda`;
- `cargo_volume_vda_to_luggage_cover`;
- `cargo_volume_vda_to_seatback`;
- `cargo_volume_without_spare_wheel_iso3832`;
- `maximum_cargo_volume_iso3832`.

They are not migrated or reinterpreted by this modeling package. New context-rich
brochure imports shall use `boot_capacity` plus the accepted context relation after the
schema, validators, SQLite export and reporting surfaces support it.

### Reporting and uniqueness

Context-distinct `boot_capacity` rows must not be collapsed into one scalar or selected
arbitrarily. Reporting shall either require an explicit cargo context or expose all
source-backed contexts. The follow-up schema package shall validate one-to-one context
cardinality, controlled references and cargo-attribute eligibility before any brochure
cargo values are imported.

### Scope boundary

This decision does not import cargo values and does not modify current master-data
schemas. Gear-specific 80–120 km/h elasticity remains a separate future modeling
question; no generic all-purpose measurement-context architecture is introduced here.
"""

REVIEW_TEXT = r"""# Brochure Cargo Measurement Context Model

Date: 2026-07-25

## Purpose

Define the smallest reusable representation that can preserve the cargo-volume contexts
found in the registered Sandero, Sandero Stepway, Jogger, Bigster and Duster brochures
without creating a new attribute for every combination of measurement method, seat
state and equipment state.

## Existing limitation

`configuration_attribute_values.csv` stores one numeric value with configuration,
attribute, fuel, date, source and notes. It cannot distinguish multiple valid
`boot_capacity` values for the same configuration and source when those values differ
by VDA versus ordinary litres, raised versus folded seats, underfloor versus main space,
or spare-wheel, repair-kit and double-floor conditions.

The catalogue already contains historical cargo attributes that encode selected
qualifiers in their names. Extending that pattern to all brochure combinations would
multiply attributes, make comparisons brittle and still fail to preserve grouped seat
states such as a folded-or-removed third row.

## Accepted representation

The numeric observation stays in `configuration_attribute_values.csv` under the neutral
`boot_capacity` attribute. A new optional one-to-one
`configuration_cargo_volume_contexts.csv` relation will carry only the context needed
to interpret that value.

Planned fields:

| Field | Requirement | Meaning |
| --- | --- | --- |
| `configuration_attribute_value_code` | required, unique | Referenced cargo value |
| `measurement_basis_code` | required | VDA/ISO 3832 or ordinary source-stated litres |
| `second_row_state_code` | optional | Upright, folded, removed or explicit grouped state |
| `third_row_state_code` | optional | Upright, folded, removed or explicit grouped state |
| `compartment_code` | required | Main, underfloor or source-stated total space |
| `spare_wheel_state_code` | optional | Explicit present or absent qualifier |
| `tyre_repair_kit_state_code` | optional | Explicit present or absent qualifier |
| `double_floor_state_code` | optional | Explicit present or absent qualifier |
| `notes` | optional | Remaining source wording and audit detail |

## Dimensions inherited from configuration

Five- versus seven-seat layout and 4x2 versus 4x4 grouping are preserved through the
exact target configuration. They are not duplicated in the context row. Importers must
prove that every selected configuration matches the brochure group before materializing
the value.

## Conservative rules

- Empty optional fields mean not stated, not absent.
- A repair kit is not inferred merely because a spare wheel is absent.
- A spare wheel is not inferred merely because a repair kit is absent.
- Main and underfloor volumes remain separate unless the source states a total.
- Maximum capacity is represented through explicit seat state, not a new maximum-only
  attribute.
- Context-distinct observations must remain separate in reports and SQLite.
- Existing specialized cargo observations are retained without migration.

## Rejected alternatives

### More cargo-specific attributes

Rejected because every new combination of VDA, seat row, compartment, wheel and floor
state would require another attribute and would encode observation context in the
vocabulary rather than the observation.

### Many optional columns in every value row

Rejected because almost all current configuration values do not need cargo-specific
columns. A sparse one-to-one relation keeps the stable value schema focused.

### Generic key-value measurement context

Rejected for this package because type-dependent keys and values would weaken reference
validation and introduce a broad architecture before another domain proves the need.
Gear-specific elasticity remains deferred.

## Follow-up

The next package shall implement the header-only relation and controlled dictionaries,
reference and semantic validation, SQLite discovery, data-dictionary coverage and
regression tests. No brochure cargo values shall be imported until those surfaces and
context-aware reporting behavior are available.
"""

PACKAGE_TEXT = r"""# Brochure Cargo Measurement Context Modeling

Date: 2026-07-25

## Purpose

Accept a minimal architecture for cargo-volume observations whose meaning depends on
measurement basis, seat-row state, compartment and equipment qualifiers.

## Decision

- Keep numeric values in `configuration_attribute_values.csv`.
- Use the existing neutral `boot_capacity` attribute for future context-rich imports.
- Add a separate optional one-to-one `configuration_cargo_volume_contexts.csv` relation
  in the next schema package.
- Preserve measurement basis and cargo-specific dynamic conditions in that relation.
- Preserve passenger layout and drive type through exact configuration identity.
- Retain existing specialized cargo attributes and observations without migration.

## Data impact

This package changes documentation, the machine-readable model contract and project
state only. It adds no master-data rows, no schema file and no brochure cargo value.

## Acceptance criteria

- architecture decision D-023 is recorded;
- the machine-readable contract exactly defines fields, dictionaries, inheritance and
  non-inference rules;
- the review explains accepted and rejected alternatives;
- project state selects a schema-foundation follow-up package;
- the complete repository test suite remains green.
"""

REPORT_DATA = {
    "version": 1,
    "kind": "brochure_cargo_measurement_context_model",
    "accepted_on": "2026-07-25",
    "status": "accepted",
    "value_relation": "data/master/configuration_attribute_values.csv",
    "canonical_attribute_code": "boot_capacity",
    "value_unit": "L",
    "context_relation": {
        "file": "data/master/configuration_cargo_volume_contexts.csv",
        "cardinality": "zero_or_one_context_per_configuration_attribute_value",
        "reference_column": "configuration_attribute_value_code",
        "fields": [
            "id",
            "code",
            "configuration_attribute_value_code",
            "measurement_basis_code",
            "second_row_state_code",
            "third_row_state_code",
            "compartment_code",
            "spare_wheel_state_code",
            "tyre_repair_kit_state_code",
            "double_floor_state_code",
            "notes",
        ],
        "required_fields": [
            "id",
            "code",
            "configuration_attribute_value_code",
            "measurement_basis_code",
            "compartment_code",
        ],
    },
    "controlled_dictionaries": {
        "cargo_measurement_bases": ["vda_iso_3832", "ordinary_litre"],
        "cargo_seat_states": ["upright", "folded", "removed", "folded_or_removed"],
        "cargo_compartment_types": [
            "main_luggage_compartment",
            "underfloor_compartment",
            "source_stated_total",
        ],
        "context_presence_states": ["present", "absent"],
    },
    "inherited_from_configuration": ["passenger_layout", "number_of_seats", "drive_type"],
    "rules": [
        "empty_optional_context_is_not_stated_not_absent",
        "spare_wheel_repair_kit_and_double_floor_are_independent",
        "main_underfloor_and_source_stated_total_are_not_interchangeable",
        "seat_and_drive_source_groups_require_exact_matching_configurations",
        "vda_dm3_is_normalized_numerically_to_litres_with_basis_preserved",
        "context_distinct_values_must_not_be_collapsed",
        "one_context_row_may_reference_only_a_boot_capacity_value",
    ],
    "legacy_policy": {
        "migrate_existing_values": False,
        "retained_attribute_codes": [
            "cargo_volume_vda",
            "cargo_volume_vda_to_luggage_cover",
            "cargo_volume_vda_to_seatback",
            "cargo_volume_without_spare_wheel_iso3832",
            "maximum_cargo_volume_iso3832",
        ],
    },
    "deferred": ["gear_specific_elasticity_context"],
    "next_package": "Brochure Cargo Context Schema Foundation",
}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _apply_decision() -> None:
    text = DECISIONS.read_text(encoding="utf-8")
    if DECISION_HEADING not in text:
        DECISIONS.write_text(text.rstrip() + "\n\n" + DECISION.rstrip() + "\n", encoding="utf-8")
    elif DECISION.rstrip() not in text:
        raise RuntimeError("existing D-023 content differs from the accepted contract")


def _apply_changelog() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    if CHANGELOG_ENTRY in text:
        return
    anchor = "### Added\n\n"
    if anchor not in text:
        raise RuntimeError("CHANGELOG Added section not found")
    CHANGELOG.write_text(text.replace(anchor, anchor + CHANGELOG_ENTRY + "\n", 1), encoding="utf-8")


def _apply_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("baseline", {}).get("rows") != 8145:
        raise RuntimeError("unexpected master-row baseline")
    state["updated_on"] = "2026-07-25"
    state["phase"] = "Brochure Cargo Measurement Context Modeling"
    state["baseline"]["tests"] = 766
    state["current_package"] = {
        "name": "Brochure Cargo Measurement Context Modeling",
        "status": "complete",
        "goal": (
            "Accept the smallest reusable representation for brochure cargo values by "
            "keeping numeric observations in configuration_attribute_values.csv and "
            "defining a one-to-one cargo context relation for measurement basis, seat "
            "state, compartment and explicit equipment qualifiers."
        ),
    }
    state["next_package"] = {
        "name": "Brochure Cargo Context Schema Foundation",
        "status": "planned",
        "goal": (
            "Implement the header-only configuration_cargo_volume_contexts relation, "
            "controlled context dictionaries, references, semantic validation, SQLite "
            "and data-dictionary coverage without importing brochure cargo values."
        ),
    }
    _write(STATE, json.dumps(state, ensure_ascii=False, indent=2))


def apply() -> None:
    _apply_decision()
    _apply_changelog()
    _write(REVIEW, REVIEW_TEXT)
    _write(PACKAGE, PACKAGE_TEXT)
    _write(REPORT, json.dumps(REPORT_DATA, ensure_ascii=False, indent=2))
    _apply_state()


def check() -> None:
    decisions = DECISIONS.read_text(encoding="utf-8")
    if decisions.count(DECISION_HEADING) != 1 or DECISION.rstrip() not in decisions:
        raise RuntimeError("D-023 decision contract mismatch")
    if CHANGELOG_ENTRY not in CHANGELOG.read_text(encoding="utf-8"):
        raise RuntimeError("changelog entry missing")
    if REVIEW.read_text(encoding="utf-8").rstrip() != REVIEW_TEXT.rstrip():
        raise RuntimeError("review document differs")
    if PACKAGE.read_text(encoding="utf-8").rstrip() != PACKAGE_TEXT.rstrip():
        raise RuntimeError("package document differs")
    if json.loads(REPORT.read_text(encoding="utf-8")) != REPORT_DATA:
        raise RuntimeError("machine-readable context model differs")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if not state.get("phase"):
        raise RuntimeError("project phase missing")
    if state.get("baseline", {}).get("tests", 0) < 766:
        raise RuntimeError("test baseline regressed")
    if state.get("baseline", {}).get("rows", 0) < 8145:
        raise RuntimeError("master-row baseline regressed")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package is not complete")
    if not state.get("next_package", {}).get("name"):
        raise RuntimeError("next package missing")
    print("PASS: brochure cargo measurement-context model contract")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.apply:
            apply()
        check()
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
