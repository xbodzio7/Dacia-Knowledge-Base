#!/usr/bin/env python3
"""Import exact Bigster and Duster brochure towing mass observations."""

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
SPEC = ROOT / "data" / "imports" / "brochure_technical_values" / "bigster-duster-towing-masses-20260726.json"
VALUES = MASTER / "configuration_attribute_values.csv"
RELATIONSHIPS = MASTER / "source_configurations.csv"
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
RELATIONSHIP_FIELDS = (
    "id",
    "source_code",
    "configuration_code",
    "relationship",
    "notes",
)
SOURCE_CONTRACTS = {
    "src_pl_bigster_brochure_20251210": (
        "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf",
        "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74",
        "2025-12-10",
    ),
    "src_pl_duster_mini_brochure_20251020": (
        "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf",
        "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8",
        "2025-10-20",
    ),
}
ATTRIBUTES = {
    "gross_train_weight": ("integer", "kg", "active"),
    "unbraked_trailer_weight": ("integer", "kg", "active"),
}
EXPECTED_SOURCE_COUNTS = Counter(
    {
        "src_pl_bigster_brochure_20251210": 28,
        "src_pl_duster_mini_brochure_20251020": 20,
    }
)
EXPECTED_POWERTRAIN_COUNTS = Counter(
    {
        "mild hybrid-G 140 4x2": 4,
        "mild hybrid 140 4x2": 7,
        "hybrid-G 150 4x4": 3,
        "hybrid 155 4x2": 6,
        "Eco-G 120 4x2": 4,
    }
)


class ImportContractError(RuntimeError):
    """Raised when reviewed brochure evidence or repository state drifts."""


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


def write_rows_atomic(
    path: Path,
    fields: Sequence[str],
    rows: Iterable[Mapping[str, str]],
) -> None:
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_spec() -> dict[str, Any]:
    payload = json.loads(SPEC.read_text(encoding="utf-8"))
    ensure(payload.get("version") == 1, "unsupported package version")
    ensure(payload.get("kind") == "bigster_duster_brochure_towing_masses", "unexpected package kind")
    ensure(payload.get("reviewed_on") == "2026-07-26", "unexpected review date")
    ensure(payload.get("value_id_start") == 2225, "unexpected value ID start")
    ensure(payload.get("relationship_id_start") == 217, "unexpected relationship ID start")
    ensure(set(payload.get("attributes", [])) == set(ATTRIBUTES), "package attributes differ")

    sources = payload.get("sources")
    ensure(isinstance(sources, list) and len(sources) == 2, "expected two brochure sources")
    ensure({item.get("source_code") for item in sources if isinstance(item, dict)} == set(SOURCE_CONTRACTS), "source set differs")

    configurations: list[str] = []
    powertrains: Counter[str] = Counter()
    for source in sources:
        ensure(isinstance(source, dict), "source package must be an object")
        source_code = str(source.get("source_code", ""))
        ensure(source.get("observation_date") == SOURCE_CONTRACTS[source_code][2], f"source date differs: {source_code}")
        groups = source.get("groups")
        ensure(isinstance(groups, list) and groups, f"source groups missing: {source_code}")
        for group in groups:
            ensure(isinstance(group, dict), "powertrain group must be an object")
            ensure(set(group) == {
                "powertrain_label",
                "transmission_type",
                "source_page",
                "gross_train_weight",
                "unbraked_trailer_weight",
                "configurations",
            }, "unexpected powertrain group fields")
            ensure(group.get("transmission_type") in {"manual", "automatic"}, "unexpected transmission type")
            ensure(group.get("source_page") in {20, 21}, "unexpected source page")
            for attribute in ATTRIBUTES:
                value = str(group.get(attribute, ""))
                ensure(value.isdigit() and int(value) > 0, f"invalid {attribute} value")
            group_configurations = group.get("configurations")
            ensure(isinstance(group_configurations, list) and group_configurations, "empty configuration group")
            configurations.extend(str(code) for code in group_configurations)
            powertrains[str(group.get("powertrain_label", ""))] += len(group_configurations)

    ensure(len(configurations) == 24, "expected 24 exact configurations")
    ensure(len(set(configurations)) == 24, "configuration groups overlap")
    ensure(powertrains == EXPECTED_POWERTRAIN_COUNTS, "powertrain configuration distribution differs")

    relationships = payload.get("new_source_relationships")
    ensure(isinstance(relationships, list) and len(relationships) == 3, "expected three new source relationships")
    ensure(
        {str(item.get("configuration_code", "")) for item in relationships if isinstance(item, dict)}
        == {
            "bigster_expression_hybridg150_4x4_automatic",
            "bigster_extreme_hybridg150_4x4_automatic",
            "bigster_journey_hybridg150_4x4_automatic",
        },
        "new source relationship set differs",
    )
    ensure(all(item.get("relationship") == "brochure_technical_data_for" for item in relationships), "relationship type differs")

    excluded = payload.get("excluded_evidence")
    ensure(isinstance(excluded, list) and len(excluded) == 4, "expected four exclusion boundaries")
    ensure(
        {str(item.get("code", "")) for item in excluded if isinstance(item, dict)}
        == {
            "duster_hybridg150_without_exact_configuration",
            "duster_ecog120_automatic_uses_newer_homologation",
            "no_cross_powertrain_projection",
            "no_other_mass_rows",
        },
        "exclusion boundary set differs",
    )
    return payload


