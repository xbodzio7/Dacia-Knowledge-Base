from pathlib import Path
import csv


def validate_duplicates(csv_file: Path):
    with csv_file.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return []

        if "id" not in reader.fieldnames:
            return []

        seen = {}
        errors = []

        for row_number, row in enumerate(reader, start=2):
            identifier = row["id"].strip()

            if not identifier:
                continue

            if identifier in seen:
                errors.append(
                    f"{csv_file}: duplicate id '{identifier}' "
                    f"(rows {seen[identifier]} and {row_number})"
                )
            else:
                seen[identifier] = row_number

        return errors
