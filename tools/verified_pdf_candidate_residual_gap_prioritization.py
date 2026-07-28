#!/usr/bin/env python3
"""Build or verify deterministic review packages for residual verified-PDF candidates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PRIORITIZATION_VERSION = 1
PRIORITIZATION_KIND = "verified_pdf_candidate_residual_gap_prioritization"
PRIORITIZED_ON = "2026-07-28"
DEFAULT_RECONCILIATION = Path(
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.json"
)
DEFAULT_JSON = Path(
    "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
)
DEFAULT_MARKDOWN = Path(
    "data/reporting/verified_pdf_candidate_residual_gap_prioritization.md"
)
TARGET_STATUSES = ("ambiguous", "unresolved")
MAX_PACKAGE_SIZE = 40
NEXT_PACKAGE = "Bigster Technical Page 20 Ambiguity Review"
STATUS_PRIORITY = {"ambiguous": 0, "unresolved": 1}
DOMAIN_PRIORITY = {"technical_tables": 0, "equipment_matrix": 1}


class ResidualGapPrioritizationError(RuntimeError):
    """Controlled prioritization failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ResidualGapPrioritizationError(message)


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ResidualGapPrioritizationError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ResidualGapPrioritizationError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def validate_reconciliation(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("version") == 1, "reconciliation version differs")
    ensure(
        payload.get("kind") == "verified_pdf_candidate_coverage_reconciliation",
        "reconciliation kind differs",
    )
    ensure(payload.get("status") == "complete", "reconciliation is not complete")
    policy = payload.get("policy")
    ensure(isinstance(policy, Mapping), "reconciliation policy is missing")
    ensure(policy.get("master_data_changes") is False, "reconciliation changes master data")
    ensure(
        policy.get("approved_import_spec_generation") is False,
        "reconciliation creates approved imports",
    )
    boundaries = payload.get("semantic_boundaries")
    ensure(isinstance(boundaries, Mapping), "reconciliation boundaries are missing")
    ensure(
        boundaries.get("candidate_text_and_candidate_id_are_preserved") is True,
        "candidate identity boundary differs",
    )
    candidates = payload.get("candidates")
    ensure(isinstance(candidates, list), "reconciliation candidates are missing")
    identifiers = [candidate.get("candidate_id") for candidate in candidates if isinstance(candidate, Mapping)]
    ensure(len(identifiers) == len(candidates), "reconciliation candidate entry differs")
    ensure(len(identifiers) == len(set(identifiers)), "reconciliation candidate IDs are not unique")


def candidate_sort_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        int(candidate["line_start"]),
        int(candidate["line_end"]),
        str(candidate["candidate_id"]),
    )


def boundary_key(candidate: Mapping[str, Any]) -> tuple[str, str, int, str]:
    return (
        str(candidate["source_code"]),
        str(candidate["domain"]),
        int(candidate["page"]),
        str(candidate["coverage_status"]),
    )


def package_group_sort_key(
    item: tuple[tuple[str, str, int, str], list[dict[str, Any]]]
) -> tuple[Any, ...]:
    (source_code, domain, page, status), candidates = item
    ensure(status in STATUS_PRIORITY, f"unsupported residual status: {status}")
    ensure(domain in DOMAIN_PRIORITY, f"unsupported residual domain: {domain}")
    return (
        STATUS_PRIORITY[status],
        DOMAIN_PRIORITY[domain],
        -len(candidates),
        source_code,
        page,
    )


def chunks(values: Sequence[dict[str, Any]], size: int) -> Iterable[list[dict[str, Any]]]:
    ensure(size > 0, "package size must be positive")
    for start in range(0, len(values), size):
        yield list(values[start : start + size])


def evidence_counts(candidates: Sequence[Mapping[str, Any]]) -> tuple[int, int]:
    signature_count = 0
    record_count = 0
    for candidate in candidates:
        signatures = candidate.get("evidence_signatures")
        ensure(isinstance(signatures, list), "candidate evidence signatures are missing")
        signature_count += len(signatures)
        for signature in signatures:
            ensure(isinstance(signature, Mapping), "candidate evidence signature differs")
            records = signature.get("records")
            ensure(isinstance(records, list), "candidate evidence records are missing")
            declared_count = signature.get("record_count")
            ensure(declared_count == len(records), "candidate evidence record count differs")
            record_count += len(records)
    return signature_count, record_count


