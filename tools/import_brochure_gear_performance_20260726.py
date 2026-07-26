#!/usr/bin/env python3
"""Import exact selected-gear 80–120 km/h brochure observations."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

try:
    from import_configuration_values import (
        ImportSpec,
        apply_import,
        build_expected_rows,
        load_spec,
        verify_import,
    )
except ModuleNotFoundError:  # package import in tests
    from tools.import_configuration_values import (
        ImportSpec,
        apply_import,
        build_expected_rows,
        load_spec,
        verify_import,
    )

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_ROOT = ROOT / "data" / "imports" / "configuration_values"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"

SPEC_CONTRACTS = (
    (
        SPEC_ROOT / "sandero-brochure-elasticity-80-120-20260202.json",
        2119,
        16,
        "src_pl_sandero_brochure_20260202",
        "2026-02-02",
        {"4": 8, "5": 8},
    ),
    (
        SPEC_ROOT / "sandero-stepway-brochure-elasticity-80-120-20260202.json",
        2135,
        22,
        "src_pl_sandero_stepway_brochure_20260202",
        "2026-02-02",
        {"4": 10, "5": 6, "6": 6},
    ),
    (
        SPEC_ROOT / "jogger-brochure-elasticity-80-120-20251217.json",
        2157,
        32,
        "src_pl_jogger_brochure_20251217",
        "2025-12-17",
        {"4": 32},
    ),
)

SOURCE_CONTRACTS = {
    "src_pl_sandero_brochure_20260202": (
        "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
        "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
        "2026-02-02",
    ),
    "src_pl_sandero_stepway_brochure_20260202": (
        "PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf",
        "800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48",
        "2026-02-02",
    ),
    "src_pl_jogger_brochure_20251217": (
        "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf",
        "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6",
        "2025-12-17",
    ),
}

EXPECTED_SOURCE_COUNTS = {
    "src_pl_sandero_brochure_20260202": 16,
    "src_pl_sandero_stepway_brochure_20260202": 22,
    "src_pl_jogger_brochure_20251217": 32,
}
EXPECTED_FUEL_COUNTS = {"lpg": 30, "petrol": 40}
EXPECTED_GEAR_COUNTS = {"4": 50, "5": 14, "6": 6}
EXPECTED_MODEL_COUNTS = {"sandero": 16, "sandero_stepway": 22, "jogger": 32}


class ContractError(RuntimeError):
    """Raised when reviewed source or repository boundaries differ."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_specs() -> tuple[ImportSpec, ...]:
    specs: list[ImportSpec] = []
    for path, id_start, count, source_code, observation_date, gear_counts in SPEC_CONTRACTS:
        spec = load_spec(path)
        ensure(spec.id_start == id_start, f"unexpected id_start: {path}")
        ensure(spec.attribute_code == "elasticity_80_120", f"unexpected attribute: {path}")
        ensure(
            (spec.data_type, spec.unit, spec.status) == ("decimal", "s", "active"),
            f"unexpected attribute contract: {path}",
        )
        ensure(spec.observation_date == observation_date, f"unexpected date: {path}")
        ensure(spec.source_page in {17, 19}, f"unexpected source page: {path}")
        ensure(len(spec.rows) == count, f"unexpected row count: {path}")
        ensure({row.source_code for row in spec.rows} == {source_code}, f"source mismatch: {path}")
        ensure(Counter(row.gear_number for row in spec.rows) == Counter(gear_counts), f"gear scope differs: {path}")
        ensure(all(row.fuel_type_code in {"lpg", "petrol"} for row in spec.rows), f"fuel scope differs: {path}")
        specs.append(spec)
    ensure(sum(len(spec.rows) for spec in specs) == 70, "expected 70 observations")
    return tuple(specs)


def verify_sources() -> None:
    sources = {row.get("code", ""): row for row in read_rows(MASTER / "sources.csv")}
    for source_code, (relative_path, expected_hash, document_date) in SOURCE_CONTRACTS.items():
        source = sources.get(source_code)
        ensure(source is not None, f"missing source: {source_code}")
        ensure(source.get("source_type") == "brochure_pdf", f"source type differs: {source_code}")
        ensure(source.get("publisher") == "Dacia" and source.get("market") == "PL", f"source identity differs: {source_code}")
        ensure(source.get("status") == "active", f"source is not active: {source_code}")
        ensure(source.get("document_date") == document_date, f"source date differs: {source_code}")
        ensure(source.get("file_path") == relative_path, f"source path differs: {source_code}")
        ensure(source.get("sha256") == expected_hash, f"registered source hash differs: {source_code}")
        archived = ROOT / relative_path
        ensure(archived.is_file(), f"archived source missing: {relative_path}")
        ensure(file_sha256(archived) == expected_hash, f"archived source hash differs: {source_code}")


