#!/usr/bin/env python3
"""Close the final three eligible Sandero source-scoped completeness candidates."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from tools import configuration_gap_resolution_plan as gap_plan
from tools import existing_configuration_missing_data_analysis as missing_analysis
from tools import verified_pdf_candidate_coverage_reconciliation as reconciliation

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
SPEC = ROOT / "data" / "imports" / "sandero_residual_source_closure_20260801.csv"
VALUES = MASTER / "configuration_attribute_values.csv"
AVAILABILITY = MASTER / "configuration_attribute_availability.csv"
STATE = ROOT / "project" / "state.json"
PACKAGE = ROOT / "project" / "packages" / "sandero-residual-source-closure-20260801.md"
TEST = ROOT / "tests" / "test_sandero_residual_source_closure_20260801.py"
OBSERVATION_DATE = "2026-06-26"
AS_OF = "2026-08-01"
EXHAUSTED = "source_exhausted_not_stated"

EXPRESSION_SOURCE = "src_pl_sandero_expression_ecog120_mt_20260626"
JOURNEY_SOURCE = "src_pl_sandero_journey_ecog120_mt_20260626"
TCE_SOURCE = "src_pl_sandero_stepway_catalog_tce_slice_20260703"
EXPRESSION_CONFIGURATION = "sandero_iii_expression_ecog120_manual"
JOURNEY_CONFIGURATION = "sandero_iii_journey_ecog120_manual"
TCE_CONFIGURATIONS = (
    "sandero_iii_essential_tce100_manual",
    "sandero_iii_expression_tce100_manual",
    "sandero_iii_journey_tce100_manual",
    "sandero_stepway_iii_essential_tce110_manual",
    "sandero_stepway_iii_expression_tce110_manual",
    "sandero_stepway_iii_extreme_tce110_manual",
)
STEPWAY_TCE_CONFIGURATIONS = TCE_CONFIGURATIONS[3:]

SOURCE_METADATA = {
    EXPRESSION_SOURCE: {
        "path": ROOT / "PDF" / "Cenniki" / "NOWE SANDERO expression Eco-G 120 f.pdf",
        "sha256": "82a8853d90b492e48595ff33db73632dc309b8a12d08d11dd3c259fca4eaff68",
        "review": REPORTING / "sandero_expression_source_gap_review.json",
        "review_md": REPORTING / "sandero_expression_source_gap_review.md",
    },
    JOURNEY_SOURCE: {
        "path": ROOT / "PDF" / "Cenniki" / "NOWE SANDERO journey Eco-G 120 f.pdf",
        "sha256": "7ab1526e7bc2a72ff2b179f30cd0c8c223633f1100d31aa7dd80594325b302a3",
        "review": REPORTING / "sandero_journey_source_gap_review.json",
        "review_md": REPORTING / "sandero_journey_source_gap_review.md",
    },
    TCE_SOURCE: {
        "path": ROOT / "PDF" / "Cenniki" / "DACIA SANDERO I SANDERO STEPWAY cennik MY26 20260703.pdf",
        "sha256": "5af2dbaf268480ec1e7e6d6e35fd2037b6fba3fb79972026e4f68c08055ba783",
        "review": REPORTING / "sandero_tce_catalog_source_gap_review.json",
        "review_md": REPORTING / "sandero_tce_catalog_source_gap_review.md",
    },
}

SPEC_FIELDS = (
    "record_type",
    "configuration_code",
    "attribute_code",
    "value",
    "availability_status",
    "source_code",
    "source_page",
    "source_section",
    "source_text",
    "normalization_notes",
)
VALUE_FIELDS = (
    "id", "code", "configuration_code", "attribute_code", "fuel_type_code",
    "gear_number", "value", "observation_date", "source_code", "notes",
)
AVAILABILITY_FIELDS = (
    "id", "code", "configuration_code", "attribute_code",
    "availability_status", "observation_date", "source_code", "notes",
)
SPEC_ROWS = (
    {
        "record_type": "value",
        "configuration_code": EXPRESSION_CONFIGURATION,
        "attribute_code": "wheel_finish",
        "value": "stalowe",
        "availability_status": "",
        "source_code": EXPRESSION_SOURCE,
        "source_page": "2",
        "source_section": "Felgi",
        "source_text": '16" felgi stalowe ATARA',
        "normalization_notes": "Retains only the source-visible finish wording; wheel design and material remain separate existing observations.",
    },
    {
        "record_type": "value",
        "configuration_code": JOURNEY_CONFIGURATION,
        "attribute_code": "wheel_finish",
        "value": "aluminiowe",
        "availability_status": "",
        "source_code": JOURNEY_SOURCE,
        "source_page": "2",
        "source_section": "Felgi",
        "source_text": '16" felgi aluminiowe TAMIA',
        "normalization_notes": "Retains only the source-visible finish wording; wheel design and material remain separate existing observations.",
    },
    {
        "record_type": "availability",
        "configuration_code": JOURNEY_CONFIGURATION,
        "attribute_code": "parking_assist_system",
        "value": "",
        "availability_status": "standard",
        "source_code": JOURNEY_SOURCE,
        "source_page": "4",
        "source_section": "Komfort",
        "source_text": "system wspomagania parkowania przód/tył",
        "normalization_notes": "The aggregate parking-assistance attribute is supported directly by the exact configuration source.",
    },
)

TARGET_DECISIONS = {
    ("technical", EXPRESSION_SOURCE, EXPRESSION_CONFIGURATION, "wheel_finish"),
    ("technical", JOURNEY_SOURCE, JOURNEY_CONFIGURATION, "wheel_finish"),
    ("equipment", JOURNEY_SOURCE, JOURNEY_CONFIGURATION, "parking_assist_system"),
}
EVIDENCE_PATHS = (
    REPORTING / "configuration_gap_evidence.json",
    REPORTING / "sandero_ecog120_manual_gap_evidence.json",
)
SOURCE_REVIEW_INDEX = REPORTING / "configuration_gap_source_review.json"

MANIFEST_PATHS = [
    "data/imports/sandero_residual_source_closure_20260801.csv",
    "data/master/configuration_attribute_availability.csv",
    "data/master/configuration_attribute_values.csv",
    "data/reporting/configuration_gap_evidence.json",
    "data/reporting/configuration_gap_resolution_plan.json",
    "data/reporting/configuration_gap_source_review.json",
    "data/reporting/existing_configuration_missing_data_analysis.json",
    "data/reporting/existing_configuration_missing_data_analysis.md",
    "data/reporting/sandero_ecog120_manual_gap_evidence.json",
    "data/reporting/sandero_expression_source_gap_review.json",
    "data/reporting/sandero_expression_source_gap_review.md",
    "data/reporting/sandero_journey_source_gap_review.json",
    "data/reporting/sandero_journey_source_gap_review.md",
    "data/reporting/sandero_tce_catalog_source_gap_review.json",
    "data/reporting/sandero_tce_catalog_source_gap_review.md",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
    "project/ROADMAP.md",
    "project/SESSION_STATE.md",
    "project/STATE_SUMMARY.md",
    "project/packages/sandero-residual-source-closure-20260801.md",
    "project/state.json",
    "tests/test_sandero_residual_source_closure_20260801.py",
    "tools/import_sandero_residual_source_closure_20260801.py",
]


class ClosureError(RuntimeError):
    pass


def canonical_json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ClosureError(f"missing CSV header: {path}")
        return list(reader.fieldnames), [dict(row) for row in reader]


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ClosureError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(payload), encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_text(path: Path) -> str:
    try:
        process = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ClosureError(f"cannot extract source PDF text: {path}: {exc}") from exc
    return process.stdout


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def verify_sources() -> None:
    for source, metadata in SOURCE_METADATA.items():
        path = metadata["path"]
        if not isinstance(path, Path) or not path.is_file():
            raise ClosureError(f"missing source file for {source}: {path}")
        actual = sha256(path)
        if actual != metadata["sha256"]:
            raise ClosureError(f"source SHA-256 mismatch for {source}: {actual}")

    expression = compact(pdf_text(SOURCE_METADATA[EXPRESSION_SOURCE]["path"]))
    journey = compact(pdf_text(SOURCE_METADATA[JOURNEY_SOURCE]["path"]))
    tce = compact(pdf_text(SOURCE_METADATA[TCE_SOURCE]["path"]))
    if compact('16" felgi stalowe ATARA') not in expression:
        raise ClosureError("Expression wheel statement is not present in the exact PDF")
    if compact('16" felgi aluminiowe TAMIA') not in journey:
        raise ClosureError("Journey wheel statement is not present in the exact PDF")
    if compact("system wspomagania parkowania przód/tył") not in journey:
        raise ClosureError("Journey parking-assistance statement is not present in the exact PDF")
    if "tce 100" not in tce or "tce 110" not in tce:
        raise ClosureError("TCe catalogue technical slice is missing")
    if any(token in tce for token in ("80–120", "80 – 120", "80-120")):
        raise ClosureError("TCe catalogue unexpectedly states 80-120 km/h elasticity")
    if "wysokość całkowita" in tce or "1586" in tce or "1535" in tce:
        raise ClosureError("TCe catalogue unexpectedly states Stepway overall height")


def note(row: Mapping[str, str]) -> str:
    return (
        f"Source page {row['source_page']}, section {row['source_section']}: "
        f"{row['source_text']}. {row['normalization_notes']}"
    )


def row_code(row: Mapping[str, str]) -> str:
    suffix = "_availability" if row["record_type"] == "availability" else ""
    return (
        f"{row['configuration_code']}_{row['attribute_code']}{suffix}"
        "_residual_source_closure_20260626"
    )


def write_spec() -> None:
    write_csv(SPEC, SPEC_FIELDS, SPEC_ROWS)


def append_rows() -> None:
    value_fields, values = read_csv(VALUES)
    if value_fields != list(VALUE_FIELDS):
        raise ClosureError("configuration value header changed")
    value_generated = [
        {
            "code": row_code(row),
            "configuration_code": row["configuration_code"],
            "attribute_code": row["attribute_code"],
            "fuel_type_code": "",
            "gear_number": "",
            "value": row["value"],
            "observation_date": OBSERVATION_DATE,
            "source_code": row["source_code"],
            "notes": note(row),
        }
        for row in SPEC_ROWS
        if row["record_type"] == "value"
    ]
    existing_value_codes = {row["code"] for row in values}
    existing_value_semantics = {
        (
            row["configuration_code"], row["attribute_code"],
            row["fuel_type_code"], row["gear_number"], row["observation_date"],
        )
        for row in values
    }
    next_value_id = max(int(row["id"]) for row in values) + 1
    for generated in value_generated:
        semantic = (
            generated["configuration_code"], generated["attribute_code"],
            generated["fuel_type_code"], generated["gear_number"],
            generated["observation_date"],
        )
        if generated["code"] in existing_value_codes:
            continue
        if semantic in existing_value_semantics:
            raise ClosureError(f"conflicting existing value semantic: {semantic}")
        values.append({"id": str(next_value_id), **generated})
        next_value_id += 1
    write_csv(VALUES, VALUE_FIELDS, values)

    availability_fields, availability = read_csv(AVAILABILITY)
    if availability_fields != list(AVAILABILITY_FIELDS):
        raise ClosureError("configuration availability header changed")
    availability_generated = [
        {
            "code": row_code(row),
            "configuration_code": row["configuration_code"],
            "attribute_code": row["attribute_code"],
            "availability_status": row["availability_status"],
            "observation_date": OBSERVATION_DATE,
            "source_code": row["source_code"],
            "notes": note(row),
        }
        for row in SPEC_ROWS
        if row["record_type"] == "availability"
    ]
    existing_availability_codes = {row["code"] for row in availability}
    existing_availability_semantics = {
        (
            row["configuration_code"], row["attribute_code"],
            row["observation_date"], row["source_code"],
        )
        for row in availability
    }
    next_availability_id = max(int(row["id"]) for row in availability) + 1
    for generated in availability_generated:
        semantic = (
            generated["configuration_code"], generated["attribute_code"],
            generated["observation_date"], generated["source_code"],
        )
        if generated["code"] in existing_availability_codes:
            continue
        if semantic in existing_availability_semantics:
            raise ClosureError(f"conflicting existing availability semantic: {semantic}")
        availability.append({"id": str(next_availability_id), **generated})
        next_availability_id += 1
    write_csv(AVAILABILITY, AVAILABILITY_FIELDS, availability)


def scalar_resolution(configuration: str, value: str, source_page: int) -> dict[str, object]:
    return {
        "attribute_code": "wheel_finish",
        "value": value,
        "source_page": source_page,
    }


def review_payloads() -> dict[str, dict[str, object]]:
    expression = {
        "version": 1,
        "as_of": AS_OF,
        "kind": "configuration_source_gap_review",
        "model_code": "sandero",
        "configuration_code": EXPRESSION_CONFIGURATION,
        "source_code": EXPRESSION_SOURCE,
        "source_path": str(SOURCE_METADATA[EXPRESSION_SOURCE]["path"].relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": SOURCE_METADATA[EXPRESSION_SOURCE]["sha256"],
        "source_observation_date": OBSERVATION_DATE,
        "initial_gap": {"reported_records": 2, "unique_slots": 1},
        "resolution": {"scalar_values": [scalar_resolution(EXPRESSION_CONFIGURATION, "stalowe", 2)]},
        "reconciliation": {
            "classification": EXHAUSTED,
            "resolved_unique_slots": 1,
            "remaining_unique_slots": 0,
            "remaining_slots": [],
            "boundary": "The exact source states the steel ATARA wheel wording. No unresolved qualifying slots remain for this source.",
        },
    }
    journey = {
        "version": 1,
        "as_of": AS_OF,
        "kind": "configuration_source_gap_review",
        "model_code": "sandero",
        "configuration_code": JOURNEY_CONFIGURATION,
        "source_code": JOURNEY_SOURCE,
        "source_path": str(SOURCE_METADATA[JOURNEY_SOURCE]["path"].relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": SOURCE_METADATA[JOURNEY_SOURCE]["sha256"],
        "source_observation_date": OBSERVATION_DATE,
        "initial_gap": {"reported_records": 4, "unique_slots": 2},
        "resolution": {
            "scalar_values": [scalar_resolution(JOURNEY_CONFIGURATION, "aluminiowe", 2)],
            "availability": [
                {"attribute_code": "parking_assist_system", "availability_status": "standard", "source_page": 4}
            ],
        },
        "reconciliation": {
            "classification": EXHAUSTED,
            "resolved_unique_slots": 2,
            "remaining_unique_slots": 0,
            "remaining_slots": [],
            "boundary": "The exact source states the alloy TAMIA wheel wording and front/rear parking assistance. No unresolved qualifying slots remain for this source.",
        },
    }
    remaining: list[dict[str, str]] = []
    for configuration in TCE_CONFIGURATIONS:
        remaining.append(
            {
                "configuration_code": configuration,
                "attribute_code": "elasticity_80_120",
                "fuel_type_code": "petrol",
                "gear_number": "",
                "reason": "not_stated_in_source_without_gear_context",
            }
        )
    for configuration in STEPWAY_TCE_CONFIGURATIONS:
        remaining.append(
            {
                "configuration_code": configuration,
                "attribute_code": "overall_height",
                "fuel_type_code": "",
                "gear_number": "",
                "reason": "not_stated_in_source",
            }
        )
    tce = {
        "version": 1,
        "as_of": AS_OF,
        "kind": "multi_configuration_source_gap_review",
        "model_code": "sandero",
        "configuration_codes": list(TCE_CONFIGURATIONS),
        "source_code": TCE_SOURCE,
        "source_path": str(SOURCE_METADATA[TCE_SOURCE]["path"].relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": SOURCE_METADATA[TCE_SOURCE]["sha256"],
        "source_observation_date": "2026-07-03",
        "initial_gap": {"configuration_count": 6, "technical_slots": 9, "unique_slots": 9},
        "resolution": {"scalar_values": [], "availability": []},
        "preserved_context": [
            {
                "attribute_code": "elasticity_80_120",
                "reason": "The repository contains gear-specific brochure observations, but the completeness slot is unqualified and this catalogue source states no 80-120 km/h value."
            }
        ],
        "reconciliation": {
            "classification": EXHAUSTED,
            "resolved_unique_slots": 0,
            "remaining_unique_slots": 9,
            "remaining_slots": remaining,
            "boundary": "The six-page exact catalogue states neither unqualified 80-120 km/h elasticity nor Stepway overall height. Gear-specific brochure values and exact Eco-G configuration values are not projected into these TCe catalogue slots.",
        },
    }
    return {EXPRESSION_SOURCE: expression, JOURNEY_SOURCE: journey, TCE_SOURCE: tce}


def render_review(payload: Mapping[str, object]) -> str:
    reconciliation_payload = payload["reconciliation"]
    if not isinstance(reconciliation_payload, Mapping):
        raise ClosureError("invalid review reconciliation")
    lines = [
        f"# Source Gap Review — {payload['source_code']}",
        "",
        f"Classification: `{reconciliation_payload['classification']}`",
        "",
        "## Resolution",
        "",
        f"- Resolved unique slots: {reconciliation_payload['resolved_unique_slots']}",
        f"- Remaining unique slots: {reconciliation_payload['remaining_unique_slots']}",
        "",
        "## Evidence boundary",
        "",
        str(reconciliation_payload["boundary"]),
        "",
    ]
    return "\n".join(lines)


def write_reviews() -> None:
    for source, payload in review_payloads().items():
        write_json(SOURCE_METADATA[source]["review"], payload)
        SOURCE_METADATA[source]["review_md"].write_text(render_review(payload), encoding="utf-8")


def targeted_decision(decision: object) -> bool:
    if not isinstance(decision, Mapping):
        return False
    key = (
        str(decision.get("domain", "")),
        str(decision.get("source_code", "")),
        str(decision.get("configuration_code", "")),
        str(decision.get("attribute_code", "")),
    )
    return key in TARGET_DECISIONS


def targeted_triage_key(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split("|")
    if len(parts) != 6:
        return False
    domain, source, configuration, _category, attribute, _fuel = parts
    return (domain, source, configuration, attribute) in TARGET_DECISIONS


def close_reporting_dependencies() -> None:
    for path in EVIDENCE_PATHS:
        if not path.is_file():
            continue
        payload = read_json(path)
        decisions = payload.get("decisions")
        if not isinstance(decisions, list):
            raise ClosureError(f"unexpected decisions payload: {path}")
        payload["decisions"] = [item for item in decisions if not targeted_decision(item)]
        write_json(path, payload)
    source_review = read_json(SOURCE_REVIEW_INDEX)
    triage = source_review.get("review_triage_keys")
    if not isinstance(triage, list):
        raise ClosureError("unexpected configuration source-review payload")
    source_review["review_triage_keys"] = [item for item in triage if not targeted_triage_key(item)]
    write_json(SOURCE_REVIEW_INDEX, source_review)

    evidence = gap_plan.read_json(
        REPORTING / "configuration_gap_evidence.json",
        "configuration-gap evidence specification",
    )
    plan = gap_plan.build_expected_plan_spec(ROOT, evidence)
    (REPORTING / "configuration_gap_resolution_plan.json").write_text(
        gap_plan.render_json(plan), encoding="utf-8"
    )

    reconciliation_payload, reconciliation_markdown = reconciliation.build_from_paths(
        ROOT, reconciliation.DEFAULT_LEDGER, reconciliation.DEFAULT_REVIEW
    )
    (ROOT / reconciliation.DEFAULT_JSON).write_text(
        reconciliation.canonical_json(reconciliation_payload), encoding="utf-8"
    )
    (ROOT / reconciliation.DEFAULT_MARKDOWN).write_text(
        reconciliation_markdown, encoding="utf-8"
    )


def write_missing_analysis() -> dict[str, object]:
    payload = missing_analysis.collect(ROOT)
    write_json(REPORTING / "existing_configuration_missing_data_analysis.json", payload)
    (REPORTING / "existing_configuration_missing_data_analysis.md").write_text(
        missing_analysis.render_markdown(payload), encoding="utf-8"
    )
    summary = payload.get("summary")
    if not isinstance(summary, Mapping) or summary.get("eligible_candidate_count") != 0:
        raise ClosureError(f"eligible Sandero source candidates remain: {summary}")
    if payload.get("selected_next_package") is not None:
        raise ClosureError("completeness analysis still selects a source package")
    return payload


def package_markdown(analysis_payload: Mapping[str, object]) -> str:
    summary = analysis_payload["summary"]
    return f"""# Sandero Residual Source Closure