def copied_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Copy all source-backed fields without changing identity or exact text."""
    return json.loads(json.dumps(dict(candidate), ensure_ascii=False))


def make_package(
    priority: int,
    key: tuple[str, str, int, str],
    group_candidate_count: int,
    chunk_index: int,
    chunk_count: int,
    candidates: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    source_code, domain, page, status = key
    ensure(candidates, "review package must not be empty")
    ensure(len(candidates) <= MAX_PACKAGE_SIZE, "review package exceeds maximum size")
    for candidate in candidates:
        ensure(boundary_key(candidate) == key, "review package crosses a source/domain/page/status boundary")
    signatures, records = evidence_counts(candidates)
    identifier = f"residual_gap_{priority:03d}"
    return {
        "package_id": identifier,
        "priority": priority,
        "title": f"{source_code} {domain} page {page} {status} review",
        "source_code": source_code,
        "model_code": str(candidates[0]["model_code"]),
        "domain": domain,
        "page": page,
        "coverage_status": status,
        "group_candidate_count": group_candidate_count,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "candidate_count": len(candidates),
        "evidence_signature_count": signatures,
        "evidence_record_count": records,
        "candidate_ids": [str(candidate["candidate_id"]) for candidate in candidates],
        "candidates": [copied_candidate(candidate) for candidate in candidates],
        "review_contract": {
            "authored_decision_required": True,
            "candidate_id_and_exact_text_must_be_cited": True,
            "source_page_boundary_must_be_preserved": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
    }


def build_prioritization(reconciliation: Mapping[str, Any]) -> dict[str, Any]:
    validate_reconciliation(reconciliation)
    all_candidates = reconciliation["candidates"]
    residual = [
        dict(candidate)
        for candidate in all_candidates
        if candidate["coverage_status"] in TARGET_STATUSES
    ]
    ensure(residual, "no residual candidates found")

    grouped: dict[tuple[str, str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for candidate in residual:
        key = boundary_key(candidate)
        ensure(key[3] in TARGET_STATUSES, f"unsupported residual status: {key[3]}")
        grouped[key].append(candidate)

    packages: list[dict[str, Any]] = []
    priority = 1
    for key, candidates in sorted(grouped.items(), key=package_group_sort_key):
        ordered = sorted(candidates, key=candidate_sort_key)
        group_chunks = list(chunks(ordered, MAX_PACKAGE_SIZE))
        for chunk_index, candidate_chunk in enumerate(group_chunks, start=1):
            packages.append(
                make_package(
                    priority,
                    key,
                    len(ordered),
                    chunk_index,
                    len(group_chunks),
                    candidate_chunk,
                )
            )
            priority += 1

    assigned = [candidate_id for package in packages for candidate_id in package["candidate_ids"]]
    expected = [str(candidate["candidate_id"]) for candidate in residual]
    ensure(len(assigned) == len(expected), "residual candidate assignment count differs")
    ensure(len(assigned) == len(set(assigned)), "residual candidate assigned more than once")
    ensure(set(assigned) == set(expected), "residual candidate assignment is incomplete")

    status_counts = Counter(candidate["coverage_status"] for candidate in residual)
    domain_counts = Counter(candidate["domain"] for candidate in residual)
    source_counts = Counter(candidate["source_code"] for candidate in residual)
    package_status_counts = Counter(package["coverage_status"] for package in packages)
    package_domain_counts = Counter(package["domain"] for package in packages)

    first = packages[0]
    ensure(first["coverage_status"] == "ambiguous", "highest priority package must be ambiguous")
    ensure(first["domain"] == "technical_tables", "highest priority package must be technical")

    return {
        "version": PRIORITIZATION_VERSION,
        "kind": PRIORITIZATION_KIND,
        "prioritized_on": PRIORITIZED_ON,
        "status": "complete",
        "source_reconciliation": DEFAULT_RECONCILIATION.as_posix(),
        "policy": {
            "included_coverage_statuses": list(TARGET_STATUSES),
            "source_domain_page_status_bounded": True,
            "maximum_candidates_per_package": MAX_PACKAGE_SIZE,
            "ambiguous_before_unresolved": True,
            "technical_before_equipment_within_status": True,
            "larger_boundary_groups_before_smaller_groups": True,
            "candidate_id_and_exact_text_preserved": True,
            "every_residual_candidate_assigned_exactly_once": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "candidate_count": len(residual),
            "coverage_status_counts": {
                status: status_counts.get(status, 0) for status in TARGET_STATUSES
            },
            "domain_candidate_counts": {
                domain: domain_counts[domain] for domain in sorted(domain_counts)
            },
            "source_candidate_counts": {
                source: source_counts[source] for source in sorted(source_counts)
            },
            "boundary_group_count": len(grouped),
            "package_count": len(packages),
            "maximum_package_size": max(package["candidate_count"] for package in packages),
            "package_status_counts": {
                status: package_status_counts[status] for status in TARGET_STATUSES
            },
            "package_domain_counts": {
                domain: package_domain_counts[domain] for domain in sorted(package_domain_counts)
            },
        },
        "highest_priority_package": {
            key: first[key]
            for key in (
                "package_id",
                "priority",
                "source_code",
                "model_code",
                "domain",
                "page",
                "coverage_status",
                "candidate_count",
                "evidence_signature_count",
                "evidence_record_count",
            )
        },
        "packages": packages,
        "semantic_boundaries": {
            "prioritization_is_not_import_approval": True,
            "unresolved_is_not_negative_evidence": True,
            "ambiguous_requires_authored_signature_selection": True,
            "package_order_does_not_change_source_semantics": True,
            "no_configuration_attribute_unit_or_column_inference": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": (
                "Review the 23 highest-priority ambiguous technical candidates from "
                "Bigster brochure page 20 against their preserved evidence signatures, "
                "without creating master-data rows or approved import specifications."
            ),
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    statuses = summary["coverage_status_counts"]
    first = payload["highest_priority_package"]
    lines = [
        "# Verified PDF Candidate Residual Gap Prioritization",
        "",
        "Deterministic review queue for ambiguous and unresolved candidates. Priority is not import approval.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Residual candidates | {summary['candidate_count']} |",
        f"| Ambiguous | {statuses['ambiguous']} |",
        f"| Unresolved | {statuses['unresolved']} |",
        f"| Boundary groups | {summary['boundary_group_count']} |",
        f"| Review packages | {summary['package_count']} |",
        f"| Maximum package size | {summary['maximum_package_size']} |",
        "",
        "## Highest priority",
        "",
        f"Package `{first['package_id']}` contains {first['candidate_count']} ambiguous technical candidates from "
        f"`{first['source_code']}` page {first['page']}. It preserves {first['evidence_signature_count']} evidence-signature references and {first['evidence_record_count']} evidence-record references for authored review.",
        "",
        "## Review packages",
        "",
        "| Priority | Package | Source | Domain | Page | Status | Candidates | Signatures | Records |",
        "| ---: | --- | --- | --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for package in payload["packages"]:
        lines.append(
            f"| {package['priority']} | `{package['package_id']}` | `{package['source_code']}` | "
            f"`{package['domain']}` | {package['page']} | `{package['coverage_status']}` | "
            f"{package['candidate_count']} | {package['evidence_signature_count']} | "
            f"{package['evidence_record_count']} |"
        )
    lines.extend(
        [
            "",
            "## Ordering contract",
            "",
            "- Packages are bounded by source, domain, page and coverage status.",
            "- Ambiguous candidates precede unresolved candidates; technical tables precede equipment matrices within each status.",
            "- Larger boundary groups precede smaller groups, and groups larger than 40 candidates are split deterministically.",
            "- Candidate IDs, exact text, line spans and evidence signatures are copied without reinterpretation.",
            "",
            "## Safety boundary",
            "",
            "This artifact changes no master data, creates no approved import specification and performs no automatic promotion. Unresolved candidates remain unknown rather than negative evidence; ambiguous candidates require an authored choice supported by the preserved source page and signature records.",
            "",
            f"Next package: **{payload['next_package']['name']}**.",
            "",
        ]
    )
    return "\n".join(lines)


def build_from_path(repository: Path, reconciliation_path: Path) -> tuple[dict[str, Any], str]:
    reconciliation = load_json_object(repository / reconciliation_path, "coverage reconciliation")
    payload = build_prioritization(reconciliation)
    return payload, render_markdown(payload)


def ensure_safe_output(repository: Path, path: Path) -> Path:
    resolved = path if path.is_absolute() else repository / path
    try:
        relative = resolved.resolve().relative_to(repository.resolve())
    except ValueError as exc:
        raise ResidualGapPrioritizationError(f"output path leaves repository: {resolved}") from exc
    ensure(
        relative.parts[:2] not in {("data", "master"), ("data", "imports")},
        f"restricted output path: {relative}",
    )
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ResidualGapPrioritizationError(f"cannot read {label}: {exc}") from exc
    ensure(actual == expected, f"{label} differs from deterministic prioritization")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconciliation", type=Path, default=DEFAULT_RECONCILIATION)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = repository_root()
    try:
        payload, markdown = build_from_path(root, args.reconciliation)
        json_text = canonical_json(payload)
        json_path = ensure_safe_output(root, args.json)
        markdown_path = ensure_safe_output(root, args.markdown)
        if args.verify:
            verify_output(json_path, json_text, "residual prioritization JSON")
            verify_output(markdown_path, markdown, "residual prioritization Markdown")
        else:
            write_atomic(json_path, json_text)
            write_atomic(markdown_path, markdown)
    except (ResidualGapPrioritizationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    summary = payload["summary"]
    print(
        "PASS: prioritized "
        f"{summary['candidate_count']} candidates into {summary['package_count']} packages "
        f"(ambiguous={summary['coverage_status_counts']['ambiguous']}, "
        f"unresolved={summary['coverage_status_counts']['unresolved']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
