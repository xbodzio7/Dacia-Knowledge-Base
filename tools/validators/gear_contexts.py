from __future__ import annotations

import csv
import re
from pathlib import Path

VALUE_FILE = Path("data/master/configuration_attribute_values.csv")
GEAR_FIELD = "gear_number"
ELIGIBLE_ATTRIBUTES = frozenset({"elasticity_80_120"})
GEAR_PATTERN = re.compile(r"[1-9][0-9]*")


def validate_gear_contexts(root: Path) -> tuple[int, list[str]]:
    """Validate optional selected-gear qualifiers on scalar observations."""

    path = root / VALUE_FILE
    if not path.is_file():
        return 0, [f"missing gear-context source file: {VALUE_FILE.as_posix()}"]

    errors: list[str] = []
    checked = 0
    seen: dict[tuple[str, str, str, str, str], int] = {}
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            if GEAR_FIELD not in fields:
                return 0, [f"{VALUE_FILE.as_posix()} has no {GEAR_FIELD} column"]
            for row_number, row in enumerate(reader, start=2):
                checked += 1
                gear = row.get(GEAR_FIELD, "")
                if not gear:
                    continue
                prefix = f"{VALUE_FILE.as_posix()}:{row_number}"
                if GEAR_PATTERN.fullmatch(gear) is None:
                    errors.append(
                        f"{prefix}: gear_number must be a canonical positive integer"
                    )
                    continue
                attribute = row.get("attribute_code", "")
                if attribute not in ELIGIBLE_ATTRIBUTES:
                    errors.append(
                        f"{prefix}: gear_number is not allowed for attribute {attribute!r}"
                    )
                    continue
                semantic = (
                    row.get("configuration_code", ""),
                    attribute,
                    row.get("fuel_type_code", ""),
                    gear,
                    row.get("observation_date", ""),
                )
                previous = seen.get(semantic)
                if previous is not None:
                    errors.append(
                        f"{prefix}: duplicate selected-gear observation "
                        f"(first seen at row {previous})"
                    )
                else:
                    seen[semantic] = row_number
    except (OSError, csv.Error) as exc:
        return checked, [f"cannot validate gear context: {exc}"]
    return checked, errors
