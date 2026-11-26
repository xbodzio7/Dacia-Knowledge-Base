#!/usr/bin/env python3
"""Import approved historical exterior dimensions from official brochure diagrams."""

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

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SPEC_PATH = ROOT / "data" / "imports" / "brochure_technical_values" / "generic-dimensions-20251020-20260202.json"
REVIEW_PATH = ROOT / "data" / "reporting" / "brochure_generic_dimensions_semantic_mapping_review.json"
VALUE_PATH = MASTER / "configuration_attribute_values.csv"
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
SOURCE_CONTRACTS = {
    "src_pl_sandero_brochure_20260202": {
        "date": "2026-02-02",
        "page": 20,
        "path": ROOT / "PDF" / "Broszury" / "DACIA SANDERO broszura 20260202.pdf",
        "sha256": "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
        "configurations": 4,
        "observations": 10,
        "values": 40,
    },
    "src_pl_jogger_brochure_20251217": {
        "date": "2025-12-17",
        "page": 22,
        "path": ROOT / "PDF" / "Broszury" / "DACIA JOGGER broszura 20251217.pdf",
        "sha256": "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6",
        "configurations": 22,
        "observations": 11,
        "values": 242,
    },
    "src_pl_duster_mini_brochure_20251020": {
        "date": "2025-10-20",
        "page": 24,
        "path": ROOT / "PDF" / "Broszury" / "DACIA DUSTER mini broszura 20251020.pdf",
        "sha256": "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8",
        "configurations": 10,
        "observations": 10,
        "values": 100,
    },
}
ATTRIBUTE_CODES = {
    "overall_length",
    "overall_width",
    "overall_width_with_mirrors",
    "overall_height",
    "roof_height_with_rails",
    "wheelbase",
    "ground_clearance",
    "front_track",
    "rear_track",
    "front_overhang",
    "rear_overhang",
}
EXPECTED_EXCLUSIONS = {
    "duster_4x4_without_exact_source_relationship",
    "tailgate_open_heights",
    "interior_measurements",
    "seatback_angles",
    "cargo_context",
    "later_exact_sandero_values_remain_current",
}
EXPECTED_ATTRIBUTE_COUNTS = Counter(
    {
        "overall_length": 36,
        "overall_width": 36,
        "overall_width_with_mirrors": 36,
        "wheelbase": 36,
        "ground_clearance": 36,
        "front_track": 36,
        "rear_track": 36,
        "front_overhang": 36,
        "rear_overhang": 36,
        "overall_height": 26,
        "roof_height_with_rails": 32,
    }
)


