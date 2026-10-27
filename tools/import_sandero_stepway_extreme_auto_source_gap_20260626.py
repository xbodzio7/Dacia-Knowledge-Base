#!/usr/bin/env python3
"""Import exact Stepway Extreme automatic source-gap observations dated 2026-06-26."""
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
SPEC = ROOT / "data" / "imports" / "sandero_stepway_extreme_auto_source_gap_20260626.csv"
VALUE_OUTPUT = MASTER / "configuration_attribute_values.csv"
RANGE_OUTPUT = MASTER / "configuration_attribute_value_ranges.csv"
AVAILABILITY_OUTPUT = MASTER / "configuration_attribute_availability.csv"
REVIEW_JSON = REPORTING / "sandero_stepway_extreme_auto_source_gap_review.json"
REVIEW_MD = REPORTING / "sandero_stepway_extreme_auto_source_gap_review.md"
PACKAGE = ROOT / "project" / "packages" / "sandero-stepway-extreme-auto-source-gap-20260801.md"
STATE = ROOT / "project" / "state.json"
SOURCE = ROOT / "PDF" / "Cenniki" / "NOWE SANDERO STEPWAY extreme stepway Eco-G 120 auto f.pdf"
SOURCE_CODE = "src_pl_sandero_stepway_extreme_ecog120_at_20260626"
SOURCE_SHA256 = "a519c2002231cd28f92999c2d8af76fb5c58e6129ac6d5521c6436e471349aff"
OBSERVATION_DATE = "2026-06-26"
CONFIGURATION = "sandero_stepway_iii_extreme_ecog120_automatic"
MODEL_CODE = "sandero"
EXHAUSTED_CLASSIFICATION = "source_exhausted_not_stated"
SPEC_FIELDS = (
    "record_type",
    "configuration_code",
    "attribute_code",
    "fuel_type_code",
    "value",
    "minimum_value",
    "maximum_value",
    "availability_status",
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
AVAILABILITY_FIELDS = (
    "id",
    "code",
    "configuration_code",
    "attribute_code",
    "availability_status",
    "observation_date",
    "source_code",
    "notes",
)
EXPECTED_VALUE_FIRST_ID = 3564
EXPECTED_VALUE_LAST_ID = 3565
EXPECTED_RANGE_FIRST_ID = 314
EXPECTED_RANGE_LAST_ID = 316
EXPECTED_AVAILABILITY_FIRST_ID = 5905
EXPECTED_AVAILABILITY_LAST_ID = 5905
EXPECTED_SPEC = {
    ("value", "overall_height", "", "1586", "", "", ""),
    ("value", "overall_width_with_mirrors", "", "2012", "", "", ""),
    ("range", "ground_clearance", "", "", "170", "200", ""),
    ("range", "max_torque_rpm", "lpg", "", "1750", "3750", ""),
    ("range", "max_torque_rpm", "petrol", "", "2000", "4000", ""),
    ("availability", "parking_assist_system", "", "", "", "", "standard"),
}
REMAINING_TECHNICAL = (
    {"attribute_code": "front_track", "fuel_type_code": "", "reason": "not_stated_in_source"},
    {"attribute_code": "rear_track", "fuel_type_code": "", "reason": "not_stated_in_source"},
    {"attribute_code": "max_power_rpm", "fuel_type_code": "lpg", "reason": "not_stated_in_source"},
    {"attribute_code": "max_power_rpm", "fuel_type_code": "petrol", "reason": "not_stated_in_source"},
    {"attribute_code": "elasticity_80_120", "fuel_type_code": "lpg", "reason": "not_stated_in_source"},
    {"attribute_code": "elasticity_80_120", "fuel_type_code": "petrol", "reason": "not_stated_in_source"},
)
REMAINING_EQUIPMENT = (
    {"attribute_code": "gear_shift_indicator", "reason": "out_of_scope_for_automatic_transmission"},
)
MANIFEST_PATHS = [
    "data/imports/sandero_stepway_extreme_auto_source_gap_20260626.csv",
    "data/master/configuration_attribute_availability.csv",
    "data/master/configuration_attribute_value_ranges.csv",
    "data/master/configuration_attribute_values.csv",
    "data/reporting/configuration_gap_evidence.json",
    "data/reporting/configuration_gap_resolution_plan.json",
    "data/reporting/configuration_gap_source_review.json",
    "data/reporting/existing_configuration_missing_data_analysis.json",
    "data/reporting/existing_configuration_missing_data_analysis.md",
    "data/reporting/sandero_stepway_ecog120_automatic_completeness.json",
    "data/reporting/sandero_stepway_ecog120_automatic_gap_evidence.json",
    "data/reporting/sandero_stepway_extreme_auto_source_gap_review.json",
    "data/reporting/sandero_stepway_extreme_auto_source_gap_review.md",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.json",
    "data/reporting/verified_pdf_candidate_coverage_reconciliation.md",
    "project/STATE_SUMMARY.md",
    "project/packages/sandero-stepway-extreme-auto-source-gap-20260801.md",
    "project/state.json",
    "tests/test_sandero_stepway_ecog120_automatic_reporting_scope.py",
    "tests/test_sandero_stepway_extreme_auto_source_gap_20260626.py",
    "tools/align_sandero_stepway_expression_auto_snapshot_contracts_20260801.py",
    "tools/close_stepway_expression_auto_reporting_dependencies_20260801.py",
    "tools/import_sandero_stepway_extreme_auto_source_gap_20260626.py",
]


class ContractError(RuntimeError):
    """Raised when the exact source-gap package cannot be reproduced."""


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
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
            row["availability_status"],
        )
        for row in rows
    }
    if actual != EXPECTED_SPEC:
        raise ContractError(
            f"source-gap specification differs from exact contract: {actual!r}"
        )
    identities: set[tuple[str, str, str]] = set()
    for row in rows:
        if row["configuration_code"] != CONFIGURATION:
            raise ContractError(f"out-of-scope configuration: {row['configuration_code']}")
        identity = (
            row["attribute_code"],
            row["fuel_type_code"],
            row["record_type"],
        )
        if identity in identities:
            raise ContractError(f"duplicate specification identity: {identity}")
        identities.add(identity)
        if row["record_type"] not in {"value", "range", "availability"}:
            raise ContractError(f"unsupported record type: {row['record_type']}")
        if not row["source_page"].isdigit() or not row["source_label"].strip():
            raise ContractError(f"missing exact page or label: {identity}")
        if row["record_type"] == "value":
            if (
                not row["value"]
                or row["minimum_value"]
                or row["maximum_value"]
                or row["availability_status"]
            ):
                raise ContractError(f"invalid scalar row: {identity}")
        elif row["record_type"] == "range":
            if (
                row["value"]
                or not row["minimum_value"]
                or not row["maximum_value"]
                or row["availability_status"]
            ):
                raise ContractError(f"invalid range row: {identity}")
            if float(row["minimum_value"]) > float(row["maximum_value"]):
                raise ContractError(f"reversed range: {identity}")
        elif (
            row["value"]
            or row["minimum_value"]
            or row["maximum_value"]
            or row["availability_status"] != "standard"
        ):
            raise ContractError(f"invalid availability row: {identity}")
    if validate_repository:
        verify_repository_contract(rows)
    return rows


