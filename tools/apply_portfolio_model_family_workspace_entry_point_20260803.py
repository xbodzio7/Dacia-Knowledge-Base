#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"patch anchor missing in {relative}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        "tools/reporting/data_product_release_download.py",
        '''OPTIONAL_ENTRY_POINTS = {\n    "cross_model_html": "cross-model/cross-model-comparison-view.html",\n}\n''',
        '''OPTIONAL_ENTRY_POINTS = {\n    "cross_model_html": "cross-model/cross-model-comparison-view.html",\n    "model_family_summary_html": (\n        "model-families/portfolio_model_family_summary.html"\n    ),\n}\n''',
    )
    replace_once(
        "tools/reporting/data_product_workspace_index.py",
        '''CROSS_MODEL_HTML_MEMBER = "cross-model/cross-model-comparison-view.html"\nSCOPE_PATTERN = re.compile''',
        '''CROSS_MODEL_HTML_MEMBER = "cross-model/cross-model-comparison-view.html"\nMODEL_FAMILY_HTML_MEMBER = (\n    "model-families/portfolio_model_family_summary.html"\n)\nSCOPE_PATTERN = re.compile''',
    )
    replace_once(
        "tools/reporting/data_product_workspace_index.py",
        '''    if CROSS_MODEL_HTML_MEMBER in release_members:\n        links.append(\n  {\n      "title": "Models and comparison scopes",\n      "description": "Browse model families and open only existing scope reports.",\n      "path": _verified_content_path(\n          workspace_root,\n          release_members,\n          CROSS_MODEL_HTML_MEMBER,\n          label="cross-model comparison HTML",\n      ),\n  }\n        )\n    return tuple(links)\n''',
        '''    if CROSS_MODEL_HTML_MEMBER in release_members:\n        links.append(\n  {\n      "title": "Models and comparison scopes",\n      "description": "Browse model families and open only existing scope reports.",\n      "path": _verified_content_path(\n          workspace_root,\n          release_members,\n          CROSS_MODEL_HTML_MEMBER,\n          label="cross-model comparison HTML",\n      ),\n  }\n        )\n    if MODEL_FAMILY_HTML_MEMBER in release_members:\n        links.append(\n  {\n      "title": "Model family summary",\n      "description": (\n          "Review each model family with exact scopes, configurations and "\n          "source provenance."\n      ),\n      "path": _verified_content_path(\n          workspace_root,\n          release_members,\n          MODEL_FAMILY_HTML_MEMBER,\n          label="portfolio model-family summary HTML",\n      ),\n  }\n        )\n    return tuple(links)\n''',
    )
    replace_once(
        "tools/data_product_release_download.py",
        '''        "cross_model_html": "Cross-model navigation",\n        "release_notes": "Release notes",\n''',
        '''        "cross_model_html": "Cross-model navigation",\n        "model_family_summary_html": "Model family summary",\n        "release_notes": "Release notes",\n''',
    )
    replace_once(
        "tools/data_product_release_download.py",
        '''    if "cross_model_html" in raw_entry_points:\n        keys.append("cross_model_html")\n    keys.append("release_notes")\n''',
        '''    if "cross_model_html" in raw_entry_points:\n        keys.append("cross_model_html")\n    if "model_family_summary_html" in raw_entry_points:\n        keys.append("model_family_summary_html")\n    keys.append("release_notes")\n''',
    )
    print("Portfolio model-family workspace entry point patch: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
