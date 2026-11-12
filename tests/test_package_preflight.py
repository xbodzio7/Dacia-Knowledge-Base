from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.package_preflight import validate_data_tree


class PackagePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "data").mkdir()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_accepts_valid_csv_and_json_tree(self) -> None:
        (self.root / "data" / "master.csv").write_text(
            'id,note\n1,"Price includes 85,900 PLN"\n',
            encoding="utf-8",
            newline="",
        )
        (self.root / "data" / "receipt.json").write_text(
            '{"source_id": "spring", "count": 1}\n',
            encoding="utf-8",
        )

        self.assertEqual(validate_data_tree(self.root), [])

    def test_rejects_unquoted_csv_comma_that_changes_row_width(self) -> None:
        (self.root / "data" / "master.csv").write_text(
            "id,note\n1,Price includes 85,900 PLN\n",
            encoding="utf-8",
            newline="",
        )

        errors = validate_data_tree(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("expected 2 columns, got 4", errors[0])

    def test_rejects_malformed_json(self) -> None:
        (self.root / "data" / "receipt.json").write_text(
            '{"source_id": "spring",}\n',
            encoding="utf-8",
        )

        errors = validate_data_tree(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("invalid JSON", errors[0])

    def test_rejects_missing_data_directory(self) -> None:
        (self.root / "data").rmdir()

        self.assertTrue(
            validate_data_tree(self.root)[0].startswith("Data directory not found:")
        )


if __name__ == "__main__":
    unittest.main()
