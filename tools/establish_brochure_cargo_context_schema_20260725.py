#!/usr/bin/env python3
"""Materialize and verify the brochure cargo-context schema foundation."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REFERENCES = ROOT / "tools" / "validators" / "references.py"
STATUSES = ROOT / "tools" / "validators" / "statuses.py"
LEGACY_TOOL = ROOT / "tools" / "model_brochure_cargo_measurement_context_20260725.py"
LEGACY_TEST = ROOT / "tests" / "test_brochure_cargo_measurement_context_model.py"
STATE = ROOT / "project" / "state.json"
CHANGELOG = ROOT / "CHANGELOG.md"
REPORT = ROOT / "data" / "reporting" / "brochure_cargo_context_schema_foundation.json"
PACKAGE = ROOT / "project" / "packages" / "brochure-cargo-context-schema-foundation-20260725.md"
REVIEW = ROOT / "project" / "reviews" / "brochure-cargo-context-schema-foundation-2026-07-25.md"

RELATION = MASTER / "configuration_cargo_volume_contexts.csv"
DICTIONARIES = {
    MASTER / "enums" / "cargo_measurement_bases.csv": {
        "vda_iso_3832",
        "ordinary_litre",
    },
    MASTER / "enums" / "cargo_seat_states.csv": {
        "upright",
        "folded",
        "removed",
        "folded_or_removed",
    },
    MASTER / "enums" / "cargo_compartment_types.csv": {
        "main_luggage_compartment",
        "underfloor_compartment",
        "source_stated_total",
    },
    MASTER / "enums" / "context_presence_states.csv": {
        "present",
        "absent",
    },
}

EXPECTED_COLUMNS = [
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
]

CHANGELOG_ENTRY = (
    "* Added the header-only cargo-volume context relation, four controlled context "
    "dictionaries, eight reference rules, four lifecycle rules and semantic validation "
    "that restricts contexts to one `boot_capacity` observation."
)

PACKAGE_TEXT = r"""# Brochure Cargo Context Schema Foundation

Date: 2026-07-25

## Purpose

Implement the schema and validation surfaces accepted in D-023 without importing any
brochure cargo observation.

## Delivered schema

- header-only `data/master/configuration_cargo_volume_contexts.csv`;
- `cargo_measurement_bases.csv`;
- `cargo_seat_states.csv`;
- `cargo_compartment_types.csv`;
- `context_presence_states.csv`.

The relation references one existing configuration value and preserves measurement
basis, second- and third-row state, compartment and independent spare-wheel, repair-kit
and double-floor qualifiers.

## Validation

- eight cross-file reference rules;
- four active-status rules for the controlled dictionaries;
- one-to-one semantic cardinality by referenced value;
- rejection of contexts attached to attributes other than `boot_capacity`;
- automatic SQLite and data-dictionary discovery.

## Data impact

The four dictionaries add eleven controlled rows. The cargo-context relation remains
empty. Configuration values, value ranges, availability, prices and source mappings are
unchanged.

## Acceptance criteria

- 46 master CSV files and 8156 master rows;
- zero cargo-context observations;
- 1831 configuration values remain unchanged;
- complete validation and SQLite coverage;
- next work is context-aware reporting before brochure values are imported.
"""

REVIEW_TEXT = r"""# Brochure Cargo Context Schema Foundation Review

Date: 2026-07-25

## Scope

This package implements the storage and integrity foundation chosen by D-023. It does
not import Sandero, Sandero Stepway, Jogger, Bigster or Duster brochure cargo values.

## Relation

`configuration_cargo_volume_contexts.csv` is optional and one-to-one with
`configuration_attribute_values.code`. Its required fields are the referenced value,
measurement basis and compartment. Seat-row and equipment qualifiers remain optional;
an empty optional field means that the source did not state that dimension.

## Controlled vocabularies

Measurement basis distinguishes VDA/ISO 3832 from ordinary source-stated litres. Seat
states preserve upright, folded, removed and explicitly grouped folded-or-removed
wording. Compartment types distinguish main, underfloor and source-stated total volume.
Presence states contain only explicit present and absent meanings.

## Semantic boundary

The semantic validator rejects:

- more than one context row for the same value code;
- a context row attached to any attribute other than `boot_capacity`.

