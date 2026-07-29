#!/usr/bin/env python3
"""Build or verify chunk 2 of the authored Bigster page-20 unresolved review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

REVIEW_VERSION = 1
REVIEW_KIND = "bigster_technical_page20_unresolved_review_chunk2"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path(
    "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
)
DEFAULT_JSON = Path(
    "data/reporting/bigster_technical_page20_unresolved_review_chunk2.json"
)
DEFAULT_MARKDOWN = Path(
    "data/reporting/bigster_technical_page20_unresolved_review_chunk2.md"
)
PRIOR_CHUNK_REVIEW = Path(
    "data/reporting/bigster_technical_page20_unresolved_review_chunk1.json"
)
PACKAGE_ID = "residual_gap_017"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
SOURCE_PAGE = 20
SOURCE_PATH = Path("PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf")
SOURCE_SHA256 = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
PACKAGE_CANDIDATE_DIGEST = "79b25454c859f5425b79a967191ed137645a8917ae1f2341e08fd75ebebbae3a"
NEXT_PACKAGE = "Duster Mini Technical Page 21 Unresolved Review — Chunk 1"
POWERTRAIN_COLUMNS = (
    "mild_hybrid_g_140",
    "mild_hybrid_140",
    "hybrid_g_150_4x4",
    "hybrid_155",
)
DECISION_STATUSES = {
    "context_only_non_import",
    "unresolved_signature_mismatch",
}


class BigsterPage20UnresolvedChunk2ReviewError(RuntimeError):
    """Controlled authored-review failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise BigsterPage20UnresolvedChunk2ReviewError(message)


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
        raise BigsterPage20UnresolvedChunk2ReviewError(
            f"cannot read {label}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise BigsterPage20UnresolvedChunk2ReviewError(
            f"invalid JSON in {label}: {exc}"
        ) from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise BigsterPage20UnresolvedChunk2ReviewError(
            f"cannot read archived source: {exc}"
        ) from exc
    return digest.hexdigest()


def read_source_row(repository: Path) -> dict[str, str]:
    path = repository / "data/master/sources.csv"
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            ensure(reader.fieldnames is not None, "sources.csv has no header")
            matches = [
                dict(row) for row in reader if row.get("code") == SOURCE_CODE
            ]
    except OSError as exc:
        raise BigsterPage20UnresolvedChunk2ReviewError(
            f"cannot read sources.csv: {exc}"
        ) from exc
    ensure(len(matches) == 1, "Bigster brochure source registry row differs")
    return matches[0]


def source_fact(
    logical_attribute: str,
    values_by_column: Mapping[str, Sequence[str]],
    reason: str,
) -> dict[str, Any]:
    ensure(
        tuple(values_by_column) == POWERTRAIN_COLUMNS,
        f"source fact column order differs: {logical_attribute}",
    )
    return {
        "logical_attribute": logical_attribute,
        "values_by_powertrain": {
            column: list(values_by_column[column]) for column in POWERTRAIN_COLUMNS
        },
        "reason": reason,
    }


