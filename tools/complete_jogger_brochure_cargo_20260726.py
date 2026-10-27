#!/usr/bin/env python3
"""Complete and verify the Jogger official brochure cargo package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"
CHANGELOG = ROOT / "CHANGELOG.md"
REPORT = ROOT / "data" / "reporting" / "jogger_brochure_cargo_import.json"
PACKAGE = ROOT / "project" / "packages" / "jogger-brochure-cargo-import-20260726.md"
REVIEW = ROOT / "project" / "reviews" / "jogger-brochure-cargo-import-2026-07-26.md"

CHANGELOG_ENTRY = (
    "* Imported 110 context-aware `boot_capacity` observations from the official "
    "2025-12-17 Jogger brochure across 22 five- and seven-seat configurations, "
    "with 110 exact cargo-context rows and 22 source relationships."
)

REPORT_DATA = {
    "version": 1,
    "kind": "jogger_brochure_cargo_import",
    "implemented_on": "2026-07-26",
    "observation_date": "2025-12-17",
    "source_page": 22,
    "source_code": "src_pl_jogger_brochure_20251217",
    "model": "jogger",
    "configurations": 22,
    "five_seat_configurations": 11,
    "seven_seat_configurations": 11,
    "configuration_values_imported": 110,
    "cargo_context_rows_imported": 110,
    "source_configuration_relationships": 22,
    "five_seat_values_per_configuration": {
        "minimum_vda_iso3832": 708,
        "minimum_ordinary_litre": 829,
        "maximum_vda_iso3832": 1819,
        "maximum_ordinary_litre": 2094,
    },
    "seven_seat_values_per_configuration": {
        "minimum_vda_iso3832": 160,
        "minimum_ordinary_litre": 212,
        "second_row_upright_third_row_folded_vda_iso3832": 565,
        "second_row_upright_third_row_folded_ordinary_litre": 699,
        "second_row_upright_third_row_removed_vda_iso3832": 696,
        "second_row_upright_third_row_removed_ordinary_litre": 820,
    },
    "deferred_values": {
        "seven_seat_maximum_vda_iso3832": 1807,
        "seven_seat_maximum_ordinary_litre": 2085,
        "reason": (
            "The page-22 table does not state whether the third row is folded or "
            "removed for the seven-seat maximum."
        ),
    },
    "equipment_context_policy": "not_stated",
    "next_package": "Bigster Brochure Cargo Value Import",
}

PACKAGE_TEXT = """# Jogger Brochure Cargo Value Import

Date: 2026-07-26

## Scope

Import the unambiguous cargo table observations on page 22 of the official Polish
Jogger brochure dated 17 December 2025 into all 22 active Jogger configurations.

The package keeps five- and seven-seat layouts separate. It creates 110 canonical
`boot_capacity` observations, 110 one-to-one cargo-context rows and 22
source-to-configuration relationships.

## Five-seat observations per configuration

- 708 dm3 according to ISO 3832, second row upright, main luggage compartment;
- 829 ordinary litres, second row upright, main luggage compartment;
- 1819 dm3 according to ISO 3832, second row folded, source-stated total;
- 2094 ordinary litres, second row folded, source-stated total.

The brochure separately confirms that 1819 dm3 is the five-seat variant with the
rear bench folded.

## Seven-seat observations per configuration

- 160 dm3 according to ISO 3832 and 212 ordinary litres with both rear rows upright;
- 565 dm3 according to ISO 3832 and 699 ordinary litres with the second row upright
  and the third row folded;
- 696 dm3 according to ISO 3832 and 820 ordinary litres with the second row upright
  and the third row removed.

## Deferred maximum

The seven-seat maximum pair `1807 dm3 / 2085 L` is not imported. The table does not
state whether the third row is folded or removed, and those states are materially
different in the canonical context model. Importing either interpretation would be
an unsupported inference.

## Evidence boundary

The source distinguishes passenger layout and rear-row state but does not qualify
the values by spare wheel, tyre-repair kit or double floor. Those optional context
fields remain empty and mean **not stated**, never `absent`.

Every mapped configuration is active, belongs to Jogger and has an exact
configuration-level `number_of_seats` observation matching its five- or seven-seat
layout.

## Follow-up

The next package will evaluate the official Bigster brochure cargo table, including
repair-kit, spare-wheel and double-floor qualifiers already supported by the cargo
context model.
"""

REVIEW_TEXT = """# Jogger Brochure Cargo Value Import Review

Date: 2026-07-26

## Source verification

The archived 23-page official Polish Jogger brochure is checked against SHA-256
`eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6`.

Page 22 contains separate columns for the five- and seven-seat variants and gives
VDA/ISO 3832 values alongside ordinary litres.

## Mapping

