from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.validators.csv_validator import validate_csv


class CsvValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_text(
        self,
        content: str,
        *,
        encoding: str = "utf-8",
    ) -> Path:
        path = self.root / "data.csv"
        path.write_text(
            content,
            encoding=encoding,
            newline="",
        )
        return path

    def write_bytes(self, content: bytes) -> Path:
        path = self.root / "data.csv"
        path.write_bytes(content)
        return path

    def test_accepts_valid_utf8_csv(self) -> None:
        path = self.write_text(
            "id,name\n"
            "1,Duster\n"
            "2,Sandero\n"
        )

        valid, errors = validate_csv(path)

        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_accepts_utf8_bom(self) -> None:
        path = self.write_bytes(
            (
                "id,name\n"
                "1,Łódź\n"
            ).encode("utf-8-sig")
        )

        valid, errors = validate_csv(path)

        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_rejects_windows_1250(self) -> None:
        path = self.write_bytes(
            (
                "id,name\n"
                "1,Łódź\n"
            ).encode("cp1250")
        )

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(
            errors,
            ["File is not valid UTF-8"],
        )

    def test_rejects_empty_file(self) -> None:
        path = self.write_text("")

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(
            errors,
            ["File is empty or has no header"],
        )

    def test_rejects_empty_header_name(self) -> None:
        path = self.write_text(
            "id,,name\n"
            "1,value,Duster\n"
        )

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertIn(
            "Header: empty column name at position 2",
            errors,
        )

    def test_rejects_case_insensitive_duplicate_header(self) -> None:
        path = self.write_text(
            "id,Name,name\n"
            "1,Duster,Duster\n"
        )

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "duplicate column name 'name'",
            errors[0],
        )

    def test_rejects_short_row(self) -> None:
        path = self.write_text(
            "id,name,status\n"
            "1,Duster\n"
        )

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(
            errors,
            ["Line 2: expected 3 columns, got 2"],
        )

    def test_rejects_long_row(self) -> None:
        path = self.write_text(
            "id,name\n"
            "1,Duster,current\n"
        )

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(
            errors,
            ["Line 2: expected 2 columns, got 3"],
        )

    def test_rejects_empty_data_row(self) -> None:
        path = self.write_text(
            "id,name\n"
            "1,Duster\n"
            ",\n"
        )

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(
            errors,
            ["Line 3: empty data row"],
        )

    def test_rejects_malformed_csv_quoting(self) -> None:
        path = self.write_text(
            "id,name\n"
            '1,"unterminated\n'
        )

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(len(errors), 1)
        self.assertTrue(
            errors[0].startswith("CSV parse error:")
        )

    def test_reports_missing_file(self) -> None:
        path = self.root / "missing.csv"

        valid, errors = validate_csv(path)

        self.assertFalse(valid)
        self.assertEqual(
            errors,
            [f"File not found: {path}"],
        )


if __name__ == "__main__":
    unittest.main()
