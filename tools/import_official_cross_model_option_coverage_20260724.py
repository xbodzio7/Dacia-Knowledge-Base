#!/usr/bin/env python3
"""Import dated official cross-model option-coverage observations."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
SNAPSHOT = ROOT / "project" / "sources" / "dacia-pl-cross-model-option-coverage-20260724.json"
SOURCE_CODE = "src_pl_cross_model_option_coverage_20260724"
DATE = "2026-07-24"
SNAPSHOT_SHA256 = "283dcb96119804f6f100ba3d7c93d968f862aa06667a681198cb7bb77e24cf63"

TARGETS = {
    "sources.csv": (
        "id", "code", "source_type", "title", "publisher", "market",
        "document_date", "external_reference", "file_path", "sha256", "status", "notes",
    ),
    "source_models.csv": ("id", "source_code", "model_code", "relationship", "notes"),
    "source_versions.csv": ("id", "source_code", "version_code", "relationship", "notes"),
    "source_configurations.csv": ("id", "source_code", "configuration_code", "relationship", "notes"),
    "configuration_attribute_availability.csv": (
        "id", "code", "configuration_code", "attribute_code", "availability_status",
        "observation_date", "source_code", "notes",
    ),
}

EXPECTED_MODELS = {"sandero_iii", "sandero_stepway_iii", "jogger"}
EXPECTED_VERSIONS = {
    "sandero_iii_expression",
    "sandero_iii_journey",
    "sandero_stepway_iii_essential",
    "sandero_stepway_iii_expression",
    "sandero_stepway_iii_extreme",
    "jogger_essential",
    "jogger_expression",
    "jogger_extreme",
    "jogger_journey",
}
EXPECTED_ATTRIBUTES = {"shark_fin_antenna", "side_mirrors_folding"}


class ContractError(RuntimeError):
    """Raised when the normalized source contract cannot be reproduced."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ContractError(f"missing CSV header: {path}")
        return list(reader)


def require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    if header != list(fields):
        raise ContractError(f"unexpected header in {path}: {header!r}")


