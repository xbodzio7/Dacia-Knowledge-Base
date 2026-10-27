from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Sequence


def highlight(text: str, phrase: str) -> str:
    pattern = re.compile(
        re.escape(phrase),
        re.IGNORECASE,
    )
    return pattern.sub(
        lambda match: f"[{match.group(0)}]",
        text,
    )


def print_row(
    row_number: int,
    row: dict[str, str | None],
    phrase: str,
) -> None:
    print()
    print(f"  Row {row_number}")

    width = max(len(key) for key in row)

    for key, value in row.items():
        rendered = "" if value is None else str(value)
        print(
            f"    {key:<{width}} : "
            f"{highlight(rendered, phrase)}"
        )


def _csv_files(
    root: Path,
    export: Path | None,
) -> list[Path]:
    export_resolved = (
        export.resolve()
        if export is not None
        else None
    )

    return [
        csv_file
        for csv_file in sorted(root.rglob("*.csv"))
        if (
            export_resolved is None
            or csv_file.resolve() != export_resolved
        )
    ]


def _export_headers(
    csv_files: list[Path],
) -> list[str]:
    headers: list[str] = []
    seen: set[str] = set()

    for csv_file in csv_files:
        with csv_file.open(
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            for header in reader.fieldnames or []:
                if header not in seen:
                    seen.add(header)
                    headers.append(header)

    return headers


def search(
    root: Path,
    phrase: str,
    field: str | None,
    export: Path | None,
) -> tuple[int, int]:
    phrase_lower = phrase.lower()
    csv_files = _csv_files(root, export)

    matches = 0
    matched_files = 0

    writer: object | None = None
    export_file = None
    export_headers: list[str] = []

    if export is not None:
        export.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        export_headers = _export_headers(csv_files)
        export_file = export.open(
            "w",
            encoding="utf-8",
            newline="",
        )
        writer = csv.writer(export_file)
        writer.writerow([
            "file",
            "row",
            *export_headers,
        ])

    try:
        for csv_file in csv_files:
            found_in_file = False

            with csv_file.open(
                encoding="utf-8-sig",
                newline="",
            ) as handle:
                reader = csv.DictReader(handle)

                for row_number, row in enumerate(
                    reader,
                    start=2,
                ):
                    if field:
                        text = str(
                            row.get(field, "")
                        ).lower()
                    else:
                        text = " ".join(
                            str(value)
                            for value in row.values()
                            if value is not None
                        ).lower()

                    if phrase_lower not in text:
                        continue

                    if not found_in_file:
                        print()
                        print(csv_file.relative_to(root))
                        found_in_file = True
                        matched_files += 1

                    matches += 1
                    print_row(
                        row_number,
                        row,
                        phrase,
                    )

                    if writer is not None:
                        writer.writerow([
                            csv_file.relative_to(
                                root
                            ).as_posix(),
                            row_number,
                            *[
                                row.get(header, "")
                                for header
                                in export_headers
                            ],
                        ])
    finally:
        if export_file is not None:
            export_file.close()

    print()

    if matches == 0:
        print("No matching records found.")
    else:
        print(
            f"Found {matches} matching record(s) "
            f"in {matched_files} file(s)."
        )

        if export is not None:
            print(
                f"Results exported to {export}"
            )

    return matches, matched_files


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--field")
    parser.add_argument("--export")
    parser.add_argument("phrase")
    return parser.parse_args(argv)


def main(
    argv: Sequence[str] | None = None,
) -> int:
    args = parse_args(argv)
    repository = Path(__file__).resolve().parents[1]
    export = (
        Path(args.export)
        if args.export
        else None
    )

    search(
        repository,
        args.phrase,
        args.field,
        export,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
