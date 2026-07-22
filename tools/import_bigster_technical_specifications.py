#!/usr/bin/env python3
"""Apply or verify the source-backed Bigster MY26 technical package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path
from typing import Iterable, Sequence

try:
    import import_configuration_value_ranges as range_import
    import import_configuration_values as value_import
except ModuleNotFoundError:  # package import in unit tests
    from tools import import_configuration_value_ranges as range_import
    from tools import import_configuration_values as value_import

SOURCE_CODE = "src_pl_bigster_price_my26_20260703"
SOURCE_SHA256 = "9528654fb3daf3767a2defbbc80e8a85abceecb11e04bb176aa0b76443be178a"
VALUE_PATTERN = "bigster-*-20260703.json"
RANGE_FILENAME = "bigster-page6-maximum-payload-range-20260703.json"
EXPECTED_VALUE_SPECS = 41
EXPECTED_VALUES = 552
EXPECTED_RANGES = 14
EXPECTED_VALUE_IDS = range(1205, 1757)
EXPECTED_RANGE_IDS = range(145, 159)
PAGE7_SECTION = "DACIA BIGSTER WYMIARY"
PAGE7_SOURCE_TEXT = {
    "4570",
    "1812",
    "2069",
    "1711/1706",
    "1573",
    "1547",
    "2702/2704",
    "854",
    "1015/1012",
    "220/219",
}


class BigsterTechnicalError(RuntimeError):
    """Raised when the package cannot be verified deterministically."""


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise BigsterTechnicalError(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def _source_path(repository: Path) -> Path:
    _, rows = _csv_rows(repository / "data/master/sources.csv")
    matches = [row for row in rows if row["code"] == SOURCE_CODE]
    _ensure(len(matches) == 1, f"expected one registered source {SOURCE_CODE}")
    source = matches[0]
    _ensure(source["sha256"] == SOURCE_SHA256, "registered source SHA-256 differs")
    path = repository / source["file_path"]
    _ensure(path.is_file(), f"registered source file is missing: {path}")
    _ensure(_sha256(path) == SOURCE_SHA256, "source PDF SHA-256 differs")
    return path


def _value_specs(repository: Path) -> list[tuple[Path, value_import.ImportSpec]]:
    directory = repository / "data/imports/configuration_values"
    paths = sorted(directory.glob(VALUE_PATTERN))
    _ensure(len(paths) == EXPECTED_VALUE_SPECS, f"expected {EXPECTED_VALUE_SPECS} Bigster value specs, found {len(paths)}")
    loaded = [(path, value_import.load_spec(path)) for path in paths]
    _ensure(all(spec.observation_date == "2026-07-03" for _, spec in loaded), "Bigster value specs use different observation dates")
    _ensure(all({row.source_code for row in spec.rows} == {SOURCE_CODE} for _, spec in loaded), "Bigster value spec references a different source")
    return loaded


def _range_spec(repository: Path) -> tuple[Path, range_import.RangeImportSpec]:
    path = repository / "data/imports/configuration_value_ranges" / RANGE_FILENAME
    _ensure(path.is_file(), f"missing range spec: {path}")
    spec = range_import.load_spec(path)
    _ensure(spec.observation_date == "2026-07-03", "Bigster range spec uses a different observation date")
    _ensure({row.source_code for row in spec.rows} == {SOURCE_CODE}, "Bigster range spec references a different source")
    return path, spec


def _verify_source_evidence(source_path: Path, value_specs: Iterable[tuple[Path, value_import.ImportSpec]], range_spec: range_import.RangeImportSpec) -> None:
    candidates = value_import.extract_page_candidates(source_path, 6)
    compact_candidates = [value_import._compact_text(text) for _, text in candidates]

    def page6_contains(section: str, source_text: str) -> bool:
        required_section = value_import._compact_text(section)
        required_text = value_import._compact_text(source_text)
        return any(required_section in text and required_text in text for text in compact_candidates)

    page7_texts: set[str] = set()
    for path, spec in value_specs:
        if spec.source_page == 6:
            for row in spec.rows:
                _ensure(page6_contains(spec.source_section, row.source_text), f"page 6 evidence missing for {path.name}: {row.source_text!r}")
        elif spec.source_page == 7:
            _ensure(spec.source_section == PAGE7_SECTION, f"unexpected page 7 section in {path.name}")
            page7_texts.update(row.source_text for row in spec.rows)
        else:
            raise BigsterTechnicalError(f"unexpected source page in {path.name}: {spec.source_page}")
    _ensure(page7_texts == PAGE7_SOURCE_TEXT, f"page 7 dimension evidence differs: {sorted(page7_texts)}")
    for row in range_spec.rows:
        _ensure(page6_contains(range_spec.source_section, row.source_text), f"page 6 range evidence missing: {row.source_text!r}")


def _index(rows: Iterable[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[tuple[str, str, str, str], dict[str, str]]]:
    by_id: dict[str, dict[str, str]] = {}
    by_code: dict[str, dict[str, str]] = {}
    by_semantic: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in rows:
        by_id[row["id"]] = row
        by_code[row["code"].casefold()] = row
        by_semantic[(row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"])] = row
    return by_id, by_code, by_semantic


def _synchronise(path: Path, fields: Sequence[str], current: list[dict[str, str]], expected: list[dict[str, str]], *, apply: bool) -> None:
    by_id, by_code, by_semantic = _index(current)
    missing: list[dict[str, str]] = []
    for row in expected:
        semantic = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["observation_date"])
        present = [candidate for candidate in (by_id.get(row["id"]), by_code.get(row["code"].casefold()), by_semantic.get(semantic)) if candidate is not None]
        if not present:
            missing.append(row)
        else:
            _ensure(all(candidate == row for candidate in present), f"existing row conflicts with package: {row['code']}")
    if not missing:
        return
    _ensure(apply, f"{len(missing)} package rows are missing from {path.name}")
    current_max = max((int(row["id"]) for row in current), default=0)
    first = int(missing[0]["id"])
    _ensure(first == current_max + 1, f"first missing ID must be {current_max + 1}, found {first}")
    _ensure([int(row["id"]) for row in missing] == list(range(first, first + len(missing))), "missing IDs are not a contiguous suffix")
    value_import._write_csv_atomic(path, fields, [*current, *missing])


def run(repository: Path, *, apply: bool) -> None:
    source_path = _source_path(repository)
    specs = _value_specs(repository)
    _, range_spec = _range_spec(repository)
    _verify_source_evidence(source_path, specs, range_spec)

    expected_values: list[dict[str, str]] = []
    for _, spec in specs:
        expected_values.extend(value_import.build_expected_rows(repository, spec))
    expected_values.sort(key=lambda row: int(row["id"]))
    _ensure(len(expected_values) == EXPECTED_VALUES, f"expected {EXPECTED_VALUES} values, found {len(expected_values)}")
    _ensure([int(row["id"]) for row in expected_values] == list(EXPECTED_VALUE_IDS), "Bigster value IDs are not contiguous")

    values_path = repository / "data/master/configuration_attribute_values.csv"
    value_fields, current_values = _csv_rows(values_path)
    _synchronise(values_path, value_fields, current_values, expected_values, apply=apply)

    expected_ranges = list(range_import.build_expected_rows(repository, range_spec))
    expected_ranges.sort(key=lambda row: int(row["id"]))
    _ensure(len(expected_ranges) == EXPECTED_RANGES, f"expected {EXPECTED_RANGES} ranges, found {len(expected_ranges)}")
    _ensure([int(row["id"]) for row in expected_ranges] == list(EXPECTED_RANGE_IDS), "Bigster range IDs are not contiguous")

    ranges_path = repository / "data/master/configuration_attribute_value_ranges.csv"
    range_fields, current_ranges = _csv_rows(ranges_path)
    _synchronise(ranges_path, range_fields, current_ranges, expected_ranges, apply=apply)

    # Re-read after apply and require every exact row to be present.
    _, final_values = _csv_rows(values_path)
    _, final_ranges = _csv_rows(ranges_path)
    final_value_ids = {row["id"] for row in final_values}
    final_range_ids = {row["id"] for row in final_ranges}
    _ensure({row["id"] for row in expected_values} <= final_value_ids, "Bigster values remain missing after apply")
    _ensure({row["id"] for row in expected_ranges} <= final_range_ids, "Bigster ranges remain missing after apply")

    print("Bigster technical specifications: PASS")
    print(f"Value specs: {len(specs)}; values: {len(expected_values)}")
    print(f"Range specs: 1; ranges: {len(expected_ranges)}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--repository", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repository = args.repository.expanduser().resolve() if args.repository else Path(__file__).resolve().parents[1]
    try:
        run(repository, apply=args.apply)
        return 0
    except (BigsterTechnicalError, value_import.ImportSpecError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
