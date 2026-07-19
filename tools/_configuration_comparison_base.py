#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from configuration_value_range_reporting import (
    combine_latest_observations,
    range_relation,
    read_optional_ranges,
)


DEFAULT_COMPLETENESS_SPEC = Path(
    "data/reporting/configuration_completeness.json"
)
DEFAULT_EVIDENCE_SPEC = Path(
    "data/reporting/configuration_gap_evidence.json"
)
AVAILABILITY_STATES = {
    "standard",
    "optional",
    "not_available",
    "unknown",
}
EVIDENCE_STATES = {
    "ambiguous",
    "found",
    "not_stated",
    "out_of_scope",
}
PAIR_TYPES = (
    "different_version_different_transmission",
    "different_version_same_transmission",
    "same_version_different_transmission",
    "same_version_same_transmission",
)
DIFFERENCE_DOMAINS = (
    "prices",
    "technical",
    "equipment",
)
DIFFERENCE_CSV_FIELDS = (
    "pair_code",
    "pair_type",
    "domain",
    "comparison",
    "item_code",
    "item_name",
    "category",
    "context",
    "unit",
    "left_configuration_code",
    "left_version_code",
    "left_transmission_type",
    "left_state",
    "left_value",
    "left_source_code",
    "left_observation_date",
    "right_configuration_code",
    "right_version_code",
    "right_transmission_type",
    "right_state",
    "right_value",
    "right_source_code",
    "right_observation_date",
    "delta_right_minus_left",
)


class ComparisonError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ComparisonError(f"missing CSV header: {path}")
            return list(reader)
    except (OSError, UnicodeDecodeError) as exc:
        raise ComparisonError(f"cannot read UTF-8 CSV {path}: {exc}") from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"JSON root must be an object: {path}")
    return value


def iso_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ComparisonError(
            f"invalid ISO date for {label}: {value!r}"
        ) from exc


def latest(
    rows: Iterable[dict[str, str]],
    key_fields: Sequence[str],
    date_field: str,
    as_of: date,
    label: str,
) -> dict[tuple[str, ...], dict[str, str]]:
    chosen: dict[tuple[str, ...], tuple[date, dict[str, str]]] = {}
    for row in rows:
        observed = iso_date(row.get(date_field, ""), label)
        if observed > as_of:
            continue
        key = tuple(row.get(field, "") for field in key_fields)
        for field, item in zip(key_fields, key):
            if not item and field != "fuel_type_code":
                raise ComparisonError(f"{label} has incomplete key: {key}")
        previous = chosen.get(key)
        if previous is None or observed > previous[0]:
            chosen[key] = (observed, row)
        elif observed == previous[0]:
            raise ComparisonError(
                f"{label} has duplicate current records for "
                f"{key} on {observed}"
            )
    return {key: item[1] for key, item in chosen.items()}


