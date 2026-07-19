#!/usr/bin/env python3
"""One-shot materializer for the selected Jogger MY26 WLTP range package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src_pl_jogger_price_my26_20260401"
SPEC_DIR = ROOT / "data" / "imports" / "configuration_value_ranges"

MANUAL = [
    "jogger_essential_5seat_ecog120_manual",
    "jogger_expression_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_manual",
    "jogger_essential_7seat_ecog120_manual",
    "jogger_expression_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_manual",
]
AUTOMATIC = [
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
    "jogger_extreme_7seat_ecog120_automatic",
    "jogger_journey_7seat_ecog120_automatic",
]
TCE = [
    "jogger_expression_5seat_tce110_manual",
    "jogger_extreme_5seat_tce110_manual",
    "jogger_journey_5seat_tce110_manual",
    "jogger_expression_7seat_tce110_manual",
    "jogger_extreme_7seat_tce110_manual",
    "jogger_journey_7seat_tce110_manual",
]
HYBRID = [
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
]


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"patch anchor count for {relative} is {count}, expected 1: {old[:120]!r}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_spec(
    filename: str,
    id_start: int,
    attribute_code: str,
    unit: str,
    configurations: list[str],
    observations: list[tuple[str, str, str, str]],
    top_level_fuel: str = "",
) -> Path:
    rows: list[dict[str, object]] = []
    for configuration in configurations:
        for fuel, minimum, maximum, source_text in observations:
            row: dict[str, object] = {
                "configuration_code": configuration,
                "source_code": SOURCE,
                "minimum_value": minimum,
                "maximum_value": maximum,
                "lower_inclusive": True,
                "upper_inclusive": True,
                "source_text": source_text,
            }
            if fuel != top_level_fuel:
                row["fuel_type_code"] = fuel
            rows.append(row)
    payload = {
        "version": 1,
        "kind": "configuration_attribute_value_ranges",
        "id_start": id_start,
        "attribute_code": attribute_code,
        "attribute_contract": {
            "data_type": "decimal",
            "unit": unit,
            "status": "active",
        },
        "observation_date": "2026-04-01",
        "fuel_type_code": top_level_fuel,
        "source_page": 6,
        "source_section": "OSIĄGI",
        "notes_template": "Source page {page}, section {section}: {source_text}",
        "rows": rows,
    }
    path = SPEC_DIR / filename
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def create_specs() -> list[Path]:
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    return [
        write_spec(
            "jogger-page6-ecog120-manual-fuel-consumption-range-20260401.json",
            1,
            "fuel_consumption_combined",
            "l/100 km",
            MANUAL,
            [
                ("lpg", "7.3", "7.4", "LPG: 7,3-7,4"),
                ("petrol", "5.8", "5.9", "Ben: 5,8-5,9"),
            ],
        ),
        write_spec(
            "jogger-page6-ecog120-manual-co2-emissions-range-20260401.json",
            13,
            "co2_emissions",
            "g/km",
            MANUAL,
            [
                ("lpg", "119", "121", "LPG: 119-121"),
                ("petrol", "133", "134", "Ben: 133-134"),
            ],
        ),
        write_spec(
            "jogger-page6-ecog120-automatic-fuel-consumption-range-20260401.json",
            25,
            "fuel_consumption_combined",
            "l/100 km",
            AUTOMATIC,
            [
                ("lpg", "7.5", "7.6", "LPG: 7,5-7,6"),
                ("petrol", "6", "6.1", "Ben: 6,0-6,1"),
            ],
        ),
        write_spec(
            "jogger-page6-ecog120-automatic-co2-emissions-range-20260401.json",
            33,
            "co2_emissions",
            "g/km",
            AUTOMATIC,
            [
                ("lpg", "121", "123", "LPG: 121-123"),
                ("petrol", "137", "138", "Ben: 137-138"),
            ],
        ),
        write_spec(
            "jogger-page6-tce110-manual-fuel-consumption-range-20260401.json",
            41,
            "fuel_consumption_combined",
            "l/100 km",
            TCE,
            [("petrol", "5.7", "5.8", "5,7-5,8")],
            "petrol",
        ),
        write_spec(
            "jogger-page6-tce110-manual-co2-emissions-range-20260401.json",
            47,
            "co2_emissions",
            "g/km",
            TCE,
            [("petrol", "129", "131", "129-131")],
            "petrol",
        ),
        write_spec(
            "jogger-page6-hybrid155-automatic-fuel-consumption-range-20260401.json",
            53,
            "fuel_consumption_combined",
            "l/100 km",
            HYBRID,
            [("petrol", "4.5", "4.6", "4,5-4,6")],
            "petrol",
        ),
        write_spec(
            "jogger-page6-hybrid155-automatic-co2-emissions-range-20260401.json",
            59,
            "co2_emissions",
            "g/km",
            HYBRID,
            [("petrol", "103", "104", "103-104")],
            "petrol",
        ),
    ]


def patch_baseline_contract() -> None:
    replace_once(
        "tools/documentation_baseline.py",
        "    configuration_values: int\n    configuration_import_specs: int\n",
        "    configuration_values: int\n    configuration_import_specs: int\n"
        "    configuration_value_ranges: int\n"
        "    configuration_range_import_specs: int\n",
    )
    replace_once(
        "tools/documentation_baseline.py",
        '    values = read_csv_rows(master / "configuration_attribute_values.csv")\n'
        "    availability = read_csv_rows(\n",
        '    values = read_csv_rows(master / "configuration_attribute_values.csv")\n'
        '    range_path = master / "configuration_attribute_value_ranges.csv"\n'
        "    ranges = read_csv_rows(range_path) if range_path.is_file() else []\n"
        "    availability = read_csv_rows(\n",
    )
    replace_once(
        "tools/documentation_baseline.py",
        '    import_dir = repository / "data" / "imports" / "configuration_values"\n'
        "    if not import_dir.is_dir():\n"
        '        raise BaselineError(f"import directory does not exist: {import_dir}")\n',
        '    import_dir = repository / "data" / "imports" / "configuration_values"\n'
        "    if not import_dir.is_dir():\n"
        '        raise BaselineError(f"import directory does not exist: {import_dir}")\n'
        "    range_import_dir = (\n"
        '        repository / "data" / "imports" / "configuration_value_ranges"\n'
        "    )\n",
    )
    replace_once(
        "tools/documentation_baseline.py",
        "        configuration_values=len(values),\n"
        '        configuration_import_specs=len(list(import_dir.glob("*.json"))),\n',
        "        configuration_values=len(values),\n"
        '        configuration_import_specs=len(list(import_dir.glob("*.json"))),\n'
        "        configuration_value_ranges=len(ranges),\n"
        "        configuration_range_import_specs=(\n"
        '            len(list(range_import_dir.glob("*.json")))\n'
        "            if range_import_dir.is_dir()\n"
        "            else 0\n"
        "        ),\n",
    )
    replace_once(
        "tools/documentation_baseline.py",
        '            "values": value.configuration_values,\n'
        '            "import_specs": value.configuration_import_specs,\n',
        '            "values": value.configuration_values,\n'
        '            "import_specs": value.configuration_import_specs,\n'
        '            "value_ranges": value.configuration_value_ranges,\n'
        '            "range_import_specs": value.configuration_range_import_specs,\n',
    )
    replace_once(
        "tools/documentation_baseline.py",
        '        ("Configuration import specs", value.configuration_import_specs),\n',
        '        ("Configuration import specs", value.configuration_import_specs),\n'
        '        ("Configuration value ranges", value.configuration_value_ranges),\n'
        '        ("Configuration range import specs", value.configuration_range_import_specs),\n',
    )
    replace_once(
        "tools/documentation_baseline.py",
        '            f"{value.configuration_import_specs}\\n"\n'
        '            "deklaratywnych specyfikacji importu oraz "\n',
        '            f"{value.configuration_import_specs} skalarnych specyfikacji importu, "\n'
        '            f"{value.configuration_value_ranges} zakresów konfiguracji i "\n'
        '            f"{value.configuration_range_import_specs}\\n"\n'
        '            "specyfikacji zakresów oraz "\n',
    )
    replace_once(
        "tools/documentation_baseline.py",
        "                (\n"
        '                    "* Declarative configuration-value imports now contain "\n'
        '                    f"{value.configuration_import_specs} versioned JSON "\n'
        '                    "specifications."\n'
        "                ),\n",
        "                (\n"
        '                    "* Declarative scalar configuration-value imports now contain "\n'
        '                    f"{value.configuration_import_specs} versioned JSON "\n'
        '                    "specifications."\n'
        "                ),\n"
        "                (\n"
        '                    "* Configuration value ranges now contain "\n'
        '                    f"{value.configuration_value_ranges} dated records from "\n'
        '                    f"{value.configuration_range_import_specs} range specifications."\n'
        "                ),\n",
    )
    replace_once(
        "tools/documentation_baseline.py",
        "                (\n"
        '                    f"- {value.configuration_import_specs} wersjonowanych "\n'
        '                    "specyfikacji w `data/imports/configuration_values`,"\n'
        "                ),\n",
        "                (\n"
        '                    f"- {value.configuration_import_specs} wersjonowanych "\n'
        '                    "specyfikacji w `data/imports/configuration_values`,"\n'
        "                ),\n"
        "                (\n"
        '                    f"- {value.configuration_value_ranges} obserwacji w "\n'
        '                    "`configuration_attribute_value_ranges.csv`,"\n'
        "                ),\n"
        "                (\n"
        '                    f"- {value.configuration_range_import_specs} wersjonowanych "\n'
        '                    "specyfikacji w `data/imports/configuration_value_ranges`,"\n'
        "                ),\n",
    )
    replace_once(
        "tools/documentation_baseline.py",
        '    print(f"Import specs         : {value.configuration_import_specs}")\n',
        '    print(f"Import specs         : {value.configuration_import_specs}")\n'
        '    print(f"Value ranges         : {value.configuration_value_ranges}")\n'
        '    print(f"Range import specs   : {value.configuration_range_import_specs}")\n',
    )


def patch_project_state_contract() -> None:
    replace_once(
        "tools/project_state.py",
        '    "configuration_import_specs": "configuration_import_specs",\n',
        '    "configuration_import_specs": "configuration_import_specs",\n'
        '    "configuration_value_ranges": "configuration_value_ranges",\n'
        '    "configuration_range_import_specs": "configuration_range_import_specs",\n',
    )
    replace_once(
        "tools/project_state.py",
        "        (\n"
        '            "- Configuration import specifications: "\n'
        '            f"{baseline[\'configuration_import_specs\']}"\n'
        "        ),\n"
        '        f"- Availability records: {baseline[\'availability_records\']}",\n',
        "        (\n"
        '            "- Configuration import specifications: "\n'
        '            f"{baseline[\'configuration_import_specs\']}"\n'
        "        ),\n"
        '        f"- Configuration value ranges: {baseline[\'configuration_value_ranges\']}",\n'
        "        (\n"
        '            "- Configuration range import specifications: "\n'
        '            f"{baseline[\'configuration_range_import_specs\']}"\n'
        "        ),\n"
        '        f"- Availability records: {baseline[\'availability_records\']}",\n',
    )
    replace_once(
        "tests/test_documentation_baseline.py",
        "        self.assertEqual(value.configuration_import_specs, 2)\n",
        "        self.assertEqual(value.configuration_import_specs, 2)\n"
        "        self.assertEqual(value.configuration_value_ranges, 0)\n"
        "        self.assertEqual(value.configuration_range_import_specs, 0)\n",
    )
    replace_once(
        "tests/project_state_contract.py",
        '                "configuration_import_specs": 1,\n'
        '                "availability_records": 4,\n',
        '                "configuration_import_specs": 1,\n'
        '                "configuration_value_ranges": 1,\n'
        '                "configuration_range_import_specs": 1,\n'
        '                "availability_records": 4,\n',
    )
    replace_once(
        "tests/project_state_contract.py",
        "            configuration_import_specs=2,\n"
        "            configuration_availability=5,\n",
        "            configuration_import_specs=2,\n"
        "            configuration_value_ranges=2,\n"
        "            configuration_range_import_specs=2,\n"
        "            configuration_availability=5,\n",
    )
    replace_once(
        "tests/project_state_contract.py",
        '                "configuration_import_specs": 2,\n'
        '                "availability_records": 5,\n',
        '                "configuration_import_specs": 2,\n'
        '                "configuration_value_ranges": 2,\n'
        '                "configuration_range_import_specs": 2,\n'
        '                "availability_records": 5,\n',
    )
    replace_once(
        "tests/project_state_contract.py",
        "        self.assertEqual(len(drift), 8)\n",
        "        self.assertEqual(len(drift), 10)\n",
    )


def update_state_and_review() -> None:
    state_path = ROOT / "project" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["reference_delivery"] = {
        "name": "Jogger WLTP Efficiency Range Import Selection",
        "pull_request": 123,
        "head_sha": "75fc4d3d00e008fbf6d623ac0705fa9194287d3c",
        "quality_run": 541,
    }
    state["baseline"] = {
        "tests": 528,
        "csv_files": 37,
        "rows": 3909,
        "configuration_values": 1204,
        "configuration_import_specs": 71,
        "configuration_value_ranges": 64,
        "configuration_range_import_specs": 8,
        "availability_records": 1811,
        "attributes": 357,
        "attribute_categories": 30,
    }
    state["current_package"] = {
        "name": "Jogger WLTP Efficiency Range Modeling and Import",
        "status": "active",
        "goal": "Materialize eight strict page-6 range specifications and 64 closed fuel-consumption and CO2 observations for all active Jogger configurations with exact fuel contexts.",
    }
    state["next_package"] = {
        "name": "Jogger Payload and Performance Range Selection",
        "status": "planned",
        "goal": "Select the seat-qualified maximum-payload ranges and the independently stated Hybrid acceleration and engine-speed ranges after the WLTP package is verified.",
    }
    state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    review = """# Jogger WLTP Efficiency Range Modeling and Import

