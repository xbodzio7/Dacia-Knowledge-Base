#!/usr/bin/env python3
"""Generate and verify stable documentation baseline counters."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from reporting.statistics import collect_statistics
from validators.references import REFERENCE_RULES
from validators.statuses import STATUS_RULES, configured_status_rules

MARKERS = {
    "README.md": (
        "<!-- dkb:documentation-baseline:readme:start -->",
        "<!-- dkb:documentation-baseline:readme:end -->",
    ),
    "CHANGELOG.md": (
        "<!-- dkb:documentation-baseline:changelog:start -->",
        "<!-- dkb:documentation-baseline:changelog:end -->",
    ),
    "project/ROADMAP.md": (
        "<!-- dkb:documentation-baseline:roadmap:start -->",
        "<!-- dkb:documentation-baseline:roadmap:end -->",
    ),
    "project/SESSION_STATE.md": (
        "<!-- dkb:documentation-baseline:session:start -->",
        "<!-- dkb:documentation-baseline:session:end -->",
    ),
}
VERSION_RE = re.compile(r"DKB Validator v([0-9]+(?:\.[0-9]+)*)")


class BaselineError(RuntimeError):
    """Raised when the baseline cannot be collected or verified."""


@dataclass(frozen=True)
class Baseline:
    version: int
    tests: int
    csv_files: int
    master_rows: int
    empty_csv_files: int
    relationships: int
    status_rules: int
    validator_version: str
    configuration_values: int
    configuration_import_specs: int
    configuration_availability: int
    availability_standard: int
    availability_optional: int
    availability_not_available: int
    availability_unknown: int
    attributes: int
    attribute_categories: int
    sqlite_tables: int
    sqlite_rows: int
    sqlite_verified: bool


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise BaselineError(f"missing CSV header: {path}")
            return list(reader)
    except (OSError, UnicodeDecodeError) as exc:
        raise BaselineError(f"cannot read UTF-8 CSV {path}: {exc}") from exc


def discover_test_count(repository: Path) -> int:
    tests = repository / "tests"
    if not tests.is_dir():
        raise BaselineError(f"tests directory does not exist: {tests}")

    discovery_code = (
        "import sys, unittest\n"
        "loader = unittest.TestLoader()\n"
        "suite = loader.discover("
        "\"tests\", pattern=\"test_*.py\")\n"
        "if loader.errors:\n"
        "    print(\"\\n\".join(loader.errors), file=sys.stderr)\n"
        "    raise SystemExit(1)\n"
        "print(f\"DKB_TEST_COUNT={suite.countTestCases()}\")\n"
    )
    environment = os.environ.copy()
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = (
        str(repository)
        if not existing_pythonpath
        else str(repository) + os.pathsep + existing_pythonpath
    )
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"

    try:
        completed = subprocess.run(
            [sys.executable, "-c", discovery_code],
            cwd=repository,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise BaselineError(
            f"cannot start test discovery: {exc}"
        ) from exc

    if completed.returncode != 0:
        detail = (
            completed.stderr
            or completed.stdout
            or "unknown discovery failure"
        ).strip()
        raise BaselineError("test discovery failed:\n" + detail)

    prefix = "DKB_TEST_COUNT="
    matches = [
        line[len(prefix):]
        for line in completed.stdout.splitlines()
        if line.startswith(prefix)
    ]
    if len(matches) != 1:
        raise BaselineError(
            "invalid test discovery output: "
            + repr(completed.stdout.strip())
        )
    try:
        return int(matches[0])
    except ValueError as exc:
        raise BaselineError(
            f"invalid test count: {matches[0]!r}"
        ) from exc


def read_validator_version(repository: Path) -> str:
    path = repository / "tools" / "validate_dkb.py"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BaselineError(f"cannot read validator: {exc}") from exc
    match = VERSION_RE.search(text)
    if match is None:
        raise BaselineError("validator version marker was not found")
    return match.group(1)


def sqlite_counts(database: Path) -> tuple[int, int]:
    if not database.is_file():
        raise BaselineError(f"SQLite database does not exist: {database}")
    try:
        connection = sqlite3.connect(
            f"file:{database.resolve().as_posix()}?mode=ro",
            uri=True,
        )
        try:
            names = [
                str(row[0])
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                    """
                ).fetchall()
            ]
            row_count = 0
            for name in names:
                quoted = '"' + name.replace('"', '""') + '"'
                row_count += int(
                    connection.execute(
                        f"SELECT COUNT(*) FROM {quoted}"
                    ).fetchone()[0]
                )
        finally:
            connection.close()
    except sqlite3.Error as exc:
        raise BaselineError(f"cannot inspect SQLite database: {exc}") from exc
    return len(names), row_count