def verify_repository_contract(spec_rows: Iterable[dict[str, str]]) -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ContractError(f"source PDF SHA-256 mismatch: {SOURCE}")
    configurations = {
        row["code"]: row for row in read_rows(MASTER / "configurations.csv")
    }
    configuration = configurations.get(CONFIGURATION)
    if configuration is None or configuration.get("status") != "active":
        raise ContractError(f"missing active configuration: {CONFIGURATION}")
    links = {
        (row["source_code"], row["configuration_code"])
        for row in read_rows(MASTER / "source_configurations.csv")
    }
    if (SOURCE_CODE, CONFIGURATION) not in links:
        raise ContractError(f"source does not document configuration: {CONFIGURATION}")
    attributes = {
        row["code"]: row for row in read_rows(MASTER / "attributes.csv")
    }
    for row in spec_rows:
        attribute = attributes.get(row["attribute_code"])
        if attribute is None or attribute.get("status") != "active":
            raise ContractError(f"missing active attribute: {row['attribute_code']}")
        if row["record_type"] == "availability" and attribute.get("data_type") != "boolean":
            raise ContractError(
                f"availability requires boolean attribute: {row['attribute_code']}"
            )


def note(row: dict[str, str]) -> str:
    text = f"Source page {row['source_page']}: {row['source_label']}."
    normalization = row["normalization_notes"].strip()
    return f"{text} {normalization}" if normalization else text


