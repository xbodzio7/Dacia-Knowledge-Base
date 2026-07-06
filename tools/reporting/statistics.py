from pathlib import Path
import csv


def collect_statistics(root: Path):
    stats = {
        "csv_files": 0,
        "rows": 0,
        "empty_files": 0,
        "datasets": [],
    }

    for csv_file in sorted(root.rglob("*.csv")):
        with csv_file.open(encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))

        count = max(len(rows) - 1, 0)

        stats["csv_files"] += 1
        stats["rows"] += count

        if count == 0:
            stats["empty_files"] += 1

        stats["datasets"].append(
            (csv_file.name, count)
        )

    stats["datasets"].sort(
        key=lambda x: x[1],
        reverse=True,
    )

    return stats
