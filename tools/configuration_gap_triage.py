#!/usr/bin/env python3
"""Generate deterministic configuration-gap triage reports."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import configuration_completeness
import source_coverage


DEFAULT_SPEC = Path("data/reporting/configuration_completeness.json")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
DOMAIN_ORDER = {
    "technical": 0,
    "equipment": 1,
}
ORDERING_FIELDS = [
    "domain",
    "source_code",
    "configuration_code",
    "category",
    "attribute_code",
    "fuel_type_code",
]


class GapTriageError(RuntimeError):
    """Controlled configuration-gap triage failure."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GapTriageError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GapTriageError(f"{label} must be a list")
    return value


def completeness_gap_key(
    domain: str,
    gap: Mapping[str, Any],
) -> tuple[str, str, str, str, str, str]:
    return (
        domain,
        str(gap.get("source_code", "")),
        str(gap.get("configuration_code", "")),
        str(gap.get("category", "")),
        str(gap.get("attribute_code", "")),
        str(gap.get("fuel_type_code", "")),
    )


def source_gap_key(
    gap: Mapping[str, Any],
) -> tuple[str, str, str, str, str, str]:
    return (
        str(gap.get("area", "")),
        str(gap.get("source_code", "")),
        str(gap.get("configuration_code", "")),
        str(gap.get("section", "")),
        str(gap.get("attribute_code", "")),
        str(gap.get("fuel_type_code", "")),
    )


def ordering_key(
    key: tuple[str, str, str, str, str, str],
) -> tuple[int, str, str, str, str, str]:
    domain, source_code, configuration_code, category, attribute_code, fuel = key
    if domain not in DOMAIN_ORDER:
        raise GapTriageError(f"unsupported gap domain: {domain!r}")
    return (
        DOMAIN_ORDER[domain],
        source_code,
        configuration_code,
        category,
        attribute_code,
        fuel,
    )


def validate_gap_key(
    key: tuple[str, str, str, str, str, str],
) -> None:
    domain, source_code, configuration_code, category, attribute_code, _ = key
    if domain not in DOMAIN_ORDER:
        raise GapTriageError(f"unsupported gap domain: {domain!r}")
    if not source_code:
        raise GapTriageError(f"gap has empty source_code: {key}")
    if not configuration_code:
        raise GapTriageError(f"gap has empty configuration_code: {key}")
    if not category:
        raise GapTriageError(f"gap has empty category: {key}")
    if not attribute_code:
        raise GapTriageError(f"gap has empty attribute_code: {key}")


def normalized_completeness_gaps(
    report: Mapping[str, Any],
) -> dict[tuple[str, str, str, str, str, str], Mapping[str, Any]]:
    raw_gaps = require_mapping(report.get("gaps"), "completeness gaps")
    result: dict[
        tuple[str, str, str, str, str, str],
        Mapping[str, Any],
    ] = {}
    for domain in ("technical", "equipment"):
        for item in require_list(raw_gaps.get(domain), f"gaps.{domain}"):
            gap = require_mapping(item, f"gaps.{domain} item")
            if gap.get("state") != "missing":
                raise GapTriageError(
                    f"unexpected completeness gap state: {gap.get('state')!r}"
                )
            key = completeness_gap_key(domain, gap)
            validate_gap_key(key)
            if key in result:
                raise GapTriageError(f"duplicate completeness gap: {key}")
            result[key] = gap
    return result


def normalized_source_gaps(
    report: Mapping[str, Any],
) -> dict[tuple[str, str, str, str, str, str], Mapping[str, Any]]:
    result: dict[
        tuple[str, str, str, str, str, str],
        Mapping[str, Any],
    ] = {}
    for item in require_list(report.get("gaps"), "source gaps"):
        gap = require_mapping(item, "source gap item")
        if gap.get("state") != "record_missing":
            raise GapTriageError(
                f"unexpected source gap state: {gap.get('state')!r}"
            )
        key = source_gap_key(gap)
        validate_gap_key(key)
        if key in result:
            raise GapTriageError(f"duplicate source gap: {key}")
        result[key] = gap
    return result