def parse_scope(
    repository: Path,
    spec_path: Path,
) -> dict[str, Any]:
    master = repository / "data" / "master"
    spec = read_json(spec_path)
    if spec.get("version") != 1:
        raise ComparisonError("completeness spec version must be 1")

    required = (
        "configuration_status",
        "configurations",
        "technical_slots",
        "equipment_attributes",
        "not_applicable",
    )
    missing = [key for key in required if key not in spec]
    if missing:
        raise ComparisonError(f"completeness spec keys missing: {missing}")

    configurations = read_csv(master / "configurations.csv")
    sources = read_csv(master / "sources.csv")
    attributes = read_csv(master / "attributes.csv")

    status = str(spec["configuration_status"])
    active_rows = {
        row["code"]: row
        for row in configurations
        if row.get("status") == status
    }
    source_rows = {
        row["code"]: row
        for row in sources
        if row.get("status") == "active"
    }
    attribute_rows = {
        row["code"]: row
        for row in attributes
        if row.get("status") == "active"
    }

    configuration_sources: dict[str, str] = {}
    for item in spec["configurations"]:
        if not isinstance(item, dict):
            raise ComparisonError("invalid configuration mapping")
        code = str(item.get("configuration_code", ""))
        source = str(item.get("source_code", ""))
        if not code or not source or code in configuration_sources:
            raise ComparisonError(
                "invalid configuration/source mapping in spec"
            )
        configuration_sources[code] = source

    if sorted(configuration_sources) != sorted(active_rows):
        raise ComparisonError(
            "spec configurations differ from current active configuration scope"
        )
    missing_sources = sorted(
        set(configuration_sources.values()) - set(source_rows)
    )
    if missing_sources:
        raise ComparisonError(
            f"inactive or missing sources in spec: {missing_sources}"
        )

    technical_slots: list[tuple[str, str]] = []
    for item in spec["technical_slots"]:
        if not isinstance(item, dict):
            raise ComparisonError("invalid technical slot in spec")
        slot = (
            str(item.get("attribute_code", "")),
            str(item.get("fuel_type_code", "")),
        )
        if not slot[0] or slot in technical_slots:
            raise ComparisonError(
                "invalid or duplicate technical slot in spec"
            )
        technical_slots.append(slot)
    technical_slots.sort()

    equipment_attributes = sorted(
        str(item) for item in spec["equipment_attributes"]
    )
    if (
        len(equipment_attributes) != len(set(equipment_attributes))
        or any(not item for item in equipment_attributes)
    ):
        raise ComparisonError(
            "invalid or duplicate equipment attribute in spec"
        )

    scoped_attributes = {
        attribute for attribute, _ in technical_slots
    } | set(equipment_attributes)
    missing_attributes = sorted(scoped_attributes - set(attribute_rows))
    if missing_attributes:
        raise ComparisonError(
            f"inactive or missing attributes in scope: {missing_attributes}"
        )

    raw_na = spec["not_applicable"]
    if not isinstance(raw_na, dict):
        raise ComparisonError("not_applicable spec must be an object")
    technical_na = {
        (
            str(item.get("configuration_code", "")),
            str(item.get("attribute_code", "")),
            str(item.get("fuel_type_code", "")),
        )
        for item in raw_na.get("technical", [])
        if isinstance(item, dict)
    }
    equipment_na = {
        (
            str(item.get("configuration_code", "")),
            str(item.get("attribute_code", "")),
        )
        for item in raw_na.get("equipment", [])
        if isinstance(item, dict)
    }

    technical_scope = {
        (configuration, attribute, fuel)
        for configuration in active_rows
        for attribute, fuel in technical_slots
    }
    equipment_scope = {
        (configuration, attribute)
        for configuration in active_rows
        for attribute in equipment_attributes
    }
    if not technical_na <= technical_scope:
        raise ComparisonError(
            "technical not_applicable outside comparison scope"
        )
    if not equipment_na <= equipment_scope:
        raise ComparisonError(
            "equipment not_applicable outside comparison scope"
        )

    return {
        "status": status,
        "configurations": {
            code: {
                "configuration_code": code,
                "version_code": row.get("version_code", ""),
                "powertrain_label": row.get("powertrain_label", ""),
                "transmission_type": row.get("transmission_type", ""),
                "source_code": configuration_sources[code],
            }
            for code, row in sorted(active_rows.items())
        },
        "attributes": {
            code: {
                "attribute_code": code,
                "category": row.get("category", ""),
                "name": row.get("name", ""),
                "data_type": row.get("data_type", ""),
                "unit": row.get("unit", ""),
            }
            for code, row in sorted(attribute_rows.items())
            if code in scoped_attributes
        },
        "technical_slots": technical_slots,
        "equipment_attributes": equipment_attributes,
        "technical_na": technical_na,
        "equipment_na": equipment_na,
        "technical_scope": technical_scope,
        "equipment_scope": equipment_scope,
    }


def normalize_value(value: str, data_type: str) -> Any:
    if data_type == "integer":
        try:
            return int(value)
        except ValueError as exc:
            raise ComparisonError(
                f"invalid integer comparison value: {value!r}"
            ) from exc
    if data_type == "decimal":
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ComparisonError(
                f"invalid decimal comparison value: {value!r}"
            ) from exc
        normalized = format(parsed.normalize(), "f")
        return "0" if normalized in {"-0", ""} else normalized
    if data_type == "boolean":
        if value not in {"true", "false"}:
            raise ComparisonError(
                f"invalid boolean comparison value: {value!r}"
            )
        return value == "true"
    return value


