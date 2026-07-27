#!/usr/bin/env python3
"""Migrate the recovered Sandero/Stepway catalogue package to isolated source slices."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master"
IMPORTER = ROOT / "tools/import_sandero_stepway_catalog_completion.py"

NEW_CONFIGURATIONS = {
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_stepway_iii_essential_tce110_manual",
    "sandero_stepway_iii_expression_tce110_manual",
    "sandero_stepway_iii_extreme_tce110_manual",
}
PRICE_CONFIGURATIONS = NEW_CONFIGURATIONS | {
    "sandero_iii_expression_ecog120_automatic",
    "sandero_iii_journey_ecog120_automatic",
}

RAW_PRICE = "src_pl_sandero_stepway_price_my26_20260703"
RAW_SANDERO = "src_pl_sandero_brochure_20260202"
RAW_STEPWAY = "src_pl_sandero_stepway_brochure_20260202"
SLICE_PRICE = "src_pl_sandero_stepway_catalog_tce_slice_20260703"
SLICE_SANDERO = "src_pl_sandero_catalog_tce_slice_20260202"
SLICE_STEPWAY = "src_pl_sandero_stepway_catalog_tce_slice_20260202"


class MigrationError(RuntimeError):
    pass


def run(*args: str) -> None:
    completed = subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.returncode:
        raise MigrationError(f"command failed ({completed.returncode}): {' '.join(args)}")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise MigrationError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise MigrationError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def restore_historical_contracts() -> None:
    run("git", "fetch", "origin", "main")
    media_test = ROOT / "tests/test_model_media_cache.py"
    backup = ROOT / ".git/model-media-cache-test.py"
    shutil.copyfile(media_test, backup)
    run("git", "checkout", "origin/main", "--", "tests")
    shutil.copyfile(backup, media_test)
    cargo_path = Path(
        "data/imports/configuration_cargo_values/"
        "sandero-stepway-brochure-cargo-20260202.json"
    )
    completed = subprocess.run(
        ["git", "show", f"origin/main:{cargo_path.as_posix()}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise MigrationError(completed.stderr.decode("utf-8", errors="replace"))
    (ROOT / cargo_path).write_bytes(completed.stdout)


def patch_importer() -> None:
    text = IMPORTER.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'PRICE_SOURCE = "src_pl_sandero_stepway_price_my26_20260703"\n'
        'SANDERO_BROCHURE_SOURCE = "src_pl_sandero_brochure_20260202"\n'
        'STEPWAY_BROCHURE_SOURCE = "src_pl_sandero_stepway_brochure_20260202"\n',
        'RAW_PRICE_SOURCE = "src_pl_sandero_stepway_price_my26_20260703"\n'
        'RAW_SANDERO_BROCHURE_SOURCE = "src_pl_sandero_brochure_20260202"\n'
        'RAW_STEPWAY_BROCHURE_SOURCE = "src_pl_sandero_stepway_brochure_20260202"\n'
        'PRICE_SOURCE = "src_pl_sandero_stepway_catalog_tce_slice_20260703"\n'
        'SANDERO_BROCHURE_SOURCE = "src_pl_sandero_catalog_tce_slice_20260202"\n'
        'STEPWAY_BROCHURE_SOURCE = "src_pl_sandero_stepway_catalog_tce_slice_20260202"\n',
        "source constants",
    )
    text = replace_once(
        text,
        'FIELDS = {\n    "versions.csv": (',
        'FIELDS = {\n'
        '    "sources.csv": (\n'
        '        "id", "code", "source_type", "title", "publisher", "market",\n'
        '        "document_date", "external_reference", "file_path", "sha256",\n'
        '        "status", "notes",\n'
        '    ),\n'
        '    "versions.csv": (',
        "source fields",
    )

    helper = '''

def _source_slice_rows(repository: Path, *, apply: bool) -> list[dict[str, str]]:
    master = repository / "data/master"
    _, registered = _read_csv(master / "sources.csv")
    raw_by_code = {row["code"]: row for row in registered}
    definitions = (
        (
            PRICE_SOURCE,
            RAW_PRICE_SOURCE,
            "Sandero and Stepway MY26 TCe catalogue slice",
            sorted(
                {str(item["code"]) for item in CONFIGURATIONS}
                | {code for code, _ in EXTRA_PRICE_OBSERVATIONS}
            ),
            [1, 2, 3, 4, 5, 6],
            ["configuration", "price", "equipment", "technical", "trim"],
        ),
        (
            SANDERO_BROCHURE_SOURCE,
            RAW_SANDERO_BROCHURE_SOURCE,
            "Sandero TCe 100 brochure technical slice",
            sorted(
                str(item["code"])
                for item in CONFIGURATIONS
                if item["model_family"] == "sandero"
            ),
            [17, 20],
            ["technical", "performance", "chassis", "dimensions", "cargo"],
        ),
        (
            STEPWAY_BROCHURE_SOURCE,
            RAW_STEPWAY_BROCHURE_SOURCE,
            "Sandero Stepway TCe 110 brochure technical slice",
            sorted(
                str(item["code"])
                for item in CONFIGURATIONS
                if item["model_family"] == "stepway"
            ),
            [17, 20],
            ["technical", "performance", "chassis", "dimensions", "cargo"],
        ),
    )
    rows: list[dict[str, str]] = []
    for code, raw_code, title, configurations, pages, families in definitions:
        raw = raw_by_code.get(raw_code)
        if raw is None:
            raise CompletionError(f"raw source missing: {raw_code}")
        payload = {
            "version": 1,
            "kind": "official_source_slice",
            "slice_code": code,
            "raw_source_code": raw_code,
            "raw_source": {
                "title": raw["title"],
                "publisher": raw["publisher"],
                "market": raw["market"],
                "document_date": raw["document_date"],
                "external_reference": raw["external_reference"],
                "file_path": raw["file_path"],
                "sha256": raw["sha256"],
            },
            "selection": {
                "configuration_codes": configurations,
                "source_pages": pages,
                "observation_families": families,
            },
            "non_inference": [
                "The slice does not replace or alter the registered raw official document.",
                "Every imported observation retains raw page and section provenance in its notes.",
                "Only values directly visible in the selected official source are represented.",
            ],
        }
        relative = Path("project/sources") / f"{code.removeprefix('src_pl_')}.json"
        rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\\n"
        target = repository / relative
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
        elif not target.exists() or target.read_text(encoding="utf-8") != rendered:
            raise CompletionError(f"source slice differs: {relative}")
        digest = __import__("hashlib").sha256(rendered.encode("utf-8")).hexdigest()
        rows.append(
            {
                "code": code,
                "source_type": "normalized_snapshot",
                "title": title,
                "publisher": raw["publisher"],
                "market": raw["market"],
                "document_date": raw["document_date"],
                "external_reference": raw["external_reference"],
                "file_path": relative.as_posix(),
                "sha256": digest,
                "status": "active",
                "notes": (
                    f"Versioned source slice of {raw_code}; the raw official "
                    "file remains canonical and hash-verified."
                ),
            }
        )
    return rows
'''
    text = replace_once(
        text,
        "\ndef _validate_references(repository: Path) -> None:\n",
        helper + "\ndef _validate_references(repository: Path) -> None:\n",
        "source helper insertion",
    )
    text = replace_once(
        text,
        '    additions: dict[str, int] = {}\n'
        '    additions["versions"], _ = _append_expected(',
        '    additions: dict[str, int] = {}\n'
        '    source_slice_rows = _source_slice_rows(repository, apply=apply)\n'
        '    additions["sources"], _ = _append_expected(\n'
        '        master / "sources.csv",\n'
        '        source_slice_rows,\n'
        '        apply=apply,\n'
        '    )\n'
        '    additions["versions"], _ = _append_expected(',
        "source apply insertion",
    )
    text = replace_once(
        text,
        '            "versions": 1,\n'
        '            "source_version_relationships": 1,',
        '            "sources": 3,\n'
        '            "versions": 1,\n'
        '            "source_version_relationships": 1,',
        "source expected additions",
    )
    text = replace_once(
        text,
        '        "price_source_code": PRICE_SOURCE,\n'
        '        "configuration_codes": [str(item["code"]) for item in CONFIGURATIONS],',
        '        "price_source_code": PRICE_SOURCE,\n'
        '        "source_slices": [\n'
        '            PRICE_SOURCE,\n'
        '            SANDERO_BROCHURE_SOURCE,\n'
        '            STEPWAY_BROCHURE_SOURCE,\n'
        '        ],\n'
        '        "configuration_codes": [str(item["code"]) for item in CONFIGURATIONS],',
        "source slice contract",
    )
    text = replace_once(
        text,
        "    _update_cargo_spec(repository, apply=apply)\n",
        "",
        "legacy cargo spec call",
    )
    compile(text, str(IMPORTER), "exec")
    IMPORTER.write_text(text, encoding="utf-8")


def migrate_existing_rows() -> None:
    fields, rows = read_csv(MASTER / "configuration_attribute_values.csv")
    for row in rows:
        if row["configuration_code"] not in NEW_CONFIGURATIONS:
            continue
        mapping = {
            RAW_PRICE: SLICE_PRICE,
            RAW_SANDERO: SLICE_SANDERO,
            RAW_STEPWAY: SLICE_STEPWAY,
        }
        row["source_code"] = mapping.get(row["source_code"], row["source_code"])
    write_csv(MASTER / "configuration_attribute_values.csv", fields, rows)

    fields, rows = read_csv(MASTER / "configuration_prices.csv")
    for row in rows:
        if (
            row["configuration_code"] in PRICE_CONFIGURATIONS
            and row["price_date"] == "2026-07-03"
            and int(row["id"]) > 118
        ):
            row["source_code"] = SLICE_PRICE
    write_csv(MASTER / "configuration_prices.csv", fields, rows)

    fields, rows = read_csv(MASTER / "configuration_attribute_availability.csv")
    for row in rows:
        if (
            row["observation_date"] == "2026-07-03"
            and row["source_code"] == RAW_PRICE
            and int(row["id"]) > 4754
        ):
            row["source_code"] = SLICE_PRICE
    write_csv(MASTER / "configuration_attribute_availability.csv", fields, rows)

    fields, rows = read_csv(MASTER / "source_configurations.csv")
    for row in rows:
        if int(row["id"]) <= 219:
            continue
        mapping = {
            RAW_PRICE: SLICE_PRICE,
            RAW_SANDERO: SLICE_SANDERO,
            RAW_STEPWAY: SLICE_STEPWAY,
        }
        row["source_code"] = mapping.get(row["source_code"], row["source_code"])
    write_csv(MASTER / "source_configurations.csv", fields, rows)

    fields, rows = read_csv(MASTER / "source_versions.csv")
    for row in rows:
        if int(row["id"]) > 62 and row["source_code"] == RAW_PRICE:
            row["source_code"] = SLICE_PRICE
    write_csv(MASTER / "source_versions.csv", fields, rows)


def update_new_evidence() -> None:
    path = ROOT / "data/reporting/sandero_tce100_stepway_tce110_manual_gap_evidence.spec"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for decision in payload.get("decisions", []):
        if decision.get("domain") == "technical":
            decision["source_code"] = SLICE_STEPWAY
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    try:
        restore_historical_contracts()
        patch_importer()
        migrate_existing_rows()
        run(sys.executable, str(IMPORTER), "--apply")
        update_new_evidence()
        run(sys.executable, str(IMPORTER), "--verify")
    except (MigrationError, OSError, csv.Error, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"migrated": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
