from pathlib import Path

from reporting.statistics import collect_statistics


def main():

    root = Path(__file__).resolve().parents[1]

    stats = collect_statistics(root)

    print("Repository statistics")
    print("---------------------")

    print(f"CSV files   : {stats['csv_files']}")
    print(f"Rows        : {stats['rows']}")
    print(f"Empty files : {stats['empty_files']}")
    print()

    print("Largest datasets")

    for name, rows in stats["datasets"][:10]:
        print(f"{name:<35}{rows:>8}")


if __name__ == "__main__":
    main()
