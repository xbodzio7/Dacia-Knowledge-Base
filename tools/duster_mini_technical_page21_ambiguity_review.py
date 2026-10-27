#!/usr/bin/env python3
"""Build or verify the authored Duster mini-brochure page-21 ambiguity review."""
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
REVIEW_KIND = "duster_mini_technical_page21_ambiguity_review"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path("data/reporting/verified_pdf_candidate_residual_gap_prioritization.json")
DEFAULT_JSON = Path("data/reporting/duster_mini_technical_page21_ambiguity_review.json")
DEFAULT_MARKDOWN = Path("data/reporting/duster_mini_technical_page21_ambiguity_review.md")
PACKAGE_ID = "residual_gap_006"
SOURCE_CODE = "src_pl_duster_mini_brochure_20251020"
SOURCE_PAGE = 21
SOURCE_PATH = Path("PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf")
SOURCE_SHA256 = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
NEXT_PACKAGE = "Duster Mini Equipment Page 23 Ambiguity Review"
DECISION_STATUSES = {"partially_covered"}


class DusterMiniPage21ReviewError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise DusterMiniPage21ReviewError(message)


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
        raise DusterMiniPage21ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DusterMiniPage21ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DusterMiniPage21ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()


def signature(attribute_code: str, value: str, fuel_type_code: str = "") -> dict[str, str]:
    return {
        "attribute_code": attribute_code,
        "value": value,
        "fuel_type_code": fuel_type_code,
        "gear_number": "",
    }


def fact(attribute_code: str, values: Sequence[str], reason: str) -> dict[str, Any]:
    return {"attribute_code": attribute_code, "source_values": list(values), "reason": reason}