ROW_FACTS: dict[str, dict[str, Any]] = {
    "fuel_tank_capacity": source_fact(
        "fuel_tank_capacity_l",
        {
            "mild_hybrid_g_140": ["LPG: 50", "Benzyna: 50"],
            "mild_hybrid_140": ["Benzyna: 50"],
            "hybrid_g_150_4x4": ["LPG: 50", "Benzyna: 50"],
            "hybrid_155": ["Benzyna: 50"],
        },
        "The row visibly distinguishes LPG and petrol tanks, but the package has no exact evidence signature and creates no approved observation.",
    ),
    "co2_emissions_combined": source_fact(
        "combined_cycle_co2_g_km",
        {
            "mild_hybrid_g_140": ["Benzyna: 130/132", "LPG: 114/116"],
            "mild_hybrid_140": ["122/124"],
            "hybrid_g_150_4x4": ["134/117 (LPG)"],
            "hybrid_155": ["104/106"],
        },
        "The combined-cycle CO2 row and its fuel-specific continuations are visually legible, but zero attached signatures are preserved.",
    ),
    "fuel_consumption_combined": source_fact(
        "combined_cycle_fuel_consumption_l_100km",
        {
            "mild_hybrid_g_140": ["Benzyna: 5,7/5,8", "LPG: 7,0/7,1"],
            "mild_hybrid_140": ["5,4/5,5"],
            "hybrid_g_150_4x4": ["5,9/7,2 (LPG)"],
            "hybrid_155": ["4,6/4,7"],
        },
        "The combined-cycle consumption row is recorded literally as a review finding; no fuel projection or import approval is created.",
    ),
    "payload": source_fact(
        "payload_min_max_kg",
        {
            "mild_hybrid_g_140": ["452/521"],
            "mild_hybrid_140": ["451/540"],
            "hybrid_g_150_4x4": ["462/509"],
            "hybrid_155": ["453/521"],
        },
        "The minimum/maximum payload values are visible in one row, but the unresolved package provides no supporting evidence signature.",
    ),
    "luggage_vda_shelf": source_fact(
        "luggage_capacity_under_shelf_dm3_vda",
        {
            "mild_hybrid_g_140": ["609**"],
            "mild_hybrid_140": ["667 / 624"],
            "hybrid_g_150_4x4": [
                "444",
                "nie ma zestawu naprawczego / koła zapasowego",
            ],
            "hybrid_155": ["546 / 488"],
        },
        "VDA values and the printed equipment qualification remain literal source context; the review does not infer a configuration mapping.",
    ),
    "luggage_vda_folded": source_fact(
        "luggage_capacity_folded_rear_seat_dm3_vda",
        {
            "mild_hybrid_g_140": ["1877**"],
            "mild_hybrid_140": ["1937 / 1894"],
            "hybrid_g_150_4x4": ["1712"],
            "hybrid_155": ["1851 / 1791"],
        },
        "The folded-seat VDA capacities are legible, but no exact signature is attached and no approved import is generated.",
    ),
    "luggage_liters_shelf": source_fact(
        "luggage_capacity_under_shelf_l",
        {
            "mild_hybrid_g_140": ["660**"],
            "mild_hybrid_140": ["702 / 681"],
            "hybrid_g_150_4x4": [
                "556",
                "nie ma zestawu naprawczego / koła zapasowego",
            ],
            "hybrid_155": ["612 / 566"],
        },
        "The litre values and printed equipment note are preserved exactly as review-only findings without reinterpretation.",
    ),
    "luggage_liters_folded": source_fact(
        "luggage_capacity_folded_rear_seat_l",
        {
            "mild_hybrid_g_140": ["1960**"],
            "mild_hybrid_140": ["1960**", "2002 / 1981"],
            "hybrid_g_150_4x4": ["1856"],
            "hybrid_155": ["1912 / 1866"],
        },
        "The printed sequence 1960** and 2002 / 1981 is preserved literally; the review does not invent which equipment state each value represents.",
    ),
}


# Indexes are 1-based positions in the exact residual_gap_017 candidate order.
ROW_ASSIGNMENTS: tuple[tuple[str, tuple[int, ...], int | None], ...] = (
    ("fuel_tank_capacity", (1,), 1),
    ("co2_emissions_combined", (2, 3, 4), 2),
    ("fuel_consumption_combined", (5, 6, 7), 5),
    ("gross_combination_mass_label", (8,), None),
    ("gross_vehicle_mass_label", (9,), None),
    ("payload", (10,), 10),
    ("braked_trailer_mass_label", (11,), None),
    ("luggage_vda_shelf", (12,), 12),
    ("luggage_vda_folded", (13,), 13),
    ("luggage_liters_shelf", (14, 15, 16), 14),
    ("luggage_liters_folded", (17, 18, 19), 17),
    ("particulate_filter_footnote", (20, 21, 22), None),
    ("homologation_payload_footnotes", (23, 24, 25, 26), None),
    ("iso_3832_footnote", (27,), None),
    ("incompatibility_note", (28,), None),
    ("spare_wheel_note", (29,), None),
)


