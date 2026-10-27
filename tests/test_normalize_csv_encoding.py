from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from tools import normalize_csv_encoding as normalize


class NormalizeCsvEncodingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = (
            tempfile.TemporaryDirectory()
        )
        self.root = Path(
            self.temporary_directory.name
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_data_file(
        self,
        relative_path: str,
        text: str,
        encoding: str,
    ) -> Path:
        path = self.root / "data" / relative_path
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            text,
            encoding=encoding,
            newline="",
        )
        return path

    def test_discovers_only_csv_files_under_data(
        self,
    ) -> None:
        first = self.write_data_file(
            "master/enums/a.csv",
            "id,name\n1,A\n",
            "utf-8",
        )
        second = self.write_data_file(
            "master/z.csv",
            "id,name\n1,Z\n",
            "utf-8",
        )

        report = self.root / "reports" / "export.csv"
        report.parent.mkdir(parents=True)
        report.write_text(
            "id\n1\n",
            encoding="utf-8",
        )

        files = normalize.discover_csv_files(
            self.root
        )

        self.assertEqual(files, [first, second])

    def test_rejects_missing_data_directory(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            normalize.EncodingNormalizationError,
            "data directory does not exist",
        ):
            normalize.discover_csv_files(
                self.root
            )

    def test_detects_utf8_and_windows_1250(
        self,
    ) -> None:
        utf8_path = self.write_data_file(
            "master/utf8.csv",
            "id,name\n1,Żółć\n",
            "utf-8",
        )
        cp1250_path = self.write_data_file(
            "master/cp1250.csv",
            "id,name\n1,Łódź\n",
            "cp1250",
        )

        self.assertEqual(
            normalize.detect_encoding(utf8_path),
            normalize.TARGET_ENCODING,
        )
        self.assertEqual(
            normalize.detect_encoding(cp1250_path),
            normalize.SOURCE_ENCODING,
        )

    def test_dry_run_preserves_source_file(
        self,
    ) -> None:
        path = self.write_data_file(
            "master/models.csv",
            "id,name\n1,Łódź\n",
            "cp1250",
        )
        original = path.read_bytes()
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = normalize.normalize_csv_files(
                self.root,
                apply=False,
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            path.read_bytes(),
            original,
        )
        self.assertIn(
            "Windows-1250      : 1",
            stdout.getvalue(),
        )
        self.assertIn(
            "Dry run only",
            stdout.getvalue(),
        )

    def test_apply_converts_file_to_utf8(
        self,
    ) -> None:
        expected = "id,name\n1,Łódź\n"
        path = self.write_data_file(
            "master/models.csv",
            expected,
            "cp1250",
        )
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = normalize.normalize_csv_files(
                self.root,
                apply=True,
            )

        self.assertEqual(result, 0)
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            expected,
        )
        self.assertFalse(
            path.with_name(
                f"{path.name}.encoding.tmp"
            ).exists()
        )
        self.assertIn(
            "Converted 1 file(s) to UTF-8.",
            stdout.getvalue(),
        )

    def test_apply_does_not_rewrite_utf8_file(
        self,
    ) -> None:
        self.write_data_file(
            "master/models.csv",
            "id,name\n1,Żółć\n",
            "utf-8",
        )

        with mock.patch.object(
            normalize,
            "convert_to_utf8",
        ) as convert:
            result = normalize.normalize_csv_files(
                self.root,
                apply=True,
            )

        self.assertEqual(result, 0)
        convert.assert_not_called()

    def test_reports_unreadable_file(
        self,
    ) -> None:
        path = (
            self.root
            / "data"
            / "master"
            / "broken.csv"
        )
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_bytes(b"\x81")

        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = normalize.normalize_csv_files(
                self.root,
                apply=False,
            )

        self.assertEqual(result, 1)
        self.assertIn(
            "Unreadable        : 1",
            stdout.getvalue(),
        )
        self.assertIn(
            "Files requiring manual review",
            stderr.getvalue(),
        )

    def test_accepts_data_directory_without_csv(
        self,
    ) -> None:
        (self.root / "data").mkdir()
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = normalize.normalize_csv_files(
                self.root,
                apply=False,
            )

        self.assertEqual(result, 0)
        self.assertIn(
            "No CSV files found.",
            stdout.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
