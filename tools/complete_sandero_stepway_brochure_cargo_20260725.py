#!/usr/bin/env python3
"""Complete and verify the Sandero/Stepway official brochure cargo package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "project" / "state.json"
CHANGELOG = ROOT / "CHANGELOG.md"
REPORT = ROOT / "data" / "reporting" / "sandero_stepway_brochure_cargo_import.json"
PACKAGE = ROOT / "project" / "packages" / "sandero-stepway-brochure-cargo-import-20260725.md"
REVIEW = ROOT / "project" / "reviews" / "sandero-stepway-brochure-cargo-import-2026-07-25.md"
SCHEMA_TOOL = ROOT / "tools" / "establish_brochure_cargo_context_schema_20260725.py"
SCHEMA_TEST = ROOT / "tests" / "test_brochure_cargo_context_schema_foundation.py"
REPORTING_TOOL = ROOT / "tools" / "establish_brochure_cargo_context_reporting_20260725.py"
REPORTING_TEST = ROOT / "tests" / "test_brochure_cargo_context_reporting_foundation.py"
IMPORTER = ROOT / "tools" / "import_sandero_stepway_brochure_cargo_20260725.py"

CHANGELOG_ENTRY = (
    "* Imported 45 context-aware `boot_capacity` observations from the official "
    "2026-02-02 Sandero and Sandero Stepway brochures across nine Eco-G 120 "
    "configurations, with 45 exact cargo-context rows and nine source relationships."
)

REPORT_DATA = {
    "version": 1,
    "kind": "sandero_stepway_brochure_cargo_import",
    "implemented_on": "2026-07-25",
    "observation_date": "2026-02-02",
    "source_page": 20,
    "source_codes": [
        "src_pl_sandero_brochure_20260202",
        "src_pl_sandero_stepway_brochure_20260202",
    ],
    "models": ["sandero_iii", "sandero_stepway_iii"],
    "configurations": 9,
    "configuration_values_imported": 45,
    "cargo_context_rows_imported": 45,
    "source_configuration_relationships": 9,
    "values_per_configuration": {
        "minimum_vda_iso3832": 328,
        "minimum_ordinary_litre": 410,
        "maximum_vda_iso3832": 1108,
        "maximum_ordinary_litre": 1455,
        "underfloor_vda_iso3832": 78,
    },
    "legacy_values_migrated": False,
    "legacy_20260626_boot_capacity_rows_preserved": 7,
    "equipment_context_policy": "not_stated",
    "conflict_policy": (
        "The brochure's 328 dm3 historical observation coexists with later "
        "configuration-specific 372 dm3 cargo_volume_vda observations; neither is "
        "overwritten or converted."
    ),
    "next_package": "Jogger Brochure Cargo Value Import",
}

PACKAGE_TEXT = """# Sandero and Stepway Brochure Cargo Import

Date: 2026-07-25

## Scope

Import the model-wide cargo table on page 20 of the official Polish Sandero and
Sandero Stepway brochures dated 2 February 2026 into every active Eco-G 120
configuration represented by those brochures.

The package creates 45 canonical `boot_capacity` observations, 45 one-to-one cargo
context rows and nine source-to-configuration relationships. It does not import TCe
100 configurations because they are not present in master data.

## Imported observations per configuration

- 328 dm3 according to ISO 3832, second row upright, main luggage compartment;
- 410 ordinary litres, second row upright, main luggage compartment;
- 1108 dm3 according to ISO 3832, second row folded, source-stated total;
- 1455 ordinary litres, second row folded, source-stated total;
- 78 dm3 according to ISO 3832, underfloor compartment, seat state not stated.

The source does not qualify these values by spare wheel, repair kit or double floor.
Those three fields remain empty and mean **not stated**, never `absent`.

## Historical conflict policy

Seven configuration documents dated 26 June 2026 already record 410 L and a separate
legacy `cargo_volume_vda` value of 372 dm3. The brochure observation of 328 dm3 is older
and uses the new canonical context model. Both histories are retained. No legacy row is
rewritten, deleted or assigned a context retroactively.

## Evidence boundary

The page presents one model-wide table and no trim-dependent or powertrain-dependent
cargo columns. The import is therefore projected only to active Sandero and Stepway
Eco-G 120 configurations belonging to the corresponding model. Five-seat layout is
verified where configuration-level evidence exists and otherwise follows the unambiguous
five-seat body represented by the brochure.