Status: complete

Package ID: `sandero_residual_source_closure_006`

## Scope

The package closes the final three eligible Sandero source candidates as one evidence-bounded unit:

- `{TCE_SOURCE}`;
- `{JOURNEY_SOURCE}`;
- `{EXPRESSION_SOURCE}`.

## Imported evidence

- Sandero Expression Eco-G 120 manual: `wheel_finish = stalowe` from page 2.
- Sandero Journey Eco-G 120 manual: `wheel_finish = aluminiowe` from page 2.
- Sandero Journey Eco-G 120 manual: `parking_assist_system = standard` from page 4.

## Formal source closure

The TCe catalogue candidate retains nine missing slots as source-exhausted: six unqualified `elasticity_80_120` slots and three Stepway `overall_height` slots. The source states neither value family. Gear-specific brochure observations, Eco-G configuration PDFs and sibling trims are not projected into the TCe configurations.

## Result

- eligible source candidates: {summary['eligible_candidate_count']};
- exhausted-source candidates retained for audit: {summary['exhausted_source_candidate_count']};
- selected next source package: none;
- no new model, domain, attribute or architecture.

The next planned package is a bounded milestone-closure review that will decide between final documentation/release work and maintenance mode without adding models.
"""


def update_state(analysis_payload: Mapping[str, object]) -> None:
    state = read_json(STATE)
    state["updated_on"] = AS_OF
    state["phase"] = "Sandero Residual Source Closure"
    baseline = state.get("baseline")
    if not isinstance(baseline, dict):
        raise ClosureError("state baseline is missing")
    baseline["tests"] = 1774
    baseline["rows"] = 11694
    baseline["configuration_values"] = 3567
    baseline["availability_records"] = 5906
    state["current_package"] = {
        "package_id": "sandero_residual_source_closure_006",
        "kind": "source_backed_completeness_import",
        "name": "Sandero Residual Source Closure",
        "status": "complete",
        "goal": "Close all three remaining eligible Sandero source candidates with exact imports or formal source-exhaustion receipts and no cross-configuration inference.",
        "manifest_paths": MANIFEST_PATHS,
    }
    state["next_package"] = {
        "package_id": "data_scope_milestone_closure_review_001",
        "kind": "data_quality_review",
        "name": "Data Scope Milestone Closure Review",
        "status": "planned",
        "goal": "Confirm that the current model and data-product milestone has no eligible source-backed completeness work remaining, reconcile final documentation, and decide between a final release or maintenance mode without adding models or domains.",
        "manifest_paths": [],
    }
    write_json(STATE, state)
    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE.write_text(package_markdown(analysis_payload), encoding="utf-8")


def write_test() -> None:
    TEST.write_text(
        '''from __future__ import annotations\n\nimport csv\nimport hashlib\nimport json\nimport unittest\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\ndef rows(path: Path):\n    with path.open(encoding="utf-8-sig", newline="") as handle:\n        return list(csv.DictReader(handle))\n\ndef payload(path: Path):\n    return json.loads(path.read_text(encoding="utf-8"))\n\nclass SanderoResidualSourceClosureTests(unittest.TestCase):\n    def test_spec_has_three_exact_rows(self):\n        spec = rows(ROOT / "data/imports/sandero_residual_source_closure_20260801.csv")\n        self.assertEqual(len(spec), 3)\n        self.assertEqual({row["record_type"] for row in spec}, {"value", "availability"})\n\n    def test_two_wheel_finish_values_are_exact(self):\n        selected = {\n            (row["configuration_code"], row["attribute_code"]): row\n            for row in rows(ROOT / "data/master/configuration_attribute_values.csv")\n            if row["code"].endswith("_residual_source_closure_20260626")\n        }\n        self.assertEqual(selected[("sandero_iii_expression_ecog120_manual", "wheel_finish")]["value"], "stalowe")\n        self.assertEqual(selected[("sandero_iii_journey_ecog120_manual", "wheel_finish")]["value"], "aluminiowe")\n        self.assertEqual({int(row["id"]) for row in selected.values()}, {3566, 3567})\n\n    def test_journey_parking_assistance_is_standard(self):\n        selected = [\n            row for row in rows(ROOT / "data/master/configuration_attribute_availability.csv")\n            if row["code"].endswith("_residual_source_closure_20260626")\n        ]\n        self.assertEqual(len(selected), 1)\n        self.assertEqual(selected[0]["attribute_code"], "parking_assist_system")\n        self.assertEqual(selected[0]["availability_status"], "standard")\n        self.assertEqual(int(selected[0]["id"]), 5906)\n\n    def test_source_hashes_match_registered_files(self):\n        expected = {\n            "PDF/Cenniki/NOWE SANDERO expression Eco-G 120 f.pdf": "82a8853d90b492e48595ff33db73632dc309b8a12d08d11dd3c259fca4eaff68",\n            "PDF/Cenniki/NOWE SANDERO journey Eco-G 120 f.pdf": "7ab1526e7bc2a72ff2b179f30cd0c8c223633f1100d31aa7dd80594325b302a3",\n            "PDF/Cenniki/DACIA SANDERO I SANDERO STEPWAY cennik MY26 20260703.pdf": "5af2dbaf268480ec1e7e6d6e35fd2037b6fba3fb79972026e4f68c08055ba783",\n        }\n        for relative, digest in expected.items():\n            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), digest)\n\n    def test_all_three_sources_have_exhaustion_receipts(self):\n        names = [\n            "sandero_expression_source_gap_review.json",\n            "sandero_journey_source_gap_review.json",\n            "sandero_tce_catalog_source_gap_review.json",\n        ]\n        reviews = [payload(ROOT / "data/reporting" / name) for name in names]\n        self.assertEqual({item["reconciliation"]["classification"] for item in reviews}, {"source_exhausted_not_stated"})\n\n    def test_tce_review_preserves_nine_unimported_slots(self):\n        review = payload(ROOT / "data/reporting/sandero_tce_catalog_source_gap_review.json")\n        remaining = review["reconciliation"]["remaining_slots"]\n        self.assertEqual(len(remaining), 9)\n        self.assertEqual(sum(item["attribute_code"] == "elasticity_80_120" for item in remaining), 6)\n        self.assertEqual(sum(item["attribute_code"] == "overall_height" for item in remaining), 3)\n        self.assertTrue(all(item.get("gear_number", "") == "" for item in remaining))\n\n    def test_analysis_has_no_eligible_source_candidate(self):\n        report = payload(ROOT / "data/reporting/existing_configuration_missing_data_analysis.json")\n        self.assertEqual(report["summary"]["eligible_candidate_count"], 0)\n        self.assertIsNone(report["selected_next_package"] )\n        ranked = {item["source_code"]: item for item in report["ranked_candidates"]}\n        self.assertEqual(ranked["src_pl_sandero_stepway_catalog_tce_slice_20260703"]["selection_status"], "source_exhausted_not_stated")\n\n    def test_state_advances_to_bounded_milestone_closure(self):\n        state = payload(ROOT / "project/state.json")\n        self.assertEqual(state["current_package"]["package_id"], "sandero_residual_source_closure_006")\n        self.assertEqual(state["current_package"]["status"], "complete")\n        self.assertEqual(state["next_package"]["package_id"], "data_scope_milestone_closure_review_001")\n        self.assertEqual(state["baseline"]["configuration_values"], 3567)\n        self.assertEqual(state["baseline"]["availability_records"], 5906)\n\nif __name__ == "__main__":\n    unittest.main()\n''',
        encoding="utf-8",
    )


def apply() -> None:
    verify_sources()
    write_spec()
    append_rows()
    write_reviews()
    close_reporting_dependencies()
    analysis_payload = write_missing_analysis()
    update_state(analysis_payload)
    write_test()


def check() -> None:
    verify_sources()
    _, values = read_csv(VALUES)
    selected_values = [row for row in values if row["code"].endswith("_residual_source_closure_20260626")]
    if len(selected_values) != 2:
        raise ClosureError(f"expected two imported values, found {len(selected_values)}")
    _, availability = read_csv(AVAILABILITY)
    selected_availability = [row for row in availability if row["code"].endswith("_residual_source_closure_20260626")]
    if len(selected_availability) != 1:
        raise ClosureError(f"expected one imported availability row, found {len(selected_availability)}")
    reviews = review_payloads()
    for source, expected in reviews.items():
        actual = read_json(SOURCE_METADATA[source]["review"])
        if actual != expected:
            raise ClosureError(f"stale source review: {source}")
    analysis_payload = missing_analysis.collect(ROOT)
    stored_analysis = read_json(REPORTING / "existing_configuration_missing_data_analysis.json")
    if stored_analysis != analysis_payload:
        raise ClosureError("missing-data analysis is stale")
    summary = analysis_payload["summary"]
    if summary["eligible_candidate_count"] != 0 or analysis_payload["selected_next_package"] is not None:
        raise ClosureError("eligible source candidates remain")
    state = read_json(STATE)
    if state["current_package"]["package_id"] != "sandero_residual_source_closure_006":
        raise ClosureError("project state is not advanced to this package")
    print("Sandero residual source closure: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if not args.check:
            apply()
        check()
    except (ClosureError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
