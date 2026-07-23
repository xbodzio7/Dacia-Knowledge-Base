#!/usr/bin/env python3
"""Import dated official Sandero Stepway web observations for exact Eco-G configurations."""
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
SNAPSHOT = ROOT / "project" / "sources" / "dacia-pl-sandero-stepway-configurations-20260723.json"
SOURCE_CODE = "src_pl_sandero_stepway_official_web_configurations_20260723"
DATE = "2026-07-23"
SNAPSHOT_SHA256 = "dd236991cba2f14f2b49e43cddbcf643741e6609dd5c2f4dbb0bb6e9dbf98ed3"

TARGETS = {
    "sources.csv": (
        "id", "code", "source_type", "title", "publisher", "market",
        "document_date", "external_reference", "file_path", "sha256", "status", "notes",
    ),
    "source_models.csv": ("id", "source_code", "model_code", "relationship", "notes"),
    "source_versions.csv": ("id", "source_code", "version_code", "relationship", "notes"),
    "source_configurations.csv": ("id", "source_code", "configuration_code", "relationship", "notes"),
    "configuration_prices.csv": (
        "id", "code", "configuration_code", "market", "price_type", "amount",
        "currency_code", "price_date", "source_code", "notes",
    ),
    "configuration_attribute_availability.csv": (
        "id", "code", "configuration_code", "attribute_code", "availability_status",
        "observation_date", "source_code", "notes",
    ),
}


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


def active_catalogue() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    models = {row["code"]: row for row in read_rows(MASTER / "models.csv") if row.get("status") == "current"}
    versions = {row["code"]: row for row in read_rows(MASTER / "versions.csv") if row.get("status") == "active"}
    configurations = {
        row["code"]: row
        for row in read_rows(MASTER / "configurations.csv")
        if row.get("status") == "active"
    }
    return models, versions, configurations