def row_code(row: dict[str, str]) -> str:
    fuel = f"_{row['fuel_type_code']}" if row["fuel_type_code"] else ""
    if row["record_type"] == "range":
        suffix = "_range"
    elif row["record_type"] == "availability":
        suffix = "_availability"
    else:
        suffix = ""
    return (
        f"{CONFIGURATION}_{row['attribute_code']}{fuel}{suffix}"
        "_source_gap_20260626"
    )


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


def generated_availability_rows(
    spec_rows: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "code": row_code(row),
            "configuration_code": CONFIGURATION,
            "attribute_code": row["attribute_code"],
            "availability_status": row["availability_status"],
            "observation_date": OBSERVATION_DATE,
            "source_code": SOURCE_CODE,
            "notes": note(row),
        }
        for row in spec_rows
        if row["record_type"] == "availability"
    ]


def semantic(
    rows: Iterable[dict[str, str]], fields: Sequence[str]
) -> list[tuple[str, ...]]:
    return sorted(
        tuple(row.get(field, "") for field in fields) for row in rows
    )


def selected_by_codes(
    rows: Iterable[dict[str, str]], codes: set[str]
) -> list[dict[str, str]]:
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
        if (
            len(actual) != len(generated)
            or semantic(actual, fields[1:]) != semantic(generated, fields[1:])
        ):
            raise ContractError(
                f"partial or conflicting source-gap observations already exist in {path}"
            )
        return
    try:
        maximum_id = max(int(row["id"]) for row in current)
    except (KeyError, ValueError) as exc:
        raise ContractError(f"non-integer IDs in {path}") from exc
    if maximum_id != expected_first_id - 1:
        raise ContractError(
            f"expected suffix after {expected_first_id - 1} in {path}, "
            f"found {maximum_id}"
        )
    output = current + [
        {"id": str(maximum_id + offset), **row}
        for offset, row in enumerate(generated, start=1)
    ]
    write_csv(path, output, fields)


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
            "reviewed_unique_slots": 13,
            "technical_slots": 11,
            "equipment_slots": 2,
        },
        "resolution": {
            "scalar_values": [
                {"attribute_code": "overall_height", "value": "1586", "source_page": 6},
                {"attribute_code": "overall_width_with_mirrors", "value": "2012", "source_page": 6},
            ],
            "ranges": [
                {"attribute_code": "ground_clearance", "fuel_type_code": "", "minimum_value": "170", "maximum_value": "200", "source_page": 6},
                {"attribute_code": "max_torque_rpm", "fuel_type_code": "lpg", "minimum_value": "1750", "maximum_value": "3750", "source_page": 6},
                {"attribute_code": "max_torque_rpm", "fuel_type_code": "petrol", "minimum_value": "2000", "maximum_value": "4000", "source_page": 6},
            ],
            "availability": [
                {"attribute_code": "parking_assist_system", "availability_status": "standard", "source_page": 4}
            ],
        },
        "preserved_out_of_scope": [
            {
                "attribute_code": "gear_shift_indicator",
                "reason": "The canonical decision already classifies the manual gear-shift indicator outside the automatic-transmission scope.",
            }
        ],
        "excluded_alternatives": [
            {"attribute_code": "overall_height", "value": "1535", "reason": "Stepway height without roof rails does not describe the exact standard configuration"},
            {"attribute_code": "overall_width_with_mirrors", "value": "1853", "reason": "folded-mirror width is outside the repository comparison convention"},
        ],
        "reconciliation": {
            "classification": EXHAUSTED_CLASSIFICATION,
            "resolved_unique_slots": 6,
            "preserved_out_of_scope_slots": 1,
            "remaining_unique_slots": 6,
            "remaining_technical_slots": list(REMAINING_TECHNICAL),
            "remaining_equipment_slots": list(REMAINING_EQUIPMENT),
            "boundary": (
                "The source does not state front/rear track widths, maximum-power engine speeds or 80-120 km/h elasticity. "
                "The manual gear-shift indicator remains outside the automatic-transmission scope."
            ),
        },
    }