Foreign-key validation separately rejects missing values and invalid dictionary codes.
No inference is made between spare wheel, repair kit and double floor.

## Tooling coverage

The generic SQLite builder and data-dictionary generator discover all five new CSVs
without special cases. Regression tests prove the empty production relation, exact
vocabularies, references, statuses, semantic failures, SQLite tables and dictionary
sections.

## Follow-up

The next package must make reporting and comparison outputs context-aware. No brochure
cargo values should be imported until reports expose all context-distinct observations
instead of collapsing them into one scalar.
"""

REPORT_DATA = {
    "version": 1,
    "kind": "brochure_cargo_context_schema_foundation",
    "implemented_on": "2026-07-25",
    "decision": "D-023",
    "relation": "data/master/configuration_cargo_volume_contexts.csv",
    "relation_rows": 0,
    "relation_columns": EXPECTED_COLUMNS,
    "dictionary_files": [
        "data/master/enums/cargo_measurement_bases.csv",
        "data/master/enums/cargo_seat_states.csv",
        "data/master/enums/cargo_compartment_types.csv",
        "data/master/enums/context_presence_states.csv",
    ],
    "dictionary_rows": 11,
    "reference_rules_added": 8,
    "status_rules_added": 4,
    "semantic_rules": [
        "one_context_per_configuration_attribute_value",
        "context_requires_boot_capacity_attribute",
    ],
    "sqlite_tables_added": 5,
    "configuration_values_imported": 0,
    "next_package": "Brochure Cargo Context Reporting Foundation",
}

REFERENCE_IMPORT_OLD = """try:
    from validators.enum_domains import validate_enum_domains
    from validators.value_ranges import validate_configuration_value_ranges
except ModuleNotFoundError:  # package import in unit tests
    from tools.validators.enum_domains import validate_enum_domains
    from tools.validators.value_ranges import validate_configuration_value_ranges
"""
REFERENCE_IMPORT_NEW = """try:
    from validators.cargo_contexts import validate_configuration_cargo_volume_contexts
    from validators.enum_domains import validate_enum_domains
    from validators.value_ranges import validate_configuration_value_ranges
except ModuleNotFoundError:  # package import in unit tests
    from tools.validators.cargo_contexts import validate_configuration_cargo_volume_contexts
    from tools.validators.enum_domains import validate_enum_domains
    from tools.validators.value_ranges import validate_configuration_value_ranges
"""

REFERENCE_ANCHOR = """    ReferenceRule(
        "data/master/attributes.csv",
        "category",
        "data/master/attribute_categories.csv",
        target_column="name",
    ),
"""
REFERENCE_BLOCK = """    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "configuration_attribute_value_code",
        "data/master/configuration_attribute_values.csv",
    ),
    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "measurement_basis_code",
        "data/master/enums/cargo_measurement_bases.csv",
    ),
    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "second_row_state_code",
        "data/master/enums/cargo_seat_states.csv",
        allow_empty=True,
    ),
    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "third_row_state_code",
        "data/master/enums/cargo_seat_states.csv",
        allow_empty=True,
    ),
    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "compartment_code",
        "data/master/enums/cargo_compartment_types.csv",
    ),
    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "spare_wheel_state_code",
        "data/master/enums/context_presence_states.csv",
        allow_empty=True,
    ),
    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "tyre_repair_kit_state_code",
        "data/master/enums/context_presence_states.csv",
        allow_empty=True,
    ),
    ReferenceRule(
        "data/master/configuration_cargo_volume_contexts.csv",
        "double_floor_state_code",
        "data/master/enums/context_presence_states.csv",
        allow_empty=True,
    ),
"""

REFERENCE_TAIL_OLD = """    _, range_errors = validate_configuration_value_ranges(root)
    errors.extend(range_errors)
    return errors
"""
REFERENCE_TAIL_NEW = """    _, range_errors = validate_configuration_value_ranges(root)
    errors.extend(range_errors)
    _, cargo_context_errors = validate_configuration_cargo_volume_contexts(root)
    errors.extend(cargo_context_errors)
    return errors
"""

STATUS_ANCHOR = """    StatusRule(
        "data/master/enums/equipment_availability_statuses.csv",
        ACTIVE_STATUSES,
    ),