def group_queue(
    queue: Iterable[Mapping[str, Any]],
    field: str,
) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "total": 0,
            "technical": 0,
            "equipment": 0,
        }
    )
    for item in queue:
        key = str(item.get(field, ""))
        if not key:
            raise GapTriageError(f"queue item has empty grouping field {field}")
        domain = str(item.get("domain", ""))
        if domain not in DOMAIN_ORDER:
            raise GapTriageError(f"queue item has invalid domain: {domain!r}")
        groups[key]["total"] += 1
        groups[key][domain] += 1
    return [
        {
            field: key,
            **groups[key],
        }
        for key in sorted(groups)
    ]


def build_triage_report(
    completeness_report: Mapping[str, Any],
    source_report: Mapping[str, Any],
) -> dict[str, Any]:
    completeness_as_of = completeness_report.get("as_of")
    source_as_of = source_report.get("as_of")
    if completeness_as_of != source_as_of:
        raise GapTriageError(
            "input report dates differ: "
            f"{completeness_as_of!r} != {source_as_of!r}"
        )
    if not isinstance(completeness_as_of, str) or not completeness_as_of:
        raise GapTriageError("input reports have no as_of date")

    completeness_gaps = normalized_completeness_gaps(completeness_report)
    source_gaps = normalized_source_gaps(source_report)
    if set(completeness_gaps) != set(source_gaps):
        missing_from_source = sorted(
            set(completeness_gaps) - set(source_gaps),
            key=ordering_key,
        )
        missing_from_completeness = sorted(
            set(source_gaps) - set(completeness_gaps),
            key=ordering_key,
        )
        raise GapTriageError(
            "input gap sets differ"
            f"; missing from source report: {missing_from_source}"
            f"; missing from completeness report: {missing_from_completeness}"
        )

    completeness_technical = require_mapping(
        completeness_report.get("technical"),
        "completeness technical summary",
    )
    completeness_equipment = require_mapping(
        completeness_report.get("equipment"),
        "completeness equipment summary",
    )
    source_records = require_mapping(
        source_report.get("records"),
        "source record summary",
    )
    source_technical = require_mapping(
        source_records.get("technical"),
        "source technical summary",
    )
    source_equipment = require_mapping(
        source_records.get("equipment"),
        "source equipment summary",
    )

    technical_count = sum(1 for key in completeness_gaps if key[0] == "technical")
    equipment_count = sum(1 for key in completeness_gaps if key[0] == "equipment")
    if completeness_technical.get("missing") != technical_count:
        raise GapTriageError("technical completeness gap count differs")
    if completeness_equipment.get("missing") != equipment_count:
        raise GapTriageError("equipment completeness gap count differs")
    if source_technical.get("missing") != technical_count:
        raise GapTriageError("technical source gap count differs")
    if source_equipment.get("missing") != equipment_count:
        raise GapTriageError("equipment source gap count differs")
    if source_technical.get("source_missing", 0) != 0:
        raise GapTriageError("technical source-registration gaps require separate triage")
    if source_equipment.get("source_missing", 0) != 0:
        raise GapTriageError("equipment source-registration gaps require separate triage")

    source_details: dict[str, Mapping[str, Any]] = {}
    for item in require_list(source_report.get("sources"), "source details"):
        source = require_mapping(item, "source detail")
        source_code = str(source.get("source_code", ""))
        if not source_code:
            raise GapTriageError("source detail has empty source_code")
        if source_code in source_details:
            raise GapTriageError(f"duplicate source detail: {source_code}")
        source_details[source_code] = source

    queue: list[dict[str, Any]] = []
    sorted_keys = sorted(completeness_gaps, key=ordering_key)
    for sequence, key in enumerate(sorted_keys, start=1):
        domain, source_code, configuration_code, category, attribute_code, fuel = key
        source = source_details.get(source_code)
        if source is None:
            raise GapTriageError(f"source detail missing for gap: {source_code}")
        if source.get("registration_state") != "registered":
            raise GapTriageError(
                f"gap source is not registered: {source_code} "
                f"({source.get('registration_state')!r})"
            )
        document_date = source.get("document_date")
        file_path = source.get("file_path")
        sha256 = source.get("sha256")
        if not isinstance(document_date, str) or not document_date:
            raise GapTriageError(f"source document date missing: {source_code}")
        if not isinstance(file_path, str) or not file_path:
            raise GapTriageError(f"source file path missing: {source_code}")
        if not isinstance(sha256, str) or SHA256_PATTERN.fullmatch(sha256) is None:
            raise GapTriageError(f"source SHA-256 invalid: {source_code}")

        triage_key = "|".join(
            (
                domain,
                source_code,
                configuration_code,
                category,
                attribute_code,
                fuel or "none",
            )
        )
        queue.append(
            {
                "sequence": sequence,
                "triage_key": triage_key,
                "domain": domain,
                "source_code": source_code,
                "configuration_code": configuration_code,
                "category": category,
                "section": category,
                "attribute_code": attribute_code,
                "fuel_type_code": fuel,
                "gap_state": "record_missing",
                "source_registration_state": "registered",
                "document_date": document_date,
                "file_path": file_path,
                "sha256": sha256,
                "triage_state": "source_verification_required",
                "priority": "unassigned",
                "recommended_action": "verify_registered_source",
                "auto_import": False,
            }
        )

    if len({item["triage_key"] for item in queue}) != len(queue):
        raise GapTriageError("triage keys are not unique")

    explicit_states = {
        "technical_not_applicable": int(
            completeness_technical.get("not_applicable", 0)
        ),
        "equipment_not_applicable": int(
            completeness_equipment.get("not_applicable", 0)
        ),
        "equipment_standard": int(
            completeness_equipment.get("standard", 0)
        ),
        "equipment_optional": int(
            completeness_equipment.get("optional", 0)
        ),
        "equipment_not_available": int(
            completeness_equipment.get("not_available", 0)
        ),
        "equipment_unknown": int(
            completeness_equipment.get("unknown", 0)
        ),
    }

    sources_with_queue = sorted({item["source_code"] for item in queue})
    source_documents = []
    for source_code in sources_with_queue:
        source = source_details[source_code]
        source_documents.append(
            {
                "source_code": source_code,
                "configuration_code": source.get("configuration_code", ""),
                "document_date": source["document_date"],
                "file_path": source["file_path"],
                "sha256": source["sha256"],
                "queue_items": sum(
                    1 for item in queue if item["source_code"] == source_code
                ),
            }
        )

    return {
        "version": 1,
        "as_of": completeness_as_of,
        "ordering": {
            "strategy": "lexicographic_non_priority",
            "fields": ORDERING_FIELDS,
            "priority_assigned": False,
        },
        "summary": {
            "total_candidates": len(queue),
            "technical_candidates": technical_count,
            "equipment_candidates": equipment_count,
            "record_missing": len(queue),
            "source_missing": 0,
            "source_verification_required": len(queue),
            "priority_assigned": 0,
            "auto_import_enabled": 0,
        },
        "explicit_states_excluded_from_queue": explicit_states,
        "groups": {
            "by_source": group_queue(queue, "source_code"),
            "by_configuration": group_queue(queue, "configuration_code"),
            "by_category": group_queue(queue, "category"),
            "by_section": group_queue(queue, "section"),
        },
        "source_documents": source_documents,
        "queue": queue,
    }


