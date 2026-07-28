#!/usr/bin/env python3
"""Build or verify a deterministic candidate-only ledger for registered PDFs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / "project" / "sources" / "official-dacia-brochures-20260725.json"
DEFAULT_JSON = ROOT / "data" / "reporting" / "official_dacia_pdf_candidate_ledger.json"
DEFAULT_MARKDOWN = ROOT / "data" / "reporting" / "official_dacia_pdf_candidate_ledger.md"
CANONICAL_BACKENDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("pdftotext-layout", ("-layout",)),
    ("pdftotext-default", ()),
    ("pdftotext-raw", ("-raw",)),
)
REVIEW_STATUSES = {
    "unreviewed_candidate",
    "requires_visual_review",
    "ambiguous_source_evidence",
    "explicit_non_import",
}
CANDIDATE_KINDS = {
    "heading",
    "table_row",
    "scalar_text",
    "range_text",
    "availability_text",
    "unclassified_text",
}
REQUIRED_CANDIDATE_FIELDS = (
    "candidate_id",
    "source_code",
    "source_file_path",
    "source_sha256",
    "document_date",
    "model_code",
    "page",
    "backend",
    "backend_version",
    "rule_code",
    "line_start",
    "line_end",
    "exact_text",
    "normalized_text",
    "candidate_kind",
    "review_status",
)


class CandidateLedgerError(RuntimeError):
    """Raised when source integrity or the ledger contract differs."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateLedgerError(message)


def relative_repository_path(path: Path, repository: Path) -> str:
    try:
        return path.resolve().relative_to(repository.resolve()).as_posix()
    except ValueError as exc:
        raise CandidateLedgerError(f"path is outside repository: {path}") from exc


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(text: str) -> str:
    """Return stable Unicode text with collapsed horizontal/vertical whitespace."""
    value = text.replace("\r\n", "\n").replace("\r", "\n")
    value = unicodedata.normalize("NFKC", value)
    return " ".join(value.split())


def candidate_id(
    source_sha256: str,
    page: int,
    rule_code: str,
    line_start: int,
    line_end: int,
    normalized_text: str,
) -> str:
    components = (
        source_sha256,
        str(page),
        rule_code,
        str(line_start),
        str(line_end),
        normalized_text,
    )
    return hashlib.sha256("\x1f".join(components).encode("utf-8")).hexdigest()


_RANGE_PATTERN = re.compile(
    r"(?<!\d)\d+(?:[.,]\d+)?\s*(?:-|–|—|\bdo\b)\s*\d+(?:[.,]\d+)?",
    re.IGNORECASE,
)
_TABLE_PATTERN = re.compile(r"\S(?:.*?\S)?(?: {2,}|\t+)\S")
_NUMBER_PATTERN = re.compile(r"\d")
_UNIT_PATTERN = re.compile(
    r"(?:\b(?:mm|cm|dm|m|km|kg|g|l|kwh|kw|km/h|nm|s|sek|obr\.?/min|co2|g/km|l/100\s*km)\b|:)",
    re.IGNORECASE,
)
_AVAILABILITY_MARKERS = (
    "seryjn",
    "standard",
    "opcj",
    "opcjonal",
    "niedostępn",
    "niedostepn",
    "pakiet",
)


def classify_candidate(exact_text: str) -> tuple[str, str]:
    normalized = normalize_text(exact_text)
    folded = normalized.casefold()
    if _TABLE_PATTERN.search(exact_text):
        return "layout_table_row", "table_row"
    if any(marker in folded for marker in _AVAILABILITY_MARKERS):
        return "surface_availability_marker", "availability_text"
    if _RANGE_PATTERN.search(normalized):
        return "numeric_range_surface", "range_text"

    letters = [character for character in normalized if character.isalpha()]
    if (
        3 <= len(letters)
        and len(normalized) <= 140
        and sum(character.isupper() for character in letters) / len(letters) >= 0.85
    ):
        return "uppercase_heading_surface", "heading"

    if _NUMBER_PATTERN.search(normalized) and _UNIT_PATTERN.search(normalized):
        return "numeric_scalar_surface", "scalar_text"
    return "nonempty_line", "unclassified_text"


