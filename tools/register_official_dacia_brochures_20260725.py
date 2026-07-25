#!/usr/bin/env python3
"""Register and verify five official Polish Dacia brochure PDF sources."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
RECEIPT_PATH = ROOT / "project" / "sources" / "official-dacia-brochures-20260725.json"

SOURCE_FIELDS = (
    "id",
    "code",
    "source_type",
    "title",
    "publisher",
    "market",
    "document_date",
    "external_reference",
    "file_path",
    "sha256",
    "status",
    "notes",
)
SOURCE_MODEL_FIELDS = (
    "id",
    "source_code",
    "model_code",
    "relationship",
    "notes",
)

EXPECTED = (
    {
        "id": "23",
        "source_model_id": "30",
        "source_code": "src_pl_bigster_brochure_20251210",
        "title": "DACIA BIGSTER broszura",
        "document_date": "2025-12-10",
        "url": "https://cdn.group.renault.com/dac/pl/pdf/broszury/bigster-brochure.pdf.asset.pdf/5f71268df9.pdf",
        "file_path": "PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf",
        "pages": 24,
        "publication_marker": "10.12.2025",
        "model_code": "bigster",
        "bytes": 10359318,
        "sha256": "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74",
        "notes": (
            "Official Polish Bigster brochure published 2025-12-10. Source registration only; "
            "technical observations require separate context-preserving imports."
        ),
    },
    {
        "id": "24",
        "source_model_id": "31",
        "source_code": "src_pl_jogger_brochure_20251217",
        "title": "DACIA JOGGER broszura",
        "document_date": "2025-12-17",
        "url": "https://cdn.group.renault.com/dac/pl/pdf/broszury/jogger-brochure.pdf.asset.pdf/6b1235f90d.pdf",
        "file_path": "PDF/Broszury/DACIA JOGGER broszura 20251217.pdf",
        "pages": 23,
        "publication_marker": "17.12.2025",
        "model_code": "jogger",
        "bytes": 3636538,
        "sha256": "eb4d44436c314d7e38d018af68e7475f03122a27f1e3f30e768f60432d338dd6",
        "notes": (
            "Official Polish Jogger brochure published 2025-12-17. Source registration only; "
            "seat-layout, seat-state and measurement-basis context must be preserved."
        ),
    },
    {
        "id": "25",
        "source_model_id": "32",
        "source_code": "src_pl_sandero_brochure_20260202",
        "title": "DACIA SANDERO broszura",
        "document_date": "2026-02-02",
        "url": "https://cdn.group.renault.com/dac/pl/pdf/broszury/sandero-brochure.pdf.asset.pdf/b83cd5df5f.pdf",
        "file_path": "PDF/Broszury/DACIA SANDERO broszura 20260202.pdf",
        "pages": 21,
        "publication_marker": "02.02.2026",
        "model_code": "sandero_iii",
        "bytes": 8358370,
        "sha256": "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97",
        "notes": (
            "Official Polish Sandero brochure published 2026-02-02. Source registration only; "
            "gear-specific elasticity and cargo measurement contexts remain deferred."
        ),
    },
    {
        "id": "26",
        "source_model_id": "33",
        "source_code": "src_pl_sandero_stepway_brochure_20260202",
        "title": "DACIA SANDERO STEPWAY broszura",
        "document_date": "2026-02-02",
        "url": "https://cdn.group.renault.com/dac/pl/pdf/broszury/sandero-stepway-brochure.pdf.asset.pdf/e154a3e830.pdf",
        "file_path": "PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf",
        "pages": 21,
        "publication_marker": "02.02.2026",
        "model_code": "sandero_stepway_iii",
        "bytes": 8541016,
        "sha256": "800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48",
        "notes": (
            "Official Polish Sandero Stepway brochure published 2026-02-02. Source registration "
            "only; gear-specific elasticity and multi-basis cargo values remain deferred."
        ),
    },
    {
        "id": "27",
        "source_model_id": "34",
        "source_code": "src_pl_duster_mini_brochure_20251020",
        "title": "DACIA DUSTER mini broszura",
        "document_date": "2025-10-20",
        "url": "https://cdn.group.renault.com/dac/pl/pdf/mini-broszury/new-duster-mini-brochure_2024.pdf.asset.pdf/b2659c32d0.pdf",
        "file_path": "PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf",
        "pages": 25,
        "publication_marker": "20.10.2025",
        "model_code": "duster_iii",
        "bytes": 9712859,
        "sha256": "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8",
        "notes": (
            "Official Polish Duster mini brochure published 2025-10-20. Its Eco-G 120 technical "
            "table describes the manual powertrain and must not populate automatic configurations."
        ),
    },
)

OWNED_CODES = {row["source_code"] for row in EXPECTED}
OWNED_SOURCE_IDS = {row["id"] for row in EXPECTED}
OWNED_SOURCE_MODEL_IDS = {row["source_model_id"] for row in EXPECTED}


class ContractError(RuntimeError):
    """Raised when the source-registration contract cannot be reproduced."""


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ContractError(f"missing CSV header: {path}")
        return list(reader)


def _require_header(path: Path, fields: Sequence[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        header = next(csv.reader(handle), None)
    _ensure(header == list(fields), f"unexpected header in {path}: {header!r}")


def _write_rows_atomic(
    path: Path,
    fields: Sequence[str],
    rows: Iterable[dict[str, str]],
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_receipt() -> dict[str, object]:
    payload = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    _ensure(payload.get("version") == 1, "unexpected brochure receipt version")
    _ensure(
        payload.get("kind") == "official_dacia_brochure_source_receipt",
        "unexpected brochure receipt kind",
    )
    _ensure(payload.get("retrieved_on") == "2026-07-25", "unexpected retrieval date")
    _ensure(payload.get("publisher") == "Dacia", "unexpected receipt publisher")
    _ensure(payload.get("market") == "PL", "unexpected receipt market")
    sources = payload.get("sources")
    _ensure(isinstance(sources, list) and len(sources) == 5, "receipt must contain five sources")
    actual = {row.get("source_code"): row for row in sources if isinstance(row, dict)}
    _ensure(set(actual) == OWNED_CODES, "receipt source-code coverage mismatch")
    for expected in EXPECTED:
        row = actual[expected["source_code"]]
        for field in (
            "source_code",
            "title",
            "document_date",
            "url",
            "file_path",
            "pages",
            "publication_marker",
            "model_code",
            "bytes",
            "sha256",
        ):
            _ensure(row.get(field) == expected[field], f"receipt mismatch: {expected['source_code']} {field}")
    return payload


def _verify_archives() -> None:
    for expected in EXPECTED:
        path = ROOT / expected["file_path"]
        _ensure(path.is_file(), f"archived brochure missing: {path}")
        _ensure(path.stat().st_size == expected["bytes"], f"brochure size mismatch: {path}")
        _ensure(_sha256(path) == expected["sha256"], f"brochure SHA-256 mismatch: {path}")
        with path.open("rb") as handle:
            _ensure(handle.read(5) == b"%PDF-", f"archived source is not a PDF: {path}")


def _expected_source_rows() -> list[dict[str, str]]:
    return [
        {
            "id": row["id"],
            "code": row["source_code"],
            "source_type": "brochure_pdf",
            "title": row["title"],
            "publisher": "Dacia",
            "market": "PL",
            "document_date": row["document_date"],
            "external_reference": row["url"],
            "file_path": row["file_path"],
            "sha256": row["sha256"],
            "status": "active",
            "notes": row["notes"],
        }
        for row in EXPECTED
    ]


def _expected_source_model_rows() -> list[dict[str, str]]:
    return [
        {
            "id": row["source_model_id"],
            "source_code": row["source_code"],
            "model_code": row["model_code"],
            "relationship": "brochure_for",
            "notes": (
                "Official Polish model-range brochure. Registration does not import or supersede "
                "configuration-level observations."
            ),
        }
        for row in EXPECTED
    ]


def _semantic(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def _replace_owned_rows(
    path: Path,
    fields: Sequence[str],
    expected: list[dict[str, str]],
    owned_codes: set[str],
    code_field: str,
    owned_ids: set[str],
) -> None:
    _require_header(path, fields)
    rows = _read_rows(path)
    retained = [row for row in rows if row.get(code_field) not in owned_codes]
    _ensure(
        not any(row.get("id") in owned_ids for row in retained),
        f"reserved identifiers are already used in {path}",
    )
    combined = [*retained, *expected]
    combined.sort(key=lambda row: int(row["id"]))
    _write_rows_atomic(path, fields, combined)


def _verify_models() -> None:
    models = {
        row["code"]
        for row in _read_rows(MASTER / "models.csv")
        if row.get("status") == "active"
    }
    expected_models = {row["model_code"] for row in EXPECTED}
    _ensure(expected_models <= models, "one or more brochure model codes are not active")


def _verify_registered_rows() -> None:
    source_path = MASTER / "sources.csv"
    model_path = MASTER / "source_models.csv"
    _require_header(source_path, SOURCE_FIELDS)
    _require_header(model_path, SOURCE_MODEL_FIELDS)

    actual_sources = [row for row in _read_rows(source_path) if row.get("code") in OWNED_CODES]
    actual_models = [
        row for row in _read_rows(model_path) if row.get("source_code") in OWNED_CODES
    ]
    _ensure(
        _semantic(actual_sources, SOURCE_FIELDS)
        == _semantic(_expected_source_rows(), SOURCE_FIELDS),
        "registered brochure source rows differ from the contract",
    )
    _ensure(
        _semantic(actual_models, SOURCE_MODEL_FIELDS)
        == _semantic(_expected_source_model_rows(), SOURCE_MODEL_FIELDS),
        "brochure source-model relationships differ from the contract",
    )


def _verify_registration_only_boundary() -> None:
    excluded = {"sources.csv", "source_models.csv"}
    for path in sorted(MASTER.rglob("*.csv")):
        if path.name in excluded:
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or "source_code" not in reader.fieldnames:
                continue
            for row in reader:
                _ensure(
                    row.get("source_code") not in OWNED_CODES,
                    f"brochure registration unexpectedly materialized observations in {path}",
                )


def check() -> None:
    _load_receipt()
    _verify_archives()
    _verify_models()
    _verify_registered_rows()
    _verify_registration_only_boundary()


def apply() -> None:
    _load_receipt()
    _verify_archives()
    _verify_models()
    _replace_owned_rows(
        MASTER / "sources.csv",
        SOURCE_FIELDS,
        _expected_source_rows(),
        OWNED_CODES,
        "code",
        OWNED_SOURCE_IDS,
    )
    _replace_owned_rows(
        MASTER / "source_models.csv",
        SOURCE_MODEL_FIELDS,
        _expected_source_model_rows(),
        OWNED_CODES,
        "source_code",
        OWNED_SOURCE_MODEL_IDS,
    )
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
        print(f"ERROR: {exc}", file=os.sys.stderr)
        return 1
    print("PASS: official Dacia brochure source registration contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
