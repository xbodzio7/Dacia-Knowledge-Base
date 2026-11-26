#!/usr/bin/env python3
"""Build or verify the authored Sandero brochure page-17 ambiguity review."""
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
REVIEW_KIND = "sandero_technical_page17_ambiguity_review"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path("data/reporting/verified_pdf_candidate_residual_gap_prioritization.json")
DEFAULT_JSON = Path("data/reporting/sandero_technical_page17_ambiguity_review.json")
DEFAULT_MARKDOWN = Path("data/reporting/sandero_technical_page17_ambiguity_review.md")
PACKAGE_ID = "residual_gap_004"
SOURCE_CODE = "src_pl_sandero_brochure_20260202"
SOURCE_PAGE = 17
SOURCE_PATH = Path("PDF/Broszury/DACIA SANDERO broszura 20260202.pdf")
SOURCE_SHA256 = "adee5017a405a22dffaca0555b47b84b718f2166534652c9863ba2f97f325f97"
NEXT_PACKAGE = "Sandero Stepway Technical Page 17 Ambiguity Review"
DECISION_STATUSES = {"covered_by_selected_evidence", "partially_covered"}


class SanderoPage17ReviewError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SanderoPage17ReviewError(message)


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
        raise SanderoPage17ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SanderoPage17ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise SanderoPage17ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()