DECISIONS = (
    {
        "candidate_id": "6fd0360bfac47f6996e0fb04b3de4470e2edb507a12c70d96008d442a1489a6c",
        "line_start": 56,
        "exact_text": "Układ kierowniczy                                                    układu kierowniczego              układu kierowniczego",
        "decision": "partially_covered",
        "selected": [signature("steering_type", "Elektryczne wspomaganie układu kierowniczego")],
        "rationale": (
            "The candidate is the steering-type row. Only the attached electric-power-assistance signature belongs "
            "to this row. Turning-circle, brake, tyre, maximum-kerb-weight and payload signatures belong to other "
            "labelled rows on the same page and are rejected."
        ),
        "source_facts": [
            fact(
                "steering_type",
                ["Elektryczne wspomaganie układu kierowniczego"],
                "The same value is printed for Hybrid-G 150 4x4, but the selected records cover only Hybrid 155 configurations.",
            )
        ],
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
        raise DusterMiniPage21ReviewError(f"cannot read sources.csv: {exc}") from exc
    ensure(len(matches) == 1, "Duster mini-brochure source registry row differs")
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
    ensure(len(matches) == 1, "residual_gap_006 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "duster_iii", "package model differs")
    ensure(package.get("domain") == "technical_tables", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "ambiguous", "package status differs")
    ensure(package.get("candidate_count") == 1, "package candidate count differs")
    ensure(package.get("evidence_signature_count") == 7, "package evidence signature count differs")
    ensure(package.get("evidence_record_count") == 21, "package evidence record count differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 1, "package candidates differ")
    return package


def verify_source(repository: Path) -> dict[str, Any]:
    row = read_source_row(repository)
    ensure(row.get("status") == "active", "Duster mini-brochure source is not active")
    ensure(row.get("source_type") == "brochure_pdf", "Duster source type differs")
    ensure(row.get("document_date") == "2025-10-20", "Duster source date differs")
    ensure(row.get("file_path") == SOURCE_PATH.as_posix(), "Duster source path differs")
    ensure(row.get("sha256") == SOURCE_SHA256, "Duster source registry hash differs")
    archived = repository / SOURCE_PATH
    ensure(archived.is_file(), "archived Duster mini-brochure is missing")
    ensure(sha256(archived) == SOURCE_SHA256, "archived Duster mini-brochure hash differs")
    return {
        "source_code": SOURCE_CODE,
        "file_path": SOURCE_PATH.as_posix(),
        "sha256": SOURCE_SHA256,
        "page": SOURCE_PAGE,
        "review_basis": "authored visual review of the archived page-21 technical table",
    }


def selected_signatures(candidate: Mapping[str, Any], expected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
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
    result = []
    for wanted in expected:
        key = signature_key(wanted)
        ensure(key in by_key, f"selected signature is not attached to candidate: {key}")
        result.append(by_key[key])
    return result


def build_review(prioritization: Mapping[str, Any], repository: Path) -> dict[str, Any]:
    package = validate_prioritization(prioritization)
    source_receipt = verify_source(repository)
    candidate = package["candidates"][0]
    authored = DECISIONS[0]
    ensure(candidate.get("candidate_id") == authored["candidate_id"], "authored decision candidate differs")
    ensure(candidate.get("line_start") == authored["line_start"] == candidate.get("line_end"), "candidate line differs")
    ensure(candidate.get("exact_text") == authored["exact_text"], "candidate exact text differs")
    ensure(candidate.get("source_code") == SOURCE_CODE and candidate.get("page") == SOURCE_PAGE, "candidate source boundary differs")
    ensure(candidate.get("coverage_status") == "ambiguous", "candidate input status differs")
    decision = str(authored["decision"])
    ensure(decision in DECISION_STATUSES, f"unknown authored decision: {decision}")
    selected = selected_signatures(candidate, authored["selected"])
    selected_records = 0
    for item in selected:
        records = item.get("records")
        ensure(isinstance(records, list) and item.get("record_count") == len(records), "selected evidence record count differs")
        for record in records:
            ensure(record.get("source_code") == SOURCE_CODE and record.get("source_page") == SOURCE_PAGE, "selected evidence boundary differs")
        selected_records += len(records)
    ensure(len(selected) == 1 and selected_records == 3, "selected evidence totals differ")
    decisions = [{
        "candidate_id": authored["candidate_id"],
        "source_code": SOURCE_CODE,
        "page": SOURCE_PAGE,
        "line_start": authored["line_start"],
        "line_end": authored["line_start"],
        "exact_text": authored["exact_text"],
        "input_coverage_status": "ambiguous",
        "authored_decision": decision,
        "rationale": authored["rationale"],
        "selected_evidence_signature_count": len(selected),
        "selected_evidence_record_count": selected_records,
        "selected_evidence_signatures": selected,
        "source_facts": authored["source_facts"],
    }]
    counts = Counter(item["authored_decision"] for item in decisions)
    ensure(counts == Counter({"partially_covered": 1}), "authored decision distribution differs")
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
            "model_code": "duster_iii",
            "domain": "technical_tables",
            "page": SOURCE_PAGE,
            "input_coverage_status": "ambiguous",
        },
        "policy": {
            "candidate_id_and_exact_text_cited": True,
            "selected_evidence_copied_without_reinterpretation": True,
            "source_page_layout_used_for_row_disambiguation": True,
            "adjacent_row_evidence_not_silently_substituted": True,
            "cross_attribute_evidence_not_silently_substituted": True,
            "unattached_powertrain_values_not_inferred": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "candidate_count": 1,
            "decision_counts": {"partially_covered": 1},
            "selected_evidence_signature_count": 1,
            "selected_evidence_record_count": 3,
            "candidates_with_selected_evidence": 1,
            "candidates_without_selected_evidence": 0,
        },
        "decisions": decisions,
        "semantic_boundaries": {
            "review_is_not_import_approval": True,
            "turning_circle_is_a_distinct_row": True,
            "brake_tyre_mass_and_payload_evidence_remain_non_substitutable": True,
            "hybrid_g_steering_value_remains_a_source_fact_without_attached_records": True,
            "no_configuration_projection_is_created": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": "Review the 26 ambiguous equipment candidates from Duster mini-brochure page 23 against their 61 preserved evidence signatures without creating master-data rows or approved import specifications.",
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    item = payload["decisions"][0]
    exact = str(item["exact_text"]).replace("|", "\\|")
    lines = [
        "# Duster Mini Technical Page 21 Ambiguity Review",
        "",
        "Authored review of `residual_gap_006`. The decision preserves row and powertrain boundaries and does not approve imports.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Reviewed candidates | {summary['candidate_count']} |",
        f"| Partially covered | {summary['decision_counts']['partially_covered']} |",
        f"| Selected evidence signatures | {summary['selected_evidence_signature_count']} |",
        f"| Selected evidence records | {summary['selected_evidence_record_count']} |",
        "",
        "## Candidate decision",
        "",
        "| Line | Candidate | Decision | Selected signatures | Exact text |",
        "| ---: | --- | --- | ---: | --- |",
        f"| {item['line_start']} | `{item['candidate_id']}` | `{item['authored_decision']}` | {item['selected_evidence_signature_count']} | {exact} |",
        "",
        "## Authored finding",
        "",
        item["rationale"],
    ]
    for source_fact in item["source_facts"]:
        values = ", ".join(f"`{value}`" for value in source_fact["source_values"])
        lines.append(f"- `{source_fact['attribute_code']}`: {values} — {source_fact['reason']}")
    lines.extend([
        "",
        "## Safety boundary",
        "",
        "- no file under `data/master` is changed;",
        "- no approved import specification is created or changed;",
        "- the turning-circle value belongs to the following row and is not selected;",
        "- brake, tyre, mass and payload evidence is not substituted for the steering-type row;",
        "- the Hybrid-G 150 4x4 column is not populated from Hybrid 155 configuration records.",
        "",
        "## Next package",
        "",
        f"**{payload['next_package']['name']}** — {payload['next_package']['goal']}",
        "",
    ])
    return "\n".join(lines)


def ensure_safe_output(repository: Path, path: Path) -> Path:
    resolved = (path if path.is_absolute() else repository / path).resolve()
    for restricted in (repository / "data/master", repository / "data/imports"):
        try:
            resolved.relative_to(restricted.resolve())
        except ValueError:
            continue
        raise DusterMiniPage21ReviewError(f"output path is restricted: {path}")
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DusterMiniPage21ReviewError(f"cannot read {label}: {exc}") from exc
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
            print("Duster mini technical page-21 ambiguity review: PASS")
        else:
            write_atomic(json_path, expected_json)
            write_atomic(markdown_path, markdown)
            print(f"JSON report written to {json_path}")
            print(f"Markdown report written to {markdown_path}")
        print("Candidates reviewed: 1")
        print("Selected evidence signatures: 1")
        print("Selected evidence records: 3")
        return 0
    except DusterMiniPage21ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
