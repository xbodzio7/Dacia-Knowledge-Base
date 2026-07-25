#!/usr/bin/env python3
"""Materialize and verify context-aware cargo reporting foundations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools" / "_configuration_comparison_base.py"
CONTEXT_FILTER = ROOT / "tools" / "configuration_comparison_context.py"
ITEM_CATALOG = ROOT / "tools" / "configuration_comparison_item_catalog.py"
COMPARISON_HTML = ROOT / "tools" / "reporting" / "configuration_comparison_html.py"
WORKBOOK_ROWS = ROOT / "tools" / "reporting" / "configuration_comparison_workbook_rows.py"
SHORTLIST = ROOT / "tools" / "reporting" / "configuration_shortlist.py"
SHORTLIST_HTML = ROOT / "tools" / "reporting" / "configuration_shortlist_html.py"
SELECTION_JS = ROOT / "tools" / "reporting" / "configuration_shortlist_selection.js"
SCHEMA_TOOL = ROOT / "tools" / "establish_brochure_cargo_context_schema_20260725.py"
SCHEMA_TEST = ROOT / "tests" / "test_brochure_cargo_context_schema_foundation.py"
STATE = ROOT / "project" / "state.json"
CHANGELOG = ROOT / "CHANGELOG.md"
REPORT = ROOT / "data" / "reporting" / "brochure_cargo_context_reporting_foundation.json"
PACKAGE = ROOT / "project" / "packages" / "brochure-cargo-context-reporting-foundation-20260725.md"
REVIEW = ROOT / "project" / "reviews" / "brochure-cargo-context-reporting-foundation-2026-07-25.md"

CHANGELOG_ENTRY = (
    "* Made comparison, shortlist, selection, flat CSV, HTML and workbook reporting "
    "preserve every context-distinct `boot_capacity` observation by measurement basis, "
    "seat state, compartment and explicit cargo-equipment qualifiers."
)

REPORT_DATA = {
    "version": 1,
    "kind": "brochure_cargo_context_reporting_foundation",
    "implemented_on": "2026-07-25",
    "decision": "D-023",
    "canonical_attribute_code": "boot_capacity",
    "context_relation": "data/master/configuration_cargo_volume_contexts.csv",
    "context_dimensions": [
        "measurement_basis_code",
        "second_row_state_code",
        "third_row_state_code",
        "compartment_code",
        "spare_wheel_state_code",
        "tyre_repair_kit_state_code",
        "double_floor_state_code",
    ],
    "reporting_surfaces": [
        "configuration_comparison_json",
        "configuration_comparison_markdown",
        "configuration_comparison_csv",
        "configuration_comparison_html",
        "configuration_comparison_item_catalog",
        "configuration_comparison_context_filter",
        "configuration_comparison_workbook",
        "configuration_shortlist_json",
        "configuration_shortlist_markdown",
        "configuration_shortlist_csv",
        "configuration_shortlist_html",
        "interactive_selection_json",
    ],
    "semantic_rules": [
        "context_signature_is_part_of_scalar_observation_identity",
        "context_distinct_boot_capacity_values_are_never_collapsed",
        "missing_matching_context_is_not_comparable",
        "blank_optional_dimension_remains_not_stated_not_absent",
        "legacy_contextless_outputs_remain_compatible",
    ],
    "configuration_values_imported": 0,
    "cargo_context_rows_imported": 0,
    "next_package": "Official Brochure Cargo Value Import",
}

PACKAGE_TEXT = r"""# Brochure Cargo Context Reporting Foundation

Date: 2026-07-25

## Purpose

Make every reporting and export surface preserve the measurement context accepted in
D-023 before any official brochure cargo value is imported.

## Observation identity

Scalar technical observations continue to use configuration, attribute and fuel context.
For `boot_capacity`, the semantic cargo-context signature is an additional identity
component. It contains measurement basis, second- and third-row state, compartment and
independent spare-wheel, repair-kit and double-floor states. Empty optional dimensions
remain explicit not-stated values and are not converted to `absent`.

## Reporting surfaces

- pairwise comparison JSON, Markdown, difference CSV and offline HTML;
- exact difference-context filtering and item catalog;
- deterministic comparison workbook and bundles;
- shortlist JSON, Markdown and flat CSV;
- interactive shortlist technical comparison and selection JSON export.

A missing matching context on either side is reported as missing/not comparable. It is
never matched to another cargo observation solely because the attribute and fuel are the
same.

## Compatibility

The production cargo-context relation remains header-only. Therefore existing legacy and
contextless comparison results, context-filter counts and current data products remain
unchanged. The new behavior is exercised with synthetic context-distinct observations.

## Data impact

