"""Jogger equipment availability constants."""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "data" / "master"
SOURCE = ROOT / "PDF" / "Cenniki" / "DACIA JOGGER cennik MY26 20260401.pdf"
SOURCE_CODE = "src_pl_jogger_price_my26_20260401"
SOURCE_SHA256 = "f0272cac35c4260d95f45d9143a29cf6b3098113d269055dc9665a69238712f1"
DATE = "2026-04-01"
MATRICES = (
    ROOT / "data/imports/jogger_equipment_availability_safety_20260401.csv",
    ROOT / "data/imports/jogger_equipment_availability_comfort_20260401.csv",
)
OUTPUT = MASTER / "configuration_attribute_availability.csv"
OUTPUT_FIELDS = ("id", "code", "configuration_code", "attribute_code", "availability_status", "observation_date", "source_code", "notes")
MATRIX_FIELDS = ("attribute_code", "source_pages", "source_label", "essential", "expression_non_hybrid", "expression_hybrid", "extreme", "journey", "notes")
STATUS_COUNTS = {"standard": 920, "optional": 84, "not_available": 162}
STATUSES = frozenset(STATUS_COUNTS)

class ContractError(RuntimeError):
    pass

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