## Status

`IMPLEMENTING`

This package materializes the denominator selected in PR #123 through the separate range table. Scalar configuration values remain unchanged.

## Denominator

Eight strict specifications create 64 closed page-6 ranges: 24 Eco-G manual, 16 Eco-G automatic, 12 TCe 110 and 12 Hybrid 155 observations. There are 32 combined fuel-consumption ranges and 32 combined CO2 ranges. Eco-G uses separate `lpg` and `petrol` contexts; TCe and Hybrid use `petrol`.

## Provenance

Range IDs form the first contiguous suffix `1-64`. Every row uses observation date `2026-04-01`, source `src_pl_jogger_price_my26_20260401`, page 6 and section `OSIĄGI`. Both endpoints are inclusive.

## Baseline counters

The canonical baseline separately tracks scalar values, scalar specifications, value ranges and range specifications.

## Boundary

Payload, acceleration, RPM and battery-capacity evidence remain outside this package. No scalar row is added or replaced.

## Expected baseline

- 528 tests;
- 37 master CSV files and 3,909 rows;
- 1,204 scalar values and 71 scalar specifications;
- 64 range values and 8 range specifications;
- 1,811 availability records;
- 357 attributes in 30 categories.

## Next package

**Jogger Payload and Performance Range Selection** will select the remaining seat-qualified and performance ranges separately.
"""
    (ROOT / "project" / "reviews" / "jogger-wltp-efficiency-range-import.md").write_text(
        review,
        encoding="utf-8",
    )


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    specs = create_specs()
    patch_baseline_contract()
    patch_project_state_contract()
    update_state_and_review()

    for spec in specs:
        run(
            [
                sys.executable,
                "tools/dkb.py",
                "import-configuration-value-ranges",
                "--spec",
                str(spec.relative_to(ROOT)),
                "--apply",
            ]
        )
    run([sys.executable, "tools/dkb.py", "project-state", "--apply"])
    run([sys.executable, "tools/dkb.py", "documentation-baseline", "--apply"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
