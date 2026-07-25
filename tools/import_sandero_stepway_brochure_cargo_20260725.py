#!/usr/bin/env python3
"""Import exact context-aware Sandero and Stepway brochure cargo values."""

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
    / "sandero-stepway-brochure-cargo-20260202.json"
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
SOURCE_CONTRACTS = {
    "src_pl_sandero_brochure_20260202": {
        "model_prefix": "sandero_iii_",
        "model_code": "sandero_iii",
        "file_path": "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
        "sha256": "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
    },
    "src_pl_sandero_stepway_brochure_20260202": {
        "model_prefix": "sandero_stepway_iii_",
        "model_code": "sandero_stepway_iii",
        "file_path": "PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf",
        "sha256": "800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48",
    },
}
EXPECTED_VALUES = {
    "minimum_vda_iso3832": "328",
    "minimum_ordinary_litre": "410",
    "maximum_vda_iso3832": "1108",
    "maximum_ordinary_litre": "1455",
    "underfloor_vda_iso3832": "78",
}


class ContractError(RuntimeError):
    """Raised when the reviewed brochure import contract cannot be reproduced."""


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
    _ensure(payload.get("value_id_start") == 1832, "unexpected value id start")
    _ensure(payload.get("context_id_start") == 1, "unexpected context id start")
    _ensure(payload.get("observation_date") == "2026-02-02", "unexpected date")
    _ensure(payload.get("source_page") == 20, "unexpected source page")
    _ensure(payload.get("attribute_code") == "boot_capacity", "unexpected attribute")
    _ensure(
        payload.get("attribute_contract")
        == {"data_type": "integer", "unit": "L", "status": "active"},
        "unexpected boot_capacity contract",
    )
    configurations = payload.get("configurations")
    observations = payload.get("observations")
    _ensure(isinstance(configurations, list), "configurations must be a list")
    _ensure(len(configurations) == 9, "expected nine Sandero configurations")
    _ensure(isinstance(observations, list), "observations must be a list")
    _ensure(len(observations) == 5, "expected five cargo observations")
    _ensure(
        {item.get("context_code"): item.get("value") for item in observations}
        == EXPECTED_VALUES,
        "cargo values differ from reviewed page-20 evidence",
    )
    _ensure(
        {item.get("source_code") for item in configurations}
        == set(SOURCE_CONTRACTS),
        "source coverage mismatch",
    )
    for item in observations:
        _ensure(
            set(item)
            == {"context_code", "value", "source_text", *CONTEXT_FIELDS_FROM_SPEC},
            f"unexpected observation fields: {sorted(item)}",
        )
        _ensure(str(item.get("source_text", "")).strip() != "", "empty source text")
    return payload


def _source_rows() -> dict[str, dict[str, str]]:
    sources = {row.get("code", ""): row for row in _read_rows(MASTER / "sources.csv")}
    selected: dict[str, dict[str, str]] = {}
    for code, contract in SOURCE_CONTRACTS.items():
        row = sources.get(code)
        _ensure(row is not None, f"registered source missing: {code}")
        _ensure(row.get("status") == "active", f"source not active: {code}")
        _ensure(row.get("publisher") == "Dacia", f"unexpected publisher: {code}")
        _ensure(row.get("market") == "PL", f"unexpected market: {code}")
        _ensure(row.get("document_date") == "2026-02-02", f"unexpected date: {code}")
        _ensure(row.get("file_path") == contract["file_path"], f"file path mismatch: {code}")
        _ensure(row.get("sha256") == contract["sha256"], f"hash registry mismatch: {code}")
        path = ROOT / contract["file_path"]
        _ensure(path.is_file(), f"registered brochure missing: {path}")
        _ensure(_file_sha256(path) == contract["sha256"], f"PDF hash mismatch: {code}")
        selected[code] = row
    return selected


def _configuration_pairs(spec: Mapping[str, Any]) -> list[tuple[str, str]]:
    result = [
        (str(item["configuration_code"]), str(item["source_code"]))
        for item in spec["configurations"]
    ]
    _ensure(len(result) == len(set(result)), "duplicate configuration/source pair")
    return result


