#!/usr/bin/env python3
"""Build a deterministic resolution plan for reviewed configuration gaps."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence


DEFAULT_EVIDENCE_SPEC = Path(
    "data/reporting/configuration_gap_evidence.json"
)
DEFAULT_PLAN_SPEC = Path(
    "data/reporting/configuration_gap_resolution_plan.json"
)
ALLOWED_EVIDENCE_CLASSIFICATIONS = {
    "found",
    "not_stated",
    "out_of_scope",
}
RESOLUTION_STATES = {
    "ready_for_import",
    "closed_not_stated",
    "closed_out_of_scope",
}
INTEGER_PATTERN = re.compile(r"^-?[0-9]+$")
BOOLEAN_VALUES = {"true", "false"}


class GapResolutionPlanError(RuntimeError):
    """Controlled configuration-gap resolution planning failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GapResolutionPlanError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GapResolutionPlanError(f"{label} must be a list")
    return value


def require_string(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        raise GapResolutionPlanError(f"{label} must be a string")
    if not allow_empty and not value:
        raise GapResolutionPlanError(f"{label} must be non-empty")
    return value


def read_json(path: Path, label: str) -> Mapping[str, Any]:
    if not path.is_file():
        raise GapResolutionPlanError(f"{label} does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GapResolutionPlanError(f"cannot read {label}: {exc}") from exc
    return require_mapping(payload, label)


def read_csv(path: Path, label: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise GapResolutionPlanError(f"{label} does not exist: {path}")
    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise GapResolutionPlanError(f"{label} has no header")
            return list(reader)
    except (OSError, csv.Error) as exc:
        raise GapResolutionPlanError(f"cannot read {label}: {exc}") from exc


def index_rows(
    rows: Sequence[Mapping[str, str]],
    field: str,
    label: str,
) -> dict[str, Mapping[str, str]]:
    result: dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = row.get(field, "")
        if not key:
            raise GapResolutionPlanError(f"{label} has an empty {field}")
        if key in result:
            raise GapResolutionPlanError(f"duplicate {label}: {key}")
        result[key] = row
    return result


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    if not slug:
        raise GapResolutionPlanError("cannot build an empty slug")
    return slug


def humanize_configuration(code: str) -> str:
    ignored = {"iii", "manual", "automatic", "ecog120"}
    tokens = [
        token
        for token in code.split("_")
        if token and token.casefold() not in ignored
    ]
    return " ".join(token.capitalize() for token in tokens)


def humanize_attribute(code: str) -> str:
    return " ".join(token.capitalize() for token in code.split("_"))


def validate_candidate_value(data_type: str, value: str, label: str) -> None:
    if not value:
        raise GapResolutionPlanError(f"{label} must be non-empty")
    if data_type == "integer":
        if INTEGER_PATTERN.fullmatch(value) is None:
            raise GapResolutionPlanError(f"{label} must be an integer")
        return
    if data_type == "decimal":
        try:
            Decimal(value)
        except InvalidOperation as exc:
            raise GapResolutionPlanError(f"{label} must be a decimal") from exc
        return
    if data_type == "boolean":
        if value.casefold() not in BOOLEAN_VALUES:
            raise GapResolutionPlanError(f"{label} must be true or false")
        return
    if data_type in {"string", "enum"}:
        return
    raise GapResolutionPlanError(
        f"unsupported candidate data type: {data_type!r}"
    )


def existing_import_semantics(
    repository: Path,
) -> set[tuple[str, str, str, str]]:
    result: set[tuple[str, str, str, str]] = set()
    root = repository / "data" / "imports" / "configuration_values"
    if not root.is_dir():
        return result
    for path in sorted(root.glob("*.json")):
        payload = read_json(path, f"import specification {path.name}")
        attribute_code = require_string(
            payload.get("attribute_code"),
            f"{path.name}.attribute_code",
        )
        observation_date = require_string(
            payload.get("observation_date"),
            f"{path.name}.observation_date",
        )
        default_fuel = require_string(
            payload.get("fuel_type_code", ""),
            f"{path.name}.fuel_type_code",
            allow_empty=True,
        )
        for row in require_list(payload.get("rows"), f"{path.name}.rows"):
            item = require_mapping(row, f"{path.name} row")
            configuration_code = require_string(
                item.get("configuration_code"),
                f"{path.name}.configuration_code",
            )
            fuel_type_code = require_string(
                item.get("fuel_type_code", default_fuel),
                f"{path.name}.row.fuel_type_code",
                allow_empty=True,
            )
            semantic = (
                configuration_code,
                attribute_code,
                fuel_type_code,
                observation_date,
            )
            if semantic in result:
                raise GapResolutionPlanError(
                    f"duplicate import semantic key: {semantic}"
                )
            result.add(semantic)
    return result


def load_repository_context(
    repository: Path,
) -> dict[str, Any]:
    master = repository / "data" / "master"
    attributes = index_rows(
        read_csv(master / "attributes.csv", "attributes"),
        "code",
        "attribute",
    )
    configurations = index_rows(
        read_csv(master / "configurations.csv", "configurations"),
        "code",
        "configuration",
    )
    sources = index_rows(
        read_csv(master / "sources.csv", "sources"),
        "code",
        "source",
    )
    source_pairs = {
        (
            row.get("source_code", ""),
            row.get("configuration_code", ""),
        )
        for row in read_csv(
            master / "source_configurations.csv",
            "source configurations",
        )
    }
    values = read_csv(
        master / "configuration_attribute_values.csv",
        "configuration attribute values",
    )
    semantics: dict[
        tuple[str, str, str, str],
        Mapping[str, str],
    ] = {}
    maximum_id = 0
    for row in values:
        try:
            maximum_id = max(maximum_id, int(row.get("id", "0")))
        except ValueError as exc:
            raise GapResolutionPlanError(
                f"configuration value has non-integer id: {row.get('id')!r}"
            ) from exc
        key = (
            row.get("configuration_code", ""),
            row.get("attribute_code", ""),
            row.get("fuel_type_code", ""),
            row.get("observation_date", ""),
        )
        if key in semantics:
            raise GapResolutionPlanError(
                f"duplicate configuration value semantic key: {key}"
            )
        semantics[key] = row
    return {
        "attributes": attributes,
        "configurations": configurations,
        "sources": sources,
        "source_pairs": source_pairs,
        "values": semantics,
        "maximum_value_id": maximum_id,
        "import_semantics": existing_import_semantics(repository),
    }


def validate_evidence(
    evidence_spec: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    if evidence_spec.get("version") != 1:
        raise GapResolutionPlanError(
            "evidence specification version must be 1"
        )
    if evidence_spec.get("review_scope") != "source_page_evidence":
        raise GapResolutionPlanError(
            "resolution planning requires source_page_evidence"
        )
    if evidence_spec.get("as_of") is None:
        raise GapResolutionPlanError("evidence as_of is missing")

    decisions: list[Mapping[str, Any]] = []
    keys: set[str] = set()
    for item in require_list(
        evidence_spec.get("decisions"),
        "evidence decisions",
    ):
        decision = require_mapping(item, "evidence decision")
        key = require_string(decision.get("triage_key"), "triage_key")
        if key in keys:
            raise GapResolutionPlanError(f"duplicate evidence key: {key}")
        keys.add(key)
        classification = require_string(
            decision.get("classification"),
            "evidence classification",
        )
        if classification == "ambiguous":
            raise GapResolutionPlanError(
                "resolution planning cannot accept ambiguous evidence"
            )
        if classification not in ALLOWED_EVIDENCE_CLASSIFICATIONS:
            raise GapResolutionPlanError(
                f"unsupported evidence classification: {classification}"
            )
        if decision.get("auto_import") is not False:
            raise GapResolutionPlanError(
                "evidence decision enables automatic import"
            )
        decisions.append(decision)
    if not decisions:
        raise GapResolutionPlanError("evidence decisions must not be empty")
    return decisions


def common_decision_fields(
    sequence: int,
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    fields = (
        "triage_key",
        "domain",
        "source_code",
        "configuration_code",
        "category",
        "attribute_code",
        "fuel_type_code",
        "document_date",
        "file_path",
        "sha256",
        "classification",
        "candidate_value",
        "source_page",
        "source_section",
        "source_text",
        "reviewed_pages",
    )
    result = {"sequence": sequence}
    for field in fields:
        value = decision.get(field)
        if field in {
            "fuel_type_code",
            "candidate_value",
            "source_section",
            "source_text",
        }:
            require_string(value, field, allow_empty=True)
        elif field == "source_page":
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value <= 0
            ):
                raise GapResolutionPlanError("source_page must be positive or null")
        elif field == "reviewed_pages":
            if not isinstance(value, list):
                raise GapResolutionPlanError("reviewed_pages must be a list")
        else:
            require_string(value, field)
        result[field] = value
    return result


def build_found_candidate(
    decision: Mapping[str, Any],
    context: Mapping[str, Any],
    sequence: int,
) -> dict[str, Any]:
    if decision.get("domain") != "technical":
        raise GapResolutionPlanError(
            "found equipment decisions require a separate model review"
        )
    configuration_code = require_string(
        decision.get("configuration_code"),
        "found configuration_code",
    )
    attribute_code = require_string(
        decision.get("attribute_code"),
        "found attribute_code",
    )
    source_code = require_string(
        decision.get("source_code"),
        "found source_code",
    )
    fuel_type_code = require_string(
        decision.get("fuel_type_code", ""),
        "found fuel_type_code",
        allow_empty=True,
    )
    observation_date = require_string(
        decision.get("document_date"),
        "found document_date",
    )
    candidate_value = require_string(
        decision.get("candidate_value"),
        "found candidate_value",
    )
    source_page = decision.get("source_page")
    if not isinstance(source_page, int) or source_page <= 0:
        raise GapResolutionPlanError(
            "found candidate requires a positive source page"
        )
    source_section = require_string(
        decision.get("source_section"),
        "found source_section",
    )
    source_text = require_string(
        decision.get("source_text"),
        "found source_text",
    )

    attributes = require_mapping(context.get("attributes"), "attributes")
    configurations = require_mapping(
        context.get("configurations"),
        "configurations",
    )
    sources = require_mapping(context.get("sources"), "sources")
    attribute = require_mapping(
        attributes.get(attribute_code),
        f"attribute {attribute_code}",
    )
    require_mapping(
        configurations.get(configuration_code),
        f"configuration {configuration_code}",
    )
    source = require_mapping(sources.get(source_code), f"source {source_code}")
    if source.get("status") != "active":
        raise GapResolutionPlanError(f"source is not active: {source_code}")
    if (
        source.get("document_date") != observation_date
        or source.get("file_path") != decision.get("file_path")
        or source.get("sha256") != decision.get("sha256")
    ):
        raise GapResolutionPlanError(
            f"source metadata differs for {source_code}"
        )
    if (
        source_code,
        configuration_code,
    ) not in context["source_pairs"]:
        raise GapResolutionPlanError(
            "found candidate source does not document configuration"
        )

    data_type = require_string(
        attribute.get("data_type"),
        "attribute data_type",
    )
    unit = require_string(
        attribute.get("unit", ""),
        "attribute unit",
        allow_empty=True,
    )
    status = require_string(attribute.get("status"), "attribute status")
    if status != "active":
        raise GapResolutionPlanError(
            f"candidate attribute is not active: {attribute_code}"
        )
    validate_candidate_value(
        data_type,
        candidate_value,
        "found candidate_value",
    )

    semantic = (
        configuration_code,
        attribute_code,
        fuel_type_code,
        observation_date,
    )
    existing = context["values"].get(semantic)
    if existing is not None:
        raise GapResolutionPlanError(
            f"candidate already exists or conflicts: {semantic}"
        )
    if semantic in context["import_semantics"]:
        raise GapResolutionPlanError(
            f"candidate is already covered by an import specification: {semantic}"
        )

    configuration_label = humanize_configuration(configuration_code)
    attribute_label = humanize_attribute(attribute_code)
    package_name = (
        f"{configuration_label} {attribute_label} Value Import"
    )
    package_id = slugify(package_name)
    specification_stem = slugify(
        f"{configuration_label} {attribute_label}"
    )
    specification_path = (
        "data/imports/configuration_values/"
        f"{specification_stem}-{observation_date.replace('-', '')}.json"
    )

    common = common_decision_fields(sequence, decision)
    common.update(
        {
            "resolution_state": "ready_for_import",
            "resolution_route": "configuration_attribute_values",
            "package_id": package_id,
            "requires_model_change": False,
            "requires_data_change": True,
            "requires_source_review": False,
            "auto_import": False,
            "attribute_contract": {
                "data_type": data_type,
                "unit": unit,
                "status": status,
            },
            "suggested_spec_path": specification_path,
        }
    )
    return common


def build_expected_plan_spec(
    repository: Path,
    evidence_spec: Mapping[str, Any],
) -> dict[str, Any]:
    decisions = validate_evidence(evidence_spec)
    context = load_repository_context(repository)
    normalized: list[dict[str, Any]] = []
    found: list[dict[str, Any]] = []

    for sequence, decision in enumerate(decisions, start=1):
        classification = decision["classification"]
        if classification == "found":
            item = build_found_candidate(
                decision,
                context,
                sequence,
            )
            found.append(item)
            normalized.append(item)
            continue

        common = common_decision_fields(sequence, decision)
        if classification == "not_stated":
            state = "closed_not_stated"
            note = (
                "No source-backed data change is planned because the "
                "reviewed relevant pages do not state the value."
            )
        else:
            state = "closed_out_of_scope"
            note = (
                "No source-backed data change is planned because the "
                "evidence decision is explicitly out of scope."
            )
        common.update(
            {
                "resolution_state": state,
                "resolution_route": "none",
                "package_id": "",
                "requires_model_change": False,
                "requires_data_change": False,
                "requires_source_review": False,
                "auto_import": False,
                "attribute_contract": None,
                "suggested_spec_path": "",
                "resolution_note": note,
            }
        )
        normalized.append(common)

    package_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in found:
        package_groups[item["package_id"]].append(item)

    candidate_packages: list[dict[str, Any]] = []
    next_id = int(context["maximum_value_id"]) + 1
    for package_id in sorted(package_groups):
        rows = sorted(
            package_groups[package_id],
            key=lambda item: item["triage_key"],
        )
        first = rows[0]
        contract = require_mapping(
            first.get("attribute_contract"),
            "candidate attribute contract",
        )
        group_key = (
            first["attribute_code"],
            first["document_date"],
            first["fuel_type_code"],
            first["source_page"],
            first["source_section"],
            first["suggested_spec_path"],
        )
        for item in rows[1:]:
            other_key = (
                item["attribute_code"],
                item["document_date"],
                item["fuel_type_code"],
                item["source_page"],
                item["source_section"],
                item["suggested_spec_path"],
            )
            if other_key != group_key:
                raise GapResolutionPlanError(
                    f"candidate package is not homogeneous: {package_id}"
                )
            if item["attribute_contract"] != contract:
                raise GapResolutionPlanError(
                    f"candidate package contract differs: {package_id}"
                )

        configuration_label = humanize_configuration(
            first["configuration_code"]
        )
        attribute_label = humanize_attribute(first["attribute_code"])
        package_name = (
            f"{configuration_label} {attribute_label} Value Import"
            if len(rows) == 1
            else f"{attribute_label} Value Import"
        )
        proposed_rows = [
            {
                "configuration_code": item["configuration_code"],
                "source_code": item["source_code"],
                "value": item["candidate_value"],
                "source_text": item["source_text"],
            }
            for item in rows
        ]
        proposed_spec = {
            "version": 1,
            "kind": "configuration_attribute_values",
            "id_start": next_id,
            "attribute_code": first["attribute_code"],
            "attribute_contract": dict(contract),
            "observation_date": first["document_date"],
            "fuel_type_code": first["fuel_type_code"],
            "source_page": first["source_page"],
            "source_section": first["source_section"],
            "notes_template": (
                "Source page {page}, section {section}: {source_text}"
            ),
            "rows": proposed_rows,
        }
        candidate_packages.append(
            {
                "package_id": package_id,
                "package_name": package_name,
                "package_type": "configuration_value_import",
                "suggested_branch": (
                    "data/"
                    + slugify(
                        f"{configuration_label} "
                        f"{first['attribute_code']}-value"
                    )
                ),
                "suggested_commit_message": (
                    "data: add "
                    + configuration_label
                    + " "
                    + first["attribute_code"].replace("_", " ")
                    + " value"
                ),
                "suggested_spec_path": first["suggested_spec_path"],
                "target_table": (
                    "data/master/configuration_attribute_values.csv"
                ),
                "planned_rows": len(rows),
                "requires_model_change": False,
                "requires_data_change": True,
                "requires_source_review": False,
                "auto_import": False,
                "proposed_import_spec": proposed_spec,
            }
        )
        next_id += len(rows)

    return {
        "version": 1,
        "kind": "configuration_gap_resolution_plan",
        "as_of": evidence_spec["as_of"],
        "review_scope": "resolution_planning",
        "source_evidence_review_scope": evidence_spec["review_scope"],
        "auto_import": False,
        "decisions": normalized,
        "candidate_packages": candidate_packages,
    }


def grouped_counts(
    decisions: Sequence[Mapping[str, Any]],
    field: str,
) -> list[dict[str, Any]]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for decision in decisions:
        key = require_string(decision.get(field), f"decision {field}")
        state = require_string(
            decision.get("resolution_state"),
            "resolution_state",
        )
        groups[key]["total"] += 1
        groups[key][state] += 1
    return [
        {
            field: key,
            "total": groups[key]["total"],
            "ready_for_import": groups[key]["ready_for_import"],
            "closed_not_stated": groups[key]["closed_not_stated"],
            "closed_out_of_scope": groups[key]["closed_out_of_scope"],
        }
        for key in sorted(groups)
    ]


def build_report(
    repository: Path,
    evidence_spec: Mapping[str, Any],
    plan_spec: Mapping[str, Any],
) -> dict[str, Any]:
    expected = build_expected_plan_spec(repository, evidence_spec)
    if plan_spec != expected:
        raise GapResolutionPlanError(
            "versioned resolution plan differs from current evidence and model"
        )

    decisions = require_list(plan_spec.get("decisions"), "plan decisions")
    packages = require_list(
        plan_spec.get("candidate_packages"),
        "candidate packages",
    )
    counts = Counter(
        require_string(
            decision.get("resolution_state"),
            "resolution_state",
        )
        for decision in decisions
    )
    if set(counts) - RESOLUTION_STATES:
        raise GapResolutionPlanError(
            f"unsupported resolution states: {sorted(set(counts) - RESOLUTION_STATES)}"
        )

    planned_rows = sum(
        int(package.get("planned_rows", 0))
        for package in packages
    )
    next_package = (
        packages[0]["package_name"]
        if len(packages) == 1
        else "Configuration Gap Resolution Execution"
    )
    return {
        **dict(plan_spec),
        "summary": {
            "total_decisions": len(decisions),
            "ready_for_import": counts["ready_for_import"],
            "closed_not_stated": counts["closed_not_stated"],
            "closed_out_of_scope": counts["closed_out_of_scope"],
            "model_review_required": 0,
            "candidate_packages": len(packages),
            "planned_rows": planned_rows,
            "requires_model_change": sum(
                1
                for package in packages
                if package.get("requires_model_change") is True
            ),
            "requires_data_change": sum(
                1
                for package in packages
                if package.get("requires_data_change") is True
            ),
            "auto_import_enabled": sum(
                1
                for package in packages
                if package.get("auto_import") is True
            ),
        },
        "groups": {
            "by_domain": grouped_counts(decisions, "domain"),
            "by_attribute": grouped_counts(decisions, "attribute_code"),
            "by_resolution_state": [
                {
                    "resolution_state": state,
                    "count": counts[state],
                }
                for state in sorted(RESOLUTION_STATES)
            ],
        },
        "next_package": next_package,
    }


def collect_report(
    repository: Path,
    plan_spec_path: Path,
    evidence_spec_path: Path,
) -> dict[str, Any]:
    evidence = read_json(
        evidence_spec_path,
        "configuration-gap evidence specification",
    )
    plan = read_json(
        plan_spec_path,
        "configuration-gap resolution plan",
    )
    return build_report(repository, evidence, plan)


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = require_mapping(report.get("summary"), "summary")
    lines = [
        "# Configuration Gap Resolution Plan",
        "",
        f"As of: `{report['as_of']}`",
        "",
        "The plan separates evidence, model decisions and data execution. "
        "It never imports data automatically.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total decisions | {summary['total_decisions']} |",
        f"| Ready for import | {summary['ready_for_import']} |",
        f"| Closed: not stated | {summary['closed_not_stated']} |",
        f"| Closed: out of scope | {summary['closed_out_of_scope']} |",
        f"| Model review required | {summary['model_review_required']} |",
        f"| Candidate packages | {summary['candidate_packages']} |",
        f"| Planned rows | {summary['planned_rows']} |",
        (
            "| Packages requiring model change | "
            f"{summary['requires_model_change']} |"
        ),
        (
            "| Packages requiring data change | "
            f"{summary['requires_data_change']} |"
        ),
        (
            "| Automatic imports enabled | "
            f"{summary['auto_import_enabled']} |"
        ),
        "",
        "## Candidate packages",
        "",
    ]
    packages = require_list(
        report.get("candidate_packages"),
        "candidate packages",
    )
    if not packages:
        lines.append("No execution package is planned.")
    for package in packages:
        lines.extend(
            [
                f"### {package['package_name']}",
                "",
                f"- Package type: `{package['package_type']}`",
                f"- Suggested branch: `{package['suggested_branch']}`",
                f"- Suggested specification: `{package['suggested_spec_path']}`",
                f"- Target table: `{package['target_table']}`",
                f"- Planned rows: {package['planned_rows']}",
                f"- Model change: `{str(package['requires_model_change']).lower()}`",
                f"- Automatic import: `{str(package['auto_import']).lower()}`",
                "",
            ]
        )
        proposed = require_mapping(
            package.get("proposed_import_spec"),
            "proposed import specification",
        )
        lines.extend(
            [
                "| Configuration | Attribute | Value | Source page |",
                "| --- | --- | --- | ---: |",
            ]
        )
        for row in require_list(proposed.get("rows"), "proposed rows"):
            lines.append(
                f"| `{row['configuration_code']}` | "
                f"`{proposed['attribute_code']}` | "
                f"`{row['value']}` | {proposed['source_page']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Resolution decisions",
            "",
            "| # | Evidence | Resolution | Configuration | Attribute | Package |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for decision in require_list(report.get("decisions"), "decisions"):
        package_id = decision.get("package_id") or "—"
        lines.append(
            f"| {decision['sequence']} | "
            f"`{decision['classification']}` | "
            f"`{decision['resolution_state']}` | "
            f"`{decision['configuration_code']}` | "
            f"`{decision['attribute_code']}` | "
            f"`{package_id}` |"
        )
    lines.extend(
        [
            "",
            f"Next package: **{report['next_package']}**.",
            "",
        ]
    )
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
            "Generate and validate a deterministic execution plan for "
            "reviewed configuration gaps."
        )
    )
    parser.add_argument(
        "--evidence-spec",
        type=Path,
        default=DEFAULT_EVIDENCE_SPEC,
    )
    parser.add_argument(
        "--plan-spec",
        type=Path,
        default=DEFAULT_PLAN_SPEC,
    )
    parser.add_argument(
        "--write-plan-spec",
        type=Path,
        help="Write the exact expected versioned plan before reporting.",
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def resolve_path(repository: Path, path: Path) -> Path:
    return path if path.is_absolute() else repository / path


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    evidence_path = resolve_path(repository, arguments.evidence_spec)
    plan_path = resolve_path(repository, arguments.plan_spec)

    try:
        if arguments.write_plan_spec is not None:
            target = resolve_path(repository, arguments.write_plan_spec)
            evidence = read_json(
                evidence_path,
                "configuration-gap evidence specification",
            )
            expected = build_expected_plan_spec(repository, evidence)
            write_atomic(target, render_json(expected))
            plan_path = target
            print(f"Resolution plan specification written to {target}")

        report = collect_report(
            repository,
            plan_path,
            evidence_path,
        )
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, render_json(report))
            print(
                "JSON configuration-gap resolution plan written to "
                f"{arguments.json_path}"
            )
        if arguments.markdown is not None:
            write_atomic(
                arguments.markdown,
                render_markdown(report),
            )
            print(
                "Markdown configuration-gap resolution plan written to "
                f"{arguments.markdown}"
            )
        summary = report["summary"]
        print("Configuration gap resolution plan")
        print("---------------------------------")
        print(f"As of                  : {report['as_of']}")
        print(
            f"Total decisions        : "
            f"{summary['total_decisions']}"
        )
        print(
            f"Ready for import       : "
            f"{summary['ready_for_import']}"
        )
        print(
            f"Closed not stated      : "
            f"{summary['closed_not_stated']}"
        )
        print(
            f"Closed out of scope    : "
            f"{summary['closed_out_of_scope']}"
        )
        print(
            f"Candidate packages     : "
            f"{summary['candidate_packages']}"
        )
        print(f"Planned rows           : {summary['planned_rows']}")
        print("Automatic import       : disabled")
        print(f"Next package           : {report['next_package']}")
        return 0
    except GapResolutionPlanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
