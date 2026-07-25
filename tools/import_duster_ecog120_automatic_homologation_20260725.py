#!/usr/bin/env python3
"""Import exact automatic-specific Duster Eco-G 120 homologation observations."""
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
DATE = "2026-07-25"
RO_SOURCE = "src_ro_duster_ecog120_automatic_homologation_20260725"
PL_SOURCE = "src_pl_duster_ecog120_automatic_wltp_20260725"
SOURCE_CODES = {RO_SOURCE, PL_SOURCE}
SNAPSHOTS = {
    RO_SOURCE: (
        ROOT / "project" / "sources" / "dacia-ro-duster-ecog120-automatic-homologation-20260725.json",
        "045bf18bc8ed2dee6ee86692e8fb7cf9a3005e6cf389c3b743376f7abe96d75d",
    ),
    PL_SOURCE: (
        ROOT / "project" / "sources" / "dacia-pl-duster-ecog120-automatic-wltp-20260725.json",
        "9fb6f9ec816ab8ddc813b4ab53c09394454c420bc01866db0b17d027faf126e7",
    ),
}
CONFIGURATION_CODES = {
    "duster_iii_expression_ecog120_4x2_automatic",
    "duster_iii_extreme_ecog120_4x2_automatic",
    "duster_iii_journey_ecog120_4x2_automatic",
}
CARGO_ATTRIBUTES = {
    "boot_capacity",
    "cargo_volume_vda",
    "cargo_volume_vda_to_luggage_cover",
    "cargo_volume_vda_to_seatback",
    "cargo_volume_without_spare_wheel_iso3832",
    "maximum_cargo_volume_iso3832",
}
TARGETS = {
    "sources.csv": (
        "id", "code", "source_type", "title", "publisher", "market",
        "document_date", "external_reference", "file_path", "sha256", "status", "notes",
    ),
    "source_models.csv": ("id", "source_code", "model_code", "relationship", "notes"),
    "source_versions.csv": ("id", "source_code", "version_code", "relationship", "notes"),
    "source_configurations.csv": (
        "id", "source_code", "configuration_code", "relationship", "notes",
    ),
    "configuration_attribute_values.csv": (
        "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
        "value", "observation_date", "source_code", "notes",
    ),
    "configuration_attribute_value_ranges.csv": (
        "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
        "minimum_value", "maximum_value", "lower_inclusive", "upper_inclusive",
        "observation_date", "source_code", "notes",
    ),
}


class ContractError(RuntimeError):
    """Raised when normalized evidence cannot reproduce the master-data contract."""


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


