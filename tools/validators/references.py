from pathlib import Path
import csv


def load_ids(csv_file: Path) -> set[str]:
    with csv_file.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if "id" not in reader.fieldnames:
            return set()

        return {
            (row["id"] or "").strip()
            for row in reader
            if (row["id"] or "").strip()
        }


def validate_references(root: Path):
    datasets = {}

    for csv_file in root.rglob("*.csv"):
        datasets[csv_file.stem] = load_ids(csv_file)

    errors = []

    for csv_file in root.rglob("*.csv"):

        with csv_file.open(encoding="utf-8", newline="") as f:

            reader = csv.DictReader(f)

            if not reader.fieldnames:
                continue

            reference_columns = [
                c
                for c in reader.fieldnames
                if c.endswith("_id")
            ]

            for row_number, row in enumerate(reader, start=2):

                for column in reference_columns:

                    value = (row.get(column) or "").strip()

                    if not value:
                        continue

                    target = column[:-3]

                    if target not in datasets:
                        continue

                    if value not in datasets[target]:

                        errors.append(
                            f"{csv_file}: row {row_number}: "
                            f"{column}='{value}' does not exist "
                            f"in {target}.csv"
                        )

    return errors
