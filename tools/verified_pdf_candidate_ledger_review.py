#!/usr/bin/env python3
"""Build or verify the source-bounded review of the verified PDF candidate ledger."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

REVIEW_VERSION = 1
REVIEW_KIND = "verified_pdf_candidate_ledger_review"
DEFAULT_LEDGER = Path("data/reporting/official_dacia_pdf_candidate_ledger.json")
DEFAULT_JSON = Path("data/reporting/verified_pdf_candidate_ledger_review.json")
DEFAULT_MARKDOWN = Path("data/reporting/verified_pdf_candidate_ledger_review.md")
REVIEWED_ON = "2026-07-28"
NEXT_PACKAGE = "Verified PDF Candidate Coverage Reconciliation"

DECISIONS: dict[str, dict[str, str]] = {
    "descriptive_non_import": {
        "status": "closed_non_import",
        "summary": "Retain as descriptive candidate-only evidence.",
        "rationale": (
            "The pages contain product narrative, navigation and broad feature claims without "
            "an authored exact configuration, attribute and context mapping. They remain useful "
            "for human reference but do not support direct structured-data promotion."
        ),
    },
    "requires_entity_mapping": {
        "status": "deferred_entity_mapping",
        "summary": "Require explicit trim, colour, package or accessory entity mapping.",
        "rationale": (
            "The pages describe colours, grades, packages and accessories. Candidate text alone "
            "does not establish the exact entity identity, applicability, price or configuration "
            "scope needed for a controlled import."
        ),
    },
    "requires_existing_evidence_reconciliation": {
        "status": "deferred_reconciliation",
        "summary": "Reconcile against current exact source-backed records before any new decision.",
        "rationale": (
            "Technical or equipment table text may duplicate later exact observations, preserve "
            "important column context, contain placeholders or expose a real residual gap. Every "
            "candidate must be compared with current evidence before it can be classified further."
        ),
    },
    "requires_visual_semantic_review": {
        "status": "deferred_visual_review",
        "summary": "Require visual page semantics and contextual mapping.",
        "rationale": (
            "Dimensions and cargo pages rely on diagram position, stars, view labels, drive or seat "
            "state and measurement basis. Text extraction order alone cannot safely map numbers to "
            "attributes or determine exact configuration scope."
        ),
    },
    "explicit_non_import": {
        "status": "closed_non_import",
        "summary": "Treat legal, navigation and publication boilerplate as explicit non-import.",
        "rationale": (
            "Publication credits, legal notices, navigation labels and calls to action are not vehicle "
            "observations and must not be projected into canonical data."
        ),
    },
}

EVIDENCE_REFERENCES: dict[str, tuple[str, ...]] = {
    "descriptive_non_import": (
        "project/reviews/verified-pdf-candidate-ledger-foundation-2026-07-28.md",
        "data/reporting/official_dacia_brochure_gap_review.json",
    ),
    "requires_entity_mapping": (
        "data/reporting/official_dacia_brochure_gap_review.json",
        "data/reporting/official_brochure_residual_evidence_review.json",
    ),
    "requires_existing_evidence_reconciliation": (
        "data/reporting/official_dacia_brochure_gap_review.json",
        "data/reporting/official_brochure_technical_gap_resolution_closure_review.json",
        "data/reporting/official_brochure_residual_evidence_review.json",
    ),
    "requires_visual_semantic_review": (
        "data/reporting/brochure_generic_dimensions_semantic_mapping_review.json",
        "data/reporting/brochure_generic_dimensions_import_closure_review.json",
        "data/reporting/brochure_cargo_import_closure_review.json",
    ),
    "explicit_non_import": (
        "project/reviews/verified-pdf-candidate-ledger-foundation-2026-07-28.md",
        "data/reporting/official_dacia_brochure_gap_review.json",
    ),
}


class LedgerReviewError(RuntimeError):
    """Controlled review failure."""


@dataclass(frozen=True)
class GroupSpec:
    group_id: str
    source_code: str
    model_code: str
    page_start: int
    page_end: int
    domain: str
    decision_code: str
    anchor_lines: tuple[tuple[int, int], ...]


SOURCE_GROUPS: tuple[GroupSpec, ...] = (
    GroupSpec("bigster_narrative", "src_pl_bigster_brochure_20251210", "bigster", 1, 13, "product_narrative", "descriptive_non_import", ((1, 1), (2, 19))),
    GroupSpec("bigster_catalogue_entities", "src_pl_bigster_brochure_20251210", "bigster", 14, 19, "colours_grades_accessories", "requires_entity_mapping", ((14, 1), (14, 6))),
    GroupSpec("bigster_technical_tables", "src_pl_bigster_brochure_20251210", "bigster", 20, 20, "technical_tables", "requires_existing_evidence_reconciliation", ((20, 1), (20, 5))),
    GroupSpec("bigster_equipment_matrix", "src_pl_bigster_brochure_20251210", "bigster", 21, 22, "equipment_matrix", "requires_existing_evidence_reconciliation", ((21, 8), (21, 5))),
    GroupSpec("bigster_dimensions_and_cargo", "src_pl_bigster_brochure_20251210", "bigster", 23, 23, "dimensions_and_cargo", "requires_visual_semantic_review", ((23, 1), (23, 32))),
    GroupSpec("bigster_legal_footer", "src_pl_bigster_brochure_20251210", "bigster", 24, 24, "legal_navigation_footer", "explicit_non_import", ((24, 16), (24, 21))),
    GroupSpec("duster_narrative", "src_pl_duster_mini_brochure_20251020", "duster_iii", 1, 13, "product_narrative", "descriptive_non_import", ((1, 1), (2, 18))),
    GroupSpec("duster_catalogue_entities", "src_pl_duster_mini_brochure_20251020", "duster_iii", 14, 19, "colours_grades_accessories", "requires_entity_mapping", ((14, 1), (14, 9))),
    GroupSpec("duster_technical_tables", "src_pl_duster_mini_brochure_20251020", "duster_iii", 20, 21, "technical_tables", "requires_existing_evidence_reconciliation", ((20, 1), (20, 7))),
    GroupSpec("duster_equipment_matrix", "src_pl_duster_mini_brochure_20251020", "duster_iii", 22, 23, "equipment_matrix", "requires_existing_evidence_reconciliation", ((22, 1), (22, 8))),
    GroupSpec("duster_dimensions_and_cargo", "src_pl_duster_mini_brochure_20251020", "duster_iii", 24, 24, "dimensions_and_cargo", "requires_visual_semantic_review", ((24, 1), (24, 38))),
    GroupSpec("duster_legal_footer", "src_pl_duster_mini_brochure_20251020", "duster_iii", 25, 25, "legal_navigation_footer", "explicit_non_import", ((25, 27), (25, 17))),
    GroupSpec("jogger_narrative", "src_pl_jogger_brochure_20251217", "jogger", 1, 12, "product_narrative", "descriptive_non_import", ((1, 1), (2, 14))),
    GroupSpec("jogger_catalogue_entities", "src_pl_jogger_brochure_20251217", "jogger", 13, 18, "colours_grades_accessories", "requires_entity_mapping", ((13, 1), (13, 6))),
    GroupSpec("jogger_technical_tables", "src_pl_jogger_brochure_20251217", "jogger", 19, 19, "technical_tables", "requires_existing_evidence_reconciliation", ((19, 1), (19, 5))),
    GroupSpec("jogger_equipment_matrix", "src_pl_jogger_brochure_20251217", "jogger", 20, 21, "equipment_matrix", "requires_existing_evidence_reconciliation", ((20, 8), (20, 5))),
    GroupSpec("jogger_dimensions_and_cargo", "src_pl_jogger_brochure_20251217", "jogger", 22, 22, "dimensions_and_cargo", "requires_visual_semantic_review", ((22, 1), (22, 40))),
    GroupSpec("jogger_legal_footer", "src_pl_jogger_brochure_20251217", "jogger", 23, 23, "legal_navigation_footer", "explicit_non_import", ((23, 16), (23, 21))),
    GroupSpec("sandero_narrative", "src_pl_sandero_brochure_20260202", "sandero_iii", 1, 11, "product_narrative", "descriptive_non_import", ((1, 1), (2, 15))),
    GroupSpec("sandero_catalogue_entities", "src_pl_sandero_brochure_20260202", "sandero_iii", 12, 16, "colours_grades_accessories", "requires_entity_mapping", ((12, 1), (12, 6))),
    GroupSpec("sandero_technical_tables", "src_pl_sandero_brochure_20260202", "sandero_iii", 17, 17, "technical_tables", "requires_existing_evidence_reconciliation", ((17, 1), (17, 5))),
    GroupSpec("sandero_equipment_matrix", "src_pl_sandero_brochure_20260202", "sandero_iii", 18, 19, "equipment_matrix", "requires_existing_evidence_reconciliation", ((18, 8), (18, 5))),
    GroupSpec("sandero_dimensions_and_cargo", "src_pl_sandero_brochure_20260202", "sandero_iii", 20, 20, "dimensions_and_cargo", "requires_visual_semantic_review", ((20, 1), (20, 51))),
    GroupSpec("sandero_legal_footer", "src_pl_sandero_brochure_20260202", "sandero_iii", 21, 21, "legal_navigation_footer", "explicit_non_import", ((21, 16), (21, 21))),
    GroupSpec("sandero_stepway_narrative", "src_pl_sandero_stepway_brochure_20260202", "sandero_stepway_iii", 1, 11, "product_narrative", "descriptive_non_import", ((1, 1), (2, 15))),
    GroupSpec("sandero_stepway_catalogue_entities", "src_pl_sandero_stepway_brochure_20260202", "sandero_stepway_iii", 12, 16, "colours_grades_accessories", "requires_entity_mapping", ((12, 1), (12, 6))),
    GroupSpec("sandero_stepway_technical_tables", "src_pl_sandero_stepway_brochure_20260202", "sandero_stepway_iii", 17, 17, "technical_tables", "requires_existing_evidence_reconciliation", ((17, 1), (17, 5))),
    GroupSpec("sandero_stepway_equipment_matrix", "src_pl_sandero_stepway_brochure_20260202", "sandero_stepway_iii", 18, 19, "equipment_matrix", "requires_existing_evidence_reconciliation", ((18, 8), (18, 5))),
    GroupSpec("sandero_stepway_dimensions_and_cargo", "src_pl_sandero_stepway_brochure_20260202", "sandero_stepway_iii", 20, 20, "dimensions_and_cargo", "requires_visual_semantic_review", ((20, 1), (20, 52))),
    GroupSpec("sandero_stepway_legal_footer", "src_pl_sandero_stepway_brochure_20260202", "sandero_stepway_iii", 21, 21, "legal_navigation_footer", "explicit_non_import", ((21, 16), (21, 21))),
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise LedgerReviewError(message)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise LedgerReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LedgerReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(payload, dict), f"{label} must be a JSON object")
    return payload


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def verify_specs(ledger: Mapping[str, Any]) -> None:
    ensure(len(SOURCE_GROUPS) == 30, "review must define exactly 30 groups")
    ensure(len({spec.group_id for spec in SOURCE_GROUPS}) == len(SOURCE_GROUPS), "group IDs differ")
    sources = ledger.get("sources")
    ensure(isinstance(sources, list), "ledger sources are missing")
    source_meta = {source["source_code"]: source for source in sources}
    grouped: dict[str, list[GroupSpec]] = defaultdict(list)
    for spec in SOURCE_GROUPS:
        ensure(spec.decision_code in DECISIONS, f"unknown decision code: {spec.decision_code}")
        ensure(spec.source_code in source_meta, f"unknown source in review spec: {spec.source_code}")
        ensure(spec.model_code == source_meta[spec.source_code]["model_code"], f"model differs: {spec.group_id}")
        ensure(1 <= spec.page_start <= spec.page_end, f"invalid page range: {spec.group_id}")
        ensure(len(spec.anchor_lines) == 2, f"each group must define two anchors: {spec.group_id}")
        grouped[spec.source_code].append(spec)
    ensure(set(grouped) == set(source_meta), "review source set differs from ledger")
    for source_code, specs in grouped.items():
        specs.sort(key=lambda item: item.page_start)
        expected = 1
        for spec in specs:
            ensure(spec.page_start == expected, f"page coverage gap or overlap: {spec.group_id}")
            expected = spec.page_end + 1
        ensure(expected - 1 == source_meta[source_code]["declared_pages"], f"page coverage differs: {source_code}")


def build_review(ledger: Mapping[str, Any]) -> dict[str, Any]:
    ensure(ledger.get("version") == 1, "candidate ledger version differs")
    ensure(ledger.get("kind") == "verified_pdf_candidate_ledger", "candidate ledger kind differs")
    candidates = ledger.get("candidates")
    ensure(isinstance(candidates, list) and candidates, "candidate ledger is empty")
    verify_specs(ledger)

    by_source_page: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    by_anchor: dict[tuple[str, int, int], list[dict[str, Any]]] = defaultdict(list)
    source_sha: dict[str, str] = {}
    for candidate in candidates:
        ensure(isinstance(candidate, dict), "candidate must be an object")
        source_code = candidate["source_code"]
        page = candidate["page"]
        line_start = candidate["line_start"]
        by_source_page[(source_code, page)].append(candidate)
        by_anchor[(source_code, page, line_start)].append(candidate)
        source_sha[source_code] = candidate["source_sha256"]

    groups: list[dict[str, Any]] = []
    covered_ids: list[str] = []
    decision_candidate_counts: Counter[str] = Counter()
    decision_group_counts: Counter[str] = Counter()
    anchor_count = 0

    for spec in SOURCE_GROUPS:
        members: list[dict[str, Any]] = []
        for page in range(spec.page_start, spec.page_end + 1):
            members.extend(by_source_page[(spec.source_code, page)])
        ensure(members, f"review group has no candidates: {spec.group_id}")
        candidate_ids = [candidate["candidate_id"] for candidate in members]
        ensure(len(candidate_ids) == len(set(candidate_ids)), f"duplicate candidate in group: {spec.group_id}")
        anchors: list[dict[str, Any]] = []
        for page, line_start in spec.anchor_lines:
            matches = by_anchor[(spec.source_code, page, line_start)]
            ensure(len(matches) == 1, f"anchor must resolve uniquely: {spec.group_id} p{page} l{line_start}")
            candidate = matches[0]
            ensure(spec.page_start <= page <= spec.page_end, f"anchor outside group: {spec.group_id}")
            anchors.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "page": candidate["page"],
                    "line_start": candidate["line_start"],
                    "line_end": candidate["line_end"],
                    "candidate_kind": candidate["candidate_kind"],
                    "exact_text": candidate["exact_text"],
                }
            )
        decision = DECISIONS[spec.decision_code]
        groups.append(
            {
                "group_id": spec.group_id,
                "source_code": spec.source_code,
                "source_sha256": source_sha[spec.source_code],
                "model_code": spec.model_code,
                "page_start": spec.page_start,
                "page_end": spec.page_end,
                "page_count": spec.page_end - spec.page_start + 1,
                "domain": spec.domain,
                "decision_code": spec.decision_code,
                "decision_status": decision["status"],
                "decision_summary": decision["summary"],
                "rationale": decision["rationale"],
                "evidence_references": list(EVIDENCE_REFERENCES[spec.decision_code]),
                "candidate_count": len(candidate_ids),
                "candidate_ids": candidate_ids,
                "anchor_candidates": anchors,
            }
        )
        covered_ids.extend(candidate_ids)
        decision_candidate_counts[spec.decision_code] += len(candidate_ids)
        decision_group_counts[spec.decision_code] += 1
        anchor_count += len(anchors)

    ledger_ids = [candidate["candidate_id"] for candidate in candidates]
    ensure(len(covered_ids) == len(ledger_ids), "review candidate total differs")
    ensure(len(set(covered_ids)) == len(covered_ids), "candidate appears in more than one review group")
    ensure(set(covered_ids) == set(ledger_ids), "review does not cover the exact ledger candidate set")

    return {
        "version": REVIEW_VERSION,
        "kind": REVIEW_KIND,
        "reviewed_on": REVIEWED_ON,
        "status": "complete",
        "source_ledger": DEFAULT_LEDGER.as_posix(),
        "source_ledger_backend_version": ledger["backend_version"],
        "policy": {
            "every_candidate_assigned_exactly_once": True,
            "anchors_cite_candidate_id_and_exact_text": True,
            "group_decisions_do_not_approve_imports": True,
            "candidate_text_is_not_reinterpreted": True,
            "missing_text_is_not_negative_evidence": True,
            "visual_diagram_semantics_are_not_inferred": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
        },
        "controlled_decisions": {
            code: {
                "status": decision["status"],
                "summary": decision["summary"],
            }
            for code, decision in DECISIONS.items()
        },
        "groups": groups,
        "summary": {
            "sources": ledger["source_count"],
            "pages": ledger["page_count"],
            "candidates": ledger["candidate_count"],
            "groups": len(groups),
            "anchors": anchor_count,
            "decision_group_counts": dict(sorted(decision_group_counts.items())),
            "decision_candidate_counts": dict(sorted(decision_candidate_counts.items())),
            "unassigned_candidates": 0,
            "duplicate_assignments": 0,
            "master_data_changes": 0,
            "approved_import_specs_created": 0,
        },
        "promotion_boundary": {
            "direct_review_to_master_import": False,
            "direct_review_to_approved_import_spec": False,
            "required_next_step": (
                "Reconcile reviewed technical and equipment candidate groups against current exact "
                "source-backed records and record candidate-level coverage decisions."
            ),
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": (
                "Reconcile reviewed technical and equipment candidate groups against current exact "
                "source-backed observations and availability records, classifying candidate IDs as "
                "already covered, unresolved, ambiguous or explicit non-import without creating imports."
            ),
        },
    }


def render_markdown(review: Mapping[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        "# Verified PDF Candidate Ledger Review",
        "",
        f"Date: {review['reviewed_on']}  ",
        f"Status: {review['status']}",
        "",
        "## Coverage",
        "",
        "| Measure | Result |",
        "| --- | ---: |",
        f"| Registered sources | {summary['sources']} |",
        f"| Declared pages | {summary['pages']} |",
        f"| Candidate spans | {summary['candidates']:,} |",
        f"| Evidence decision groups | {summary['groups']} |",
        f"| Exact-text anchors | {summary['anchors']} |",
        f"| Unassigned candidates | {summary['unassigned_candidates']} |",
        f"| Duplicate assignments | {summary['duplicate_assignments']} |",
        "",
        "Every candidate from the canonical ledger is assigned exactly once. Group decisions are review-only and do not approve configuration, attribute, unit or import-spec mappings.",
        "",
        "## Decision totals",
        "",
        "| Decision | Groups | Candidates |",
        "| --- | ---: | ---: |",
    ]
    group_counts = summary["decision_group_counts"]
    candidate_counts = summary["decision_candidate_counts"]
    for code in sorted(DECISIONS):
        lines.append(f"| `{code}` | {group_counts.get(code, 0)} | {candidate_counts.get(code, 0):,} |")
    lines.extend(["", "## Source groups", ""])
    current_source = None
    for group in review["groups"]:
        if group["source_code"] != current_source:
            current_source = group["source_code"]
            lines.extend([f"### `{current_source}`", ""])
        page_label = str(group["page_start"]) if group["page_start"] == group["page_end"] else f"{group['page_start']}–{group['page_end']}"
        lines.extend(
            [
                f"#### `{group['group_id']}` — pages {page_label}",
                "",
                f"- Domain: `{group['domain']}`",
                f"- Decision: `{group['decision_code']}` / `{group['decision_status']}`",
                f"- Candidates: {group['candidate_count']:,}",
                f"- Summary: {group['decision_summary']}",
                f"- Rationale: {group['rationale']}",
                "- Anchors:",
            ]
        )
        for anchor in group["anchor_candidates"]:
            exact = anchor["exact_text"].replace("`", "\\`")
            lines.append(
                f"  - `{anchor['candidate_id']}` — page {anchor['page']}, lines "
                f"{anchor['line_start']}–{anchor['line_end']}: `{exact}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Safety boundary",
            "",
            "This review creates no master-data row and no approved import specification. It does not infer diagram semantics, exact configuration applicability or canonical entity mappings from extraction order. Candidate-level promotion remains blocked until a separate reconciliation decision cites the candidate ID and current exact evidence.",
            "",
            "## Next package",
            "",
            f"**{review['next_package']['name']}** — {review['next_package']['goal']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_from_paths(repository: Path, ledger_path: Path) -> tuple[dict[str, Any], str]:
    resolved = ledger_path if ledger_path.is_absolute() else repository / ledger_path
    review = build_review(load_json_object(resolved, "candidate ledger"))
    return review, render_markdown(review)


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LedgerReviewError(f"cannot read {label}: {exc}") from exc
    ensure(actual == expected, f"{label} differs from deterministic review output")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = repository_root()
    json_path = args.json if args.json.is_absolute() else root / args.json
    markdown_path = args.markdown if args.markdown.is_absolute() else root / args.markdown
    try:
        review, markdown = build_from_paths(root, args.ledger)
        json_text = canonical_json(review)
        if args.verify:
            verify_output(json_path, json_text, "review JSON")
            verify_output(markdown_path, markdown, "review Markdown")
            print(
                "PASS: verified PDF candidate ledger review "
                f"({review['summary']['groups']} groups, {review['summary']['candidates']} candidates)"
            )
        else:
            write_atomic(json_path, json_text)
            write_atomic(markdown_path, markdown)
            print(
                "WROTE: verified PDF candidate ledger review "
                f"({review['summary']['groups']} groups, {review['summary']['candidates']} candidates)"
            )
    except (OSError, json.JSONDecodeError, LedgerReviewError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
