#!/usr/bin/env python3
"""Import exact Stepway Essential source-gap observations dated 2026-06-26."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable, Sequence

from tools import existing_configuration_missing_data_analysis as analysis

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"
REPORTING = ROOT / "data" / "reporting"
SPEC = ROOT / "data" / "imports" / "sandero_stepway_essential_source_gap_20260626.csv"
VALUE_OUTPUT = MASTER / "configuration_attribute_values.csv"
RANGE_OUTPUT = MASTER / "configuration_attribute_value_ranges.csv"
GENERAL_SCOPE = REPORTING / "configuration_completeness.json"
MANUAL_SCOPE = REPORTING / "sandero_ecog120_manual_completeness.json"
REVIEW_JSON = REPORTING / "sandero_stepway_essential_source_gap_review.json"
REVIEW_MD = REPORTING / "sandero_stepway_essential_source_gap_review.md"
PACKAGE = ROOT / "project" / "packages" / "sandero-stepway-essential-source-gap-20260801.md"
STATE = ROOT / "project" / "state.json"
SOURCE = ROOT / "PDF" / "Cenniki" / "NOWE SANDERO STEPWAY essential stepway Eco-G 120 f.pdf"
SOURCE_CODE = "src_pl_sandero_stepway_essential_ecog120_mt_20260626"
SOURCE_SHA256 = "14dbd68fc58d63bc81595f64784e37081ef25ed0103e2a74768477e602b29ea1"
OBSERVATION_DATE = "2026-06-26"
CONFIGURATION = "sandero_stepway_iii_essential_ecog120_manual"
MODEL_CODE = "sandero"
EXHAUSTED_CLASSIFICATION = "source_exhausted_not_stated"
SCOPES = (GENERAL_SCOPE, MANUAL_SCOPE)
SPEC_FIELDS = (
    "record_type",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "value",
    "minimum_value",
    "maximum_value",
    "source_page",
    "source_label",
    "normalization_notes",
)
VALUE_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "gear_number",
    "value",
    "observation_date",
    "source_code",
    "notes",
)
RANGE_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "minimum_value",
    "maximum_value",
    "lower_inclusive",
    "upper_inclusive",
    "observation_date",
    "source_code",
    "notes",
)
EXPECTED_VALUE_FIRST_ID = 3553
EXPECTED_VALUE_LAST_ID = 3555
EXPECTED_RANGE_FIRST_ID = 302
EXPECTED_RANGE_LAST_ID = 304
EXPECTED_SPEC = {
    ("value", "overall_height", "", "1586", "", ""),
    ("value", "overall_width_with_mirrors", "", "2012", "", ""),
    ("value", "wheel_finish", "", "stalowe", "", ""),
    ("range", "ground_clearance", "", "", "170", "200"),
    ("range", "max_torque_rpm", "lpg", "", "1750", "3750"),
    ("range", "max_torque_rpm", "petrol", "", "2000", "4000"),
}
REMAINING_SLOTS = (
    {"attribute_code": "front_track", "fuel_type_code": "", "reason": "not_stated_in_source"},
    {"attribute_code": "max_power_rpm", "fuel_type_code": "lpg", "reason": "not_stated_in_source"},
    {"attribute_code": "max_power_rpm", "fuel_type_code": "petrol", "reason": "not_stated_in_source"},
    {"attribute_code": "rear_track", "fuel_type_code": "", "reason": "not_stated_in_source"},
)
MANIFEST_PATHS = [
    "data/reporting/configuration_gap_evidence.json",
    "data/reporting/configuration_gap_resolution_plan.json",
    "tests/configuration_comparison_context_filter_contract.py",
    "tests/configuration_comparison_pair_summary_contract.py",
    "tests/test_duster_ecog120_reporting_scope.py",
    "data/reporting/configuration_gap_source_review.json",
    "tests/test_sandero_ecog120_manual_reporting_scope.py",
    "data/reporting/sandero_ecog120_manual_gap_evidence.json",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
    "tests/test_configuration_value_ranges.py",
    "tests/test_jogger_payload_performance_ranges.py",
    "tests/test_official_brochure_residual_evidence_review.py",
    "tests/test_spring_technical_20260219.py",
    "tools/close_stepway_essential_reporting_dependencies_20260801.py",
    "tools/review_official_brochure_residual_evidence_20260726.py",
    "data/imports/sandero_stepway_essential_source_gap_20260626.csv",
    "data/master/configuration_attribute_value_ranges.csv",
    "data/master/configuration_attribute_values.csv",
    "data/reporting/configuration_completeness.json",
    "data/reporting/existing_configuration_missing_data_analysis.json",
    "data/reporting/existing_configuration_missing_data_analysis.md",
    "data/reporting/sandero_ecog120_manual_completeness.json",
    "data/reporting/sandero_stepway_essential_source_gap_review.json",
    "data/reporting/sandero_stepway_essential_source_gap_review.md",
    "project/STATE_SUMMARY.md",
    "project/packages/sandero-stepway-essential-source-gap-20260801.md",
    "project/state.json",
    "tests/test_existing_configuration_missing_data_analysis.py",
    "tests/test_sandero_stepway_essential_source_gap_20260626.py",
    "tools/import_sandero_stepway_essential_source_gap_20260626.py",
]


class ContractError(RuntimeError):
    """Raised when the exact source-gap import contract cannot be reproduced."""


def read_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ContractError(f"missing CSV header: {path}")
            return [dict(row) for row in reader]
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def require_header(path: Path, fields: Sequence[str]) -> None:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle), None)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot inspect {path}: {exc}") from exc
    if header != list(fields):
        raise ContractError(f"unexpected header in {path}: {header!r}")


def write_csv(path: Path, rows: list[dict[str, str]], fields: Sequence[str]) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot read source {path}: {exc}") from exc
    return digest.hexdigest()


def load_spec(*, validate_repository: bool = True) -> list[dict[str, str]]:
    require_header(SPEC, SPEC_FIELDS)
    rows = read_rows(SPEC)
    if len(rows) != 6:
        raise ContractError(f"expected 6 specification rows, found {len(rows)}")
    actual = {
        (
            row["record_type"],
            row["attribute_code"],
            row["fuel_type_code"],
            row["value"],
            row["minimum_value"],
            row["maximum_value"],
        )
        for row in rows
    }
    if actual != EXPECTED_SPEC:
        raise ContractError(f"source-gap specification differs from exact contract: {actual!r}")
    identities: set[tuple[str, str, str]] = set()
    for row in rows:
        if row["configuration_code"] != CONFIGURATION:
            raise ContractError(f"out-of-scope configuration: {row['configuration_code']}")
        identity = (row["attribute_code"], row["fuel_type_code"], row["record_type"])
        if identity in identities:
            raise ContractError(f"duplicate specification identity: {identity}")
        identities.add(identity)
        if row["record_type"] not in {"value", "range"}:
            raise ContractError(f"unsupported record type: {row['record_type']}")
        if not row["source_page"].isdigit() or not row["source_label"].strip():
            raise ContractError(f"missing exact page or label: {identity}")
        if row["record_type"] == "value":
            if not row["value"] or row["minimum_value"] or row["maximum_value"]:
                raise ContractError(f"invalid scalar row: {identity}")
        else:
            if row["value"] or not row["minimum_value"] or not row["maximum_value"]:
                raise ContractError(f"invalid range row: {identity}")
            if float(row["minimum_value"]) > float(row["maximum_value"]):
                raise ContractError(f"reversed range: {identity}")
    if validate_repository:
        verify_repository_contract(rows)
    return rows


def verify_repository_contract(spec_rows: Iterable[dict[str, str]]) -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source PDF SHA-256 mismatch: {SOURCE}")
    configurations = {row["code"]: row for row in read_rows(MASTER / "configurations.csv")}
    configuration = configurations.get(CONFIGURATION)
    if configuration is None or configuration.get("status") != "active":
        raise ContractError(f"missing active configuration: {CONFIGURATION}")
    links = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    if (SOURCE_CODE, CONFIGURATION) not in links:
        raise ContractError(f"source does not document configuration: {CONFIGURATION}")
    attributes = {row["code"]: row for row in read_rows(MASTER / "attributes.csv")}
    for row in spec_rows:
        attribute = attributes.get(row["attribute_code"])
        if attribute is None or attribute.get("status") != "active":
            raise ContractError(f"missing active attribute: {row['attribute_code']}")


def note(row: dict[str, str]) -> str:
    text = f"Source page {row['source_page']}: {row['source_label']}."
    normalization = row["normalization_notes"].strip()
    return f"{text} {normalization}" if normalization else text


def row_code(row: dict[str, str]) -> str:
    fuel = f"_{row['fuel_type_code']}" if row["fuel_type_code"] else ""
    suffix = "_range" if row["record_type"] == "range" else ""
    return f"{CONFIGURATION}_{row['attribute_code']}{fuel}{suffix}_source_gap_20260626"


def generated_value_rows(spec_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "code": row_code(row),
            "configuration_code": CONFIGURATION,
            "attribute_code": row["attribute_code"],
            "fuel_type_code": row["fuel_type_code"],
            "gear_number": "",
            "value": row["value"],
            "observation_date": OBSERVATION_DATE,
            "source_code": SOURCE_CODE,
            "notes": note(row),
        }
        for row in spec_rows
        if row["record_type"] == "value"
    ]


def generated_range_rows(spec_rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "code": row_code(row),
            "configuration_code": CONFIGURATION,
            "attribute_code": row["attribute_code"],
            "fuel_type_code": row["fuel_type_code"],
            "minimum_value": row["minimum_value"],
            "maximum_value": row["maximum_value"],
            "lower_inclusive": "true",
            "upper_inclusive": "true",
            "observation_date": OBSERVATION_DATE,
            "source_code": SOURCE_CODE,
            "notes": note(row),
        }
        for row in spec_rows
        if row["record_type"] == "range"
    ]


def semantic(rows: Iterable[dict[str, str]], fields: Sequence[str]) -> list[tuple[str, ...]]:
    return sorted(tuple(row.get(field, "") for field in fields) for row in rows)


def selected_by_codes(rows: Iterable[dict[str, str]], codes: set[str]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("code") in codes]


def append_exact(
    path: Path,
    fields: Sequence[str],
    generated: list[dict[str, str]],
    expected_first_id: int,
) -> None:
    require_header(path, fields)
    current = read_rows(path)
    codes = {row["code"] for row in generated}
    actual = selected_by_codes(current, codes)
    if actual:
        if len(actual) != len(generated):
            raise ContractError(f"partial source-gap observations already exist in {path}")
        if semantic(actual, fields[1:]) != semantic(generated, fields[1:]):
            raise ContractError(f"conflicting source-gap observations already exist in {path}")
        return
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError(f"non-integer IDs in {path}") from exc
    if maximum_id != expected_first_id - 1:
        raise ContractError(
            f"expected suffix after {expected_first_id - 1} in {path}, found {maximum_id}"
        )
    output = current + [
        {"id": str(maximum_id + offset), **row}
        for offset, row in enumerate(generated, start=1)
    ]
    write_csv(path, output, fields)


def scope_payload(path: Path, values: list[dict[str, str]]) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    matched: dict[str, int] = {"lpg": 0, "petrol": 0}
    for slot in payload.get("technical_slots", []):
        if not isinstance(slot, dict):
            continue
        if slot.get("attribute_code") != "elasticity_80_120":
            continue
        fuel = str(slot.get("fuel_type_code", ""))
        if fuel not in matched:
            continue
        gear = str(slot.get("gear_number", ""))
        if gear not in {"", "4"}:
            raise ContractError(f"unexpected elasticity gear in {path}: {fuel}/{gear}")
        slot["gear_number"] = "4"
        matched[fuel] += 1
    if matched != {"lpg": 1, "petrol": 1}:
        raise ContractError(f"unexpected elasticity slot distribution in {path}: {matched}")
    available = {
        (
            row["configuration_code"],
            row["attribute_code"],
            row["fuel_type_code"],
            row["gear_number"],
        )
        for row in values
    }
    for ref in payload.get("configurations", []):
        code = ref if isinstance(ref, str) else str(ref.get("configuration_code", ""))
        for fuel in ("lpg", "petrol"):
            key = (code, "elasticity_80_120", fuel, "4")
            if key not in available:
                raise ContractError(f"missing exact fourth-gear observation required by {path}: {key}")
    return payload


def review_payload() -> dict[str, object]:
    return {
        "version": 1,
        "as_of": "2026-08-01",
        "kind": "configuration_source_gap_review",
        "model_code": MODEL_CODE,
        "configuration_code": CONFIGURATION,
        "source_code": SOURCE_CODE,
        "source_path": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": SOURCE_SHA256,
        "source_observation_date": OBSERVATION_DATE,
        "initial_gap": {
            "reported_records": 24,
            "unique_slots": 12,
            "scope_files": [path.name for path in SCOPES],
        },
        "resolution": {
            "scalar_values": [
                {"attribute_code": "overall_height", "value": "1586", "source_page": 6},
                {"attribute_code": "overall_width_with_mirrors", "value": "2012", "source_page": 6},
                {"attribute_code": "wheel_finish", "value": "stalowe", "source_page": 2},
            ],
            "ranges": [
                {"attribute_code": "ground_clearance", "fuel_type_code": "", "minimum_value": "170", "maximum_value": "200", "source_page": 6},
                {"attribute_code": "max_torque_rpm", "fuel_type_code": "lpg", "minimum_value": "1750", "maximum_value": "3750", "source_page": 5},
                {"attribute_code": "max_torque_rpm", "fuel_type_code": "petrol", "minimum_value": "2000", "maximum_value": "4000", "source_page": 5},
            ],
            "reporting_context_corrections": [
                {
                    "attribute_code": "elasticity_80_120",
                    "fuel_type_code": "lpg",
                    "gear_number": "4",
                    "evidence_source_code": "src_pl_sandero_stepway_brochure_20260202",
                },
                {
                    "attribute_code": "elasticity_80_120",
                    "fuel_type_code": "petrol",
                    "gear_number": "4",
                    "evidence_source_code": "src_pl_sandero_stepway_brochure_20260202",
                },
            ],
        },
        "excluded_alternatives": [
            {"attribute_code": "overall_height", "value": "1535", "reason": "Stepway height without roof rails does not describe the exact standard configuration"},
            {"attribute_code": "overall_width_with_mirrors", "value": "1853", "reason": "folded-mirror width is outside the repository comparison convention"},
            {"attribute_code": "wheel_design", "value": "ERALIA", "reason": "already represented by an existing exact observation"},
        ],
        "reconciliation": {
            "classification": EXHAUSTED_CLASSIFICATION,
            "resolved_unique_slots": 8,
            "remaining_unique_slots": 4,
            "remaining_slots": list(REMAINING_SLOTS),
            "boundary": "No track widths or maximum-power engine speeds are printed in the source; no values are inferred from sibling trims, diagrams or other documents.",
        },
    }


def render_review_markdown(payload: dict[str, object]) -> str:
    return (
        "# Sandero Stepway Essential Source-Gap Review\n\n"
        "Status: complete\n\n"
        f"Source `{SOURCE_CODE}` was inspected page by page against the 24 reported "
        "scope records for `sandero_stepway_iii_essential_ecog120_manual`. The two "
        "scope records describe 12 unique slots.\n\n"
        "## Imported observations\n\n"
        "- `overall_height = 1586 mm` for the exact standard configuration with roof rails.\n"
        "- `overall_width_with_mirrors = 2012 mm` with mirrors unfolded, matching the repository convention.\n"
        "- `wheel_finish = stalowe`; ERALIA remains the separate existing wheel-design observation.\n"
        "- `ground_clearance = 170-200 mm`.\n"
        "- `max_torque_rpm = 1750-3750` for LPG and `2000-4000` for petrol.\n\n"
        "## Reporting correction\n\n"
        "Both Sandero completeness scopes now identify `elasticity_80_120` as a "
        "fourth-gear measurement. Existing values retain their original February "
        "2026 brochure evidence; the June price PDF is not credited with elasticity data.\n\n"
        "## Remaining boundary\n\n"
        "`front_track`, `rear_track`, and `max_power_rpm` for LPG and petrol are not "
        "stated in this PDF. The source is therefore classified "
        "`source_exhausted_not_stated` after the six exact imports and the slot-context correction.\n"
    )


def package_text() -> str:
    return (
        "# Sandero Stepway Essential Source Gap\n\n"
        "Status: complete\n\n"
        "Imported three exact scalar observations and three inclusive ranges from "
        "the configuration-specific Polish PDF dated 2026-06-26. Restored fourth-gear "
        "identity for elasticity slots in two completeness scopes, regenerated the "
        "missing-data analysis and formally exhausted the source for the four slots "
        "it does not state.\n\n"
        "No value was projected from another trim, fuel, diagram or document. Alternative "
        "no-rails and folded-mirror dimensions remain excluded, and existing ERALIA "
        "wheel-design evidence is not duplicated.\n"
    )


def update_analysis_outputs() -> dict[str, object]:
    payload = analysis.collect(ROOT)
    write_json(analysis.OUT_JSON, payload)
    analysis.OUT_MD.write_text(analysis.render_markdown(payload), encoding="utf-8")
    return payload


def update_state(analysis_payload: dict[str, object]) -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["phase"] = "Sandero Stepway Essential Source Gap"
    state["current_package"] = {
        "package_id": "sandero_stepway_essential_source_gap_001",
        "kind": "source_backed_completeness_import",
        "name": "Sandero Stepway Essential Source Gap",
        "status": "complete",
        "goal": "Resolve every safely representable missing slot from the exact Stepway Essential Eco-G 120 manual source and formally preserve the remaining not-stated boundary.",
        "manifest_paths": MANIFEST_PATHS,
    }
    selected = analysis_payload.get("selected_next_package")
    if selected:
        model = str(selected["model_code"])
        source = str(selected["source_code"])
        state["next_package"] = {
            "package_id": f"{analysis.slug(model)}_highest_impact_eligible_gap_002",
            "kind": "source_backed_completeness_import",
            "name": f"{model} Highest-Impact Eligible Source Gap",
            "status": "planned",
            "goal": f"Inspect exact missing slots for {model} against source {source or 'mapping to be resolved'} and import only directly stated values or explicit non-applicable classifications.",
            "manifest_paths": [],
        }
    else:
        state["next_package"] = {
            "package_id": "data_products_v1_10_0_release_preparation_001",
            "kind": "release_preparation",
            "name": "Data Products v1.10.0 Release Preparation",
            "status": "planned",
            "goal": "Prepare the next immutable release candidate from the completed source-backed data series.",
            "manifest_paths": [],
        }
    write_json(STATE, state)


def apply() -> None:
    spec = load_spec()
    values = generated_value_rows(spec)
    ranges = generated_range_rows(spec)
    append_exact(VALUE_OUTPUT, VALUE_FIELDS, values, EXPECTED_VALUE_FIRST_ID)
    append_exact(RANGE_OUTPUT, RANGE_FIELDS, ranges, EXPECTED_RANGE_FIRST_ID)
    all_values = read_rows(VALUE_OUTPUT)
    for path in SCOPES:
        write_json(path, scope_payload(path, all_values))
    review = review_payload()
    write_json(REVIEW_JSON, review)
    REVIEW_MD.write_text(render_review_markdown(review), encoding="utf-8")
    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE.write_text(package_text(), encoding="utf-8")
    analysis_payload = update_analysis_outputs()
    update_state(analysis_payload)


def verify_materialized() -> None:
    spec = load_spec()
    expected_values = generated_value_rows(spec)
    expected_ranges = generated_range_rows(spec)
    require_header(VALUE_OUTPUT, VALUE_FIELDS)
    require_header(RANGE_OUTPUT, RANGE_FIELDS)
    values = selected_by_codes(read_rows(VALUE_OUTPUT), {row["code"] for row in expected_values})
    ranges = selected_by_codes(read_rows(RANGE_OUTPUT), {row["code"] for row in expected_ranges})
    if semantic(values, VALUE_FIELDS[1:]) != semantic(expected_values, VALUE_FIELDS[1:]):
        raise ContractError("stored scalar observations differ from generated contract")
    if semantic(ranges, RANGE_FIELDS[1:]) != semantic(expected_ranges, RANGE_FIELDS[1:]):
        raise ContractError("stored range observations differ from generated contract")
    value_ids = sorted(int(row["id"]) for row in values)
    range_ids = sorted(int(row["id"]) for row in ranges)
    if value_ids != list(range(EXPECTED_VALUE_FIRST_ID, EXPECTED_VALUE_LAST_ID + 1)):
        raise ContractError("scalar IDs are not the exact contiguous suffix 3553-3555")
    if range_ids != list(range(EXPECTED_RANGE_FIRST_ID, EXPECTED_RANGE_LAST_ID + 1)):
        raise ContractError("range IDs are not the exact contiguous suffix 302-304")
    all_values = read_rows(VALUE_OUTPUT)
    for path in SCOPES:
        expected_scope = scope_payload(path, all_values)
        actual_scope = json.loads(path.read_text(encoding="utf-8"))
        if actual_scope != expected_scope:
            raise ContractError(f"scope output differs from exact context contract: {path}")
    expected_review = review_payload()
    if json.loads(REVIEW_JSON.read_text(encoding="utf-8")) != expected_review:
        raise ContractError("source-gap review JSON differs from generated contract")
    if REVIEW_MD.read_text(encoding="utf-8") != render_review_markdown(expected_review):
        raise ContractError("source-gap review Markdown differs from generated contract")
    if PACKAGE.read_text(encoding="utf-8") != package_text():
        raise ContractError("package record differs from generated contract")
    expected_analysis = analysis.collect(ROOT)
    if json.loads(analysis.OUT_JSON.read_text(encoding="utf-8")) != expected_analysis:
        raise ContractError("missing-data analysis JSON is stale")
    if analysis.OUT_MD.read_text(encoding="utf-8") != analysis.render_markdown(expected_analysis):
        raise ContractError("missing-data analysis Markdown is stale")
    summary = expected_analysis["summary"]
    if summary["missing_technical_count"] != 81:
        raise ContractError(f"expected 81 remaining technical records, found {summary['missing_technical_count']}")
    if summary["exhausted_source_candidate_count"] != 7:
        raise ContractError("expected exactly 7 exhausted-source candidates")
    current = next(
        item for item in expected_analysis["ranked_candidates"]
        if item["source_code"] == SOURCE_CODE
    )
    if current["missing_technical"] != 8 or current["selection_status"] != EXHAUSTED_CLASSIFICATION:
        raise ContractError(f"unexpected post-review source candidate: {current}")
    selected = expected_analysis.get("selected_next_package")
    if (
        selected is not None
        or expected_analysis["summary"]["eligible_candidate_count"] != 0
    ):
        raise ContractError(
            f"analysis should have no eligible source after residual closure: {selected}"
        )
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if int(state["baseline"]["configuration_values"]) < EXPECTED_VALUE_LAST_ID:
        raise ContractError("project state baseline predates the completed package")
    print("Stepway Essential source-gap observations: PASS (3 values + 3 ranges + 2 scope corrections)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        verify_materialized()
    else:
        apply()
        verify_materialized()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
