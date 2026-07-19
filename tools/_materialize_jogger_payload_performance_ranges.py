#!/usr/bin/env python3
"""One-shot materializer for selected Jogger payload and performance ranges."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src_pl_jogger_price_my26_20260401"
SPEC_DIR = ROOT / "data" / "imports" / "configuration_value_ranges"
DATE = "2026-04-01"

MANUAL_5 = [
    "jogger_essential_5seat_ecog120_manual",
    "jogger_expression_5seat_ecog120_manual",
    "jogger_extreme_5seat_ecog120_manual",
]
MANUAL_7 = [
    "jogger_essential_7seat_ecog120_manual",
    "jogger_expression_7seat_ecog120_manual",
    "jogger_extreme_7seat_ecog120_manual",
]
AUTO_5 = [
    "jogger_extreme_5seat_ecog120_automatic",
    "jogger_journey_5seat_ecog120_automatic",
]
AUTO_7 = [
    "jogger_extreme_7seat_ecog120_automatic",
    "jogger_journey_7seat_ecog120_automatic",
]
TCE_5 = [
    "jogger_expression_5seat_tce110_manual",
    "jogger_extreme_5seat_tce110_manual",
    "jogger_journey_5seat_tce110_manual",
]
TCE_7 = [
    "jogger_expression_7seat_tce110_manual",
    "jogger_extreme_7seat_tce110_manual",
    "jogger_journey_7seat_tce110_manual",
]
HYBRID_5 = [
    "jogger_expression_5seat_hybrid155_automatic",
    "jogger_extreme_5seat_hybrid155_automatic",
    "jogger_journey_5seat_hybrid155_automatic",
]
HYBRID_7 = [
    "jogger_expression_7seat_hybrid155_automatic",
    "jogger_extreme_7seat_hybrid155_automatic",
    "jogger_journey_7seat_hybrid155_automatic",
]
MANUAL = MANUAL_5 + MANUAL_7
AUTOMATIC = AUTO_5 + AUTO_7
TCE = TCE_5 + TCE_7
HYBRID = HYBRID_5 + HYBRID_7


def write_spec(
    filename: str,
    id_start: int,
    attribute: str,
    data_type: str,
    unit: str,
    section: str,
    rows: list[tuple[str, str, str, str, str | None]],
    top_fuel: str = "",
) -> Path:
    payload_rows: list[dict[str, object]] = []
    for configuration, minimum, maximum, source_text, fuel in rows:
        row: dict[str, object] = {
            "configuration_code": configuration,
            "source_code": SOURCE,
            "minimum_value": minimum,
            "maximum_value": maximum,
            "lower_inclusive": True,
            "upper_inclusive": True,
            "source_text": source_text,
        }
        if fuel is not None and fuel != top_fuel:
            row["fuel_type_code"] = fuel
        payload_rows.append(row)
    payload = {
        "version": 1,
        "kind": "configuration_attribute_value_ranges",
        "id_start": id_start,
        "attribute_code": attribute,
        "attribute_contract": {
            "data_type": data_type,
            "unit": unit,
            "status": "active",
        },
        "observation_date": DATE,
        "fuel_type_code": top_fuel,
        "source_page": 6,
        "source_section": section,
        "notes_template": "Source page {page}, section {section}: {source_text}",
        "rows": payload_rows,
    }
    path = SPEC_DIR / filename
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def seat_rows(
    five: list[str],
    seven: list[str],
    five_min: str,
    five_max: str,
    seven_min: str,
    seven_max: str,
    source_text: str,
) -> list[tuple[str, str, str, str, None]]:
    return [
        *[(code, five_min, five_max, source_text, None) for code in five],
        *[(code, seven_min, seven_max, source_text, None) for code in seven],
    ]


def fuel_rows(
    configurations: list[str],
    observations: list[tuple[str, str, str, str]],
) -> list[tuple[str, str, str, str, str]]:
    return [
        (configuration, minimum, maximum, source_text, fuel)
        for configuration in configurations
        for fuel, minimum, maximum, source_text in observations
    ]


def create_specs() -> list[Path]:
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    return [
        write_spec(
            "jogger-page6-ecog120-manual-maximum-payload-range-20260401.json",
            65,
            "maximum_payload",
            "integer",
            "kg",
            "MASY (kg)",
            seat_rows(MANUAL_5, MANUAL_7, "453", "473", "598", "619", "453-473 / 598-619"),
        ),
        write_spec(
            "jogger-page6-ecog120-automatic-maximum-payload-range-20260401.json",
            71,
            "maximum_payload",
            "integer",
            "kg",
            "MASY (kg)",
            seat_rows(AUTO_5, AUTO_7, "450", "459", "596", "606", "450-459 / 596-606"),
        ),
        write_spec(
            "jogger-page6-tce110-manual-maximum-payload-range-20260401.json",
            75,
            "maximum_payload",
            "integer",
            "kg",
            "MASY (kg)",
            seat_rows(TCE_5, TCE_7, "455", "492", "594", "634", "455-492 / 594-634"),
        ),
        write_spec(
            "jogger-page6-hybrid155-automatic-maximum-payload-range-20260401.json",
            81,
            "maximum_payload",
            "integer",
            "kg",
            "MASY (kg)",
            seat_rows(HYBRID_5, HYBRID_7, "457", "471", "595", "612", "457-471 / 595-612"),
        ),
        write_spec(
            "jogger-page6-hybrid155-automatic-acceleration-0-100-range-20260401.json",
            87,
            "acceleration_0_100",
            "decimal",
            "s",
            "OSIĄGI",
            [(code, "8.9", "9", "8,9-9,0", None) for code in HYBRID],
        ),
        write_spec(
            "jogger-page6-ecog120-manual-max-power-rpm-range-20260401.json",
            93,
            "max_power_rpm",
            "integer",
            "rpm",
            "SILNIKI",
            fuel_rows(
                MANUAL,
                [
                    ("lpg", "4500", "5000", "LPG: 90 (122) przy 4 500 - 5 000"),
                    ("petrol", "4500", "5750", "Ben: 84 (114) przy 4 500 - 5 750"),
                ],
            ),
        ),
        write_spec(
            "jogger-page6-ecog120-manual-max-torque-rpm-range-20260401.json",
            105,
            "max_torque_rpm",
            "integer",
            "rpm",
            "SILNIKI",
            fuel_rows(
                MANUAL,
                [
                    ("lpg", "1750", "3750", "LPG: 197 przy 1 750 - 3 750"),
                    ("petrol", "2000", "4000", "Ben: 190 przy 2 000 - 4 000"),
                ],
            ),
        ),
        write_spec(
            "jogger-page6-ecog120-automatic-max-power-rpm-range-20260401.json",
            117,
            "max_power_rpm",
            "integer",
            "rpm",
            "SILNIKI",
            fuel_rows(
                AUTOMATIC,
                [
                    ("lpg", "4500", "5000", "LPG: 90 (122) przy 4 500 - 5 000"),
                    ("petrol", "4500", "5750", "Ben: 84 (114) przy 4 500 - 5 750"),
                ],
            ),
        ),
        write_spec(
            "jogger-page6-ecog120-automatic-max-torque-rpm-range-20260401.json",
            125,
            "max_torque_rpm",
            "integer",
            "rpm",
            "SILNIKI",
            fuel_rows(
                AUTOMATIC,
                [
                    ("lpg", "1750", "3750", "LPG: 197 przy 1 750 - 3 750"),
                    ("petrol", "2000", "4000", "Ben: 190 przy 2 000 - 4 000"),
                ],
            ),
        ),
        write_spec(
            "jogger-page6-tce110-manual-max-power-rpm-range-20260401.json",
            133,
            "max_power_rpm",
            "integer",
            "rpm",
            "SILNIKI",
            [(code, "5000", "5250", "81 (110) przy 5 000- 5 250", "petrol") for code in TCE],
            "petrol",
        ),
        write_spec(
            "jogger-page6-tce110-manual-max-torque-rpm-range-20260401.json",
            139,
            "max_torque_rpm",
            "integer",
            "rpm",
            "SILNIKI",
            [(code, "2900", "3500", "200 przy 2 900 - 3 500", "petrol") for code in TCE],
            "petrol",
        ),
    ]


def write_tests() -> None:
    content = r'''from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from tools.import_configuration_values import _compact_text, extract_page_candidates

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPECS = ROOT / "data" / "imports" / "configuration_value_ranges"
PDF = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
SOURCE = "src_pl_jogger_price_my26_20260401"
EXPECTED_SHA = "a03bb2de2cdadd51223e7d1a50aee898729172f39953bf2bfc946613d6e30d7b"
SELECTED_NAMES = {
    "jogger-page6-ecog120-manual-maximum-payload-range-20260401.json",
    "jogger-page6-ecog120-automatic-maximum-payload-range-20260401.json",
    "jogger-page6-tce110-manual-maximum-payload-range-20260401.json",
    "jogger-page6-hybrid155-automatic-maximum-payload-range-20260401.json",
    "jogger-page6-hybrid155-automatic-acceleration-0-100-range-20260401.json",
    "jogger-page6-ecog120-manual-max-power-rpm-range-20260401.json",
    "jogger-page6-ecog120-manual-max-torque-rpm-range-20260401.json",
    "jogger-page6-ecog120-automatic-max-power-rpm-range-20260401.json",
    "jogger-page6-ecog120-automatic-max-torque-rpm-range-20260401.json",
    "jogger-page6-tce110-manual-max-power-rpm-range-20260401.json",
    "jogger-page6-tce110-manual-max-torque-rpm-range-20260401.json",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class JoggerPayloadPerformanceRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.configurations = {
            row["code"]: row
            for row in read_rows(MASTER / "configurations.csv")
            if row["code"].startswith("jogger_")
        }
        cls.ranges = read_rows(MASTER / "configuration_attribute_value_ranges.csv")
        cls.selected = [row for row in cls.ranges if 65 <= int(row["id"]) <= 144]
        cls.scalars = read_rows(MASTER / "configuration_attribute_values.csv")
        cls.specs = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in SPECS.glob("jogger-page6-*-range-20260401.json")
            if path.name in SELECTED_NAMES
        }

    def test_eleven_specs_materialize_contiguous_ids_65_to_144(self) -> None:
        self.assertEqual(set(self.specs), SELECTED_NAMES)
        self.assertEqual(sum(len(spec["rows"]) for spec in self.specs.values()), 80)
        self.assertEqual(len(self.selected), 80)
        self.assertEqual({int(row["id"]) for row in self.selected}, set(range(65, 145)))

    def test_payload_denominator_is_seat_qualified(self) -> None:
        expected = {
            ("Eco-G 120", "manual", "5", "453", "473"): 3,
            ("Eco-G 120", "manual", "7", "598", "619"): 3,
            ("Eco-G 120", "automatic", "5", "450", "459"): 2,
            ("Eco-G 120", "automatic", "7", "596", "606"): 2,
            ("TCe 110", "manual", "5", "455", "492"): 3,
            ("TCe 110", "manual", "7", "594", "634"): 3,
            ("hybrid 155", "automatic", "5", "457", "471"): 3,
            ("hybrid 155", "automatic", "7", "595", "612"): 3,
        }
        actual: Counter[tuple[str, str, str, str, str]] = Counter()
        for row in self.selected:
            if row["attribute_code"] != "maximum_payload":
                continue
            configuration = self.configurations[row["configuration_code"]]
            seats = "7" if "_7seat_" in row["configuration_code"] else "5"
            actual[(configuration["powertrain_label"], configuration["transmission_type"], seats, row["minimum_value"], row["maximum_value"])] += 1
        self.assertEqual(actual, Counter(expected))

    def test_hybrid_acceleration_range_is_preserved_without_endpoint_inference(self) -> None:
        rows = [row for row in self.selected if row["attribute_code"] == "acceleration_0_100"]
        self.assertEqual(len(rows), 6)
        self.assertEqual({(row["minimum_value"], row["maximum_value"], row["fuel_type_code"]) for row in rows}, {("8.9", "9", "")})
        self.assertEqual({row["configuration_code"] for row in rows}, {code for code, item in self.configurations.items() if item["powertrain_label"] == "hybrid 155"})

    def test_engine_speed_ranges_preserve_group_and_fuel_contexts(self) -> None:
        expected = {
            ("Eco-G 120", "manual", "max_power_rpm", "lpg", "4500", "5000"): 6,
            ("Eco-G 120", "manual", "max_power_rpm", "petrol", "4500", "5750"): 6,
            ("Eco-G 120", "manual", "max_torque_rpm", "lpg", "1750", "3750"): 6,
            ("Eco-G 120", "manual", "max_torque_rpm", "petrol", "2000", "4000"): 6,
            ("Eco-G 120", "automatic", "max_power_rpm", "lpg", "4500", "5000"): 4,
            ("Eco-G 120", "automatic", "max_power_rpm", "petrol", "4500", "5750"): 4,
            ("Eco-G 120", "automatic", "max_torque_rpm", "lpg", "1750", "3750"): 4,
            ("Eco-G 120", "automatic", "max_torque_rpm", "petrol", "2000", "4000"): 4,
            ("TCe 110", "manual", "max_power_rpm", "petrol", "5000", "5250"): 6,
            ("TCe 110", "manual", "max_torque_rpm", "petrol", "2900", "3500"): 6,
        }
        actual: Counter[tuple[str, str, str, str, str, str]] = Counter()
        for row in self.selected:
            if row["attribute_code"] not in {"max_power_rpm", "max_torque_rpm"}:
                continue
            configuration = self.configurations[row["configuration_code"]]
            actual[(configuration["powertrain_label"], configuration["transmission_type"], row["attribute_code"], row["fuel_type_code"], row["minimum_value"], row["maximum_value"])] += 1
        self.assertEqual(actual, Counter(expected))

    def test_all_selected_ranges_are_closed_dated_and_source_backed(self) -> None:
        self.assertTrue(all(row["lower_inclusive"] == "true" for row in self.selected))
        self.assertTrue(all(row["upper_inclusive"] == "true" for row in self.selected))
        self.assertEqual({row["observation_date"] for row in self.selected}, {"2026-04-01"})
        self.assertEqual({row["source_code"] for row in self.selected}, {SOURCE})
        self.assertEqual({row["attribute_code"] for row in self.selected}, {"maximum_payload", "acceleration_0_100", "max_power_rpm", "max_torque_rpm"})

    def test_prior_ranges_and_scalar_values_remain_unchanged(self) -> None:
        self.assertEqual(len(self.ranges), 144)
        self.assertEqual(len([row for row in self.ranges if int(row["id"]) <= 64]), 64)
        self.assertEqual(len(self.scalars), 1204)
        scalar_keys = {(row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"]) for row in self.scalars}
        selected_keys = {(row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"]) for row in self.selected}
        self.assertFalse(scalar_keys & selected_keys)

    def test_registered_pdf_hash_and_source_texts_are_verified(self) -> None:
        self.assertTrue(PDF.is_file())
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), EXPECTED_SHA)
        if shutil.which("pdftotext") is None:
            return
        pages = [_compact_text(text) for _, text in extract_page_candidates(PDF, 6)]
        source_texts = {row["source_text"] for spec in self.specs.values() for row in spec["rows"]}
        self.assertEqual(len(source_texts), 11)
        for text in source_texts:
            compact = _compact_text(text)
            self.assertTrue(any(compact in page for page in pages), text)

    def test_state_exposes_updated_range_denominators(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        baseline = state["baseline"]
        self.assertEqual(baseline["tests"], 536)
        self.assertEqual(baseline["rows"], 3989)
        self.assertEqual(baseline["configuration_values"], 1204)
        self.assertEqual(baseline["configuration_value_ranges"], 144)
        self.assertEqual(baseline["configuration_range_import_specs"], 19)


if __name__ == "__main__":
    unittest.main()
'''
    (ROOT / "tests" / "test_jogger_payload_performance_ranges.py").write_text(content, encoding="utf-8")


def update_state_and_review() -> None:
    state_path = ROOT / "project" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["reference_delivery"] = {
        "name": "Jogger Payload and Performance Range Selection",
        "pull_request": 125,
        "head_sha": "c4995a952f71b6dc07afd8948e877e67864a63a6",
        "quality_run": 565,
    }
    state["baseline"] = {
        "tests": 536,
        "csv_files": 37,
        "rows": 3989,
        "configuration_values": 1204,
        "configuration_import_specs": 71,
        "configuration_value_ranges": 144,
        "configuration_range_import_specs": 19,
        "availability_records": 1811,
        "attributes": 357,
        "attribute_categories": 30,
    }
    state["current_package"] = {
        "name": "Jogger Payload and Performance Range Modeling and Import",
        "status": "active",
        "goal": "Materialize 11 strict specifications and 80 closed page-6 payload, Hybrid acceleration and engine-speed ranges with IDs 65-144.",
    }
    state["next_package"] = {
        "name": "Jogger Remaining Page-6 Exact Measurement Review",
        "status": "planned",
        "goal": "Review the remaining cargo, LPG-capacity and hybrid-system exact measurements against their dedicated canonical attributes.",
    }
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    review = '''# Jogger Payload and Performance Range Modeling and Import

## Status

`IMPLEMENTING`

This package materializes the denominator selected in PR #125 through the canonical configuration-value range table. It does not change scalar observations.

## Denominator

Eleven strict specifications create 80 closed page-6 ranges with IDs `65-144`:

- 22 seat-qualified `maximum_payload` ranges;
- 6 Hybrid 155 `acceleration_0_100` ranges preserving `8.9-9.0 s` without endpoint-to-seat inference;
- 52 `max_power_rpm` and `max_torque_rpm` ranges with explicit LPG or petrol contexts.

## Preservation boundary

Range IDs `1-64` and all 1,204 scalar observations remain unchanged. Exact Hybrid combustion-engine and electric-motor RPM evidence is not remapped.

## Expected baseline

- 536 tests;
- 37 master CSV files and 3,989 rows;
- 1,204 scalar values and 71 scalar specifications;
- 144 range values and 19 range specifications;
- 1,811 availability records;
- 357 attributes in 30 categories.

## Next package

**Jogger Remaining Page-6 Exact Measurement Review** will review cargo, LPG-capacity and hybrid-system exact measurements.
'''
    (ROOT / "project" / "reviews" / "jogger-payload-performance-range-import.md").write_text(review, encoding="utf-8")


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    specs = create_specs()
    write_tests()
    update_state_and_review()
    for path in specs:
        run([
            sys.executable,
            "tools/dkb.py",
            "import-configuration-value-ranges",
            "--spec",
            str(path.relative_to(ROOT)),
            "--apply",
        ])
    run([sys.executable, "tools/dkb.py", "project-state", "--apply"])
    run([sys.executable, "tools/dkb.py", "documentation-baseline", "--apply"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