No configuration value, range, availability, price, source mapping or brochure cargo
context row is added or changed by this package.

## Follow-up

The reporting path is ready for a source-backed official brochure cargo-value import.
"""

REVIEW_TEXT = r"""# Brochure Cargo Context Reporting Foundation Review

Date: 2026-07-25

## Scope

This package changes reporting semantics only. It does not import values from the five
registered Dacia brochures and does not migrate legacy cargo attributes.

## Collapse prevention

The former latest-observation key `(configuration, attribute, fuel)` was insufficient for
canonical `boot_capacity`: two source-backed values with different seat or compartment
conditions could collide. The reporting key now adds the exact semantic cargo-context
signature. Scalar and range observation behavior outside this attribute remains unchanged.

## Missing-context behavior

For each pair, reporting uses the union of observed cargo signatures. A missing signature
on one side becomes a missing state and the comparison is `not_comparable`. If the whole
attribute is absent, the existing evidence state is retained and annotated with the exact
counterpart context. This prevents an upright main-compartment value from being compared
with a folded maximum value.

## Exposed context

Machine-readable outputs include the exact cargo-context object. Flat surfaces include a
deterministic context string containing all seven dimensions, including blank optional
values. The workbook additionally stores deterministic JSON for each side. Browser labels
show the context-distinct rows separately, and selection exports include the complete
cargo observations.

## Compatibility

When no cargo context exists, the old key, filter context and output counts are preserved.
The production relation remains empty, and a regression test pins the existing 305
difference rows and context counts.

## Verification

