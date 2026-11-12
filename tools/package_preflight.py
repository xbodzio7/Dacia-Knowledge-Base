"""Fail-fast structural preflight for repository data files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.validators.csv_validator import validate_csv


def validate_data_tree(repository: Path) -> list[str]:
    """Validate every data CSV and JSON file without modifying repository data."""
    data_root = repository / "data"
    if not data_root.is_dir():
        return [f"Data directory not found: {data_root}"]

    errors: list[str] = []
    csv_paths = sorted(data_root.rglob("*.csv"))
    json_paths = sorted(data_root.rglob("*.json"))

    for path in csv_paths:
        valid, file_errors = validate_csv(path)
        if not valid:
            errors.extend(
                f"{path.relative_to(repository)}: {error}"
                for error in file_errors
            )

    for path in json_paths:
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except UnicodeDecodeError:
            errors.append(
                f"{path.relative_to(repository)}: file is not valid UTF-8"
            )
        except json.JSONDecodeError as exc:
            errors.append(
                f"{path.relative_to(repository)}: invalid JSON at line "
                f"{exc.lineno}, column {exc.colno}: {exc.msg}"
            )
        except OSError as exc:
            errors.append(
                f"{path.relative_to(repository)}: cannot read file: {exc}"
            )

    return errors


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    errors = validate_data_tree(repository)
    if errors:
        print("Package preflight failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    csv_count = len(list((repository / "data").rglob("*.csv")))
    json_count = len(list((repository / "data").rglob("*.json")))
    print(
        "Package preflight passed: "
        f"{csv_count} CSV files and {json_count} JSON files are structurally valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
