from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import quality_artifact_manifest as manifest  # noqa: E402


class QualityArtifactManifestContractTests(unittest.TestCase):
    def test_generation_is_deterministic_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text_file = root / "quality.log"
            json_file = root / "quality-summary.json"
            text_file.write_text("quality\n", encoding="utf-8")
            json_file.write_text("{}\n", encoding="utf-8")
            output = root / "artifact-manifest.json"

            payload = manifest.build_manifest(
                [text_file, json_file],
                output,
            )
            rendered = json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ) + "\n"

            self.assertEqual(payload["version"], 1)
            self.assertEqual(payload["hash_algorithm"], "sha256")
            self.assertEqual(payload["file_count"], 2)
            self.assertEqual(
                [entry["name"] for entry in payload["files"]],
                ["quality-summary.json", "quality.log"],
            )
            self.assertEqual(
                rendered,
                json.dumps(
                    manifest.build_manifest(
                        [json_file, text_file],
                        output,
                    ),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
            )

    def test_written_manifest_verifies_extracted_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "nested"
            nested.mkdir()
            first = root / "report.csv"
            second = nested / "report.md"
            first.write_bytes(b"a,b\n1,2\n")
            second.write_text("# Report\n", encoding="utf-8")
            output = root / "artifact-manifest.json"

            payload = manifest.build_manifest([first, second], output)
            manifest.write_manifest(output, payload)

            self.assertEqual(
                manifest.verify_manifest(output, root),
                payload,
            )

    def test_verification_detects_content_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "report.json"
            output = root / "artifact-manifest.json"
            data.write_text("{}\n", encoding="utf-8")
            manifest.write_manifest(
                output,
                manifest.build_manifest([data], output),
            )
            data.write_text('{"changed": true}\n', encoding="utf-8")

            with self.assertRaisesRegex(
                manifest.ManifestError,
                "size mismatch|sha256 mismatch",
            ):
                manifest.verify_manifest(output, root)

    def test_duplicate_basenames_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_dir = root / "one"
            second_dir = root / "two"
            first_dir.mkdir()
            second_dir.mkdir()
            first = first_dir / "report.json"
            second = second_dir / "report.json"
            first.write_text("{}\n", encoding="utf-8")
            second.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(
                manifest.ManifestError,
                "duplicate artifact file name",
            ):
                manifest.build_manifest(
                    [first, second],
                    root / "artifact-manifest.json",
                )

    def test_missing_and_unexpected_files_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "report.json"
            output = root / "artifact-manifest.json"
            data.write_text("{}\n", encoding="utf-8")
            manifest.write_manifest(
                output,
                manifest.build_manifest([data], output),
            )
            data.unlink()

            with self.assertRaisesRegex(
                manifest.ManifestError,
                "missing artifact files",
            ):
                manifest.verify_manifest(output, root)

            data.write_text("{}\n", encoding="utf-8")
            (root / "unexpected.txt").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(
                manifest.ManifestError,
                "unexpected artifact files",
            ):
                manifest.verify_manifest(output, root)

    def test_cli_generation_and_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "report.md"
            output = root / "artifact-manifest.json"
            data.write_text("# Report\n", encoding="utf-8")

            self.assertEqual(
                manifest.main(
                    [
                        "--output",
                        str(output),
                        "--file",
                        str(data),
                    ]
                ),
                0,
            )
            self.assertEqual(
                manifest.main(
                    [
                        "--verify",
                        str(output),
                        "--root",
                        str(root),
                    ]
                ),
                0,
            )


if __name__ == "__main__":
    unittest.main()