Eleven active five-seat and eleven active seven-seat configurations are linked with
`brochure_technical_data_for`. The importer checks active status, Jogger identity,
powertrain, transmission and the exact `number_of_seats` value for every
configuration.

## Context mapping

- five-seat minimum: second row `upright`, third row not applicable/not stated;
- five-seat maximum: second row `folded`, `source_stated_total`;
- seven-seat minimum: second and third rows `upright`;
- seven-seat intermediate: second row `upright`, third row `folded`;
- seven-seat removed-row state: second row `upright`, third row `removed`;
- VDA/ISO 3832 and ordinary litres remain separate observations.

## Non-inference

- `1807/2085` is excluded because its third-row state is not stated;
- no five-seat value is reused for a seven-seat configuration;
- no spare-wheel, repair-kit or double-floor state is inferred;
- no configuration outside the explicit 22-row scope receives a value;
- no source value is converted between VDA/ISO 3832 and ordinary litres.

## Reproducibility

The versioned JSON specification generates exact value IDs 1877-1986 and context
IDs 46-155. The importer is idempotent, validates the archived PDF hash, reproduces
all 110 values and contexts, and preserves unrelated master data.
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _apply_state_and_docs() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    baseline = state.get("baseline", {})
    if baseline.get("configuration_values") not in {1876, 1986}:
        raise RuntimeError("unexpected pre- or post-import configuration-value baseline")
    if baseline.get("rows") not in {8255, 8497}:
        raise RuntimeError("unexpected pre- or post-import master-row baseline")

    state["updated_on"] = "2026-07-26"
    state["phase"] = "Jogger Brochure Cargo Value Import"
    state["baseline"].update(
        {
            "tests": 795,
            "csv_files": 46,
            "rows": 8497,
            "configuration_values": 1986,
            "configuration_import_specs": 114,
            "configuration_value_ranges": 176,
            "configuration_range_import_specs": 20,
            "availability_records": 4754,
            "attributes": 381,
            "attribute_categories": 30,
        }
    )
    state["current_package"] = {
        "name": "Jogger Brochure Cargo Value Import",
        "status": "complete",
        "goal": (
            "Import 110 source-backed Jogger boot_capacity observations across exact "
            "five- and seven-seat layouts while preserving second-row, third-row and "
            "measurement-basis context and deferring the ambiguous seven-seat maximum."
        ),
    }
    state["next_package"] = {
        "name": "Bigster Brochure Cargo Value Import",
        "status": "planned",
        "goal": (
            "Import source-backed Bigster cargo observations with exact measurement "
            "basis, rear-bench state, repair-kit or spare-wheel and double-floor context."
        ),
    }
    _write(STATE, json.dumps(state, ensure_ascii=False, indent=2))

    text = CHANGELOG.read_text(encoding="utf-8")
    if CHANGELOG_ENTRY not in text:
        anchor = "### Added\n\n"
        if anchor not in text:
            raise RuntimeError("CHANGELOG Added section not found")
        CHANGELOG.write_text(
            text.replace(anchor, anchor + CHANGELOG_ENTRY + "\n", 1),
            encoding="utf-8",
        )

    _write(REPORT, json.dumps(REPORT_DATA, ensure_ascii=False, indent=2))
    _write(PACKAGE, PACKAGE_TEXT)
    _write(REVIEW, REVIEW_TEXT)


def apply() -> None:
    _apply_state_and_docs()


def check() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("phase") != "Jogger Brochure Cargo Value Import":
        raise RuntimeError("project phase mismatch")
    if state.get("baseline", {}).get("tests") != 795:
        raise RuntimeError("test baseline mismatch")
    if state.get("baseline", {}).get("rows") != 8497:
        raise RuntimeError("master-row baseline mismatch")
    if state.get("baseline", {}).get("configuration_values") != 1986:
        raise RuntimeError("configuration-value baseline mismatch")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package is not complete")
    if state.get("next_package", {}).get("name") != "Bigster Brochure Cargo Value Import":
        raise RuntimeError("next package mismatch")

    expected_files = {
        REPORT: json.dumps(REPORT_DATA, ensure_ascii=False, indent=2) + "\n",
        PACKAGE: PACKAGE_TEXT.rstrip() + "\n",
        REVIEW: REVIEW_TEXT.rstrip() + "\n",
    }
    for path, expected in expected_files.items():
        if path.read_text(encoding="utf-8") != expected:
            raise RuntimeError(f"generated package artifact differs: {path}")

    if CHANGELOG_ENTRY not in CHANGELOG.read_text(encoding="utf-8"):
        raise RuntimeError("CHANGELOG entry missing")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        apply() if args.apply else check()
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print("PASS: Jogger brochure cargo package completion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
