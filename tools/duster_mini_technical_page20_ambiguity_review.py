#!/usr/bin/env python3
"""Build or verify the authored Duster mini-brochure page-20 ambiguity review."""
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
REVIEW_KIND = "duster_mini_technical_page20_ambiguity_review"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path("data/reporting/verified_pdf_candidate_residual_gap_prioritization.json")
DEFAULT_JSON = Path("data/reporting/duster_mini_technical_page20_ambiguity_review.json")
DEFAULT_MARKDOWN = Path("data/reporting/duster_mini_technical_page20_ambiguity_review.md")
PACKAGE_ID = "residual_gap_003"
SOURCE_CODE = "src_pl_duster_mini_brochure_20251020"
SOURCE_PAGE = 20
SOURCE_PATH = Path("PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf")
SOURCE_SHA256 = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
NEXT_PACKAGE = "Sandero Technical Page 17 Ambiguity Review"
DECISION_STATUSES = {"covered_by_selected_evidence", "partially_covered"}


class DusterMiniPage20ReviewError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise DusterMiniPage20ReviewError(message)


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
        raise DusterMiniPage20ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DusterMiniPage20ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DusterMiniPage20ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()


def signature(attribute_code: str, value: str) -> dict[str, str]:
    return {"attribute_code": attribute_code, "value": value, "fuel_type_code": "", "gear_number": ""}


def range_signature(attribute_code: str, minimum: str, maximum: str) -> dict[str, str]:
    return {
        "attribute_code": attribute_code,
        "minimum_value": minimum,
        "maximum_value": maximum,
        "lower_inclusive": "true",
        "upper_inclusive": "true",
        "fuel_type_code": "",
    }


def fact(attribute_code: str, values: Sequence[str], reason: str) -> dict[str, Any]:
    return {"attribute_code": attribute_code, "source_values": list(values), "reason": reason}


