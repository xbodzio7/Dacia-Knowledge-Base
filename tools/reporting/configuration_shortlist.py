from __future__ import annotations

import csv
import io
import json
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

REPORT_VERSION = 1
PRICE_MARKET = "PL"
PRICE_TYPE = "catalog_gross"
PRICE_CURRENCY = "PLN"
AVAILABLE_EQUIPMENT_STATES = frozenset({"standard", "optional"})


class ShortlistError(ValueError):
    """Raised when shortlist inputs or repository records are invalid."""


@dataclass(frozen=True)
class ShortlistCriteria:
    as_of: str | None = None
    models: tuple[str, ...] = ()
    versions: tuple[str, ...] = ()
    transmissions: tuple[str, ...] = ()
    powertrains: tuple[str, ...] = ()
    minimum_price: Decimal | None = None
    maximum_price: Decimal | None = None
    seats: int | None = None
    required_equipment: tuple[str, ...] = ()
    required_standard_equipment: tuple[str, ...] = ()


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        raise ShortlistError(f"cannot read {path}: {exc}") from exc


def _iso_date(value: str, label: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ShortlistError(
            f"{label} must use YYYY-MM-DD format: {value!r}"
        ) from exc
    return parsed.isoformat()


def _decimal(value: str | Decimal | None, label: str) -> Decimal | None:
    if value is None or isinstance(value, Decimal):
        return value
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ShortlistError(f"{label} must be numeric: {value!r}") from exc
    if not parsed.is_finite():
        raise ShortlistError(f"{label} must be finite: {value!r}")
    return parsed


def _decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    cleaned = {value.strip() for value in values if value.strip()}
    return tuple(sorted(cleaned))


def normalize_criteria(criteria: ShortlistCriteria) -> ShortlistCriteria:
    minimum = _decimal(criteria.minimum_price, "minimum price")
    maximum = _decimal(criteria.maximum_price, "maximum price")
    if minimum is not None and minimum < 0:
        raise ShortlistError("minimum price cannot be negative")
    if maximum is not None and maximum < 0:
        raise ShortlistError("maximum price cannot be negative")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ShortlistError("minimum price cannot exceed maximum price")
    if criteria.seats is not None and criteria.seats <= 0:
        raise ShortlistError("seats must be a positive integer")

    standard = _unique(criteria.required_standard_equipment)
    general = tuple(
        code
        for code in _unique(criteria.required_equipment)
        if code not in set(standard)
    )
    powertrains = _unique(criteria.powertrains)
    if any(not value for value in powertrains):
        raise ShortlistError("powertrain filters cannot be empty")

    return ShortlistCriteria(
        as_of=(
            _iso_date(criteria.as_of, "--as-of")
            if criteria.as_of is not None
            else None
        ),
        models=_unique(criteria.models),
        versions=_unique(criteria.versions),
        transmissions=_unique(criteria.transmissions),
        powertrains=powertrains,
        minimum_price=minimum,
        maximum_price=maximum,
        seats=criteria.seats,
        required_equipment=general,
        required_standard_equipment=standard,
    )


def _latest(
    rows: Sequence[Mapping[str, str]],
    key_fields: Sequence[str],
    date_field: str,
    as_of: str,
) -> dict[tuple[str, ...], dict[str, str]]:
    selected: dict[tuple[str, ...], dict[str, str]] = {}
    for source_row in rows:
        row = dict(source_row)
        current_date = _iso_date(row.get(date_field, ""), date_field)
        if current_date > as_of:
            continue
        key = tuple(row.get(field, "") for field in key_fields)
        current = selected.get(key)
        if current is None:
            selected[key] = row
            continue
        current_key = (current[date_field], current.get("code", ""))
        candidate_key = (current_date, row.get("code", ""))
        if candidate_key > current_key:
            selected[key] = row
    return selected


def _effective_as_of(
    requested: str | None,
    prices: Sequence[Mapping[str, str]],
    values: Sequence[Mapping[str, str]],
    availability: Sequence[Mapping[str, str]],
) -> str:
    if requested is not None:
        return requested
    candidates = [row.get("price_date", "") for row in prices]
    candidates.extend(row.get("observation_date", "") for row in values)
    candidates.extend(
        row.get("observation_date", "") for row in availability
    )
    valid = [_iso_date(value, "record date") for value in candidates if value]
    if not valid:
        raise ShortlistError("cannot determine an effective report date")
    return max(valid)


def _validate_codes(
    label: str,
    requested: Sequence[str],
    available: set[str],
) -> None:
    unknown = sorted(set(requested) - available)
    if unknown:
        raise ShortlistError(
            f"unknown {label} code(s): {', '.join(unknown)}"
        )


def _price_state(row: Mapping[str, str] | None) -> dict[str, Any]:
    if row is None:
        return {"state": "missing"}
    amount = _decimal(row.get("amount"), "catalogue price")
    if amount is None:
        raise ShortlistError("catalogue price cannot be empty")
    return {
        "state": "recorded",
        "amount": _decimal_text(amount),
        "currency_code": row.get("currency_code", ""),
        "price_date": row.get("price_date", ""),
        "source_code": row.get("source_code", ""),
    }


def _seat_state(row: Mapping[str, str] | None) -> dict[str, Any]:
    if row is None:
        return {"state": "missing"}
    raw_value = row.get("value", "")
    try:
        value = int(Decimal(raw_value))
    except (InvalidOperation, ValueError) as exc:
        raise ShortlistError(
            f"invalid number_of_seats value: {raw_value!r}"
        ) from exc
    return {
        "state": "recorded",
        "value": value,
        "observation_date": row.get("observation_date", ""),
        "source_code": row.get("source_code", ""),
    }


def _equipment_state(
    attribute_code: str,
    row: Mapping[str, str] | None,
    requirement: str,
) -> dict[str, Any]:
    if row is None:
        return {
            "attribute_code": attribute_code,
            "requirement": requirement,
            "state": "missing",
        }
    return {
        "attribute_code": attribute_code,
        "requirement": requirement,
        "state": "recorded",
        "availability_status": row.get("availability_status", ""),
        "observation_date": row.get("observation_date", ""),
        "source_code": row.get("source_code", ""),
    }


def _filters_payload(criteria: ShortlistCriteria) -> dict[str, Any]:
    return {
        "models": list(criteria.models),
        "versions": list(criteria.versions),
        "transmissions": list(criteria.transmissions),
        "powertrains": list(criteria.powertrains),
        "minimum_price_pln": (
            _decimal_text(criteria.minimum_price)
            if criteria.minimum_price is not None
            else None
        ),
        "maximum_price_pln": (
            _decimal_text(criteria.maximum_price)
            if criteria.maximum_price is not None
            else None
        ),
        "seats": criteria.seats,
        "required_equipment": list(criteria.required_equipment),
        "required_standard_equipment": list(
            criteria.required_standard_equipment
        ),
    }


def collect_report(
    repository: Path,
    criteria: ShortlistCriteria,
) -> dict[str, Any]:
    criteria = normalize_criteria(criteria)
    master = repository / "data" / "master"
    model_rows = read_csv(master / "models.csv")
    version_rows = read_csv(master / "versions.csv")
    configuration_rows = read_csv(master / "configurations.csv")
    price_rows = read_csv(master / "configuration_prices.csv")
    value_rows = read_csv(master / "configuration_attribute_values.csv")
    availability_rows = read_csv(
        master / "configuration_attribute_availability.csv"
    )

    configurations = [
        row for row in configuration_rows if row.get("status") == "active"
    ]
    if not configurations:
        raise ShortlistError("no active configurations found")
    configuration_codes = {row["code"] for row in configurations}
    versions = {row["code"]: row for row in version_rows}
    models = {row["code"]: row for row in model_rows}

    for configuration in configurations:
        version_code = configuration.get("version_code", "")
        if version_code not in versions:
            raise ShortlistError(
                f"configuration references unknown version: {version_code!r}"
            )
        model_code = versions[version_code].get("model_code", "")
        if model_code not in models:
            raise ShortlistError(
                f"version references unknown model: {model_code!r}"
            )

    scoped_prices = [
        row
        for row in price_rows
        if row.get("configuration_code") in configuration_codes
        and row.get("market") == PRICE_MARKET
        and row.get("price_type") == PRICE_TYPE
        and row.get("currency_code") == PRICE_CURRENCY
    ]
    scoped_values = [
        row
        for row in value_rows
        if row.get("configuration_code") in configuration_codes
        and row.get("attribute_code") == "number_of_seats"
        and row.get("fuel_type_code", "") == ""
    ]
    scoped_availability = [
        row
        for row in availability_rows
        if row.get("configuration_code") in configuration_codes
    ]
    as_of = _effective_as_of(
        criteria.as_of,
        scoped_prices,
        scoped_values,
        scoped_availability,
    )

    prices = _latest(
        scoped_prices,
        ("configuration_code",),
        "price_date",
        as_of,
    )
    seats = _latest(
        scoped_values,
        ("configuration_code",),
        "observation_date",
        as_of,
    )
    availability = _latest(
        scoped_availability,
        ("configuration_code", "attribute_code"),
        "observation_date",
        as_of,
    )

    active_model_codes = {
        versions[row["version_code"]]["model_code"]
        for row in configurations
    }
    active_version_codes = {row["version_code"] for row in configurations}
    equipment_codes = {
        row.get("attribute_code", "")
        for row in scoped_availability
        if row.get("attribute_code", "")
    }
    _validate_codes("model", criteria.models, active_model_codes)
    _validate_codes("version", criteria.versions, active_version_codes)
    _validate_codes(
        "equipment attribute",
        (
            *criteria.required_equipment,
            *criteria.required_standard_equipment,
        ),
        equipment_codes,
    )

    requirements = [
        (code, "available") for code in criteria.required_equipment
    ]
    requirements.extend(
        (code, "standard")
        for code in criteria.required_standard_equipment
    )

    exclusion_counts: Counter[str] = Counter()
    results: list[dict[str, Any]] = []
    price_missing_total = 0
    seats_missing_total = 0
    equipment_missing_totals: Counter[str] = Counter()

    for configuration in configurations:
        configuration_code = configuration["code"]
        version = versions[configuration["version_code"]]
        model = models[version["model_code"]]
        price_row = prices.get((configuration_code,))
        seat_row = seats.get((configuration_code,))
        price = _price_state(price_row)
        seat = _seat_state(seat_row)
        if price["state"] == "missing":
            price_missing_total += 1
        if seat["state"] == "missing":
            seats_missing_total += 1

        reasons: set[str] = set()
        if criteria.models and model["code"] not in criteria.models:
            reasons.add("model")
        if criteria.versions and version["code"] not in criteria.versions:
            reasons.add("version")
        if (
            criteria.transmissions
            and configuration.get("transmission_type", "")
            not in criteria.transmissions
        ):
            reasons.add("transmission")
        if criteria.powertrains and not any(
            phrase.casefold()
            in configuration.get("powertrain_label", "").casefold()
            for phrase in criteria.powertrains
        ):
            reasons.add("powertrain")

        price_value: Decimal | None = None
        if price["state"] == "recorded":
            price_value = Decimal(str(price["amount"]))
        if criteria.minimum_price is not None:
            if price_value is None:
                reasons.add("price_missing")
            elif price_value < criteria.minimum_price:
                reasons.add("price_below_minimum")
        if criteria.maximum_price is not None:
            if price_value is None:
                reasons.add("price_missing")
            elif price_value > criteria.maximum_price:
                reasons.add("price_above_maximum")

        if criteria.seats is not None:
            if seat["state"] == "missing":
                reasons.add("number_of_seats_missing")
            elif seat["value"] != criteria.seats:
                reasons.add("number_of_seats")

        equipment_states: list[dict[str, Any]] = []
        for attribute_code, requirement in requirements:
            row = availability.get((configuration_code, attribute_code))
            item = _equipment_state(attribute_code, row, requirement)
            equipment_states.append(item)
            if item["state"] == "missing":
                equipment_missing_totals[attribute_code] += 1
                reasons.add(f"equipment_missing:{attribute_code}")
                continue
            state = str(item.get("availability_status", ""))
            if requirement == "standard":
                if state != "standard":
                    reasons.add(
                        f"equipment_not_standard:{attribute_code}"
                    )
            elif state not in AVAILABLE_EQUIPMENT_STATES:
                reasons.add(f"equipment_not_available:{attribute_code}")

        for reason in reasons:
            exclusion_counts[reason] += 1
        if reasons:
            continue

        results.append(
            {
                "configuration_code": configuration_code,
                "model_code": model["code"],
                "model_name": model.get("name", ""),
                "version_code": version["code"],
                "version_name": version.get("name", ""),
                "powertrain_label": configuration.get(
                    "powertrain_label", ""
                ),
                "transmission_type": configuration.get(
                    "transmission_type", ""
                ),
                "catalog_price": price,
                "number_of_seats": seat,
                "required_equipment": equipment_states,
            }
        )

    def sort_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
        price = item["catalog_price"]
        missing = price.get("state") != "recorded"
        amount = (
            Decimal(str(price["amount"]))
            if not missing
            else Decimal("Infinity")
        )
        return (
            missing,
            amount,
            item["model_code"],
            item["version_code"],
            item["configuration_code"],
        )

    results.sort(key=sort_key)
    return {
        "version": REPORT_VERSION,
        "as_of": as_of,
        "price_dimension": {
            "market": PRICE_MARKET,
            "price_type": PRICE_TYPE,
            "currency_code": PRICE_CURRENCY,
        },
        "filters": _filters_payload(criteria),
        "summary": {
            "active_configurations": len(configurations),
            "matched_configurations": len(results),
            "excluded_configurations": len(configurations) - len(results),
            "exclusion_reason_counts": dict(
                sorted(exclusion_counts.items())
            ),
            "data_unknowns": {
                "catalog_price_missing": price_missing_total,
                "number_of_seats_missing": seats_missing_total,
                "required_equipment_missing": dict(
                    sorted(equipment_missing_totals.items())
                ),
            },
        },
        "results": results,
    }


def _markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _filter_lines(filters: Mapping[str, Any]) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    for key in (
        "models",
        "versions",
        "transmissions",
        "powertrains",
        "required_equipment",
        "required_standard_equipment",
    ):
        values = filters.get(key, [])
        lines.append((key, ", ".join(values) if values else "—"))
    for key in ("minimum_price_pln", "maximum_price_pln", "seats"):
        value = filters.get(key)
        lines.append((key, "—" if value is None else str(value)))
    return lines


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Configuration Shortlist",
        "",
        f"As of: `{_markdown(report['as_of'])}`",
        "",
        "## Filters",
        "",
        "| Criterion | Value |",
        "| --- | --- |",
    ]
    lines.extend(
        f"| `{_markdown(key)}` | {_markdown(value)} |"
        for key, value in _filter_lines(report["filters"])
    )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Active configurations: {summary['active_configurations']}",
            f"- Matched configurations: {summary['matched_configurations']}",
            f"- Excluded configurations: {summary['excluded_configurations']}",
            "- Missing catalogue prices: "
            f"{summary['data_unknowns']['catalog_price_missing']}",
            "- Missing seat counts: "
            f"{summary['data_unknowns']['number_of_seats_missing']}",
        ]
    )
    reason_counts = summary["exclusion_reason_counts"]
    if reason_counts:
        lines.extend(["", "### Exclusion reasons", ""])
        lines.extend(
            f"- `{_markdown(reason)}`: {count}"
            for reason, count in reason_counts.items()
        )
    equipment_missing = summary["data_unknowns"][
        "required_equipment_missing"
    ]
    if equipment_missing:
        lines.extend(["", "### Missing equipment statements", ""])
        lines.extend(
            f"- `{_markdown(code)}`: {count}"
            for code, count in equipment_missing.items()
        )

    lines.extend(
        [
            "",
            "## Matches",
            "",
            "| Price | Model | Version | Powertrain | Transmission | "
            "Seats | Required equipment | Configuration |",
            "| ---: | --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for item in report["results"]:
        price = item["catalog_price"]
        price_text = (
            f"{price['amount']} {price['currency_code']}"
            if price["state"] == "recorded"
            else "missing"
        )
        seats = item["number_of_seats"]
        seats_text = (
            str(seats["value"])
            if seats["state"] == "recorded"
            else "missing"
        )
        equipment = "; ".join(
            (
                f"{entry['attribute_code']}="
                f"{entry.get('availability_status', entry['state'])}"
            )
            for entry in item["required_equipment"]
        )
        lines.append(
            "| "
            + " | ".join(
                _markdown(value)
                for value in (
                    price_text,
                    item["model_name"],
                    item["version_name"],
                    item["powertrain_label"],
                    item["transmission_type"],
                    seats_text,
                    equipment or "—",
                    f"`{item['configuration_code']}`",
                )
            )
            + " |"
        )
    if not report["results"]:
        lines.append("| — | — | — | — | — | — | — | No matches |")
    return "\n".join(lines) + "\n"


CSV_FIELDS = (
    "configuration_code",
    "model_code",
    "model_name",
    "version_code",
    "version_name",
    "powertrain_label",
    "transmission_type",
    "catalog_price_pln",
    "price_date",
    "price_source_code",
    "number_of_seats",
    "seats_observation_date",
    "seats_source_code",
    "required_equipment_states",
    "required_equipment_sources",
)


def csv_rows(report: Mapping[str, Any]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for item in report["results"]:
        price = item["catalog_price"]
        seats = item["number_of_seats"]
        equipment = item["required_equipment"]
        output.append(
            {
                "configuration_code": item["configuration_code"],
                "model_code": item["model_code"],
                "model_name": item["model_name"],
                "version_code": item["version_code"],
                "version_name": item["version_name"],
                "powertrain_label": item["powertrain_label"],
                "transmission_type": item["transmission_type"],
                "catalog_price_pln": (
                    str(price.get("amount", ""))
                    if price["state"] == "recorded"
                    else ""
                ),
                "price_date": str(price.get("price_date", "")),
                "price_source_code": str(price.get("source_code", "")),
                "number_of_seats": (
                    str(seats.get("value", ""))
                    if seats["state"] == "recorded"
                    else ""
                ),
                "seats_observation_date": str(
                    seats.get("observation_date", "")
                ),
                "seats_source_code": str(seats.get("source_code", "")),
                "required_equipment_states": ";".join(
                    f"{entry['attribute_code']}="
                    f"{entry.get('availability_status', entry['state'])}"
                    for entry in equipment
                ),
                "required_equipment_sources": ";".join(
                    f"{entry['attribute_code']}="
                    f"{entry.get('source_code', '')}"
                    for entry in equipment
                ),
            }
        )
    return output


def render_csv(report: Mapping[str, Any]) -> str:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
    writer.writeheader()
    writer.writerows(csv_rows(report))
    return handle.getvalue()


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="")
    temporary.replace(path)
