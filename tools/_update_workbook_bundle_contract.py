from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tests" / "test_configuration_comparison_bundle.py"
text = PATH.read_text(encoding="utf-8")
text = text.replace(
    "self.assertEqual(len(files), 9)",
    "self.assertEqual(len(files), 10)",
)
text = text.replace(
    "def test_singleton_bundle_writes_only_manifest(self) -> None:",
    "def test_singleton_bundle_writes_workbook_and_manifest(self) -> None:",
)
text = text.replace(
    'self.assertEqual(names, ["comparison-bundle-manifest.json"])',
    'self.assertEqual(\n'
    '            names,\n'
    '            [\n'
    '                "comparison-bundle-manifest.json",\n'
    '                "configuration-comparison-workbook.xlsx",\n'
    '            ],\n'
    '        )',
)
if "self.assertEqual(len(files), 9)" in text:
    raise RuntimeError("old bundle file-count assertion remains")
if "writes_only_manifest" in text:
    raise RuntimeError("old singleton test name remains")
PATH.write_text(text, encoding="utf-8")