def verify_sources() -> None:
    sources = {row.get("code", ""): row for row in read_rows(MASTER / "sources.csv")}
    for code, (relative_path, expected_hash, document_date) in SOURCE_CONTRACTS.items():
        row = sources.get(code)
        ensure(row is not None and row.get("status") == "active", f"active source missing: {code}")
        ensure(row.get("source_type") == "brochure_pdf", f"source type differs: {code}")
        ensure(row.get("document_date") == document_date, f"source date differs: {code}")
        ensure(row.get("file_path") == relative_path, f"source path differs: {code}")
        ensure(row.get("sha256") == expected_hash, f"source registry hash differs: {code}")
        archived = ROOT / relative_path
        ensure(archived.is_file() and sha256(archived) == expected_hash, f"archived source hash differs: {code}")


def iter_groups(spec: Mapping[str, Any]):
    for source in spec["sources"]:
        for group in source["groups"]:
            yield source, group


def verify_references(spec: Mapping[str, Any]) -> None:
    attributes = {row.get("code", ""): row for row in read_rows(MASTER / "attributes.csv")}
    for code, contract in ATTRIBUTES.items():
        row = attributes.get(code)
        ensure(row is not None, f"attribute missing: {code}")
        ensure((row.get("data_type"), row.get("unit"), row.get("status")) == contract, f"attribute contract differs: {code}")

    configurations = {row.get("code", ""): row for row in read_rows(MASTER / "configurations.csv")}
    for _, group in iter_groups(spec):
        for code in group["configurations"]:
            row = configurations.get(code)
            ensure(row is not None and row.get("status") == "active", f"active configuration missing: {code}")
            ensure(row.get("powertrain_label") == group["powertrain_label"], f"powertrain differs: {code}")
            ensure(row.get("transmission_type") == group["transmission_type"], f"transmission differs: {code}")

    later_duster_configurations = {
        code
        for code in configurations
        if code.startswith("duster_iii_") and "hybridg150" in code
    }
    ensure(
        later_duster_configurations == DUSTER_HYBRIDG150_CONFIGURATION_CODES,
        "later exact Duster hybrid-G 150 catalogue scope differs",
    )


