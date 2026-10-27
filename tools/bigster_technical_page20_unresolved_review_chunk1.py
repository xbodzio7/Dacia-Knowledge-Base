#!/usr/bin/env python3
"""Build or verify chunk 1 of the authored Bigster page-20 unresolved review."""

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
REVIEW_KIND = "bigster_technical_page20_unresolved_review_chunk1"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path(
    "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
)
DEFAULT_JSON = Path(
    "data/reporting/bigster_technical_page20_unresolved_review_chunk1.json"
)
DEFAULT_MARKDOWN = Path(
    "data/reporting/bigster_technical_page20_unresolved_review_chunk1.md"
)
PRIOR_PAGE20_REVIEW = Path(
    "data/reporting/bigster_technical_page20_ambiguity_review.json"
)
PACKAGE_ID = "residual_gap_016"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
SOURCE_PAGE = 20
SOURCE_PATH = Path("PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf")
SOURCE_SHA256 = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
PACKAGE_CANDIDATE_DIGEST = "e6d340a4fba44f5a5d69b30a27e5a64b8a25b378e8940b4b641a5fdfcbd21101"
NEXT_PACKAGE = "Bigster Technical Page 20 Unresolved Review — Chunk 2"
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


class BigsterPage20UnresolvedChunk1ReviewError(RuntimeError):
    """Controlled authored-review failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise BigsterPage20UnresolvedChunk1ReviewError(message)


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
        raise BigsterPage20UnresolvedChunk1ReviewError(
            f"cannot read {label}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise BigsterPage20UnresolvedChunk1ReviewError(
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
        raise BigsterPage20UnresolvedChunk1ReviewError(
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
        raise BigsterPage20UnresolvedChunk1ReviewError(
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
    "propulsion": source_fact(
        "propulsion_system",
        {
            "mild_hybrid_g_140": ["Benzyna", "LPG", "Elektryczny mild hybrid 48 V"],
            "mild_hybrid_140": ["Benzyna", "Elektryczny mild hybrid 48 V"],
            "hybrid_g_150_4x4": ["Benzyna", "LPG", "Elektryczny mild hybrid 48 V"],
            "hybrid_155": ["Benzyna", "Elektryczny full hybrid 280 V"],
        },
        "The complete multi-line propulsion row is visually legible, but this residual package has no attached conservative evidence signature.",
    ),
    "maximum_power": source_fact(
        "maximum_power",
        {
            "mild_hybrid_g_140": ["103 kW (140 KM) przy 5500 obr./min"],
            "mild_hybrid_140": ["103 kW (140 KM) przy 5500 obr./min"],
            "hybrid_g_150_4x4": [
                "103 kW (140 KM) przy 4500 obr./min – silnik spalinowy",
                "113 kW (150 KM) – moc łączna",
            ],
            "hybrid_155": ["116 kW (155 KM) przy 5300 obr./min"],
        },
        "The values and combustion-versus-combined-power distinction are visible in the row, but no exact signature is attached to the package.",
    ),
    "maximum_torque": source_fact(
        "maximum_torque",
        {
            "mild_hybrid_g_140": ["230 N.m przy 2100 obr./min"],
            "mild_hybrid_140": ["230 N.m przy 2100 obr./min"],
            "hybrid_g_150_4x4": [
                "230 N.m przy 4000 obr./min – silnik spalinowy",
                "87 N.m przy 1630 obr./min – elektryczny",
            ],
            "hybrid_155": [
                "172 N.m przy 3000 obr./min – silnik spalinowy",
                "205 N.m przy 0–1630 obr./min – elektryczny",
            ],
        },
        "The complete multi-line torque row is visually legible; the asterisk remains source context, and no exact signature is attached.",
    ),
    "injection_type": source_fact(
        "injection_type",
        {column: ["Wtrysk bezpośredni"] for column in POWERTRAIN_COLUMNS},
        "All four columns state direct injection, but the unresolved package carries no evidence signature.",
    ),
    "engine_displacement": source_fact(
        "engine_displacement_cm3",
        {
            "mild_hybrid_g_140": ["1199"],
            "mild_hybrid_140": ["1199"],
            "hybrid_g_150_4x4": ["1199"],
            "hybrid_155": ["1789"],
        },
        "The displacement row is complete but remains review-only without an attached signature.",
    ),
    "cylinders_valves": source_fact(
        "cylinders_and_valves",
        {
            "mild_hybrid_g_140": ["3 cylindry", "12 zaworów"],
            "mild_hybrid_140": ["3 cylindry", "12 zaworów"],
            "hybrid_g_150_4x4": ["3 cylindry", "12 zaworów"],
            "hybrid_155": ["4 cylindry", "16 zaworów"],
        },
        "The two-line row is visually complete, but no exact candidate signature is attached.",
    ),
    "emissions_standard": source_fact(
        "emissions_standard",
        {column: ["Euro 6e-bis"] for column in POWERTRAIN_COLUMNS},
        "The shared emissions standard is visible for all columns but has no attached signature in this package.",
    ),
    "particulate_filter": source_fact(
        "particulate_filter",
        {column: ["Tak"] for column in POWERTRAIN_COLUMNS},
        "The visually shared yes marker spans all four powertrains; it is not converted into approved data without a signature.",
    ),
    "traction_battery": source_fact(
        "traction_battery",
        {
            "mild_hybrid_g_140": ["Litowo-jonowy", "48 V", "0,84 kWh"],
            "mild_hybrid_140": ["Litowo-jonowy", "48 V", "0,84 kWh"],
            "hybrid_g_150_4x4": ["Litowo-jonowy", "48 V", "0,84 kWh"],
            "hybrid_155": ["Litowo-jonowy", "280 V", "1,4 kWh"],
        },
        "The type, voltage and capacity are visually joined within one row; no scalar or compound signature is attached.",
    ),
    "maximum_speed": source_fact(
        "maximum_speed_kmh",
        {column: ["180"] for column in POWERTRAIN_COLUMNS},
        "The complete row is visible but remains unresolved because no evidence signature is attached.",
    ),
    "acceleration_0_100": source_fact(
        "acceleration_0_100_s",
        {
            "mild_hybrid_g_140": ["10,0"],
            "mild_hybrid_140": ["9,8"],
            "hybrid_g_150_4x4": ["10,4"],
            "hybrid_155": ["9,7"],
        },
        "The complete acceleration row is visible but is not approved for import without an exact signature.",
    ),
    "drivetrain": source_fact(
        "drivetrain",
        {
            "mild_hybrid_g_140": ["4×2"],
            "mild_hybrid_140": ["4×2"],
            "hybrid_g_150_4x4": ["4×4 z tylnym silnikiem elektrycznym"],
            "hybrid_155": ["4×2"],
        },
        "The third-column continuation is visually part of the drivetrain row; no signature is attached and no projection is created.",
    ),
    "gearbox": source_fact(
        "gearbox_type_and_gears",
        {
            "mild_hybrid_g_140": ["Manualna", "6-biegowa"],
            "mild_hybrid_140": ["Manualna", "6-biegowa"],
            "hybrid_g_150_4x4": ["Automatyczna", "dwusprzęgłowa", "6-biegowa"],
            "hybrid_155": ["Automatyczna", "Multi-mode", "4+2"],
        },
        "The multi-line gearbox row is visually complete, but no exact compound signature is attached.",
    ),
    "front_brakes": source_fact(
        "front_brake_disc_dimensions_mm",
        {column: ["Φ296x26"] for column in POWERTRAIN_COLUMNS},
        "The diameter and thickness values are visible across all columns, but no attached signature supports approval.",
    ),
    "homologation_protocol": source_fact(
        "homologation_protocol",
        {column: ["WLTP(3)"] for column in POWERTRAIN_COLUMNS},
        "The shared protocol label and footnote marker are source context; no signature is attached.",
    ),
    "eco_mode": source_fact(
        "eco_mode",
        {column: ["Tak"] for column in POWERTRAIN_COLUMNS},
        "The visually shared yes marker spans all four columns but remains review-only without evidence signatures.",
    ),
}


# Indexes are 1-based positions in the exact residual_gap_016 candidate order.
ROW_ASSIGNMENTS: tuple[tuple[str, tuple[int, ...], int | None], ...] = (
    ("powertrain_column_headers", (1, 2), None),
    ("propulsion", (3, 4, 5, 6, 7, 8, 9), 5),
    ("maximum_power", (10, 11), 11),
    ("maximum_torque", (12, 13, 14, 15, 16, 17), 12),
    ("injection_type", (18,), 18),
    ("engine_displacement", (19,), 19),
    ("cylinders_valves", (20, 21), 21),
    ("emissions_standard", (22,), 22),
    ("particulate_filter", (23,), 23),
    ("traction_battery", (24, 25), 25),
    ("maximum_speed", (26,), 26),
    ("acceleration_0_100", (27,), 27),
    ("drivetrain", (28, 29), 28),
    ("gearbox", (30, 31, 32, 33), 30),
    ("front_brakes", (34, 35), 34),
    ("rear_brakes_prior_review", (36, 37, 38), None),
    ("homologation_protocol", (39,), 39),
    ("eco_mode", (40,), 40),
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
    ensure(len(matches) == 1, "residual_gap_016 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "bigster", "package model differs")
    ensure(package.get("domain") == "technical_tables", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "unresolved", "package status differs")
    ensure(package.get("group_candidate_count") == 69, "package group count differs")
    ensure(package.get("chunk_index") == 1, "package chunk index differs")
    ensure(package.get("chunk_count") == 2, "package chunk count differs")
    ensure(package.get("candidate_count") == 40, "package candidate count differs")
    ensure(package.get("evidence_signature_count") == 0, "package evidence signatures differ")
    ensure(package.get("evidence_record_count") == 0, "package evidence records differ")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 40, "package candidates differ")
    ensure(candidate_digest(candidates) == PACKAGE_CANDIDATE_DIGEST, "package candidate content differs")
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


def validate_prior_review(repository: Path) -> dict[str, Any]:
    payload = load_json_object(repository / PRIOR_PAGE20_REVIEW, "prior Bigster page-20 review")
    ensure(payload.get("kind") == "bigster_technical_page20_ambiguity_review", "prior review kind differs")
    ensure(payload.get("package_id") == "residual_gap_001", "prior review package differs")
    ensure(payload.get("status") == "complete", "prior review is not complete")
    decisions = payload.get("decisions")
    ensure(isinstance(decisions, list), "prior review decisions are missing")
    rear = [item for item in decisions if isinstance(item, Mapping) and item.get("line_start") == 77]
    ensure(len(rear) == 1, "prior rear-brake decision differs")
    ensure(rear[0].get("authored_decision") == "covered_by_selected_evidence", "prior rear-brake status differs")
    return {
        "report_path": PRIOR_PAGE20_REVIEW.as_posix(),
        "package_id": "residual_gap_001",
        "candidate_id": rear[0].get("candidate_id"),
        "line_start": 77,
        "authored_decision": "covered_by_selected_evidence",
        "reason": "Chunk-1 lines 74, 79 and 80 are split fragments of the same rear-brake row already resolved around line 77; they remain context-only and do not duplicate or replace the prior selected evidence.",
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
            if logical_row == "rear_brakes_prior_review":
                rationale = (
                    "This line is a split fragment of the rear-brake row already resolved in residual_gap_001; "
                    "it is preserved as context and does not duplicate the prior evidence decision."
                )
                role = "prior_review_fragment"
            elif logical_row == "powertrain_column_headers":
                rationale = (
                    "This line is part of the two-line powertrain column header and is not an independent technical observation."
                )
                role = "column_header_fragment"
            elif is_anchor:
                rationale = (
                    "The complete logical row is legible from the visual page layout, but this residual package contains no "
                    "attached conservative evidence signature. The source fact is recorded for review only and does not approve an import."
                )
                role = "logical_row_anchor"
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
    prior_review = validate_prior_review(repository)
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
                "context_only_non_import": 24,
                "unresolved_signature_mismatch": 16,
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
            "candidate_count": 40,
            "group_candidate_count": 69,
            "chunk_index": 1,
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
            "row_grouping_basis": "authored visual review; wrapped pdftotext lines are grouped by horizontal alignment, labels and column boundaries",
        },
        "policy": {
            "candidate_id_and_exact_text_cited": True,
            "source_page_boundary_preserved": True,
            "source_page_layout_used_for_row_disambiguation": True,
            "wrapped_lines_not_promoted_to_independent_observations": True,
            "zero_attached_evidence_preserved": True,
            "source_facts_do_not_authorize_import": True,
            "prior_review_decisions_not_duplicated": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "candidate_count": 40,
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
        "prior_review_reference": prior_review,
        "decisions": decisions,
        "milestone_review": {
            "package_interval": 5,
            "packages_reviewed": [
                "Bigster Equipment Page 21 Ambiguity Review",
                "Jogger Equipment Page 21 Ambiguity Review",
                "Sandero Equipment Page 18 Ambiguity Review",
                "Sandero Equipment Page 19 Ambiguity Review",
                "Sandero Stepway Equipment Page 18 Ambiguity Review",
            ],
            "durable_architectural_decision_required": False,
            "migration_record_required": False,
            "separate_review_only_pull_request_required": False,
            "conclusion": "The five-package review confirms that the existing authored-review vocabulary, evidence boundaries and no-import policy remain sufficient; the residual queue continues without a separate review-only package.",
        },
        "semantic_boundaries": {
            "review_is_not_import_approval": True,
            "column_headers_and_wrapped_fragments_are_context_only": True,
            "clear_source_rows_without_signatures_remain_unresolved": True,
            "source_values_are_not_projected_to_configurations": True,
            "rear_brake_fragments_defer_to_residual_gap_001": True,
            "no_configuration_projection_is_created": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": "Review chunk 2 of the remaining 29 unresolved technical candidates from Bigster brochure page 20 without creating master-data rows or approved import specifications.",
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    counts = summary["decision_counts"]
    lines = [
        "# Bigster Technical Page 20 Unresolved Review — Chunk 1",
        "",
        "Authored review of `residual_gap_016`. Forty extraction candidates are regrouped into visual table rows; the review records source facts but does not approve imports.",
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
        "The page contains four powertrain columns: `MILD HYBRID-G 140`, `MILD HYBRID 140`, `HYBRID-G 150 4×4` and `HYBRID 155`. Wrapped `pdftotext` lines are grouped by their visual row alignment rather than treated as independent records.",
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
        lines.append(
            f"### Line {item['line_start']} — `{item['logical_row']}`"
        )
        lines.append("")
        lines.append(item["rationale"])
        lines.append("")
        for column in POWERTRAIN_COLUMNS:
            values = "; ".join(f"`{value}`" for value in fact["values_by_powertrain"][column])
            lines.append(f"- `{column}`: {values}")
        lines.append(f"- Boundary: {fact['reason']}")
        lines.append("")
    prior = payload["prior_review_reference"]
    lines.extend(
        [
            "## Prior rear-brake decision",
            "",
            f"Lines 74, 79 and 80 remain context-only fragments. The exact rear-brake evidence decision is preserved in `{prior['report_path']}` at line {prior['line_start']} (`{prior['candidate_id']}`), with status `{prior['authored_decision']}`.",
            "",
            "## Five-package milestone review",
            "",
            payload["milestone_review"]["conclusion"],
            "",
            "## Safety boundary",
            "",
            "- no file under `data/master` is changed;",
            "- no approved import specification is created or changed;",
            "- all 40 exact candidate IDs, texts, pages and line ranges are preserved;",
            "- zero attached evidence signatures and records remain zero;",
            "- visually legible values are source findings only, not approved observations;",
            "- column headers and wrapped fragments are not promoted to standalone data;",
            "- the prior rear-brake evidence decision is referenced rather than duplicated.",
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
        raise BigsterPage20UnresolvedChunk1ReviewError(
            f"output path is restricted: {path}"
        )
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BigsterPage20UnresolvedChunk1ReviewError(
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
            verify_output(json_output, json_text, "Bigster page-20 chunk-1 review JSON")
            verify_output(
                markdown_output,
                markdown,
                "Bigster page-20 chunk-1 review Markdown",
            )
            print("Bigster technical page-20 unresolved review chunk 1: PASS")
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
    except BigsterPage20UnresolvedChunk1ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