def collect_baseline(
    repository: Path,
    database: Path | None = None,
) -> Baseline:
    statistics = collect_statistics(repository)
    registry = repository / "data/master/attribute_enum_domains.csv"
    if registry.is_file():
        configured_rules, status_rule_errors = configured_status_rules(repository)
        if status_rule_errors:
            raise BaselineError(
                "cannot resolve status rules: " + "; ".join(status_rule_errors)
            )
    else:
        configured_rules = STATUS_RULES
    master = repository / "data" / "master"
    values = read_csv_rows(master / "configuration_attribute_values.csv")
    availability = read_csv_rows(
        master / "configuration_attribute_availability.csv"
    )
    attributes = read_csv_rows(master / "attributes.csv")
    categories = read_csv_rows(master / "attribute_categories.csv")
    import_dir = repository / "data" / "imports" / "configuration_values"
    if not import_dir.is_dir():
        raise BaselineError(f"import directory does not exist: {import_dir}")

    statuses = {
        "standard": 0,
        "optional": 0,
        "not_available": 0,
        "unknown": 0,
    }
    for row in availability:
        status = row.get("availability_status", "")
        if status not in statuses:
            raise BaselineError(f"unexpected availability status: {status!r}")
        statuses[status] += 1

    csv_files = int(statistics["csv_files"])
    master_rows = int(statistics["rows"])
    if database is None:
        sqlite_tables = csv_files
        sqlite_rows = master_rows
        sqlite_verified = False
    else:
        sqlite_tables, sqlite_rows = sqlite_counts(database)
        if sqlite_tables != csv_files or sqlite_rows != master_rows:
            raise BaselineError(
                "SQLite baseline differs from master CSV data: "
                f"tables={sqlite_tables}/{csv_files}, "
                f"rows={sqlite_rows}/{master_rows}"
            )
        sqlite_verified = True

    return Baseline(
        version=1,
        tests=discover_test_count(repository),
        csv_files=csv_files,
        master_rows=master_rows,
        empty_csv_files=int(statistics["empty_files"]),
        relationships=len(REFERENCE_RULES),
        status_rules=len(configured_rules),
        validator_version=read_validator_version(repository),
        configuration_values=len(values),
        configuration_import_specs=len(list(import_dir.glob("*.json"))),
        configuration_availability=len(availability),
        availability_standard=statuses["standard"],
        availability_optional=statuses["optional"],
        availability_not_available=statuses["not_available"],
        availability_unknown=statuses["unknown"],
        attributes=len(attributes),
        attribute_categories=len(categories),
        sqlite_tables=sqlite_tables,
        sqlite_rows=sqlite_rows,
        sqlite_verified=sqlite_verified,
    )


def payload(value: Baseline) -> dict[str, Any]:
    return {
        "version": value.version,
        "tests": value.tests,
        "master": {
            "csv_files": value.csv_files,
            "rows": value.master_rows,
            "empty_csv_files": value.empty_csv_files,
        },
        "validation": {
            "relationships": value.relationships,
            "status_rules": value.status_rules,
            "validator_version": value.validator_version,
        },
        "configuration": {
            "values": value.configuration_values,
            "import_specs": value.configuration_import_specs,
            "availability": {
                "total": value.configuration_availability,
                "by_status": {
                    "standard": value.availability_standard,
                    "optional": value.availability_optional,
                    "not_available": value.availability_not_available,
                    "unknown": value.availability_unknown,
                },
            },
        },
        "catalogue": {
            "attributes": value.attributes,
            "attribute_categories": value.attribute_categories,
        },
        "sqlite": {
            "tables": value.sqlite_tables,
            "rows": value.sqlite_rows,
            "verified": value.sqlite_verified,
        },
    }