"""
STATUS_BLOCK = """    StatusRule(
        "data/master/enums/cargo_measurement_bases.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/enums/cargo_seat_states.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/enums/cargo_compartment_types.csv",
        ACTIVE_STATUSES,
    ),
    StatusRule(
        "data/master/enums/context_presence_states.csv",
        ACTIVE_STATUSES,
    ),
"""

LEGACY_TOOL_OLD = """    if state.get("phase") != "Brochure Cargo Measurement Context Modeling":
        raise RuntimeError("project phase mismatch")
    if state.get("baseline", {}).get("tests") != 766:
        raise RuntimeError("test baseline mismatch")
    if state.get("baseline", {}).get("rows") != 8145:
        raise RuntimeError("master-row baseline mismatch")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package is not complete")
    if state.get("next_package", {}).get("name") != "Brochure Cargo Context Schema Foundation":
        raise RuntimeError("next package mismatch")
"""
LEGACY_TOOL_NEW = """    if not state.get("phase"):
        raise RuntimeError("project phase missing")
    if state.get("baseline", {}).get("tests", 0) < 766:
        raise RuntimeError("test baseline regressed")
    if state.get("baseline", {}).get("rows", 0) < 8145:
        raise RuntimeError("master-row baseline regressed")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package is not complete")
    if not state.get("next_package", {}).get("name"):
        raise RuntimeError("next package missing")
"""

LEGACY_TEST_OLD = """        self.assertEqual(state["phase"], "Brochure Cargo Measurement Context Modeling")
        self.assertEqual(state["baseline"]["tests"], 766)
        self.assertEqual(state["baseline"]["rows"], 8145)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Brochure Cargo Context Schema Foundation",
        )
