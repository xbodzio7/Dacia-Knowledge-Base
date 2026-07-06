from pathlib import Path
import csv


REQUIRED_COLUMNS = {
    "id",
    "name",
}


def validate_required_fields(csv_file: Path):
    with csv_file.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return []

        required = [
            column
            for column in REQUIRED_COLUMNS
            if column in reader.fieldnames
        ]

        errors = []

        for row_number, row in enumerate(reader, start=2):
            for column in required:
                value = (row.get(column) or "").strip()

                if not value:
                    errors.append(
                        f"{csv_file}: row {row_number}: missing value in '{column}'"
                    )

        return errors
