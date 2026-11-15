#!/usr/bin/env python3
"""Import the reviewed Spring MY26 2026-02-06 price and commercial matrices."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
IMPORTS = ROOT / "data/imports"
SOURCE = "src_pl_spring_price_my26_20260206"
SOURCE_DATE = "2026-02-06"
SOURCE_URL = "https://www.dacia.pgd.pl/SiteData/Dacia/images/NowaStrona/Cenniki/2026/kwiecien/Spring.pdf"
SOURCE_PATH = "PDF/Cenniki/DACIA SPRING cennik MY26 20260206.pdf"
SOURCE_SHA256 = "ab36fba1106ca4929c42330df7896cea8fe56e8774353f6cbb5a7a94cfc18055"
CONFIGS = {
    "spring_essential_electric70_automatic",
    "spring_expression_electric70_automatic",
    "spring_extreme_electric100_automatic",
}
GRADES = {"spring_essential", "spring_expression", "spring_extreme"}
PRICE_SPEC = IMPORTS / "spring_my26_configuration_prices_20260206.csv"
MAP_SPEC = IMPORTS / "spring_my26_commercial_item_configurations_20260206.csv"
CONFIG_SPEC = IMPORTS / "spring_my26_source_configurations_20260206.csv"
VERSION_SPEC = IMPORTS / "spring_my26_source_versions_20260206.csv"
PRICE_FIELDS = ("id", "code", "configuration_code", "market", "price_type", "amount",
                "currency_code", "price_date", "source_code", "notes")
MAP_FIELDS = ("id", "code", "commercial_item_code", "configuration_code",
              "availability_status", "amount", "currency_code", "price_date",
              "source_code", "notes")
CONFIG_FIELDS = ("id", "source_code", "configuration_code", "relationship", "notes")
VERSION_FIELDS = ("id", "source_code", "version_code", "relationship", "notes")
PRICE_SPEC_FIELDS = ("code", "configuration_code", "market", "price_type", "amount",
                     "currency_code", "price_date", "source_code", "source_page",
                     "source_label", "notes")
MAP_SPEC_FIELDS = ("code", "commercial_item_code", "configuration_code",
                   "availability_status", "amount", "currency_code", "price_date",
                   "source_code", "source_page", "source_label", "notes")
CONFIG_SPEC_FIELDS = ("source_code", "configuration_code", "relationship", "notes")
VERSION_SPEC_FIELDS = ("source_code", "version_code", "relationship", "notes")


class ContractError(RuntimeError):
    pass


def read(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                raise ContractError(f"missing CSV header: {path}")
            return list(reader)
    except OSError as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def read_spec(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != fields:
                raise ContractError(f"unexpected CSV header: {path}")
            return list(reader)
    except OSError as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def write_atomic(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def verify_source() -> None:
    sources = {row["code"]: row for row in read(MASTER / "sources.csv")}
    source = sources.get(SOURCE)
    if source is None:
        raise ContractError("Spring MY26 source is not registered")
    expected = {
        "source_type": "configuration_pdf", "document_date": SOURCE_DATE,
        "external_reference": SOURCE_URL, "file_path": SOURCE_PATH,
        "sha256": SOURCE_SHA256, "market": "PL", "status": "active",
    }
    if any(source.get(key) != value for key, value in expected.items()):
        raise ContractError("registered Spring MY26 source identity differs from the reviewed source")
    binary = ROOT / SOURCE_PATH
    if not binary.is_file() or digest(binary) != SOURCE_SHA256:
        raise ContractError("archived Spring MY26 PDF is missing or has a different SHA-256")
    model_links = [row for row in read(MASTER / "source_models.csv")
                   if row["source_code"] == SOURCE]
    if len(model_links) != 1 or model_links[0]["model_code"] != "spring" or model_links[0]["relationship"] != "price_list_for":
        raise ContractError("Spring source model relationship is missing or ambiguous")
    configurations = {row["code"]: row for row in read(MASTER / "configurations.csv")}
    if CONFIGS - set(configurations) or any(configurations[c]["status"] != "active" for c in CONFIGS):
        raise ContractError("the three exact Spring MY26 configurations are not active")
    if {c for c in configurations if c.startswith("spring_")} != CONFIGS:
        raise ContractError("Spring configuration set differs from the reviewed three-configuration boundary")


def specs():
    prices = read_spec(PRICE_SPEC, PRICE_SPEC_FIELDS)
    maps = read_spec(MAP_SPEC, MAP_SPEC_FIELDS)
    configs = read_spec(CONFIG_SPEC, CONFIG_SPEC_FIELDS)
    versions = read_spec(VERSION_SPEC, VERSION_SPEC_FIELDS)
    if len(prices) != 3 or {r["configuration_code"] for r in prices} != CONFIGS:
        raise ContractError("price specification must contain the three exact page-1 cells")
    if len(maps) != 10 or len({r["code"] for r in maps}) != 10:
        raise ContractError("commercial specification must contain ten unique dated mappings")
    if len(configs) != 3 or {r["configuration_code"] for r in configs} != CONFIGS:
        raise ContractError("source configuration specification must link exactly three configurations")
    if len(versions) != 3 or {r["version_code"] for r in versions} != GRADES:
        raise ContractError("source grade specification must link exactly three printed grades")
    for row in prices:
        if (row["market"], row["price_type"], row["currency_code"], row["price_date"], row["source_code"]) != ("PL", "catalog_gross", "PLN", SOURCE_DATE, SOURCE):
            raise ContractError("price specification has invalid market, type, currency, date or source")
        if not row["notes"].strip() or row["source_page"] != "1" or row["source_label"] != "Cena promocyjna":
            raise ContractError("price row must preserve the printed page-1 source label and ambiguity")
    for row in maps:
        if (row["availability_status"], row["currency_code"], row["price_date"], row["source_code"]) != ("optional", "PLN", SOURCE_DATE, SOURCE):
            raise ContractError("commercial mapping has invalid status, currency, date or source")
        if not row["amount"].isdigit() or not row["notes"].strip():
            raise ContractError("priced commercial mapping requires an amount and evidence note")
    if Counter(r["commercial_item_code"] for r in maps) != Counter({
        "spring_colour_lichen_khaki": 3,
        "spring_domestic_socket_charging_cable_option": 3,
        "spring_dc40_charging_option": 1,
        "spring_techno_package": 1,
        "spring_city_package": 1,
        "spring_power_package": 1,
    }):
        raise ContractError("commercial mapping distribution differs from the reviewed page-3/page-4 matrix")
    if any(r["configuration_code"] not in CONFIGS for r in maps):
        raise ContractError("commercial mapping targets a configuration outside the source")
    if any(r["configuration_code"] == "spring_extreme_electric100_automatic" and r["commercial_item_code"] == "spring_dc40_charging_option" for r in maps):
        raise ContractError("ambiguous printed P cell for Extreme must not be imported")
    return prices, maps, configs, versions


def generated_rows():
    price_spec, map_spec, config_spec, version_spec = specs()
    prices = [{
        "code": r["code"], "configuration_code": r["configuration_code"],
        "market": r["market"], "price_type": r["price_type"], "amount": r["amount"],
        "currency_code": r["currency_code"], "price_date": r["price_date"],
        "source_code": r["source_code"],
        "notes": f"Printed page {r['source_page']}; source row: {r['source_label']}. {r['notes']}",
    } for r in price_spec]
    maps = [{
        "code": r["code"], "commercial_item_code": r["commercial_item_code"],
        "configuration_code": r["configuration_code"],
        "availability_status": r["availability_status"], "amount": r["amount"],
        "currency_code": r["currency_code"], "price_date": r["price_date"],
        "source_code": r["source_code"],
        "notes": f"Printed page {r['source_page']}; source row: {r['source_label']}. {r['notes']}",
    } for r in map_spec]
    return prices, maps, config_spec, version_spec


def compare(actual, expected, fields, label):
    left = sorted(tuple(row.get(k, "") for k in fields) for row in actual)
    right = sorted(tuple(row.get(k, "") for k in fields) for row in expected)
    if left != right:
        raise ContractError(f"{label} rows differ from the reviewed import specification")


def append_rows(current, additions, fields, label):
    if not additions:
        return current
    current_codes = {row["code"] for row in current} if "code" in fields else set()
    if "code" in fields and current_codes & {row["code"] for row in additions}:
        raise ContractError(f"{label} code collision")
    ids = [int(row["id"]) for row in current]
    if len(ids) != len(set(ids)):
        raise ContractError(f"{label} contains duplicate IDs")
    next_id = max(ids, default=0) + 1
    return current + [{"id": str(next_id + i), **row} for i, row in enumerate(additions)]


def check() -> dict[str, int]:
    verify_source()
    expected_prices, expected_maps, expected_configs, expected_versions = generated_rows()
    price_rows = read(MASTER / "configuration_prices.csv")
    map_rows = read(MASTER / "commercial_item_configurations.csv")
    config_rows = read(MASTER / "source_configurations.csv")
    version_rows = read(MASTER / "source_versions.csv")
    source_prices = [r for r in price_rows if r["source_code"] == SOURCE]
    source_maps = [r for r in map_rows if r["source_code"] == SOURCE]
    source_configs = [r for r in config_rows if r["source_code"] == SOURCE]
    source_versions = [r for r in version_rows if r["source_code"] == SOURCE]
    compare(source_prices, expected_prices, PRICE_FIELDS[1:], "Spring MY26 prices")
    compare(source_maps, expected_maps, MAP_FIELDS[1:], "Spring MY26 commercial mappings")
    compare(source_configs, expected_configs, CONFIG_FIELDS[1:], "Spring MY26 configuration links")
    compare(source_versions, expected_versions, VERSION_FIELDS[1:], "Spring MY26 grade links")
    for rows, label in ((price_rows, "configuration prices"), (map_rows, "commercial mappings"),
                        (config_rows, "source configuration links"), (version_rows, "source grade links")):
        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise ContractError(f"duplicate IDs in {label}")
    if len({r["code"] for r in price_rows}) != len(price_rows):
        raise ContractError("duplicate configuration price codes")
    if len({r["code"] for r in map_rows}) != len(map_rows):
        raise ContractError("duplicate commercial mapping codes")
    if len({(r["configuration_code"], r["source_code"], r["price_date"]) for r in source_prices}) != len(source_prices):
        raise ContractError("duplicate Spring MY26 price natural key")
    if len({(r["commercial_item_code"], r["configuration_code"], r["source_code"], r["price_date"]) for r in source_maps}) != len(source_maps):
        raise ContractError("duplicate Spring MY26 commercial natural key")
    return {"price_rows": len(source_prices), "commercial_mappings": len(source_maps),
            "source_configuration_links": len(source_configs), "source_grade_links": len(source_versions)}


def apply() -> dict[str, int]:
    verify_source()
    expected_prices, expected_maps, expected_configs, expected_versions = generated_rows()
    paths = {
        "prices": MASTER / "configuration_prices.csv",
        "maps": MASTER / "commercial_item_configurations.csv",
        "configs": MASTER / "source_configurations.csv",
        "versions": MASTER / "source_versions.csv",
    }
    fields = {"prices": PRICE_FIELDS, "maps": MAP_FIELDS,
              "configs": CONFIG_FIELDS, "versions": VERSION_FIELDS}
    expected = {"prices": expected_prices, "maps": expected_maps,
                "configs": expected_configs, "versions": expected_versions}
    current = {key: read(path) for key, path in paths.items()}
    for key in paths:
        source_rows = [r for r in current[key] if r["source_code"] == SOURCE]
        if source_rows:
            compare(source_rows, expected[key], fields[key][1:], key)
        else:
            current[key] = append_rows(current[key], expected[key], fields[key], key)
    staged = []
    try:
        for key, path in paths.items():
            fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields[key], lineterminator="\n")
                writer.writeheader()
                writer.writerows(current[key])
            staged.append((path, temporary))
        for path, temporary in staged:
            os.replace(temporary, path)
    finally:
        for _, temporary in staged:
            try:
                os.unlink(temporary)
            except OSError:
                pass
    return check()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = apply() if args.apply else check()
    except (ContractError, OSError, KeyError, ValueError) as exc:
        parser.error(str(exc))
    print("Spring MY26 price/commercial import: PASS", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