"""
LEGACY_TEST_NEW = """        self.assertTrue(state["phase"])
        self.assertGreaterEqual(state["baseline"]["tests"], 766)
        self.assertGreaterEqual(state["baseline"]["rows"], 8145)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertTrue(state["next_package"]["name"])
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _patch(path: Path, old: str, new: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    if old not in text:
        raise RuntimeError(f"patch anchor missing in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _apply_code_contracts() -> None:
    _patch(
        REFERENCES,
        REFERENCE_IMPORT_OLD,
        REFERENCE_IMPORT_NEW,
        "validate_configuration_cargo_volume_contexts",
    )
    text = REFERENCES.read_text(encoding="utf-8")
    if '"data/master/configuration_cargo_volume_contexts.csv"' not in text:
        if REFERENCE_ANCHOR not in text:
            raise RuntimeError("reference rule anchor missing")
        REFERENCES.write_text(
            text.replace(REFERENCE_ANCHOR, REFERENCE_BLOCK + REFERENCE_ANCHOR, 1),
            encoding="utf-8",
        )
    _patch(
        REFERENCES,
        REFERENCE_TAIL_OLD,
        REFERENCE_TAIL_NEW,
        "cargo_context_errors",
    )

    status_text = STATUSES.read_text(encoding="utf-8")
    if '"data/master/enums/cargo_measurement_bases.csv"' not in status_text:
        if STATUS_ANCHOR not in status_text:
            raise RuntimeError("status rule anchor missing")
        STATUSES.write_text(
            status_text.replace(STATUS_ANCHOR, STATUS_ANCHOR + STATUS_BLOCK, 1),
            encoding="utf-8",
        )

    _patch(
        LEGACY_TOOL,
        LEGACY_TOOL_OLD,
        LEGACY_TOOL_NEW,
        "test baseline regressed",
    )
    _patch(
        LEGACY_TEST,
        LEGACY_TEST_OLD,
        LEGACY_TEST_NEW,
        "self.assertGreaterEqual(state[\"baseline\"][\"tests\"], 766)",
    )


def _apply_changelog() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    if CHANGELOG_ENTRY in text:
        return
    anchor = "### Added\n\n"
    if anchor not in text:
        raise RuntimeError("CHANGELOG Added section not found")
    CHANGELOG.write_text(
        text.replace(anchor, anchor + CHANGELOG_ENTRY + "\n", 1),
        encoding="utf-8",
    )


def _apply_state() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("baseline", {}).get("configuration_values") != 1831:
        raise RuntimeError("unexpected configuration-value baseline")
    state["updated_on"] = "2026-07-25"
    state["phase"] = "Brochure Cargo Context Schema Foundation"
    state["current_package"] = {
        "name": "Brochure Cargo Context Schema Foundation",
        "status": "complete",
        "goal": (
            "Implement the header-only configuration_cargo_volume_contexts relation, "
            "controlled context dictionaries, references, semantic validation, SQLite "
            "and data-dictionary coverage without importing brochure cargo values."
        ),
    }
    state["next_package"] = {
        "name": "Brochure Cargo Context Reporting Foundation",
        "status": "planned",
        "goal": (
            "Make comparison, shortlist and export reporting expose cargo-context fields "
            "and preserve every context-distinct boot_capacity observation before any "
            "official brochure cargo values are imported."
        ),
    }
    _write(STATE, json.dumps(state, ensure_ascii=False, indent=2))


def apply() -> None:
    _apply_code_contracts()
    _apply_changelog()
    _apply_state()
    _write(REPORT, json.dumps(REPORT_DATA, ensure_ascii=False, indent=2))
    _write(PACKAGE, PACKAGE_TEXT)
    _write(REVIEW, REVIEW_TEXT)


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def check() -> None:
    columns, rows = _read_csv(RELATION)
    if columns != EXPECTED_COLUMNS or rows:
        raise RuntimeError("cargo context relation is not the accepted header-only schema")
    for path, expected_codes in DICTIONARIES.items():
        dictionary_columns, dictionary_rows = _read_csv(path)
        if dictionary_columns != ["code", "name", "description", "status"]:
            raise RuntimeError(f"dictionary header mismatch: {path}")
        if {row["code"] for row in dictionary_rows} != expected_codes:
            raise RuntimeError(f"dictionary codes mismatch: {path}")
        if {row["status"] for row in dictionary_rows} != {"active"}:
            raise RuntimeError(f"dictionary statuses mismatch: {path}")

    references = REFERENCES.read_text(encoding="utf-8")
    if REFERENCE_IMPORT_NEW not in references:
        raise RuntimeError("cargo semantic validator import missing")
    if REFERENCE_BLOCK not in references:
        raise RuntimeError("cargo reference rules missing")
    if REFERENCE_TAIL_NEW not in references:
        raise RuntimeError("cargo semantic validation is not executed")

    statuses = STATUSES.read_text(encoding="utf-8")
    if STATUS_BLOCK not in statuses:
        raise RuntimeError("cargo dictionary status rules missing")
    if LEGACY_TOOL_NEW not in LEGACY_TOOL.read_text(encoding="utf-8"):
        raise RuntimeError("historical model tool still pins obsolete state")
    if LEGACY_TEST_NEW not in LEGACY_TEST.read_text(encoding="utf-8"):
        raise RuntimeError("historical model test still pins obsolete state")

    if CHANGELOG_ENTRY not in CHANGELOG.read_text(encoding="utf-8"):
        raise RuntimeError("changelog entry missing")
    if json.loads(REPORT.read_text(encoding="utf-8")) != REPORT_DATA:
        raise RuntimeError("schema foundation report differs")
    if PACKAGE.read_text(encoding="utf-8").rstrip() != PACKAGE_TEXT.rstrip():
        raise RuntimeError("package document differs")
    if REVIEW.read_text(encoding="utf-8").rstrip() != REVIEW_TEXT.rstrip():
        raise RuntimeError("review document differs")

    state = json.loads(STATE.read_text(encoding="utf-8"))
    baseline = state.get("baseline", {})
    if state.get("phase") != "Brochure Cargo Context Schema Foundation":
        raise RuntimeError("project phase mismatch")
    if baseline.get("tests") != 776:
        raise RuntimeError("test baseline mismatch")
    if baseline.get("csv_files") != 46:
        raise RuntimeError("CSV baseline mismatch")
    if baseline.get("rows") != 8156:
        raise RuntimeError("master-row baseline mismatch")
    if baseline.get("configuration_values") != 1831:
        raise RuntimeError("configuration values changed")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package is not complete")
    if state.get("next_package", {}).get("name") != "Brochure Cargo Context Reporting Foundation":
        raise RuntimeError("next package mismatch")

    print("PASS: brochure cargo context schema foundation contract")


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
    except (OSError, ValueError, RuntimeError, csv.Error) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
