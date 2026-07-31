"""Backward-compatible projections around the 2026-07-03 catalogue completion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, TypeVar

CATALOG_COMPLETION_RELATIVE_PATH = Path(
    "data/imports/catalog_completion/sandero-stepway-tce-20260703.json"
)
ADDED_CONFIGURATION_CODES = frozenset(
    {
        "sandero_iii_essential_tce100_manual",
        "sandero_iii_expression_tce100_manual",
        "sandero_iii_journey_tce100_manual",
        "sandero_stepway_iii_essential_tce110_manual",
        "sandero_stepway_iii_expression_tce110_manual",
        "sandero_stepway_iii_extreme_tce110_manual",
    }
)
ADDED_SCOPE_SLUG = "sandero_tce100_stepway_tce110_manual"
LATER_CONFIGURATION_CODES = frozenset(
    {
        "spring_essential_electric70_automatic",
        "spring_expression_electric70_automatic",
        "spring_extreme_electric100_automatic",
    }
)
LATER_SCOPE_SLUGS = frozenset({"spring_electric70_automatic", "spring_electric100_automatic"})

T = TypeVar("T", bound=Mapping[str, str])


def completion_applied(repository: Path) -> bool:
    path = repository / CATALOG_COMPLETION_RELATIVE_PATH
    if not path.is_file():
        return False
    payload = json.loads(path.read_text(encoding="utf-8"))
    actual = set(payload.get("configuration_codes", []))
    if actual != ADDED_CONFIGURATION_CODES:
        raise ValueError("catalogue completion configuration scope differs")
    return True


def pre_completion_rows(
    repository: Path,
    rows: Iterable[T],
    *,
    code_field: str = "code",
) -> list[T]:
    materialized = list(rows)
    if not completion_applied(repository):
        return materialized
    excluded = ADDED_CONFIGURATION_CODES | LATER_CONFIGURATION_CODES
    return [row for row in materialized if row.get(code_field) not in excluded]


def pre_completion_scope_paths(repository: Path, paths: Iterable[Path]) -> list[Path]:
    materialized = list(paths)
    if not completion_applied(repository):
        return materialized
    excluded_suffixes = {
        f"{ADDED_SCOPE_SLUG}_completeness.json",
        *(f"{slug}_completeness.json" for slug in LATER_SCOPE_SLUGS),
    }
    return [path for path in materialized if path.name not in excluded_suffixes]
