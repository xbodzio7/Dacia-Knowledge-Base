from __future__ import annotations

import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))
import documentation_baseline as baseline  # noqa: E402


class DocumentationBaselineTests(unittest.TestCase):
    def write_csv(
        self,
        path: Path,
        header: list[str],
        rows: list[list[str]],
    ) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def make_repository(self, root: Path) -> Path:
        repository = root / "repository"
        master = repository / "data" / "master"
        imports = (
            repository
            / "data"
            / "imports"
            / "configuration_values"
        )
        tests = repository / "tests"
        tools = repository / "tools"
        master.mkdir(parents=True)
        imports.mkdir(parents=True)
        tests.mkdir(parents=True)
        tools.mkdir(parents=True)

        self.write_csv(
            master / "attributes.csv",
            ["id", "code"],
            [["1", "a"], ["2", "b"]],
        )
        self.write_csv(
            master / "attribute_categories.csv",
            ["id", "code"],
            [["1", "general"]],
        )
        self.write_csv(
            master / "configuration_attribute_values.csv",
            ["id", "code"],
            [["1", "x"], ["2", "y"], ["3", "z"]],
        )
        self.write_csv(
            master / "configuration_attribute_availability.csv",
            ["id", "availability_status"],
            [
                ["1", "standard"],
                ["2", "standard"],
                ["3", "optional"],
                ["4", "not_available"],
                ["5", "unknown"],
            ],
        )
        self.write_csv(
            master / "configuration_prices.csv",
            ["id", "price"],
            [["1", "100"]],
        )
        (imports / "one.json").write_text("{}\n", encoding="utf-8")
        (imports / "two.json").write_text("{}\n", encoding="utf-8")
        (tools / "validate_dkb.py").write_text(
            'print("DKB Validator v9.9")\n',
            encoding="utf-8",
        )
        (tools / "__init__.py").write_text(
            "",
            encoding="utf-8",
        )
        (tools / "fixture_module.py").write_text(
            "VALUE = 1\n",
            encoding="utf-8",
        )
        (tests / "test_fixture_baseline.py").write_text(
            "import unittest\n"
            "from tools.fixture_module import VALUE\n\n"
            "class FixtureTests(unittest.TestCase):\n"
            "    def test_one(self):\n"
            "        self.assertEqual(VALUE, 1)\n\n"
            "    def test_two(self):\n"
            "        pass\n",
            encoding="utf-8",
        )
        return repository

    def add_documents(self, repository: Path) -> None:
        for relative_path, (start, end) in baseline.MARKERS.items():
            path = repository / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"Before\n{start}\nstale\n{end}\nAfter\n",
                encoding="utf-8",
            )

    def build_database(self, repository: Path, database: Path) -> None:
        connection = sqlite3.connect(database)
        try:
            for csv_file in sorted(
                (repository / "data" / "master").rglob("*.csv")
            ):
                with csv_file.open(
                    "r",
                    encoding="utf-8-sig",
                    newline="",
                ) as handle:
                    rows = list(csv.reader(handle))
                headers = rows[0]
                data = rows[1:]
                columns = ", ".join(
                    f'"{name}" TEXT' for name in headers
                )
                connection.execute(
                    f'CREATE TABLE "{csv_file.stem}" ({columns})'
                )
                if data:
                    placeholders = ", ".join("?" for _ in headers)
                    connection.executemany(
                        f'INSERT INTO "{csv_file.stem}" '
                        f"VALUES ({placeholders})",
                        data,
                    )
            connection.commit()
        finally:
            connection.close()

    def test_collects_deterministic_source_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.make_repository(Path(directory))
            value = baseline.collect_baseline(repository)
            first = baseline.render_json(value)
            second = baseline.render_json(value)

        self.assertEqual(value.tests, 2)
        self.assertEqual(value.csv_files, 5)
        self.assertEqual(value.master_rows, 12)
        self.assertEqual(value.configuration_values, 3)
        self.assertEqual(value.configuration_import_specs, 2)
        self.assertEqual(value.configuration_value_ranges, 0)
        self.assertEqual(value.configuration_range_import_specs, 0)
        self.assertEqual(value.configuration_availability, 5)
        self.assertEqual(value.availability_standard, 2)
        self.assertEqual(value.availability_optional, 1)
        self.assertEqual(value.availability_not_available, 1)
        self.assertEqual(value.availability_unknown, 1)
        self.assertEqual(value.attributes, 2)
        self.assertEqual(value.attribute_categories, 1)
        self.assertEqual(value.validator_version, "9.9")
        self.assertFalse(value.sqlite_verified)
        self.assertEqual(first, second)
        self.assertNotIn("generated_at", first)
        self.assertEqual(json.loads(first)["master"]["rows"], 12)

    def test_verifies_matching_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = self.make_repository(root)
            database = root / "baseline.sqlite"
            self.build_database(repository, database)
            value = baseline.collect_baseline(repository, database)

        self.assertTrue(value.sqlite_verified)
        self.assertEqual(value.sqlite_tables, 5)
        self.assertEqual(value.sqlite_rows, 12)

    def test_rejects_sqlite_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = self.make_repository(root)
            database = root / "baseline.sqlite"
            connection = sqlite3.connect(database)
            connection.execute('CREATE TABLE "only_one" ("id" TEXT)')
            connection.commit()
            connection.close()

            with self.assertRaisesRegex(
                baseline.BaselineError,
                "SQLite baseline differs",
            ):
                baseline.collect_baseline(repository, database)

    def test_apply_then_check_managed_documents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.make_repository(Path(directory))
            self.add_documents(repository)
            value = baseline.collect_baseline(repository)
            changed = baseline.apply_documents(repository, value)
            drift = baseline.check_documents(repository, value)

        self.assertEqual(changed, sorted(baseline.MARKERS))
        self.assertEqual(drift, [])

    def test_detects_document_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.make_repository(Path(directory))
            self.add_documents(repository)
            value = baseline.collect_baseline(repository)
            baseline.apply_documents(repository, value)
            readme = repository / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8").replace(
                    "2 testów",
                    "99 testów",
                ),
                encoding="utf-8",
            )
            drift = baseline.check_documents(repository, value)

        self.assertEqual(drift, ["README.md"])

    def test_rejects_missing_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.make_repository(Path(directory))
            self.add_documents(repository)
            (repository / "README.md").write_text(
                "No markers\n",
                encoding="utf-8",
            )
            value = baseline.collect_baseline(repository)
            with self.assertRaisesRegex(
                baseline.BaselineError,
                "marker pair",
            ):
                baseline.check_documents(repository, value)

    def test_markdown_and_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.make_repository(Path(directory))
            value = baseline.collect_baseline(repository)
            report = baseline.render_markdown(value)
        arguments = baseline.parse_args(
            [
                "--check",
                "--database",
                "database.sqlite",
                "--json",
                "baseline.json",
                "--markdown",
                "baseline.md",
            ]
        )

        self.assertIn("| Tests | 2 |", report)
        self.assertIn("| Master rows | 12 |", report)
        self.assertTrue(arguments.check)
        self.assertEqual(arguments.database, Path("database.sqlite"))
        self.assertEqual(arguments.json_path, Path("baseline.json"))
        self.assertEqual(arguments.markdown, Path("baseline.md"))


if __name__ == "__main__":
    unittest.main()