def write_rows(
    path: Path,
    fields: Sequence[str],
    rows: Iterable[dict[str, str]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_snapshots() -> dict[str, dict]:
    payloads: dict[str, dict] = {}
    for source_code, (path, expected_sha) in SNAPSHOTS.items():
        actual_sha = file_sha256(path)
        if actual_sha != expected_sha:
            raise ContractError(
                f"normalized snapshot SHA-256 mismatch for {source_code}: {actual_sha}"
            )
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            payload.get("source_code") != source_code
            or payload.get("observed_on") != DATE
        ):
            raise ContractError(f"snapshot identity mismatch: {source_code}")
        payloads[source_code] = payload
    return payloads


def normalized_contract() -> dict[str, list[dict[str, str]]]:
    payloads = load_snapshots()
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
    fuel_types = {
        row["code"]
        for row in read_rows(MASTER / "enums" / "fuel_types.csv")
        if row.get("status") == "active"
    }

    expected_versions: dict[str, str] = {}
    for code in sorted(CONFIGURATION_CODES):
        configuration = configurations.get(code)
        if not configuration:
            raise ContractError(f"active configuration missing: {code}")
        if configuration.get("powertrain_label") != "Eco-G 120 4x2":
            raise ContractError(f"powertrain mismatch: {code}")
        if configuration.get("transmission_type") != "automatic":
            raise ContractError(f"transmission mismatch: {code}")
        expected_versions[code] = configuration["version_code"]

    scalar_rows: list[dict[str, str]] = []
    range_rows: list[dict[str, str]] = []
    source_model_rows: list[dict[str, str]] = []
    source_version_rows: list[dict[str, str]] = []
    source_configuration_rows: list[dict[str, str]] = []
    source_rows: list[dict[str, str]] = []
    scalar_keys: set[tuple[str, str, str]] = set()
    range_keys: set[tuple[str, str, str]] = set()

    source_metadata = {
        RO_SOURCE: {
            "title": "Dacia Romania exact Duster Eco-G 120 automatic homologation cards",
            "market": "RO",
            "external_reference": "https://vanzari.dacia.ro/",
            "relationship": "automatic_homologation_data_for",
            "notes": (
                "Exact 2026 Expression, Extreme and Journey ECO-G 120 auto 2WD stock pages; "
                "automatic-specific power, torque, performance, mass, towing and consumption "
                "evidence. Cargo volume remains an explicit non-import."
            ),
        },
        PL_SOURCE: {
            "title": "Dacia Poland exact Duster Eco-G 120 automatic WLTP cards",
            "market": "PL",
            "external_reference": "https://www.dacia.pl/katalog-nci/",
            "relationship": "automatic_wltp_data_for",
            "notes": (
                "Exact Polish Expression, Extreme and Journey Eco-G 120 auto stock pages; "
                "LPG WLTP CO2 and source-stated fuel-tank capacity only."
            ),
        },
    }

    for source_code in (RO_SOURCE, PL_SOURCE):
        payload = payloads[source_code]
        cards = payload.get("cards", [])
        if len(cards) != 3:
            raise ContractError(f"expected three exact cards: {source_code}")
        if {card.get("configuration_code") for card in cards} != CONFIGURATION_CODES:
            raise ContractError(f"configuration coverage mismatch: {source_code}")
        if payload.get("market") != source_metadata[source_code]["market"]:
            raise ContractError(f"source market mismatch: {source_code}")

        path, expected_sha = SNAPSHOTS[source_code]
        metadata = source_metadata[source_code]
        source_rows.append({
            "code": source_code,
            "source_type": "web_snapshot",
            "title": metadata["title"],
            "publisher": "Dacia",
            "market": metadata["market"],
            "document_date": DATE,
            "external_reference": metadata["external_reference"],
            "file_path": path.relative_to(ROOT).as_posix(),
            "sha256": expected_sha,
            "status": "active",
            "notes": metadata["notes"],
        })
        source_model_rows.append({
            "source_code": source_code,
            "model_code": "duster_iii",
            "relationship": metadata["relationship"],
            "notes": metadata["notes"],
        })

        seen_versions: set[str] = set()
        for card in cards:
            configuration_code = card["configuration_code"]
            version_code = card["version_code"]
            if version_code != expected_versions[configuration_code]:
                raise ContractError(
                    f"version mismatch: {source_code}/{configuration_code}"
                )
            if not str(card.get("url", "")).startswith("https://"):
                raise ContractError(f"official URL missing: {configuration_code}")
            source_configuration_rows.append({
                "source_code": source_code,
                "configuration_code": configuration_code,
                "relationship": metadata["relationship"],
                "notes": (
                    f"Exact {metadata['market']} stock page {card['vehicle_id']} "
                    f"identifies {card['version_name']} Eco-G 120 automatic."
                ),
            })
            if version_code not in seen_versions:
                seen_versions.add(version_code)
                source_version_rows.append({
                    "source_code": source_code,
                    "version_code": version_code,
                    "relationship": metadata["relationship"],
                    "notes": f"Exact automatic evidence observed {DATE}.",
                })

            for item in card.get("scalar_values", []):
                attribute_code = item["attribute_code"]
                fuel_type_code = item.get("fuel_type_code", "")
                key = (configuration_code, attribute_code, fuel_type_code)
                if key in scalar_keys or key in range_keys:
                    raise ContractError(f"duplicate or colliding observation: {key}")
                scalar_keys.add(key)
                attribute = attributes.get(attribute_code)
                if not attribute:
                    raise ContractError(f"inactive attribute: {attribute_code}")
                if attribute.get("unit") != item.get("unit", ""):
                    raise ContractError(f"attribute unit mismatch: {attribute_code}")
                if fuel_type_code and fuel_type_code not in fuel_types:
                    raise ContractError(f"inactive fuel type: {fuel_type_code}")
                if attribute_code in CARGO_ATTRIBUTES:
                    raise ContractError("automatic cargo values must remain unimported")
                scalar_rows.append({
                    "code": (
                        f"{configuration_code}_{attribute_code}_"
                        f"{fuel_type_code or 'all'}_{source_code}_{DATE.replace('-', '')}"
                    ),
                    "configuration_code": configuration_code,
                    "attribute_code": attribute_code,
                    "fuel_type_code": fuel_type_code,
                    "value": str(item["value"]),
                    "observation_date": DATE,
                    "source_code": source_code,
                    "notes": (
                        f"Exact official Dacia {metadata['market']} automatic card "
                        f"{card['vehicle_id']}: {item['source_text']}."
                    ),
                })

            for item in card.get("range_values", []):
                attribute_code = item["attribute_code"]
                fuel_type_code = item.get("fuel_type_code", "")
                key = (configuration_code, attribute_code, fuel_type_code)
                if key in scalar_keys or key in range_keys:
                    raise ContractError(f"duplicate or colliding observation: {key}")
                range_keys.add(key)
                attribute = attributes.get(attribute_code)
                if not attribute:
                    raise ContractError(f"inactive range attribute: {attribute_code}")
                if attribute.get("unit") != item.get("unit", ""):
                    raise ContractError(f"range attribute unit mismatch: {attribute_code}")
                if fuel_type_code and fuel_type_code not in fuel_types:
                    raise ContractError(f"inactive range fuel type: {fuel_type_code}")
                if attribute_code in CARGO_ATTRIBUTES:
                    raise ContractError("automatic cargo ranges must remain unimported")
                minimum = str(item["minimum_value"])
                maximum = str(item["maximum_value"])
                if float(minimum) > float(maximum):
                    raise ContractError(f"reversed range: {key}")
                range_rows.append({
                    "code": (
                        f"{configuration_code}_{attribute_code}_"
                        f"{fuel_type_code or 'all'}_{source_code}_{DATE.replace('-', '')}_range"
                    ),
                    "configuration_code": configuration_code,
                    "attribute_code": attribute_code,
                    "fuel_type_code": fuel_type_code,
                    "minimum_value": minimum,
                    "maximum_value": maximum,
                    "lower_inclusive": "true",
                    "upper_inclusive": "true",
                    "observation_date": DATE,
                    "source_code": source_code,
                    "notes": (
                        f"Exact official Dacia {metadata['market']} automatic card "
                        f"{card['vehicle_id']}: {item['source_text']}. "
                        "The source-stated endpoints are preserved without inference."
                    ),
                })

    if len(scalar_rows) != 60:
        raise ContractError(f"expected 60 scalar observations, got {len(scalar_rows)}")
    if len(range_rows) != 18:
        raise ContractError(f"expected 18 range observations, got {len(range_rows)}")
    if len([row for row in scalar_rows if row["source_code"] == RO_SOURCE]) != 54:
        raise ContractError("expected 54 Romanian scalar observations")
    if len([row for row in scalar_rows if row["source_code"] == PL_SOURCE]) != 6:
        raise ContractError("expected six Polish supplementary observations")
    if any(row["attribute_code"] in CARGO_ATTRIBUTES for row in scalar_rows + range_rows):
        raise ContractError("cargo boundary violated")

    return {
        "sources.csv": sorted(source_rows, key=lambda row: row["code"]),
        "source_models.csv": sorted(
            source_model_rows, key=lambda row: (row["source_code"], row["model_code"])
        ),
        "source_versions.csv": sorted(
            source_version_rows, key=lambda row: (row["source_code"], row["version_code"])
        ),
        "source_configurations.csv": sorted(
            source_configuration_rows,
            key=lambda row: (row["source_code"], row["configuration_code"]),
        ),
        "configuration_attribute_values.csv": sorted(
            scalar_rows, key=lambda row: row["code"]
        ),
        "configuration_attribute_value_ranges.csv": sorted(
            range_rows, key=lambda row: row["code"]
        ),
    }


def owned(
    rows: list[dict[str, str]],
    name: str,
) -> list[dict[str, str]]:
    if name == "sources.csv":
        return [row for row in rows if row.get("code") in SOURCE_CODES]
    return [row for row in rows if row.get("source_code") in SOURCE_CODES]


def semantic(
    rows: Iterable[dict[str, str]],
    fields: Sequence[str],
) -> list[tuple[str, ...]]:
    payload_fields = [field for field in fields if field != "id"]
    return sorted(
        tuple(row.get(field, "") for field in payload_fields)
        for row in rows
    )


def check() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        current = read_rows(path)
        if semantic(owned(current, name), fields) != semantic(contract[name], fields):
            raise ContractError(f"master data differs from normalized contract: {name}")


def apply() -> None:
    contract = normalized_contract()
    for name, fields in TARGETS.items():
        path = MASTER / name
        require_header(path, fields)
        rows = read_rows(path)
        current_owned = owned(rows, name)
        retained = [row for row in rows if row not in current_owned]
        next_id = max((int(row["id"]) for row in retained), default=0) + 1
        generated = [
            {"id": str(next_id + index), **row}
            for index, row in enumerate(contract[name])
        ]
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
    except (
        ContractError,
        OSError,
        csv.Error,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("PASS: Duster Eco-G 120 automatic homologation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
