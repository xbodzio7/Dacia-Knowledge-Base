#!/usr/bin/env python3
"""Complete and verify the Bigster official brochure cargo package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"
CHANGELOG = ROOT / "CHANGELOG.md"
REPORT = ROOT / "data" / "reporting" / "bigster_brochure_cargo_import.json"
PACKAGE = ROOT / "project" / "packages" / "bigster-brochure-cargo-import-20260726.md"
REVIEW = ROOT / "project" / "reviews" / "bigster-brochure-cargo-import-2026-07-26.md"

CHANGELOG_ENTRY = (
    "* Imported 68 context-aware `boot_capacity` observations from the official "
    "2025-12-10 Bigster brochure across 11 exact 4x2 configurations, preserving "
    "repair-kit, optional spare-wheel, seat-state and measurement-basis context."
)

REPORT_DATA = {
    "version": 1,
    "kind": "bigster_brochure_cargo_import",
    "implemented_on": "2026-07-26",
    "observation_date": "2025-12-10",
    "source_page": 20,
    "source_code": "src_pl_bigster_brochure_20251210",
    "model": "bigster",
    "configurations": 11,
    "configuration_values_imported": 68,
    "cargo_context_rows_imported": 68,
    "source_configuration_relationships": 11,
    "groups": {
        "mild_hybrid_g_140": {
            "configurations": 4,
            "values": [609, 1877, 660, 1960],
            "spare_wheel": "explicitly unavailable",
        },
        "mild_hybrid_140": {
            "configurations": 4,
            "repair_kit_values": [667, 1937, 702, 2002],
            "spare_wheel_values": [624, 1894, 681, 1981],
            "spare_wheel_scope": "Expression, Journey and Extreme only",
        },
        "hybrid_155": {
            "configurations": 3,
            "repair_kit_values": [546, 1851, 612, 1912],
            "spare_wheel_values": [488, 1791, 566, 1866],
        },
    },
    "deferred": {
        "hybrid_g_150_4x4_values": [444, 1712, 556, 1856],
        "hybrid_g_150_4x4_reason": (
            "The technical table says no repair kit / spare wheel, while the same "
            "brochure equipment table marks the repair kit as standard."
        ),
        "generic_dimensions_values": [667, 702, 1937, 2002],
        "generic_dimensions_reason": (
            "The dimensions page states no double floor and no spare wheel but does "
            "not identify a powertrain, so it is not projected by numerical matching."
        ),
    },
    "next_package": "Duster Brochure Cargo Value Import",
}

PACKAGE_TEXT = """# Bigster Brochure Cargo Value Import

Date: 2026-07-26

## Scope

Import 68 unambiguous luggage-capacity observations from page 20 of the official
Polish Bigster brochure dated 10 December 2025. The package covers eleven exact
4x2 configurations:

- four mild hybrid-G 140 manual configurations;
- four mild hybrid 140 manual configurations;
- three hybrid 155 automatic configurations.

Each value receives a one-to-one cargo-context row preserving VDA/ISO 3832 versus
ordinary litres, rear-bench state, compartment meaning, repair-kit state and
spare-wheel state.

## Equipment states

The brochure lists the tyre-repair kit as standard. Its footnote says that the
optional spare wheel replaces the kit. Therefore:

- repair-kit observations use `tyre_repair_kit_state_code = present` and
  `spare_wheel_state_code = absent`;
- spare-wheel observations use `spare_wheel_state_code = present` and
  `tyre_repair_kit_state_code = absent`;
- Essential receives no spare-wheel observations;
- mild hybrid-G 140 receives no spare-wheel observations because the brochure
  explicitly marks the spare wheel unavailable for that powertrain.

The page-20 table does not state double-floor condition, so every imported
`double_floor_state_code` remains empty and means **not stated**.

## Deferred hybrid-G 150 4x4

The four values `444`, `1712`, `556` and `1856` are not imported. Their technical
column says there is no repair kit / spare wheel, while the equipment table in the
same brochure marks the repair kit as standard for every trim. Importing either a
present or absent equipment state would resolve a source contradiction by guess.

## Deferred dimensions-page values

Page 23 gives `667/702` and `1937/2002` with no double floor and no spare wheel.
It does not identify a powertrain. Although the numbers match the mild hybrid 140
technical column, numerical equality is not sufficient evidence for projecting the
additional double-floor qualifier into exact configurations.

## Follow-up

