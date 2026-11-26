#!/usr/bin/env python3
"""Build or verify the authored Duster mini-brochure page-22 equipment ambiguity review."""
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
REVIEW_KIND = "duster_mini_equipment_page22_ambiguity_review"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path("data/reporting/verified_pdf_candidate_residual_gap_prioritization.json")
DEFAULT_JSON = Path("data/reporting/duster_mini_equipment_page22_ambiguity_review.json")
DEFAULT_MARKDOWN = Path("data/reporting/duster_mini_equipment_page22_ambiguity_review.md")
PACKAGE_ID = "residual_gap_008"
SOURCE_CODE = "src_pl_duster_mini_brochure_20251020"
SOURCE_PAGE = 22
SOURCE_PATH = Path("PDF/Broszury/DACIA DUSTER mini broszura 20251020.pdf")
SOURCE_SHA256 = "84040b64bd67391cce4a99ada3021b0ad1a493f9430a666783e4632dd6ce85e8"
NEXT_PACKAGE = "Bigster Equipment Page 22 Ambiguity Review"
DECISION_STATUSES = {"covered", "partially_covered"}
TRIMS = ("essential", "expression", "journey", "extreme")

class DusterMiniEquipmentPage22ReviewError(RuntimeError):
    pass

def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]

def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise DusterMiniEquipmentPage22ReviewError(message)

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
        raise DusterMiniEquipmentPage22ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DusterMiniEquipmentPage22ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DusterMiniEquipmentPage22ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()

def availability_signature(attribute_code: str, availability_status: str) -> dict[str, str]:
    return {"attribute_code": attribute_code, "availability_status": availability_status}

