#!/usr/bin/env python3
"""Build or verify conservative coverage reconciliation for reviewed PDF candidates."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

RECONCILIATION_VERSION = 1
RECONCILIATION_KIND = "verified_pdf_candidate_coverage_reconciliation"
RECONCILED_ON = "2026-07-28"
DEFAULT_LEDGER = Path("data/reporting/official_dacia_pdf_candidate_ledger.json")
DEFAULT_REVIEW = Path("data/reporting/verified_pdf_candidate_ledger_review.json")
DEFAULT_JSON = Path("data/reporting/verified_pdf_candidate_coverage_reconciliation.json")
DEFAULT_MARKDOWN = Path("data/reporting/verified_pdf_candidate_coverage_reconciliation.md")
NEXT_PACKAGE = "Verified PDF Candidate Residual Gap Prioritization"
TARGET_DECISION = "requires_existing_evidence_reconciliation"
TARGET_DOMAINS = {"technical_tables", "equipment_matrix"}
COVERAGE_STATUSES = {
    "already_covered",
    "unresolved",
    "ambiguous",
    "explicit_non_import",
}
EVIDENCE_TABLES = (
    ("configuration_attribute_values", "configuration_attribute_values.csv"),
    ("configuration_attribute_value_ranges", "configuration_attribute_value_ranges.csv"),
    ("configuration_attribute_availability", "configuration_attribute_availability.csv"),
)
VARIANT_TOKENS = {"essential", "expression", "journey", "extreme"}
STOP_TOKENS = {
    "source", "page", "official", "brochure", "section", "strona", "sekcja",
    "dacia", "dane", "techniczne", "wyposazenie", "opcje", "oraz", "dla",
    "jest", "sa", "w", "i", "z", "ze", "na", "do", "od", "przy", "typ",
    "rodzaj", "kolor", "km", "h", "s", "l", "kg", "cm3", "mm", "nm",
    "kw", "cee", "ewg", "kmh", "obr", "min",
}
STRUCTURAL_KEYS = {
    "06 wyposazenie i opcje",
    "07 wyposazenie i opcje",
    "wyposazenie i opcje",
    "o6 specyfikacje techniczne",
    "06 specyfikacje techniczne",
    "07 dane techniczne",
    "06 silniki",
}


class CoverageReconciliationError(RuntimeError):
    """Controlled reconciliation failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CoverageReconciliationError(message)


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CoverageReconciliationError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CoverageReconciliationError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(payload, dict), f"{label} must be a JSON object")
    return payload


def read_csv_rows(path: Path, label: str) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            ensure(reader.fieldnames is not None, f"{label} has no header")
            return [dict(row) for row in reader]
    except OSError as exc:
        raise CoverageReconciliationError(f"cannot read {label}: {exc}") from exc


def match_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold().replace("ł", "l")
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    return " ".join(re.findall(r"[a-z0-9]+", normalized))


def meaningful_tokens(value: str) -> list[str]:
    return [
        token
        for token in match_key(value).split()
        if len(token) > 1 and not token.isdigit() and token not in STOP_TOKENS
    ]


def candidate_match_tokens(candidate: Mapping[str, Any]) -> list[str]:
    exact_text = str(candidate.get("exact_text", "")).strip()
    prefix = re.split(r"\s{3,}", exact_text, maxsplit=1)[0].strip()
    prefix_tokens = meaningful_tokens(prefix)
    if len(prefix_tokens) >= 2:
        return prefix_tokens
    return meaningful_tokens(str(candidate.get("normalized_text", "")))


def is_ordered_subsequence(needle: Sequence[str], haystack: Sequence[str]) -> bool:
    if len(needle) < 2:
        return False
    position = 0
    for token in haystack:
        if token == needle[position]:
            position += 1
            if position == len(needle):
                return True
    return False


def is_structural_non_import(candidate: Mapping[str, Any]) -> bool:
    if candidate.get("candidate_kind") == "heading":
        return True
    exact_text = str(candidate.get("exact_text", "")).strip()
    key = match_key(exact_text)
    if key in STRUCTURAL_KEYS or key.startswith("skonfiguruj i zamow"):
        return True
    if re.match(r"^\([0-9]+\)", exact_text):
        return True
    if re.match(r"^[0-9]+\s+", key) and len(key.split()) < 6:
        return True
    tokens = set(key.split())
    return bool(tokens) and tokens <= VARIANT_TOKENS


