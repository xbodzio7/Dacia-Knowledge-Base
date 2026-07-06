from pathlib import Path
from datetime import datetime


def write_validation_report(
    output: Path,
    repository_ok: bool,
    csv_ok: bool,
    statistics: dict,
):
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as f:
        f.write("# Validation Report\n\n")
        f.write(
            f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n"
        )

        f.write("## Status\n\n")

        f.write(
            f"- Repository validation: {'PASS' if repository_ok else 'FAIL'}\n"
        )
        f.write(
            f"- CSV validation: {'PASS' if csv_ok else 'FAIL'}\n\n"
        )

        f.write("## Statistics\n\n")
        f.write(f"- CSV files: {statistics['csv_files']}\n")
        f.write(f"- Rows: {statistics['rows']}\n")
        f.write(f"- Empty files: {statistics['empty_files']}\n\n")

        f.write("## Largest datasets\n\n")

        for name, rows in statistics["datasets"][:10]:
            f.write(f"- {name}: {rows}\n")