def normalized_contract() -> dict[str, list[dict[str, str]]]:
    payload = snapshot()
    models, versions, configurations = active_catalogue()
    attributes = {
        row["code"]: row
        for row in read_rows(MASTER / "attributes.csv")
        if row.get("status") == "active"
    }

    if payload.get("model_code") not in models:
        raise ContractError("snapshot model is not active")

    version_rows: list[dict[str, str]] = []
    configuration_rows: list[dict[str, str]] = []
    price_rows: list[dict[str, str]] = []
    availability_rows: list[dict[str, str]] = []
    seen_configurations: set[str] = set()

    for version_observation in payload.get("version_observations", []):
        version_code = version_observation["version_code"]
        version = versions.get(version_code)
        if not version or version.get("model_code") != payload["model_code"]:
            raise ContractError(f"inactive or mismatched version: {version_code}")
        version_rows.append({
            "source_code": SOURCE_CODE,
            "version_code": version_code,
            "relationship": "web_version_page_documents",
            "notes": (
                f"Official Dacia Poland version and equipment pages observed {DATE}; "
                f"grade code {version_observation['grade_code']}."
            ),
        })

        highlights = version_observation.get("standard_highlights", [])
        highlight_codes = [item["attribute_code"] for item in highlights]
        if len(highlight_codes) != len(set(highlight_codes)):
            raise ContractError(f"duplicate highlights for {version_code}")
        for item in highlights:
            attribute = attributes.get(item["attribute_code"])
            if not attribute or attribute.get("data_type") != "boolean":
                raise ContractError(f"invalid highlighted attribute: {item['attribute_code']}")
            if not item.get("source_label"):
                raise ContractError(f"missing source label: {item['attribute_code']}")

        for observed in version_observation.get("configurations", []):
            configuration_code = observed["configuration_code"]
            configuration = configurations.get(configuration_code)
            if not configuration or configuration.get("version_code") != version_code:
                raise ContractError(f"inactive or mismatched configuration: {configuration_code}")
            if configuration_code in seen_configurations:
                raise ContractError(f"duplicate configuration observation: {configuration_code}")
            seen_configurations.add(configuration_code)
            if configuration.get("powertrain_label") != observed["powertrain_label"]:
                raise ContractError(f"powertrain mismatch: {configuration_code}")
            if configuration.get("transmission_type") != observed["transmission_type"]:
                raise ContractError(f"transmission mismatch: {configuration_code}")
            amount = observed["catalog_price_pln"]
            if not isinstance(amount, int) or amount <= 0:
                raise ContractError(f"invalid catalogue price: {configuration_code}")

            configuration_rows.append({
                "source_code": SOURCE_CODE,
                "configuration_code": configuration_code,
                "relationship": "web_configuration_documents",
                "notes": (
                    f"Official version page explicitly lists {observed['powertrain_label']} "
                    f"with {observed['transmission_type']} gearbox and catalogue price; "
                    "only source-visible version highlights are expanded."
                ),
            })
            price_rows.append({
                "code": f"{configuration_code}_pl_official_web_20260723",
                "configuration_code": configuration_code,
                "market": "PL",
                "price_type": "catalog_gross",
                "amount": str(amount),
                "currency_code": "PLN",
                "price_date": DATE,
                "source_code": SOURCE_CODE,
                "notes": (
                    "Official Dacia Poland version page catalogue price observed 2026-07-23; "
                    "financing, promotions, accessories and dealer-stock prices excluded."
                ),
            })
            for highlight in highlights:
                attribute_code = highlight["attribute_code"]
                availability_rows.append({
                    "code": f"{configuration_code}_{attribute_code}_official_web_20260723",
                    "configuration_code": configuration_code,
                    "attribute_code": attribute_code,
                    "availability_status": "standard",
                    "observation_date": DATE,
                    "source_code": SOURCE_CODE,
                    "notes": (
                        f"Official version-page highlight: {highlight['source_label']}. "
                        "Expanded only to an exact powertrain/gearbox configuration listed on the same page."
                    ),
                })

    expected = {
        "sandero_stepway_iii_essential_ecog120_manual",
        "sandero_stepway_iii_expression_ecog120_manual",
        "sandero_stepway_iii_expression_ecog120_automatic",
        "sandero_stepway_iii_extreme_ecog120_manual",
        "sandero_stepway_iii_extreme_ecog120_automatic",
    }
    if seen_configurations != expected:
        raise ContractError("configuration coverage differs from the five active Stepway Eco-G states")
    if len(version_rows) != 3 or len(price_rows) != 5 or len(availability_rows) != 24:
        raise ContractError("unexpected normalized contract counts")

    source_row = {
        "code": SOURCE_CODE,
        "source_type": "web_snapshot",
        "title": "Dacia Polska Sandero Stepway official version/configurator observations",
        "publisher": "Dacia",
        "market": "PL",
        "document_date": DATE,
        "external_reference": "https://www.dacia.pl/samochody/sandero-stepway-crossover/konfigurator.html",
        "file_path": SNAPSHOT.relative_to(ROOT).as_posix(),
        "sha256": SNAPSHOT_SHA256,
        "status": "active",
        "notes": (
            "Dated dynamic official-web observation. Exact configuration prices and source-visible "
            "version highlights only; unproven option applicability remains unimported."
        ),
    }
    model_row = {
        "source_code": SOURCE_CODE,
        "model_code": payload["model_code"],
        "relationship": "web_configuration_for",
        "notes": "Official Polish Sandero Stepway version and configurator pages observed 2026-07-23.",
    }
    return {
        "sources.csv": [source_row],
        "source_models.csv": [model_row],
        "source_versions.csv": version_rows,
        "source_configurations.csv": configuration_rows,
        "configuration_prices.csv": price_rows,
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
        generated: list[dict[str, str]] = []
        for row in contract[name]:
            generated.append({"id": str(next_id), **row})
            next_id += 1
        write_rows(path, fields, [*retained, *generated])
    check()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.apply:
            apply()
        else:
            check()
    except (ContractError, OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Sandero Stepway official web configuration contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