def parse_note_page(notes: str) -> int | None:
    match = re.search(r"(?:source|official brochure) page\s+([1-9][0-9]*)", notes, re.IGNORECASE)
    return int(match.group(1)) if match else None


def model_lookup(repository: Path) -> tuple[dict[str, str], set[str]]:
    versions = read_csv_rows(repository / "data/master/versions.csv", "versions")
    configurations = read_csv_rows(repository / "data/master/configurations.csv", "configurations")
    version_models = {row["code"]: row["model_code"] for row in versions}
    configuration_models: dict[str, str] = {}
    active_configurations: set[str] = set()
    for row in configurations:
        version_code = row["version_code"]
        ensure(version_code in version_models, f"configuration references unknown version: {row['code']}")
        configuration_models[row["code"]] = version_models[version_code]
        if row["status"] == "active":
            active_configurations.add(row["code"])
    return configuration_models, active_configurations


def evidence_signature(table: str, row: Mapping[str, str]) -> dict[str, str]:
    if table == "configuration_attribute_values":
        return {
            "attribute_code": row["attribute_code"],
            "value": row["value"],
            "fuel_type_code": row.get("fuel_type_code", ""),
            "gear_number": row.get("gear_number", ""),
        }
    if table == "configuration_attribute_value_ranges":
        return {
            "attribute_code": row["attribute_code"],
            "minimum_value": row["minimum_value"],
            "maximum_value": row["maximum_value"],
            "lower_inclusive": row["lower_inclusive"],
            "upper_inclusive": row["upper_inclusive"],
            "fuel_type_code": row.get("fuel_type_code", ""),
        }
    ensure(table == "configuration_attribute_availability", f"unknown evidence table: {table}")
    return {
        "attribute_code": row["attribute_code"],
        "availability_status": row["availability_status"],
    }


