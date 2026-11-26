#!/usr/bin/env python3
"""Build or verify the authored Bigster page-20 ambiguity review."""

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
REVIEW_KIND = "bigster_technical_page20_ambiguity_review"
REVIEWED_ON = "2026-07-28"
DEFAULT_PRIORITIZATION = Path(
    "data/reporting/verified_pdf_candidate_residual_gap_prioritization.json"
)
DEFAULT_JSON = Path(
    "data/reporting/bigster_technical_page20_ambiguity_review.json"
)
DEFAULT_MARKDOWN = Path(
    "data/reporting/bigster_technical_page20_ambiguity_review.md"
)
PACKAGE_ID = "residual_gap_001"
SOURCE_CODE = "src_pl_bigster_brochure_20251210"
SOURCE_PAGE = 20
SOURCE_PATH = Path("PDF/Broszury/DACIA BIGSTER broszura 20251210.pdf")
SOURCE_SHA256 = "76795d4ea524172a324fd44b6a630ffbb14be9d151df8c95de79a8dd4e6aed74"
NEXT_PACKAGE = "Jogger Technical Page 19 Ambiguity Review"
DECISION_STATUSES = {
    "covered_by_selected_evidence",
    "partially_covered",
    "context_only_non_import",
    "deferred_source_conflict",
    "unresolved_signature_mismatch",
}


