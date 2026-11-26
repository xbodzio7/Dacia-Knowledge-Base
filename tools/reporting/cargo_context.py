from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


CARGO_ATTRIBUTE_CODE = "boot_capacity"
CARGO_CONTEXT_RELATION = "configuration_cargo_volume_contexts.csv"
CARGO_CONTEXT_FIELDS: tuple[str, ...] = (
    "measurement_basis_code",
    "second_row_state_code",
    "third_row_state_code",
    "compartment_code",
    "spare_wheel_state_code",
    "tyre_repair_kit_state_code",
    "double_floor_state_code",
)


class CargoContextError(ValueError):
    """Raised when cargo measurement context cannot be represented safely."""


def semantic_payload(row: Mapping[str, str]) -> dict[str, str]:
    """Return the exact semantic dimensions of one cargo context row."""

    return {field: str(row.get(field, "")) for field in CARGO_CONTEXT_FIELDS}


def context_payload(row: Mapping[str, str]) -> dict[str, str]:
    """Return semantic dimensions plus traceable relation metadata."""

    payload = {
        "code": str(row.get("code", "")),
        **semantic_payload(row),
        "notes": str(row.get("notes", "")),
    }
    return payload


def semantic_signature(context: Mapping[str, str] | None) -> str:
    """Return a deterministic non-lossy signature for one cargo context."""

    if context is None:
        return ""
    return ";".join(
        f"{field}={str(context.get(field, ''))}"
        for field in CARGO_CONTEXT_FIELDS
    )


def observation_signature(
    gear_number: str = "",
    cargo_context_signature: str = "",
) -> str:
    """Return the non-lossy context signature beyond attribute and fuel."""

    parts: list[str] = []
    if gear_number:
        parts.append(f"gear_number={gear_number}")
    if cargo_context_signature:
        parts.append(cargo_context_signature)
    return ";".join(parts)


def technical_context(
    fuel_type_code: str,
    cargo_context: Mapping[str, str] | None = None,
    gear_number: str = "",
) -> str:
    """Return the exact filter/export context for one technical observation."""

    parts = [f"fuel_type_code={fuel_type_code}"]
    if gear_number:
        parts.append(f"gear_number={gear_number}")
    cargo = semantic_signature(cargo_context)
    if cargo:
        parts.append(cargo)
    return ";".join(parts)


def cargo_context_json(context: Mapping[str, str] | None) -> str:
    """Serialize context deterministically for flat export surfaces."""

    if context is None:
        return ""
    return json.dumps(
        dict(context),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def read_context_rows(
    master: Path,
    read_csv: Callable[[Path], list[dict[str, str]]],
) -> list[dict[str, str]]:
    """Read the optional cargo-context relation, including its header-only state."""

    path = master / CARGO_CONTEXT_RELATION
    return read_csv(path) if path.is_file() else []


def context_index(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, dict[str, str]]:
    """Index context rows by referenced configuration-value code."""

    indexed: dict[str, dict[str, str]] = {}
    for source in rows:
        row = {str(key): str(value) for key, value in source.items()}
        value_code = row.get("configuration_attribute_value_code", "")
        if not value_code:
            raise CargoContextError(
                "cargo context has no configuration_attribute_value_code"
            )
        if value_code in indexed:
            raise CargoContextError(
                "duplicate cargo context for configuration value: "
                f"{value_code}"
            )
        indexed[value_code] = row
    return indexed


def annotate_scalar_values(
    value_rows: Sequence[Mapping[str, str]],
    context_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, Any]]:
    """Attach exact cargo context to a complete or deliberately scoped value set.

    Repository-wide referential integrity is enforced by the master-data validator.
    Reporting callers commonly pass only values for one scope, so context rows owned by
    configurations outside that scope must be ignored rather than treated as dangling.
    """

    values = [dict(row) for row in value_rows]
    values_by_code: dict[str, dict[str, Any]] = {}
    for row in values:
        code = str(row.get("code", ""))
        if not code:
            raise CargoContextError("configuration value has no code")
        if code in values_by_code:
            raise CargoContextError(f"duplicate configuration value code: {code}")
        values_by_code[code] = row

    indexed = context_index(context_rows)
    for code, source_context in indexed.items():
        value = values_by_code.get(code)
        if value is None:
            continue
        attribute_code = str(value.get("attribute_code", ""))
        if attribute_code != CARGO_ATTRIBUTE_CODE:
            raise CargoContextError(
                "cargo context references non-boot_capacity value: "
                f"{code} ({attribute_code})"
            )
        payload = context_payload(source_context)
        value["_cargo_context"] = payload
        value["_cargo_context_signature"] = semantic_signature(payload)

    for value in values:
        value.setdefault("_cargo_context", None)
        value.setdefault("_cargo_context_signature", "")
    return values


def cargo_observations(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return context-aware canonical cargo observations in deterministic order."""

    observations: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("attribute_code", "")) != CARGO_ATTRIBUTE_CODE:
            continue
        context = row.get("_cargo_context")
        observations.append(
            {
                "value_code": str(row.get("code", "")),
                "value": str(row.get("value", "")),
                "fuel_type_code": str(row.get("fuel_type_code", "")),
                "gear_number": str(row.get("gear_number", "")),
                "observation_date": str(row.get("observation_date", "")),
                "source_code": str(row.get("source_code", "")),
                "cargo_context": dict(context) if isinstance(context, Mapping) else None,
                "cargo_context_signature": str(
                    row.get("_cargo_context_signature", "")
                ),
                "context": technical_context(
                    str(row.get("fuel_type_code", "")),
                    context if isinstance(context, Mapping) else None,
                    str(row.get("gear_number", "")),
                ),
            }
        )
    observations.sort(
        key=lambda item: (
            item["cargo_context_signature"],
            item["observation_date"],
            item["value_code"],
        )
    )
    return observations
