#!/usr/bin/env python3
"""Build or verify the authored Sandero Stepway brochure page-18 equipment ambiguity review."""
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
REVIEW_KIND = "sandero_stepway_equipment_page18_ambiguity_review"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path("data/reporting/verified_pdf_candidate_residual_gap_prioritization.json")
DEFAULT_JSON = Path("data/reporting/sandero_stepway_equipment_page18_ambiguity_review.json")
DEFAULT_MARKDOWN = Path("data/reporting/sandero_stepway_equipment_page18_ambiguity_review.md")
PACKAGE_ID = "residual_gap_015"
SOURCE_CODE = "src_pl_sandero_stepway_brochure_20260202"
SOURCE_PAGE = 18
SOURCE_PATH = Path("PDF/Broszury/DACIA SANDERO STEPWAY broszura 20260202.pdf")
SOURCE_SHA256 = "800e6e6df78e55e9fd3ac270dd5df26447c82830c92ced112ee83c3b44595d48"
NEXT_PACKAGE = "Bigster Technical Page 20 Unresolved Review — Chunk 1"
DECISION_STATUSES = {"covered"}
TRIMS = ("essential", "expression", "extreme")


class SanderoStepwayEquipmentPage18ReviewError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SanderoStepwayEquipmentPage18ReviewError(message)


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
        raise SanderoStepwayEquipmentPage18ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SanderoStepwayEquipmentPage18ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise SanderoStepwayEquipmentPage18ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()


def availability_signature(attribute_code: str, availability_status: str) -> dict[str, str]:
    return {"attribute_code": attribute_code, "availability_status": availability_status}


DECISIONS = (
    {
        "candidate_id": "ec4e48ba49e9e26f9b158c5427a8063c899061b5d2343499a5c4695767303f71",
        "line_start": 42,
        "line_end": 42,
        "exact_text": "Relingi dachowe                                          •                    -                      -",
        "decision": "covered",
        "selected": [availability_signature("roof_rails", "standard")],
        "rejected": {
            json.dumps(
                availability_signature("modular_roof_rails", "standard"),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ): (
                "The modular-roof-rail signature belongs to the immediately following, visually distinct row "
                "'Modułowe relingi dachowe (szare Megalith)', which is unavailable in Essential and standard in "
                "Expression and Extreme. Its two Expression records must not be substituted into the plain-roof-rail row."
            )
        },
        "row_context": "complete plain roof-rails row immediately above the distinct modular-roof-rails row",
        "source_availability": {
            "essential": "standard",
            "expression": "not_available",
            "extreme": "not_available",
        },
        "adjacent_row_context": {
            "label": "Modułowe relingi dachowe (szare Megalith)",
            "essential": "not_available",
            "expression": "standard",
            "extreme": "standard",
        },
        "rationale": (
            "The 2026-02-02 brochure prints two consecutive but separate roof-rail rows. The candidate row 'Relingi "
            "dachowe' is standard only in Essential and unavailable in Expression and Extreme. The immediately following "
            "'Modułowe relingi dachowe (szare Megalith)' row has the inverse layout: unavailable in Essential and standard "
            "in Expression and Extreme. The attached Essential roof_rails record is selected; the two Expression "
            "modular_roof_rails records are retained and explicitly rejected as evidence for the adjacent row. The review "
            "does not approve an import or project unavailable states between configurations."
        ),
    },
)


