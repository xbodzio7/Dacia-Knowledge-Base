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

        if rows:
            header = rows[0]
            data = rows[1:]
        else:
            header = []
            data = []

        row_count = len(data)

        stats["csv_files"] += 1
        stats["rows"] += row_count

        if row_count == 0:
            stats["empty_files"] += 1

        filled = 0
        total = 0

        for row in data:
            padded = row + [""] * (len(header) - len(row))

            for value in padded[: len(header)]:
                total += 1

                if value.strip():
                    filled += 1

        completeness = 100.0 if total == 0 else filled / total * 100

        stats["datasets"].append(
            {
                "name": csv_file.name,
                "rows": row_count,
                "columns": len(header),
                "completeness": completeness,
            }
        )

    stats["datasets"].sort(
        key=lambda dataset: dataset["rows"],
        reverse=True,
    )

    return stats
