from pathlib import Path
import argparse
import csv
import re


def highlight(text: str, phrase: str) -> str:
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    return pattern.sub(lambda m: f"[{m.group(0)}]", text)


def print_row(row_number: int, row: dict, phrase: str):
    print()
    print(f"  Row {row_number}")

    width = max(len(key) for key in row.keys())

    for key, value in row.items():
        value = "" if value is None else str(value)
        print(f"    {key:<{width}} : {highlight(value, phrase)}")


def search(root: Path, phrase: str, field: str | None):

    phrase_lower = phrase.lower()

    for csv_file in sorted(root.rglob("*.csv")):

        found = False

        with csv_file.open(encoding="utf-8", newline="") as f:

            reader = csv.DictReader(f)

            for row_number, row in enumerate(reader, start=2):

                if field:
                    text = str(row.get(field, "")).lower()
                else:
                    text = " ".join(
                        str(v)
                        for v in row.values()
                        if v is not None
                    ).lower()

                if phrase_lower in text:

                    if not found:
                        print()
                        print(csv_file.relative_to(root))
                        found = True

                    print_row(row_number, row, phrase)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--field",
        help="Search only selected column",
    )

    parser.add_argument(
        "phrase",
    )

    args = parser.parse_args()

    repository = Path(__file__).resolve().parents[1]

    search(
        repository,
        args.phrase,
        args.field,
    )


if __name__ == "__main__":
    main()
