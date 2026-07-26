#!/usr/bin/env python3
"""Import exact context-aware Jogger brochure cargo values."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = (
    ROOT
    / "data"
    / "imports"
    / "configuration_cargo_values"
    / "jogger-brochure-cargo-20251217.json"
)
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
CONTEXT_PATH = MASTER / "configuration_cargo_volume_contexts.csv"
SOURCE_CONFIGURATION_PATH = MASTER / "source_configurations.csv"

VALUE_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "gear_number",
    "value",
    "observation_date",
    "source_code",
    "notes",
)
CONTEXT_FIELDS = (
    "id",
    "code",
    "configuration_attribute_value_code",
    "measurement_basis_code",
    "second_row_state_code",
    "third_row_state_code",
    "compartment_code",
    "spare_wheel_state_code",
    "tyre_repair_kit_state_code",
    "double_floor_state_code",
    "notes",
)
SOURCE_CONFIGURATION_FIELDS = (
    "id",
    "source_code",
    "configuration_code",
    "relationship",
    "notes",
)
CONTEXT_FIELDS_FROM_SPEC = CONTEXT_FIELDS[3:-1]
RELATIONSHIP = "brochure_technical_data_for"
SOURCE_CODE = "src_pl_jogger_brochure_20251217"
SOURCE_FILE = "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf"
SOURCE_SHA256 = "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6"
EXPECTED_LAYOUT_VALUES = {
    5: {
        "five_seat_minimum_vda_iso3832": "708",
        "five_seat_minimum_ordinary_litre": "829",
        "five_seat_maximum_vda_iso3832": "1819",
        "five_seat_maximum_ordinary_litre": "2094",
    },
    7: {
        "seven_seat_minimum_vda_iso3832": "160",
        "seven_seat_minimum_ordinary_litre": "212",
        "seven_seat_second_upright_third_folded_vda_iso3832": "565",
        "seven_seat_second_upright_third_folded_ordinary_litre": "699",
        "seven_seat_second_upright_third_removed_vda_iso3832": "696",
        "seven_seat_second_upright_third_removed_ordinary_litre": "820",
    },
}


class ContractError(RuntimeError):
    """Raised when the reviewed Jogger brochure contract cannot be reproduced."""


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def _require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    _ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def _write_rows_atomic(
    path: Path,
    fields: Sequence[str],
    rows: Iterable[Mapping[str, str]],
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


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    _ensure(isinstance(payload, dict), "cargo import spec must be an object")
    _ensure(payload.get("version") == 1, "unsupported cargo import spec version")
    _ensure(
        payload.get("kind") == "configuration_cargo_values",
        "unsupported cargo import spec kind",
    )
    _ensure(payload.get("value_id_start") == 1877, "unexpected value id start")
    _ensure(payload.get("context_id_start") == 46, "unexpected context id start")
    _ensure(payload.get("observation_date") == "2025-12-17", "unexpected date")
    _ensure(payload.get("source_page") == 22, "unexpected source page")
    _ensure(payload.get("source_code") == SOURCE_CODE, "unexpected source code")
    _ensure(payload.get("attribute_code") == "boot_capacity", "unexpected attribute")
    _ensure(
        payload.get("attribute_contract")
        == {"data_type": "integer", "unit": "L", "status": "active"},
        "unexpected boot_capacity contract",
    )

    layouts = payload.get("layouts")
    _ensure(isinstance(layouts, list), "layouts must be a list")
    _ensure(len(layouts) == 2, "expected five- and seven-seat layouts")
    by_seats: dict[int, Mapping[str, Any]] = {}
    all_configurations: list[str] = []
    all_context_codes: list[str] = []
    for raw_layout in layouts:
        _ensure(isinstance(raw_layout, dict), "layout must be an object")
        seat_count = raw_layout.get("seat_count")
        _ensure(seat_count in {5, 7}, f"unsupported seat count: {seat_count!r}")
        _ensure(seat_count not in by_seats, f"duplicate seat layout: {seat_count}")
        configurations = raw_layout.get("configurations")
        observations = raw_layout.get("observations")
        _ensure(isinstance(configurations, list), "layout configurations must be a list")
        _ensure(len(configurations) == 11, f"expected eleven {seat_count}-seat configurations")
        _ensure(all(isinstance(code, str) and code for code in configurations), "invalid configuration code")
        _ensure(isinstance(observations, list), "layout observations must be a list")
        expected_values = EXPECTED_LAYOUT_VALUES[seat_count]
        _ensure(
            {str(item.get("context_code")): str(item.get("value")) for item in observations}
            == expected_values,
            f"{seat_count}-seat values differ from reviewed page-22 evidence",
        )
        for observation in observations:
            _ensure(
                set(observation)
                == {"context_code", "value", "source_text", *CONTEXT_FIELDS_FROM_SPEC},
                f"unexpected observation fields: {sorted(observation)}",
            )
            _ensure(str(observation.get("source_text", "")).strip() != "", "empty source text")
            all_context_codes.append(str(observation["context_code"]))
        all_configurations.extend(str(code) for code in configurations)
        by_seats[int(seat_count)] = raw_layout

    _ensure(len(all_configurations) == len(set(all_configurations)), "duplicate configuration")
    _ensure(len(all_context_codes) == len(set(all_context_codes)), "duplicate context code")

    deferred = payload.get("deferred_observations")
    _ensure(isinstance(deferred, list) and len(deferred) == 1, "expected one deferred observation")
    deferred_text = str(deferred[0].get("source_text", ""))
    _ensure("1807" in deferred_text and "2085" in deferred_text, "deferred maximum pair changed")
    _ensure(str(deferred[0].get("reason", "")).strip() != "", "deferred reason missing")
    return payload


def _source_row() -> dict[str, str]:
    sources = {row.get("code", ""): row for row in _read_rows(MASTER / "sources.csv")}
    row = sources.get(SOURCE_CODE)
    _ensure(row is not None, f"registered source missing: {SOURCE_CODE}")
    _ensure(row.get("status") == "active", "Jogger brochure source is not active")
    _ensure(row.get("publisher") == "Dacia", "unexpected publisher")
    _ensure(row.get("market") == "PL", "unexpected market")
    _ensure(row.get("document_date") == "2025-12-17", "unexpected source date")
    _ensure(row.get("file_path") == SOURCE_FILE, "source file path mismatch")
    _ensure(row.get("sha256") == SOURCE_SHA256, "source hash registry mismatch")
    path = ROOT / SOURCE_FILE
    _ensure(path.is_file(), f"registered brochure missing: {path}")
    _ensure(_file_sha256(path) == SOURCE_SHA256, "archived Jogger PDF hash mismatch")
    return row


def _layout_entries(
    spec: Mapping[str, Any],
) -> list[tuple[int, str, Mapping[str, Any]]]:
    entries: list[tuple[int, str, Mapping[str, Any]]] = []
    for layout in spec["layouts"]:
        seat_count = int(layout["seat_count"])
        for configuration_code in layout["configurations"]:
            for observation in layout["observations"]:
                entries.append((seat_count, str(configuration_code), observation))
    _ensure(len(entries) == 110, "expected 110 Jogger cargo observations")
    return entries


def _configuration_codes(spec: Mapping[str, Any]) -> list[str]:
    result = [
        str(configuration_code)
        for layout in spec["layouts"]
        for configuration_code in layout["configurations"]
    ]
    _ensure(len(result) == 22 and len(result) == len(set(result)), "expected 22 configurations")
    return result


def _verify_configurations(spec: Mapping[str, Any]) -> None:
    configurations = {
        row.get("code", ""): row
        for row in _read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    seat_values = {
        row.get("configuration_code", ""): row.get("value", "")
        for row in _read_rows(VALUE_PATH)
        if row.get("attribute_code") == "number_of_seats"
        and row.get("fuel_type_code", "") == ""
    }
    allowed_powertrains = {"Eco-G 120", "TCe 110", "hybrid 155"}
    for layout in spec["layouts"]:
        seat_count = int(layout["seat_count"])
        marker = f"_{seat_count}seat_"
        for configuration_code in layout["configurations"]:
            row = configurations.get(configuration_code)
            _ensure(row is not None, f"active configuration missing: {configuration_code}")
            _ensure(str(configuration_code).startswith("jogger_"), f"not a Jogger: {configuration_code}")
            _ensure(marker in str(configuration_code), f"seat marker mismatch: {configuration_code}")
            _ensure(
                row.get("powertrain_label") in allowed_powertrains,
                f"unexpected powertrain: {configuration_code}",
            )
            _ensure(
                row.get("transmission_type") in {"manual", "automatic"},
                f"unexpected transmission: {configuration_code}",
            )
            _ensure(
                seat_values.get(str(configuration_code)) == str(seat_count),
                f"seat-count evidence mismatch: {configuration_code}",
            )


def _verify_attribute(spec: Mapping[str, Any]) -> None:
    matches = [
        row
        for row in _read_rows(MASTER / "attributes.csv")
        if row.get("code") == spec["attribute_code"]
    ]
    _ensure(len(matches) == 1, "expected one boot_capacity attribute")
    row = matches[0]
    contract = spec["attribute_contract"]
    _ensure(
        {key: row.get(key, "") for key in contract} == contract,
        "boot_capacity attribute contract differs",
    )


def _expected_value_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    next_id = int(spec["value_id_start"])
    date_slug = str(spec["observation_date"]).replace("-", "")
    for _seat_count, configuration_code, observation in _layout_entries(spec):
        context_code = str(observation["context_code"])
        code = f"{configuration_code}_boot_capacity_{context_code}_{date_slug}"
        rows.append(
            {
                "id": str(next_id),
                "code": code,
                "configuration_code": configuration_code,
                "attribute_code": "boot_capacity",
                "fuel_type_code": "",
                "gear_number": "",
                "value": str(observation["value"]),
                "observation_date": str(spec["observation_date"]),
                "source_code": SOURCE_CODE,
                "notes": (
                    f"Source page {spec['source_page']}, section {spec['source_section']}: "
                    f"{observation['source_text']}. Context is stored in "
                    "configuration_cargo_volume_contexts.csv."
                ),
            }
        )
        next_id += 1
    return rows


def _expected_context_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    next_id = int(spec["context_id_start"])
    values = _expected_value_rows(spec)
    entries = _layout_entries(spec)
    _ensure(len(values) == len(entries), "value/context generation mismatch")
    for value, (_seat_count, _configuration_code, observation) in zip(values, entries):
        rows.append(
            {
                "id": str(next_id),
                "code": f"cargo_context_{value['code']}",
                "configuration_attribute_value_code": value["code"],
                **{
                    field: str(observation[field])
                    for field in CONTEXT_FIELDS_FROM_SPEC
                },
                "notes": (
                    f"Official Jogger brochure page {spec['source_page']}; exact context "
                    f"for {observation['source_text']}. Empty optional fields mean not stated."
                ),
            }
        )
        next_id += 1
    return rows


def _expected_source_configuration_rows(
    spec: Mapping[str, Any],
) -> list[dict[str, str]]:
    return [
        {
            "source_code": SOURCE_CODE,
            "configuration_code": configuration_code,
            "relationship": RELATIONSHIP,
            "notes": (
                "The official model brochure lists five- and seven-seat Jogger variants "
                "and gives the corresponding cargo table on page 22. The exact seat count "
                "is verified against configuration-level master data."
            ),
        }
        for configuration_code in _configuration_codes(spec)
    ]


def _semantic(
    rows: Iterable[Mapping[str, str]],
    fields: Sequence[str],
) -> list[tuple[str, ...]]:
    payload = [field for field in fields if field != "id"]
    return sorted(
        tuple(str(row.get(field, "")) for field in payload)
        for row in rows
    )


def _apply_owned_rows(
    path: Path,
    fields: Sequence[str],
    expected: list[dict[str, str]],
    owned_codes: set[str],
) -> None:
    _require_header(path, fields)
    existing = _read_rows(path)
    retained = [row for row in existing if row.get("code", "") not in owned_codes]
    expected_ids = {row["id"] for row in expected}
    _ensure(
        not any(row.get("id", "") in expected_ids for row in retained),
        f"reserved ID collision in {path}",
    )
    _write_rows_atomic(path, fields, [*retained, *expected])


def _apply_source_configurations(spec: Mapping[str, Any]) -> None:
    _require_header(SOURCE_CONFIGURATION_PATH, SOURCE_CONFIGURATION_FIELDS)
    rows = _read_rows(SOURCE_CONFIGURATION_PATH)
    configurations = set(_configuration_codes(spec))
    retained = [
        row
        for row in rows
        if not (
            row.get("source_code") == SOURCE_CODE
            and row.get("configuration_code") in configurations
            and row.get("relationship") == RELATIONSHIP
        )
    ]
    expected = _expected_source_configuration_rows(spec)
    next_id = max((int(row["id"]) for row in retained), default=0) + 1
    generated = [
        {"id": str(next_id + offset), **row}
        for offset, row in enumerate(expected)
    ]
    _write_rows_atomic(
        SOURCE_CONFIGURATION_PATH,
        SOURCE_CONFIGURATION_FIELDS,
        [*retained, *generated],
    )


def _verify_materialized(spec: Mapping[str, Any]) -> None:
    expected_values = _expected_value_rows(spec)
    expected_contexts = _expected_context_rows(spec)
    expected_relations = _expected_source_configuration_rows(spec)
    value_codes = {row["code"] for row in expected_values}
    context_codes = {row["code"] for row in expected_contexts}
    configurations = set(_configuration_codes(spec))

    actual_values = [
        row for row in _read_rows(VALUE_PATH)
        if row.get("code", "") in value_codes
    ]
    actual_contexts = [
        row for row in _read_rows(CONTEXT_PATH)
        if row.get("code", "") in context_codes
    ]
    actual_relations = [
        row for row in _read_rows(SOURCE_CONFIGURATION_PATH)
        if row.get("source_code") == SOURCE_CODE
        and row.get("configuration_code") in configurations
        and row.get("relationship") == RELATIONSHIP
    ]

    _ensure(
        _semantic(actual_values, VALUE_FIELDS) == _semantic(expected_values, VALUE_FIELDS),
        "materialized Jogger cargo values differ from import contract",
    )
    _ensure(
        _semantic(actual_contexts, CONTEXT_FIELDS)
        == _semantic(expected_contexts, CONTEXT_FIELDS),
        "materialized Jogger cargo contexts differ from import contract",
    )
    _ensure(
        _semantic(actual_relations, SOURCE_CONFIGURATION_FIELDS)
        == _semantic(expected_relations, SOURCE_CONFIGURATION_FIELDS),
        "Jogger source-configuration relations differ from import contract",
    )
    _ensure(len(actual_values) == 110, "expected 110 Jogger cargo values")
    _ensure(len(actual_contexts) == 110, "expected 110 Jogger cargo contexts")


def _verify_non_inference(spec: Mapping[str, Any]) -> None:
    expected_values = _expected_value_rows(spec)
    imported_codes = {row["code"] for row in expected_values}
    imported_rows = [
        row for row in _read_rows(VALUE_PATH)
        if row.get("code", "") in imported_codes
    ]
    _ensure(
        not {row.get("value", "") for row in imported_rows} & {"1807", "2085"},
        "ambiguous seven-seat maximum was imported",
    )

    contexts = {
        row.get("configuration_attribute_value_code", ""): row
        for row in _read_rows(CONTEXT_PATH)
        if row.get("configuration_attribute_value_code", "") in imported_codes
    }
    _ensure(set(contexts) == imported_codes, "new Jogger cargo values lack context")
    for row in contexts.values():
        _ensure(row.get("spare_wheel_state_code", "") == "", "spare wheel inferred")
        _ensure(row.get("tyre_repair_kit_state_code", "") == "", "repair kit inferred")
        _ensure(row.get("double_floor_state_code", "") == "", "double floor inferred")

    five_codes = {
        configuration_code
        for layout in spec["layouts"]
        if int(layout["seat_count"]) == 5
        for configuration_code in layout["configurations"]
    }
    seven_codes = set(_configuration_codes(spec)) - five_codes
    for value in imported_rows:
        context = contexts[value["code"]]
        if value["configuration_code"] in five_codes:
            _ensure(context.get("third_row_state_code", "") == "", "third row inferred for five-seat layout")
        elif value["configuration_code"] in seven_codes:
            _ensure(
                context.get("third_row_state_code", "") in {"upright", "folded", "removed"},
                "seven-seat third-row state missing",
            )


def check() -> None:
    spec = _load_spec()
    _source_row()
    _verify_attribute(spec)
    _verify_configurations(spec)
    _verify_materialized(spec)
    _verify_non_inference(spec)


def apply() -> None:
    spec = _load_spec()
    _source_row()
    _verify_attribute(spec)
    _verify_configurations(spec)
    expected_values = _expected_value_rows(spec)
    expected_contexts = _expected_context_rows(spec)
    _apply_owned_rows(
        VALUE_PATH,
        VALUE_FIELDS,
        expected_values,
        {row["code"] for row in expected_values},
    )
    _apply_owned_rows(
        CONTEXT_PATH,
        CONTEXT_FIELDS,
        expected_contexts,
        {row["code"] for row in expected_contexts},
    )
    _apply_source_configurations(spec)
    check()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        apply() if args.apply else check()
    except (ContractError, OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        return 1
    print("PASS: Jogger official brochure cargo import contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
