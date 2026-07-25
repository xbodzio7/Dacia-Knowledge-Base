#!/usr/bin/env python3
"""Make source coverage cargo-context aware and refresh the workbook contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "_source_coverage_base.py"
WORKBOOK_TEST = ROOT / "tests" / "test_configuration_comparison_workbook.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"patch anchor missing: {label}")
    return text.replace(old, new, 1)


text = SOURCE.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from configuration_value_range_reporting import (\n"
    "    combine_latest_observations,\n"
    "    read_optional_ranges,\n"
    ")\n",
    "from configuration_value_range_reporting import (\n"
    "    combine_latest_observations,\n"
    "    read_optional_ranges,\n"
    ")\n"
    "from reporting.cargo_context import (\n"
    "    CargoContextError,\n"
    "    annotate_scalar_values,\n"
    "    read_context_rows,\n"
    ")\n",
    "cargo imports",
)
text = replace_once(
    text,
    '            if not item and field != "fuel_type_code":\n',
    '            if not item and field not in {"fuel_type_code", "_cargo_context_signature"}:\n',
    "optional context signature",
)
text = replace_once(
    text,
    "    scoped_values = [\n"
    "        row for row in values\n"
    "        if row.get(\"configuration_code\") in scoped_configurations\n"
    "    ]\n"
    "    scoped_ranges = [\n"
    "        row for row in ranges\n"
    "        if row.get(\"configuration_code\") in scoped_configurations\n"
    "    ]\n",
    "    raw_scoped_values = [\n"
    "        row for row in values\n"
    "        if row.get(\"configuration_code\") in scoped_configurations\n"
    "    ]\n"
    "    try:\n"
    "        scoped_values = annotate_scalar_values(\n"
    "            raw_scoped_values,\n"
    "            read_context_rows(master, read_csv),\n"
    "        )\n"
    "    except CargoContextError as exc:\n"
    "        raise SourceCoverageError(str(exc)) from exc\n"
    "    scoped_ranges = [\n"
    "        {**row, \"_cargo_context_signature\": \"\", \"_cargo_context\": None}\n"
    "        for row in ranges\n"
    "        if row.get(\"configuration_code\") in scoped_configurations\n"
    "    ]\n",
    "annotate scoped values",
)
text = replace_once(
    text,
    "    current_scalar_values = latest_records(\n"
    "        scoped_values,\n"
    "        (\"configuration_code\", \"attribute_code\", \"fuel_type_code\"),\n"
    "        \"observation_date\",\n"
    "        as_of,\n"
    "        \"configuration values\",\n"
    "    )\n"
    "    current_range_values = latest_records(\n"
    "        scoped_ranges,\n"
    "        (\"configuration_code\", \"attribute_code\", \"fuel_type_code\"),\n"
    "        \"observation_date\",\n"
    "        as_of,\n"
    "        \"configuration value ranges\",\n"
    "    )\n"
    "    current_values = combine_latest_observations(\n"
    "        current_scalar_values, current_range_values, SourceCoverageError\n"
    "    )\n",
    "    current_scalar_values = latest_records(\n"
    "        scoped_values,\n"
    "        (\n"
    "            \"configuration_code\",\n"
    "            \"attribute_code\",\n"
    "            \"fuel_type_code\",\n"
    "            \"_cargo_context_signature\",\n"
    "        ),\n"
    "        \"observation_date\",\n"
    "        as_of,\n"
    "        \"configuration values\",\n"
    "    )\n"
    "    current_range_values = latest_records(\n"
    "        scoped_ranges,\n"
    "        (\n"
    "            \"configuration_code\",\n"
    "            \"attribute_code\",\n"
    "            \"fuel_type_code\",\n"
    "            \"_cargo_context_signature\",\n"
    "        ),\n"
    "        \"observation_date\",\n"
    "        as_of,\n"
    "        \"configuration value ranges\",\n"
    "    )\n"
    "    current_values = combine_latest_observations(\n"
    "        current_scalar_values, current_range_values, SourceCoverageError\n"
    "    )\n"
    "    current_value_groups: dict[\n"
    "        tuple[str, str, str], dict[str, dict[str, Any]]\n"
    "    ] = {}\n"
    "    for current_key, current_row in current_values.items():\n"
    "        base_key = (current_key[0], current_key[1], current_key[2])\n"
    "        current_value_groups.setdefault(base_key, {})[current_key[3]] = current_row\n",
    "context-aware current values",
)
text = replace_once(
    text,
    "                if key in current_values:\n",
    "                if key in current_value_groups:\n",
    "grouped technical membership",
)
SOURCE.write_text(text, encoding="utf-8")

workbook = WORKBOOK_TEST.read_text(encoding="utf-8")
workbook = replace_once(
    workbook,
    '            "A1:AS209",\n',
    '            "A1:AS213",\n',
    "workbook comparison dimension",
)
WORKBOOK_TEST.write_text(workbook, encoding="utf-8")
print("PASS: source coverage and workbook cargo integration applied")