def expected_rows(specs: Iterable[ImportSpec]) -> tuple[dict[str, str], ...]:
    rows = tuple(row for spec in specs for row in build_expected_rows(ROOT, spec))
    ensure(len(rows) == 70, "expected 70 generated rows")
    ensure([int(row["id"]) for row in rows] == list(range(2119, 2189)), "value IDs are not contiguous")
    ensure(len({row["code"] for row in rows}) == 70, "generated value codes are not unique")
    ensure(Counter(row["source_code"] for row in rows) == Counter(EXPECTED_SOURCE_COUNTS), "source counts differ")
    ensure(Counter(row["fuel_type_code"] for row in rows) == Counter(EXPECTED_FUEL_COUNTS), "fuel counts differ")
    ensure(Counter(row["gear_number"] for row in rows) == Counter(EXPECTED_GEAR_COUNTS), "gear counts differ")
    return rows


def model_bucket(configuration_code: str) -> str:
    if configuration_code.startswith("sandero_stepway_"):
        return "sandero_stepway"
    if configuration_code.startswith("sandero_"):
        return "sandero"
    if configuration_code.startswith("jogger_"):
        return "jogger"
    raise ContractError(f"unexpected target model: {configuration_code}")


def verify_configurations(rows: Iterable[dict[str, str]]) -> None:
    configurations = {
        row.get("code", ""): row
        for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    target_codes = {row["configuration_code"] for row in rows}
    ensure(len(target_codes) == 31, "expected 31 exact configurations")
    ensure(Counter(model_bucket(row["configuration_code"]) for row in rows) == Counter(EXPECTED_MODEL_COUNTS), "model counts differ")

    for code in target_codes:
        configuration = configurations.get(code)
        ensure(configuration is not None, f"active configuration missing: {code}")
        if "_ecog120_" in code:
            ensure(configuration.get("powertrain_label") == "Eco-G 120", f"Eco-G powertrain differs: {code}")
        elif "_tce110_" in code:
            ensure(configuration.get("powertrain_label") == "TCe 110", f"TCe powertrain differs: {code}")
        elif "_hybrid155_" in code:
            ensure(configuration.get("powertrain_label") == "hybrid 155", f"hybrid powertrain differs: {code}")
        else:
            raise ContractError(f"unexpected target powertrain: {code}")
        expected_transmission = "automatic" if code.endswith("_automatic") else "manual"
        ensure(configuration.get("transmission_type") == expected_transmission, f"transmission differs: {code}")

    seat_values = {
        (row.get("configuration_code", ""), row.get("value", ""))
        for row in read_rows(VALUE_PATH)
        if row.get("attribute_code") == "number_of_seats"
    }
    for code in target_codes:
        if not code.startswith("jogger_"):
            continue
        expected_seats = "7" if "_7seat_" in code else "5"
        ensure((code, expected_seats) in seat_values, f"seat layout differs: {code}")


def verify_boundaries(rows: Iterable[dict[str, str]]) -> None:
    rows = tuple(rows)
    stepway_auto = [
        row for row in rows
        if row["configuration_code"].startswith("sandero_stepway_")
        and row["configuration_code"].endswith("_automatic")
    ]
    ensure(len(stepway_auto) == 4, "expected four Stepway automatic observations")
    ensure({row["gear_number"] for row in stepway_auto} == {"4"}, "unstated Stepway automatic gears were inferred")
    ensure(
        not any(
            row["configuration_code"].startswith(("sandero_iii_tce", "sandero_stepway_iii_tce"))
            for row in rows
        ),
        "unmodeled Sandero or Stepway TCe configuration was imported",
    )
    ensure(all(row["gear_number"] for row in rows), "gear-qualified import contains a blank gear")


def apply(specs: Iterable[ImportSpec]) -> None:
    for spec in specs:
        apply_import(ROOT, spec)


def check(specs: Iterable[ImportSpec]) -> None:
    for spec in specs:
        verify_import(ROOT, spec)
    rows = expected_rows(specs)
    verify_configurations(rows)
    verify_boundaries(rows)

    actual = [
        row for row in read_rows(VALUE_PATH)
        if row.get("attribute_code") == "elasticity_80_120"
        and row.get("source_code") in SOURCE_CONTRACTS
    ]
    ensure(len(actual) == 70, "master data does not contain exactly 70 reviewed observations")
    expected_by_code = {row["code"]: row for row in rows}
    ensure({row["code"]: row for row in actual} == expected_by_code, "master observations differ from reviewed specs")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    try:
        verify_sources()
        specs = load_specs()
        rows = expected_rows(specs)
        verify_configurations(rows)
        verify_boundaries(rows)
        if args.apply:
            apply(specs)
        check(specs)
    except (ContractError, OSError, ValueError) as exc:
        parser.error(str(exc))

    print("PASS: exact brochure selected-gear performance values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
