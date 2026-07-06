from pathlib import Path
import csv
import sys


def search(root: Path, phrase: str):

    phrase = phrase.lower()

    for csv_file in sorted(root.rglob("*.csv")):

        found = False

        with csv_file.open(
            encoding="utf-8",
            newline=""
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                text = " ".join(
                    str(v)
                    for v in row.values()
                    if v is not None
                ).lower()

                if phrase in text:

                    if not found:
                        print(csv_file.relative_to(root))
                        found = True

                    print(" ", row)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python tools/search.py <phrase>")
        raise SystemExit(1)

    repository = Path(__file__).resolve().parents[1]

    search(repository, sys.argv[1])