DECISIONS = ({'candidate_id': 'd2cd87ae3c3eca07f3fe8d82719a57c12be9fa806e8f50b17630197a2181524e',
  'line_start': 15,
  'line_end': 15,
  'exact_text': 'Automatycznie włączane światła',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'automatic_headlights', 'availability_status': 'standard'}],
  'row_context': 'first line of the automatic dipped-headlights row',
  'source_availability': {'essential': 'standard',
                          'expression': 'standard',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This candidate is the first line of the automatic dipped-headlights row. Only '
               'automatic_headlights:standard belongs to the row. Rain-sensing-wiper signatures describe a separate '
               'function and are rejected.'},
 {'candidate_id': '3bc148f177d5790ba3cbca9a714aad74af045db4527e846796f014f9f0fa6811',
  'line_start': 117,
  'line_end': 117,
  'exact_text': 'System kontroli toru jazdy (ESC)(1) +',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'electronic_stability_control', 'availability_status': 'standard'},
               {'attribute_code': 'hill_start_assist', 'availability_status': 'standard'}],
  'row_context': 'first line of the combined ESC and hill-start-assist row',
  'source_availability': {'essential': 'standard',
                          'expression': 'standard',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This first fragment starts the combined ESC plus HSA row. Both standard signatures are retained at the '
               'visual-row boundary; neither attribute is projected outside that row.'},
 {'candidate_id': 'e504a831e8ebda129fbcbaa2a27bd82a916fd1c8f27a5f777ed19063b90d0a4c',
  'line_start': 118,
  'line_end': 118,
  'exact_text': 'system wspomagania ruszania pod górę                       •                   •                  '
                '•                   •',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'electronic_stability_control', 'availability_status': 'standard'},
               {'attribute_code': 'hill_start_assist', 'availability_status': 'standard'}],
  'row_context': 'availability-bearing middle line of the combined ESC and hill-start-assist row',
  'source_availability': {'essential': 'standard',
                          'expression': 'standard',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This availability-bearing fragment completes the ESC plus HSA label. Both standard signatures belong '
               'to the same visual row and are retained without merging their attribute identities.'},
 {'candidate_id': '8f90c98b7a9e1b6c384b2f156b2e5035648a177a0417e41aec1498b1f012885c',
  'line_start': 120,
  'line_end': 120,
  'exact_text': 'Przednie i tylne pasy bezpieczeństwa',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'driver_seat_belt_height_adjustment', 'availability_status': 'not_available'},
               {'attribute_code': 'front_seat_belt_pretensioners', 'availability_status': 'standard'},
               {'attribute_code': 'rear_seat_belt_pretensioners', 'availability_status': 'standard'}],
  'row_context': 'first line of the front/rear pretensioner row without height adjustment',
  'source_availability': {'essential': 'standard pretensioners; height adjustment not available',
                          'expression': 'standard pretensioners; height adjustment not available',
                          'journey': 'standard pretensioners; height adjustment not available',
                          'extreme': 'standard pretensioners; height adjustment not available'},
  'rationale': 'The three-line row states front and rear pyrotechnic pretensioners and no height adjustment. All three '
               'attached signatures are retained as separate facts within the same visual row.'},
 {'candidate_id': 'e5957ec575751dfcf18e5a9e21f5e26a0112aa75a4483467f7bbedf0c5da15e4',
  'line_start': 121,
  'line_end': 121,
  'exact_text': 'z napinaczami pirotechnicznymi bez                         •                   •                  '
                '•                   •',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'driver_seat_belt_height_adjustment', 'availability_status': 'not_available'},
               {'attribute_code': 'front_seat_belt_pretensioners', 'availability_status': 'standard'},
               {'attribute_code': 'rear_seat_belt_pretensioners', 'availability_status': 'standard'}],
  'row_context': 'availability-bearing middle line of the front/rear pretensioner row without height adjustment',
  'source_availability': {'essential': 'standard pretensioners; height adjustment not available',
                          'expression': 'standard pretensioners; height adjustment not available',
                          'journey': 'standard pretensioners; height adjustment not available',
                          'extreme': 'standard pretensioners; height adjustment not available'},
  'rationale': 'This fragment carries the four standard markers and begins the no-height-adjustment clause. Front and '
               'rear pretensioners remain standard while height adjustment remains unavailable.'},
 {'candidate_id': '4bafe8134f33bfb85a91020706ddcfd101195d36c14e6101f8d1c140defd073c',
  'line_start': 122,
  'line_end': 122,
  'exact_text': 'regulacji wysokości',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'driver_seat_belt_height_adjustment', 'availability_status': 'not_available'},
               {'attribute_code': 'front_seat_belt_pretensioners', 'availability_status': 'standard'},
               {'attribute_code': 'rear_seat_belt_pretensioners', 'availability_status': 'standard'}],
  'row_context': 'final line of the front/rear pretensioner row without height adjustment',
  'source_availability': {'essential': 'standard pretensioners; height adjustment not available',
                          'expression': 'standard pretensioners; height adjustment not available',
                          'journey': 'standard pretensioners; height adjustment not available',
                          'extreme': 'standard pretensioners; height adjustment not available'},
  'rationale': 'The final fragment closes the no-height-adjustment clause of the same pretensioner row. The three '
               'signatures remain separate and source-bounded.'},
 {'candidate_id': '5962f79da4da74d4680112782476829ed627ddd91cca737527725f094aef95fa',
  'line_start': 153,
  'line_end': 153,
  'exact_text': 'wyświetlacz zespołu wskaźników                             -                   •                  '
                '•                   •',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'instrument_cluster_colour_7', 'availability_status': 'not_available'},
               {'attribute_code': 'instrument_cluster_colour_7', 'availability_status': 'standard'}],
  'row_context': 'middle line of the 7-inch digital instrument-cluster row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'standard',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This fragment belongs to the 7-inch digital colour instrument-cluster row. Essential remains '
               'unavailable and the other trims remain standard; the analog cluster is a separate row.'},
 {'candidate_id': 'e8e19aa4e1de55306aff83b6261e273c67386748f1c8a0c37aa0534783f09734',
  'line_start': 164,
  'line_end': 164,
  'exact_text': 'Ogranicznik / Regulator prędkości                         •/•                 •/•                '
                '•/•                 •/•',
  'decision': 'covered',
  'selected': [{'attribute_code': 'cruise_control', 'availability_status': 'standard'},
               {'attribute_code': 'speed_limiter', 'availability_status': 'standard'}],
  'row_context': 'complete speed-limiter and cruise-control row',
  'source_availability': {'essential': 'standard',
                          'expression': 'standard',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This complete row prints both limiter and cruise-control markers for every trim. Both standard '
               'signatures are retained as distinct attributes.'},
 {'candidate_id': 'e8e92c334cfdb2f2476fc2ad204eb75925f5235325abcf7edd4762c868858980',
  'line_start': 170,
  'line_end': 170,
  'exact_text': 'Czujniki parkowania z tyłu                                 •                   •                  '
                '•                   •',
  'decision': 'covered',
  'selected': [{'attribute_code': 'rear_parking_sensors', 'availability_status': 'standard'}],
  'row_context': 'complete rear-parking-sensor row',
  'source_availability': {'essential': 'standard',
                          'expression': 'standard',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This complete row is limited to rear parking sensors in all trims. The attached front-parking-sensor '
               'record is a different row and is rejected.'},
 {'candidate_id': '25175fba71d23d4587ebeb4365f188e9ec7e0ba7ed1cd1d818962e42350713f6',
  'line_start': 173,
  'line_end': 173,
  'exact_text': 'Czujniki parkowania z przodu i z boku                      -                   -',
  'decision': 'partially_covered',
  'selected': [{'attribute_code': 'front_parking_sensors', 'availability_status': 'not_available'},
               {'attribute_code': 'front_parking_sensors', 'availability_status': 'optional'}],
  'row_context': 'front-and-side parking-sensor row with option markers split across adjacent lines',
  'source_availability': {'essential': 'not_available',
                          'expression': 'not_available',
                          'journey': 'optional_package',
                          'extreme': 'optional_package'},
  'rationale': 'The row prints dashes for Essential and Expression and option/package markers for Journey and Extreme. '
               'Standard front-sensor evidence from later configurations is rejected, and no missing side-sensor '
               'attribute is invented.'},
 {'candidate_id': '01325df6ea284632046d8257e9f1994fd542d4626c697d47d962916a74a78968',
  'line_start': 176,
  'line_end': 176,
  'exact_text': 'Kamera cofania                                             -                   •                  '
                '•                   •',
  'decision': 'covered',
  'selected': [{'attribute_code': 'rear_view_camera', 'availability_status': 'not_available'},
               {'attribute_code': 'rear_view_camera', 'availability_status': 'standard'}],
  'row_context': 'complete rear-view-camera row',
  'source_availability': {'essential': 'not_available',
                          'expression': 'standard',
                          'journey': 'standard',
                          'extreme': 'standard'},
  'rationale': 'This complete row preserves the unavailable Essential state and standard Expression, Journey and '
               'Extreme states for the rear-view camera.'})

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
        raise DusterMiniEquipmentPage22ReviewError(f"cannot read sources.csv: {exc}") from exc
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
    ensure(len(matches) == 1, "residual_gap_008 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "duster_iii", "package model differs")
    ensure(package.get("domain") == "equipment_matrix", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "ambiguous", "package status differs")
    ensure(package.get("candidate_count") == 11, "package candidate count differs")
    ensure(package.get("evidence_signature_count") == 27, "package evidence signature count differs")
    ensure(package.get("evidence_record_count") == 551, "package evidence record count differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 11, "package candidates differ")
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
    return {"source_code": SOURCE_CODE, "file_path": SOURCE_PATH.as_posix(), "sha256": SOURCE_SHA256, "page": SOURCE_PAGE,
            "review_basis": "authored visual review of the archived page-22 equipment matrix"}

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
    ensure(len(DECISIONS) == len(candidates), "authored decision count differs")
    by_id = {str(item["candidate_id"]): item for item in candidates}
    ensure(len(by_id) == len(candidates), "candidate IDs are not unique")
    decisions = []
    for authored in DECISIONS:
        candidate = by_id.get(str(authored["candidate_id"]))
        ensure(candidate is not None, "authored decision candidate is missing")
        ensure(candidate.get("line_start") == authored["line_start"] and candidate.get("line_end") == authored["line_end"], "candidate line differs")
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
                ensure(record.get("table") == "configuration_attribute_availability", "selected evidence table differs")
                ensure(str(record.get("configuration_code", "")).startswith("duster_iii_"), "selected evidence model boundary differs")
            selected_records += len(records)
        visual = authored["source_availability"]
        ensure(tuple(visual) == TRIMS, "source availability trim keys differ")
        decisions.append({
            "candidate_id": authored["candidate_id"], "source_code": SOURCE_CODE, "page": SOURCE_PAGE,
            "line_start": authored["line_start"], "line_end": authored["line_end"], "exact_text": authored["exact_text"],
            "input_coverage_status": "ambiguous", "authored_decision": decision, "row_context": authored["row_context"],
            "source_availability": visual, "rationale": authored["rationale"],
            "selected_evidence_signature_count": len(selected), "selected_evidence_record_count": selected_records,
            "selected_evidence_signatures": selected,
            "rejected_attached_signature_count": len(candidate["evidence_signatures"]) - len(selected),
        })
    decision_ids = [item["candidate_id"] for item in decisions]
    ensure(len(decision_ids) == len(set(decision_ids)) == 11, "authored candidate assignment differs")
    counts = Counter(item["authored_decision"] for item in decisions)
    ensure(counts == Counter({"partially_covered": 8, "covered": 3}), "authored decision distribution differs")
    selected_signature_count = sum(item["selected_evidence_signature_count"] for item in decisions)
    selected_record_count = sum(item["selected_evidence_record_count"] for item in decisions)
    ensure((selected_signature_count, selected_record_count) == (23, 524), "selected evidence totals differ")
    return {
        "version": REVIEW_VERSION, "kind": REVIEW_KIND, "reviewed_on": REVIEWED_ON, "status": "complete",
        "source_prioritization": DEFAULT_PRIORITIZATION.as_posix(), "package_id": PACKAGE_ID, "source_receipt": source_receipt,
        "scope": {"candidate_count": 11, "source_code": SOURCE_CODE, "model_code": "duster_iii", "domain": "equipment_matrix", "page": SOURCE_PAGE, "input_coverage_status": "ambiguous"},
        "policy": {"candidate_id_and_exact_text_cited": True, "selected_evidence_copied_without_reinterpretation": True,
                   "source_page_layout_used_for_row_disambiguation": True, "multi_line_rows_preserved": True,
                   "package_markers_not_rewritten_as_standard": True, "cross_attribute_evidence_not_silently_substituted": True,
                   "configuration_states_not_projected_between_trims": True, "master_data_changes": False,
                   "approved_import_spec_generation": False, "automatic_promotion": False},
        "summary": {"candidate_count": 11, "decision_counts": {"covered": 3, "partially_covered": 8},
                    "selected_evidence_signature_count": selected_signature_count, "selected_evidence_record_count": selected_record_count,
                    "rejected_attached_signature_count": 27-selected_signature_count, "rejected_attached_record_count": 551-selected_record_count,
                    "candidates_with_selected_evidence": 11, "candidates_without_selected_evidence": 0},
        "decisions": decisions,
        "semantic_boundaries": {"review_is_not_import_approval": True, "bullet_option_and_dash_symbols_remain_distinct": True,
                                 "multi_line_rows_are_reviewed_as_visual_units": True, "automatic_headlights_remain_distinct_from_rain_sensing_wipers": True,
                                 "esc_and_hill_start_assist_remain_distinct_attributes": True, "seat_belt_pretensioners_and_height_adjustment_remain_distinct": True,
                                 "rear_parking_sensors_remain_distinct_from_front_and_side_sensors": True, "optional_parking_evidence_is_not_rewritten_as_standard": True,
                                 "no_configuration_projection_is_created": True},
        "next_package": {"name": NEXT_PACKAGE, "status": "planned",
                         "goal": "Review the 7 ambiguous equipment candidates from Bigster brochure page 22 against their 18 preserved evidence signatures without creating master-data rows or approved import specifications."},
    }

def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    lines = ["# Duster Mini Equipment Page 22 Ambiguity Review", "",
             "Authored review of `residual_gap_008`. Multi-line safety and control rows, trim columns and option markers are preserved; the review does not approve imports.", "",
             "## Summary", "", "| Measure | Value |", "| --- | ---: |",
             f"| Reviewed candidates | {summary['candidate_count']} |", f"| Covered | {summary['decision_counts']['covered']} |",
             f"| Partially covered | {summary['decision_counts']['partially_covered']} |",
             f"| Selected evidence signatures | {summary['selected_evidence_signature_count']} |",
             f"| Selected evidence records | {summary['selected_evidence_record_count']} |",
             f"| Rejected attached signatures | {summary['rejected_attached_signature_count']} |",
             "", "## Candidate decisions", "", "| Line | Candidate | Decision | Signatures | Records | Row context |", "| ---: | --- | --- | ---: | ---: | --- |"]
    for item in payload["decisions"]:
        context = str(item["row_context"]).replace("|", "\\|")
        lines.append(f"| {item['line_start']} | `{item['candidate_id']}` | `{item['authored_decision']}` | {item['selected_evidence_signature_count']} | {item['selected_evidence_record_count']} | {context} |")
    lines.extend(["", "## Safety boundary", "", "- no file under `data/master` is changed;", "- no approved import specification is created or changed;",
                  "- `•`, `¤` and `-` remain standard, optional and unavailable respectively;", "- multi-line labels are reviewed as one visual row without inventing new attributes;",
                  "- option and package markers do not inherit standard status from later configuration records;", "- rain-sensor, front-sensor and other adjacent-attribute evidence is rejected rather than substituted;",
                  "", "## Next package", "", f"**{payload['next_package']['name']}** — {payload['next_package']['goal']}", ""])
    return "\n".join(lines)

def ensure_safe_output(repository: Path, path: Path) -> Path:
    resolved = (path if path.is_absolute() else repository / path).resolve()
    for restricted in (repository / "data/master", repository / "data/imports"):
        try:
            resolved.relative_to(restricted.resolve())
        except ValueError:
            continue
        raise DusterMiniEquipmentPage22ReviewError(f"output path is restricted: {path}")
    return resolved

def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DusterMiniEquipmentPage22ReviewError(f"cannot read {label}: {exc}") from exc
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
            print("Duster mini equipment page-22 ambiguity review: PASS")
        else:
            write_atomic(json_path, expected_json)
            write_atomic(markdown_path, markdown)
            print(f"JSON report written to {json_path}")
            print(f"Markdown report written to {markdown_path}")
        print("Candidates reviewed: 11")
        print("Selected evidence signatures: 23")
        print("Selected evidence records: 524")
        return 0
    except DusterMiniEquipmentPage22ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