class ImportContractError(RuntimeError):
    """Raised when the reviewed generic dimension import contract drifts."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ImportContractError(message)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
        return list(reader)


def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def write_rows_atomic(path: Path, fields: Sequence[str], values: Iterable[Mapping[str, str]]) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(values)
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


def mapping(items: Any) -> dict[str, int]:
    ensure(isinstance(items, list), "mapping must be a list")
    result: dict[str, int] = {}
    for item in items:
        ensure(isinstance(item, dict), "mapping item must be an object")
        code = str(item.get("attribute_code", ""))
        value = item.get("value")
        ensure(code and code not in result, f"duplicate or empty mapping attribute: {code}")
        ensure(isinstance(value, int) and value > 0, f"invalid mapping value: {code}")
        result[code] = value
    return result


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported spec version")
    ensure(payload.get("kind") == "brochure_generic_dimension_observations", "unexpected spec kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "review date differs")
    ensure(payload.get("mapping_review") == "data/reporting/brochure_generic_dimensions_semantic_mapping_review.json", "mapping review path differs")
    ensure(payload.get("value_id_start") == 2568, "value ID start differs")
    groups = payload.get("groups")
    ensure(isinstance(groups, list) and len(groups) == 3, "expected three import groups")
    ensure({str(group.get("source_code", "")) for group in groups if isinstance(group, dict)} == set(SOURCE_CONTRACTS), "source group set differs")
    ensure(sum(len(group.get("configurations", [])) for group in groups) == 36, "configuration total differs")
    ensure(sum(len(group.get("configurations", [])) * len(group.get("observations", [])) for group in groups) == 382, "value total differs")
    for group in groups:
        ensure(isinstance(group, dict), "group must be an object")
        source = str(group.get("source_code", ""))
        contract = SOURCE_CONTRACTS[source]
        ensure(group.get("source_page") == contract["page"], f"source page differs: {source}")
        ensure(group.get("observation_date") == contract["date"], f"observation date differs: {source}")
        configurations = group.get("configurations")
        observations = group.get("observations")
        ensure(isinstance(configurations, list) and len(configurations) == contract["configurations"], f"configuration count differs: {source}")
        ensure(len(set(configurations)) == len(configurations), f"duplicate configuration: {source}")
        ensure(isinstance(observations, list) and len(observations) == contract["observations"], f"observation count differs: {source}")
        ensure({str(item.get("attribute_code", "")) for item in observations if isinstance(item, dict)} <= ATTRIBUTE_CODES, f"unknown attribute: {source}")
        for item in observations:
            ensure(isinstance(item, dict) and set(item) == {"attribute_code", "value", "source_text"}, f"observation fields differ: {source}")
            ensure(isinstance(item["value"], int) and int(item["value"]) > 0, f"invalid integer value: {source}")
            ensure(str(item["source_text"]).strip(), f"source text missing: {source}")
    exclusions = payload.get("excluded_evidence")
    ensure(isinstance(exclusions, list), "excluded evidence is missing")
    ensure({str(item.get("code", "")) for item in exclusions if isinstance(item, dict)} == EXPECTED_EXCLUSIONS, "exclusion set differs")
    return payload


def load_review() -> dict[str, Any]:
    payload = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    ensure(payload.get("kind") == "brochure_generic_dimensions_semantic_mapping_review", "unexpected mapping review kind")
    ensure(payload.get("status") == "complete", "mapping review is not complete")
    ensure(payload.get("import_plan", {}).get("scalar_values") == 382, "mapping review import total differs")
    return payload


def verify_sources() -> None:
    registry = {row["code"]: row for row in read_rows(MASTER / "sources.csv")}
    for source, contract in SOURCE_CONTRACTS.items():
        row = registry.get(source)
        ensure(row is not None and row.get("status") == "active", f"active source missing: {source}")
        ensure(row.get("source_type") == "brochure_pdf", f"source type differs: {source}")
        ensure(row.get("publisher") == "Dacia" and row.get("market") == "PL", f"source identity differs: {source}")
        ensure(row.get("document_date") == contract["date"], f"source date differs: {source}")
        path = contract["path"]
        ensure(path.is_file(), f"archived source missing: {source}")
        ensure(row.get("sha256") == contract["sha256"], f"source registry hash differs: {source}")
        ensure(file_sha256(path) == contract["sha256"], f"archived source hash differs: {source}")


def verify_references(spec: Mapping[str, Any], review: Mapping[str, Any]) -> None:
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for code in ATTRIBUTE_CODES:
        row = attributes.get(code)
        ensure(row is not None and row.get("status") == "active", f"active attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit")) == ("integer", "mm"), f"attribute contract differs: {code}")

    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    relationships = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    seen: set[str] = set()
    for group in spec["groups"]:
        source = str(group["source_code"])
        for code in group["configurations"]:
            ensure(code not in seen, f"configuration appears in multiple groups: {code}")
            seen.add(code)
            row = configurations.get(str(code))
            ensure(row is not None and row.get("status") == "active", f"active configuration missing: {code}")
            ensure((source, str(code), "brochure_technical_data_for") in relationships, f"source relationship missing: {code}")
        if source == "src_pl_duster_mini_brochure_20251020":
            ensure(all("4x2" in configurations[str(code)].get("powertrain_label", "") for code in group["configurations"]), "Duster target is not 4x2")

    review_sources = {str(item["source_code"]): item for item in review["sources"]}
    spec_sources = {str(item["source_code"]): item for item in spec["groups"]}
    ensure(set(review_sources) == set(spec_sources), "review/spec source set differs")
    ensure(mapping(review_sources["src_pl_sandero_brochure_20260202"]["mappings"]) == mapping(spec_sources["src_pl_sandero_brochure_20260202"]["observations"]), "Sandero review/spec mapping differs")
    ensure(mapping(review_sources["src_pl_jogger_brochure_20251217"]["mappings"]) == mapping(spec_sources["src_pl_jogger_brochure_20251217"]["observations"]), "Jogger review/spec mapping differs")
    ensure(mapping(review_sources["src_pl_duster_mini_brochure_20251020"]["eligible_4x2_mappings"]) == mapping(spec_sources["src_pl_duster_mini_brochure_20251020"]["observations"]), "Duster review/spec mapping differs")


def expected_rows(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for group in spec["groups"]:
        date_token = str(group["observation_date"]).replace("-", "")
        for configuration in group["configurations"]:
            for observation in group["observations"]:
                attribute = str(observation["attribute_code"])
                result.append(
                    {
                        "id": str(int(spec["value_id_start"]) + len(result)),
                        "code": f"{configuration}_{attribute}_{date_token}_brochure_dimension",
                        "configuration_code": str(configuration),
                        "attribute_code": attribute,
                        "fuel_type_code": "",
                        "gear_number": "",
                        "value": str(observation["value"]),
                        "observation_date": str(group["observation_date"]),
                        "source_code": str(group["source_code"]),
                        "notes": f"Source page {group['source_page']}, visually reviewed dimension diagram: {observation['source_text']}",
                    }
                )
    ensure(len(result) == 382, "expected 382 generated values")
    ensure([int(row["id"]) for row in result] == list(range(2568, 2950)), "generated IDs differ")
    ensure(len({row["code"] for row in result}) == 382, "generated codes are not unique")
    ensure(Counter(row["attribute_code"] for row in result) == EXPECTED_ATTRIBUTE_COUNTS, "attribute distribution differs")
    ensure(Counter(row["source_code"] for row in result) == Counter({source: contract["values"] for source, contract in SOURCE_CONTRACTS.items()}), "source distribution differs")
    ensure(not ({row["attribute_code"] for row in result} & {"approach_angle", "departure_angle"}), "seatback angles entered the import")
    return result


def plan(expected: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    require_header(VALUE_PATH, VALUE_FIELDS)
    current = read_rows(VALUE_PATH)
    by_id = {row["id"]: row for row in current}
    by_code = {row["code"]: row for row in current}
    identities = {
        (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"]): row
        for row in current
    }
    missing: list[dict[str, str]] = []
    existing: list[dict[str, str]] = []
    for expected_row in expected:
        row = dict(expected_row)
        matched = by_code.get(row["code"])
        if matched is not None:
            ensure(matched == row, f"existing row differs: {row['code']}")
            existing.append(row)
            continue
        identity = (row["configuration_code"], row["attribute_code"], row["fuel_type_code"], row["gear_number"], row["observation_date"])
        ensure(row["id"] not in by_id, f"ID already used: {row['id']}")
        ensure(identity not in identities, f"observation identity already used: {identity}")
        missing.append(row)
    return missing, existing


def apply(expected: Sequence[Mapping[str, str]]) -> None:
    missing, _ = plan(expected)
    if missing:
        write_rows_atomic(VALUE_PATH, VALUE_FIELDS, [*read_rows(VALUE_PATH), *missing])


def verify_package(expected: Sequence[Mapping[str, str]]) -> None:
    missing, existing = plan(expected)
    ensure(not missing and len(existing) == 382, f"package incomplete: missing={len(missing)}, existing={len(existing)}")
    package = [row for row in read_rows(VALUE_PATH) if 2568 <= int(row["id"]) <= 2949]
    ensure(package == [dict(row) for row in expected], "committed package differs from reviewed rows")


def run(*, apply_changes: bool) -> None:
    spec = load_spec()
    review = load_review()
    verify_sources()
    verify_references(spec, review)
    expected = expected_rows(spec)
    if apply_changes:
        apply(expected)
    verify_package(expected)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        run(apply_changes=args.apply)
    except (ImportContractError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print("PASS: brochure generic dimension observations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
