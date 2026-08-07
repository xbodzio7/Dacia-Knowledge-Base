from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping


CONFIGURATOR_OBSERVATION_KIND = "configurator_observation"
_CONFIGURATOR_COMMERCIAL_REPORT = "cross_model_configurator_commercial_data.json"
_CONFIGURATOR_STANDARD_EQUIPMENT_REPORT = (
    "cross_model_configurator_standard_equipment.json"
)
_CONFIGURATOR_TECHNICAL_DATA_REPORT = "cross_model_configurator_technical_data.json"
_CONFIGURATOR_CONFLICT_CLOSURE_REPORT = (
    "cross_model_configurator_conflict_closure.json"
)
_CONFIGURATOR_REPORTS = (
    _CONFIGURATOR_COMMERCIAL_REPORT,
    _CONFIGURATOR_STANDARD_EQUIPMENT_REPORT,
    _CONFIGURATOR_TECHNICAL_DATA_REPORT,
    _CONFIGURATOR_CONFLICT_CLOSURE_REPORT,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _eligible(value: str, as_of: str) -> bool:
    if not value:
        return True
    return date.fromisoformat(value) <= date.fromisoformat(as_of)


def _read_json_object(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return payload


def _unique_by_code(rows: object, *, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError(f"{label} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{label} contains a non-object row")
        code = str(row.get("configuration_code", "")).strip()
        if not code:
            raise ValueError(f"{label} contains a row without configuration_code")
        if code in result:
            raise ValueError(f"{label} contains duplicate configuration_code {code}")
        result[code] = row
    return result


def _source_categories(
    row: Mapping[str, Any],
    *,
    label: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    categories: list[dict[str, Any]] = []
    source_lines: list[str] = []
    raw_categories = row.get("categories", [])
    if not isinstance(raw_categories, list):
        raise ValueError(f"{label} categories must be a list")
    for category in raw_categories:
        if not isinstance(category, dict):
            raise ValueError(f"{label} category must be an object")
        lines = category.get("source_lines", [])
        if not isinstance(lines, list) or not all(isinstance(line, str) for line in lines):
            raise ValueError(f"{label} source lines must be strings")
        normalized_lines = [line for line in lines if line]
        categories.append(
            {
                "category": str(category.get("category", "")),
                "source_lines": normalized_lines,
            }
        )
        source_lines.extend(normalized_lines)
    return categories, source_lines


def _collect_configurator_observations(
    repository: Path,
    configuration_codes: set[str],
    as_of: str,
) -> dict[str, dict[str, Any]]:
    reporting = repository / "data" / "reporting"
    paths = {name: reporting / name for name in _CONFIGURATOR_REPORTS}
    present = {name for name, path in paths.items() if path.is_file()}
    if not present:
        return {}
    if present != set(paths):
        missing = ", ".join(sorted(set(paths) - present))
        raise ValueError(f"incomplete configurator observation bundle; missing: {missing}")

    commercial = _read_json_object(paths[_CONFIGURATOR_COMMERCIAL_REPORT])
    standard = _read_json_object(paths[_CONFIGURATOR_STANDARD_EQUIPMENT_REPORT])
    technical = _read_json_object(paths[_CONFIGURATOR_TECHNICAL_DATA_REPORT])
    closure = _read_json_object(paths[_CONFIGURATOR_CONFLICT_CLOSURE_REPORT])

    if int(closure.get("unresolved_identity_conflicts", -1)) != 0:
        raise ValueError("configurator observation bundle has unresolved identity conflicts")
    if not closure.get("closure_policy", {}).get("no_cross_phase_promotion"):
        raise ValueError("configurator observation bundle does not preserve phase boundaries")

    commercial_rows = _unique_by_code(commercial.get("rows"), label="commercial rows")
    standard_rows = _unique_by_code(
        standard.get("documents"),
        label="standard-equipment documents",
    )
    technical_rows = _unique_by_code(
        technical.get("documents"),
        label="technical-data documents",
    )
    closure_rows = _unique_by_code(closure.get("rows"), label="identity closure rows")
    expected_codes = set(closure_rows)
    if (
        set(commercial_rows) != expected_codes
        or set(standard_rows) != expected_codes
        or set(technical_rows) != expected_codes
    ):
        raise ValueError("configurator observation bundle configuration sets do not match")

    source_codes = {
        str(commercial.get("source_code", "")),
        str(standard.get("source_code", "")),
        str(technical.get("source_code", "")),
        str(closure.get("source_code", "")),
    }
    observed_dates = {
        str(commercial.get("observed_on", "")),
        str(standard.get("observed_on", "")),
        str(technical.get("observed_on", "")),
        str(closure.get("observed_on", "")),
    }
    if len(source_codes) != 1 or "" in source_codes:
        raise ValueError("configurator observation bundle source codes do not match")
    if len(observed_dates) != 1 or "" in observed_dates:
        raise ValueError("configurator observation bundle observation dates do not match")
    observed_on = next(iter(observed_dates))
    if not _eligible(observed_on, as_of):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for exact_code in sorted(expected_codes):
        mapping = closure_rows[exact_code]
        canonical_code = str(mapping.get("canonical_configuration_code", "")).strip()
        if not canonical_code:
            raise ValueError(f"identity closure row {exact_code} has no canonical code")
        if canonical_code in result:
            raise ValueError(f"duplicate canonical configurator observation {canonical_code}")
        if canonical_code not in configuration_codes:
            continue

        commercial_row = commercial_rows[exact_code]
        standard_row = standard_rows[exact_code]
        technical_row = technical_rows[exact_code]
        standard_categories, standard_source_lines = _source_categories(
            standard_row,
            label=f"standard-equipment data for {exact_code}",
        )
        technical_categories, technical_source_lines = _source_categories(
            technical_row,
            label=f"technical data for {exact_code}",
        )
        standard_filename = str(standard_row.get("filename", ""))
        technical_filename = str(technical_row.get("filename", ""))
        if standard_filename != technical_filename:
            raise ValueError(
                f"configurator observation filenames differ for {exact_code}"
            )

        result[canonical_code] = {
            "code": f"{CONFIGURATOR_OBSERVATION_KIND}::{exact_code}",
            "name": "Dokładna obserwacja zapisanej konfiguracji producenta",
            "kind": CONFIGURATOR_OBSERVATION_KIND,
            "availability_status": "observed_exact_saved_configuration",
            "amount": None,
            "currency_code": "PLN",
            "price_date": observed_on,
            "source_code": next(iter(source_codes)),
            "equipment_codes": [],
            "equipment_source_texts": {},
            "exact_configuration_code": exact_code,
            "canonical_configuration_code": canonical_code,
            "identity_classification": str(mapping.get("classification", "")),
            "source_phase": str(mapping.get("source_phase") or commercial_row.get("phase", "")),
            "model_family": str(commercial_row.get("model_family", "")),
            "grade": str(commercial_row.get("grade", "")),
            "powertrain": str(commercial_row.get("powertrain", "")),
            "observed_on": observed_on,
            "filename": standard_filename,
            "source_pages": list(standard_row.get("source_pages", [])),
            "technical_data_source_pages": list(
                technical_row.get("source_pages", technical.get("source_pages", []))
            ),
            "selected_colour": {
                "value": str(commercial_row.get("colour", "")),
                "price_pln": commercial_row.get("colour_price_pln"),
                "source_page": commercial_row.get("source_page"),
            },
            "selected_wheels": {
                "value": str(commercial_row.get("wheels", "")),
                "price_pln": commercial_row.get("wheels_price_pln"),
                "source_page": commercial_row.get("source_page"),
            },
            "selected_upholstery": {
                "value": str(commercial_row.get("upholstery", "")),
                "price_pln": commercial_row.get("upholstery_price_pln"),
                "source_page": commercial_row.get("source_page"),
            },
            "standard_equipment_categories": standard_categories,
            "standard_equipment_source_lines": standard_source_lines,
            "technical_data_categories": technical_categories,
            "technical_data_source_lines": technical_source_lines,
            "exact_saved_configuration_only": True,
            "semantic_technical_line_coercion_performed": False,
        }
    return result


def collect_commercial_components(
    repository: Path,
    configuration_codes: Iterable[str],
    as_of: str,
) -> dict[str, list[dict[str, Any]]]:
    requested = set(configuration_codes)
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)

    master = repository / "data" / "master"
    required = (
        master / "commercial_items.csv",
        master / "commercial_item_attributes.csv",
        master / "commercial_item_configurations.csv",
    )
    if all(path.is_file() for path in required):
        items = {
            row["code"]: row
            for row in read_csv(master / "commercial_items.csv")
            if row.get("status") == "active"
            and _eligible(row.get("observation_date", ""), as_of)
        }
        attributes: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in read_csv(master / "commercial_item_attributes.csv"):
            if row.get("commercial_item_code") in items:
                attributes[row["commercial_item_code"]].append(row)

        # Offer availability and an exact saved-configuration selected state are
        # distinct observations. Keep the latest row for each status first,
        # then merge both meanings into one logical UI component. This prevents
        # a later `standard` observation from hiding an earlier valid `optional`
        # offer and its exact price.
        latest_by_status: dict[tuple[str, str, str], dict[str, str]] = {}
        for row in read_csv(master / "commercial_item_configurations.csv"):
            configuration_code = row.get("configuration_code", "")
            item_code = row.get("commercial_item_code", "")
            if configuration_code not in requested or item_code not in items:
                continue
            if not _eligible(row.get("price_date", ""), as_of):
                continue
            status = row.get("availability_status", "")
            key = (configuration_code, item_code, status)
            previous = latest_by_status.get(key)
            if previous is None or row.get("price_date", "") > previous.get("price_date", ""):
                latest_by_status[key] = row

        grouped: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
        for (configuration_code, item_code, status), row in latest_by_status.items():
            grouped[(configuration_code, item_code)][status] = row

        for (configuration_code, item_code), states in sorted(grouped.items()):
            item = items[item_code]
            member_rows = sorted(
                attributes.get(item_code, []),
                key=lambda row: row["attribute_code"],
            )
            selector_mapping = states.get("optional")
            if selector_mapping is None:
                selector_mapping = max(
                    states.values(),
                    key=lambda row: (row.get("price_date", ""), row.get("code", "")),
                )
            selected_mapping = states.get("standard")
            amount_text = selector_mapping.get("amount", "")
            result[configuration_code].append(
                {
                    "code": item_code,
                    "name": item.get("name", item_code),
                    "kind": item.get("item_type", "option"),
                    "availability_status": selector_mapping.get("availability_status", ""),
                    "amount": float(amount_text) if amount_text else None,
                    "currency_code": selector_mapping.get("currency_code", "PLN"),
                    "price_date": selector_mapping.get("price_date", ""),
                    "source_code": selector_mapping.get("source_code", ""),
                    "equipment_codes": [row["attribute_code"] for row in member_rows],
                    "equipment_source_texts": {
                        row["attribute_code"]: row.get("source_text", "")
                        for row in member_rows
                    },
                    "selected_state_observed": selected_mapping is not None,
                    "selected_state_observation_date": (
                        selected_mapping.get("price_date", "") if selected_mapping else ""
                    ),
                    "selected_state_source_code": (
                        selected_mapping.get("source_code", "") if selected_mapping else ""
                    ),
                }
            )

    observations = _collect_configurator_observations(repository, requested, as_of)
    for configuration_code, observation in sorted(observations.items()):
        result[configuration_code].append(observation)
    return dict(result)


def commercial_offer_rows(
    repository: Path,
    configuration_codes: Iterable[str],
    as_of: str,
) -> list[dict[str, Any]]:
    components = collect_commercial_components(repository, configuration_codes, as_of)
    rows: list[dict[str, Any]] = []
    for configuration_code in sorted(components):
        for item in components[configuration_code]:
            if item.get("kind") == CONFIGURATOR_OBSERVATION_KIND:
                continue
            rows.append({"configuration_code": configuration_code, **item})
    return rows