def render_review_markdown(payload: dict[str, object]) -> str:
    return (
        "# Sandero Stepway Extreme Automatic Source-Gap Review\n\n"
        "Status: complete\n\n"
        f"Source `{SOURCE_CODE}` was inspected page by page against 13 unique gap decisions for `{CONFIGURATION}`.\n\n"
        "## Imported observations\n\n"
        "- `overall_height = 1586 mm` for the exact standard configuration with roof rails.\n"
        "- `overall_width_with_mirrors = 2012 mm` with mirrors unfolded.\n"
        "- `ground_clearance = 170-200 mm`.\n"
        "- `max_torque_rpm = 1750-3750` for LPG and `2000-4000` for petrol.\n"
        "- `parking_assist_system = standard`, based on the direct front/rear parking-assistance statement.\n\n"
        "## Preserved boundaries\n\n"
        "`front_track`, `rear_track`, both `max_power_rpm` contexts and both `elasticity_80_120` contexts are not stated. "
        "`gear_shift_indicator` remains explicitly outside the automatic-transmission scope. No value is projected from a manual sibling configuration.\n"
    )


def package_text() -> str:
    return (
        "# Sandero Stepway Extreme Automatic Source Gap\n\n"
        "Status: complete\n\n"
        "Imported two exact scalar observations, three inclusive ranges and one standard equipment observation from the configuration-specific Polish PDF dated 2026-06-26. "
        "The source is formally exhausted for six unstated technical slots; the gear-shift indicator remains outside the automatic-transmission scope.\n\n"
        "No value or availability state was projected from another trim or transmission.\n"
    )


def update_analysis_outputs() -> dict[str, object]:
    payload = analysis.collect(ROOT)
    write_json(analysis.OUT_JSON, payload)
    analysis.OUT_MD.write_text(
        analysis.render_markdown(payload), encoding="utf-8"
    )
    return payload


def update_state(analysis_payload: dict[str, object]) -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["phase"] = "Sandero Stepway Extreme Automatic Source Gap"
    state["current_package"] = {
        "package_id": "sandero_stepway_extreme_auto_source_gap_005",
        "kind": "source_backed_completeness_import",
        "name": "Sandero Stepway Extreme Automatic Source Gap",
        "status": "complete",
        "goal": (
            "Resolve every safely representable missing slot from the exact Stepway Extreme Eco-G 120 automatic source and preserve not-stated and automatic-transmission boundaries."
        ),
        "manifest_paths": MANIFEST_PATHS,
    }
    selected = analysis_payload.get("selected_next_package")
    if selected:
        model = str(selected["model_code"])
        source = str(selected["source_code"])
        state["next_package"] = {
            "package_id": f"{analysis.slug(model)}_highest_impact_eligible_gap_006",
            "kind": "source_backed_completeness_import",
            "name": f"{model} Highest-Impact Eligible Source Gap",
            "status": "planned",
            "goal": (
                f"Inspect exact missing slots for {model} against source {source or 'mapping to be resolved'} and import only directly stated values or explicit non-applicable classifications."
            ),
            "manifest_paths": [],
        }
    else:
        state["next_package"] = {
            "package_id": "configuration_gap_closure_documentation_milestone_001",
            "kind": "documentation_milestone",
            "name": "Configuration Gap Closure Documentation Milestone",
            "status": "planned",
            "goal": "Record the completed source-backed configuration-gap closure series.",
            "manifest_paths": [],
        }
    write_json(STATE, state)