def _decode_output(data: bytes) -> str:
    for encoding in ("utf-8", "cp1250", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def pdftotext_version() -> str:
    executable = shutil.which("pdftotext")
    ensure(executable is not None, "pdftotext executable is unavailable")
    completed = subprocess.run(
        [executable, "-v"],
        check=False,
        capture_output=True,
    )
    ensure(completed.returncode == 0, "cannot read pdftotext version")
    output = _decode_output(completed.stderr + completed.stdout)
    first_line = next((line.strip() for line in output.splitlines() if line.strip()), "")
    ensure(first_line, "pdftotext version output is empty")
    return first_line


def pdf_page_count(path: Path) -> int:
    executable = shutil.which("pdfinfo")
    ensure(executable is not None, "pdfinfo executable is unavailable")
    completed = subprocess.run(
        [executable, str(path)],
        check=False,
        capture_output=True,
    )
    ensure(completed.returncode == 0, f"cannot inspect PDF page count: {path.name}")
    output = _decode_output(completed.stdout + completed.stderr)
    match = re.search(r"^Pages:\s*(\d+)\s*$", output, re.MULTILINE)
    ensure(match is not None, f"PDF page count is missing: {path.name}")
    return int(match.group(1))


def split_document_pages(text: str, declared_pages: int) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    pages = normalized.split("\x0c")
    while len(pages) > declared_pages and pages[-1] == "":
        pages.pop()
    ensure(
        len(pages) == declared_pages,
        f"extracted page count differs: expected {declared_pages}, got {len(pages)}",
    )
    return pages


def extract_document_candidates(path: Path, declared_pages: int) -> dict[str, list[str]]:
    """Extract all pages once per canonical backend."""
    executable = shutil.which("pdftotext")
    ensure(executable is not None, "pdftotext executable is unavailable")
    extracted: dict[str, list[str]] = {}
    for backend, mode in CANONICAL_BACKENDS:
        completed = subprocess.run(
            [
                executable,
                *mode,
                "-enc",
                "UTF-8",
                str(path),
                "-",
            ],
            check=False,
            capture_output=True,
        )
        ensure(
            completed.returncode == 0,
            f"{backend} extraction failed for {path.name}",
        )
        extracted[backend] = split_document_pages(
            _decode_output(completed.stdout),
            declared_pages,
        )
    return extracted


def load_receipt(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidateLedgerError(f"cannot read receipt: {path}") from exc
    ensure(isinstance(payload, dict), "receipt must be a JSON object")
    ensure(payload.get("version") == 1, "receipt version differs")
    ensure(
        payload.get("kind") == "official_dacia_brochure_source_receipt",
        "receipt kind differs",
    )
    sources = payload.get("sources")
    ensure(isinstance(sources, list) and sources, "receipt sources are missing")
    required = {
        "source_code",
        "file_path",
        "sha256",
        "bytes",
        "pages",
        "document_date",
        "model_code",
    }
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in sources:
        ensure(isinstance(item, dict), "receipt source must be an object")
        ensure(required <= set(item), "receipt source fields are missing")
        code = str(item["source_code"])
        ensure(code and code not in seen, f"duplicate receipt source: {code}")
        seen.add(code)
        normalized.append(dict(item))
    return sorted(normalized, key=lambda item: str(item["source_code"]))


def verify_source(
    repository: Path,
    source: Mapping[str, Any],
    *,
    page_counter: Callable[[Path], int],
) -> Path:
    relative = Path(str(source["file_path"]))
    ensure(not relative.is_absolute(), "receipt source path must be relative")
    path = repository / relative
    ensure(path.is_file(), f"registered PDF is missing: {relative.as_posix()}")
    expected_bytes = int(source["bytes"])
    ensure(
        path.stat().st_size == expected_bytes,
        f"registered PDF byte size differs: {relative.as_posix()}",
    )
    actual_sha = file_sha256(path)
    ensure(
        actual_sha == str(source["sha256"]),
        f"registered PDF SHA-256 differs: {relative.as_posix()}",
    )
    expected_pages = int(source["pages"])
    ensure(
        page_counter(path) == expected_pages,
        f"registered PDF page count differs: {relative.as_posix()}",
    )
    return path


def _candidate_record(
    source: Mapping[str, Any],
    *,
    page: int,
    backend: str,
    backend_version: str,
    rule_code: str,
    line_start: int,
    line_end: int,
    exact_text: str,
    candidate_kind: str,
    review_status: str,
) -> dict[str, Any]:
    normalized = normalize_text(exact_text)
    ensure(candidate_kind in CANDIDATE_KINDS, f"unsupported candidate kind: {candidate_kind}")
    ensure(review_status in REVIEW_STATUSES, f"unsupported review status: {review_status}")
    record = {
        "candidate_id": candidate_id(
            str(source["sha256"]),
            page,
            rule_code,
            line_start,
            line_end,
            normalized,
        ),
        "source_code": str(source["source_code"]),
        "source_file_path": Path(str(source["file_path"])).as_posix(),
        "source_sha256": str(source["sha256"]),
        "document_date": str(source["document_date"]),
        "model_code": str(source["model_code"]),
        "page": page,
        "backend": backend,
        "backend_version": backend_version,
        "rule_code": rule_code,
        "line_start": line_start,
        "line_end": line_end,
        "exact_text": exact_text,
        "normalized_text": normalized,
        "candidate_kind": candidate_kind,
        "review_status": review_status,
    }
    ensure(tuple(record) == REQUIRED_CANDIDATE_FIELDS, "candidate field order differs")
    return record


def page_candidates(
    source: Mapping[str, Any],
    page: int,
    extracted: Mapping[str, Sequence[str]],
    backend_version: str,
) -> tuple[str, list[dict[str, Any]]]:
    selected_backend = CANONICAL_BACKENDS[0][0]
    page_text = ""
    for backend, _ in CANONICAL_BACKENDS:
        pages = extracted.get(backend)
        ensure(pages is not None, f"canonical backend output is missing: {backend}")
        ensure(len(pages) >= page, f"canonical backend page is missing: {backend} page {page}")
        candidate_text = str(pages[page - 1])
        if normalize_text(candidate_text):
            selected_backend = backend
            page_text = candidate_text
            break

    if not normalize_text(page_text):
        return selected_backend, [
            _candidate_record(
                source,
                page=page,
                backend=selected_backend,
                backend_version=backend_version,
                rule_code="empty_page_text",
                line_start=0,
                line_end=0,
                exact_text="",
                candidate_kind="unclassified_text",
                review_status="requires_visual_review",
            )
        ]

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(page_text.split("\n"), start=1):
        if not normalize_text(line):
            continue
        rule_code, kind = classify_candidate(line)
        records.append(
            _candidate_record(
                source,
                page=page,
                backend=selected_backend,
                backend_version=backend_version,
                rule_code=rule_code,
                line_start=line_number,
                line_end=line_number,
                exact_text=line,
                candidate_kind=kind,
                review_status="unreviewed_candidate",
            )
        )
    ensure(records, f"non-empty page produced no candidates: page {page}")
    return selected_backend, records


def build_ledger(
    repository: Path = ROOT,
    receipt_path: Path = DEFAULT_RECEIPT,
    *,
    page_counter: Callable[[Path], int] = pdf_page_count,
    document_extractor: Callable[[Path, int], Mapping[str, Sequence[str]]] = extract_document_candidates,
    version_reader: Callable[[], str] = pdftotext_version,
) -> dict[str, Any]:
    repository = repository.resolve()
    receipt_path = receipt_path.resolve()
    receipt_relative = relative_repository_path(receipt_path, repository)
    sources = load_receipt(receipt_path)
    backend_version = version_reader()
    all_candidates: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []

    for source in sources:
        path = verify_source(repository, source, page_counter=page_counter)
        declared_pages = int(source["pages"])
        extracted = document_extractor(path, declared_pages)
        source_candidates: list[dict[str, Any]] = []
        backend_counts: Counter[str] = Counter()
        visual_pages: list[int] = []
        for page in range(1, declared_pages + 1):
            backend, records = page_candidates(
                source,
                page,
                extracted,
                backend_version,
            )
            backend_counts[backend] += 1
            if any(item["review_status"] == "requires_visual_review" for item in records):
                visual_pages.append(page)
            source_candidates.extend(records)
        source_candidates.sort(
            key=lambda item: (
                item["source_code"],
                item["page"],
                item["line_start"],
                item["line_end"],
                item["rule_code"],
                item["candidate_id"],
            )
        )
        all_candidates.extend(source_candidates)
        source_summaries.append(
            {
                "source_code": str(source["source_code"]),
                "source_file_path": Path(str(source["file_path"])).as_posix(),
                "source_sha256": str(source["sha256"]),
                "document_date": str(source["document_date"]),
                "model_code": str(source["model_code"]),
                "declared_pages": declared_pages,
                "candidate_count": len(source_candidates),
                "backend_page_counts": {
                    backend: backend_counts.get(backend, 0)
                    for backend, _ in CANONICAL_BACKENDS
                },
                "requires_visual_review_pages": visual_pages,
            }
        )

    all_candidates.sort(
        key=lambda item: (
            item["source_code"],
            item["page"],
            item["line_start"],
            item["line_end"],
            item["rule_code"],
            item["candidate_id"],
        )
    )
    ids = [item["candidate_id"] for item in all_candidates]
    ensure(len(ids) == len(set(ids)), "candidate identifiers are not unique")
    kind_counts = Counter(str(item["candidate_kind"]) for item in all_candidates)
    status_counts = Counter(str(item["review_status"]) for item in all_candidates)
    return {
        "version": 1,
        "kind": "verified_pdf_candidate_ledger",
        "receipt_path": receipt_relative,
        "canonical_backend_order": [backend for backend, _ in CANONICAL_BACKENDS],
        "backend_version": backend_version,
        "source_count": len(source_summaries),
        "page_count": sum(int(item["declared_pages"]) for item in source_summaries),
        "candidate_count": len(all_candidates),
        "candidate_kind_counts": {
            kind: kind_counts.get(kind, 0) for kind in sorted(CANDIDATE_KINDS)
        },
        "review_status_counts": {
            status: status_counts.get(status, 0) for status in sorted(REVIEW_STATUSES)
        },
        "semantic_boundaries": {
            "candidate_output_is_not_an_import_spec": True,
            "configuration_code_is_not_inferred": True,
            "attribute_code_is_not_approved": True,
            "units_are_not_canonicalized": True,
            "missing_text_is_not_negative_evidence": True,
            "master_data_changes": 0,
            "approved_import_specs_created": 0,
            "ocr": False,
            "automatic_promotion": False,
        },
        "sources": source_summaries,
        "candidates": all_candidates,
    }


def json_bytes(ledger: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def markdown_text(ledger: Mapping[str, Any]) -> str:
    lines = [
        "# Official Dacia PDF Candidate Ledger",
        "",
        "Candidate-only extraction summary. This artifact does not approve imports, infer configurations or canonicalize attributes and units.",
        "",
        "## Coverage",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Registered sources | {ledger['source_count']} |",
        f"| Declared pages | {ledger['page_count']} |",
        f"| Candidates | {ledger['candidate_count']} |",
        f"| Backend version | `{ledger['backend_version']}` |",
        "",
        "## Sources",
        "",
        "| Source | Model | Pages | Candidates | Layout | Default | Raw | Visual review pages |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for source in ledger["sources"]:
        backend_counts = source["backend_page_counts"]
        visual = ", ".join(str(page) for page in source["requires_visual_review_pages"]) or "—"
        lines.append(
            "| {source_code} | {model_code} | {declared_pages} | {candidate_count} | {layout} | {default} | {raw} | {visual} |".format(
                source_code=source["source_code"],
                model_code=source["model_code"],
                declared_pages=source["declared_pages"],
                candidate_count=source["candidate_count"],
                layout=backend_counts["pdftotext-layout"],
                default=backend_counts["pdftotext-default"],
                raw=backend_counts["pdftotext-raw"],
                visual=visual,
            )
        )

    lines.extend(["", "## Candidate kinds", "", "| Kind | Count |", "| --- | ---: |"])
    for kind, count in ledger["candidate_kind_counts"].items():
        lines.append(f"| `{kind}` | {count} |")

    lines.extend(["", "## Review statuses", "", "| Status | Count |", "| --- | ---: |"])
    for status, count in ledger["review_status_counts"].items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(
        [
            "",
            "## Promotion boundary",
            "",
            "A later, separately authored review decision must cite `candidate_id` and exact source text. Direct candidate-to-master import and direct generation of approved import specifications are forbidden.",
            "",
            "Pages with no canonical text layer are classified as `requires_visual_review`; they are never interpreted as `not_stated` or other negative evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def markdown_bytes(ledger: Mapping[str, Any]) -> bytes:
    return markdown_text(ledger).encode("utf-8")


def ensure_safe_output(path: Path, repository: Path) -> None:
    resolved = path.resolve()
    for forbidden in (repository / "data" / "master", repository / "data" / "imports"):
        try:
            resolved.relative_to(forbidden.resolve())
        except ValueError:
            continue
        raise CandidateLedgerError(f"candidate artifacts cannot be written under {forbidden.relative_to(repository)}")


def write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def verify_bytes(path: Path, expected: bytes) -> None:
    ensure(path.is_file(), f"candidate artifact is missing: {path}")
    ensure(path.read_bytes() == expected, f"candidate artifact differs: {path}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing artifacts instead of writing them.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repository = ROOT
    try:
        ensure_safe_output(args.json, repository)
        ensure_safe_output(args.markdown, repository)
        ledger = build_ledger(repository, args.receipt)
        expected_json = json_bytes(ledger)
        expected_markdown = markdown_bytes(ledger)
        if args.verify:
            verify_bytes(args.json, expected_json)
            verify_bytes(args.markdown, expected_markdown)
            action = "verified"
        else:
            write_bytes(args.json, expected_json)
            write_bytes(args.markdown, expected_markdown)
            action = "written"
    except (CandidateLedgerError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"PASS: PDF candidate ledger {action}: "
        f"sources={ledger['source_count']} pages={ledger['page_count']} "
        f"candidates={ledger['candidate_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