Synthetic fixtures prove equal and different context-matched values, missing counterpart
contexts, exact filters, catalog contexts, shortlist exports, browser facets and selection
JSON. Full repository quality and project-state checks remain required before merge.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _patch(path: Path, old: str, new: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    if old not in text:
        raise RuntimeError(f"patch anchor missing in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _replace_between(
    path: Path,
    start: str,
    end: str,
    replacement: str,
    marker: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    left = text.find(start)
    if left < 0:
        raise RuntimeError(f"start anchor missing in {path}: {start!r}")
    right = text.find(end, left)
    if right < 0:
        raise RuntimeError(f"end anchor missing in {path}: {end!r}")
    path.write_text(text[:left] + replacement + text[right:], encoding="utf-8")


def _patch_comparison_base() -> None:
    _patch(
        BASE,
        "from configuration_value_range_reporting import (\n    combine_latest_observations,\n    range_relation,\n    read_optional_ranges,\n)\n",
        "from configuration_value_range_reporting import (\n    combine_latest_observations,\n    range_relation,\n    read_optional_ranges,\n)\nfrom reporting.cargo_context import (\n    CargoContextError,\n    annotate_scalar_values,\n    read_context_rows,\n    technical_context,\n)\n",
        "from reporting.cargo_context import (",
    )
    _replace_between(
        BASE,
        "def recorded_technical_state(\n",
        "def recorded_range_state(\n",
        '''def recorded_technical_state(\n    row: Mapping[str, Any],\n    attribute: Mapping[str, str],\n) -> dict[str, Any]:\n    value = str(row.get("value", ""))\n    data_type = str(attribute.get("data_type", ""))\n    result: dict[str, Any] = {\n        "state": "recorded",\n        "value": value,\n        "normalized_value": normalize_value(value, data_type),\n        "data_type": data_type,\n        "unit": str(attribute.get("unit", "")),\n        "observation_date": str(row.get("observation_date", "")),\n        "source_code": str(row.get("source_code", "")),\n    }\n    context = row.get("_cargo_context")\n    if isinstance(context, Mapping):\n        result["cargo_context"] = dict(context)\n        result["cargo_context_signature"] = str(\n            row.get("_cargo_context_signature", "")\n        )\n    return result\n\n\n''',
        'result["cargo_context_signature"]',
    )
    _patch(
        BASE,
        '''    scoped_values = [\n        row\n        for row in values\n        if row.get("configuration_code") in configuration_set\n    ]\n    scoped_ranges = [\n        row\n        for row in ranges\n        if row.get("configuration_code") in configuration_set\n    ]\n''',
        '''    scoped_values = [\n        row\n        for row in values\n        if row.get("configuration_code") in configuration_set\n    ]\n    try:\n        scoped_values = annotate_scalar_values(\n            scoped_values,\n            read_context_rows(master, read_csv),\n        )\n    except CargoContextError as exc:\n        raise ComparisonError(str(exc)) from exc\n    scoped_ranges = [\n        {**row, "_cargo_context_signature": "", "_cargo_context": None}\n        for row in ranges\n        if row.get("configuration_code") in configuration_set\n    ]\n''',
        "scoped_values = annotate_scalar_values(",
    )
    _patch(
        BASE,
        '''            "configuration_code",\n            "attribute_code",\n            "fuel_type_code",\n        ),\n        "observation_date",\n        as_of,\n        "configuration values",\n''',
        '''            "configuration_code",\n            "attribute_code",\n            "fuel_type_code",\n            "_cargo_context_signature",\n        ),\n        "observation_date",\n        as_of,\n        "configuration values",\n''',
        '"_cargo_context_signature",\n        ),\n        "observation_date",\n        as_of,\n        "configuration values"',
    )
    _patch(
        BASE,
        '''            "configuration_code",\n            "attribute_code",\n            "fuel_type_code",\n        ),\n        "observation_date",\n        as_of,\n        "configuration value ranges",\n''',
        '''            "configuration_code",\n            "attribute_code",\n            "fuel_type_code",\n            "_cargo_context_signature",\n        ),\n        "observation_date",\n        as_of,\n        "configuration value ranges",\n''',
        '"_cargo_context_signature",\n        ),\n        "observation_date",\n        as_of,\n        "configuration value ranges"',
    )
    _patch(
        BASE,
        '''    current_values = combine_latest_observations(\n        current_scalar_values, current_range_values, ComparisonError\n    )\n    current_availability = latest(\n''',
        '''    current_values = combine_latest_observations(\n        current_scalar_values, current_range_values, ComparisonError\n    )\n    current_value_groups: dict[\n        tuple[str, str, str], dict[str, dict[str, Any]]\n    ] = {}\n    for key, row in current_values.items():\n        base_key = (key[0], key[1], key[2])\n        current_value_groups.setdefault(base_key, {})[key[3]] = row\n    current_availability = latest(\n''',
        "current_value_groups:",
    )
    _patch(
        BASE,
        "        if key not in current_values:\n            missing_evidence_keys.add(\n",
        "        if key not in current_value_groups:\n            missing_evidence_keys.add(\n",
        "if key not in current_value_groups:",
    )
    _patch(
        BASE,
        "            if key in current_values:\n                raise ComparisonError(\n                    f\"not_applicable technical slot has a record: {key}\"\n",
        "            if key in current_value_groups:\n                raise ComparisonError(\n                    f\"not_applicable technical slot has a record: {key}\"\n",
        "if key in current_value_groups:",
    )
    technical_loop = '''        technical_items: list[dict[str, Any]] = []\n        for attribute_code, fuel in scope["technical_slots"]:\n            attribute = scope["attributes"][attribute_code]\n            left_key = (left_code, attribute_code, fuel)\n            right_key = (right_code, attribute_code, fuel)\n            left_group = current_value_groups.get(left_key, {})\n            right_group = current_value_groups.get(right_key, {})\n            signatures = sorted(set(left_group) | set(right_group))\n            if not signatures:\n                signatures = [""]\n\n            for signature in signatures:\n                context_row = left_group.get(signature) or right_group.get(signature)\n                raw_context = (\n                    context_row.get("_cargo_context")\n                    if context_row is not None\n                    else None\n                )\n                cargo_context = (\n                    dict(raw_context)\n                    if isinstance(raw_context, Mapping)\n                    else None\n                )\n\n                if left_key in scope["technical_na"]:\n                    left_state: dict[str, Any] = {"state": "not_applicable"}\n                elif signature in left_group:\n                    left_row = left_group[signature]\n                    left_state = (\n                        recorded_range_state(left_row, attribute)\n                        if left_row.get("_observation_kind") == "range"\n                        else recorded_technical_state(left_row, attribute)\n                    )\n                elif not left_group:\n                    left_state = evidence_state(\n                        evidence[("technical", left_code, attribute_code, fuel)]\n                    )\n                else:\n                    left_state = {"state": "missing"}\n                if cargo_context is not None and "cargo_context" not in left_state:\n                    left_state["cargo_context"] = dict(cargo_context)\n                    left_state["cargo_context_signature"] = signature\n\n                if right_key in scope["technical_na"]:\n                    right_state: dict[str, Any] = {"state": "not_applicable"}\n                elif signature in right_group:\n                    right_row = right_group[signature]\n                    right_state = (\n                        recorded_range_state(right_row, attribute)\n                        if right_row.get("_observation_kind") == "range"\n                        else recorded_technical_state(right_row, attribute)\n                    )\n                elif not right_group:\n                    right_state = evidence_state(\n                        evidence[("technical", right_code, attribute_code, fuel)]\n                    )\n                else:\n                    right_state = {"state": "missing"}\n                if cargo_context is not None and "cargo_context" not in right_state:\n                    right_state["cargo_context"] = dict(cargo_context)\n                    right_state["cargo_context_signature"] = signature\n\n                technical_comparison, relation = technical_comparison_result(\n                    left_state, right_state\n                )\n                technical_item: dict[str, Any] = {\n                    "attribute_code": attribute_code,\n                    "attribute_name": attribute["name"],\n                    "category": attribute["category"],\n                    "fuel_type_code": fuel,\n                    "unit": attribute["unit"],\n                    "left": left_state,\n                    "right": right_state,\n                    "comparison": technical_comparison,\n                }\n                if cargo_context is not None:\n                    technical_item["cargo_context"] = dict(cargo_context)\n                    technical_item["context"] = technical_context(\n                        fuel, cargo_context\n                    )\n                if relation is not None:\n                    technical_item["range_relation"] = relation\n                technical_items.append(technical_item)\n\n'''
    _replace_between(
        BASE,
        "        technical_items: list[dict[str, Any]] = []\n",
        "        equipment_items: list[dict[str, Any]] = []\n",
        technical_loop,
        'technical_item["cargo_context"]',
    )
    _patch(
        BASE,
        '''                    fuel = str(item["fuel_type_code"])\n                    context = (\n                        f"fuel_type_code={fuel}"\n                        if fuel\n                        else "fuel_type_code="\n                    )\n''',
        '''                    fuel = str(item["fuel_type_code"])\n                    raw_cargo_context = item.get("cargo_context")\n                    context = technical_context(\n                        fuel,\n                        raw_cargo_context\n                        if isinstance(raw_cargo_context, Mapping)\n                        else None,\n                    )\n''',
        "raw_cargo_context = item.get(\"cargo_context\")",
    )
    _patch(
        BASE,
        '''                elif domain == "technical":\n                    key = item["attribute_code"]\n                    context = item["fuel_type_code"] or "none"\n''',
        '''                elif domain == "technical":\n                    key = item["attribute_code"]\n                    context = item.get("context") or (\n                        item["fuel_type_code"] or "none"\n                    )\n''',
        'context = item.get("context")',
    )


def _patch_context_surfaces() -> None:
    _patch(
        CONTEXT_FILTER,
        "import configuration_comparison as core\n",
        "import configuration_comparison as core\nfrom reporting.cargo_context import technical_context\n",
        "from reporting.cargo_context import technical_context",
    )
    _patch(
        CONTEXT_FILTER,
        '''    if domain == "technical":\n        return f"fuel_type_code={item['fuel_type_code']}"\n''',
        '''    if domain == "technical":\n        cargo_context = item.get("cargo_context")\n        return technical_context(\n            str(item.get("fuel_type_code", "")),\n            cargo_context if isinstance(cargo_context, Mapping) else None,\n        )\n''',
        "cargo_context = item.get(\"cargo_context\")",
    )
    _patch(
        ITEM_CATALOG,
        "from configuration_comparison import (\n",
        "from reporting.cargo_context import technical_context\n\nfrom configuration_comparison import (\n",
        "from reporting.cargo_context import technical_context",
    )
    _patch(
        ITEM_CATALOG,
        '''    if domain == "technical":\n        fuel = str(item.get("fuel_type_code", ""))\n        return (\n            str(item.get("attribute_name", "")),\n            str(item.get("category", "")),\n            f"fuel_type_code={fuel}",\n        )\n''',
        '''    if domain == "technical":\n        fuel = str(item.get("fuel_type_code", ""))\n        cargo_context = item.get("cargo_context")\n        return (\n            str(item.get("attribute_name", "")),\n            str(item.get("category", "")),\n            technical_context(\n                fuel,\n                cargo_context if isinstance(cargo_context, Mapping) else None,\n            ),\n        )\n''',
        "cargo_context = item.get(\"cargo_context\")",
    )
    _patch(
        COMPARISON_HTML,
        "from typing import Any, Mapping\n",
        "from typing import Any, Mapping\n\nfrom reporting.cargo_context import technical_context\n",
        "from reporting.cargo_context import technical_context",
    )
    _patch(
        COMPARISON_HTML,
        '''    if domain == "technical" and item.get("fuel_type_code"):\n        context.append(f"paliwo: {item['fuel_type_code']}")\n''',
        '''    if domain == "technical":\n        cargo_context = item.get("cargo_context")\n        if isinstance(cargo_context, Mapping):\n            context.append(\n                "kontekst: "\n                + technical_context(\n                    str(item.get("fuel_type_code", "")),\n                    cargo_context,\n                )\n            )\n        elif item.get("fuel_type_code"):\n            context.append(f"paliwo: {item['fuel_type_code']}")\n''',
        '"kontekst: "',
    )


def _patch_workbook() -> None:
    _patch(
        WORKBOOK_ROWS,
        "from reporting.commercial_offers import commercial_offer_rows\n",
        "from reporting.cargo_context import cargo_context_json, technical_context\nfrom reporting.commercial_offers import commercial_offer_rows\n",
        "from reporting.cargo_context import cargo_context_json",
    )
    _patch(
        WORKBOOK_ROWS,
        '''    "reviewed_pages",\n    "evidence_basis_json",\n)\n''',
        '''    "reviewed_pages",\n    "evidence_basis_json",\n    "cargo_context_json",\n)\n''',
        '"cargo_context_json",\n)',
    )
    _patch(
        WORKBOOK_ROWS,
        '''        reviewed_text,\n        basis_text,\n    )\n''',
        '''        reviewed_text,\n        basis_text,\n        cargo_context_json(\n            state.get("cargo_context")\n            if isinstance(state.get("cargo_context"), Mapping)\n            else None\n        ),\n    )\n''',
        "cargo_context_json(\n            state.get(\"cargo_context\")",
    )
    _patch(
        WORKBOOK_ROWS,
        '''    context = (\n        f"fuel_type_code={item.get('fuel_type_code', '')}"\n        if domain == "technical" and item.get("fuel_type_code")\n        else ""\n    )\n''',
        '''    context = ""\n    if domain == "technical":\n        cargo_context = item.get("cargo_context")\n        if isinstance(cargo_context, Mapping) or item.get("fuel_type_code"):\n            context = technical_context(\n                str(item.get("fuel_type_code", "")),\n                cargo_context if isinstance(cargo_context, Mapping) else None,\n            )\n''',
        "if isinstance(cargo_context, Mapping) or item.get(\"fuel_type_code\")",
    )


def _patch_shortlist() -> None:
    _patch(
        SHORTLIST,
        "from typing import Any, Iterable, Mapping, Sequence\n",
        "from typing import Any, Iterable, Mapping, Sequence\n\nfrom reporting.cargo_context import (\n    CARGO_ATTRIBUTE_CODE,\n    CargoContextError,\n    annotate_scalar_values,\n    cargo_observations,\n    read_context_rows,\n)\n",
        "from reporting.cargo_context import (",
    )
    _patch(
        SHORTLIST,
        '''    value_rows = read_csv(master / "configuration_attribute_values.csv")\n    availability_rows = read_csv(\n''',
        '''    value_rows = read_csv(master / "configuration_attribute_values.csv")\n    try:\n        value_rows = annotate_scalar_values(\n            value_rows,\n            read_context_rows(master, read_csv),\n        )\n    except CargoContextError as exc:\n        raise ShortlistError(str(exc)) from exc\n    availability_rows = read_csv(\n''',
        "value_rows = annotate_scalar_values(",
    )
    _patch(
        SHORTLIST,
        '''    scoped_values = [\n        row\n        for row in value_rows\n        if row.get("configuration_code") in configuration_codes\n        and row.get("attribute_code") == "number_of_seats"\n        and row.get("fuel_type_code", "") == ""\n    ]\n''',
        '''    scoped_values = [\n        row\n        for row in value_rows\n        if row.get("configuration_code") in configuration_codes\n        and row.get("attribute_code") == "number_of_seats"\n        and row.get("fuel_type_code", "") == ""\n    ]\n    scoped_cargo_values = [\n        row\n        for row in value_rows\n        if row.get("configuration_code") in configuration_codes\n        and row.get("attribute_code") == CARGO_ATTRIBUTE_CODE\n    ]\n''',
        "scoped_cargo_values = [",
    )
    _patch(
        SHORTLIST,
        '''    seats = _latest(\n        scoped_values,\n        ("configuration_code",),\n        "observation_date",\n        as_of,\n    )\n    availability = _latest(\n''',
        '''    seats = _latest(\n        scoped_values,\n        ("configuration_code",),\n        "observation_date",\n        as_of,\n    )\n    cargo_values = _latest(\n        scoped_cargo_values,\n        (\n            "configuration_code",\n            "attribute_code",\n            "fuel_type_code",\n            "_cargo_context_signature",\n        ),\n        "observation_date",\n        as_of,\n    )\n    availability = _latest(\n''',
        "cargo_values = _latest(",
    )
    _patch(
        SHORTLIST,
        '''                "number_of_seats": seat,\n                "required_equipment": equipment_states,\n''',
        '''                "number_of_seats": seat,\n                "cargo_volumes": cargo_observations(\n                    [\n                        row\n                        for key, row in cargo_values.items()\n                        if key[0] == configuration_code\n                    ]\n                ),\n                "required_equipment": equipment_states,\n''',
        '"cargo_volumes": cargo_observations(',
    )
    _patch(
        SHORTLIST,
        '''    if not report["results"]:\n        lines.append("| — | — | — | — | — | — | — | No matches |")\n    return "\\n".join(lines) + "\\n"\n''',
        '''    if not report["results"]:\n        lines.append("| — | — | — | — | — | — | — | No matches |")\n\n    cargo_rows = [\n        (item["configuration_code"], observation)\n        for item in report["results"]\n        for observation in item.get("cargo_volumes", [])\n    ]\n    if cargo_rows:\n        lines.extend(\n            [\n                "",\n                "## Context-aware cargo observations",\n                "",\n                "| Configuration | Value | Context | Source | Date |",\n                "| --- | ---: | --- | --- | --- |",\n            ]\n        )\n        for configuration_code, observation in cargo_rows:\n            lines.append(\n                "| "\n                + " | ".join(\n                    _markdown(value)\n                    for value in (\n                        f"`{configuration_code}`",\n                        f"{observation['value']} L",\n                        observation["context"],\n                        observation["source_code"],\n                        observation["observation_date"],\n                    )\n                )\n                + " |"\n            )\n    return "\\n".join(lines) + "\\n"\n''',
        "## Context-aware cargo observations",
    )
    _patch(
        SHORTLIST,
        '''    "seats_source_code",\n    "required_equipment_states",\n''',
        '''    "seats_source_code",\n    "cargo_volumes_json",\n    "required_equipment_states",\n''',
        '"cargo_volumes_json",',
    )
    _patch(
        SHORTLIST,
        '''                "seats_source_code": str(seats.get("source_code", "")),\n                "required_equipment_states": ";".join(\n''',
        '''                "seats_source_code": str(seats.get("source_code", "")),\n                "cargo_volumes_json": json.dumps(\n                    item.get("cargo_volumes", []),\n                    ensure_ascii=False,\n                    sort_keys=True,\n                    separators=(",", ":"),\n                ),\n                "required_equipment_states": ";".join(\n''',
        '"cargo_volumes_json": json.dumps(',
    )


def _patch_shortlist_html() -> None:
    _patch(
        SHORTLIST_HTML,
        "from reporting import configuration_shortlist as core\n",
        "from reporting import configuration_shortlist as core\nfrom reporting.cargo_context import (\n    CARGO_ATTRIBUTE_CODE,\n    CargoContextError,\n    annotate_scalar_values,\n    read_context_rows,\n    semantic_signature,\n    technical_context,\n)\n",
        "from reporting.cargo_context import (",
    )
    _patch(
        SHORTLIST_HTML,
        '''def _comparison_key(attribute_code: str, fuel_type_code: str) -> str:\n    return f"{attribute_code}::{fuel_type_code or 'all'}"\n''',
        '''def _comparison_key(\n    attribute_code: str,\n    fuel_type_code: str,\n    cargo_context_signature: str = "",\n) -> str:\n    base = f"{attribute_code}::{fuel_type_code or 'all'}"\n    return (\n        base\n        if not cargo_context_signature\n        else f"{base}::cargo::{cargo_context_signature}"\n    )\n''',
        "cargo_context_signature: str = \"\"",
    )
    _patch(
        SHORTLIST_HTML,
        '''    unit = _unit_label(attribute.get("unit", ""))\n    value = _scalar_display(row.get("value", ""), attribute, enum_labels)\n    display_value = f"{value} {unit}".strip()\n    return {\n        "key": _comparison_key(attribute_code, fuel_type_code),\n''',
        '''    unit = _unit_label(attribute.get("unit", ""))\n    value = _scalar_display(row.get("value", ""), attribute, enum_labels)\n    display_value = f"{value} {unit}".strip()\n    cargo_context = row.get("_cargo_context")\n    context_payload = (\n        dict(cargo_context)\n        if isinstance(cargo_context, Mapping)\n        else None\n    )\n    signature = str(row.get("_cargo_context_signature", ""))\n    return {\n        "key": _comparison_key(attribute_code, fuel_type_code, signature),\n''',
        "context_payload = (",
    )
    _patch(
        SHORTLIST_HTML,
        '''        "fuel_type_label": _FUEL_LABELS_PL.get(fuel_type_code, fuel_type_code),\n        "kind": "value",\n''',
        '''        "fuel_type_label": _FUEL_LABELS_PL.get(fuel_type_code, fuel_type_code),\n        "cargo_context": context_payload,\n        "cargo_context_signature": signature,\n        "cargo_context_label": (\n            semantic_signature(context_payload)\n            if context_payload is not None\n            else ""\n        ),\n        "context": technical_context(fuel_type_code, context_payload),\n        "kind": "value",\n''',
        '"cargo_context_label": (',
    )
    _patch(
        SHORTLIST_HTML,
        '''    value_rows = [\n        row for row in core.read_csv(master / "configuration_attribute_values.csv")\n        if row.get("configuration_code") in configuration_codes\n    ]\n''',
        '''    value_rows = [\n        row for row in core.read_csv(master / "configuration_attribute_values.csv")\n        if row.get("configuration_code") in configuration_codes\n    ]\n    try:\n        value_rows = annotate_scalar_values(\n            value_rows,\n            read_context_rows(master, core.read_csv),\n        )\n    except CargoContextError as exc:\n        raise core.ShortlistError(str(exc)) from exc\n''',
        "value_rows = annotate_scalar_values(",
    )
    _patch(
        SHORTLIST_HTML,
        '''        ("configuration_code", "attribute_code", "fuel_type_code"),\n        "observation_date",\n        as_of,\n    )\n    latest_ranges = core._latest(\n''',
        '''        (\n            "configuration_code",\n            "attribute_code",\n            "fuel_type_code",\n            "_cargo_context_signature",\n        ),\n        "observation_date",\n        as_of,\n    )\n    latest_ranges = core._latest(\n''',
        '"_cargo_context_signature",\n        ),\n        "observation_date",\n        as_of,\n    )\n    latest_ranges',
    )
    _patch(
        SHORTLIST_HTML,
        '''    for (configuration_code, attribute_code, _), row in latest_values.items():\n''',
        '''    for (configuration_code, attribute_code, _, _), row in latest_values.items():\n''',
        "for (configuration_code, attribute_code, _, _), row in latest_values.items():",
    )
    _patch(
        SHORTLIST_HTML,
        '''            "fuel_type_code", "fuel_type_label",\n        )}\n''',
        '''            "fuel_type_code", "fuel_type_label", "cargo_context",\n            "cargo_context_signature", "cargo_context_label", "context",\n        )}\n''',
        '"cargo_context_signature", "cargo_context_label", "context",',
    )
    _patch(
        SHORTLIST_HTML,
        '''                "comparison_values": value_index.get(code, {}),\n                "equipment": equipment,\n''',
        '''                "comparison_values": value_index.get(code, {}),\n                "cargo_volumes": sorted(\n                    [\n                        state\n                        for state in value_index.get(code, {}).values()\n                        if state.get("attribute_code") == CARGO_ATTRIBUTE_CODE\n                    ],\n                    key=lambda state: (\n                        state.get("cargo_context_signature", ""),\n                        state.get("observation_date", ""),\n                        state.get("key", ""),\n                    ),\n                ),\n                "equipment": equipment,\n''',
        '"cargo_volumes": sorted(',
    )


def _patch_selection_export() -> None:
    _patch(
        SELECTION_JS,
        '''      catalog_price: configuration.catalog_price,\n      number_of_seats: configuration.number_of_seats\n''',
        '''      catalog_price: configuration.catalog_price,\n      number_of_seats: configuration.number_of_seats,\n      cargo_volumes: configuration.cargo_volumes || []\n''',
        "cargo_volumes: configuration.cargo_volumes || []",
    )
    _patch(
        SELECTION_JS,
        '''  function comparisonValueLabel(facet) {\n    const fuel = String(facet.fuel_type_label || "").trim();\n    return fuel ? `${facet.label} — ${fuel}` : String(facet.label || facet.attribute_code || facet.key);\n  }\n''',
        '''  function comparisonValueLabel(facet) {\n    const label = String(facet.label || facet.attribute_code || facet.key);\n    const fuel = String(facet.fuel_type_label || "").trim();\n    const cargo = String(facet.cargo_context_label || "").trim();\n    return [label, fuel, cargo].filter(Boolean).join(" — ");\n  }\n''',
        "const cargo = String(facet.cargo_context_label",
    )


def _decouple_historical_schema_contract() -> None:
    _replace_between(
        SCHEMA_TOOL,
        '    if state.get("phase") != "Brochure Cargo Context Schema Foundation":\n',
        '    print("PASS: brochure cargo context schema foundation contract")\n',
        '''    if not state.get("phase"):\n        raise RuntimeError("project phase missing")\n    if baseline.get("tests", 0) < 776:\n        raise RuntimeError("test baseline regressed")\n    if baseline.get("csv_files", 0) < 46:\n        raise RuntimeError("CSV baseline regressed")\n    if baseline.get("rows", 0) < 8156:\n        raise RuntimeError("master-row baseline regressed")\n    if baseline.get("configuration_values") != 1831:\n        raise RuntimeError("configuration values changed")\n    if state.get("current_package", {}).get("status") != "complete":\n        raise RuntimeError("current package is not complete")\n    if not state.get("next_package", {}).get("name"):\n        raise RuntimeError("next package missing")\n\n''',
        "CSV baseline regressed",
    )
    _replace_between(
        SCHEMA_TEST,
        '        self.assertEqual(state["phase"], "Brochure Cargo Context Schema Foundation")\n',
        '\n\nif __name__ == "__main__":\n',
        '''        self.assertTrue(state["phase"])\n        self.assertGreaterEqual(state["baseline"]["tests"], 776)\n        self.assertGreaterEqual(state["baseline"]["csv_files"], 46)\n        self.assertGreaterEqual(state["baseline"]["rows"], 8156)\n        self.assertEqual(state["baseline"]["configuration_values"], 1831)\n        self.assertEqual(state["current_package"]["status"], "complete")\n        self.assertTrue(state["next_package"]["name"])\n''',
        'self.assertGreaterEqual(state["baseline"]["csv_files"], 46)',
    )


def _apply_state_and_docs() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("baseline", {}).get("configuration_values") != 1831:
        raise RuntimeError("unexpected configuration-value baseline")
    state["updated_on"] = "2026-07-25"
    state["phase"] = "Brochure Cargo Context Reporting Foundation"
    state["current_package"] = {
        "name": "Brochure Cargo Context Reporting Foundation",
        "status": "complete",
        "goal": (
            "Make comparison, shortlist and export reporting expose exact cargo-context "
            "fields and preserve every context-distinct boot_capacity observation without "
            "importing official brochure values."
        ),
    }
    state["next_package"] = {
        "name": "Official Brochure Cargo Value Import",
        "status": "planned",
        "goal": (
            "Import source-backed canonical boot_capacity observations from the registered "
            "official brochures with exact cargo context and no migration or inference from "
            "legacy cargo attributes."
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


def apply() -> None:
    _patch_comparison_base()
    _patch_context_surfaces()
    _patch_workbook()
    _patch_shortlist()
    _patch_shortlist_html()
    _patch_selection_export()
    _decouple_historical_schema_contract()
    _apply_state_and_docs()


def check() -> None:
    required_markers = {
        BASE: [
            "current_value_groups:",
            'technical_item["cargo_context"]',
            'raw_cargo_context = item.get("cargo_context")',
        ],
        CONTEXT_FILTER: ["from reporting.cargo_context import technical_context"],
        ITEM_CATALOG: ["from reporting.cargo_context import technical_context"],
        COMPARISON_HTML: ['"kontekst: "'],
        WORKBOOK_ROWS: ['"cargo_context_json",', "cargo_context_json("],
        SHORTLIST: ['"cargo_volumes": cargo_observations(', '"cargo_volumes_json": json.dumps('],
        SHORTLIST_HTML: ['"cargo_volumes": sorted(', "cargo_context_signature: str = \"\""],
        SELECTION_JS: ["cargo_volumes: configuration.cargo_volumes || []"],
        SCHEMA_TOOL: ["CSV baseline regressed"],
        SCHEMA_TEST: ['self.assertGreaterEqual(state["baseline"]["csv_files"], 46)'],
    }
    for path, markers in required_markers.items():
        text = path.read_text(encoding="utf-8")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            raise RuntimeError(f"reporting marker missing in {path}: {missing}")

    if json.loads(REPORT.read_text(encoding="utf-8")) != REPORT_DATA:
        raise RuntimeError("reporting foundation report differs")
    if PACKAGE.read_text(encoding="utf-8").rstrip() != PACKAGE_TEXT.rstrip():
        raise RuntimeError("package document differs")
    if REVIEW.read_text(encoding="utf-8").rstrip() != REVIEW_TEXT.rstrip():
        raise RuntimeError("review document differs")
    if CHANGELOG_ENTRY not in CHANGELOG.read_text(encoding="utf-8"):
        raise RuntimeError("changelog entry missing")

    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("phase") != "Brochure Cargo Context Reporting Foundation":
        raise RuntimeError("project phase mismatch")
    if state.get("baseline", {}).get("configuration_values") != 1831:
        raise RuntimeError("configuration values changed")
    if state.get("current_package", {}).get("status") != "complete":
        raise RuntimeError("current package is not complete")
    if state.get("next_package", {}).get("name") != "Official Brochure Cargo Value Import":
        raise RuntimeError("next package mismatch")

    relation = ROOT / "data" / "master" / "configuration_cargo_volume_contexts.csv"
    lines = relation.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) != 1:
        raise RuntimeError("production cargo-context relation is no longer header-only")
    print("PASS: brochure cargo context reporting foundation contract")


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
