from pathlib import Path
import csv
from datetime import datetime


def generate_entity_catalog(root: Path, output: Path):

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as report:

        report.write("# Entity Catalog\n\n")
        report.write(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        master_dir = (
            root / "data" / "master"
        )

        for csv_file in sorted(
            master_dir.rglob("*.csv")
        ):

            relative = csv_file.relative_to(root).as_posix()

            with csv_file.open(
                encoding="utf-8-sig",
                newline=""
            ) as f:

                reader = csv.reader(f)
                rows = list(reader)

            if rows:
                header = rows[0]
                data_rows = len(rows) - 1
            else:
                header = []
                data_rows = 0

            report.write(f"## {relative}\n\n")
            report.write(f"Rows: **{data_rows}**\n\n")

            report.write("Columns:\n\n")

            if header:
                for column in header:
                    report.write(f"- {column}\n")
            else:
                report.write("_No columns_\n")

            report.write("\n")
