#!/usr/bin/env python3
"""Review configuration gaps against relevant registered PDF source pages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import import_configuration_values


DEFAULT_REVIEW_SPEC = Path(
    "data/reporting/configuration_gap_source_review.json"
)
DEFAULT_EVIDENCE_SPEC = Path(
    "data/reporting/configuration_gap_evidence.json"
)
NOTE_PATTERN = re.compile(
    r"^Source page (?P<page>[1-9][0-9]*)"
    r"(?:, section (?P<section>[^:]+))?: "
    r"(?P<text>.+)$"
)
CLASSIFICATIONS = {
    "found",
    "not_stated",
    "ambiguous",
    "out_of_scope",
}


class SourcePageReviewError(RuntimeError):
    """Controlled source-page review failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SourcePageReviewError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise SourcePageReviewError(f"{label} must be a list")
    return value


def require_string(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        raise SourcePageReviewError(f"{label} must be a string")
    if not allow_empty and not value:
        raise SourcePageReviewError(f"{label} must be non-empty")
    return value


def read_json(path: Path, label: str) -> Mapping[str, Any]:
    if not path.is_file():
        raise SourcePageReviewError(f"{label} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourcePageReviewError(f"cannot read {label}: {exc}") from exc
    return require_mapping(payload, label)


def read_csv(path: Path, label: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise SourcePageReviewError(f"{label} does not exist: {path}")
    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise SourcePageReviewError(
                    f"{label} has no header: {path}"
                )
            return list(reader)
    except (OSError, csv.Error) as exc:
        raise SourcePageReviewError(f"cannot read {label}: {exc}") from exc


def compact_text(text: str) -> str:
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


def normalized_lines(text: str) -> list[str]:
    return [
        " ".join(line.split())
        for line in text.replace("\r", "\n").split("\n")
        if line.split()
    ]


def source_text_window(text: str, needle: str) -> str | None:
    target = compact_text(needle)
    if not target:
        raise SourcePageReviewError("review needle must not be empty")
    lines = normalized_lines(text)
    matches: list[str] = []
    for width in (1, 2, 3):
        for index in range(0, len(lines) - width + 1):
            window = " ".join(lines[index : index + width])
            if target in compact_text(window):
                matches.append(window)
        if matches:
            break
    if not matches:
        return None
    return min(matches, key=lambda item: (len(item), item.casefold()))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_note(note: str) -> tuple[int, str] | None:
    match = NOTE_PATTERN.fullmatch(note.strip())
    if match is None:
        return None
    return int(match.group("page")), match.group("text")


def load_sources(
    repository: Path,
) -> dict[str, Mapping[str, str]]:
    rows = read_csv(
        repository / "data" / "master" / "sources.csv",
        "source registry",
    )
    result: dict[str, Mapping[str, str]] = {}
    for row in rows:
        code = row.get("code", "")
        if not code:
            raise SourcePageReviewError("source has empty code")
        if code in result:
            raise SourcePageReviewError(
                f"duplicate source code: {code}"
            )
        result[code] = row
    return result


def load_anchors(
    repository: Path,
) -> dict[tuple[str, int], tuple[str, ...]]:
    anchors: dict[tuple[str, int], set[str]] = defaultdict(set)
    master = repository / "data" / "master"
    for filename in (
        "configuration_attribute_values.csv",
        "configuration_attribute_availability.csv",
        "configuration_prices.csv",
    ):
        for row in read_csv(master / filename, filename):
            source_code = row.get("source_code", "")
            parsed = parse_note(row.get("notes", ""))
            if not source_code or parsed is None:
                continue
            page, source_text = parsed
            if compact_text(source_text):
                anchors[(source_code, page)].add(source_text)
    return {
        key: tuple(sorted(values, key=str.casefold))
        for key, values in anchors.items()
    }


def validate_review_spec(
    review_spec: Mapping[str, Any],
) -> tuple[
    dict[str, Mapping[str, Any]],
    tuple[str, ...],
]:
    if review_spec.get("version") != 1:
        raise SourcePageReviewError(
            "source review specification version must be 1"
        )
    if review_spec.get("kind") != (
        "configuration_gap_source_page_review"
    ):
        raise SourcePageReviewError(
            "source review specification kind differs"
        )
    if review_spec.get("review_scope") != "relevant_source_pages":
        raise SourcePageReviewError(
            "source review scope differs"
        )
    if review_spec.get("auto_import") is not False:
        raise SourcePageReviewError(
            "source review must disable automatic import"
        )

    target_values = require_list(
        review_spec.get("review_triage_keys"),
        "review_triage_keys",
    )
    target_keys = tuple(
        require_string(value, "review triage key")
        for value in target_values
    )
    if not target_keys or len(target_keys) != len(set(target_keys)):
        raise SourcePageReviewError(
            "review_triage_keys must be non-empty and unique"
        )

    result: dict[str, Mapping[str, Any]] = {}
    for item in require_list(review_spec.get("rules"), "review rules"):
        rule = require_mapping(item, "review rule")
        attribute_code = require_string(
            rule.get("attribute_code"),
            "review rule attribute_code",
        )
        if attribute_code in result:
            raise SourcePageReviewError(
                f"duplicate source review rule: {attribute_code}"
            )
        pages = require_list(rule.get("review_pages"), "review_pages")
        if (
            not pages
            or any(
                not isinstance(page, int)
                or isinstance(page, bool)
                or page <= 0
                for page in pages
            )
            or len(pages) != len(set(pages))
        ):
            raise SourcePageReviewError(
                f"invalid review pages for {attribute_code}"
            )
        require_string(
            rule.get("source_section"),
            "review rule source_section",
        )
        matches = require_list(rule.get("matches"), "review matches")
        candidate_keys: set[tuple[str, str]] = set()
        for match in matches:
            candidate = require_mapping(match, "review match")
            needle = require_string(
                candidate.get("needle"),
                "review match needle",
            )
            candidate_value = require_string(
                candidate.get("candidate_value"),
                "review match candidate_value",
            )
            key = (compact_text(needle), candidate_value)
            if key in candidate_keys:
                raise SourcePageReviewError(
                    f"duplicate review match for {attribute_code}: {key}"
                )
            candidate_keys.add(key)
            excludes = candidate.get("exclude_needles", [])
            if not isinstance(excludes, list) or any(
                not isinstance(value, str) or not value
                for value in excludes
            ):
                raise SourcePageReviewError(
                    f"invalid exclude needles for {attribute_code}"
                )
        result[attribute_code] = rule
    return result, target_keys


def validate_evidence_spec(
    evidence_spec: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    if evidence_spec.get("version") != 1:
        raise SourcePageReviewError(
            "evidence specification version must be 1"
        )
    if evidence_spec.get("review_scope") not in {
        "structured_evidence_only",
        "source_page_evidence",
    }:
        raise SourcePageReviewError(
            "evidence specification review_scope differs"
        )
    decisions = require_list(
        evidence_spec.get("decisions"),
        "evidence decisions",
    )
    keys: set[str] = set()
    normalized: list[Mapping[str, Any]] = []
    for item in decisions:
        decision = require_mapping(item, "evidence decision")
        key = require_string(
            decision.get("triage_key"),
            "evidence triage_key",
        )
        if key in keys:
            raise SourcePageReviewError(
                f"duplicate evidence decision: {key}"
            )
        keys.add(key)
        classification = require_string(
            decision.get("classification"),
            "evidence classification",
        )
        if classification not in CLASSIFICATIONS:
            raise SourcePageReviewError(
                f"unsupported evidence classification: {classification}"
            )
        if decision.get("auto_import") is not False:
            raise SourcePageReviewError(
                "evidence decision enables automatic import"
            )
        normalized.append(decision)
    return normalized


def page_extraction(
    path: Path,
    page: int,
    anchors: Sequence[str],
    *,
    extractor: Callable[
        [Path, int],
        list[tuple[str, str]],
    ] = import_configuration_values.extract_page_candidates,
) -> dict[str, Any]:
    candidates = extractor(path, page)
    if not candidates:
        return {
            "page": page,
            "complete": False,
            "backend": "",
            "text": "",
            "anchor_count": len(anchors),
            "recovered_anchors": 0,
            "coverage": 0.0,
        }

    unique_anchors = tuple(
        sorted(
            {
                compact_text(anchor)
                for anchor in anchors
                if compact_text(anchor)
            }
        )
    )
    scored: list[tuple[int, int, int, str, str]] = []
    for backend, text in candidates:
        compact = compact_text(text)
        recovered = sum(
            1 for anchor in unique_anchors if anchor in compact
        )
        backend_name = backend.casefold()
        if "layout" in backend_name or "table" in backend_name:
            backend_rank = 3
        elif "default" in backend_name:
            backend_rank = 2
        elif "raw" in backend_name:
            backend_rank = 1
        else:
            backend_rank = 0
        scored.append(
            (
                recovered,
                backend_rank,
                len(compact),
                backend,
                text,
            )
        )
    recovered, _, length, backend, text = max(
        scored,
        key=lambda item: (
            item[0],
            item[1],
            item[2],
            item[3],
        ),
    )

    anchor_count = len(unique_anchors)
    coverage = (
        recovered / anchor_count if anchor_count else 1.0
    )
    minimum_recovered = (
        0
        if anchor_count == 0
        else min(
            anchor_count,
            max(1, math.ceil(anchor_count * 0.4)),
        )
    )
    complete = (
        length >= 100
        and recovered >= minimum_recovered
        and coverage >= (0.4 if anchor_count else 1.0)
    )
    return {
        "page": page,
        "complete": complete,
        "backend": backend,
        "text": text,
        "anchor_count": anchor_count,
        "recovered_anchors": recovered,
        "coverage": round(coverage, 4),
    }


def review_one_decision(
    decision: Mapping[str, Any],
    rule: Mapping[str, Any],
    pages: Mapping[int, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    key = require_string(decision.get("triage_key"), "triage_key")
    reviewed_pages = [
        page
        for page in rule["review_pages"]
        if pages.get(page, {}).get("complete") is True
    ]
    observations: list[dict[str, Any]] = []
    all_complete = len(reviewed_pages) == len(rule["review_pages"])

    for page in rule["review_pages"]:
        page_result = pages.get(page)
        if not page_result or not page_result.get("complete"):
            continue
        text = str(page_result["text"])
        compact_page = compact_text(text)
        for match in rule["matches"]:
            excludes = match.get("exclude_needles", [])
            if any(
                compact_text(excluded) in compact_page
                for excluded in excludes
            ):
                continue
            source_text = source_text_window(
                text,
                str(match["needle"]),
            )
            if source_text is None:
                continue
            observations.append(
                {
                    "page": page,
                    "backend": page_result["backend"],
                    "needle": match["needle"],
                    "candidate_value": match[
                        "candidate_value"
                    ],
                    "source_text": match["needle"],
                }
            )

    candidate_values = sorted(
        {
            str(observation["candidate_value"])
            for observation in observations
        }
    )
    updated = dict(decision)
    updated.update(
        {
            "classification": "ambiguous",
            "manual_source_review_required": True,
            "reason_code": "source_page_review_unresolved",
            "review_note": (
                "Relevant source pages require an unambiguous direct "
                "statement before this decision can be resolved."
            ),
            "candidate_value": "",
            "source_page": None,
            "source_section": "",
            "source_text": "",
            "reviewed_pages": [],
            "basis": None,
            "auto_import": False,
        }
    )
    result = {
        "triage_key": key,
        "attribute_code": decision["attribute_code"],
        "source_code": decision["source_code"],
        "configuration_code": decision["configuration_code"],
        "review_pages": list(rule["review_pages"]),
        "reviewed_pages": reviewed_pages,
        "extraction_complete": all_complete,
        "observations": observations,
        "result_classification": "ambiguous",
        "candidate_value": "",
        "reason_code": "",
    }

    if not all_complete:
        result["reason_code"] = "source_page_extraction_incomplete"
        return updated, result

    if not observations:
        updated.update(
            {
                "classification": "not_stated",
                "manual_source_review_required": False,
                "reason_code": "not_stated_on_relevant_pages",
                "review_note": (
                    "No direct configured source statement was found "
                    "on every reviewed relevant PDF page."
                ),
                "candidate_value": "",
                "source_page": None,
                "source_section": "",
                "source_text": "",
                "reviewed_pages": reviewed_pages,
                "basis": None,
                "auto_import": False,
            }
        )
        result.update(
            {
                "result_classification": "not_stated",
                "reason_code": "not_stated_on_relevant_pages",
            }
        )
        return updated, result

    if len(candidate_values) > 1:
        result["reason_code"] = "conflicting_source_statements"
        return updated, result

    chosen = min(
        observations,
        key=lambda item: (
            int(item["page"]),
            len(str(item["source_text"])),
            str(item["source_text"]).casefold(),
        ),
    )
    candidate_value = candidate_values[0]
    updated.update(
        {
            "classification": "found",
            "manual_source_review_required": False,
            "reason_code": "direct_source_statement_found",
            "review_note": (
                "A direct source statement was retained from the "
                "registered PDF page; modeling and import remain separate."
            ),
            "candidate_value": candidate_value,
            "source_page": chosen["page"],
            "source_section": rule["source_section"],
            "source_text": chosen["source_text"],
            "reviewed_pages": [chosen["page"]],
            "basis": None,
            "auto_import": False,
        }
    )
    result.update(
        {
            "result_classification": "found",
            "candidate_value": candidate_value,
            "reason_code": "direct_source_statement_found",
        }
    )
    return updated, result


def build_review(
    repository: Path,
    review_spec: Mapping[str, Any],
    evidence_spec: Mapping[str, Any],
    *,
    extractor: Callable[
        [Path, int],
        list[tuple[str, str]],
    ] = import_configuration_values.extract_page_candidates,
) -> tuple[dict[str, Any], dict[str, Any]]:
    rules, target_keys = validate_review_spec(review_spec)
    decisions = validate_evidence_spec(evidence_spec)
    if review_spec.get("as_of") != evidence_spec.get("as_of"):
        raise SourcePageReviewError(
            "source review date differs from evidence specification"
        )

    decisions_by_key = {
        str(decision["triage_key"]): decision
        for decision in decisions
    }
    if set(target_keys) - set(decisions_by_key):
        raise SourcePageReviewError(
            "source review targets reference unknown triage keys: "
            f"{sorted(set(target_keys) - set(decisions_by_key))}"
        )
    target_attributes = {
        str(decisions_by_key[key]["attribute_code"])
        for key in target_keys
    }
    if target_attributes != set(rules):
        raise SourcePageReviewError(
            "source review rules do not match target attributes"
            f"; missing: {sorted(target_attributes - set(rules))}"
            f"; extra: {sorted(set(rules) - target_attributes)}"
        )
    for key in target_keys:
        if decisions_by_key[key]["classification"] == "out_of_scope":
            raise SourcePageReviewError(
                f"source review target is out_of_scope: {key}"
            )

    target_key_set = set(target_keys)
    sources = load_sources(repository)
    anchors = load_anchors(repository)
    page_cache: dict[tuple[str, int], dict[str, Any]] = {}
    verified_sources: set[str] = set()

    updated_decisions: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    for decision in decisions:
        if str(decision["triage_key"]) not in target_key_set:
            updated_decisions.append(dict(decision))
            continue

        source_code = str(decision["source_code"])
        source = sources.get(source_code)
        if source is None:
            raise SourcePageReviewError(
                f"unknown registered source: {source_code}"
            )
        if source.get("status") != "active":
            raise SourcePageReviewError(
                f"inactive registered source: {source_code}"
            )
        source_path = repository / source.get("file_path", "")
        if not source_path.is_file():
            raise SourcePageReviewError(
                f"registered source file is missing: {source_path}"
            )
        if source_code not in verified_sources:
            actual_sha = file_sha256(source_path)
            if actual_sha != source.get("sha256"):
                raise SourcePageReviewError(
                    f"registered source SHA-256 differs: "
                    f"{source_path.name}"
                )
            verified_sources.add(source_code)
        if decision.get("sha256") != source.get("sha256"):
            raise SourcePageReviewError(
                f"evidence source SHA-256 differs: {source_code}"
            )
        if decision.get("file_path") != source.get("file_path"):
            raise SourcePageReviewError(
                f"evidence source path differs: {source_code}"
            )

        rule = rules[str(decision["attribute_code"])]
        pages: dict[int, Mapping[str, Any]] = {}
        for page in rule["review_pages"]:
            cache_key = (source_code, int(page))
            if cache_key not in page_cache:
                page_cache[cache_key] = page_extraction(
                    source_path,
                    int(page),
                    anchors.get(cache_key, ()),
                    extractor=extractor,
                )
            pages[int(page)] = page_cache[cache_key]

        updated, review_row = review_one_decision(
            decision,
            rule,
            pages,
        )
        updated_decisions.append(updated)
        review_rows.append(review_row)

    updated_spec = dict(evidence_spec)
    updated_spec["review_scope"] = "source_page_evidence"
    updated_spec["decisions"] = updated_decisions

    result_counts = Counter(
        row["result_classification"]
        for row in review_rows
    )
    evidence_counts = Counter(
        row["classification"]
        for row in updated_decisions
    )
    reviewed_page_pairs = sorted(
        {
            (source_code, page)
            for (source_code, page), result in page_cache.items()
            if result["complete"]
        }
    )
    incomplete_page_pairs = sorted(
        {
            (source_code, page)
            for (source_code, page), result in page_cache.items()
            if not result["complete"]
        }
    )
    report = {
        "version": 1,
        "as_of": evidence_spec["as_of"],
        "review_scope": "relevant_source_pages",
        "summary": {
            "review_targets": len(review_rows),
            "found": result_counts["found"],
            "not_stated": result_counts["not_stated"],
            "ambiguous": result_counts["ambiguous"],
            "out_of_scope_unchanged": evidence_counts[
                "out_of_scope"
            ],
            "candidate_values": sum(
                1
                for row in updated_decisions
                if row["classification"] == "found"
                and bool(row["candidate_value"])
            ),
            "manual_source_review_required": sum(
                1
                for row in updated_decisions
                if row["manual_source_review_required"]
            ),
            "reviewed_source_pages": len(reviewed_page_pairs),
            "incomplete_source_pages": len(
                incomplete_page_pairs
            ),
            "source_documents": len(verified_sources),
            "auto_import_enabled": 0,
        },
        "reviewed_source_pages": [
            {
                "source_code": source_code,
                "page": page,
                **{
                    key: value
                    for key, value in page_cache[
                        (source_code, page)
                    ].items()
                    if key != "text"
                },
            }
            for source_code, page in reviewed_page_pairs
        ],
        "incomplete_source_pages": [
            {
                "source_code": source_code,
                "page": page,
                **{
                    key: value
                    for key, value in page_cache[
                        (source_code, page)
                    ].items()
                    if key != "text"
                },
            }
            for source_code, page in incomplete_page_pairs
        ],
        "decisions": review_rows,
    }
    return updated_spec, report


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = require_mapping(report.get("summary"), "summary")
    lines = [
        "# Configuration Gap Source Page Review",
        "",
        f"As of: `{report['as_of']}`",
        "",
        "The review uses exact text extracted from relevant pages of "
        "registered PDF files whose SHA-256 hashes match the source registry.",
        "",
        "A direct match produces an evidence candidate only. "
        "Modeling and import remain separate, and automatic import is disabled.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Review targets | {summary['review_targets']} |",
        f"| Found | {summary['found']} |",
        f"| Not stated | {summary['not_stated']} |",
        f"| Still ambiguous | {summary['ambiguous']} |",
        f"| Candidate values | {summary['candidate_values']} |",
        (
            "| Manual source review required | "
            f"{summary['manual_source_review_required']} |"
        ),
        (
            "| Reviewed source pages | "
            f"{summary['reviewed_source_pages']} |"
        ),
        (
            "| Incomplete source pages | "
            f"{summary['incomplete_source_pages']} |"
        ),
        f"| Source documents | {summary['source_documents']} |",
        f"| Automatic imports enabled | {summary['auto_import_enabled']} |",
        "",
        "## Decisions",
        "",
        "| Triage key | Result | Candidate | Reviewed pages | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in require_list(report.get("decisions"), "decisions"):
        pages = ", ".join(
            str(page) for page in row["reviewed_pages"]
        ) or "-"
        candidate = row["candidate_value"] or "-"
        lines.append(
            f"| `{row['triage_key']}` | "
            f"`{row['result_classification']}` | "
            f"`{candidate}` | {pages} | "
            f"`{row['reason_code']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(
            content,
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Review ambiguous configuration gaps against relevant "
            "registered PDF source pages."
        )
    )
    parser.add_argument(
        "--review-spec",
        type=Path,
        default=DEFAULT_REVIEW_SPEC,
    )
    parser.add_argument(
        "--evidence-spec",
        type=Path,
        default=DEFAULT_EVIDENCE_SPEC,
    )
    parser.add_argument(
        "--write-evidence-spec",
        type=Path,
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help=(
            "Require the generated evidence specification to equal "
            "the versioned evidence specification."
        ),
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()

    review_path = arguments.review_spec
    if not review_path.is_absolute():
        review_path = repository / review_path
    evidence_path = arguments.evidence_spec
    if not evidence_path.is_absolute():
        evidence_path = repository / evidence_path

    try:
        review_spec = read_json(
            review_path,
            "configuration-gap source review specification",
        )
        evidence_spec = read_json(
            evidence_path,
            "configuration-gap evidence specification",
        )
        updated_spec, report = build_review(
            repository,
            review_spec,
            evidence_spec,
        )
        if arguments.verify:
            if render_json(updated_spec) != render_json(evidence_spec):
                raise SourcePageReviewError(
                    "versioned evidence specification differs "
                    "from source-page review output"
                )
        if arguments.write_evidence_spec is not None:
            target = arguments.write_evidence_spec
            if not target.is_absolute():
                target = repository / target
            write_atomic(target, render_json(updated_spec))
            print(
                "Evidence specification written to "
                f"{target}"
            )
        if arguments.json_path is not None:
            write_atomic(
                arguments.json_path,
                render_json(report),
            )
            print(
                "JSON source-page review written to "
                f"{arguments.json_path}"
            )
        if arguments.markdown is not None:
            write_atomic(
                arguments.markdown,
                render_markdown(report),
            )
            print(
                "Markdown source-page review written to "
                f"{arguments.markdown}"
            )

        summary = report["summary"]
        print("Configuration gap source page review")
        print("------------------------------------")
        print(f"As of                 : {report['as_of']}")
        print(
            f"Review targets        : "
            f"{summary['review_targets']}"
        )
        print(f"Found                 : {summary['found']}")
        print(f"Not stated            : {summary['not_stated']}")
        print(
            f"Still ambiguous       : "
            f"{summary['ambiguous']}"
        )
        print(
            f"Candidate values      : "
            f"{summary['candidate_values']}"
        )
        print(
            f"Reviewed source pages : "
            f"{summary['reviewed_source_pages']}"
        )
        print(
            f"Incomplete pages      : "
            f"{summary['incomplete_source_pages']}"
        )
        print("Automatic import       : disabled")
        return 0
    except (
        SourcePageReviewError,
        import_configuration_values.ImportSpecError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