## Follow-up

The next package imports Jogger cargo values with explicit five- and seven-seat layouts
and second-/third-row state combinations.
"""

REVIEW_TEXT = """# Sandero and Stepway Brochure Cargo Import Review

Date: 2026-07-25

## Source verification

Both archived PDFs are checked against their registered SHA-256 identities:

- Sandero: `adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97`;
- Sandero Stepway: `800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48`.

The reviewed page-20 tables contain the same five cargo facts: `328/410`, `1108/1455`
and underfloor capacity `78`.

## Mapping

The source is model-wide. Four active Sandero and five active Stepway Eco-G 120
configurations are linked using `brochure_technical_data_for`. The importer checks model
prefix, active status, Eco-G 120 powertrain and manual/automatic transmission.

## Context mapping

VDA/ISO 3832 and ordinary-litre values are separate observations. Minimum values use
`upright` plus `main_luggage_compartment`; maximum values use `folded` plus
`source_stated_total`; underfloor capacity uses `underfloor_compartment` with seat state
left unstated. Spare-wheel, tyre-repair-kit and double-floor states remain blank because
the brochure does not state them.

## Non-inference

- no tyre-repair-kit state is copied from configuration PDFs;
- no spare-wheel or double-floor state is inferred;
- no legacy value is migrated to the new relation;
- no TCe 100 configuration is invented;
- the later 372 dm3 legacy observation is not replaced by the older 328 dm3 brochure row.

## Reproducibility

