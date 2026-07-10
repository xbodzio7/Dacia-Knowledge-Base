"""
Statistics collection with robust encoding support.
"""

from pathlib import Path
import csv
from typing import Any


def read_csv_robust(path: Path):
    """Read CSV with multiple encoding attempts."""
    encodings = ["utf-8-sig", "utf-8", "windows-1250", "cp1250"]
    
    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding, newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
            return rows, encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Failed to read {path} with any encoding")


def collect_statistics(root: Path) -> dict[str, Any]:
    """Collect statistics from all CSV files."""
    stats: dict[str, Any] = {
        "csv_files": 0,
        "rows": 0,
        "empty_files": 0,
        "datasets": [],
    }

    for csv_file in sorted(root.rglob("*.csv")):
        if ".git" in csv_file.parts:
            continue

        try:
            rows, encoding = read_csv_robust(csv_file)

            if rows:
                header = rows[0]
                data_rows = rows[1:]
            else:
                header = []
                data_rows = []

            row_count = len(data_rows)

            stats["csv_files"] += 1
            stats["rows"] += row_count

            if row_count == 0:
                stats["empty_files"] += 1

            # Calculate completeness
            filled = 0
            total = 0
            for row in data_rows:
                padded = row + [""] * (len(header) - len(row))
                for value in padded[: len(header)]:
                    total += 1
                    if value and value.strip():
                        filled += 1

            completeness = round(100.0 * filled / total, 1) if total > 0 else 100.0

            stats["datasets"].append({
                "name": csv_file.name,
                "path": str(csv_file.relative_to(root)),
                "rows": row_count,
                "columns": len(header),
                "completeness": completeness,
                "encoding": encoding
            })

        except Exception as e:
            print(f"Warning: Could not process {csv_file.name}: {e}")

    stats["datasets"].sort(key=lambda x: x["rows"], reverse=True)

    return stats