def write_rows(path: Path, fields: Sequence[str], rows: Iterable[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def snapshot() -> dict:
    if file_sha256(SNAPSHOT) != SNAPSHOT_SHA256:
        raise ContractError("normalized snapshot SHA-256 mismatch")
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if payload.get("source_code") != SOURCE_CODE or payload.get("observed_on") != DATE:
        raise ContractError("snapshot identity mismatch")
    return payload


def normalized_contract() -> dict[str, list[dict[str, str]]]:
    payload = snapshot()
    models = {
        row["code"]: row
        for row in read_rows(MASTER / "models.csv")
        if row.get("status") == "current"
    }
    versions = {
        row["code"]: row
        for row in read_rows(MASTER / "versions.csv")
        if row.get("status") == "active"
    }
    configurations = {
        row["code"]: row
        for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    attributes = {
        row["code"]: row
        for row in read_rows(MASTER / "attributes.csv")
        if row.get("status") == "active"
    }
    statuses = {
        row["code"]
        for row in read_rows(MASTER / "enums" / "equipment_availability_statuses.csv")
        if row.get("status") == "active"
    }

    version_rows: list[dict[str, str]] = []
    configuration_rows: list[dict[str, str]] = []
    availability_rows: list[dict[str, str]] = []
    seen_versions: set[str] = set()
    seen_configurations: set[str] = set()
    imported_models: set[str] = set()

    for observation in payload.get("version_observations", []):
        model_code = observation["model_code"]
        version_code = observation["version_code"]
        if model_code not in models:
            raise ContractError(f"current model missing: {model_code}")
        version = versions.get(version_code)
        if not version or version.get("model_code") != model_code:
            raise ContractError(f"inactive or mismatched version: {version_code}")
        if version_code in seen_versions:
            raise ContractError(f"duplicate version observation: {version_code}")
        seen_versions.add(version_code)
        imported_models.add(model_code)

        equipment_url = observation.get("equipment_url", "")
        grade_code = observation.get("grade_code", "")
        if not equipment_url.startswith("https://www.dacia.pl/") or not grade_code:
            raise ContractError(f"invalid official grade source: {version_code}")
        version_rows.append({
            "source_code": SOURCE_CODE,
            "version_code": version_code,
            "relationship": "web_option_coverage_documents",
            "notes": (
                f"Official Dacia Poland grade-specific equipment page observed {DATE}; "
                f"grade code {grade_code}."
            ),
        })

        items = observation.get("availability", [])
        if not items:
            raise ContractError(f"missing availability evidence: {version_code}")
        item_codes = [item["attribute_code"] for item in items]
        if len(item_codes) != len(set(item_codes)):
            raise ContractError(f"duplicate attribute evidence: {version_code}")
        for item in items:
            attribute_code = item["attribute_code"]
            attribute = attributes.get(attribute_code)
            if attribute_code not in EXPECTED_ATTRIBUTES or not attribute:
                raise ContractError(f"invalid target attribute: {attribute_code}")
            if attribute.get("data_type") != "boolean":
                raise ContractError(f"target attribute is not boolean: {attribute_code}")
            if item["availability_status"] not in statuses:
                raise ContractError(f"invalid availability status: {item['availability_status']}")
            if not item.get("source_label"):
                raise ContractError(f"missing source label: {attribute_code}")

        version_configurations = observation.get("configurations", [])
        if not version_configurations:
            raise ContractError(f"missing exact configurations: {version_code}")
        for configuration_code in version_configurations:
            configuration = configurations.get(configuration_code)
            if not configuration or configuration.get("version_code") != version_code:
                raise ContractError(f"inactive or mismatched configuration: {configuration_code}")
            if configuration_code in seen_configurations:
                raise ContractError(f"configuration appears under multiple versions: {configuration_code}")
            seen_configurations.add(configuration_code)
            configuration_rows.append({
                "source_code": SOURCE_CODE,
                "configuration_code": configuration_code,
                "relationship": "web_option_coverage_documents",
                "notes": (
                    f"Active configuration belongs to exact grade {version_code} documented by "
                    f"the official equipment page observed {DATE}."
                ),
            })
            for item in items:
                attribute_code = item["attribute_code"]
                status = item["availability_status"]
                qualifier = (
                    " Explicit alternate factory equipment supports the negative state."
                    if status == "not_available"
                    else " The item is listed as factory standard equipment for the grade."
                )
                availability_rows.append({
                    "code": f"{configuration_code}_{attribute_code}_official_web_20260724",
                    "configuration_code": configuration_code,
                    "attribute_code": attribute_code,
                    "availability_status": status,
                    "observation_date": DATE,
                    "source_code": SOURCE_CODE,
                    "notes": (
                        f"Official grade-page evidence: {item['source_label']}."
                        f" Expanded only to active configurations of {version_code}.{qualifier}"
                    ),
                })

    if imported_models != EXPECTED_MODELS:
        raise ContractError("imported model coverage mismatch")
    if seen_versions != EXPECTED_VERSIONS:
        raise ContractError("version coverage mismatch")
    if len(seen_configurations) != 31:
        raise ContractError("expected 31 exact configurations")
    if len(availability_rows) != 37:
        raise ContractError("expected 37 availability observations")
    if sum(row["availability_status"] == "standard" for row in availability_rows) != 34:
        raise ContractError("expected 34 standard observations")
    if sum(row["availability_status"] == "not_available" for row in availability_rows) != 3:
        raise ContractError("expected three explicit negative observations")
    shark_rows = [row for row in availability_rows if row["attribute_code"] == "shark_fin_antenna"]
    folding_rows = [row for row in availability_rows if row["attribute_code"] == "side_mirrors_folding"]
    if len(shark_rows) != 31 or len(folding_rows) != 6:
        raise ContractError("target attribute counts mismatch")

    source_row = {
        "code": SOURCE_CODE,
        "source_type": "web_snapshot",
        "title": "Dacia Polska cross-model factory option coverage observations",
        "publisher": "Dacia",
        "market": "PL",
        "document_date": DATE,
        "external_reference": "https://www.dacia.pl/",
        "file_path": SNAPSHOT.relative_to(ROOT).as_posix(),
        "sha256": SNAPSHOT_SHA256,
        "status": "active",
        "notes": (
            "Dated normalized snapshot of official grade-specific equipment pages. "
            "Factory shark-fin antenna and power-folding mirror evidence only; accessories, "
            "unproven Duster states and broadened package mappings are excluded."
        ),
    }
    model_rows = [
        {
            "source_code": SOURCE_CODE,
            "model_code": model_code,
            "relationship": "web_option_coverage_for",
            "notes": f"Official Polish grade-specific equipment pages observed {DATE}.",
        }
        for model_code in sorted(imported_models)
    ]
    return {
        "sources.csv": [source_row],
        "source_models.csv": model_rows,
        "source_versions.csv": version_rows,
        "source_configurations.csv": configuration_rows,
        "configuration_attribute_availability.csv": availability_rows,
    }


def source_owned(rows: list[dict[str, str]], name: str) -> list[dict[str, str]]:
    if name == "sources.csv":
        return [row for row in rows if row.get("code") == SOURCE_CODE]
    return [row for row in rows if row.get("source_code") == SOURCE_CODE]


def semantic(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    payload_fields = [field for field in fields if field != "id"]
    return sorted(tuple(row.get(field, "") for field in payload_fields) for row in rows)


def check() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        actual = source_owned(read_rows(path), name)
        if semantic(actual, fields) != semantic(contract[name], fields):
            raise ContractError(f"master data differs from normalized contract: {name}")


def apply() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        rows = read_rows(path)
        retained = [row for row in rows if row not in source_owned(rows, name)]
        next_id = max((int(row["id"]) for row in retained), default=0) + 1
        generated = [{"id": str(next_id + index), **row} for index, row in enumerate(contract[name])]
        write_rows(path, fields, [*retained, *generated])
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
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: official cross-model option coverage contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
