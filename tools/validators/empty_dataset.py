from pathlib import Path
import csv


def validate_empty_dataset(csv_file: Path):
    with csv_file.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) <= 1:
        return [
            f"{csv_file}: dataset contains no data rows"
        ]

    return []
