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
    print(f"{'Dataset':35} {'Rows':>8} {'Cols':>6} {'Complete':>11}")

    for dataset in stats["datasets"][:10]:
        print(
            f"{dataset['name']:<35}"
            f"{dataset['rows']:>8}"
            f"{dataset['columns']:>6}"
            f"{dataset['completeness']:>10.1f}%"
        )


if __name__ == "__main__":
    main()