def collect_report(
    repository: Path,
    spec_path: Path,
    as_of_value: str | None = None,
) -> dict[str, Any]:
    completeness_report = configuration_completeness.collect_report(
        repository,
        spec_path,
        as_of_value,
    )
    source_report = source_coverage.collect_report(
        repository,
        spec_path,
        as_of_value,
    )
    return build_triage_report(completeness_report, source_report)


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def render_group_table(
    lines: list[str],
    title: str,
    rows: Sequence[Mapping[str, Any]],
    key: str,
) -> None:
    lines.extend(
        [
            "",
            f"## {title}",
            "",
            f"| {key.replace('_', ' ').title()} | Total | Technical | Equipment |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    if not rows:
        lines.append("| — | 0 | 0 | 0 |")
        return
    for row in rows:
        lines.append(
            f"| `{row[key]}` | {row['total']} | "
            f"{row['technical']} | {row['equipment']} |"
        )


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = require_mapping(report.get("summary"), "summary")
    explicit = require_mapping(
        report.get("explicit_states_excluded_from_queue"),
        "explicit states",
    )
    groups = require_mapping(report.get("groups"), "groups")

    lines = [
        "# Configuration Gap Triage",
        "",
        f"As of: `{report['as_of']}`",
        "",
        "The queue is ordered lexicographically for reproducibility. "
        "Its sequence is not a business priority.",
        "",
        "Every item requires verification in its registered source. "
        "No value is inferred and automatic import is disabled.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total candidates | {summary['total_candidates']} |",
        f"| Technical candidates | {summary['technical_candidates']} |",
        f"| Equipment candidates | {summary['equipment_candidates']} |",
        f"| Source-registration gaps | {summary['source_missing']} |",
        f"| Records requiring source verification | {summary['source_verification_required']} |",
        f"| Assigned priorities | {summary['priority_assigned']} |",
        f"| Automatic imports enabled | {summary['auto_import_enabled']} |",
        "",
        "## Explicit states excluded from the queue",
        "",
        "| State | Records |",
        "| --- | ---: |",
    ]
    for key in sorted(explicit):
        lines.append(f"| `{key}` | {explicit[key]} |")

    render_group_table(
        lines,
        "By source",
        require_list(groups.get("by_source"), "groups.by_source"),
        "source_code",
    )
    render_group_table(
        lines,
        "By configuration",
        require_list(
            groups.get("by_configuration"),
            "groups.by_configuration",
        ),
        "configuration_code",
    )
    render_group_table(
        lines,
        "By category",
        require_list(groups.get("by_category"), "groups.by_category"),
        "category",
    )

    lines.extend(
        [
            "",
            "## Source documents",
            "",
            "| Source | Configuration | Date | SHA-256 | Queue items |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for source in require_list(report.get("source_documents"), "source_documents"):
        lines.append(
            f"| `{source['source_code']}` | "
            f"`{source['configuration_code']}` | "
            f"`{source['document_date']}` | "
            f"`{source['sha256']}` | {source['queue_items']} |"
        )

    lines.extend(
        [
            "",
            "## Verification queue",
            "",
            "| # | Domain | Source | Configuration | Category | Attribute | Fuel context | State |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    queue = require_list(report.get("queue"), "queue")
    if not queue:
        lines.append("| — | — | — | — | — | — | — | — |")
    else:
        for item in queue:
            fuel = item["fuel_type_code"] or "none"
            lines.append(
                f"| {item['sequence']} | {item['domain']} | "
                f"`{item['source_code']}` | "
                f"`{item['configuration_code']}` | "
                f"{item['category']} | "
                f"`{item['attribute_code']}` | `{fuel}` | "
                f"`{item['triage_state']}` |"
            )
    lines.append("")
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic, non-prioritized verification queue "
            "for configuration-data gaps."
        )
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=DEFAULT_SPEC,
        help="Configuration completeness denominator specification.",
    )
    parser.add_argument(
        "--as-of",
        help="Optional inclusive snapshot date in YYYY-MM-DD form.",
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    spec_path = arguments.spec
    if not spec_path.is_absolute():
        spec_path = repository / spec_path
    try:
        report = collect_report(
            repository,
            spec_path,
            arguments.as_of,
        )
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, render_json(report))
            print(f"JSON gap triage report written to {arguments.json_path}")
        if arguments.markdown is not None:
            write_atomic(arguments.markdown, render_markdown(report))
            print(
                "Markdown gap triage report written to "
                f"{arguments.markdown}"
            )
        summary = report["summary"]
        print("Configuration gap triage")
        print("------------------------")
        print(f"As of                    : {report['as_of']}")
        print(f"Total candidates         : {summary['total_candidates']}")
        print(f"Technical candidates     : {summary['technical_candidates']}")
        print(f"Equipment candidates     : {summary['equipment_candidates']}")
        print(f"Source-registration gaps : {summary['source_missing']}")
        print(
            "Source verification      : "
            f"{summary['source_verification_required']}"
        )
        print("Priority assignment       : disabled")
        print("Automatic import          : disabled")
        return 0
    except (
        GapTriageError,
        configuration_completeness.CompletenessError,
        source_coverage.SourceCoverageError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
