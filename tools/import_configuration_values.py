#!/usr/bin/env python3
"""Apply or verify declarative configuration-attribute value imports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SPEC_VERSION = 1
SPEC_KIND = "configuration_attribute_values"
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
TOP_LEVEL_KEYS = {
    "version",
    "kind",
    "id_start",
    "attribute_code",
    "attribute_contract",
    "observation_date",
    "fuel_type_code",
    "source_page",
    "source_section",
    "notes_template",
    "rows",
}
CONTRACT_KEYS = {"data_type", "unit", "status"}
ROW_REQUIRED_KEYS = {
    "configuration_code",
    "source_code",
    "value",
    "source_text",
}
ROW_OPTIONAL_KEYS = {"fuel_type_code"}
ALLOWED_PLACEHOLDERS = {
    "page",
    "section",
    "source_text",
    "value",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
}


class ImportSpecError(RuntimeError):
    """Raised when a declarative import cannot be validated safely."""


@dataclass(frozen=True)
class ImportRow:
    configuration_code: str
    source_code: str
    value: str
    source_text: str
    fuel_type_code: str | None = None


@dataclass(frozen=True)
class ImportSpec:
    path: Path
    id_start: int
    attribute_code: str
    data_type: str
    unit: str
    status: str
    observation_date: str
    fuel_type_code: str
    source_page: int
    source_section: str
    notes_template: str
    rows: tuple[ImportRow, ...]


@dataclass(frozen=True)
class ImportPlan:
    expected_rows: tuple[dict[str, str], ...]
    existing_rows: tuple[dict[str, str], ...]
    missing_rows: tuple[dict[str, str], ...]


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ImportSpecError(message)


def _strict_keys(
    payload: Mapping[str, Any],
    expected: set[str],
    *,
    label: str,
    optional: set[str] | None = None,
) -> None:
    optional_keys = optional or set()
    actual = set(payload)
    missing = expected - actual
    unknown = actual - expected - optional_keys
    _ensure(not missing, f"{label} is missing keys: {sorted(missing)}")
    _ensure(not unknown, f"{label} has unknown keys: {sorted(unknown)}")


def _require_string(value: Any, label: str, *, allow_empty: bool = False) -> str:
    _ensure(isinstance(value, str), f"{label} must be a string")
    if not allow_empty:
        _ensure(value.strip() != "", f"{label} must not be empty")
    return value


def _require_positive_integer(value: Any, label: str) -> int:
    _ensure(
        isinstance(value, int) and not isinstance(value, bool) and value > 0,
        f"{label} must be a positive integer",
    )
    return value


def _validate_iso_date(value: str, label: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ImportSpecError(f"{label} must be an ISO date: {value!r}") from exc
    _ensure(parsed.isoformat() == value, f"{label} must use YYYY-MM-DD")
    return value


def _validate_template(template: str) -> None:
    placeholders = set(re.findall(r"{([a-z_]+)}", template))
    _ensure(
        placeholders <= ALLOWED_PLACEHOLDERS,
        f"notes_template has unsupported placeholders: "
        f"{sorted(placeholders - ALLOWED_PLACEHOLDERS)}",
    )
    _ensure(
        {"page", "section", "source_text"} <= placeholders,
        "notes_template must include {page}, {section} and {source_text}",
    )
    try:
        template.format(
            page=1,
            section="section",
            source_text="field value",
            value="value",
            configuration_code="configuration",
            attribute_code="attribute",
            fuel_type_code="",
        )
    except (KeyError, ValueError) as exc:
        raise ImportSpecError(f"invalid notes_template: {exc}") from exc


def load_spec(path: Path) -> ImportSpec:
    """Load one strict versioned import specification."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ImportSpecError(f"cannot read spec {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ImportSpecError(f"invalid JSON in spec {path}: {exc}") from exc

    _ensure(isinstance(payload, dict), "spec root must be a JSON object")
    _strict_keys(payload, TOP_LEVEL_KEYS, label="spec")
    _ensure(payload["version"] == SPEC_VERSION, "unsupported spec version")
    _ensure(payload["kind"] == SPEC_KIND, "unsupported spec kind")

    contract = payload["attribute_contract"]
    _ensure(isinstance(contract, dict), "attribute_contract must be an object")
    _strict_keys(contract, CONTRACT_KEYS, label="attribute_contract")

    rows_payload = payload["rows"]
    _ensure(isinstance(rows_payload, list) and rows_payload, "rows must be a non-empty list")

    rows: list[ImportRow] = []
    seen_configurations: set[tuple[str, str]] = set()
    for index, item in enumerate(rows_payload, start=1):
        label = f"rows[{index}]"
        _ensure(isinstance(item, dict), f"{label} must be an object")
        _strict_keys(
            item,
            ROW_REQUIRED_KEYS,
            optional=ROW_OPTIONAL_KEYS,
            label=label,
        )
        configuration_code = _require_string(
            item["configuration_code"],
            f"{label}.configuration_code",
        )
        source_code = _require_string(item["source_code"], f"{label}.source_code")
        value = _require_string(item["value"], f"{label}.value")
        source_text = _require_string(item["source_text"], f"{label}.source_text")
        row_fuel = item.get("fuel_type_code")
        if row_fuel is not None:
            row_fuel = _require_string(
                row_fuel,
                f"{label}.fuel_type_code",
                allow_empty=True,
            )
        semantic_key = (
            configuration_code,
            "" if row_fuel is None else row_fuel,
        )
        _ensure(
            semantic_key not in seen_configurations,
            f"{label} duplicates configuration and fuel context: {semantic_key}",
        )
        seen_configurations.add(semantic_key)
        rows.append(
            ImportRow(
                configuration_code=configuration_code,
                source_code=source_code,
                value=value,
                source_text=source_text,
                fuel_type_code=row_fuel,
            )
        )

    observation_date = _validate_iso_date(
        _require_string(payload["observation_date"], "observation_date"),
        "observation_date",
    )
    notes_template = _require_string(payload["notes_template"], "notes_template")
    _validate_template(notes_template)

    return ImportSpec(
        path=path.resolve(),
        id_start=_require_positive_integer(payload["id_start"], "id_start"),
        attribute_code=_require_string(payload["attribute_code"], "attribute_code"),
        data_type=_require_string(contract["data_type"], "attribute_contract.data_type"),
        unit=_require_string(contract["unit"], "attribute_contract.unit", allow_empty=True),
        status=_require_string(contract["status"], "attribute_contract.status"),
        observation_date=observation_date,
        fuel_type_code=_require_string(
            payload["fuel_type_code"],
            "fuel_type_code",
            allow_empty=True,
        ),
        source_page=_require_positive_integer(payload["source_page"], "source_page"),
        source_section=_require_string(payload["source_section"], "source_section"),
        notes_template=notes_template,
        rows=tuple(rows),
    )


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read one UTF-8 master-data CSV."""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            _ensure(reader.fieldnames is not None, f"missing CSV header: {path}")
            return list(reader.fieldnames), list(reader)
    except OSError as exc:
        raise ImportSpecError(f"cannot read CSV {path}: {exc}") from exc


def _single_by_code(rows: Iterable[dict[str, str]], code: str, label: str) -> dict[str, str]:
    matches = [row for row in rows if row.get("code") == code]
    _ensure(len(matches) == 1, f"expected exactly one {label} {code!r}")
    return matches[0]


def _validate_value(data_type: str, value: str, label: str) -> None:
    if data_type == "integer":
        _ensure(
            re.fullmatch(r"-?(?:0|[1-9][0-9]*)", value) is not None,
            f"{label} must be a canonical integer",
        )
        return
    if data_type == "decimal":
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ImportSpecError(f"{label} must be a decimal") from exc
        _ensure(parsed.is_finite(), f"{label} must be finite")
        return
    if data_type == "boolean":
        _ensure(value in {"true", "false"}, f"{label} must be true or false")
        return
    if data_type in {"string", "enum"}:
        _ensure(value != "", f"{label} must not be empty")
        return
    raise ImportSpecError(f"unsupported attribute data_type: {data_type!r}")


def _row_code(
    configuration_code: str,
    attribute_code: str,
    fuel_type_code: str,
    observation_date: str,
) -> str:
    parts = [configuration_code, attribute_code]
    if fuel_type_code:
        parts.append(fuel_type_code)
    parts.append(observation_date.replace("-", ""))
    return "_".join(parts)


def build_expected_rows(repository: Path, spec: ImportSpec) -> tuple[dict[str, str], ...]:
    """Build exact target CSV rows after validating all repository references."""
    master = repository / "data" / "master"
    _, attributes = read_csv(master / "attributes.csv")
    _, configurations = read_csv(master / "configurations.csv")
    _, sources = read_csv(master / "sources.csv")
    _, source_configurations = read_csv(master / "source_configurations.csv")
    _, existing_values = read_csv(master / "configuration_attribute_values.csv")

    attribute = _single_by_code(attributes, spec.attribute_code, "attribute")
    expected_contract = {
        "data_type": spec.data_type,
        "unit": spec.unit,
        "status": spec.status,
    }
    actual_contract = {
        "data_type": attribute.get("data_type", ""),
        "unit": attribute.get("unit", ""),
        "status": attribute.get("status", ""),
    }
    _ensure(
        actual_contract == expected_contract,
        f"attribute contract differs for {spec.attribute_code!r}: "
        f"expected {expected_contract}, found {actual_contract}",
    )

    configuration_codes = {row.get("code", "") for row in configurations}
    sources_by_code = {row.get("code", ""): row for row in sources}
    source_pairs = {
        (row.get("source_code", ""), row.get("configuration_code", ""))
        for row in source_configurations
    }
    known_fuels = {
        row.get("fuel_type_code", "")
        for row in existing_values
        if row.get("fuel_type_code", "")
    }

    result: list[dict[str, str]] = []
    for offset, row in enumerate(spec.rows):
        label = f"rows[{offset + 1}]"
        _ensure(
            row.configuration_code in configuration_codes,
            f"{label} references unknown configuration {row.configuration_code!r}",
        )
        source = sources_by_code.get(row.source_code)
        _ensure(source is not None, f"{label} references unknown source {row.source_code!r}")
        _ensure(
            (row.source_code, row.configuration_code) in source_pairs,
            f"{label} source does not document configuration",
        )
        _ensure(source.get("status") == "active", f"{label} source is not active")
        _ensure(
            re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", "")) is not None,
            f"{label} source has no valid SHA-256",
        )
        _ensure(source.get("file_path", "") != "", f"{label} source has no file path")

        fuel = spec.fuel_type_code if row.fuel_type_code is None else row.fuel_type_code
        if fuel:
            _ensure(
                fuel in known_fuels,
                f"{label} uses unknown fuel_type_code {fuel!r}",
            )

        _validate_value(spec.data_type, row.value, f"{label}.value")
        notes = spec.notes_template.format(
            page=spec.source_page,
            section=spec.source_section,
            source_text=row.source_text,
            value=row.value,
            configuration_code=row.configuration_code,
            attribute_code=spec.attribute_code,
            fuel_type_code=fuel,
        )
        _ensure(notes.strip() != "", f"{label} generated empty notes")

        result.append(
            {
                "id": str(spec.id_start + offset),
                "code": _row_code(
                    row.configuration_code,
                    spec.attribute_code,
                    fuel,
                    spec.observation_date,
                ),
                "configuration_code": row.configuration_code,
                "attribute_code": spec.attribute_code,
                "fuel_type_code": fuel,
                "value": row.value,
                "observation_date": spec.observation_date,
                "source_code": row.source_code,
                "notes": notes,
            }
        )

    ids = [row["id"] for row in result]
    codes = [row["code"].casefold() for row in result]
    semantic = [
        (
            row["configuration_code"],
            row["attribute_code"],
            row["fuel_type_code"],
            row["observation_date"],
        )
        for row in result
    ]
    _ensure(len(ids) == len(set(ids)), "spec generates duplicate IDs")
    _ensure(len(codes) == len(set(codes)), "spec generates duplicate codes")
    _ensure(len(semantic) == len(set(semantic)), "spec generates duplicate observations")
    return tuple(result)


def plan_import(repository: Path, spec: ImportSpec) -> ImportPlan:
    """Classify expected rows as exact-existing or missing; reject conflicts."""
    expected = build_expected_rows(repository, spec)
    path = repository / "data" / "master" / "configuration_attribute_values.csv"
    fields, current = read_csv(path)
    _ensure(tuple(fields) == VALUE_FIELDS, "configuration value CSV header differs")

    by_id = {row["id"]: row for row in current}
    by_code = {row["code"].casefold(): row for row in current}
    by_semantic = {
        (
            row["configuration_code"],
            row["attribute_code"],
            row["fuel_type_code"],
            row["observation_date"],
        ): row
        for row in current
    }

    exact: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    for row in expected:
        semantic = (
            row["configuration_code"],
            row["attribute_code"],
            row["fuel_type_code"],
            row["observation_date"],
        )
        candidates = [
            by_id.get(row["id"]),
            by_code.get(row["code"].casefold()),
            by_semantic.get(semantic),
        ]
        present = [candidate for candidate in candidates if candidate is not None]
        if not present:
            missing.append(row)
            continue
        _ensure(
            all(candidate == row for candidate in present),
            f"existing row conflicts with spec: {row['code']}",
        )
        exact.append(row)

    if missing:
        current_ids = [int(row["id"]) for row in current]
        current_max = max(current_ids, default=0)
        first_missing = int(missing[0]["id"])
        _ensure(
            first_missing == current_max + 1,
            f"first missing ID must be {current_max + 1}, found {first_missing}",
        )
        _ensure(
            [int(row["id"]) for row in missing]
            == list(range(first_missing, first_missing + len(missing))),
            "missing IDs must form a contiguous suffix",
        )
    return ImportPlan(
        expected_rows=expected,
        existing_rows=tuple(exact),
        missing_rows=tuple(missing),
    )


def _write_csv_atomic(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[dict[str, str]],
) -> None:
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                lineterminator="\n",
            )
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


def apply_import(repository: Path, spec: ImportSpec) -> ImportPlan:
    """Append only missing exact rows atomically and return the verified plan."""
    plan = plan_import(repository, spec)
    if not plan.missing_rows:
        return plan

    path = repository / "data" / "master" / "configuration_attribute_values.csv"
    fields, current = read_csv(path)
    _write_csv_atomic(path, fields, [*current, *plan.missing_rows])

    verified = plan_import(repository, spec)
    _ensure(not verified.missing_rows, "rows remain missing after apply")
    return verified


def verify_import(repository: Path, spec: ImportSpec) -> ImportPlan:
    """Require every spec row to exist exactly."""
    plan = plan_import(repository, spec)
    _ensure(
        not plan.missing_rows,
        f"spec has {len(plan.missing_rows)} missing rows",
    )
    return plan


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _compact_text(text: str) -> str:
    translated = text.translate(str.maketrans({"ł": "l", "Ł": "L"}))
    decomposed = unicodedata.normalize("NFKD", translated)
    plain = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    return "".join(
        character
        for character in plain.casefold()
        if character.isalnum()
    )


def _decode_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "cp1250", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_page_candidates(path: Path, page: int) -> list[tuple[str, str]]:
    """Extract one PDF page through available deterministic text backends."""
    candidates: list[tuple[str, str]] = []
    executable = shutil.which("pdftotext")
    if executable:
        for label, mode in (
            ("pdftotext-raw", ("-raw",)),
            ("pdftotext-layout", ("-layout",)),
            ("pdftotext-default", ()),
        ):
            completed = subprocess.run(
                [
                    executable,
                    "-f",
                    str(page),
                    "-l",
                    str(page),
                    *mode,
                    str(path),
                    "-",
                ],
                check=False,
                capture_output=True,
            )
            if completed.returncode == 0 and completed.stdout:
                text = _decode_bytes(completed.stdout).replace("\x0c", "")
                if _compact_text(text):
                    candidates.append((label, text))

    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
        except ImportError:
            continue
        reader = module.PdfReader(str(path))
        _ensure(len(reader.pages) >= page, f"PDF has fewer than {page} pages: {path}")
        text = reader.pages[page - 1].extract_text() or ""
        if _compact_text(text):
            candidates.append((module_name, text))

    unique: list[tuple[str, str]] = []
    signatures: set[str] = set()
    for label, text in candidates:
        signature = _compact_text(text)
        if signature not in signatures:
            signatures.add(signature)
            unique.append((label, text))
    _ensure(unique, f"cannot extract page {page}: {path}")
    return unique


def verify_registered_sources(
    repository: Path,
    spec: ImportSpec,
    *,
    verify_text: bool = True,
) -> None:
    """Verify registry metadata, file hashes and optional page text."""
    master = repository / "data" / "master"
    _, sources = read_csv(master / "sources.csv")
    sources_by_code = {row["code"]: row for row in sources}

    for row in spec.rows:
        source = sources_by_code.get(row.source_code)
        _ensure(source is not None, f"unknown source {row.source_code!r}")
        path = repository / source["file_path"]
        _ensure(path.is_file(), f"registered source file is missing: {path}")
        actual = _file_sha256(path)
        _ensure(
            actual == source["sha256"],
            f"registered source SHA-256 differs: {path.name}",
        )
        if not verify_text:
            continue
        required_section = _compact_text(spec.source_section)
        required_text = _compact_text(row.source_text)
        found = False
        for _, text in extract_page_candidates(path, spec.source_page):
            compact = _compact_text(text)
            if required_section in compact and required_text in compact:
                found = True
                break
        _ensure(
            found,
            f"page {spec.source_page} does not contain the declared "
            f"section and source text for {row.source_code}",
        )


def _summary(spec: ImportSpec, plan: ImportPlan, mode: str) -> None:
    print(f"Spec     : {spec.path}")
    print(f"Attribute: {spec.attribute_code}")
    print(f"Rows     : {len(plan.expected_rows)}")
    print(f"Existing : {len(plan.existing_rows)}")
    print(f"Missing  : {len(plan.missing_rows)}")
    print(f"Mode     : {mode}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate, apply or verify one declarative "
            "configuration-value import."
        ),
    )
    parser.add_argument("--spec", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument(
        "--skip-source-text",
        action="store_true",
        help="Verify registered file hashes but skip PDF text extraction.",
    )
    parser.add_argument(
        "--skip-source-files",
        action="store_true",
        help="Skip source file hash and text checks.",
    )
    parser.add_argument(
        "--repository",
        type=Path,
        default=None,
        help="Repository root; defaults to the parent of tools.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = (
        arguments.repository.expanduser().resolve()
        if arguments.repository is not None
        else Path(__file__).resolve().parents[1]
    )
    try:
        spec = load_spec(arguments.spec.expanduser().resolve())
        if not arguments.skip_source_files:
            verify_registered_sources(
                repository,
                spec,
                verify_text=not arguments.skip_source_text,
            )

        if arguments.apply:
            plan = apply_import(repository, spec)
            mode = "apply"
        elif arguments.verify:
            plan = verify_import(repository, spec)
            mode = "verify"
        else:
            plan = plan_import(repository, spec)
            mode = "plan"

        _summary(spec, plan, mode)
        print("PASS")
        return 0
    except ImportSpecError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