def expected_values(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    start = int(spec["value_id_start"])
    for source, group in iter_groups(spec):
        source_code = str(source["source_code"])
        date = str(source["observation_date"])
        compact_date = date.replace("-", "")
        page = int(group["source_page"])
        for configuration in group["configurations"]:
            for attribute in ("gross_train_weight", "unbraked_trailer_weight"):
                value = str(group[attribute])
                source_label = (
                    "Dopuszczalna masa całkowita zestawu/zespołu pojazdów"
                    if attribute == "gross_train_weight"
                    else "Maksymalna masa przyczepy bez hamulca"
                )
                result.append(
                    {
                        "id": str(start + len(result)),
                        "code": f"{configuration}_{attribute}_{source_code}_{compact_date}",
                        "configuration_code": str(configuration),
                        "attribute_code": attribute,
                        "fuel_type_code": "",
                        "gear_number": "",
                        "value": value,
                        "observation_date": date,
                        "source_code": source_code,
                        "notes": f"Official brochure page {page}: {source_label}: {value} kg.",
                    }
                )
    ensure(len(result) == 48, "expected 48 generated observations")
    ensure([int(row["id"]) for row in result] == list(range(2225, 2273)), "generated value IDs differ")
    ensure(len({row["code"] for row in result}) == 48, "generated value codes are not unique")
    ensure(Counter(row["source_code"] for row in result) == EXPECTED_SOURCE_COUNTS, "source value counts differ")
    ensure(Counter(row["attribute_code"] for row in result) == Counter({"gross_train_weight": 24, "unbraked_trailer_weight": 24}), "attribute value counts differ")
    return result


def expected_relationships(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    start = int(spec["relationship_id_start"])
    result = []
    for index, item in enumerate(spec["new_source_relationships"]):
        result.append(
            {
                "id": str(start + index),
                "source_code": str(item["source_code"]),
                "configuration_code": str(item["configuration_code"]),
                "relationship": str(item["relationship"]),
                "notes": str(item["notes"]),
            }
        )
    ensure([int(row["id"]) for row in result] == [217, 218, 219], "relationship IDs differ")
    return result


def merge_rows(
    existing: list[dict[str, str]],
    expected: list[dict[str, str]],
    semantic_fields: Sequence[str],
) -> list[dict[str, str]]:
    by_id = {row.get("id", ""): row for row in existing}
    by_code = {row.get("code", "").casefold(): row for row in existing if "code" in row}
    by_semantic = {
        tuple(row.get(field, "") for field in semantic_fields): row
        for row in existing
    }
    additions: list[dict[str, str]] = []
    for row in expected:
        candidates = [by_id.get(row["id"])]
        if "code" in row:
            candidates.append(by_code.get(row["code"].casefold()))
        candidates.append(by_semantic.get(tuple(row.get(field, "") for field in semantic_fields)))
        present = [item for item in candidates if item is not None]
        if present:
            ensure(all(item == row for item in present), f"existing row differs: {row}")
        else:
            additions.append(row)
    if additions:
        current_max = max((int(row["id"]) for row in existing), default=0)
        ensure(int(additions[0]["id"]) == current_max + 1, "append-only ID boundary differs")
        ensure([int(row["id"]) for row in additions] == list(range(current_max + 1, current_max + 1 + len(additions))), "added IDs are not contiguous")
    return [*existing, *additions]


def apply(spec: Mapping[str, Any]) -> None:
    require_header(VALUES, VALUE_FIELDS)
    require_header(RELATIONSHIPS, RELATIONSHIP_FIELDS)
    value_rows = read_rows(VALUES)
    relationship_rows = read_rows(RELATIONSHIPS)
    merged_values = merge_rows(
        value_rows,
        expected_values(spec),
        (
            "configuration_code",
            "attribute_code",
            "fuel_type_code",
            "gear_number",
            "observation_date",
        ),
    )
    merged_relationships = merge_rows(
        relationship_rows,
        expected_relationships(spec),
        ("source_code", "configuration_code", "relationship"),
    )
    if merged_values != value_rows:
        write_rows_atomic(VALUES, VALUE_FIELDS, merged_values)
    if merged_relationships != relationship_rows:
        write_rows_atomic(RELATIONSHIPS, RELATIONSHIP_FIELDS, merged_relationships)


def check(spec: Mapping[str, Any]) -> None:
    expected_value_rows = expected_values(spec)
    all_values = read_rows(VALUES)
    package_configurations = {row["configuration_code"] for row in expected_value_rows}
    package_sources = set(SOURCE_CONTRACTS)
    actual = {
        row["code"]: row
        for row in all_values
        if row.get("source_code") in package_sources
        and row.get("configuration_code") in package_configurations
        and row.get("attribute_code") in ATTRIBUTES
    }
    ensure(actual == {row["code"]: row for row in expected_value_rows}, "master towing package differs")

    relationship_rows = read_rows(RELATIONSHIPS)
    pairs = {
        (row.get("source_code", ""), row.get("configuration_code", ""), row.get("relationship", ""))
        for row in relationship_rows
    }
    for source, group in iter_groups(spec):
        for configuration in group["configurations"]:
            ensure(
                (source["source_code"], configuration, "brochure_technical_data_for") in pairs,
                f"source relationship missing: {configuration}",
            )
    expected_new = {row["id"]: row for row in expected_relationships(spec)}
    actual_new = {row["id"]: row for row in relationship_rows if row.get("id") in expected_new}
    ensure(actual_new == expected_new, "new relationship rows differ")

    excluded_configurations = {
        "duster_iii_expression_ecog120_4x2_automatic",
        "duster_iii_extreme_ecog120_4x2_automatic",
        "duster_iii_journey_ecog120_4x2_automatic",
    }
    ensure(not (package_configurations & excluded_configurations), "newer automatic homologation scope was imported")
    ensure(
        package_configurations.isdisjoint(DUSTER_HYBRIDG150_CONFIGURATION_CODES),
        "later Duster hybrid-G 150 catalogue identities were imported into the historical brochure package",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        verify_sources()
        spec = load_spec()
        verify_references(spec)
        if args.apply:
            apply(spec)
        check(spec)
    except (ImportContractError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("PASS: Bigster and Duster brochure towing masses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
