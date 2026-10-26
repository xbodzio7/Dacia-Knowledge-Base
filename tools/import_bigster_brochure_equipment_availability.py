#!/usr/bin/env python3
"""Import visually verified Bigster brochure equipment-matrix cells for 2025-12-10."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE = ROOT / "PDF" / "Broszury" / "DACIA BIGSTER broszura 20251210.pdf"
SOURCE_SHA256 = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
DATE = "2025-12-10"
SPEC = ROOT / "data" / "imports" / "bigster_brochure_equipment_availability_20251210.csv"
OUTPUT = MASTER / "configuration_attribute_availability.csv"
FIELDS = ("id", "code", "configuration_code", "attribute_code", "availability_status", "observation_date", "source_code", "notes")
SPEC_FIELDS = ("configuration_code", "attribute_code", "availability_status", "source_page", "source_label", "normalization_notes")
EXPECTED_CONFIGS = {
    "bigster_essential_mildhybridg140_4x2_manual",
    "bigster_expression_mildhybridg140_4x2_manual",
    "bigster_extreme_mildhybridg140_4x2_manual",
    "bigster_journey_mildhybridg140_4x2_manual",
    "bigster_essential_mildhybrid140_4x2_manual",
    "bigster_expression_mildhybrid140_4x2_manual",
    "bigster_extreme_mildhybrid140_4x2_manual",
    "bigster_journey_mildhybrid140_4x2_manual",
    "bigster_expression_hybrid155_4x2_automatic",
    "bigster_extreme_hybrid155_4x2_automatic",
    "bigster_journey_hybrid155_4x2_automatic",
    "bigster_expression_hybridg150_4x4_automatic",
    "bigster_extreme_hybridg150_4x4_automatic",
    "bigster_journey_hybridg150_4x4_automatic",
}
# Authored from rendered printed pages 21-22. The adaptive-cruise row is
# explicitly limited to Hybrid 155; other rows use their printed grade cells.
RULES = {
    "roof_rails": (21, "Fixed roof rails", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "not_available"}, False),
    "modular_roof_rails": (21, "Modular roof rails", {"essential": "not_available", "expression": "not_available", "journey": "not_available", "extreme": "standard"}, False),
    "privacy_glass": (21, "Rear tinted windows", {"essential": "not_available", "expression": "not_available", "journey": "standard", "extreme": "standard"}, False),
    "driver_seat_height_adjustment": (21, "Driver seat height adjustment", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "driver_seat_lumbar_adjustment": (21, "Driver lumbar adjustment", {"essential": "not_available", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "passenger_seat_height_adjustment": (21, "Passenger seat height adjustment", {"essential": "not_available", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "tyre_pressure_monitoring_system": (21, "Tyre pressure monitoring system", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "isofix_rear": (21, "ISOFIX on outer rear seats", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "cruise_control": (21, "Cruise control and limiter operated from steering wheel", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "speed_limiter": (21, "Cruise control and limiter operated from steering wheel", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "adaptive_cruise_control": (21, "Adaptive cruise control (Hybrid 155 only)", {"essential": "not_available", "expression": "not_available", "journey": "optional", "extreme": "optional"}, True),
    "rear_seat_easy_fold": (21, "Rear bench Easy Fold 40/20/40", {"essential": "not_available", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "side_mirrors_electric_adjustment": (22, "Heated electric mirrors", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "side_mirrors_heated": (22, "Heated electric mirrors", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "side_mirrors_folding": (22, "Electric-folding mirrors", {"essential": "not_available", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "front_windows_power": (22, "Front/rear one-touch windows", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "rear_windows_power": (22, "Front/rear one-touch windows", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "one_touch_windows": (22, "Front/rear one-touch windows", {"essential": "standard", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "manual_air_conditioning": (22, "Manual air conditioning", {"essential": "standard", "expression": "not_available", "journey": "not_available", "extreme": "not_available"}, False),
    "automatic_climate_control": (22, "Dual-zone automatic climate control with rear vents", {"essential": "not_available", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "dual_zone_climate_control": (22, "Dual-zone automatic climate control with rear vents", {"essential": "not_available", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "rear_air_vents": (22, "Dual-zone automatic climate control with rear vents", {"essential": "not_available", "expression": "standard", "journey": "standard", "extreme": "standard"}, False),
    "power_tailgate": (22, "Electric tailgate", {"essential": "not_available", "expression": "not_available", "journey": "standard", "extreme": "optional"}, False),
}


class ContractError(RuntimeError):
    """Raised when source or master data does not satisfy the import contract."""


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                raise ContractError(f"missing CSV header: {path}")
            return list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def require_header(path: Path, expected: tuple[str, ...]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream), None)
    if header != list(expected):
        raise ContractError(f"unexpected CSV header in {path}: {header!r}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def grade_for(configuration_code: str) -> str:
    for grade in ("essential", "expression", "journey", "extreme"):
        if configuration_code.startswith(f"bigster_{grade}_"):
            return grade
    raise ContractError(f"configuration has no exact brochure grade: {configuration_code}")


def expected_spec_rows() -> set[tuple[str, str, str, str, str]]:
    expected = set()
    for configuration_code in EXPECTED_CONFIGS:
        grade = grade_for(configuration_code)
        for attribute_code, (page, label, grade_states, hybrid155_only) in RULES.items():
            if hybrid155_only and "_hybrid155_" not in configuration_code:
                continue
            expected.add((configuration_code, attribute_code, grade_states[grade], str(page), label))
    if len(expected) != 311:
        raise ContractError(f"internal page-21/22 contract expected 311 cells, got {len(expected)}")
    return expected


def spec_records() -> list[dict[str, str]]:
    require_header(SPEC, SPEC_FIELDS)
    records = read_csv(SPEC)
    expected = expected_spec_rows()
    actual = {
        (row["configuration_code"], row["attribute_code"], row["availability_status"], row["source_page"], row["source_label"])
        for row in records
    }
    if len(records) != len(actual) or actual != expected:
        missing = len(expected - actual)
        extra = len(actual - expected)
        raise ContractError(f"brochure equipment spec differs from exact page-21/22 contract (missing={missing}, extra={extra}, rows={len(records)})")
    if any(not row["normalization_notes"].strip() for row in records):
        raise ContractError("one or more source-matrix cells lack evidence/normalization notes")
    return records


def generated_rows() -> list[dict[str, str]]:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError("Bigster brochure source SHA-256 mismatch")
    spec = spec_records()
    configurations = {row["code"]: row for row in read_csv(MASTER / "configurations.csv")}
    if any(code not in configurations or configurations[code].get("status") != "active" for code in EXPECTED_CONFIGS):
        raise ContractError("one or more exact Bigster configurations are missing or inactive")
    attributes = {row["code"]: row for row in read_csv(MASTER / "attributes.csv")}
    for attribute_code in RULES:
        attribute = attributes.get(attribute_code)
        if not attribute or attribute.get("status") != "active" or attribute.get("data_type") != "boolean":
            raise ContractError(f"attribute is missing, inactive or not boolean: {attribute_code}")
    links = {(row["source_code"], row["configuration_code"]) for row in read_csv(MASTER / "source_configurations.csv")}
    if any((SOURCE_CODE, code) not in links for code in EXPECTED_CONFIGS):
        raise ContractError("one or more exact source-to-configuration links are missing")

    result = []
    for row in spec:
        code = row["configuration_code"]
        note = (
            f"Official Bigster brochure, printed page {row['source_page']}: {row['source_label']}; "
            f"{row['availability_status']} marker in the exact {configurations[code]['version_code']} grade column. "
            f"{row['normalization_notes'].strip()}"
        )
        result.append({
            "code": f"{code}_{row['attribute_code']}_20251210",
            "configuration_code": code,
            "attribute_code": row["attribute_code"],
            "availability_status": row["availability_status"],
            "observation_date": DATE,
            "source_code": SOURCE_CODE,
            "notes": note,
        })
    return result


def semantic(rows: list[dict[str, str]]) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in FIELDS[1:]) for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    current = read_csv(OUTPUT)
    expected = generated_rows()
    actual = [
        row for row in current
        if row.get("source_code") == SOURCE_CODE and row.get("observation_date") == DATE
    ]
    expected_semantic = semantic(expected)
    actual_semantic = semantic(actual)
    if len(actual_semantic) != len(set(actual_semantic)):
        raise ContractError("duplicate source/date equipment observations exist")
    expected_set = set(expected_semantic)
    actual_set = set(actual_semantic)
    if not actual_set <= expected_set:
        raise ContractError("stored source/date equipment rows contain observations outside the exact brochure contract")
    if args.check:
        if actual_set != expected_set or len(actual) != len(expected):
            raise ContractError(f"stored brochure equipment observations differ from contract (expected={len(expected)}, actual={len(actual)})")
        print("Bigster brochure equipment availability: PASS (311 direct page-21/22 observations)")
        return 0
    if actual_set == expected_set and len(actual) == len(expected):
        print("Bigster brochure equipment observations already match the contract.")
        return 0
    missing_semantic = expected_set - actual_set
    missing = [row for row in expected if tuple(row.get(field, "") for field in FIELDS[1:]) in missing_semantic]
    maximum = max((int(row["id"]) for row in current), default=0)
    additions = [{"id": str(maximum + offset), **row} for offset, row in enumerate(missing, start=1)]
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(current + additions)
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Imported {len(additions)} missing direct Bigster brochure equipment observations.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, OSError, ValueError, KeyError) as exc:
        raise SystemExit(f"Bigster brochure equipment import failed: {exc}")