def evidence_index(
    evidence_path: Path,
    as_of: date,
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    payload = read_json(evidence_path)
    if payload.get("version") != 1:
        raise ComparisonError("evidence spec version must be 1")
    evidence_as_of = iso_date(str(payload.get("as_of", "")), "evidence as_of")
    if evidence_as_of != as_of:
        raise ComparisonError(
            "comparison as_of must match the versioned evidence snapshot"
        )
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        raise ComparisonError("evidence decisions must be a list")

    indexed: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            raise ComparisonError("invalid evidence decision")
        domain = str(decision.get("domain", ""))
        configuration = str(decision.get("configuration_code", ""))
        attribute = str(decision.get("attribute_code", ""))
        fuel = str(decision.get("fuel_type_code", ""))
        classification = str(decision.get("classification", ""))
        if domain not in {"technical", "equipment"}:
            raise ComparisonError(
                f"invalid evidence domain: {domain!r}"
            )
        if classification not in EVIDENCE_STATES:
            raise ComparisonError(
                f"invalid evidence classification: {classification!r}"
            )
        if domain == "equipment" and fuel:
            raise ComparisonError(
                "equipment evidence must have empty fuel context"
            )
        key = (domain, configuration, attribute, fuel)
        if not configuration or not attribute or key in indexed:
            raise ComparisonError(
                f"invalid or duplicate evidence key: {key}"
            )
        indexed[key] = decision
    return indexed


def recorded_technical_state(
    row: Mapping[str, str],
    attribute: Mapping[str, str],
) -> dict[str, Any]:
    value = str(row.get("value", ""))
    data_type = str(attribute.get("data_type", ""))
    return {
        "state": "recorded",
        "value": value,
        "normalized_value": normalize_value(value, data_type),
        "data_type": data_type,
        "unit": str(attribute.get("unit", "")),
        "observation_date": str(row.get("observation_date", "")),
        "source_code": str(row.get("source_code", "")),
    }


def recorded_range_state(
    row: Mapping[str, str],
    attribute: Mapping[str, str],
) -> dict[str, Any]:
    data_type = str(attribute.get("data_type", ""))
    return {
        "state": "recorded",
        "minimum_value": normalize_value(str(row.get("minimum_value", "")), data_type),
        "maximum_value": normalize_value(str(row.get("maximum_value", "")), data_type),
        "lower_inclusive": str(row.get("lower_inclusive", "")) == "true",
        "upper_inclusive": str(row.get("upper_inclusive", "")) == "true",
        "data_type": data_type,
        "unit": str(attribute.get("unit", "")),
        "observation_date": str(row.get("observation_date", "")),
        "source_code": str(row.get("source_code", "")),
    }


def technical_comparison_result(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> tuple[str, str | None]:
    if left.get("state") != "recorded" or right.get("state") != "recorded":
        return "not_comparable", None
    if "minimum_value" not in left and "minimum_value" not in right:
        return comparison_result(left, right, comparable_key="normalized_value"), None
    try:
        relation = range_relation(left, right)
    except ValueError as exc:
        raise ComparisonError(str(exc)) from exc
    return ("equal" if relation == "identical" else "different"), relation


def evidence_state(decision: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "state": str(decision.get("classification", "")),
        "reason_code": str(decision.get("reason_code", "")),
        "source_code": str(decision.get("source_code", "")),
        "reviewed_pages": list(decision.get("reviewed_pages", [])),
    }
    basis = decision.get("basis")
    if isinstance(basis, dict):
        result["basis"] = dict(sorted(basis.items()))
    return result


def pair_type(
    left: Mapping[str, str],
    right: Mapping[str, str],
) -> str:
    same_version = left["version_code"] == right["version_code"]
    same_transmission = (
        left["transmission_type"] == right["transmission_type"]
    )
    if same_version and not same_transmission:
        return "same_version_different_transmission"
    if not same_version and same_transmission:
        return "different_version_same_transmission"
    if same_version and same_transmission:
        return "same_version_same_transmission"
    return "different_version_different_transmission"


def comparison_result(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    comparable_key: str,
) -> str:
    if left.get("state") != "recorded" or right.get("state") != "recorded":
        return "not_comparable"
    return (
        "equal"
        if left.get(comparable_key) == right.get(comparable_key)
        else "different"
    )


def count_results(items: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter(str(item["comparison"]) for item in items)
    return {
        "comparisons": len(items),
        "equal": counts["equal"],
        "different": counts["different"],
        "not_comparable": counts["not_comparable"],
    }


def collect_report(
    repository: Path,
    completeness_spec: Path,
    evidence_spec: Path,
    as_of_value: str | None = None,
    pair_type_filter: str | None = None,
) -> dict[str, Any]:
    if (
        pair_type_filter is not None
        and pair_type_filter not in PAIR_TYPES
    ):
        raise ComparisonError(
            f"unsupported pair type filter: {pair_type_filter!r}"
        )
    scope = parse_scope(repository, completeness_spec)
    evidence_payload = read_json(evidence_spec)
    evidence_date_value = str(evidence_payload.get("as_of", ""))
    as_of = iso_date(
        as_of_value if as_of_value is not None else evidence_date_value,
        "--as-of",
    )
    evidence = evidence_index(evidence_spec, as_of)

    master = repository / "data" / "master"
    prices = read_csv(master / "configuration_prices.csv")
    values = read_csv(master / "configuration_attribute_values.csv")
    ranges = read_optional_ranges(master, read_csv)
    availability = read_csv(
        master / "configuration_attribute_availability.csv"
    )

    configuration_codes = sorted(scope["configurations"])
    configuration_set = set(configuration_codes)
    scoped_prices = [
        row
        for row in prices
        if row.get("configuration_code") in configuration_set
    ]
    scoped_values = [
        row
        for row in values
        if row.get("configuration_code") in configuration_set
    ]
    scoped_ranges = [
        row
        for row in ranges
        if row.get("configuration_code") in configuration_set
    ]
    scoped_availability = [
        row
        for row in availability
        if row.get("configuration_code") in configuration_set
    ]

    current_prices = latest(
        scoped_prices,
        (
            "configuration_code",
            "market",
            "price_type",
            "currency_code",
        ),
        "price_date",
        as_of,
        "configuration prices",
    )
    current_scalar_values = latest(
        scoped_values,
        (
            "configuration_code",
            "attribute_code",
            "fuel_type_code",
        ),
        "observation_date",
        as_of,
        "configuration values",
    )
    current_range_values = latest(
        scoped_ranges,
        (
            "configuration_code",
            "attribute_code",
            "fuel_type_code",
        ),
        "observation_date",
        as_of,
        "configuration value ranges",
    )
    current_values = combine_latest_observations(
        current_scalar_values, current_range_values, ComparisonError
    )
    current_availability = latest(
        scoped_availability,
        ("configuration_code", "attribute_code"),
        "observation_date",
        as_of,
        "configuration availability",
    )

    allowed_slots = set(scope["technical_slots"])
    extra_slots = sorted(
        {(key[1], key[2]) for key in current_values} - allowed_slots
    )
    if extra_slots:
        raise ComparisonError(
            f"observed technical slots are absent from scope: {extra_slots}"
        )
    extra_equipment = sorted(
        {key[1] for key in current_availability}
        - set(scope["equipment_attributes"])
    )
    if extra_equipment:
        raise ComparisonError(
            "observed equipment attributes are absent from scope: "
            f"{extra_equipment}"
        )

    for key, row in current_values.items():
        expected_source = scope["configurations"][key[0]]["source_code"]
        if row.get("source_code") != expected_source:
            raise ComparisonError(
                f"technical record source differs from scope mapping: {key}"
            )
    for key, row in current_availability.items():
        expected_source = scope["configurations"][key[0]]["source_code"]
        if row.get("source_code") != expected_source:
            raise ComparisonError(
                f"equipment record source differs from scope mapping: {key}"
            )
        state = row.get("availability_status", "")
        if state not in AVAILABILITY_STATES:
            raise ComparisonError(
                f"unexpected availability status for {key}: {state!r}"
            )
    for key, row in current_prices.items():
        expected_source = scope["configurations"][key[0]]["source_code"]
        if row.get("source_code") != expected_source:
            raise ComparisonError(
                f"price record source differs from scope mapping: {key}"
            )

    missing_evidence_keys: set[tuple[str, str, str, str]] = set()
    for configuration, attribute, fuel in scope["technical_scope"]:
        key = (configuration, attribute, fuel)
        if key in scope["technical_na"]:
            if key in current_values:
                raise ComparisonError(
                    f"not_applicable technical slot has a record: {key}"
                )
            continue
        if key not in current_values:
            missing_evidence_keys.add(
                ("technical", configuration, attribute, fuel)
            )

    for configuration, attribute in scope["equipment_scope"]:
        key = (configuration, attribute)
        if key in scope["equipment_na"]:
            if key in current_availability:
                raise ComparisonError(
                    f"not_applicable equipment slot has a record: {key}"
                )
            continue
        if key not in current_availability:
            missing_evidence_keys.add(
                ("equipment", configuration, attribute, "")
            )

    if set(evidence) != missing_evidence_keys:
        missing = sorted(missing_evidence_keys - set(evidence))
        extra = sorted(set(evidence) - missing_evidence_keys)
        raise ComparisonError(
            "evidence decisions differ from current missing comparison scope; "
            f"missing={missing}, extra={extra}"
        )

    price_dimensions = sorted(
        {(key[1], key[2], key[3]) for key in current_prices}
    )
    pairs: list[dict[str, Any]] = []
    aggregate = {
        "prices": Counter(),
        "technical": Counter(),
        "equipment": Counter(),
    }

    for left_code, right_code in combinations(configuration_codes, 2):
        left_configuration = scope["configurations"][left_code]
        right_configuration = scope["configurations"][right_code]
        current_pair_type = pair_type(
            left_configuration,
            right_configuration,
        )
        if (
            pair_type_filter is not None
            and current_pair_type != pair_type_filter
        ):
            continue

        price_items: list[dict[str, Any]] = []
        for market, price_kind, currency in price_dimensions:
            left_row = current_prices.get(
                (left_code, market, price_kind, currency)
            )
            right_row = current_prices.get(
                (right_code, market, price_kind, currency)
            )
            left_state: dict[str, Any]
            right_state: dict[str, Any]
            if left_row is None:
                left_state = {"state": "missing"}
            else:
                try:
                    amount = Decimal(left_row["amount"])
                except InvalidOperation as exc:
                    raise ComparisonError(
                        f"invalid price amount: {left_row['amount']!r}"
                    ) from exc
                left_state = {
                    "state": "recorded",
                    "amount": format(amount.normalize(), "f"),
                    "price_date": left_row["price_date"],
                    "source_code": left_row["source_code"],
                }
            if right_row is None:
                right_state = {"state": "missing"}
            else:
                try:
                    amount = Decimal(right_row["amount"])
                except InvalidOperation as exc:
                    raise ComparisonError(
                        f"invalid price amount: {right_row['amount']!r}"
                    ) from exc
                right_state = {
                    "state": "recorded",
                    "amount": format(amount.normalize(), "f"),
                    "price_date": right_row["price_date"],
                    "source_code": right_row["source_code"],
                }
            result = comparison_result(
                left_state,
                right_state,
                comparable_key="amount",
            )
            item: dict[str, Any] = {
                "market": market,
                "price_type": price_kind,
                "currency_code": currency,
                "left": left_state,
                "right": right_state,
                "comparison": result,
            }
            if result == "different":
                item["amount_delta_right_minus_left"] = format(
                    Decimal(str(right_state["amount"]))
                    - Decimal(str(left_state["amount"])),
                    "f",
                )
            price_items.append(item)

        technical_items: list[dict[str, Any]] = []
        for attribute_code, fuel in scope["technical_slots"]:
            attribute = scope["attributes"][attribute_code]
            left_key = (left_code, attribute_code, fuel)
            right_key = (right_code, attribute_code, fuel)

            if left_key in scope["technical_na"]:
                left_state = {"state": "not_applicable"}
            elif left_key in current_values:
                left_row = current_values[left_key]
                left_state = (
                    recorded_range_state(left_row, attribute)
                    if left_row.get("_observation_kind") == "range"
                    else recorded_technical_state(left_row, attribute)
                )
            else:
                left_state = evidence_state(
                    evidence[
                        (
                            "technical",
                            left_code,
                            attribute_code,
                            fuel,
                        )
                    ]
                )

            if right_key in scope["technical_na"]:
                right_state = {"state": "not_applicable"}
            elif right_key in current_values:
                right_row = current_values[right_key]
                right_state = (
                    recorded_range_state(right_row, attribute)
                    if right_row.get("_observation_kind") == "range"
                    else recorded_technical_state(right_row, attribute)
                )
            else:
                right_state = evidence_state(
                    evidence[
                        (
                            "technical",
                            right_code,
                            attribute_code,
                            fuel,
                        )
                    ]
                )

            technical_comparison, relation = technical_comparison_result(
                left_state, right_state
            )
            technical_item = {
                "attribute_code": attribute_code,
                "attribute_name": attribute["name"],
                "category": attribute["category"],
                "fuel_type_code": fuel,
                "unit": attribute["unit"],
                "left": left_state,
                "right": right_state,
                "comparison": technical_comparison,
            }
            if relation is not None:
                technical_item["range_relation"] = relation
            technical_items.append(technical_item)

        equipment_items: list[dict[str, Any]] = []
        for attribute_code in scope["equipment_attributes"]:
            attribute = scope["attributes"][attribute_code]
            left_key = (left_code, attribute_code)
            right_key = (right_code, attribute_code)

            if left_key in scope["equipment_na"]:
                left_state = {"state": "not_applicable"}
            elif left_key in current_availability:
                row = current_availability[left_key]
                left_state = {
                    "state": "recorded",
                    "availability_status": row["availability_status"],
                    "observation_date": row["observation_date"],
                    "source_code": row["source_code"],
                }
            else:
                left_state = evidence_state(
                    evidence[
                        (
                            "equipment",
                            left_code,
                            attribute_code,
                            "",
                        )
                    ]
                )

            if right_key in scope["equipment_na"]:
                right_state = {"state": "not_applicable"}
            elif right_key in current_availability:
                row = current_availability[right_key]
                right_state = {
                    "state": "recorded",
                    "availability_status": row["availability_status"],
                    "observation_date": row["observation_date"],
                    "source_code": row["source_code"],
                }
            else:
                right_state = evidence_state(
                    evidence[
                        (
                            "equipment",
                            right_code,
                            attribute_code,
                            "",
                        )
                    ]
                )

            equipment_items.append(
                {
                    "attribute_code": attribute_code,
                    "attribute_name": attribute["name"],
                    "category": attribute["category"],
                    "left": left_state,
                    "right": right_state,
                    "comparison": comparison_result(
                        left_state,
                        right_state,
                        comparable_key="availability_status",
                    ),
                }
            )

        summaries = {
            "prices": count_results(price_items),
            "technical": count_results(technical_items),
            "equipment": count_results(equipment_items),
        }
        for domain, summary in summaries.items():
            aggregate[domain].update(
                {
                    "comparisons": summary["comparisons"],
                    "equal": summary["equal"],
                    "different": summary["different"],
                    "not_comparable": summary["not_comparable"],
                }
            )

        pairs.append(
            {
                "pair_code": f"{left_code}__vs__{right_code}",
                "pair_type": current_pair_type,
                "left_configuration": dict(left_configuration),
                "right_configuration": dict(right_configuration),
                "summary": summaries,
                "prices": price_items,
                "technical": technical_items,
                "equipment": equipment_items,
            }
        )

    evidence_counts = Counter(
        str(decision.get("classification", ""))
        for decision in evidence.values()
    )
    summary = {
        domain: {
            "comparisons": counts["comparisons"],
            "equal": counts["equal"],
            "different": counts["different"],
            "not_comparable": counts["not_comparable"],
        }
        for domain, counts in aggregate.items()
    }
    summary["total_differences"] = sum(
        int(summary[domain]["different"])
        for domain in ("prices", "technical", "equipment")
    )
    selected_configuration_codes = sorted(
        {
            configuration["configuration_code"]
            for pair in pairs
            for configuration in (
                pair["left_configuration"],
                pair["right_configuration"],
            )
        }
    )
    unfiltered_pair_count = (
        len(configuration_codes) * (len(configuration_codes) - 1) // 2
    )

    return {
        "version": 1,
        "as_of": as_of.isoformat(),
        "scope": {
            "configuration_status": scope["status"],
            "active_configurations": len(configuration_codes),
            "configuration_codes": configuration_codes,
            "pair_type_filter": pair_type_filter,
            "unfiltered_pair_count": unfiltered_pair_count,
            "pair_count": len(pairs),
            "selected_configurations": len(
                selected_configuration_codes
            ),
            "selected_configuration_codes": (
                selected_configuration_codes
            ),
            "price_dimensions": len(price_dimensions),
            "technical_slots": len(scope["technical_slots"]),
            "equipment_attributes": len(
                scope["equipment_attributes"]
            ),
        },
        "evidence_summary": {
            "total": len(evidence),
            "ambiguous": evidence_counts["ambiguous"],
            "found": evidence_counts["found"],
            "not_stated": evidence_counts["not_stated"],
            "out_of_scope": evidence_counts["out_of_scope"],
        },
        "summary": summary,
        "pairs": pairs,
    }


def render_json(report: Mapping[str, Any]) -> str:
    return (
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def range_state_value(state: Mapping[str, Any]) -> str:
    lower = "[" if state.get("lower_inclusive") else "("
    upper = "]" if state.get("upper_inclusive") else ")"
    return (
        f"{lower}{state.get('minimum_value', '')},"
        f"{state.get('maximum_value', '')}{upper}"
    )


def difference_state_value(
    state: Mapping[str, Any],
    domain: str,
) -> str:
    if domain == "prices":
        return str(state.get("amount", ""))
    if domain == "technical":
        if "minimum_value" in state:
            return range_state_value(state)
        return str(state.get("value", ""))
    return str(state.get("availability_status", ""))


def difference_state_date(
    state: Mapping[str, Any],
    domain: str,
) -> str:
    key = "price_date" if domain == "prices" else "observation_date"
    return str(state.get(key, ""))


def comparison_item_code(
    item: Mapping[str, Any],
    domain: str,
) -> str:
    if domain == "prices":
        return str(item["price_type"])
    return str(item["attribute_code"])


def difference_item_codes(
    report: Mapping[str, Any],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                comparison_item_code(item, domain)
                for pair in report["pairs"]
                for domain in DIFFERENCE_DOMAINS
                for item in pair[domain]
            }
        )
    )


def difference_csv_rows(
    report: Mapping[str, Any],
    difference_domain: str | None = None,
    difference_item_code: str | None = None,
    known_item_codes: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    if (
        difference_domain is not None
        and difference_domain not in DIFFERENCE_DOMAINS
    ):
        raise ComparisonError(
            f"unsupported difference domain: {difference_domain!r}"
        )
    if difference_item_code is not None:
        available_item_codes = set(
            known_item_codes
            if known_item_codes is not None
            else difference_item_codes(report)
        )
        if difference_item_code not in available_item_codes:
            raise ComparisonError(
                "unsupported difference item code: "
                f"{difference_item_code!r}"
            )
    rows: list[dict[str, str]] = []
    for pair in report["pairs"]:
        left_configuration = pair["left_configuration"]
        right_configuration = pair["right_configuration"]
        for domain in DIFFERENCE_DOMAINS:
            if (
                difference_domain is not None
                and domain != difference_domain
            ):
                continue
            for item in pair[domain]:
                current_item_code = comparison_item_code(
                    item,
                    domain,
                )
                if (
                    difference_item_code is not None
                    and current_item_code != difference_item_code
                ):
                    continue
                if item["comparison"] != "different":
                    continue
                left = item["left"]
                right = item["right"]
                if (
                    left.get("state") != "recorded"
                    or right.get("state") != "recorded"
                ):
                    raise ComparisonError(
                        "difference export requires two recorded states"
                    )

                if domain == "prices":
                    item_code = str(item["price_type"])
                    item_name = ""
                    category = ""
                    context = (
                        f"market={item['market']};"
                        f"price_type={item['price_type']};"
                        f"currency_code={item['currency_code']}"
                    )
                    unit = str(item["currency_code"])
                    delta = str(
                        item.get("amount_delta_right_minus_left", "")
                    )
                elif domain == "technical":
                    item_code = str(item["attribute_code"])
                    item_name = str(item["attribute_name"])
                    category = str(item["category"])
                    fuel = str(item["fuel_type_code"])
                    context = (
                        f"fuel_type_code={fuel}"
                        if fuel
                        else "fuel_type_code="
                    )
                    if item.get("range_relation"):
                        context += (
                            f";range_relation={item['range_relation']}"
                        )
                    unit = str(item["unit"])
                    delta = ""
                else:
                    item_code = str(item["attribute_code"])
                    item_name = str(item["attribute_name"])
                    category = str(item["category"])
                    context = ""
                    unit = ""
                    delta = ""

                rows.append(
                    {
                        "pair_code": str(pair["pair_code"]),
                        "pair_type": str(pair["pair_type"]),
                        "domain": domain,
                        "comparison": "different",
                        "item_code": item_code,
                        "item_name": item_name,
                        "category": category,
                        "context": context,
                        "unit": unit,
                        "left_configuration_code": str(
                            left_configuration["configuration_code"]
                        ),
                        "left_version_code": str(
                            left_configuration["version_code"]
                        ),
                        "left_transmission_type": str(
                            left_configuration["transmission_type"]
                        ),
                        "left_state": str(left["state"]),
                        "left_value": difference_state_value(
                            left,
                            domain,
                        ),
                        "left_source_code": str(
                            left.get("source_code", "")
                        ),
                        "left_observation_date": difference_state_date(
                            left,
                            domain,
                        ),
                        "right_configuration_code": str(
                            right_configuration["configuration_code"]
                        ),
                        "right_version_code": str(
                            right_configuration["version_code"]
                        ),
                        "right_transmission_type": str(
                            right_configuration["transmission_type"]
                        ),
                        "right_state": str(right["state"]),
                        "right_value": difference_state_value(
                            right,
                            domain,
                        ),
                        "right_source_code": str(
                            right.get("source_code", "")
                        ),
                        "right_observation_date": difference_state_date(
                            right,
                            domain,
                        ),
                        "delta_right_minus_left": delta,
                    }
                )
    return rows


def render_difference_csv(
    report: Mapping[str, Any],
    difference_domain: str | None = None,
    difference_item_code: str | None = None,
    known_item_codes: Sequence[str] | None = None,
) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=DIFFERENCE_CSV_FIELDS,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(
        difference_csv_rows(
            report,
            difference_domain,
            difference_item_code,
            known_item_codes,
        )
    )
    return output.getvalue()


def markdown_cell(value: Any) -> str:
    text = str(value)
    return text.replace("|", r"\|").replace("\n", " ")


def state_label(state: Mapping[str, Any], domain: str) -> str:
    kind = str(state.get("state", ""))
    if kind != "recorded":
        return kind
    if domain == "prices":
        return str(state.get("amount", ""))
    if domain == "technical":
        value = (
            range_state_value(state)
            if "minimum_value" in state
            else str(state.get("value", ""))
        )
        unit = str(state.get("unit", ""))
        return f"{value} {unit}".strip()
    return str(state.get("availability_status", ""))


def render_markdown(report: Mapping[str, Any]) -> str:
    scope = report["scope"]
    summary = report["summary"]
    evidence = report["evidence_summary"]
    lines = [
        "# Configuration Comparison Report",
        "",
        f"As of: `{report['as_of']}`",
        "",
        "## Scope",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Active configurations | {scope['active_configurations']} |",
        (
            "| Pair type filter | "
            f"`{scope['pair_type_filter'] or 'all'}` |"
        ),
        (
            "| Available configuration pairs | "
            f"{scope['unfiltered_pair_count']} |"
        ),
        f"| Selected configuration pairs | {scope['pair_count']} |",
        (
            "| Selected configurations | "
            f"{scope['selected_configurations']} |"
        ),
        f"| Price dimensions | {scope['price_dimensions']} |",
        f"| Technical slots per configuration | {scope['technical_slots']} |",
        f"| Equipment attributes per configuration | {scope['equipment_attributes']} |",
        "",
        "## Comparison summary",
        "",
        "| Domain | Comparisons | Equal | Different | Not comparable |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for domain, label in (
        ("prices", "Prices"),
        ("technical", "Technical values"),
        ("equipment", "Equipment availability"),
    ):
        item = summary[domain]
        lines.append(
            f"| {label} | {item['comparisons']} | {item['equal']} | "
            f"{item['different']} | {item['not_comparable']} |"
        )

    if scope["pair_type_filter"] is not None:
        lines.extend(
            [
                "",
                (
                    "The evidence summary remains global to the active "
                    "configuration scope and is not reduced by pair filtering."
                ),
            ]
        )

    lines.extend(
        [
            "",
            (
                "Evidence states for currently unrecorded applicable slots: "
                f"`not_stated={evidence['not_stated']}`, "
                f"`out_of_scope={evidence['out_of_scope']}`, "
                f"`ambiguous={evidence['ambiguous']}`, "
                f"`found={evidence['found']}`."
            ),
            "",
            (
                "Only comparisons where both configurations have recorded "
                "source-backed states can be `equal` or `different`. Missing, "
                "`not_stated`, `out_of_scope`, `ambiguous` and "
                "`not_applicable` remain `not_comparable`."
            ),
            "",
            "## Pair overview",
            "",
            (
                "| Pair | Pair type | Price differences | Technical "
                "differences | Equipment differences | Not comparable |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for pair in report["pairs"]:
        not_comparable = sum(
            int(pair["summary"][domain]["not_comparable"])
            for domain in ("prices", "technical", "equipment")
        )
        lines.append(
            f"| `{pair['pair_code']}` | `{pair['pair_type']}` | "
            f"{pair['summary']['prices']['different']} | "
            f"{pair['summary']['technical']['different']} | "
            f"{pair['summary']['equipment']['different']} | "
            f"{not_comparable} |"
        )

    for domain, title in (
        ("prices", "Price differences"),
        ("technical", "Technical differences"),
        ("equipment", "Equipment differences"),
    ):
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                (
                    "| Pair | Attribute / dimension | Context | Left | "
                    "Right |"
                ),
                "| --- | --- | --- | --- | --- |",
            ]
        )
        found = False
        for pair in report["pairs"]:
            for item in pair[domain]:
                if item["comparison"] != "different":
                    continue
                found = True
                if domain == "prices":
                    key = (
                        f"{item['market']} / {item['price_type']} / "
                        f"{item['currency_code']}"
                    )
                    context = (
                        "delta "
                        f"{item['amount_delta_right_minus_left']}"
                    )
                elif domain == "technical":
                    key = item["attribute_code"]
                    context = item["fuel_type_code"] or "none"
                else:
                    key = item["attribute_code"]
                    context = item["category"]
                lines.append(
                    f"| `{pair['pair_code']}` | `{markdown_cell(key)}` | "
                    f"{markdown_cell(context)} | "
                    f"{markdown_cell(state_label(item['left'], domain))} | "
                    f"{markdown_cell(state_label(item['right'], domain))} |"
                )
        if not found:
            lines.append("| — | — | — | — | — |")

    lines.append("")
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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic pairwise comparisons for active "
            "configuration prices, technical values and equipment states."
        )
    )
    parser.add_argument(
        "--completeness-spec",
        type=Path,
        default=DEFAULT_COMPLETENESS_SPEC,
    )
    parser.add_argument(
        "--evidence-spec",
        type=Path,
        default=DEFAULT_EVIDENCE_SPEC,
    )
    parser.add_argument("--as-of")
    parser.add_argument(
        "--pair-type",
        choices=PAIR_TYPES,
        help=(
            "Limit output to one deterministic version/transmission "
            "pair classification."
        ),
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument(
        "--difference-domain",
        choices=DIFFERENCE_DOMAINS,
        help=(
            "Limit the flat CSV to price, technical or equipment "
            "differences without changing JSON or Markdown."
        ),
    )
    parser.add_argument(
        "--difference-item-code",
        help=(
            "Limit the flat CSV to one exact item code known to the "
            "full active comparison report."
        ),
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        help="Write a flat CSV containing only actual differences.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    repository = repository_root()
    completeness_spec = arguments.completeness_spec
    evidence_spec = arguments.evidence_spec
    if not completeness_spec.is_absolute():
        completeness_spec = repository / completeness_spec
    if not evidence_spec.is_absolute():
        evidence_spec = repository / evidence_spec

    try:
        report = collect_report(
            repository,
            completeness_spec,
            evidence_spec,
            arguments.as_of,
            arguments.pair_type,
        )
        known_item_codes: tuple[str, ...] | None = None
        if arguments.difference_item_code is not None:
            validation_report = report
            if arguments.pair_type is not None:
                validation_report = collect_report(
                    repository,
                    completeness_spec,
                    evidence_spec,
                    arguments.as_of,
                    None,
                )
            known_item_codes = difference_item_codes(
                validation_report
            )
        if arguments.json_path is not None:
            write_atomic(arguments.json_path, render_json(report))
            print(
                "JSON configuration comparison report written to "
                f"{arguments.json_path}"
            )
        if arguments.markdown is not None:
            write_atomic(
                arguments.markdown,
                render_markdown(report),
            )
            print(
                "Markdown configuration comparison report written to "
                f"{arguments.markdown}"
            )
        if arguments.csv_path is not None:
            write_atomic(
                arguments.csv_path,
                render_difference_csv(
                    report,
                    arguments.difference_domain,
                    arguments.difference_item_code,
                    known_item_codes,
                ),
            )
            print(
                "CSV configuration differences written to "
                f"{arguments.csv_path}"
            )
        print("Configuration comparison")
        print("------------------------")
        print(f"As of                  : {report['as_of']}")
        print(
            "Active configurations  : "
            f"{report['scope']['active_configurations']}"
        )
        print(
            "Pair type filter       : "
            f"{report['scope']['pair_type_filter'] or 'all'}"
        )
        print(
            "Available pairs        : "
            f"{report['scope']['unfiltered_pair_count']}"
        )
        print(f"Selected pairs         : {report['scope']['pair_count']}")
        print(
            "Price differences      : "
            f"{report['summary']['prices']['different']}"
        )
        print(
            "Technical differences  : "
            f"{report['summary']['technical']['different']}"
        )
        print(
            "Equipment differences  : "
            f"{report['summary']['equipment']['different']}"
        )
        print(
            "CSV difference domain   : "
            f"{arguments.difference_domain or 'all'}"
        )
        print(
            "CSV difference item     : "
            f"{arguments.difference_item_code or 'all'}"
        )
        csv_difference_row_count = len(
            difference_csv_rows(
                report,
                arguments.difference_domain,
                arguments.difference_item_code,
                known_item_codes,
            )
        )
        print(
            "CSV difference rows     : "
            f"{csv_difference_row_count}"
        )
        print(
            "Not-comparable states  : "
            f"{sum(report['summary'][domain]['not_comparable'] for domain in ('prices', 'technical', 'equipment'))}"
        )
        return 0
    except ComparisonError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