def signature(attribute_code: str, value: str, fuel_type_code: str = "") -> dict[str, str]:
    return {"attribute_code": attribute_code, "value": value, "fuel_type_code": fuel_type_code, "gear_number": ""}


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
        "candidate_id": "af8a18cbf33fdcd88948e6aee518dafabcbd161530767a7dfe5af917885ca481",
        "line_start": 15,
        "exact_text": "Maks. moc w kW EWG (KM)",
        "decision": "partially_covered",
        "selected": [signature("engine_power", "90", "lpg"), signature("engine_power", "84", "petrol")],
        "rationale": "Both attached signatures match the LPG and petrol cells for the Eco-G 120 automatic column. The same values printed for the manual Eco-G column and the 74 kW TCe value have no attached records and are not inferred.",
        "source_facts": [fact("engine_power", ["74", "90", "84"], "The row also prints TCe 100 and manual Eco-G values, but the attached evidence covers only two automatic Eco-G configurations.")],
    },
    {
        "candidate_id": "515189b35b81d62360ad7b68509b7e48fe6d8607f89baa4cd10a4be0fc5478c3",
        "line_start": 19,
        "exact_text": "Maks. moment obrotowy w Nm",
        "decision": "partially_covered",
        "selected": [signature("engine_torque", "197", "lpg"), signature("engine_torque", "190", "petrol")],
        "rationale": "Both attached signatures match the LPG and petrol torque cells for the Eco-G 120 automatic column. TCe 100 and manual Eco-G cells remain source facts because no matching records are attached to this candidate.",
        "source_facts": [fact("engine_torque", ["200", "197", "190"], "The complete visual row contains TCe 100 and manual Eco-G values beyond the attached automatic-configuration evidence.")],
    },
    {
        "candidate_id": "9e24e542a7f69f9b3e053325bb9b606de1c0142e0bb19b3ba882cee4b3d196bf",
        "line_start": 82,
        "exact_text": "Maksymalna masa własna                      1132                        1209                               1232",
        "decision": "partially_covered",
        "selected": [signature("maximum_kerb_weight", "1209"), signature("maximum_kerb_weight", "1232")],
        "rationale": "The two attached masses match the manual and automatic Eco-G columns. The visible 1132 kg TCe value has no attached evidence and is not projected to any configuration.",
        "source_facts": [fact("maximum_kerb_weight", ["1132"], "The TCe column is visible in the source row but is outside the attached evidence set.")],
    },
    {
        "candidate_id": "8c95af2d22e4b73b8cce5e064156bcab2a61942c6164133eb0b6652e688d4c1e",
        "line_start": 84,
        "exact_text": "Dopuszczalna masa całkowita",
        "decision": "partially_covered",
        "selected": [signature("gross_vehicle_weight", "1665")],
        "rationale": "This first repeated label fragment begins the vehicle-GVW row and therefore selects only the attached 1665 kg gross-vehicle signature. The attached 2765 kg gross-train signature belongs to the following row and is rejected here.",
        "source_facts": [fact("gross_vehicle_weight", ["1570", "1640"], "The TCe and manual Eco-G vehicle-GVW values are visible but have no attached signatures for this candidate.")],
    },
    {
        "candidate_id": "7d03dc1a0f23d041d391cc4a2e7ff42ad1c1582209a5bc866a24fc6f5d554df2",
        "line_start": 87,
        "exact_text": "Dopuszczalna masa całkowita",
        "decision": "partially_covered",
        "selected": [signature("gross_train_weight", "2765")],
        "rationale": "This second repeated label fragment begins the gross-train row and therefore selects only the attached 2765 kg gross-train signature. The attached 1665 kg gross-vehicle signature belongs to the preceding row and is rejected here.",
        "source_facts": [fact("gross_train_weight", ["2550", "2740"], "The TCe and manual Eco-G gross-train values are visible but have no attached signatures for this candidate.")],
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
        raise SanderoPage17ReviewError(f"cannot read sources.csv: {exc}") from exc
    ensure(len(matches) == 1, "Sandero brochure source registry row differs")
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
    ensure(len(matches) == 1, "residual_gap_004 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "sandero_iii", "package model differs")
    ensure(package.get("domain") == "technical_tables", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "ambiguous", "package status differs")
    ensure(package.get("candidate_count") == 5, "package candidate count differs")
    ensure(package.get("evidence_signature_count") == 10, "package evidence signature count differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 5, "package candidates differ")
    return package


def verify_source(repository: Path) -> dict[str, Any]:
    row = read_source_row(repository)
    ensure(row.get("status") == "active", "Sandero brochure source is not active")
    ensure(row.get("source_type") == "brochure_pdf", "Sandero source type differs")
    ensure(row.get("document_date") == "2026-02-02", "Sandero source date differs")
    ensure(row.get("file_path") == SOURCE_PATH.as_posix(), "Sandero source path differs")
    ensure(row.get("sha256") == SOURCE_SHA256, "Sandero source registry hash differs")
    archived = repository / SOURCE_PATH
    ensure(archived.is_file(), "archived Sandero brochure is missing")
    ensure(sha256(archived) == SOURCE_SHA256, "archived Sandero brochure hash differs")
    return {
        "source_code": SOURCE_CODE,
        "file_path": SOURCE_PATH.as_posix(),
        "sha256": SOURCE_SHA256,
        "page": SOURCE_PAGE,
        "review_basis": "authored visual review of the archived page-17 technical table",
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
    ensure(counts == Counter({"partially_covered": 5}), "authored decision distribution differs")
    ensure(selected_count == 8 and selected_records == 16, "selected evidence totals differ")

    return {
        "version": REVIEW_VERSION,
        "kind": REVIEW_KIND,
        "reviewed_on": REVIEWED_ON,
        "status": "complete",
        "source_prioritization": DEFAULT_PRIORITIZATION.as_posix(),
        "package_id": PACKAGE_ID,
        "source_receipt": source_receipt,
        "scope": {"candidate_count": 5, "source_code": SOURCE_CODE, "model_code": "sandero_iii", "domain": "technical_tables", "page": SOURCE_PAGE, "input_coverage_status": "ambiguous"},
        "policy": {
            "candidate_id_and_exact_text_cited": True,
            "selected_evidence_copied_without_reinterpretation": True,
            "source_page_layout_used_for_row_disambiguation": True,
            "adjacent_candidate_evidence_not_silently_substituted": True,
            "cross_attribute_evidence_not_silently_substituted": True,
            "unattached_powertrain_values_not_inferred": True,
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
            "cross_attribute_evidence_remains_non_substitutable": True,
            "unattached_powertrain_values_remain_source_facts": True,
            "partial_coverage_does_not_authorize_missing_value_inference": True,
            "no_configuration_projection_is_created": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": "Review the 4 ambiguous technical candidates from the Sandero Stepway brochure page 17 against their 12 preserved evidence signatures without creating master-data rows or approved import specifications.",
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    counts = summary["decision_counts"]
    lines = [
        "# Sandero Technical Page 17 Ambiguity Review",
        "",
        "Authored review of `residual_gap_004`. Decisions preserve row, powertrain and candidate boundaries and do not approve imports.",
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
        "- values without attached evidence are retained only as source facts;",
        "- gross-vehicle and gross-train evidence is not exchanged between repeated label fragments;",
        "- selected automatic evidence is not projected onto manual or TCe configurations.",
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
        raise SanderoPage17ReviewError(f"output path is restricted: {path}")
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SanderoPage17ReviewError(f"cannot read {label}: {exc}") from exc
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
            verify_output(json_path, json_text, "Sandero page-17 review JSON")
            verify_output(markdown_path, markdown, "Sandero page-17 review Markdown")
            print("Sandero technical page-17 ambiguity review: PASS")
        else:
            write_atomic(json_path, json_text)
            write_atomic(markdown_path, markdown)
            print(f"JSON report written to {json_path}")
            print(f"Markdown report written to {markdown_path}")
        print(f"Candidates reviewed: {payload['summary']['candidate_count']}")
        print(f"Selected evidence signatures: {payload['summary']['selected_evidence_signature_count']}")
        print(f"Selected evidence records: {payload['summary']['selected_evidence_record_count']}")
        return 0
    except SanderoPage17ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