def _verify_configurations(spec: Mapping[str, Any]) -> None:
    configurations = {
        row.get("code", ""): row
        for row in _read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    values = _read_rows(VALUE_PATH)
    seat_values = {
        row.get("configuration_code", ""): row.get("value", "")
        for row in values
        if row.get("attribute_code") == "number_of_seats"
        and row.get("fuel_type_code", "") == ""
    }
    for configuration_code, source_code in _configuration_pairs(spec):
        row = configurations.get(configuration_code)
        _ensure(row is not None, f"active configuration missing: {configuration_code}")
        contract = SOURCE_CONTRACTS[source_code]
        _ensure(
            configuration_code.startswith(contract["model_prefix"]),
            f"configuration/model mismatch: {configuration_code}",
        )
        _ensure(
            row.get("powertrain_label") == "Eco-G 120",
            f"unexpected powertrain: {configuration_code}",
        )
        _ensure(
            row.get("transmission_type") in {"manual", "automatic"},
            f"unexpected transmission: {configuration_code}",
        )
        seat_value = seat_values.get(configuration_code)
        _ensure(
            seat_value in {None, "5"},
            f"configuration is not five-seat: {configuration_code}",
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


def _slug(value: str) -> str:
    return value.replace("-", "").replace(" ", "_").lower()


def _expected_value_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    next_id = int(spec["value_id_start"])
    date_slug = str(spec["observation_date"]).replace("-", "")
    for configuration_code, source_code in _configuration_pairs(spec):
        for observation in spec["observations"]:
            context_code = str(observation["context_code"])
            code = f"{configuration_code}_boot_capacity_{context_code}_{date_slug}"
            rows.append(
                {
                    "id": str(next_id),
                    "code": code,
                    "configuration_code": configuration_code,
                    "attribute_code": "boot_capacity",
                    "fuel_type_code": "",
                    "value": str(observation["value"]),
                    "observation_date": str(spec["observation_date"]),
                    "source_code": source_code,
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
    values = _expected_value_rows(spec)
    observations_by_code = {
        str(item["context_code"]): item for item in spec["observations"]
    }
    rows: list[dict[str, str]] = []
    next_id = int(spec["context_id_start"])
    for value in values:
        context_code = value["code"].split("_boot_capacity_", 1)[1].rsplit("_20260202", 1)[0]
        observation = observations_by_code[context_code]
        row = {
            "id": str(next_id),
            "code": f"cargo_context_{value['code']}",
            "configuration_attribute_value_code": value["code"],
            **{
                field: str(observation[field])
                for field in CONTEXT_FIELDS_FROM_SPEC
            },
            "notes": (
                f"Official brochure page {spec['source_page']}; exact context for "
                f"{observation['source_text']}. Empty optional fields mean not stated."
            ),
        }
        rows.append(row)
        next_id += 1
    return rows


def _expected_source_configuration_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "source_code": source_code,
            "configuration_code": configuration_code,
            "relationship": RELATIONSHIP,
            "notes": (
                "The model-level official brochure lists the represented Eco-G 120 "
                "powertrain and gives one model-wide cargo table on page 20; the active "
                "configuration inherits five-seat layout from master data."
            ),
        }
        for configuration_code, source_code in _configuration_pairs(spec)
    ]


def _semantic(rows: Iterable[Mapping[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    payload = [field for field in fields if field != "id"]
    return sorted(tuple(str(row.get(field, "")) for field in payload) for row in rows)


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
    pairs = set(_configuration_pairs(spec))
    retained = [
        row
        for row in rows
        if not (
            (row.get("configuration_code", ""), row.get("source_code", "")) in pairs
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
    expected_source_configurations = _expected_source_configuration_rows(spec)

    actual_values = [
        row
        for row in _read_rows(VALUE_PATH)
        if row.get("code", "") in {item["code"] for item in expected_values}
    ]
    actual_contexts = [
        row
        for row in _read_rows(CONTEXT_PATH)
        if row.get("code", "") in {item["code"] for item in expected_contexts}
    ]
    pairs = set(_configuration_pairs(spec))
    actual_source_configurations = [
        row
        for row in _read_rows(SOURCE_CONFIGURATION_PATH)
        if (row.get("configuration_code", ""), row.get("source_code", "")) in pairs
        and row.get("relationship") == RELATIONSHIP
    ]
    _ensure(
        _semantic(actual_values, VALUE_FIELDS) == _semantic(expected_values, VALUE_FIELDS),
        "materialized cargo values differ from import contract",
    )
    _ensure(
        _semantic(actual_contexts, CONTEXT_FIELDS)
        == _semantic(expected_contexts, CONTEXT_FIELDS),
        "materialized cargo contexts differ from import contract",
    )
    _ensure(
        _semantic(actual_source_configurations, SOURCE_CONFIGURATION_FIELDS)
        == _semantic(expected_source_configurations, SOURCE_CONFIGURATION_FIELDS),
        "source-configuration relations differ from import contract",
    )
    _ensure(len(actual_values) == 45, "expected 45 cargo values")
    _ensure(len(actual_contexts) == 45, "expected 45 cargo contexts")


def _verify_non_inference(spec: Mapping[str, Any]) -> None:
    imported_codes = {row["code"] for row in _expected_value_rows(spec)}
    all_values = _read_rows(VALUE_PATH)
    legacy = [
        row
        for row in all_values
        if row.get("attribute_code") == "boot_capacity"
        and row.get("observation_date") == "2026-06-26"
        and row.get("configuration_code", "").startswith(
            ("sandero_iii_", "sandero_stepway_iii_")
        )
    ]
    _ensure(len(legacy) == 7, "legacy 2026-06-26 boot-capacity history changed")
    _ensure({row.get("value") for row in legacy} == {"410"}, "legacy 410 L values changed")
    contexts = _read_rows(CONTEXT_PATH)
    context_value_codes = {
        row.get("configuration_attribute_value_code", "") for row in contexts
    }
    _ensure(
        not any(row.get("code", "") in context_value_codes for row in legacy),
        "legacy contextless values must not be migrated",
    )
    _ensure(imported_codes <= context_value_codes, "new cargo values lack context")
    for row in contexts:
        if row.get("configuration_attribute_value_code", "") not in imported_codes:
            continue
        _ensure(row.get("spare_wheel_state_code", "") == "", "spare wheel inferred")
        _ensure(row.get("tyre_repair_kit_state_code", "") == "", "repair kit inferred")
        _ensure(row.get("double_floor_state_code", "") == "", "double floor inferred")


def check() -> None:
    spec = _load_spec()
    _source_rows()
    _verify_attribute(spec)
    _verify_configurations(spec)
    _verify_materialized(spec)
    _verify_non_inference(spec)


def apply() -> None:
    spec = _load_spec()
    _source_rows()
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
    print("PASS: Sandero and Stepway official brochure cargo import contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