def render_json(value: Baseline) -> str:
    return json.dumps(
        payload(value),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def render_markdown(value: Baseline) -> str:
    verified = "yes" if value.sqlite_verified else "derived from master CSV"
    rows = [
        ("Tests", value.tests),
        ("Master CSV files", value.csv_files),
        ("Master rows", value.master_rows),
        ("Empty master CSV files", value.empty_csv_files),
        ("Declared relationships", value.relationships),
        ("Status rules", value.status_rules),
        ("Validator version", value.validator_version),
        ("Configuration values", value.configuration_values),
        ("Configuration import specs", value.configuration_import_specs),
        ("Equipment availability", value.configuration_availability),
        ("Availability: standard", value.availability_standard),
        ("Availability: optional", value.availability_optional),
        ("Availability: not_available", value.availability_not_available),
        ("Availability: unknown", value.availability_unknown),
        ("Canonical attributes", value.attributes),
        ("Attribute categories", value.attribute_categories),
        ("SQLite tables", value.sqlite_tables),
        ("SQLite rows", value.sqlite_rows),
        ("SQLite verified", verified),
    ]
    lines = [
        "# Documentation Baseline",
        "",
        "| Counter | Value |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {label} | {item} |" for label, item in rows)
    return "\n".join(lines) + "\n"


def blocks(value: Baseline) -> dict[str, str]:
    return {
        "README.md": (
            f"Zweryfikowany model obejmuje {value.tests} testów, "
            f"{value.csv_files} pliki CSV, {value.master_rows} rekordów\n"
            f"danych, {value.relationships} relacje między tabelami, "
            f"{value.configuration_values} wartości konfiguracji, "
            f"{value.configuration_import_specs}\n"
            "deklaratywnych specyfikacji importu oraz "
            f"{value.configuration_availability} rekordów dostępności "
            "wyposażenia.\n"
            f"Katalog zawiera {value.attributes} kanonicznych atrybutów i "
            f"{value.attribute_categories} kategorii atrybutów. Baza\n"
            f"SQLite obejmuje {value.sqlite_tables} tabele i "
            f"{value.sqlite_rows} rekordów, pozostaje zgodna z CSV, "
            "a wszystkie\n"
            "źródłowe pliki CSV są zapisane jako UTF-8."
        ),
        "CHANGELOG.md": "\n".join(
            [
                f"* The automated test suite now contains {value.tests} tests.",
                (
                    "* The verified master-data baseline now contains "
                    f"{value.csv_files} CSV files and {value.master_rows} rows."
                ),
                (
                    "* SQLite verification now covers "
                    f"{value.sqlite_tables} tables and {value.sqlite_rows} rows."
                ),
                (
                    "* Configuration attribute values now contain "
                    f"{value.configuration_values} dated records."
                ),
                (
                    "* Declarative configuration-value imports now contain "
                    f"{value.configuration_import_specs} versioned JSON "
                    "specifications."
                ),
                (
                    "* The canonical catalogue now contains "
                    f"{value.attributes} attributes in "
                    f"{value.attribute_categories} categories."
                ),
                (
                    "* Equipment availability now contains "
                    f"{value.configuration_availability} records: "
                    f"{value.availability_standard} `standard`, "
                    f"{value.availability_optional} `optional`, "
                    f"{value.availability_not_available} `not_available` and "
                    f"{value.availability_unknown} `unknown`."
                ),
            ]
        ),
        "project/ROADMAP.md": "\n".join(
            [
                f"- {value.tests} testów automatycznych,",
                (
                    "- deterministyczna komenda `documentation-baseline` "
                    "z kontrolą bieżących podsumowań,"
                ),
            ]
        ),
        "project/SESSION_STATE.md": "\n".join(
            [
                f"- {value.tests} testów automatycznych zakończonych powodzeniem,",
                f"- {value.csv_files} pliki CSV w `data/master`,",
                f"- {value.master_rows} rekordów danych,",
                f"- {value.relationships} relacje między tabelami,",
                f"- {value.status_rules} reguł statusów,",
                f"- walidator repozytorium w wersji {value.validator_version},",
                (
                    f"- {value.configuration_values} obserwacji w "
                    "`configuration_attribute_values.csv`,"
                ),
                (
                    f"- {value.configuration_import_specs} wersjonowanych "
                    "specyfikacji w `data/imports/configuration_values`,"
                ),
                (
                    f"- {value.configuration_availability} rekordów w "
                    "`configuration_attribute_availability.csv`,"
                ),
                (
                    f"- {value.availability_standard} rekordów `standard`, "
                    f"{value.availability_optional} `optional`, "
                    f"{value.availability_not_available} `not_available` i "
                    f"{value.availability_unknown} `unknown`,"
                ),
                (
                    f"- {value.attributes} kanonicznych atrybutów w "
                    f"{value.attribute_categories} kategoriach,"
                ),
                (
                    f"- baza SQLite obejmująca {value.sqlite_tables} tabele "
                    f"i {value.sqlite_rows} rekordów,"
                ),
                "- zgodność schematu i zawartości SQLite z plikami CSV,",
                "- wszystkie źródłowe pliki CSV zapisane jako UTF-8.",
            ]
        ),
    }


def replace_block(
    text: str,
    start: str,
    end: str,
    content: str,
    relative_path: str,
) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise BaselineError(
            f"{relative_path}: expected exactly one managed marker pair"
        )
    left = text.index(start)
    right = text.index(end, left)
    if right <= left:
        raise BaselineError(f"{relative_path}: managed markers are reversed")
    replacement = f"{start}\n{content.rstrip()}\n{end}"
    return text[:left] + replacement + text[right + len(end):]


def expected_documents(
    repository: Path,
    value: Baseline,
) -> dict[Path, str]:
    result: dict[Path, str] = {}
    for relative_path, content in blocks(value).items():
        path = repository / relative_path
        try:
            current = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise BaselineError(f"cannot read {relative_path}: {exc}") from exc
        start, end = MARKERS[relative_path]
        result[path] = replace_block(
            current,
            start,
            end,
            content,
            relative_path,
        )
    return result


def check_documents(repository: Path, value: Baseline) -> list[str]:
    drift: list[str] = []
    for path, expected in expected_documents(repository, value).items():
        if path.read_text(encoding="utf-8") != expected:
            drift.append(str(path.relative_to(repository)).replace("\\", "/"))
    return sorted(drift)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def apply_documents(repository: Path, value: Baseline) -> list[str]:
    changed: list[str] = []
    for path, expected in expected_documents(repository, value).items():
        if path.read_text(encoding="utf-8") == expected:
            continue
        write_atomic(path, expected)
        changed.append(str(path.relative_to(repository)).replace("\\", "/"))
    return sorted(changed)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic counters and verify or update "
            "managed documentation baseline blocks."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--database", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def print_summary(value: Baseline) -> None:
    state = "verified" if value.sqlite_verified else "derived"
    print("Documentation baseline")
    print("----------------------")
    print(f"Tests                : {value.tests}")
    print(f"Master CSV files     : {value.csv_files}")
    print(f"Master rows          : {value.master_rows}")
    print(f"Configuration values : {value.configuration_values}")
    print(f"Import specs         : {value.configuration_import_specs}")
    print(f"Availability records : {value.configuration_availability}")
    print(f"Attributes           : {value.attributes}")
    print(f"Attribute categories : {value.attribute_categories}")
    print(f"SQLite tables        : {value.sqlite_tables} ({state})")
    print(f"SQLite rows          : {value.sqlite_rows} ({state})")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    try:
        value = collect_baseline(repository, arguments.database)
        if arguments.apply:
            changed = apply_documents(repository, value)
            if changed:
                print("Updated documentation baseline blocks:")
                for relative_path in changed:
                    print(f"  {relative_path}")
            else:
                print("Documentation baseline blocks are already current.")
        if arguments.check:
            drift = check_documents(repository, value)
            if drift:
                print(
                    "ERROR: documentation baseline drift detected:",
                    file=sys.stderr,
                )
                for relative_path in drift:
                    print(f"  {relative_path}", file=sys.stderr)
                print(
                    "Run: python tools/dkb.py documentation-baseline --apply",
                    file=sys.stderr,
                )
                return 1
            print("Documentation baseline blocks: PASS")
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, render_json(value))
            print(f"JSON baseline written to {arguments.json_path}")
        if arguments.markdown is not None:
            write_atomic(arguments.markdown, render_markdown(value))
            print(f"Markdown baseline written to {arguments.markdown}")
        print_summary(value)
        return 0
    except BaselineError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