class BigsterPage20ReviewError(RuntimeError):
    """Controlled authored-review failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise BigsterPage20ReviewError(message)


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
        raise BigsterPage20ReviewError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise BigsterPage20ReviewError(f"invalid JSON in {label}: {exc}") from exc
    ensure(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise BigsterPage20ReviewError(f"cannot read archived source: {exc}") from exc
    return digest.hexdigest()


def read_source_row(repository: Path) -> dict[str, str]:
    path = repository / "data/master/sources.csv"
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            ensure(reader.fieldnames is not None, "sources.csv has no header")
            matches = [dict(row) for row in reader if row.get("code") == SOURCE_CODE]
    except OSError as exc:
        raise BigsterPage20ReviewError(f"cannot read sources.csv: {exc}") from exc
    ensure(len(matches) == 1, "Bigster brochure source registry row differs")
    return matches[0]


def signature(attribute_code: str, value: str) -> dict[str, str]:
    return {
        "attribute_code": attribute_code,
        "value": value,
        "fuel_type_code": "",
        "gear_number": "",
    }


def fact(attribute_code: str, values: Sequence[str], reason: str) -> dict[str, Any]:
    return {
        "attribute_code": attribute_code,
        "source_values": list(values),
        "reason": reason,
    }


DECISIONS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "ff2cfb88e41d2640552d70cb85f81f9c6e28f6e02e0965457afdb1eba5a53397",
        "line_start": 63,
        "exact_text": "Układ kierowniczy                                                   Ze wspomaganiem elektrycznym",
        "decision": "covered_by_selected_evidence",
        "selected": [signature("steering_type", "Ze wspomaganiem elektrycznym")],
        "rationale": "The row states electric power assistance; the turning-circle and unrelated chassis signatures belong to neighbouring rows.",
        "source_facts": [],
    },
    {
        "candidate_id": "86e33e875ec789d2158604e3d0d69634b0a600856d47ca16c21be4cfeb2081cc",
        "line_start": 77,
        "exact_text": "tarcza pełna:                                                                                                      (hamulec postojowy",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("rear_brake_type", "Bęben 9” (hamulec postojowy manualny) / tarcza pełna Φ280x9,6 (hamulec postojowy automatyczny)"),
            signature("rear_brake_type", "Tarcza pełna Ø280x9,6"),
        ],
        "rationale": "The line is a split fragment of the two rear-brake specifications shown across the four powertrain columns.",
        "source_facts": [],
    },
    {
        "candidate_id": "6b16b6b892640e914634c512e720f777a5c3f4933edc34b3a8b5e308d8175e61",
        "line_start": 85,
        "exact_text": "                                            6.5 J17 EC32           6.5 J17 EC32         225 / 55 R18 102 H XL         6.5 J17 EC32",
        "decision": "partially_covered",
        "selected": [
            signature("standard_tyre_specification", "215/65/17 99 / 6.5 J17 EC32; 215/60/18 98 / 6.5 J18 EC32; 205/55/19 97 / 7 J19 EC31"),
            signature("standard_tyre_specification", "215/65/17 99 / 6.5 J17 EC32; 215/60/18 98 / 6.5 J18 EC32; 205/55/19 97 / 7 J19 EC32"),
            signature("standard_tyre_specification", "215/65/17 99 / 6.5 J17 EC32; 215/60/18 98 / 6.5 J18 EC32; 205/55/19 97 / 7 J19 EC33"),
        ],
        "rationale": "Three 4x2 wheel fragments map to preserved signatures. The 4x4 tyre fragment is visible in this line but its full signature is attached to the adjacent candidate at line 87.",
        "source_facts": [fact("standard_tyre_specification", ["225 / 55 R18 102 H XL"], "No matching 4x4 signature is attached to this exact candidate; the full 4x4 signature is preserved on the adjacent line-87 candidate.")],
    },
    {
        "candidate_id": "a022542d3659709874331b49720c37d161e084cce3a2d39aa67dd9e2fa9077dc",
        "line_start": 87,
        "exact_text": "Rozmiary opon                               6.5 J18 EC32           6.5 J18 EC32         205 / 55 R19 97 H XL          6.5 J18 EC32",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("standard_tyre_specification", "215/65/17 99 / 6.5 J17 EC32; 215/60/18 98 / 6.5 J18 EC32; 205/55/19 97 / 7 J19 EC31"),
            signature("standard_tyre_specification", "215/65/17 99 / 6.5 J17 EC32; 215/60/18 98 / 6.5 J18 EC32; 205/55/19 97 / 7 J19 EC32"),
            signature("standard_tyre_specification", "215/65/17 99 / 6.5 J17 EC32; 215/60/18 98 / 6.5 J18 EC32; 205/55/19 97 / 7 J19 EC33"),
            signature("standard_tyre_specification", "225/60 R17 103 H XL 3PMSF / ALU 6.5 J17 5 36; 225/55 R18 102 H XL 3PMSF / ALU 7 J18 5 39; 205/55 R19 97 H XL letnie / ALU 7 J19 5 31; 225/55 R18 102 Y XL letnie / ALU 7 J18 5 39"),
        ],
        "rationale": "The row fragment belongs to all four complete tyre specifications already preserved for exact active configurations.",
        "source_facts": [],
    },
    {
        "candidate_id": "cbbf198ab0ba0278ef3263c4788363c82fb922edba05a81b5cc1a6b2ae5672e3",
        "line_start": 107,
        "exact_text": "      MASY (kg) I OBJĘTOŚCI (dm³ LUB LITRY)",
        "decision": "context_only_non_import",
        "selected": [],
        "rationale": "This is a section heading and unit overview, not an independent configuration observation.",
        "source_facts": [],
    },
    {
        "candidate_id": "ac026cdc5eecd20db2d922394ed239bbb74841150e942e357db6577893850210",
        "line_start": 108,
        "exact_text": "Masa własna maks.                              1478                    1439                      1515                     1487",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("maximum_kerb_weight", "1439"),
            signature("maximum_kerb_weight", "1478"),
            signature("maximum_kerb_weight", "1487"),
            signature("maximum_kerb_weight", "1515"),
        ],
        "rationale": "All four maximum-qualified kerb masses map to the exact existing powertrain projections.",
        "source_facts": [],
    },
    {
        "candidate_id": "a6264f24a5055a7253605774bc3c18e3b6f0d427d904eea7f81208bc624d67c1",
        "line_start": 110,
        "exact_text": "Dopuszczalna masa całkowita",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("gross_train_weight", "2940"),
            signature("gross_train_weight", "3390"),
            signature("gross_train_weight", "3430"),
            signature("gross_train_weight", "3545"),
        ],
        "rationale": "The following source line completes the label as gross train weight; all four values are already preserved from brochure page 20.",
        "source_facts": [],
    },
    {
        "candidate_id": "c3c6fdaa07353e7979d62aa82463cbc10f6797712ff9b4cc99363a557fbcb28b",
        "line_start": 113,
        "exact_text": "Dopuszczalna masa całkowita",
        "decision": "unresolved_signature_mismatch",
        "selected": [],
        "rationale": "The following source line completes the label as gross vehicle weight, but every attached signature is gross train weight and therefore cannot support this row.",
        "source_facts": [fact("gross_vehicle_weight", ["1930", "1890", "2045", "1940"], "The correct row meaning and values are visible on page 20, but no matching preserved evidence signature is attached to this candidate.")],
    },
    {
        "candidate_id": "39db289420d88d1ea305961ef5b59d36444fdc0df9651876d7e78d2ea4404c47",
        "line_start": 118,
        "exact_text": "Maksymalna masa przyczepy",
        "decision": "unresolved_signature_mismatch",
        "selected": [],
        "rationale": "The following source line completes the label as braked trailer weight, but every attached signature is unbraked trailer weight.",
        "source_facts": [fact("braked_trailer_weight", ["1500", "1500", "1500", "1000"], "The correct braked-trailer values are visible on page 20, but no matching preserved evidence signature is attached to this candidate.")],
    },
    {
        "candidate_id": "41bbd0e6df72e4f4f833936641ab29538dfb10915f9bdf138c87087fbd19b5cc",
        "line_start": 121,
        "exact_text": "Maksymalna masa przyczepy",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("unbraked_trailer_weight", "710"),
            signature("unbraked_trailer_weight", "740"),
            signature("unbraked_trailer_weight", "745"),
            signature("unbraked_trailer_weight", "750"),
        ],
        "rationale": "The following line completes the label as unbraked trailer weight and all four values are already preserved.",
        "source_facts": [],
    },
    {
        "candidate_id": "2384fc01f5d85e3b058641ef3295f3e7f84bc37d2fbe6c1b3390533ed7851ed5",
        "line_start": 123,
        "exact_text": "bez hamulca",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("unbraked_trailer_weight", "710"),
            signature("unbraked_trailer_weight", "740"),
            signature("unbraked_trailer_weight", "745"),
            signature("unbraked_trailer_weight", "750"),
        ],
        "rationale": "This continuation explicitly qualifies the preceding row as unbraked trailer weight.",
        "source_facts": [],
    },
    {
        "candidate_id": "30383e012debb4437af7e2c4dc88fde985e8f3d5411af50e41e4bf6ab4583cf4",
        "line_start": 125,
        "exact_text": "pod półką bagażową                                                                      444 (nie ma zestawu",
        "decision": "deferred_source_conflict",
        "selected": [],
        "rationale": "The 444 dm³ VDA Hybrid-G 150 4x4 value belongs to the brochure column whose tyre-repair-kit wording contradicts the equipment evidence; the existing cargo review deliberately deferred that complete column.",
        "source_facts": [fact("boot_capacity", ["444"], "Hybrid-G 150 4x4 cargo remains deferred until the tyre-repair-kit contradiction is resolved by corrected official evidence.")],
    },
    {
        "candidate_id": "d29ea5d85db0649b00ea016ba88e4d520a6bf53494c109b66a1f04ea8c37b6a4",
        "line_start": 126,
        "exact_text": "z zestawem naprawczym /                        609**                 667 / 624          naprawczego / koła              546 / 488",
        "decision": "partially_covered",
        "selected": [
            signature("boot_capacity", "546"),
            signature("boot_capacity", "609"),
            signature("boot_capacity", "667"),
        ],
        "rationale": "Repair-kit values 609, 667 and 546 are attached to this candidate. Spare-wheel values 624 and 488 are preserved on the adjacent line-127 candidate; the Hybrid-G 150 equipment context remains deferred.",
        "source_facts": [fact("boot_capacity", ["624", "488"], "Matching spare-wheel signatures are attached to the adjacent line-127 candidate rather than this exact candidate.")],
    },
    {
        "candidate_id": "003f4ab48c8a1c45688384d0098cc137bc89e34850caeea03993df39c1679f63",
        "line_start": 127,
        "exact_text": "z kołem zapasowym(5)                                                                       zapasowego)",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("boot_capacity", "488"),
            signature("boot_capacity", "624"),
        ],
        "rationale": "This continuation carries the upright VDA spare-wheel alternatives for mild hybrid 140 and hybrid 155.",
        "source_facts": [],
    },
    {
        "candidate_id": "668c92578b7754ecdd1186c9a0a66335fd1633469b305c5e978c11bb807a5266",
        "line_start": 128,
        "exact_text": "(dm³ VDA)",
        "decision": "context_only_non_import",
        "selected": [],
        "rationale": "The measurement basis is a qualifier already represented by cargo-context rows for imported observations; it is not a standalone scalar fact.",
        "source_facts": [],
    },
    {
        "candidate_id": "89ef9a910122c654f65f9453b2dee74e699c88262eea67e3572110c7aac57050",
        "line_start": 130,
        "exact_text": "ze złożoną tylną kanapą",
        "decision": "context_only_non_import",
        "selected": [],
        "rationale": "Folded second-row state is an observation qualifier represented by cargo-context rows, not an independent value.",
        "source_facts": [],
    },
    {
        "candidate_id": "eec3ad011ca04ebb1e04104807172f92ea41f0ea66ec25728d7faa031128e6a6",
        "line_start": 131,
        "exact_text": "z zestawem naprawczym /                       1877**               1937 / 1894                   1712                  1851 / 1791",
        "decision": "partially_covered",
        "selected": [
            signature("boot_capacity", "1851"),
            signature("boot_capacity", "1877"),
            signature("boot_capacity", "1937"),
        ],
        "rationale": "Repair-kit values 1877, 1937 and 1851 are attached here. Spare-wheel values 1894 and 1791 are attached to line 132, while Hybrid-G 150 value 1712 remains in the deliberately deferred column.",
        "source_facts": [
            fact("boot_capacity", ["1894", "1791"], "Matching spare-wheel signatures are attached to the adjacent line-132 candidate."),
            fact("boot_capacity", ["1712"], "Hybrid-G 150 4x4 cargo remains deferred due to the documented equipment-context contradiction."),
        ],
    },
    {
        "candidate_id": "b028c365c2607cc4600a9228e914262c789177b23670891c2b46fa8149e95b7d",
        "line_start": 132,
        "exact_text": "z kołem zapasowym(5)",
        "decision": "covered_by_selected_evidence",
        "selected": [
            signature("boot_capacity", "1791"),
            signature("boot_capacity", "1894"),
        ],
        "rationale": "This continuation carries the folded VDA spare-wheel alternatives for mild hybrid 140 and hybrid 155.",
        "source_facts": [],
    },
    {
        "candidate_id": "243364b290ee41854ec36d58beb10fef48920c134de37989db231feb0ab08af0",
        "line_start": 133,
        "exact_text": "(dm³ VDA)",
        "decision": "context_only_non_import",
        "selected": [],
        "rationale": "The VDA basis is already stored as cargo observation context and is not independently imported.",
        "source_facts": [],
    },
    {
        "candidate_id": "6f5fa4070102273882f5a279cec54cf62043e1a0b9de32b9713fd638d712dab4",
        "line_start": 135,
        "exact_text": "pod półką bagażową                                                                      556 (nie ma zestawu",
        "decision": "deferred_source_conflict",
        "selected": [],
        "rationale": "The 556 ordinary-litre Hybrid-G 150 4x4 value belongs to the same deliberately deferred cargo column with contradictory equipment context.",
        "source_facts": [fact("boot_capacity", ["556"], "Hybrid-G 150 4x4 cargo remains deferred until corrected official evidence resolves the equipment contradiction.")],
    },
    {
        "candidate_id": "34b6006dbff656d524640adc5e972d955cc8422ca34aa7feaed53031c3037c77",
        "line_start": 137,
        "exact_text": "z zestawem naprawczym /                                                                    zapasowego)",
        "decision": "context_only_non_import",
        "selected": [],
        "rationale": "This is an equipment-state continuation for the ordinary-litre cargo row; imported observations already carry explicit repair-kit or spare-wheel context and the 4x4 column remains deferred.",
        "source_facts": [],
    },
    {
        "candidate_id": "9ee1a9f2d2fc72f55882adb1e9c6dfb5b032fb6b7f83b98c7b4cdd577ff2ae0d",
        "line_start": 140,
        "exact_text": "ze złożoną tylną kanapą",
        "decision": "context_only_non_import",
        "selected": [],
        "rationale": "Folded second-row state is a cargo observation qualifier, not a standalone scalar observation.",
        "source_facts": [],
    },
    {
        "candidate_id": "4a8c8eeaa984895ae6b4e732dbd2ace7c4690e04e7af1b27d3234d03b290eeef",
        "line_start": 142,
        "exact_text": "z zestawem naprawczym /",
        "decision": "context_only_non_import",
        "selected": [],
        "rationale": "This line only continues the equipment qualifier for values on the preceding source line; the qualifier is preserved in cargo contexts for imported columns.",
        "source_facts": [],
    },
)


def signature_key(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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
    matches = [package for package in packages if isinstance(package, Mapping) and package.get("package_id") == PACKAGE_ID]
    ensure(len(matches) == 1, "residual_gap_001 package differs")
    package = dict(matches[0])
    ensure(package.get("source_code") == SOURCE_CODE, "package source differs")
    ensure(package.get("model_code") == "bigster", "package model differs")
    ensure(package.get("domain") == "technical_tables", "package domain differs")
    ensure(package.get("page") == SOURCE_PAGE, "package page differs")
    ensure(package.get("coverage_status") == "ambiguous", "package status differs")
    ensure(package.get("candidate_count") == 23, "package candidate count differs")
    candidates = package.get("candidates")
    ensure(isinstance(candidates, list) and len(candidates) == 23, "package candidates differ")
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
        "review_basis": "authored visual review of the archived page-20 technical table",
    }


def selected_signatures(candidate: Mapping[str, Any], expected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    available = candidate.get("evidence_signatures")
    ensure(isinstance(available, list), "candidate evidence signatures are missing")
    by_key: dict[str, dict[str, Any]] = {}
    for item in available:
        ensure(isinstance(item, Mapping), "candidate evidence signature differs")
        sig = item.get("signature")
        ensure(isinstance(sig, Mapping), "candidate signature payload is missing")
        key = signature_key(sig)
        ensure(key not in by_key, "candidate evidence signature is duplicated")
        by_key[key] = json.loads(json.dumps(dict(item), ensure_ascii=False))
    result: list[dict[str, Any]] = []
    for wanted in expected:
        key = signature_key(wanted)
        ensure(key in by_key, f"selected signature is not attached to candidate: {key}")
        result.append(by_key[key])
    return result


def build_review(prioritization: Mapping[str, Any], repository: Path) -> dict[str, Any]:
    package = validate_prioritization(prioritization)
    source_receipt = verify_source(repository)
    candidates = package["candidates"]
    candidate_by_id = {str(candidate.get("candidate_id")): candidate for candidate in candidates if isinstance(candidate, Mapping)}
    ensure(len(candidate_by_id) == 23, "package candidate IDs are not unique")
    manifest_ids = [entry["candidate_id"] for entry in DECISIONS]
    ensure(len(manifest_ids) == len(set(manifest_ids)) == 23, "authored decision candidate IDs differ")
    ensure(set(manifest_ids) == set(candidate_by_id), "authored decision partition differs")

    decisions: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    selected_count = 0
    selected_record_count = 0
    for authored in DECISIONS:
        candidate = candidate_by_id[authored["candidate_id"]]
        ensure(candidate.get("line_start") == authored["line_start"], f"candidate line differs: {authored['candidate_id']}")
        ensure(candidate.get("line_end") == authored["line_start"], f"candidate line span differs: {authored['candidate_id']}")
        ensure(candidate.get("exact_text") == authored["exact_text"], f"candidate exact text differs: {authored['candidate_id']}")
        ensure(candidate.get("source_code") == SOURCE_CODE, "candidate source boundary differs")
        ensure(candidate.get("page") == SOURCE_PAGE, "candidate page boundary differs")
        ensure(candidate.get("coverage_status") == "ambiguous", "candidate input status differs")
        decision = str(authored["decision"])
        ensure(decision in DECISION_STATUSES, f"unknown authored decision: {decision}")
        selected = selected_signatures(candidate, authored["selected"])
        for item in selected:
            records = item.get("records")
            ensure(isinstance(records, list), "selected evidence records are missing")
            ensure(item.get("record_count") == len(records), "selected evidence record count differs")
            for record in records:
                ensure(isinstance(record, Mapping), "selected evidence record differs")
                ensure(record.get("source_code") == SOURCE_CODE, "selected evidence source differs")
                ensure(record.get("source_page") == SOURCE_PAGE, "selected evidence page differs")
            selected_record_count += len(records)
        selected_count += len(selected)
        status_counts[decision] += 1
        decisions.append(
            {
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
                "selected_evidence_record_count": sum(int(item["record_count"]) for item in selected),
                "selected_evidence_signatures": selected,
                "source_facts": authored["source_facts"],
            }
        )

    ensure(sum(status_counts.values()) == 23, "authored decision count differs")
    ensure(status_counts == Counter({
        "covered_by_selected_evidence": 9,
        "partially_covered": 3,
        "context_only_non_import": 7,
        "deferred_source_conflict": 2,
        "unresolved_signature_mismatch": 2,
    }), "authored decision distribution differs")

    return {
        "version": REVIEW_VERSION,
        "kind": REVIEW_KIND,
        "reviewed_on": REVIEWED_ON,
        "status": "complete",
        "source_prioritization": DEFAULT_PRIORITIZATION.as_posix(),
        "package_id": PACKAGE_ID,
        "source_receipt": source_receipt,
        "scope": {
            "candidate_count": 23,
            "source_code": SOURCE_CODE,
            "model_code": "bigster",
            "domain": "technical_tables",
            "page": SOURCE_PAGE,
            "input_coverage_status": "ambiguous",
        },
        "policy": {
            "candidate_id_and_exact_text_cited": True,
            "selected_evidence_copied_without_reinterpretation": True,
            "source_page_layout_used_for_row_disambiguation": True,
            "adjacent_line_evidence_not_silently_attached": True,
            "master_data_changes": False,
            "approved_import_spec_generation": False,
            "automatic_promotion": False,
        },
        "summary": {
            "candidate_count": 23,
            "decision_counts": {status: status_counts.get(status, 0) for status in sorted(DECISION_STATUSES)},
            "selected_evidence_signature_count": selected_count,
            "selected_evidence_record_count": selected_record_count,
            "candidates_with_selected_evidence": sum(1 for item in decisions if item["selected_evidence_signature_count"] > 0),
            "candidates_without_selected_evidence": sum(1 for item in decisions if item["selected_evidence_signature_count"] == 0),
        },
        "decisions": decisions,
        "semantic_boundaries": {
            "review_is_not_import_approval": True,
            "context_only_fragments_are_not_negative_evidence": True,
            "source_conflict_deferral_is_preserved": True,
            "signature_mismatch_does_not_authorize_cross_attribute_substitution": True,
            "no_configuration_projection_is_created": True,
        },
        "next_package": {
            "name": NEXT_PACKAGE,
            "status": "planned",
            "goal": "Review the 16 ambiguous technical candidates from Jogger brochure page 19 against their 34 preserved evidence signatures without creating master-data rows or approved import specifications.",
        },
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    counts = summary["decision_counts"]
    lines = [
        "# Bigster Technical Page 20 Ambiguity Review",
        "",
        "Authored review of `residual_gap_001`. Decisions preserve the source page and do not approve imports.",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Reviewed candidates | {summary['candidate_count']} |",
        f"| Covered by selected evidence | {counts['covered_by_selected_evidence']} |",
        f"| Partially covered | {counts['partially_covered']} |",
        f"| Context-only non-import | {counts['context_only_non_import']} |",
        f"| Deferred source conflict | {counts['deferred_source_conflict']} |",
        f"| Unresolved signature mismatch | {counts['unresolved_signature_mismatch']} |",
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
        lines.append(
            f"| {item['line_start']} | `{item['candidate_id']}` | `{item['authored_decision']}` | "
            f"{item['selected_evidence_signature_count']} | {exact} |"
        )
    lines.extend(["", "## Residual authored findings", ""])
    for item in payload["decisions"]:
        if item["authored_decision"] not in {
            "partially_covered",
            "deferred_source_conflict",
            "unresolved_signature_mismatch",
        }:
            continue
        lines.append(f"### Line {item['line_start']} — `{item['candidate_id']}`")
        lines.append("")
        lines.append(item["rationale"])
        for source_fact in item["source_facts"]:
            values = ", ".join(f"`{value}`" for value in source_fact["source_values"])
            lines.append(
                f"- `{source_fact['attribute_code']}`: {values} — {source_fact['reason']}"
            )
        lines.append("")
    lines.extend(
        [
            "## Safety boundary",
            "",
            "- no file under `data/master` is changed;",
            "- no approved import specification is created or changed;",
            "- no mismatched signature is substituted across attributes;",
            "- Hybrid-G 150 4x4 cargo remains deferred under the existing source-conflict decision.",
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
        raise BigsterPage20ReviewError(f"output path is restricted: {path}")
    return resolved


def verify_output(path: Path, expected: str, label: str) -> None:
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BigsterPage20ReviewError(f"cannot read {label}: {exc}") from exc
    ensure(actual == expected, f"{label} differs from deterministic output")


def build_from_path(repository: Path, prioritization_path: Path) -> tuple[dict[str, Any], str]:
    resolved = prioritization_path if prioritization_path.is_absolute() else repository / prioritization_path
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
            verify_output(json_output, json_text, "Bigster page-20 review JSON")
            verify_output(markdown_output, markdown, "Bigster page-20 review Markdown")
            print("Bigster technical page-20 ambiguity review: PASS")
        else:
            write_atomic(json_output, json_text)
            write_atomic(markdown_output, markdown)
            print(f"JSON report written to {json_output}")
            print(f"Markdown report written to {markdown_output}")
        summary = payload["summary"]
        print(f"Candidates reviewed: {summary['candidate_count']}")
        print(f"Selected evidence signatures: {summary['selected_evidence_signature_count']}")
        print(f"Selected evidence records: {summary['selected_evidence_record_count']}")
        return 0
    except BigsterPage20ReviewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