def candidate_digest(candidates: Sequence[Mapping[str, Any]]) -> str:
    material = [
        {
            "candidate_id": item.get("candidate_id"),
            "line_start": item.get("line_start"),
            "line_end": item.get("line_end"),
            "exact_text": item.get("exact_text"),
        }
        for item in candidates
    ]
    encoded = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_prioritization(payload: Mapping[str, Any]) -> dict[str, Any]:
    ensure(payload.get("version") == 1, "prioritization version differs")
    ensure(
        payload.get("kind") == "verified_pdf_candidate_residual_gap_prioritization",
        "prioritization kind differs",
    )
    ensure(payload.get("status") == "complete", "prioritization is not complete")
    policy = payload.get("policy")
    ensure(isinstance(policy, Mapping), "prioritization policy is missing")
    ensure(policy.get("master_data_changes") is False, "prioritization changes master data")
    ensure(
        policy.get("approved_import_spec_generation") is False,
        "prioritization creates approved imports",
    )
    packages = payload.get("packages")
    ensure(isinstance(packages, list), "prioritization packages are missing")
    matches = [
        package
        for package in packages
        if isinstance(package, Mapping) and package.get("package_id") == PACKAGE_ID
    ]
    ensure(len(matches) == 1, "residual_gap_017 package differs")
    package = dict(matches[0])
    expected = {
        "source_code": SOURCE_CODE,
        "model_code": "bigster",
        "domain": "technical_tables",
        "page": SOURCE_PAGE,
        "coverage_status": "unresolved",
        "group_candidate_count": 69,
        "chunk_index": 2,
        "chunk_count": 2,
        "candidate_count": 29,
        "evidence_signature_count": 0,
        "evidence_record_count": 0,
    }
    for key, value in expected.items():
        ensure(package.get(key) == value, f"package {key} differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 29, "package candidates differ")
    ensure(
        candidate_digest(candidates) == PACKAGE_CANDIDATE_DIGEST,
        "package candidate content differs",
    )
    for candidate in candidates:
        ensure(isinstance(candidate, Mapping), "package candidate differs")
        ensure(candidate.get("source_code") == SOURCE_CODE, "candidate source boundary differs")
        ensure(candidate.get("page") == SOURCE_PAGE, "candidate page boundary differs")
        ensure(candidate.get("coverage_status") == "unresolved", "candidate input status differs")
        ensure(candidate.get("evidence_signatures") == [], "unresolved candidate unexpectedly has evidence")
    return package


def verify_source(repository: Path) -> dict[str, Any]:
    row = read_source_row(repository)
    ensure(row.get("status") == "active", "Bigster brochure source is not active")
    ensure(row.get("source_type") == "brochure_pdf", "Bigster source type differs")
    ensure(row.get("document_date") == "2025-12-10", "Bigster source date differs")
    ensure(row.get("file_path") == SOURCE_PATH.as_posix(), "Bigster source path differs")
    ensure(row.get("sha256") == SOURCE_SHA256, "Bigster source registry hash differs")
    archived = repository / SOURCE_PATH
    ensure(archived.is_file(), "archived Bigster brochure is missing")
    ensure(sha256(archived) == SOURCE_SHA256, "archived Bigster brochure hash differs")
    return {
        "source_code": SOURCE_CODE,
        "file_path": SOURCE_PATH.as_posix(),
        "sha256": SOURCE_SHA256,
        "page": SOURCE_PAGE,
        "review_basis": "authored visual review of the archived page-20 four-column technical table",
    }


def validate_prior_chunk(repository: Path) -> dict[str, Any]:
    payload = load_json_object(
        repository / PRIOR_CHUNK_REVIEW,
        "prior Bigster page-20 unresolved review chunk 1",
    )
    ensure(
        payload.get("kind") == "bigster_technical_page20_unresolved_review_chunk1",
        "prior chunk kind differs",
    )
    ensure(payload.get("package_id") == "residual_gap_016", "prior chunk package differs")
    ensure(payload.get("status") == "complete", "prior chunk is not complete")
    scope = payload.get("scope")
    summary = payload.get("summary")
    ensure(isinstance(scope, Mapping), "prior chunk scope is missing")
    ensure(isinstance(summary, Mapping), "prior chunk summary is missing")
    ensure(scope.get("candidate_count") == 40, "prior chunk candidate count differs")
    ensure(scope.get("group_candidate_count") == 69, "prior chunk group count differs")
    ensure(scope.get("chunk_index") == 1, "prior chunk index differs")
    ensure(scope.get("chunk_count") == 2, "prior chunk count differs")
    ensure(summary.get("selected_evidence_signature_count") == 0, "prior chunk evidence signatures differ")
    ensure(summary.get("selected_evidence_record_count") == 0, "prior chunk evidence records differ")
    return {
        "report_path": PRIOR_CHUNK_REVIEW.as_posix(),
        "package_id": "residual_gap_016",
        "status": "complete",
        "candidate_count": 40,
        "group_candidate_count": 69,
        "chunk_index": 1,
        "chunk_count": 2,
        "selected_evidence_signature_count": 0,
        "selected_evidence_record_count": 0,
        "reason": "Chunk 2 completes the same 69-candidate Bigster page-20 unresolved group without changing or reinterpreting the 40 decisions recorded in chunk 1.",
    }


def authored_partition(candidates: Sequence[Mapping[str, Any]]) -> dict[int, dict[str, Any]]:
    partition: dict[int, dict[str, Any]] = {}
    used: set[int] = set()
    for logical_row, indexes, anchor in ROW_ASSIGNMENTS:
        for index in indexes:
            ensure(1 <= index <= len(candidates), f"authored index out of range: {index}")
            ensure(index not in used, f"authored index duplicated: {index}")
            used.add(index)
            is_anchor = anchor == index
            decision = (
                "unresolved_signature_mismatch"
                if is_anchor
                else "context_only_non_import"
            )
            if is_anchor:
                rationale = (
                    "The complete logical row is legible from the visual page layout, but this residual package contains no "
                    "attached conservative evidence signature. The source fact is recorded for review only and does not approve an import."
                )
                role = "logical_row_anchor"
            elif logical_row.endswith("_footnote") or logical_row.endswith("_footnotes"):
                rationale = (
                    "This extracted line is source footnote context. It qualifies nearby printed values but is not an independent observation."
                )
                role = "footnote_context"
                if logical_row == "iso_3832_footnote":
                    rationale = (
                        "This extracted line is a source note preserved for interpretation boundaries; it is not an independent observation."
                    )
                    role = "source_note_context"
            elif logical_row.endswith("_note"):
                rationale = (
                    "This extracted line is a source note preserved for interpretation boundaries; it is not an independent observation."
                )
                role = "source_note_context"
            elif logical_row.endswith("_label"):
                rationale = (
                    "This extracted line is a surrounding row label without a complete value group in this chunk and is not promoted to data."
                )
                role = "surrounding_row_label_fragment"
            else:
                rationale = (
                    "This line is a continuation or value fragment of the visually grouped logical row; it is not treated as a separate observation."
                )
                role = "logical_row_fragment"
            partition[index] = {
                "logical_row": logical_row,
                "row_role": role,
                "authored_decision": decision,
                "rationale": rationale,
                "source_facts": [ROW_FACTS[logical_row]] if is_anchor else [],
            }
    ensure(used == set(range(1, len(candidates) + 1)), "authored candidate partition differs")
    return partition


def build_review(prioritization: Mapping[str, Any], repository: Path) -> dict[str, Any]:
    package = validate_prioritization(prioritization)
    source_receipt = verify_source(repository)
    prior_chunk = validate_prior_chunk(repository)
    candidates = package["candidates"]
    partition = authored_partition(candidates)

    decisions: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    for index, candidate in enumerate(candidates, 1):
        authored = partition[index]
        decision = authored["authored_decision"]
        ensure(decision in DECISION_STATUSES, f"unknown authored decision: {decision}")
        status_counts[decision] += 1
        decisions.append(
            {
                "candidate_id": candidate["candidate_id"],
                "source_code": SOURCE_CODE,
                "page": SOURCE_PAGE,
                "line_start": candidate["line_start"],
                "line_end": candidate["line_end"],
                "exact_text": candidate["exact_text"],
                "candidate_kind": candidate["candidate_kind"],
                "input_coverage_status": "unresolved",
                "logical_row": authored["logical_row"],
                "row_role": authored["row_role"],
                "authored_decision": decision,
                "rationale": authored["rationale"],
                "selected_evidence_signature_count": 0,
                "selected_evidence_record_count": 0,
                "selected_evidence_signatures": [],
                "source_facts": authored["source_facts"],
            }
        )

    ensure(
        status_counts
        == Counter(
            {
                "context_only_non_import": 21,
                "unresolved_signature_mismatch": 8,
            }
        ),
        "authored decision distribution differs",
    )

    return {
        "version": REVIEW_VERSION,
        "kind": REVIEW_KIND,
        "reviewed_on": REVIEWED_ON,
        "status": "complete",
        "source_prioritization": DEFAULT_PRIORITIZATION.as_posix(),
        "package_id": PACKAGE_ID,
        "source_receipt": source_receipt,
        "scope": {
            "candidate_count": 29,
            "group_candidate_count": 69,
            "chunk_index": 2,
            "chunk_count": 2,
            "source_code": SOURCE_CODE,
            "model_code": "bigster",
            "domain": "technical_tables",
            "page": SOURCE_PAGE,
            "input_coverage_status": "unresolved",
            "attached_evidence_signature_count": 0,
            "attached_evidence_record_count": 0,
        },
        "source_page_layout": {
            "table_type": "four-column technical specification table",
            "powertrain_columns": list(POWERTRAIN_COLUMNS),
            "column_labels": {
                "mild_hybrid_g_140": "MILD HYBRID-G 140",
                "mild_hybrid_140": "MILD HYBRID 140",
                "hybrid_g_150_4x4": "HYBRID-G 150 4×4",
                "hybrid_155": "HYBRID 155",
            },
            "row_grouping_basis": "authored visual review; wrapped pdftotext lines, labels, footnotes and notes are grouped by alignment and source context",
        },
        "policy": {
            "candidate_id_and_exact_text_cited": True,
            "source_page_boundary_preserved": True,
            "source_page_layout_used_for_row_disambiguation": True,
            "wrapped_lines_not_promoted_to_independent_observations": True,
            "footnotes_and_notes_not_promoted_to_observations": True,
            "zero_attached_evidence_preserved": True,
            "source_facts_do_not_authorize_import": True,
            "literal_source_values_preserved_without_invented_interpretation": True,
            "prior_chunk_decisions_not_duplicated": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "candidate_count": 29,
            "logical_row_count": len(ROW_ASSIGNMENTS),
            "decision_counts": {
                status: status_counts.get(status, 0)
                for status in sorted(DECISION_STATUSES)
            },
            "selected_evidence_signature_count": 0,
            "selected_evidence_record_count": 0,
            "candidates_with_source_facts": sum(
                1 for item in decisions if item["source_facts"]
            ),
            "candidates_without_source_facts": sum(
                1 for item in decisions if not item["source_facts"]
            ),
        },
        "prior_chunk_reference": prior_chunk,
        "decisions": decisions,
        "semantic_boundaries": {
            "review_is_not_import_approval": True,
            "wrapped_fragments_footnotes_and_notes_are_context_only": True,
            "clear_source_rows_without_signatures_remain_unresolved": True,
            "printed_slashes_asterisks_and_value_order_are_preserved": True,
            "source_values_are_not_projected_to_configurations": True,
            "chunk_1_decisions_remain_unchanged": True,
            "no_configuration_projection_is_created": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": "Review the first bounded chunk of unresolved Duster mini-brochure page-21 technical candidates without creating master-data rows or approved import specifications.",
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    counts = summary["decision_counts"]
    lines = [
        "# Bigster Technical Page 20 Unresolved Review — Chunk 2",
        "",
        "Authored review of `residual_gap_017`. Twenty-nine extraction candidates complete the page-20 unresolved group; the review records literal source facts but does not approve imports.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Reviewed candidates | {summary['candidate_count']} |",
        f"| Logical visual groups | {summary['logical_row_count']} |",
        f"| Context-only non-import | {counts['context_only_non_import']} |",
        f"| Unresolved signature mismatch | {counts['unresolved_signature_mismatch']} |",
        f"| Candidates with source facts | {summary['candidates_with_source_facts']} |",
        "| Attached evidence signatures | 0 |",
        "| Attached evidence records | 0 |",
        "",
        "## Visual table boundary",
        "",
        "The page continues the same four powertrain columns: `MILD HYBRID-G 140`, `MILD HYBRID 140`, `HYBRID-G 150 4×4` and `HYBRID 155`. Wrapped `pdftotext` lines, labels, footnotes and notes are grouped by visual alignment and source context rather than treated as independent records.",
        "",
        "## Candidate decisions",
        "",
        "| Line | Candidate | Logical row | Role | Decision | Exact text |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for item in payload["decisions"]:
        exact = str(item["exact_text"]).replace("|", "\\|")
        lines.append(
            f"| {item['line_start']} | `{item['candidate_id']}` | `{item['logical_row']}` | "
            f"`{item['row_role']}` | `{item['authored_decision']}` | {exact} |"
        )
    lines.extend(["", "## Review-only source facts", ""])
    for item in payload["decisions"]:
        if not item["source_facts"]:
            continue
        fact = item["source_facts"][0]
        lines.append(f"### Line {item['line_start']} — `{item['logical_row']}`")
        lines.append("")
        lines.append(item["rationale"])
        lines.append("")
        for column in POWERTRAIN_COLUMNS:
            values = "; ".join(
                f"`{value}`" for value in fact["values_by_powertrain"][column]
            )
            lines.append(f"- `{column}`: {values}")
        lines.append(f"- Boundary: {fact['reason']}")
        lines.append("")
    prior = payload["prior_chunk_reference"]
    lines.extend(
        [
            "## Chunk boundary",
            "",
            f"This report completes the 69-candidate page-20 unresolved group after `{prior['report_path']}` reviewed the first {prior['candidate_count']} candidates. Chunk 1 remains unchanged and selected evidence remains zero in both chunks.",
            "",
            "## Safety boundary",
            "",
            "- no file under `data/master` is changed;",
            "- no approved import specification is created or changed;",
            "- all 29 exact candidate IDs, texts, pages and line ranges are preserved;",
            "- zero attached evidence signatures and records remain zero;",
            "- visually legible values are source findings only, not approved observations;",
            "- labels, wrapped fragments, footnotes and notes are not promoted to standalone data;",
            "- printed value order, slashes and asterisks are preserved without invented interpretation;",
            "- no values are projected between powertrains or configurations.",
            "",
            "## Next package",
            "",
            f"**{payload['next_package']['name']}** — {payload['next_package']['goal']}",
            "",
        ]
    )
    return "\n".join(lines)


def ensure_safe_output(repository: Path, path: Path) -> Path:
    resolved = path if path.is_absolute() else repository / path
    resolved = resolved.resolve()
    for restricted in (repository / "data/master", repository / "data/imports"):
        try:
            resolved.relative_to(restricted.resolve())
        except ValueError:
            continue
        raise BigsterPage20UnresolvedChunk2ReviewError(
            f"output path is restricted: {path}"
        )
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BigsterPage20UnresolvedChunk2ReviewError(
            f"cannot read {label}: {exc}"
        ) from exc
    ensure(actual == expected, f"{label} differs from deterministic output")


def build_from_path(
    repository: Path, prioritization_path: Path
) -> tuple[dict[str, Any], str]:
    resolved = (
        prioritization_path
        if prioritization_path.is_absolute()
        else repository / prioritization_path
    )
    prioritization = load_json_object(resolved, "residual-gap prioritization")
    payload = build_review(prioritization, repository)
    return payload, render_markdown(payload)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--prioritization", type=Path, default=DEFAULT_PRIORITIZATION)
    result.add_argument("--json", type=Path, default=DEFAULT_JSON)
    result.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    result.add_argument("--verify", action="store_true")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    repository = repository_root()
    try:
        payload, markdown = build_from_path(repository, arguments.prioritization)
        json_output = ensure_safe_output(repository, arguments.json)
        markdown_output = ensure_safe_output(repository, arguments.markdown)
        json_text = canonical_json(payload)
        if arguments.verify:
            verify_output(json_output, json_text, "Bigster page-20 chunk-2 review JSON")
            verify_output(
                markdown_output,
                markdown,
                "Bigster page-20 chunk-2 review Markdown",
            )
            print("Bigster technical page-20 unresolved review chunk 2: PASS")
        else:
            write_atomic(json_output, json_text)
            write_atomic(markdown_output, markdown)
            print(f"JSON report written to {json_output}")
            print(f"Markdown report written to {markdown_output}")
        summary = payload["summary"]
        print(f"Candidates reviewed: {summary['candidate_count']}")
        print(
            "Unresolved signature mismatches: "
            f"{summary['decision_counts']['unresolved_signature_mismatch']}"
        )
        print("Selected evidence signatures: 0")
        print("Selected evidence records: 0")
        return 0
    except BigsterPage20UnresolvedChunk2ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
