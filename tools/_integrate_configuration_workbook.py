from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "reporting" / "configuration_comparison_bundle.py"
text = PATH.read_text(encoding="utf-8")

import_marker = "import configuration_comparison as comparison\n"
imports = (
    import_marker
    + "from reporting.configuration_comparison_workbook import write_bundle_workbook\n"
    + "from reporting.deterministic_xlsx_model import WorkbookError\n"
)
if "write_bundle_workbook" not in text:
    if import_marker not in text:
        raise RuntimeError("bundle import marker not found")
    text = text.replace(import_marker, imports, 1)

write_marker = '''        _write_text(
            build_root / "comparison-bundle-manifest.json",
            _json_text(manifest),
        )
'''
replacement = '''        try:
            workbook_path = write_bundle_workbook(
                repository,
                build_root,
                manifest,
            )
        except WorkbookError as exc:
            raise BundleError(f"workbook generation failed: {exc}") from exc
        manifest["workbook"] = _file_record(workbook_path, build_root)
        _write_text(
            build_root / "comparison-bundle-manifest.json",
            _json_text(manifest),
        )
'''
if 'manifest["workbook"]' not in text:
    if write_marker not in text:
        raise RuntimeError("bundle manifest marker not found")
    text = text.replace(write_marker, replacement, 1)

PATH.write_text(text, encoding="utf-8")