def apply() -> None:
    spec = load_spec()
    append_exact(
        VALUE_OUTPUT,
        VALUE_FIELDS,
        generated_value_rows(spec),
        EXPECTED_VALUE_FIRST_ID,
    )
    append_exact(
        RANGE_OUTPUT,
        RANGE_FIELDS,
        generated_range_rows(spec),
        EXPECTED_RANGE_FIRST_ID,
    )
    append_exact(
        AVAILABILITY_OUTPUT,
        AVAILABILITY_FIELDS,
        generated_availability_rows(spec),
        EXPECTED_AVAILABILITY_FIRST_ID,
    )
    review = review_payload()
    write_json(REVIEW_JSON, review)
    REVIEW_MD.write_text(render_review_markdown(review), encoding="utf-8")
    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE.write_text(package_text(), encoding="utf-8")
    update_state(update_analysis_outputs())


def verify_materialized() -> None:
    spec = load_spec()
    groups = (
        (
            VALUE_OUTPUT,
            VALUE_FIELDS,
            generated_value_rows(spec),
            EXPECTED_VALUE_FIRST_ID,
            EXPECTED_VALUE_LAST_ID,
        ),
        (
            RANGE_OUTPUT,
            RANGE_FIELDS,
            generated_range_rows(spec),
            EXPECTED_RANGE_FIRST_ID,
            EXPECTED_RANGE_LAST_ID,
        ),
        (
            AVAILABILITY_OUTPUT,
            AVAILABILITY_FIELDS,
            generated_availability_rows(spec),
            EXPECTED_AVAILABILITY_FIRST_ID,
            EXPECTED_AVAILABILITY_LAST_ID,
        ),
    )
    for path, fields, expected, first_id, last_id in groups:
        require_header(path, fields)
        actual = selected_by_codes(
            read_rows(path), {row["code"] for row in expected}
        )
        if semantic(actual, fields[1:]) != semantic(expected, fields[1:]):
            raise ContractError(
                f"stored observations differ from generated contract: {path}"
            )
        ids = sorted(int(row["id"]) for row in actual)
        if ids != list(range(first_id, last_id + 1)):
            raise ContractError(
                f"observation IDs differ from exact suffix {first_id}-{last_id}: {path}"
            )
    expected_review = review_payload()
    if json.loads(REVIEW_JSON.read_text(encoding="utf-8")) != expected_review:
        raise ContractError("source-gap review JSON differs from generated contract")
    if REVIEW_MD.read_text(encoding="utf-8") != render_review_markdown(
        expected_review
    ):
        raise ContractError("source-gap review Markdown differs from generated contract")
    if PACKAGE.read_text(encoding="utf-8") != package_text():
        raise ContractError("package record differs from generated contract")
    expected_analysis = analysis.collect(ROOT)
    if json.loads(analysis.OUT_JSON.read_text(encoding="utf-8")) != expected_analysis:
        raise ContractError("missing-data analysis JSON is stale")
    if analysis.OUT_MD.read_text(encoding="utf-8") != analysis.render_markdown(
        expected_analysis
    ):
        raise ContractError("missing-data analysis Markdown is stale")
    current = next(
        item
        for item in expected_analysis["ranked_candidates"]
        if item["source_code"] == SOURCE_CODE
    )
    if current["selection_status"] != EXHAUSTED_CLASSIFICATION:
        raise ContractError(f"source was not exhausted: {current}")
    resolved_technical = {
        "ground_clearance",
        "overall_height",
        "overall_width_with_mirrors",
        "max_torque_rpm",
    }
    scoped = [
        item
        for item in expected_analysis["configurations"]
        if item["configuration_code"] == CONFIGURATION
    ]
    if not scoped:
        raise ContractError("exact configuration is absent from completeness analysis")
    for item in scoped:
        missing_technical = {
            slot["attribute_code"] for slot in item["missing_technical_slots"]
        }
        if missing_technical & resolved_technical:
            raise ContractError(f"resolved technical slots remain missing: {item}")
        if "parking_assist_system" in item["missing_equipment_attributes"]:
            raise ContractError(f"resolved parking assistance remains missing: {item}")
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
    print(
        "Stepway Extreme automatic source-gap observations: PASS "
        "(2 values + 3 ranges + 1 availability)"
    )


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
