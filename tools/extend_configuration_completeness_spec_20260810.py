#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data/reporting/configuration_completeness.json"
MASTER = ROOT / "data/master"
EFFECTIVE_FROM = "2026-08-09"

EXPECTED_NEW_TECHNICAL_SLOTS = tuple(
    (code, "")
    for code in (
        "body_style_source_stated",
        "cargo_floor_width",
        "centre_console_variant",
        "drive_layout",
        "factory_speed_limit",
        "fuel_type",
        "gearbox_source_description",
        "gearbox_type",
        "ground_clearance_laden",
        "ground_clearance_unladen",
        "height_with_tailgate_open",
        "homologation_procedure_code",
        "homologation_protocol",
        "interface_language_source_stated",
        "key_count",
        "minimum_kerb_weight",
        "overall_height_source_stated",
        "rear_windows_power",
        "reversing_lights_count",
        "roof_height_with_rails",
        "roof_type_source_stated",
        "side_mirrors_electric_adjustment",
        "speaker_count",
        "steering_wheel_material",
        "technical_type_code",
    )
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_spec() -> dict[str, Any]:
    value = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("version") != 1:
        raise RuntimeError("unexpected configuration completeness spec")
    return value


def slot(item: dict[str, Any]) -> tuple[str, str]:
    return (
        str(item.get("attribute_code", "")),
        str(item.get("fuel_type_code", "")),
    )


def observed_slots(spec: dict[str, Any]) -> set[tuple[str, str]]:
    configurations = {
        str(item.get("configuration_code", ""))
        for item in spec.get("configurations", [])
        if item.get("configuration_code")
    }
    observed: set[tuple[str, str]] = set()
    for name in (
        "configuration_attribute_values.csv",
        "configuration_value_ranges.csv",
    ):
        path = MASTER / name
        if not path.is_file():
            continue
        for row in read_csv(path):
            if row.get("configuration_code", "") not in configurations:
                continue
            attribute = row.get("attribute_code", "").strip()
            if attribute:
                observed.add((attribute, row.get("fuel_type_code", "").strip()))
    return observed


def verify(spec: dict[str, Any]) -> None:
    slots = [slot(item) for item in spec.get("technical_slots", [])]
    if any(not item[0] for item in slots) or len(slots) != len(set(slots)):
        raise RuntimeError("invalid or duplicate technical slot in completeness spec")

    expected = set(EXPECTED_NEW_TECHNICAL_SLOTS)
    missing = sorted(expected - set(slots))
    if missing:
        raise RuntimeError(f"expected configurator technical slots missing from spec: {missing}")

    wrong_effective_from = sorted(
        slot(item)
        for item in spec.get("technical_slots", [])
        if slot(item) in expected
        and str(item.get("effective_from", "")) != EFFECTIVE_FROM
    )
    if wrong_effective_from:
        raise RuntimeError(
            "configurator technical slot effective_from differs: "
            f"{wrong_effective_from}"
        )

    active_attributes = {
        row.get("code", "")
        for row in read_csv(MASTER / "attributes.csv")
        if row.get("status") == "active"
    }
    inactive = sorted({item[0] for item in expected} - active_attributes)
    if inactive:
        raise RuntimeError(f"expected configurator attributes are not active: {inactive}")

    observed = observed_slots(spec)
    unobserved = sorted(expected - observed)
    if unobserved:
        raise RuntimeError(
            f"completeness extension lacks source-backed observations: {unobserved}"
        )
    unexpected = sorted(observed - set(slots))
    if unexpected:
        raise RuntimeError(
            f"observed technical slots remain absent from spec: {unexpected}"
        )


def apply() -> int:
    spec = read_spec()
    technical = list(spec.get("technical_slots", []))
    existing = {slot(item) for item in technical}
    additions = [item for item in EXPECTED_NEW_TECHNICAL_SLOTS if item not in existing]
    for attribute, fuel in additions:
        technical.append(
            {
                "attribute_code": attribute,
                "fuel_type_code": fuel,
                "effective_from": EFFECTIVE_FROM,
            }
        )
    technical.sort(
        key=lambda item: (
            str(item.get("attribute_code", "")),
            str(item.get("fuel_type_code", "")),
            str(item.get("gear_number", "")),
        )
    )
    spec["technical_slots"] = technical
    SPEC_PATH.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    verify(spec)
    return len(additions)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.apply:
        added = apply()
        print(f"Configuration completeness technical slots added: {added}")
    else:
        verify(read_spec())
        print("Configuration completeness configurator extension: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
