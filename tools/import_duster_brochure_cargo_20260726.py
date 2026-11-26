#!/usr/bin/env python3
"""Import exact context-aware Duster brochure cargo values."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from catalog_completion_history import DUSTER_HYBRIDG150_CONFIGURATION_CODES

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = ROOT / "data" / "imports" / "configuration_cargo_values" / "duster-brochure-cargo-20251020.json"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
CONTEXT_PATH = MASTER / "configuration_cargo_volume_contexts.csv"
SOURCE_CONFIGURATION_PATH = MASTER / "source_configurations.csv"
SOURCE_CODE = "src_pl_duster_mini_brochure_20251020"
SOURCE_FILE = "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf"
SOURCE_SHA256 = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
RELATIONSHIP = "brochure_technical_data_for"
VALUE_FIELDS = ("id", "code", "configuration_code", "attribute_code", "fuel_type_code", "gear_number", "value", "observation_date", "source_code", "notes")
CONTEXT_FIELDS = ("id", "code", "configuration_attribute_value_code", "measurement_basis_code", "second_row_state_code", "third_row_state_code", "compartment_code", "spare_wheel_state_code", "tyre_repair_kit_state_code", "double_floor_state_code", "notes")
SOURCE_CONFIGURATION_FIELDS = ("id", "source_code", "configuration_code", "relationship", "notes")
CONTEXT_SPEC_FIELDS = CONTEXT_FIELDS[3:-1]
EXPECTED_GROUPS = {
    "eco_g_120_manual_4x2": ("Eco-G 120 4x2", "manual", 4, 4, 0, {"453", "1545", "513", "1632"}),
    "mild_hybrid_140_manual_4x2": ("mild hybrid 140 4x2", "manual", 3, 3, 3, {"517", "1609", "594", "1635", "474", "1566", "545", "1537"}),
    "hybrid_155_automatic_4x2": ("hybrid 155 4x2", "automatic", 3, 3, 3, {"430", "1545", "496", "1609", "349", "1415", "401", "1528"}),
}
FORBIDDEN_AUTOMATICS = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
DEFERRED_VALUES = {"348", "1414", "400", "1527", "456", "1548"}


class ContractError(RuntimeError):
    pass


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def write_rows_atomic(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1 and payload.get("kind") == "configuration_cargo_values", "unsupported cargo spec")
    ensure(payload.get("value_id_start") == 2055, "unexpected value id start")
    ensure(payload.get("context_id_start") == 224, "unexpected context id start")
    ensure(payload.get("source_configuration_id_start") == 207, "unexpected relationship id start")
    ensure(payload.get("observation_date") == "2025-10-20", "unexpected observation date")
    ensure(payload.get("source_page") == 20, "unexpected source page")
    ensure(payload.get("source_code") == SOURCE_CODE, "unexpected source code")
    ensure(payload.get("attribute_code") == "boot_capacity", "unexpected attribute")
    ensure(payload.get("attribute_contract") == {"data_type": "integer", "unit": "L", "status": "active"}, "unexpected attribute contract")
    groups = payload.get("groups")
    ensure(isinstance(groups, list) and len(groups) == 3, "expected three import groups")
    seen: set[str] = set()
    configurations: set[str] = set()
    for group in groups:
        ensure(isinstance(group, dict), "group must be an object")
        code = str(group.get("group_code", ""))
        expected = EXPECTED_GROUPS.get(code)
        ensure(expected is not None and code not in seen, f"invalid group: {code}")
        seen.add(code)
        powertrain, transmission, config_count, repair_count, spare_count, values = expected
        ensure(group.get("powertrain_label") == powertrain, f"powertrain mismatch: {code}")
        ensure(group.get("transmission_type") == transmission, f"transmission mismatch: {code}")
        configs = group.get("configurations")
        repair_configs = group.get("repair_kit_configurations")
        spare_configs = group.get("spare_wheel_configurations")
        repair_obs = group.get("repair_kit_observations")
        spare_obs = group.get("spare_wheel_observations")
        for label, value in (("configurations", configs), ("repair configs", repair_configs), ("spare configs", spare_configs), ("repair observations", repair_obs), ("spare observations", spare_obs)):
            ensure(isinstance(value, list), f"{code}.{label} must be a list")
        ensure(len(configs) == config_count and len(repair_configs) == repair_count and len(spare_configs) == spare_count, f"target count mismatch: {code}")
        ensure(set(repair_configs) <= set(configs) and set(spare_configs) <= set(configs), f"target outside group: {code}")
        ensure(len(repair_obs) == 4 and len(spare_obs) == (4 if spare_configs else 0), f"observation count mismatch: {code}")
        all_obs = [*repair_obs, *spare_obs]
        ensure({str(item.get("value", "")) for item in all_obs} == values, f"source values differ: {code}")
        for item in all_obs:
            ensure(set(item) == {"context_code", "value", "source_text", *CONTEXT_SPEC_FIELDS}, f"unexpected observation fields: {code}")
            ensure(str(item.get("source_text", "")).strip() != "", "empty source text")
            ensure(item.get("third_row_state_code") == "" and item.get("double_floor_state_code") == "", "unstated context inferred")
        overlap = configurations & set(configs)
        ensure(not overlap, f"configuration repeated: {sorted(overlap)}")
        configurations.update(str(item) for item in configs)
    ensure(seen == set(EXPECTED_GROUPS) and len(configurations) == 10, "import scope differs")
    deferred = payload.get("deferred_groups")
    ensure(isinstance(deferred, list) and len(deferred) == 3, "expected three deferrals")
    ensure(any(item.get("group_code") == "eco_g_120_automatic" for item in deferred), "automatic deferral missing")
    ensure(any(item.get("group_code") == "hybrid_g_150_4x4_unmodeled" for item in deferred), "4x4 deferral missing")
    ensure(any(item.get("group_code") == "generic_dimensions_page" for item in deferred), "generic dimensions deferral missing")
    return payload


def verify_source() -> None:
    sources = {row.get("code", ""): row for row in read_rows(MASTER / "sources.csv")}
    row = sources.get(SOURCE_CODE)
    ensure(row is not None and row.get("status") == "active", "active Duster brochure source missing")
    ensure(row.get("publisher") == "Dacia" and row.get("market") == "PL", "source identity mismatch")
    ensure(row.get("document_date") == "2025-10-20" and row.get("file_path") == SOURCE_FILE, "source metadata mismatch")
    ensure(row.get("sha256") == SOURCE_SHA256, "source registry hash mismatch")
    path = ROOT / SOURCE_FILE
    ensure(path.is_file() and file_sha256(path) == SOURCE_SHA256, "archived Duster PDF hash mismatch")


def entries(spec: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    result: list[tuple[str, Mapping[str, Any]]] = []
    for group in spec["groups"]:
        for code in group["repair_kit_configurations"]:
            result.extend((str(code), item) for item in group["repair_kit_observations"])
        for code in group["spare_wheel_configurations"]:
            result.extend((str(code), item) for item in group["spare_wheel_observations"])
    ensure(len(result) == 64, "expected 64 Duster cargo observations")
    return result


def configuration_codes(spec: Mapping[str, Any]) -> list[str]:
    codes = [str(code) for group in spec["groups"] for code in group["configurations"]]
    ensure(len(codes) == 10 and len(set(codes)) == 10, "expected ten configurations")
    return codes


def verify_configurations(spec: Mapping[str, Any]) -> None:
    rows = {row.get("code", ""): row for row in read_rows(MASTER / "configurations.csv") if row.get("status") == "active"}
    expected_counts = Counter()
    for group in spec["groups"]:
        for code in group["configurations"]:
            row = rows.get(str(code))
            ensure(row is not None, f"active configuration missing: {code}")
            ensure(str(code).startswith("duster_iii_") and "_4x2_" in str(code), f"Duster drive mismatch: {code}")
            ensure(row.get("powertrain_label") == group["powertrain_label"], f"powertrain mismatch: {code}")
            ensure(row.get("transmission_type") == group["transmission_type"], f"transmission mismatch: {code}")
            expected_counts[str(code)] = 8 if code in group["spare_wheel_configurations"] else 4
    ensure(expected_counts == Counter(code for code, _ in entries(spec)), "configuration observation counts differ")
    ensure(FORBIDDEN_AUTOMATICS <= set(rows), "automatic deferral targets changed")
    later_duster_configurations = {
        code
        for code, row in rows.items()
        if code.startswith("duster_iii_")
        and row.get("powertrain_label") == "hybrid-G 150 4x4"
    }
    ensure(
        later_duster_configurations == DUSTER_HYBRIDG150_CONFIGURATION_CODES,
        "later exact Duster hybrid-G 150 catalogue scope differs",
    )
    ensure(
        set(configuration_codes(spec)).isdisjoint(DUSTER_HYBRIDG150_CONFIGURATION_CODES),
        "later Duster hybrid-G 150 catalogue identities entered the historical cargo package",
    )


def expected_rows(spec: Mapping[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    values: list[dict[str, str]] = []
    contexts: list[dict[str, str]] = []
    for offset, (configuration_code, observation) in enumerate(entries(spec)):
        value_id = int(spec["value_id_start"]) + offset
        context_id = int(spec["context_id_start"]) + offset
        value_code = f"{configuration_code}_boot_capacity_{observation['context_code']}_20251020"
        values.append({
            "id": str(value_id), "code": value_code, "configuration_code": configuration_code,
            "attribute_code": "boot_capacity", "fuel_type_code": "", "gear_number": "", "value": str(observation["value"]),
            "observation_date": "2025-10-20", "source_code": SOURCE_CODE,
            "notes": f"Source page 20, powertrain-specific cargo table: {observation['source_text']}",
        })
        context = {"id": str(context_id), "code": f"{value_code}_cargo_context", "configuration_attribute_value_code": value_code}
        context.update({field: str(observation[field]) for field in CONTEXT_SPEC_FIELDS})
        context["notes"] = "Exact cargo measurement and equipment context preserved from the source table."
        contexts.append(context)
    relationships = []
    for offset, code in enumerate(configuration_codes(spec)):
        relationships.append({
            "id": str(int(spec["source_configuration_id_start"]) + offset),
            "source_code": SOURCE_CODE,
            "configuration_code": code,
            "relationship": RELATIONSHIP,
            "notes": "The official Duster brochure powertrain-specific technical table documents this exact 4x2 powertrain and its cargo values; equipment context is preserved per observation.",
        })
    return values, contexts, relationships


def merge_owned(existing: list[dict[str, str]], expected: list[dict[str, str]], key: str, label: str) -> list[dict[str, str]]:
    index = {row.get(key, ""): row for row in existing}
    ensure(len(index) == len(existing), f"duplicate {label} key")
    additions = []
    for row in expected:
        current = index.get(row[key])
        if current is None:
            additions.append(row)
        else:
            ensure(current == row, f"existing {label} differs: {row[key]}")
    return [*existing, *additions]


def apply(spec: Mapping[str, Any]) -> None:
    require_header(VALUE_PATH, VALUE_FIELDS)
    require_header(CONTEXT_PATH, CONTEXT_FIELDS)
    require_header(SOURCE_CONFIGURATION_PATH, SOURCE_CONFIGURATION_FIELDS)
    expected_values, expected_contexts, expected_relationships = expected_rows(spec)
    values = merge_owned(read_rows(VALUE_PATH), expected_values, "code", "configuration value")
    contexts = merge_owned(read_rows(CONTEXT_PATH), expected_contexts, "code", "cargo context")
    relationships = read_rows(SOURCE_CONFIGURATION_PATH)
    pair_index = {(row.get("source_code", ""), row.get("configuration_code", "")): row for row in relationships}
    additions = []
    for row in expected_relationships:
        pair = (row["source_code"], row["configuration_code"])
        current = pair_index.get(pair)
        if current is None:
            additions.append(row)
        else:
            ensure(current == row, f"existing source relationship differs: {pair}")
    write_rows_atomic(VALUE_PATH, VALUE_FIELDS, values)
    write_rows_atomic(CONTEXT_PATH, CONTEXT_FIELDS, contexts)
    write_rows_atomic(SOURCE_CONFIGURATION_PATH, SOURCE_CONFIGURATION_FIELDS, [*relationships, *additions])


def check(spec: Mapping[str, Any]) -> None:
    expected_values, expected_contexts, expected_relationships = expected_rows(spec)
    values = {row.get("code", ""): row for row in read_rows(VALUE_PATH)}
    contexts = {row.get("code", ""): row for row in read_rows(CONTEXT_PATH)}
    relationships = {(row.get("source_code", ""), row.get("configuration_code", "")): row for row in read_rows(SOURCE_CONFIGURATION_PATH)}
    for row in expected_values:
        ensure(values.get(row["code"]) == row, f"missing or changed value: {row['code']}")
    for row in expected_contexts:
        ensure(contexts.get(row["code"]) == row, f"missing or changed context: {row['code']}")
    for row in expected_relationships:
        pair = (row["source_code"], row["configuration_code"])
        ensure(relationships.get(pair) == row, f"missing or changed relationship: {pair}")
    owned = [row for row in values.values() if row.get("source_code") == SOURCE_CODE and row.get("attribute_code") == "boot_capacity"]
    ensure(len(owned) == 64 and {int(row["id"]) for row in owned} == set(range(2055, 2119)), "owned value count or ids differ")
    owned_context_codes = {row["code"] for row in expected_contexts}
    ensure({int(contexts[code]["id"]) for code in owned_context_codes} == set(range(224, 288)), "context ids differ")
    ensure(not any(row.get("configuration_code") in FORBIDDEN_AUTOMATICS and row.get("source_code") == SOURCE_CODE for row in values.values()), "manual brochure projected to Eco-G automatic")
    ensure(not any(row.get("value") in DEFERRED_VALUES and row.get("source_code") == SOURCE_CODE for row in owned), "deferred generic or 4x4 value imported")
    counts = Counter(row["configuration_code"] for row in owned)
    ensure(sorted(counts.values()) == [4, 4, 4, 4, 8, 8, 8, 8, 8, 8], "per-configuration counts differ")
    print("PASS: Duster official brochure cargo import contract")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        spec = load_spec()
        verify_source()
        verify_configurations(spec)
        if args.apply:
            apply(spec)
        check(spec)
    except (ContractError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
