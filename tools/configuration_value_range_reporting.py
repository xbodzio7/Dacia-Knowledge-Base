"""Shared helpers for reporting scalar and range configuration observations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, TypeVar

ErrorType = TypeVar("ErrorType", bound=Exception)


def read_optional_ranges(master: Path, read_csv: Any) -> list[dict[str, str]]:
    """Read the canonical range table when present; keep legacy fixtures valid."""

    path = master / "configuration_attribute_value_ranges.csv"
    return read_csv(path) if path.is_file() else []


def combine_latest_observations(
    scalar_rows: Mapping[tuple[str, ...], dict[str, str]],
    range_rows: Mapping[tuple[str, ...], dict[str, str]],
    error_type: type[ErrorType],
) -> dict[tuple[str, ...], dict[str, str]]:
    """Choose the latest scalar or range row for each semantic key."""

    result: dict[tuple[str, ...], dict[str, str]] = {}
    for key in sorted(set(scalar_rows) | set(range_rows)):
        scalar = scalar_rows.get(key)
        ranged = range_rows.get(key)
        if scalar is None:
            selected = dict(ranged or {})
            selected["_observation_kind"] = "range"
            result[key] = selected
            continue
        if ranged is None:
            result[key] = scalar
            continue
        try:
            scalar_date = date.fromisoformat(scalar.get("observation_date", ""))
            range_date = date.fromisoformat(ranged.get("observation_date", ""))
        except ValueError as exc:
            raise error_type(f"invalid observation date while merging {key}") from exc
        if scalar_date == range_date:
            raise error_type(
                f"scalar and range observations collide on the same date: {key}"
            )
        if range_date > scalar_date:
            selected = dict(ranged)
            selected["_observation_kind"] = "range"
            result[key] = selected
        else:
            result[key] = scalar
    return result


def _decimal(value: Any) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"invalid numeric comparison value: {value!r}") from exc
    if not parsed.is_finite():
        raise ValueError(f"non-finite numeric comparison value: {value!r}")
    return parsed


def _interval(state: Mapping[str, Any]) -> tuple[Decimal, Decimal, bool, bool]:
    if "minimum_value" in state:
        return (
            _decimal(state["minimum_value"]),
            _decimal(state["maximum_value"]),
            bool(state["lower_inclusive"]),
            bool(state["upper_inclusive"]),
        )
    point = _decimal(state["normalized_value"])
    return point, point, True, True


def range_relation(left: Mapping[str, Any], right: Mapping[str, Any]) -> str:
    """Return identical, overlapping or disjoint for numeric states."""

    left_min, left_max, left_lower, left_upper = _interval(left)
    right_min, right_max, right_lower, right_upper = _interval(right)
    if (
        left_min == right_min
        and left_max == right_max
        and left_lower == right_lower
        and left_upper == right_upper
    ):
        return "identical"
    if left_max < right_min or right_max < left_min:
        return "disjoint"
    if left_max == right_min and not (left_upper and right_lower):
        return "disjoint"
    if right_max == left_min and not (right_upper and left_lower):
        return "disjoint"
    return "overlapping"
