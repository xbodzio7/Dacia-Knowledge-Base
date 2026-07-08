from pathlib import Path
import csv
from datetime import datetime


def generate_data_dictionary(root: Path, output: Path):

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as report:

        report.write("# Data Dictionary\n\n")
        report.write(
            f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
        )

        for csv_file in sorted(root.rglob("*.csv")):

            relative = csv_file.relative_to(root)

            with csv_file.open(
                encoding="utf-8",
                newline=""
            ) as f:

                reader = csv.DictReader(f)

                fieldnames = reader.fieldnames or []
                rows = list(reader)

            report.write(f"## {relative}\n\n")
            report.write(f"Rows: **{len(rows)}**\n\n")

            report.write(
                "| Column | Filled | Coverage | Status |\n"
            )
            report.write(
                "|--------|-------:|---------:|--------|\n"
            )

            columns = []

            for field in fieldnames:

                filled = sum(
                    1
                    for row in rows
                    if (row.get(field) or "").strip()
                )

                coverage = (
                    100.0
                    if not rows
                    else filled / len(rows) * 100
                )

                if coverage == 100.0:
                    status = "OK"
                elif coverage == 0.0:
                    status = "EMPTY"
                else:
                    status = "PARTIAL"

                columns.append(
                    (coverage, field, filled, status)
                )

            for coverage, field, filled, status in sorted(
                columns,
                key=lambda item: (item[0], item[1])
            ):
                report.write(
                    f"| {field} | {filled} | {coverage:.1f}% | {status} |\n"
                )

            report.write("\n")