def signature_key(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_source_row(repository: Path) -> dict[str, str]:
    path = repository / "data/master/sources.csv"
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            ensure(reader.fieldnames is not None, "sources.csv has no header")
            matches = [dict(row) for row in reader if row.get("code") == SOURCE_CODE]
    except OSError as exc:
        raise SanderoStepwayEquipmentPage18ReviewError(f"cannot read sources.csv: {exc}") from exc
    ensure(len(matches) == 1, "Sandero Stepway brochure source registry row differs")
    return matches[0]


def validate_prioritization(payload: Mapping[str, Any]) -> dict[str, Any]:
    ensure(payload.get("version") == 1, "prioritization version differs")
    ensure(payload.get("kind") == "verified_pdf_candidate_residual_gap_prioritization", "prioritization kind differs")
    ensure(payload.get("status") == "complete", "prioritization is not complete")
    policy = payload.get("policy")
    ensure(isinstance(policy, Mapping), "prioritization policy is missing")
    ensure(policy.get("master_data_changes") is False, "prioritization changes master data")
    ensure(policy.get("approved_import_spec_generation") is False, "prioritization creates approved imports")
    packages = payload.get("packages")
    ensure(isinstance(packages, list), "prioritization packages are missing")
    matches = [item for item in packages if isinstance(item, Mapping) and item.get("package_id") == PACKAGE_ID]
    ensure(len(matches) == 1, "residual_gap_015 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "sandero_stepway_iii", "package model differs")
    ensure(package.get("domain") == "equipment_matrix", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "ambiguous", "package status differs")
    ensure(package.get("candidate_count") == 1, "package candidate count differs")
    ensure(package.get("evidence_signature_count") == 2, "package evidence signature count differs")
    ensure(package.get("evidence_record_count") == 3, "package evidence record count differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 1, "package candidates differ")
    return package


def verify_source(repository: Path) -> dict[str, Any]:
    row = read_source_row(repository)
    ensure(row.get("status") == "active", "Sandero Stepway brochure source is not active")
    ensure(row.get("source_type") == "brochure_pdf", "Sandero Stepway source type differs")
    ensure(row.get("document_date") == "2026-02-02", "Sandero Stepway source date differs")
    ensure(row.get("file_path") == SOURCE_PATH.as_posix(), "Sandero Stepway source path differs")
    ensure(row.get("sha256") == SOURCE_SHA256, "Sandero Stepway source registry hash differs")
    archived = repository / SOURCE_PATH
    ensure(archived.is_file(), "archived Sandero Stepway brochure is missing")
    ensure(sha256(archived) == SOURCE_SHA256, "archived Sandero Stepway brochure hash differs")
    return {
        "source_code": SOURCE_CODE,
        "file_path": SOURCE_PATH.as_posix(),
        "sha256": SOURCE_SHA256,
        "page": SOURCE_PAGE,
        "review_basis": "authored visual review of the archived page-18 equipment matrix",
    }


def attached_signatures(candidate: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    available = candidate.get("evidence_signatures")
    ensure(isinstance(available, list), "candidate evidence signatures are missing")
    by_key: dict[str, dict[str, Any]] = {}
    for item in available:
        ensure(isinstance(item, Mapping), "candidate evidence signature differs")
        payload = item.get("signature")
        ensure(isinstance(payload, Mapping), "candidate signature payload is missing")
        key = signature_key(payload)
        ensure(key not in by_key, "candidate evidence signature is duplicated")
        by_key[key] = json.loads(json.dumps(dict(item), ensure_ascii=False))
    return by_key


def partition_signatures(
    candidate: Mapping[str, Any],
    expected_selected: Sequence[Mapping[str, Any]],
    rejection_reasons: Mapping[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_key = attached_signatures(candidate)
    selected_keys = [signature_key(item) for item in expected_selected]
    ensure(len(selected_keys) == len(set(selected_keys)), "selected signature is duplicated")
    selected: list[dict[str, Any]] = []
    for key in selected_keys:
        ensure(key in by_key, f"selected signature is not attached to candidate: {key}")
        selected.append(by_key[key])
    rejected_keys = sorted(set(by_key) - set(selected_keys))
    ensure(set(rejected_keys) == set(rejection_reasons), "rejected signature reason assignment differs")
    rejected: list[dict[str, Any]] = []
    for key in rejected_keys:
        item = by_key[key]
        rejected.append({**item, "rejection_reason": rejection_reasons[key]})
    return selected, rejected


def validate_evidence_items(items: Sequence[Mapping[str, Any]]) -> int:
    record_count = 0
    for item in items:
        records = item.get("records")
        ensure(isinstance(records, list) and item.get("record_count") == len(records), "evidence record count differs")
        for record in records:
            ensure(record.get("table") == "configuration_attribute_availability", "evidence table differs")
            ensure(
                str(record.get("configuration_code", "")).startswith("sandero_stepway_iii_"),
                "evidence model boundary differs",
            )
        record_count += len(records)
    return record_count


def build_review(prioritization: Mapping[str, Any], repository: Path) -> dict[str, Any]:
    package = validate_prioritization(prioritization)
    source_receipt = verify_source(repository)
    candidates = package["candidates"]
    ensure(len(DECISIONS) == len(candidates), "authored decision count differs")
    by_id = {str(item["candidate_id"]): item for item in candidates}
    ensure(len(by_id) == len(candidates), "candidate IDs are not unique")
    decisions = []
    for authored in DECISIONS:
        candidate = by_id.get(str(authored["candidate_id"]))
        ensure(candidate is not None, "authored decision candidate is missing")
        ensure(
            candidate.get("line_start") == authored["line_start"] and candidate.get("line_end") == authored["line_end"],
            "candidate line differs",
        )
        ensure(candidate.get("exact_text") == authored["exact_text"], "candidate exact text differs")
        ensure(candidate.get("source_code") == SOURCE_CODE and candidate.get("page") == SOURCE_PAGE, "candidate source boundary differs")
        ensure(candidate.get("coverage_status") == "ambiguous", "candidate input status differs")
        decision = str(authored["decision"])
        ensure(decision in DECISION_STATUSES, f"unknown authored decision: {decision}")
        selected, rejected = partition_signatures(candidate, authored["selected"], authored["rejected"])
        selected_records = validate_evidence_items(selected)
        rejected_records = validate_evidence_items(rejected)
        visual = authored["source_availability"]
        ensure(tuple(visual) == TRIMS, "source availability trim keys differ")
        adjacent = authored["adjacent_row_context"]
        ensure(tuple(key for key in adjacent if key != "label") == TRIMS, "adjacent-row trim keys differ")
        decisions.append(
            {
                "candidate_id": authored["candidate_id"],
                "source_code": SOURCE_CODE,
                "page": SOURCE_PAGE,
                "line_start": authored["line_start"],
                "line_end": authored["line_end"],
                "exact_text": authored["exact_text"],
                "input_coverage_status": "ambiguous",
                "authored_decision": decision,
                "row_context": authored["row_context"],
                "source_availability": visual,
                "adjacent_row_context": adjacent,
                "rationale": authored["rationale"],
                "selected_evidence_signature_count": len(selected),
                "selected_evidence_record_count": selected_records,
                "selected_evidence_signatures": selected,
                "rejected_attached_signature_count": len(rejected),
                "rejected_attached_record_count": rejected_records,
                "rejected_attached_signatures": rejected,
            }
        )
    decision_ids = [item["candidate_id"] for item in decisions]
    ensure(len(decision_ids) == len(set(decision_ids)) == 1, "authored candidate assignment differs")
    counts = Counter(item["authored_decision"] for item in decisions)
    ensure(counts == Counter({"covered": 1}), "authored decision distribution differs")
    selected_signature_count = sum(item["selected_evidence_signature_count"] for item in decisions)
    selected_record_count = sum(item["selected_evidence_record_count"] for item in decisions)
    rejected_signature_count = sum(item["rejected_attached_signature_count"] for item in decisions)
    rejected_record_count = sum(item["rejected_attached_record_count"] for item in decisions)
    ensure((selected_signature_count, selected_record_count) == (1, 1), "selected evidence totals differ")
    ensure((rejected_signature_count, rejected_record_count) == (1, 2), "rejected evidence totals differ")
    return {
        "version": REVIEW_VERSION,
        "kind": REVIEW_KIND,
        "reviewed_on": REVIEWED_ON,
        "status": "complete",
        "source_prioritization": DEFAULT_PRIORITIZATION.as_posix(),
        "package_id": PACKAGE_ID,
        "source_receipt": source_receipt,
        "scope": {
            "candidate_count": 1,
            "source_code": SOURCE_CODE,
            "model_code": "sandero_stepway_iii",
            "domain": "equipment_matrix",
            "page": SOURCE_PAGE,
            "input_coverage_status": "ambiguous",
        },
        "policy": {
            "candidate_id_and_exact_text_cited": True,
            "selected_evidence_copied_without_reinterpretation": True,
            "rejected_evidence_preserved_with_reason": True,
            "source_page_layout_used_for_row_disambiguation": True,
            "multi_line_rows_preserved": True,
            "package_markers_not_rewritten_as_standard": True,
            "cross_attribute_evidence_not_silently_substituted": True,
            "configuration_states_not_projected_between_trims": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "candidate_count": 1,
            "decision_counts": {"covered": 1},
            "selected_evidence_signature_count": selected_signature_count,
            "selected_evidence_record_count": selected_record_count,
            "rejected_attached_signature_count": rejected_signature_count,
            "rejected_attached_record_count": rejected_record_count,
            "candidates_with_selected_evidence": 1,
            "candidates_without_selected_evidence": 0,
        },
        "decisions": decisions,
        "semantic_boundaries": {
            "review_is_not_import_approval": True,
            "bullet_option_and_dash_symbols_remain_distinct": True,
            "complete_row_trim_states_are_preserved": True,
            "plain_roof_rails_remain_distinct_from_modular_roof_rails": True,
            "adjacent_row_evidence_is_preserved_but_rejected": True,
            "essential_expression_and_extreme_states_are_not_projected": True,
            "no_configuration_projection_is_created": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": (
                "Review chunk 1 of the 40 unresolved technical candidates from Bigster brochure page 20 without "
                "creating master-data rows or approved import specifications."
            ),
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    decision = payload["decisions"][0]
    rejected = decision["rejected_attached_signatures"][0]
    rejected_signature = rejected["signature"]
    row_context = str(decision["row_context"]).replace("|", "\\|")
    rejection_reason = str(rejected["rejection_reason"]).replace("|", "\\|")
    lines = [
        "# Sandero Stepway Equipment Page 18 Ambiguity Review",
        "",
        "Authored review of `residual_gap_015`. The plain-roof-rail row is separated from the immediately following modular-roof-rail row; the review does not approve imports.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Reviewed candidates | {summary['candidate_count']} |",
        f"| Covered | {summary['decision_counts']['covered']} |",
        f"| Selected evidence signatures | {summary['selected_evidence_signature_count']} |",
        f"| Selected evidence records | {summary['selected_evidence_record_count']} |",
        f"| Rejected attached signatures | {summary['rejected_attached_signature_count']} |",
        f"| Rejected attached records | {summary['rejected_attached_record_count']} |",
        "",
        "## Candidate decisions",
        "",
        "| Line | Candidate | Decision | Selected signatures | Selected records | Row context |",
        "| ---: | --- | --- | ---: | ---: | --- |",
        (
            f"| {decision['line_start']} | `{decision['candidate_id']}` | `{decision['authored_decision']}` | "
            f"{decision['selected_evidence_signature_count']} | {decision['selected_evidence_record_count']} | "
            f"{row_context} |"
        ),
        "",
        "## Rejected attached evidence",
        "",
        "| Signature | Records | Rejection reason |",
        "| --- | ---: | --- |",
        (
            f"| `{rejected_signature['attribute_code']}:{rejected_signature['availability_status']}` | "
            f"{rejected['record_count']} | {rejection_reason} |"
        ),
        "",
        "The two rejected records remain embedded in the JSON report exactly as attached to the candidate.",
        "",
        "## Safety boundary",
        "",
        "- no file under `data/master` is changed;",
        "- no approved import specification is created or changed;",
        "- the candidate row remains Essential `•`, Expression `-`, Extreme `-`;",
        "- the adjacent modular-roof-rail row remains Essential `-`, Expression `•`, Extreme `•`;",
        "- `roof_rails` and `modular_roof_rails` remain distinct attributes;",
        "- the rejected modular signature and both of its records are preserved with an explicit rejection reason;",
        "- unavailable states are not inferred from missing configuration records;",
        "",
        "## Next package",
        "",
        f"**{payload['next_package']['name']}** — {payload['next_package']['goal']}",
        "",
    ]
    return "\n".join(lines)


def ensure_safe_output(repository: Path, path: Path) -> Path:
    resolved = (path if path.is_absolute() else repository / path).resolve()
    for restricted in (repository / "data/master", repository / "data/imports"):
        try:
            resolved.relative_to(restricted.resolve())
        except ValueError:
            continue
        raise SanderoStepwayEquipmentPage18ReviewError(f"output path is restricted: {path}")
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SanderoStepwayEquipmentPage18ReviewError(f"cannot read {label}: {exc}") from exc
    ensure(actual == expected, f"{label} differs from deterministic output")


def build_from_path(repository: Path, prioritization_path: Path) -> tuple[dict[str, Any], str]:
    resolved = prioritization_path if prioritization_path.is_absolute() else repository / prioritization_path
    payload = build_review(load_json_object(resolved, "residual-gap prioritization"), repository)
    return payload, render_markdown(payload)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--prioritization", type=Path, default=DEFAULT_PRIORITIZATION)
    result.add_argument("--json", type=Path, default=DEFAULT_JSON)
    result.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    result.add_argument("--verify", action="store_true")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    repository = repository_root()
    try:
        payload, markdown = build_from_path(repository, args.prioritization)
        json_path = ensure_safe_output(repository, args.json)
        markdown_path = ensure_safe_output(repository, args.markdown)
        expected_json = canonical_json(payload)
        if args.verify:
            verify_output(json_path, expected_json, "JSON report")
            verify_output(markdown_path, markdown, "Markdown report")
            print("Sandero Stepway equipment page-18 ambiguity review: PASS")
        else:
            write_atomic(json_path, expected_json)
            write_atomic(markdown_path, markdown)
            print(f"JSON report written to {json_path}")
            print(f"Markdown report written to {markdown_path}")
        print("Candidates reviewed: 1")
        print("Selected evidence signatures: 1")
        print("Selected evidence records: 1")
        print("Rejected attached signatures: 1")
        print("Rejected attached records: 2")
        return 0
    except SanderoStepwayEquipmentPage18ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
