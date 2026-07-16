#!/usr/bin/env python3
"""Generate deterministic configuration-gap evidence review reports."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import configuration_gap_triage


DEFAULT_EVIDENCE_SPEC = Path(
    "data/reporting/configuration_gap_evidence.json"
)
DEFAULT_COMPLETENESS_SPEC = (
    configuration_gap_triage.DEFAULT_SPEC
)
CLASSIFICATIONS = {
    "found",
    "not_stated",
    "ambiguous",
    "out_of_scope",
}
REVIEW_SCOPES = {
    "structured_evidence_only",
    "source_page_evidence",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SOURCE_NOTE_PATTERN = re.compile(
    r"^Source page (?P<page>[1-9][0-9]*)"
    r"(?:, section (?P<section>[^:]+))?: "
    r"(?P<text>.+)$"
)


class GapEvidenceError(RuntimeError):
    """Controlled configuration-gap evidence failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GapEvidenceError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GapEvidenceError(f"{label} must be a list")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise GapEvidenceError(f"{label} must be a non-empty string")
    return value


def read_json(path: Path, label: str) -> Mapping[str, Any]:
    if not path.is_file():
        raise GapEvidenceError(f"{label} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GapEvidenceError(f"cannot read {label}: {exc}") from exc
    return require_mapping(payload, label)


def read_csv_rows(path: Path, label: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise GapEvidenceError(f"{label} does not exist: {path}")
    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            return list(csv.DictReader(handle))
    except (OSError, csv.Error) as exc:
        raise GapEvidenceError(f"cannot read {label}: {exc}") from exc


def parse_source_note(note: str) -> tuple[int, str, str]:
    match = SOURCE_NOTE_PATTERN.fullmatch(note)
    if match is None:
        raise GapEvidenceError(
            f"availability note has unsupported source form: {note!r}"
        )
    return (
        int(match.group("page")),
        match.group("section") or "",
        match.group("text"),
    )


def triage_index(
    triage_report: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in require_list(triage_report.get("queue"), "triage queue"):
        row = require_mapping(item, "triage queue item")
        key = require_string(row.get("triage_key"), "triage_key")
        if key in result:
            raise GapEvidenceError(f"duplicate triage key: {key}")
        result[key] = row
    return result


def decision_index(
    evidence_spec: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in require_list(
        evidence_spec.get("decisions"),
        "evidence decisions",
    ):
        row = require_mapping(item, "evidence decision")
        key = require_string(row.get("triage_key"), "decision triage_key")
        if key in result:
            raise GapEvidenceError(f"duplicate evidence decision: {key}")
        result[key] = row
    return result


def load_master_indexes(
    repository: Path,
) -> tuple[
    dict[tuple[str, str], Mapping[str, str]],
    dict[str, Mapping[str, str]],
    dict[str, Mapping[str, str]],
]:
    availability_rows = read_csv_rows(
        repository
        / "data"
        / "master"
        / "configuration_attribute_availability.csv",
        "configuration availability",
    )
    configuration_rows = read_csv_rows(
        repository / "data" / "master" / "configurations.csv",
        "configurations",
    )
    attribute_rows = read_csv_rows(
        repository / "data" / "master" / "attributes.csv",
        "attributes",
    )

    availability: dict[tuple[str, str], Mapping[str, str]] = {}
    for row in availability_rows:
        key = (
            row.get("configuration_code", ""),
            row.get("attribute_code", ""),
        )
        if not all(key):
            raise GapEvidenceError(
                f"availability row has an empty key: {key}"
            )
        if key in availability:
            raise GapEvidenceError(
                f"duplicate current availability key: {key}"
            )
        availability[key] = row

    configurations: dict[str, Mapping[str, str]] = {}
    for row in configuration_rows:
        code = row.get("code", "")
        if not code:
            raise GapEvidenceError("configuration has empty code")
        if code in configurations:
            raise GapEvidenceError(
                f"duplicate configuration code: {code}"
            )
        configurations[code] = row

    attributes: dict[str, Mapping[str, str]] = {}
    for row in attribute_rows:
        code = row.get("code", "")
        if not code:
            raise GapEvidenceError("attribute has empty code")
        if code in attributes:
            raise GapEvidenceError(
                f"duplicate attribute code: {code}"
            )
        attributes[code] = row

    return availability, configurations, attributes


def validate_common_metadata(
    triage_row: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> None:
    fields = (
        "domain",
        "source_code",
        "configuration_code",
        "category",
        "attribute_code",
        "fuel_type_code",
        "document_date",
        "file_path",
        "sha256",
    )
    for field in fields:
        if decision.get(field) != triage_row.get(field):
            raise GapEvidenceError(
                f"decision metadata differs for "
                f"{triage_row.get('triage_key')}: {field}"
            )
    sha256 = decision.get("sha256")
    if (
        not isinstance(sha256, str)
        or SHA256_PATTERN.fullmatch(sha256) is None
    ):
        raise GapEvidenceError(
            f"decision has invalid SHA-256: {sha256!r}"
        )


def validate_availability_basis(
    decision: Mapping[str, Any],
    basis: Mapping[str, Any],
    availability: Mapping[
        tuple[str, str],
        Mapping[str, str],
    ],
) -> dict[str, Any]:
    configuration_code = require_string(
        decision.get("configuration_code"),
        "decision configuration_code",
    )
    basis_attribute = require_string(
        basis.get("attribute_code"),
        "availability basis attribute_code",
    )
    row = availability.get(
        (configuration_code, basis_attribute)
    )
    if row is None:
        raise GapEvidenceError(
            "availability basis record does not exist: "
            f"{configuration_code}/{basis_attribute}"
        )

    expected = {
        "availability_status": row.get(
            "availability_status",
            "",
        ),
        "observation_date": row.get("observation_date", ""),
        "source_code": row.get("source_code", ""),
    }
    for field, value in expected.items():
        if basis.get(field) != value:
            raise GapEvidenceError(
                f"availability basis differs: {field}"
            )
    if row.get("source_code") != decision.get("source_code"):
        raise GapEvidenceError(
            "availability basis source differs from gap source"
        )

    page, section, source_text = parse_source_note(
        row.get("notes", "")
    )
    if basis.get("source_page") != page:
        raise GapEvidenceError(
            "availability basis source_page differs"
        )
    if basis.get("source_section") != section:
        raise GapEvidenceError(
            "availability basis source_section differs"
        )
    if basis.get("source_text") != source_text:
        raise GapEvidenceError(
            "availability basis source_text differs"
        )
    return {
        "type": "availability_record",
        "attribute_code": basis_attribute,
        "availability_status": expected[
            "availability_status"
        ],
        "observation_date": expected["observation_date"],
        "source_code": expected["source_code"],
        "source_page": page,
        "source_section": section,
        "source_text": source_text,
    }


def validate_configuration_basis(
    decision: Mapping[str, Any],
    basis: Mapping[str, Any],
    configurations: Mapping[str, Mapping[str, str]],
    attributes: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    configuration_code = require_string(
        decision.get("configuration_code"),
        "decision configuration_code",
    )
    configuration = configurations.get(configuration_code)
    if configuration is None:
        raise GapEvidenceError(
            f"configuration basis does not exist: "
            f"{configuration_code}"
        )
    field = require_string(
        basis.get("field"),
        "configuration basis field",
    )
    if field != "transmission_type":
        raise GapEvidenceError(
            f"unsupported configuration basis field: {field}"
        )
    value = require_string(
        basis.get("value"),
        "configuration basis value",
    )
    if configuration.get(field) != value:
        raise GapEvidenceError(
            f"configuration basis differs: "
            f"{configuration_code}/{field}"
        )
    if decision.get("attribute_code") != "gear_shift_indicator":
        raise GapEvidenceError(
            "transmission scope basis is limited to "
            "gear_shift_indicator"
        )
    if value != "automatic":
        raise GapEvidenceError(
            "gear-shift scope basis requires automatic transmission"
        )
    attribute = attributes.get("gear_shift_indicator")
    if attribute is None:
        raise GapEvidenceError(
            "gear_shift_indicator attribute is missing"
        )
    description = attribute.get("description", "")
    if "gear-change recommendations" not in description:
        raise GapEvidenceError(
            "gear_shift_indicator description contract differs"
        )
    if basis.get("attribute_description") != description:
        raise GapEvidenceError(
            "configuration basis attribute description differs"
        )
    return {
        "type": "configuration_field",
        "field": field,
        "value": value,
        "attribute_description": description,
    }


def validate_decision(
    triage_row: Mapping[str, Any],
    decision: Mapping[str, Any],
    availability: Mapping[
        tuple[str, str],
        Mapping[str, str],
    ],
    configurations: Mapping[str, Mapping[str, str]],
    attributes: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    validate_common_metadata(triage_row, decision)

    classification = require_string(
        decision.get("classification"),
        "classification",
    )
    if classification not in CLASSIFICATIONS:
        raise GapEvidenceError(
            f"unsupported evidence classification: "
            f"{classification!r}"
        )
    if decision.get("auto_import") is not False:
        raise GapEvidenceError(
            "evidence decisions must keep auto_import disabled"
        )
    reason_code = require_string(
        decision.get("reason_code"),
        "reason_code",
    )
    review_note = require_string(
        decision.get("review_note"),
        "review_note",
    )
    candidate_value = decision.get("candidate_value", "")
    if not isinstance(candidate_value, str):
        raise GapEvidenceError(
            "candidate_value must be a string"
        )

    normalized: dict[str, Any] = {
        "classification": classification,
        "reason_code": reason_code,
        "review_note": review_note,
        "candidate_value": candidate_value,
        "manual_source_review_required": bool(
            decision.get("manual_source_review_required")
        ),
        "auto_import": False,
    }

    if classification == "ambiguous":
        if (
            decision.get("manual_source_review_required")
            is not True
        ):
            raise GapEvidenceError(
                "ambiguous decisions require manual source review"
            )
        if candidate_value:
            raise GapEvidenceError(
                "ambiguous decisions cannot contain candidate values"
            )
        if decision.get("source_page") is not None:
            raise GapEvidenceError(
                "ambiguous decisions cannot claim a source page"
            )
        if decision.get("source_text", ""):
            raise GapEvidenceError(
                "ambiguous decisions cannot claim source text"
            )
        normalized.update(
            {
                "source_page": None,
                "source_section": "",
                "source_text": "",
                "reviewed_pages": [],
                "basis": None,
            }
        )
        return normalized

    if classification == "found":
        page = decision.get("source_page")
        if not isinstance(page, int) or page <= 0:
            raise GapEvidenceError(
                "found decisions require a positive source_page"
            )
        section = require_string(
            decision.get("source_section"),
            "found source_section",
        )
        source_text = require_string(
            decision.get("source_text"),
            "found source_text",
        )
        if not candidate_value:
            raise GapEvidenceError(
                "found decisions require candidate_value"
            )
        if decision.get("manual_source_review_required") is not False:
            raise GapEvidenceError(
                "found decisions cannot remain pending review"
            )
        normalized.update(
            {
                "source_page": page,
                "source_section": section,
                "source_text": source_text,
                "reviewed_pages": [page],
                "basis": None,
            }
        )
        return normalized

    if classification == "not_stated":
        reviewed_pages = decision.get("reviewed_pages")
        if (
            not isinstance(reviewed_pages, list)
            or not reviewed_pages
            or any(
                not isinstance(page, int) or page <= 0
                for page in reviewed_pages
            )
        ):
            raise GapEvidenceError(
                "not_stated decisions require reviewed_pages"
            )
        if candidate_value:
            raise GapEvidenceError(
                "not_stated decisions cannot contain candidate values"
            )
        if decision.get("manual_source_review_required") is not False:
            raise GapEvidenceError(
                "not_stated decisions cannot remain pending review"
            )
        if decision.get("source_text", ""):
            raise GapEvidenceError(
                "not_stated decisions cannot claim source text"
            )
        normalized.update(
            {
                "source_page": None,
                "source_section": "",
                "source_text": "",
                "reviewed_pages": sorted(set(reviewed_pages)),
                "basis": None,
            }
        )
        return normalized

    if candidate_value:
        raise GapEvidenceError(
            "out_of_scope decisions cannot contain candidate values"
        )
    if decision.get("manual_source_review_required") is not False:
        raise GapEvidenceError(
            "out_of_scope decisions cannot remain pending review"
        )
    basis = require_mapping(
        decision.get("basis"),
        "out_of_scope basis",
    )
    basis_type = require_string(
        basis.get("type"),
        "out_of_scope basis type",
    )
    if basis_type == "availability_record":
        normalized_basis = validate_availability_basis(
            decision,
            basis,
            availability,
        )
    elif basis_type == "configuration_field":
        normalized_basis = validate_configuration_basis(
            decision,
            basis,
            configurations,
            attributes,
        )
    else:
        raise GapEvidenceError(
            f"unsupported out_of_scope basis type: "
            f"{basis_type!r}"
        )
    normalized.update(
        {
            "source_page": normalized_basis.get(
                "source_page"
            ),
            "source_section": normalized_basis.get(
                "source_section",
                "",
            ),
            "source_text": normalized_basis.get(
                "source_text",
                "",
            ),
            "reviewed_pages": (
                [normalized_basis["source_page"]]
                if normalized_basis.get("source_page")
                else []
            ),
            "basis": normalized_basis,
        }
    )
    return normalized


def grouped_counts(
    decisions: Sequence[Mapping[str, Any]],
    field: str,
) -> list[dict[str, Any]]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for decision in decisions:
        key = require_string(
            decision.get(field),
            f"decision {field}",
        )
        classification = require_string(
            decision.get("classification"),
            "decision classification",
        )
        groups[key]["total"] += 1
        groups[key][classification] += 1
    return [
        {
            field: key,
            "total": groups[key]["total"],
            "found": groups[key]["found"],
            "not_stated": groups[key]["not_stated"],
            "ambiguous": groups[key]["ambiguous"],
            "out_of_scope": groups[key]["out_of_scope"],
        }
        for key in sorted(groups)
    ]


def build_evidence_report(
    repository: Path,
    triage_report: Mapping[str, Any],
    evidence_spec: Mapping[str, Any],
) -> dict[str, Any]:
    if evidence_spec.get("version") != 1:
        raise GapEvidenceError(
            "evidence specification version must be 1"
        )
    if evidence_spec.get("as_of") != triage_report.get("as_of"):
        raise GapEvidenceError(
            "evidence specification date differs from triage"
        )
    review_scope = evidence_spec.get("review_scope")
    if review_scope not in REVIEW_SCOPES:
        raise GapEvidenceError(
            "evidence specification review_scope differs"
        )
    policy = require_mapping(
        evidence_spec.get("review_policy"),
        "review_policy",
    )
    if policy.get("auto_import") is not False:
        raise GapEvidenceError(
            "review policy must disable automatic import"
        )
    if set(
        require_list(
            policy.get("allowed_classifications"),
            "allowed classifications",
        )
    ) != CLASSIFICATIONS:
        raise GapEvidenceError(
            "review policy classification set differs"
        )

    triage_rows = triage_index(triage_report)
    decision_rows = decision_index(evidence_spec)
    if set(triage_rows) != set(decision_rows):
        missing = sorted(set(triage_rows) - set(decision_rows))
        extra = sorted(set(decision_rows) - set(triage_rows))
        raise GapEvidenceError(
            "evidence decisions do not match triage queue"
            f"; missing: {missing}; extra: {extra}"
        )

    (
        availability,
        configurations,
        attributes,
    ) = load_master_indexes(repository)

    normalized_decisions: list[dict[str, Any]] = []
    for triage_row in sorted(
        triage_rows.values(),
        key=lambda row: int(row.get("sequence", 0)),
    ):
        key = str(triage_row["triage_key"])
        normalized = validate_decision(
            triage_row,
            decision_rows[key],
            availability,
            configurations,
            attributes,
        )
        normalized_decisions.append(
            {
                "sequence": int(triage_row["sequence"]),
                "triage_key": key,
                "domain": triage_row["domain"],
                "source_code": triage_row["source_code"],
                "configuration_code": triage_row[
                    "configuration_code"
                ],
                "category": triage_row["category"],
                "section": triage_row["section"],
                "attribute_code": triage_row[
                    "attribute_code"
                ],
                "fuel_type_code": triage_row[
                    "fuel_type_code"
                ],
                "document_date": triage_row[
                    "document_date"
                ],
                "file_path": triage_row["file_path"],
                "sha256": triage_row["sha256"],
                **normalized,
            }
        )

    counts = Counter(
        row["classification"]
        for row in normalized_decisions
    )
    manual_review = sum(
        1
        for row in normalized_decisions
        if row["manual_source_review_required"]
    )
    candidate_imports = sum(
        1
        for row in normalized_decisions
        if row["classification"] == "found"
        and bool(row["candidate_value"])
    )
    source_documents = sorted(
        {
            (
                row["source_code"],
                row["document_date"],
                row["file_path"],
                row["sha256"],
            )
            for row in normalized_decisions
        }
    )

    basis_counts = Counter(
        (
            row["basis"]["type"]
            if isinstance(row.get("basis"), Mapping)
            else "none"
        )
        for row in normalized_decisions
    )

    pdf_page_review_complete = (
        review_scope == "source_page_evidence"
        and manual_review == 0
    )
    next_action = (
        "plan_evidence_backed_resolution"
        if pdf_page_review_complete
        else "resolve_remaining_source_ambiguity"
        if review_scope == "source_page_evidence"
        else "manual_pdf_page_review"
    )

    return {
        "version": 1,
        "as_of": triage_report["as_of"],
        "review_scope": review_scope,
        "pdf_page_review_complete": pdf_page_review_complete,
        "summary": {
            "total_decisions": len(normalized_decisions),
            "found": counts["found"],
            "not_stated": counts["not_stated"],
            "ambiguous": counts["ambiguous"],
            "out_of_scope": counts["out_of_scope"],
            "manual_source_review_required": manual_review,
            "candidate_imports": candidate_imports,
            "auto_import_enabled": 0,
            "source_documents": len(source_documents),
            "availability_record_bases": basis_counts[
                "availability_record"
            ],
            "configuration_field_bases": basis_counts[
                "configuration_field"
            ],
        },
        "next_action": next_action,
        "groups": {
            "by_source": grouped_counts(
                normalized_decisions,
                "source_code",
            ),
            "by_configuration": grouped_counts(
                normalized_decisions,
                "configuration_code",
            ),
            "by_category": grouped_counts(
                normalized_decisions,
                "category",
            ),
            "by_classification": [
                {
                    "classification": classification,
                    "count": counts[classification],
                }
                for classification in sorted(CLASSIFICATIONS)
            ],
        },
        "source_documents": [
            {
                "source_code": source_code,
                "document_date": document_date,
                "file_path": file_path,
                "sha256": sha256,
                "decisions": sum(
                    1
                    for row in normalized_decisions
                    if row["source_code"] == source_code
                ),
            }
            for (
                source_code,
                document_date,
                file_path,
                sha256,
            ) in source_documents
        ],
        "decisions": normalized_decisions,
    }


def collect_report(
    repository: Path,
    evidence_spec_path: Path,
    completeness_spec_path: Path,
    as_of_value: str | None = None,
) -> dict[str, Any]:
    triage_report = configuration_gap_triage.collect_report(
        repository,
        completeness_spec_path,
        as_of_value,
    )
    evidence_spec = read_json(
        evidence_spec_path,
        "configuration-gap evidence specification",
    )
    return build_evidence_report(
        repository,
        triage_report,
        evidence_spec,
    )


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def render_group_table(
    lines: list[str],
    title: str,
    rows: Sequence[Mapping[str, Any]],
    key: str,
) -> None:
    lines.extend(
        [
            "",
            f"## {title}",
            "",
            "| Group | Total | Found | Not stated | Ambiguous | Out of scope |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row[key]}` | {row['total']} | "
            f"{row['found']} | {row['not_stated']} | "
            f"{row['ambiguous']} | {row['out_of_scope']} |"
        )


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = require_mapping(report.get("summary"), "summary")
    review_scope = report.get("review_scope")
    if review_scope == "source_page_evidence":
        scope_lines = [
            (
                "Relevant registered PDF pages were reviewed through "
                "deterministic text extraction with source hashes preserved."
            ),
            (
                "Unresolved ambiguous decisions remain explicit; "
                "modeling and import are separate."
            ),
        ]
    else:
        scope_lines = [
            (
                "This is a conservative structured-evidence classification. "
                "It does not claim that the seven registered PDFs have been "
                "exhaustively reviewed page by page."
            ),
            (
                "Ambiguous decisions remain queued for manual PDF page review."
            ),
        ]
    lines = [
        "# Configuration Gap Evidence Review",
        "",
        f"As of: `{report['as_of']}`",
        "",
        scope_lines[0],
        "",
        "No value is inferred and automatic import is disabled. "
        + scope_lines[1],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total decisions | {summary['total_decisions']} |",
        f"| Found | {summary['found']} |",
        f"| Not stated | {summary['not_stated']} |",
        f"| Ambiguous | {summary['ambiguous']} |",
        f"| Out of scope | {summary['out_of_scope']} |",
        (
            "| Manual source review required | "
            f"{summary['manual_source_review_required']} |"
        ),
        f"| Candidate imports | {summary['candidate_imports']} |",
        f"| Automatic imports enabled | {summary['auto_import_enabled']} |",
        (
            "| Availability-record bases | "
            f"{summary['availability_record_bases']} |"
        ),
        (
            "| Configuration-field bases | "
            f"{summary['configuration_field_bases']} |"
        ),
    ]

    groups = require_mapping(report.get("groups"), "groups")
    render_group_table(
        lines,
        "By source",
        require_list(groups.get("by_source"), "groups.by_source"),
        "source_code",
    )
    render_group_table(
        lines,
        "By category",
        require_list(
            groups.get("by_category"),
            "groups.by_category",
        ),
        "category",
    )

    lines.extend(
        [
            "",
            "## Decisions",
            "",
            "| # | Classification | Source | Configuration | Attribute | Evidence |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in require_list(report.get("decisions"), "decisions"):
        basis = row.get("basis")
        if isinstance(basis, Mapping):
            evidence = str(basis.get("type", ""))
        elif row.get("classification") == "found":
            evidence = f"source page {row['source_page']}"
        elif row.get("classification") == "not_stated":
            pages = ", ".join(
                str(page) for page in row.get("reviewed_pages", [])
            )
            evidence = f"reviewed pages {pages}"
        else:
            evidence = "manual PDF review required"
        lines.append(
            f"| {row['sequence']} | `{row['classification']}` | "
            f"`{row['source_code']}` | "
            f"`{row['configuration_code']}` | "
            f"`{row['attribute_code']}` | {evidence} |"
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
            "Generate a deterministic, non-inferential evidence "
            "classification for configuration gaps."
        )
    )
    parser.add_argument(
        "--evidence-spec",
        type=Path,
        default=DEFAULT_EVIDENCE_SPEC,
        help="Versioned configuration-gap evidence specification.",
    )
    parser.add_argument(
        "--completeness-spec",
        type=Path,
        default=DEFAULT_COMPLETENESS_SPEC,
        help="Configuration completeness denominator specification.",
    )
    parser.add_argument(
        "--as-of",
        help="Optional inclusive snapshot date in YYYY-MM-DD form.",
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()

    evidence_spec_path = arguments.evidence_spec
    if not evidence_spec_path.is_absolute():
        evidence_spec_path = repository / evidence_spec_path

    completeness_spec_path = arguments.completeness_spec
    if not completeness_spec_path.is_absolute():
        completeness_spec_path = (
            repository / completeness_spec_path
        )

    try:
        report = collect_report(
            repository,
            evidence_spec_path,
            completeness_spec_path,
            arguments.as_of,
        )
        if arguments.json_path is not None:
            write_atomic(
                arguments.json_path,
                render_json(report),
            )
            print(
                "JSON gap evidence report written to "
                f"{arguments.json_path}"
            )
        if arguments.markdown is not None:
            write_atomic(
                arguments.markdown,
                render_markdown(report),
            )
            print(
                "Markdown gap evidence report written to "
                f"{arguments.markdown}"
            )
        summary = report["summary"]
        print("Configuration gap evidence review")
        print("---------------------------------")
        print(f"As of                 : {report['as_of']}")
        print(f"Review scope          : {report['review_scope']}")
        print(
            "PDF page review       : "
            + (
                "complete"
                if report["pdf_page_review_complete"]
                else "incomplete"
            )
        )
        print(
            f"Total decisions       : "
            f"{summary['total_decisions']}"
        )
        print(f"Found                 : {summary['found']}")
        print(f"Not stated            : {summary['not_stated']}")
        print(f"Ambiguous             : {summary['ambiguous']}")
        print(
            f"Out of scope          : "
            f"{summary['out_of_scope']}"
        )
        print(
            "Manual PDF review      : "
            f"{summary['manual_source_review_required']}"
        )
        print(
            f"Candidate imports      : "
            f"{summary['candidate_imports']}"
        )
        print("Automatic import       : disabled")
        return 0
    except (
        GapEvidenceError,
        configuration_gap_triage.GapTriageError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
