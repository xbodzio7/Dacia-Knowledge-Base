"""Constants and CSV helpers for Duster equipment availability."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "data" / "master"
SOURCE = ROOT / "PDF" / "Cenniki" / "DACIA DUSTER cennik MY26 PY25.pdf"
SOURCE_CODE = "src_pl_duster_price_my26_py25_20260206"
SOURCE_SHA256 = "f6126fd4546031c643248b0e19639aa5736e54f8088567460681c938be3932b7"
DATE = "2026-02-06"
MATRICES = (
    ROOT / "data" / "imports" / "duster_equipment_availability_appearance.csv",
    ROOT / "data" / "imports" / "duster_equipment_availability_control.csv",
)
OUTPUT = MASTER / "configuration_attribute_availability.csv"
OUTPUT_FIELDS = (
    "id", "code", "configuration_code", "attribute_code",
    "availability_status", "observation_date", "source_code", "notes",
)
MATRIX_FIELDS = (
    "attribute_code", "source_pages", "source_label",
    "legacy_essential", "legacy_expression", "legacy_extreme",
    "legacy_journey", "legacy_journey_plus",
    "current_essential", "current_expression", "current_extreme",
    "current_journey", "notes",
)
STATUS_COUNTS = {"standard": 1092, "optional": 112, "not_available": 188}
STATUSES = frozenset(STATUS_COUNTS)
LEGACY = ("_ecog100_", "_mildhybrid130_", "_hybrid140_")
CURRENT = ("_ecog120_", "_mildhybrid140_", "_hybrid155_")


class ContractError(RuntimeError):
    """Raised when the source-backed contract cannot be reproduced."""


def read_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ContractError(f"missing CSV header: {path}")
            return list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc


def require_header(path: Path, fields: tuple[str, ...]) -> None:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle), None)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise ContractError(f"cannot inspect {path}: {exc}") from exc
    if header != list(fields):
        raise ContractError(f"unexpected header in {path}: {header!r}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot read source {path}: {exc}") from exc
    return digest.hexdigest()