The next package will evaluate the official Duster mini-brochure cargo table with
exact 4x2/4x4 and repair-kit/spare-wheel boundaries. Manual brochure values will
not be inherited by current automatic Eco-G 120 stock configurations.
"""

REVIEW_TEXT = """# Bigster Brochure Cargo Value Import Review

Date: 2026-07-26

## Source identity

The archived 24-page official Polish Bigster brochure is verified against SHA-256
`76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74`.

## Technical table

Page 20 distinguishes four powertrains and provides VDA/ISO 3832 and ordinary-litre
values under the luggage shelf and with the rear bench folded. The mild hybrid 140
and hybrid 155 columns separately state repair-kit and spare-wheel values. The
mild hybrid-G 140 footnote states that a spare wheel is unavailable.

## Configuration projection

Only exact active configurations whose canonical powertrain labels match the
source column are included. The import covers eleven 4x2 configurations and creates
`brochure_technical_data_for` relationships for those targets only.

The three hybrid-G 150 4x4 configurations remain outside the import because the
brochure contradicts itself on tyre-repair-kit presence. No source relationship is
created for an observation that remains deferred.

## Context rules

- VDA/ISO 3832 and ordinary litres remain separate rows;
- rear bench upright uses `main_luggage_compartment`;
- rear bench folded uses `source_stated_total`;
- repair kit and spare wheel are mutually exclusive only where the brochure
  explicitly says the spare option replaces the kit;
- double-floor and third-row states remain empty because page 20 does not qualify
  them;
- no value from the generic dimensions page is assigned to a powertrain by matching
  its number.

## Reproducibility

The versioned JSON specification generates exact value IDs 1987-2054 and context
IDs 156-223. The importer is idempotent, verifies the archived PDF hash, exact
configuration labels and all 68 value/context pairs, and preserves unrelated master
data.
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def apply() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    baseline = state.get("baseline", {})
    if baseline.get("configuration_values") not in {1986, 2054}:
        raise RuntimeError("unexpected pre- or post-import configuration-value baseline")
    if baseline.get("rows") not in {8497, 8644}:
        raise RuntimeError("unexpected pre- or post-import master-row baseline")

    state["updated_on"] = "2026-07-26"
    state["phase"] = "Bigster Brochure Cargo Value Import"
    state["baseline"].update(
        {
            "tests": 799,
            "csv_files": 46,
            "rows": 8644,
            "configuration_values": 2054,
            "configuration_import_specs": 114,
            "configuration_value_ranges": 176,
            "configuration_range_import_specs": 20,
            "availability_records": 4754,
            "attributes": 381,
            "attribute_categories": 30,
        }
    )
    state["current_package"] = {
        "name": "Bigster Brochure Cargo Value Import",
        "status": "complete",
        "goal": (
            "Import 68 source-backed Bigster boot_capacity observations across exact "
            "4x2 powertrains while preserving measurement, rear-bench, repair-kit and "
            "spare-wheel context and deferring contradictory 4x4 evidence."
        ),
    }
    state["next_package"] = {
        "name": "Duster Brochure Cargo Value Import",
        "status": "planned",
        "goal": (
            "Import source-backed Duster cargo observations only where drive type, "
            "powertrain, seat state and repair-kit or spare-wheel context map exactly "
            "to modeled configurations."
        ),
    }
    _write(STATE, json.dumps(state, ensure_ascii=False, indent=2))

    changelog = CHANGELOG.read_text(encoding="utf-8")
    if CHANGELOG_ENTRY not in changelog:
        anchor = "### Added\n\n"
        if anchor not in changelog:
            raise RuntimeError("CHANGELOG Added section not found")
        CHANGELOG.write_text(
            changelog.replace(anchor, anchor + CHANGELOG_ENTRY + "\n", 1),
            encoding="utf-8",
        )

    _write(REPORT, json.dumps(REPORT_DATA, ensure_ascii=False, indent=2))
    _write(PACKAGE, PACKAGE_TEXT)
    _write(REVIEW, REVIEW_TEXT)


def check() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("phase") != "Bigster Brochure Cargo Value Import":
        raise RuntimeError("project phase mismatch")
    baseline = state.get("baseline", {})
    if baseline.get("tests") != 799:
        raise RuntimeError("test baseline mismatch")
    if baseline.get("rows") != 8644:
        raise RuntimeError("master-row baseline mismatch")
    if baseline.get("configuration_values") != 2054:
        raise RuntimeError("configuration-value baseline mismatch")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package is not complete")
    if state.get("next_package", {}).get("name") != "Duster Brochure Cargo Value Import":
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
    print("PASS: Bigster brochure cargo package completion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