DECISIONS = (
    {
        "candidate_id": "ec2ff275fa561863a5da266d3c552ab95d5de4c4a1efe2135e7597da30ad6e77",
        "line_start": 52,
        "exact_text": "Układ kierowniczy                                                    układu kierowniczego            układu kierowniczego",
        "decision": "covered_by_selected_evidence",
        "selected": [signature("steering_type", "Elektryczne wspomaganie układu kierowniczego")],
        "rationale": "The visual row is the steering-type row. Brake, tyre, mass, payload and turning-circle signatures are adjacent-row matches and are not selected.",
        "source_facts": [],
    },
    {
        "candidate_id": "6da4e74ede4d02c9cce0f2b899db297ed61cb74316ed00120126a034ff584153",
        "line_start": 87,
        "exact_text": "Maks. masa całkowita samochodu gotowego",
        "decision": "covered_by_selected_evidence",
        "selected": [signature("maximum_kerb_weight", "1350"), signature("maximum_kerb_weight", "1376")],
        "rationale": "The split label continues with the Eco-G 120 and mild hybrid 140 maximum ready-to-drive masses shown on the same row.",
        "source_facts": [],
    },
    {
        "candidate_id": "3acabcb9d6f1db21630d6a687ae88008952748f44e44a04ca244dcfc3f863932",
        "line_start": 95,
        "exact_text": "Maks./min. ładowność(5)                                                     455/487                          454/528",
        "decision": "covered_by_selected_evidence",
        "selected": [range_signature("payload", "455", "487"), range_signature("payload", "454", "528")],
        "rationale": "Both attached closed payload intervals match the two visible powertrain columns. Source order and the printed Maks./min. wording are preserved without relabelling endpoints.",
        "source_facts": [],
    },
    {
        "candidate_id": "86fc1329b953a27106b7ebae34c739fcb87fed2dad8dd02225966be30bda9e26",
        "line_start": 103,
        "exact_text": "(dm3 VDA)",
        "decision": "partially_covered",
        "selected": [signature("boot_capacity", "453"), signature("boot_capacity", "517"), signature("boot_capacity", "474")],
        "rationale": "The unit fragment completes the upright VDA cargo row. Only 453, 517 and 474 are visible in the page-20 row; folded-row and page-21 Hybrid 155 signatures are not substituted.",
        "source_facts": [
            fact("boot_capacity", ["430", "349", "1415"], "Hybrid 155 values belong to the following source page and are excluded from this page-20 candidate."),
            fact("boot_capacity", ["1545", "1609", "1566"], "These attached values belong to the following folded-seat VDA row, not the upright row completed by this fragment."),
        ],
    },
    {
        "candidate_id": "814fd871b681107ac44c91516f42db45b174611169bf385c3d928480125dcfbb",
        "line_start": 106,
        "exact_text": "zapasowym(6), (7) (dm3 VDA)",
        "decision": "partially_covered",
        "selected": [signature("boot_capacity", "1566")],
        "rationale": "The fragment belongs to the folded-seat VDA row and the attached 1566 dm3 spare-wheel value is selected. Repair-kit values are visible but are not attached to this candidate, while Hybrid 155 values belong to page 21.",
        "source_facts": [fact("boot_capacity", ["1545", "1609"], "Visible repair-kit folded-seat values remain source facts because their signatures are attached to the adjacent line-103 candidate.")],
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
        raise DusterMiniPage20ReviewError(f"cannot read sources.csv: {exc}") from exc
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
    matches = [p for p in packages if isinstance(p, Mapping) and p.get("package_id") == PACKAGE_ID]
    ensure(len(matches) == 1, "residual_gap_003 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "duster_iii", "package model differs")
    ensure(package.get("domain") == "technical_tables", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "ambiguous", "package status differs")
    ensure(package.get("candidate_count") == 5, "package candidate count differs")
    ensure(package.get("evidence_signature_count") == 26, "package evidence signature count differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 5, "package candidates differ")
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
        "review_basis": "authored visual review of the archived page-20 technical table",
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
    candidates = package["candidates"]
    candidate_by_id = {str(c.get("candidate_id")): c for c in candidates if isinstance(c, Mapping)}
    ensure(len(candidate_by_id) == 5, "package candidate IDs are not unique")
    manifest_ids = [d["candidate_id"] for d in DECISIONS]
    ensure(len(manifest_ids) == len(set(manifest_ids)) == 5, "authored decision candidate IDs differ")
    ensure(set(manifest_ids) == set(candidate_by_id), "authored decision partition differs")

    decisions = []
    counts: Counter[str] = Counter()
    selected_count = 0
    selected_records = 0
    for authored in DECISIONS:
        candidate = candidate_by_id[authored["candidate_id"]]
        ensure(candidate.get("line_start") == authored["line_start"] and candidate.get("line_end") == authored["line_start"], f"candidate line differs: {authored['candidate_id']}")
        ensure(candidate.get("exact_text") == authored["exact_text"], f"candidate exact text differs: {authored['candidate_id']}")
        ensure(candidate.get("source_code") == SOURCE_CODE and candidate.get("page") == SOURCE_PAGE, "candidate source boundary differs")
        ensure(candidate.get("coverage_status") == "ambiguous", "candidate input status differs")
        decision = str(authored["decision"])
        ensure(decision in DECISION_STATUSES, f"unknown authored decision: {decision}")
        selected = selected_signatures(candidate, authored["selected"])
        for item in selected:
            records = item.get("records")
            ensure(isinstance(records, list) and item.get("record_count") == len(records), "selected evidence record count differs")
            for record in records:
                ensure(record.get("source_code") == SOURCE_CODE and record.get("source_page") == SOURCE_PAGE, "selected evidence boundary differs")
            selected_records += len(records)
        selected_count += len(selected)
        counts[decision] += 1
        decisions.append({
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
            "selected_evidence_record_count": sum(int(x["record_count"]) for x in selected),
            "selected_evidence_signatures": selected,
            "source_facts": authored["source_facts"],
        })
    ensure(counts == Counter({"covered_by_selected_evidence": 3, "partially_covered": 2}), "authored decision distribution differs")
    ensure(selected_count == 9 and selected_records == 34, "selected evidence totals differ")

    return {
        "version": REVIEW_VERSION,
        "kind": REVIEW_KIND,
        "reviewed_on": REVIEWED_ON,
        "status": "complete",
        "source_prioritization": DEFAULT_PRIORITIZATION.as_posix(),
        "package_id": PACKAGE_ID,
        "source_receipt": source_receipt,
        "scope": {"candidate_count": 5, "source_code": SOURCE_CODE, "model_code": "duster_iii", "domain": "technical_tables", "page": SOURCE_PAGE, "input_coverage_status": "ambiguous"},
        "policy": {
            "candidate_id_and_exact_text_cited": True,
            "selected_evidence_copied_without_reinterpretation": True,
            "source_page_layout_used_for_row_disambiguation": True,
            "adjacent_candidate_evidence_not_silently_substituted": True,
            "following_page_evidence_not_silently_substituted": True,
            "payload_source_order_preserved_without_endpoint_relabelling": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "candidate_count": 5,
            "decision_counts": {status: counts.get(status, 0) for status in sorted(DECISION_STATUSES)},
            "selected_evidence_signature_count": selected_count,
            "selected_evidence_record_count": selected_records,
            "candidates_with_selected_evidence": sum(item["selected_evidence_signature_count"] > 0 for item in decisions),
            "candidates_without_selected_evidence": sum(item["selected_evidence_signature_count"] == 0 for item in decisions),
        },
        "decisions": decisions,
        "semantic_boundaries": {
            "review_is_not_import_approval": True,
            "following_page_hybrid_values_remain_non_substitutable": True,
            "adjacent_candidate_evidence_remains_non_substitutable": True,
            "partial_coverage_does_not_authorize_missing_value_inference": True,
            "no_configuration_projection_is_created": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": "Review the 5 ambiguous technical candidates from the Sandero brochure page 17 against their 10 preserved evidence signatures without creating master-data rows or approved import specifications.",
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    counts = summary["decision_counts"]
    lines = [
        "# Duster Mini Technical Page 20 Ambiguity Review",
        "",
        "Authored review of `residual_gap_003`. Decisions preserve page and candidate boundaries and do not approve imports.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Reviewed candidates | {summary['candidate_count']} |",
        f"| Covered by selected evidence | {counts['covered_by_selected_evidence']} |",
        f"| Partially covered | {counts['partially_covered']} |",
        f"| Selected evidence signatures | {summary['selected_evidence_signature_count']} |",
        f"| Selected evidence records | {summary['selected_evidence_record_count']} |",
        "",
        "## Candidate decisions",
        "",
        "| Line | Candidate | Decision | Selected signatures | Exact text |",
        "| ---: | --- | --- | ---: | --- |",
    ]
    for item in payload["decisions"]:
        exact = str(item["exact_text"]).replace("|", "\\|")
        lines.append(f"| {item['line_start']} | `{item['candidate_id']}` | `{item['authored_decision']}` | {item['selected_evidence_signature_count']} | {exact} |")
    lines.extend(["", "## Partial findings", ""])
    for item in payload["decisions"]:
        if item["authored_decision"] != "partially_covered":
            continue
        lines.extend([f"### Line {item['line_start']} — `{item['candidate_id']}`", "", item["rationale"]])
        for source_fact in item["source_facts"]:
            values = ", ".join(f"`{value}`" for value in source_fact["source_values"])
            lines.append(f"- `{source_fact['attribute_code']}`: {values} — {source_fact['reason']}")
        lines.append("")
    lines.extend([
        "## Safety boundary",
        "",
        "- no file under `data/master` is changed;",
        "- no approved import specification is created or changed;",
        "- page-21 Hybrid 155 values are not substituted into page 20;",
        "- signatures attached to an adjacent candidate are not silently reassigned;",
        "- payload source order is preserved without relabelling the numeric interval endpoints.",
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
        raise DusterMiniPage20ReviewError(f"output path is restricted: {path}")
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DusterMiniPage20ReviewError(f"cannot read {label}: {exc}") from exc
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
    arguments = parser().parse_args(argv)
    repository = repository_root()
    try:
        payload, markdown = build_from_path(repository, arguments.prioritization)
        json_path = ensure_safe_output(repository, arguments.json)
        markdown_path = ensure_safe_output(repository, arguments.markdown)
        json_text = canonical_json(payload)
        if arguments.verify:
            verify_output(json_path, json_text, "Duster mini page-20 review JSON")
            verify_output(markdown_path, markdown, "Duster mini page-20 review Markdown")
            print("Duster mini technical page-20 ambiguity review: PASS")
        else:
            write_atomic(json_path, json_text)
            write_atomic(markdown_path, markdown)
            print(f"JSON report written to {json_path}")
            print(f"Markdown report written to {markdown_path}")
        print(f"Candidates reviewed: {payload['summary']['candidate_count']}")
        print(f"Selected evidence signatures: {payload['summary']['selected_evidence_signature_count']}")
        print(f"Selected evidence records: {payload['summary']['selected_evidence_record_count']}")
        return 0
    except DusterMiniPage20ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