One versioned JSON specification generates exact IDs 1832-1876 and context IDs 1-45.
The importer is idempotent, validates every semantic row and preserves all unrelated
master data.
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _patch(path: Path, old: str, new: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    if old not in text:
        raise RuntimeError(f"patch anchor missing in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _patch_historical_contracts() -> None:
    _patch(
        SCHEMA_TOOL,
        '''    if columns != EXPECTED_COLUMNS or rows:\n        raise RuntimeError("cargo context relation is not the accepted header-only schema")\n''',
        '''    if columns != EXPECTED_COLUMNS:\n        raise RuntimeError("cargo context relation header differs from the accepted schema")\n''',
        "relation header differs from the accepted schema",
    )
    _patch(
        SCHEMA_TEST,
        '''    def test_relation_is_header_only_and_matches_d023(self) -> None:\n        columns, rows = self.read_rows(RELATION)\n        self.assertEqual(columns, EXPECTED_COLUMNS)\n        self.assertEqual(rows, [])\n''',
        '''    def test_relation_matches_d023_and_remains_one_to_one(self) -> None:\n        columns, rows = self.read_rows(RELATION)\n        self.assertEqual(columns, EXPECTED_COLUMNS)\n        value_codes = [\n            row["configuration_attribute_value_code"] for row in rows\n        ]\n        self.assertEqual(len(value_codes), len(set(value_codes)))\n''',
        "test_relation_matches_d023_and_remains_one_to_one",
    )
    _patch(
        REPORTING_TOOL,
        '''    if state.get("phase") != "Brochure Cargo Context Reporting Foundation":\n        raise RuntimeError("project phase mismatch")\n    if state.get("baseline", {}).get("configuration_values") != 1831:\n        raise RuntimeError("configuration values changed")\n    if state.get("current_package", {}).get("status") != "complete":\n        raise RuntimeError("current package is not complete")\n    if state.get("next_package", {}).get("name") != "Official Brochure Cargo Value Import":\n        raise RuntimeError("next package mismatch")\n\n    relation = ROOT / "data" / "master" / "configuration_cargo_volume_contexts.csv"\n    lines = relation.read_text(encoding="utf-8-sig").splitlines()\n    if len(lines) != 1:\n        raise RuntimeError("production cargo-context relation is no longer header-only")\n''',
        '''    if not state.get("phase"):\n        raise RuntimeError("project phase missing")\n    if state.get("baseline", {}).get("configuration_values", 0) < 1831:\n        raise RuntimeError("configuration-value baseline regressed")\n    if state.get("current_package", {}).get("status") != "complete":\n        raise RuntimeError("current package is not complete")\n    if not state.get("next_package", {}).get("name"):\n        raise RuntimeError("next package missing")\n\n    relation = ROOT / "data" / "master" / "configuration_cargo_volume_contexts.csv"\n    lines = relation.read_text(encoding="utf-8-sig").splitlines()\n    if not lines:\n        raise RuntimeError("production cargo-context relation has no header")\n''',
        "configuration-value baseline regressed",
    )
    _patch(
        REPORTING_TEST,
        '''        self.assertEqual(\n            context_filter.difference_contexts(report),\n            (\n                "",\n                "fuel_type_code=",\n                "fuel_type_code=lpg",\n                "fuel_type_code=petrol",\n                "market=PL;currency_code=PLN",\n            ),\n        )\n        self.assertEqual(len(comparison.difference_csv_rows(report)), 305)\n''',
        '''        contexts = set(context_filter.difference_contexts(report))\n        self.assertTrue(\n            {\n                "",\n                "fuel_type_code=",\n                "fuel_type_code=lpg",\n                "fuel_type_code=petrol",\n                "market=PL;currency_code=PLN",\n            } <= contexts\n        )\n        self.assertGreaterEqual(len(comparison.difference_csv_rows(report)), 305)\n''',
        "self.assertGreaterEqual(len(comparison.difference_csv_rows(report)), 305)",
    )
    _patch(
        IMPORTER,
        '''        _ensure(\n            seat_values.get(configuration_code) == "5",\n            f"five-seat evidence missing: {configuration_code}",\n        )\n''',
        '''        seat_value = seat_values.get(configuration_code)\n        _ensure(\n            seat_value in {None, "5"},\n            f"configuration is not five-seat: {configuration_code}",\n        )\n''',
        "seat_value in {None, \"5\"}",
    )


def _apply_state_and_docs() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("baseline", {}).get("configuration_values") not in {1831, 1876}:
        raise RuntimeError("unexpected pre- or post-import configuration-value baseline")
    state["updated_on"] = "2026-07-25"
    state["phase"] = "Sandero and Stepway Brochure Cargo Import"
    state["current_package"] = {
        "name": "Sandero and Stepway Brochure Cargo Import",
        "status": "complete",
        "goal": (
            "Import 45 source-backed canonical boot_capacity observations from the "
            "official Sandero and Stepway brochures with exact measurement, seat and "
            "compartment context while preserving legacy cargo history."
        ),
    }
    state["next_package"] = {
        "name": "Jogger Brochure Cargo Value Import",
        "status": "planned",
        "goal": (
            "Import official Jogger five- and seven-seat cargo observations with exact "
            "second-row, third-row, removal and measurement-basis context."
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
    _patch_historical_contracts()
    _apply_state_and_docs()


def check() -> None:
    markers = {
        SCHEMA_TOOL: ["relation header differs from the accepted schema"],
        SCHEMA_TEST: ["test_relation_matches_d023_and_remains_one_to_one"],
        REPORTING_TOOL: ["configuration-value baseline regressed"],
        REPORTING_TEST: [
            "self.assertGreaterEqual(len(comparison.difference_csv_rows(report)), 305)"
        ],
        IMPORTER: ['seat_value in {None, "5"}'],
    }
    for path, expected in markers.items():
        text = path.read_text(encoding="utf-8")
        missing = [item for item in expected if item not in text]
        if missing:
            raise RuntimeError(f"missing completion marker in {path}: {missing}")
    if json.loads(REPORT.read_text(encoding="utf-8")) != REPORT_DATA:
        raise RuntimeError("import report differs")
    if PACKAGE.read_text(encoding="utf-8").rstrip() != PACKAGE_TEXT.rstrip():
        raise RuntimeError("package document differs")
    if REVIEW.read_text(encoding="utf-8").rstrip() != REVIEW_TEXT.rstrip():
        raise RuntimeError("review document differs")
    if CHANGELOG_ENTRY not in CHANGELOG.read_text(encoding="utf-8"):
        raise RuntimeError("changelog entry missing")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("phase") != "Sandero and Stepway Brochure Cargo Import":
        raise RuntimeError("phase mismatch")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package incomplete")
    if state.get("next_package", {}).get("name") != "Jogger Brochure Cargo Value Import":
        raise RuntimeError("next package mismatch")
    print("PASS: Sandero and Stepway brochure cargo package completion")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.apply:
            apply()
        check()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
