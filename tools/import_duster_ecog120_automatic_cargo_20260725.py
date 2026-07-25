#!/usr/bin/env python3
"""Import exact catalogue cargo values for Duster Eco-G 120 automatic."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
import unicodedata
from pathlib import Path
from typing import Iterable, Sequence

import import_configuration_values as value_importer

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SOURCE_CODE = "src_pl_duster_price_my26_20260703"
SOURCE_SHA256 = "40bb4f3db9019c500fcb4c759f5ad395aa3b35a68bb22aa74f031fefe09727f2"
SOURCE_DATE = "2026-07-03"
SOURCE_PAGE = 6
CONFIGURATION_CODES = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
ATTRIBUTE_VALUES = {
    "cargo_volume_without_spare_wheel_iso3832": "439",
    "maximum_cargo_volume_iso3832": "1373",
}
SPEC_PATHS = (
    ROOT
    / "data"
    / "imports"
    / "configuration_values"
    / "duster-page6-cargo-volume-without-spare-wheel-iso3832-20260703.json",
    ROOT
    / "data"
    / "imports"
    / "configuration_values"
    / "duster-page6-maximum-cargo-volume-iso3832-20260703.json",
)
SOURCE_CONFIGURATION_FIELDS = (
    "id",
    "source_code",
    "configuration_code",
    "relationship",
    "notes",
)
RELATIONSHIP = "catalogue_technical_data_for"


class ContractError(RuntimeError):
    """Raised when the catalogue cargo contract cannot be reproduced."""


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ContractError(f"missing CSV header: {path}")
        return list(reader)


def _require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    _ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def _write_rows_atomic(
    path: Path,
    fields: Sequence[str],
    rows: Iterable[dict[str, str]],
) -> None:
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _compact(text: str) -> str:
    translated = text.translate(str.maketrans({"ł": "l", "Ł": "L"}))
    decomposed = unicodedata.normalize("NFKD", translated)
    plain = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    return "".join(character for character in plain.casefold() if character.isalnum())


def _source_row() -> dict[str, str]:
    matches = [
        row
        for row in _read_rows(MASTER / "sources.csv")
        if row.get("code") == SOURCE_CODE
    ]
    _ensure(len(matches) == 1, "expected exactly one registered Duster MY26 source")
    row = matches[0]
    _ensure(row.get("status") == "active", "Duster MY26 source is not active")
    _ensure(row.get("publisher") == "Dacia", "unexpected source publisher")
    _ensure(row.get("market") == "PL", "unexpected source market")
    _ensure(row.get("document_date") == SOURCE_DATE, "unexpected source date")
    _ensure(row.get("sha256") == SOURCE_SHA256, "unexpected registered source hash")
    path = ROOT / row.get("file_path", "")
    _ensure(path.is_file(), f"registered source file is missing: {path}")
    _ensure(_file_sha256(path) == SOURCE_SHA256, "source PDF SHA-256 mismatch")
    return row


def _verify_source_page(path: Path) -> None:
    """Verify the immutable PDF and reviewed declarative page-6 evidence."""
    _ensure(path.is_file(), f"registered source file is missing: {path}")
    required_source_texts = {
        "Bez koła zapasowego 439",
        "Maksymalna pojemność bagażnika 1373",
    }
    declared_source_texts = {
        row.source_text
        for spec in _load_specs()
        for row in spec.rows
    }
    _ensure(
        required_source_texts <= declared_source_texts,
        "declarative page-6 cargo evidence is incomplete",
    )


def _verify_configurations() -> None:
    configurations = {
        row["code"]: row
        for row in _read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    for code in sorted(CONFIGURATION_CODES):
        row = configurations.get(code)
        _ensure(row is not None, f"active configuration missing: {code}")
        _ensure(row.get("powertrain_label") == "Eco-G 120 4x2", f"powertrain mismatch: {code}")
        _ensure(row.get("transmission_type") == "automatic", f"transmission mismatch: {code}")


def _expected_source_configuration_rows() -> list[dict[str, str]]:
    return [
        {
            "source_code": SOURCE_CODE,
            "configuration_code": code,
            "relationship": RELATIONSHIP,
            "notes": (
                "Official MY26 price-list matrix identifies the exact Eco-G 120 automatic "
                "configuration; page 6 supplies the ISO 3832 cargo values."
            ),
        }
        for code in sorted(CONFIGURATION_CODES)
    ]


def _owned_source_configuration_rows(
    rows: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code") in CONFIGURATION_CODES
        and row.get("relationship") == RELATIONSHIP
    ]


def _semantic(
    rows: Iterable[dict[str, str]],
    fields: Sequence[str],
) -> list[tuple[str, ...]]:
    payload_fields = [field for field in fields if field != "id"]
    return sorted(tuple(row.get(field, "") for field in payload_fields) for row in rows)


def _apply_source_configuration_rows() -> None:
    path = MASTER / "source_configurations.csv"
    _require_header(path, SOURCE_CONFIGURATION_FIELDS)
    rows = _read_rows(path)
    owned = _owned_source_configuration_rows(rows)
    retained = [row for row in rows if row not in owned]
    next_id = max((int(row["id"]) for row in retained), default=0) + 1
    generated = [
        {"id": str(next_id + offset), **row}
        for offset, row in enumerate(_expected_source_configuration_rows())
    ]
    _write_rows_atomic(path, SOURCE_CONFIGURATION_FIELDS, [*retained, *generated])


def _verify_source_configuration_rows() -> None:
    path = MASTER / "source_configurations.csv"
    _require_header(path, SOURCE_CONFIGURATION_FIELDS)
    actual = _owned_source_configuration_rows(_read_rows(path))
    expected = _expected_source_configuration_rows()
    _ensure(
        _semantic(actual, SOURCE_CONFIGURATION_FIELDS)
        == _semantic(expected, SOURCE_CONFIGURATION_FIELDS),
        "source-configuration relationships differ from the cargo contract",
    )


def _load_specs() -> tuple[value_importer.ImportSpec, ...]:
    specs = tuple(value_importer.load_spec(path) for path in SPEC_PATHS)
    _ensure(
        {spec.attribute_code for spec in specs} == set(ATTRIBUTE_VALUES),
        "cargo import-spec attribute coverage mismatch",
    )
    for spec in specs:
        _ensure(spec.observation_date == SOURCE_DATE, "cargo spec date mismatch")
        _ensure(spec.source_page == SOURCE_PAGE, "cargo spec page mismatch")
        _ensure(spec.fuel_type_code == "", "cargo spec must be fuel independent")
        _ensure(
            {row.configuration_code for row in spec.rows} == CONFIGURATION_CODES,
            f"cargo spec configuration coverage mismatch: {spec.path.name}",
        )
        _ensure(
            {row.source_code for row in spec.rows} == {SOURCE_CODE},
            f"cargo spec source mismatch: {spec.path.name}",
        )
        _ensure(
            {row.value for row in spec.rows} == {ATTRIBUTE_VALUES[spec.attribute_code]},
            f"cargo spec value mismatch: {spec.path.name}",
        )
    return specs


def _verify_no_petrol_co2() -> None:
    forbidden = [
        row
        for row in _read_rows(MASTER / "configuration_attribute_values.csv")
        if row.get("configuration_code") in CONFIGURATION_CODES
        and row.get("attribute_code") == "co2_emissions"
        and row.get("fuel_type_code") == "petrol"
    ]
    _ensure(
        not forbidden,
        "petrol CO2 must remain unimported because the catalogue does not split 123 g/km by fuel",
    )


def check() -> None:
    source = _source_row()
    _verify_source_page(ROOT / source["file_path"])
    _verify_configurations()
    _verify_source_configuration_rows()
    for spec in _load_specs():
        value_importer.verify_registered_sources(ROOT, spec, verify_text=False)
        value_importer.verify_import(ROOT, spec)
    _verify_no_petrol_co2()


def apply() -> None:
    source = _source_row()
    _verify_source_page(ROOT / source["file_path"])
    _verify_configurations()
    _apply_source_configuration_rows()
    for spec in _load_specs():
        value_importer.verify_registered_sources(ROOT, spec, verify_text=False)
        value_importer.apply_import(ROOT, spec)
    check()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        apply() if args.apply else check()
    except (
        ContractError,
        value_importer.ImportSpecError,
        OSError,
        csv.Error,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        return 1
    print("PASS: Duster Eco-G 120 automatic cargo and emissions-gap contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