def signature_key(signature: Mapping[str, str]) -> str:
    return json.dumps(dict(signature), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_evidence(repository: Path) -> list[dict[str, Any]]:
    configuration_models, active_configurations = model_lookup(repository)
    evidence: list[dict[str, Any]] = []
    for table, filename in EVIDENCE_TABLES:
        for row in read_csv_rows(repository / "data/master" / filename, table):
            if row.get("source_code") == "src_pl_sandero_stepway_full_technical_standard_equipment_20260809":
                continue
            configuration_code = row.get("configuration_code", "")
            if configuration_code not in active_configurations:
                continue
            notes = row.get("notes", "")
            if not notes.strip():
                continue
            signature = evidence_signature(table, row)
            evidence.append(
                {
                    "table": table,
                    "record_code": row["code"],
                    "configuration_code": configuration_code,
                    "model_code": configuration_models[configuration_code],
                    "source_code": row["source_code"],
                    "source_page": parse_note_page(notes),
                    "notes": notes,
                    "note_tokens": meaningful_tokens(notes),
                    "signature": signature,
                    "signature_key": signature_key(signature),
                }
            )
    return sorted(evidence, key=lambda item: (item["table"], item["record_code"]))


def validate_inputs(ledger: Mapping[str, Any], review: Mapping[str, Any]) -> None:
    ensure(ledger.get("version") == 1, "ledger version differs")
    ensure(ledger.get("kind") == "verified_pdf_candidate_ledger", "ledger kind differs")
    ensure(review.get("version") == 1, "review version differs")
    ensure(review.get("kind") == "verified_pdf_candidate_ledger_review", "review kind differs")
    ensure(review.get("status") == "complete", "review is not complete")
    policy = review.get("policy")
    ensure(isinstance(policy, Mapping), "review policy is missing")
    ensure(policy.get("every_candidate_assigned_exactly_once") is True, "review assignment policy differs")
    ensure(policy.get("master_data_changes") is False, "review changes master data")
    ensure(policy.get("approved_import_spec_generation") is False, "review creates imports")


def target_groups(review: Mapping[str, Any]) -> list[dict[str, Any]]:
    groups = review.get("groups")
    ensure(isinstance(groups, list), "review groups are missing")
    selected = [
        dict(group)
        for group in groups
        if isinstance(group, Mapping) and group.get("decision_code") == TARGET_DECISION
    ]
    ensure(len(selected) == 10, "coverage reconciliation must select exactly 10 review groups")
    ensure({group.get("domain") for group in selected} == TARGET_DOMAINS, "target domains differ")
    ensure(len({group.get("group_id") for group in selected}) == len(selected), "target group IDs differ")
    return sorted(selected, key=lambda group: str(group["group_id"]))


def evidence_matches(
    candidate: Mapping[str, Any],
    group: Mapping[str, Any],
    evidence: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    tokens = candidate_match_tokens(candidate)
    if len(tokens) < 2:
        return []
    domain = group["domain"]
    matches: list[dict[str, Any]] = []
    for item in evidence:
        if domain == "technical_tables":
            if item["table"] == "configuration_attribute_availability":
                continue
            if item["source_code"] != candidate["source_code"]:
                continue
            if item["source_page"] != candidate["page"]:
                continue
            basis = "same_source_page_ordered_text"
        else:
            if item["table"] != "configuration_attribute_availability":
                continue
            if item["model_code"] != candidate["model_code"]:
                continue
            basis = "same_model_ordered_equipment_text"
        if is_ordered_subsequence(tokens, item["note_tokens"]):
            matches.append(
                {
                    "table": item["table"],
                    "record_code": item["record_code"],
                    "configuration_code": item["configuration_code"],
                    "source_code": item["source_code"],
                    "source_page": item["source_page"],
                    "match_basis": basis,
                    "signature": item["signature"],
                    "signature_key": item["signature_key"],
                }
            )
    return sorted(matches, key=lambda item: (item["signature_key"], item["table"], item["record_code"]))


def summarize_matches(matches: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for match in matches:
        grouped[str(match["signature_key"])].append(match)
    summaries: list[dict[str, Any]] = []
    for key in sorted(grouped):
        items = grouped[key]
        summaries.append(
            {
                "signature": dict(items[0]["signature"]),
                "record_count": len(items),
                "records": [
                    {
                        "table": item["table"],
                        "record_code": item["record_code"],
                        "configuration_code": item["configuration_code"],
                        "source_code": item["source_code"],
                        "source_page": item["source_page"],
                        "match_basis": item["match_basis"],
                    }
                    for item in items
                ],
            }
        )
    return summaries


def reconcile_candidate(
    candidate: Mapping[str, Any],
    group: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    tokens = candidate_match_tokens(candidate)
    if is_structural_non_import(candidate):
        status = "explicit_non_import"
        basis = "structural_heading_or_footnote"
        summaries: list[dict[str, Any]] = []
    else:
        matches = evidence_matches(candidate, group, evidence)
        summaries = summarize_matches(matches)
        if not summaries:
            status = "unresolved"
            basis = "no_conservative_exact_evidence_match"
        elif len(summaries) == 1:
            status = "already_covered"
            basis = "single_existing_evidence_signature"
        else:
            status = "ambiguous"
            basis = "multiple_existing_evidence_signatures"
    ensure(status in COVERAGE_STATUSES, f"unknown coverage status: {status}")
    return {
        "candidate_id": candidate["candidate_id"],
        "group_id": group["group_id"],
        "domain": group["domain"],
        "source_code": candidate["source_code"],
        "model_code": candidate["model_code"],
        "page": candidate["page"],
        "line_start": candidate["line_start"],
        "line_end": candidate["line_end"],
        "candidate_kind": candidate["candidate_kind"],
        "rule_code": candidate["rule_code"],
        "exact_text": candidate["exact_text"],
        "match_tokens": tokens,
        "coverage_status": status,
        "classification_basis": basis,
        "evidence_signatures": summaries,
    }


def build_reconciliation(
    ledger: Mapping[str, Any],
    review: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    validate_inputs(ledger, review)
    groups = target_groups(review)
    candidates = ledger.get("candidates")
    ensure(isinstance(candidates, list), "ledger candidates are missing")
    candidate_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
    ensure(len(candidate_by_id) == len(candidates), "ledger candidate IDs are not unique")

    assignments: list[dict[str, Any]] = []
    group_summaries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for group in groups:
        candidate_ids = group.get("candidate_ids")
        ensure(isinstance(candidate_ids, list) and candidate_ids, f"group candidate IDs missing: {group['group_id']}")
        group_assignments: list[dict[str, Any]] = []
        for candidate_id in candidate_ids:
            ensure(candidate_id in candidate_by_id, f"review references unknown candidate: {candidate_id}")
            ensure(candidate_id not in seen, f"candidate assigned twice in reconciliation: {candidate_id}")
            candidate = candidate_by_id[candidate_id]
            ensure(candidate["source_code"] == group["source_code"], f"candidate source differs: {candidate_id}")
            assignment = reconcile_candidate(candidate, group, evidence)
            group_assignments.append(assignment)
            assignments.append(assignment)
            seen.add(candidate_id)
        counts = Counter(item["coverage_status"] for item in group_assignments)
        group_summaries.append(
            {
                "group_id": group["group_id"],
                "source_code": group["source_code"],
                "model_code": group["model_code"],
                "domain": group["domain"],
                "page_start": group["page_start"],
                "page_end": group["page_end"],
                "candidate_count": len(group_assignments),
                "coverage_status_counts": {status: counts.get(status, 0) for status in sorted(COVERAGE_STATUSES)},
            }
        )

    assignments.sort(
        key=lambda item: (
            item["source_code"], item["page"], item["line_start"], item["line_end"], item["candidate_id"]
        )
    )
    overall = Counter(item["coverage_status"] for item in assignments)
    domain_counts: dict[str, Counter[str]] = defaultdict(Counter)
    source_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for item in assignments:
        domain_counts[item["domain"]][item["coverage_status"]] += 1
        source_counts[item["source_code"]][item["coverage_status"]] += 1
    evidence_counts = Counter(item["table"] for item in evidence)

    return {
        "version": RECONCILIATION_VERSION,
        "kind": RECONCILIATION_KIND,
        "reconciled_on": RECONCILED_ON,
        "status": "complete",
        "source_ledger": DEFAULT_LEDGER.as_posix(),
        "source_review": DEFAULT_REVIEW.as_posix(),
        "policy": {
            "target_review_decision": TARGET_DECISION,
            "technical_match_requires_same_source_and_page": True,
            "equipment_match_requires_active_same_model_record": True,
            "ordered_text_match_requires_at_least_two_meaningful_tokens": True,
            "single_signature_means_already_covered": True,
            "multiple_signatures_mean_ambiguous": True,
            "missing_match_means_unresolved_not_not_stated": True,
            "structural_headings_and_footnotes_are_explicit_non_import": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "target_groups": len(groups),
            "candidate_count": len(assignments),
            "coverage_status_counts": {status: overall.get(status, 0) for status in sorted(COVERAGE_STATUSES)},
            "active_evidence_record_counts": {name: evidence_counts.get(name, 0) for name, _ in EVIDENCE_TABLES},
        },
        "domain_status_counts": {
            domain: {status: domain_counts[domain].get(status, 0) for status in sorted(COVERAGE_STATUSES)}
            for domain in sorted(domain_counts)
        },
        "source_status_counts": {
            source: {status: source_counts[source].get(status, 0) for status in sorted(COVERAGE_STATUSES)}
            for source in sorted(source_counts)
        },
        "groups": group_summaries,
        "candidates": assignments,
        "semantic_boundaries": {
            "coverage_is_not_import_approval": True,
            "ambiguous_candidates_require_authored_review": True,
            "unresolved_candidates_are_not_negative_evidence": True,
            "candidate_text_and_candidate_id_are_preserved": True,
            "no_configuration_or_attribute_inference": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": (
                "Prioritize unresolved and ambiguous candidate IDs into small source- and page-bounded residual review packages, "
                "without creating master-data rows or approved import specifications."
            ),
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    status_counts = summary["coverage_status_counts"]
    lines = [
        "# Verified PDF Candidate Coverage Reconciliation",
        "",
        "Candidate-level reconciliation against existing active source-backed records. Coverage is not import approval.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Reconciled review groups | {summary['target_groups']} |",
        f"| Reconciled candidates | {summary['candidate_count']} |",
        f"| Already covered | {status_counts['already_covered']} |",
        f"| Ambiguous | {status_counts['ambiguous']} |",
        f"| Unresolved | {status_counts['unresolved']} |",
        f"| Explicit non-import | {status_counts['explicit_non_import']} |",
        "",
        "## Domains",
        "",
        "| Domain | Candidates | Covered | Ambiguous | Unresolved | Non-import |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for domain, counts in payload["domain_status_counts"].items():
        total = sum(counts.values())
        lines.append(
            f"| `{domain}` | {total} | {counts['already_covered']} | {counts['ambiguous']} | "
            f"{counts['unresolved']} | {counts['explicit_non_import']} |"
        )
    lines.extend([
        "",
        "## Groups",
        "",
        "| Group | Source | Domain | Pages | Candidates | Covered | Ambiguous | Unresolved | Non-import |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for group in payload["groups"]:
        counts = group["coverage_status_counts"]
        pages = str(group["page_start"]) if group["page_start"] == group["page_end"] else f"{group['page_start']}–{group['page_end']}"
        lines.append(
            f"| `{group['group_id']}` | `{group['source_code']}` | `{group['domain']}` | {pages} | "
            f"{group['candidate_count']} | {counts['already_covered']} | {counts['ambiguous']} | "
            f"{counts['unresolved']} | {counts['explicit_non_import']} |"
        )
    lines.extend([
        "",
        "## Classification contract",
        "",
        "- Technical candidates match only active exact records from the same registered source and PDF page.",
        "- Equipment candidates match only active availability records for the same model family.",
        "- Ordered text matching requires at least two meaningful tokens; one semantic signature is `already_covered`, several are `ambiguous`.",
        "- No conservative match is `unresolved`; it is never interpreted as `not_stated` or another negative value.",
        "- Structural headings, column labels and numbered footnotes are `explicit_non_import`.",
        "",
        "## Safety boundary",
        "",
        "This artifact changes no master data, creates no approved import specification and performs no automatic promotion. A later authored decision must cite the candidate ID, exact text and selected evidence signature.",
        "",
        f"Next package: **{payload['next_package']['name']}**.",
        "",
    ])
    return "\n".join(lines)


def build_from_paths(repository: Path, ledger_path: Path, review_path: Path) -> tuple[dict[str, Any], str]:
    ledger = load_json_object(repository / ledger_path, "candidate ledger")
    review = load_json_object(repository / review_path, "candidate ledger review")
    evidence = load_evidence(repository)
    payload = build_reconciliation(ledger, review, evidence)
    return payload, render_markdown(payload)


def ensure_safe_output(repository: Path, path: Path) -> Path:
    resolved = path if path.is_absolute() else repository / path
    relative = resolved.resolve().relative_to(repository.resolve())
    ensure(relative.parts[:2] not in {("data", "master"), ("data", "imports")}, f"restricted output path: {relative}")
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CoverageReconciliationError(f"cannot read {label}: {exc}") from exc
    ensure(actual == expected, f"{label} differs from deterministic reconciliation")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = repository_root()
    try:
        payload, markdown = build_from_paths(root, args.ledger, args.review)
        json_text = canonical_json(payload)
        json_path = ensure_safe_output(root, args.json)
        markdown_path = ensure_safe_output(root, args.markdown)
        if args.verify:
            verify_output(json_path, json_text, "coverage reconciliation JSON")
            verify_output(markdown_path, markdown, "coverage reconciliation Markdown")
        else:
            write_atomic(json_path, json_text)
            write_atomic(markdown_path, markdown)
    except (CoverageReconciliationError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    counts = payload["summary"]["coverage_status_counts"]
    print(
        "PASS: reconciled "
        f"{payload['summary']['candidate_count']} candidates "
        f"(covered={counts['already_covered']}, ambiguous={counts['ambiguous']}, "
        f"unresolved={counts['unresolved']}, non_import={counts['explicit_non_import']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
