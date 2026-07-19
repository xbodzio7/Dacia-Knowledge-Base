from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "dkb.py"
text = PATH.read_text(encoding="utf-8")

command_marker = '''    "configuration-comparison-bundle": (
'''
command_entry = '''    "data-product-release": (
        "data_product_release.py",
        "Build or verify deterministic versioned data-product release assets.",
        "--output-directory DIR [--version MAJOR.MINOR.PATCH] "
        "[--commit-sha SHA] [--verify]",
    ),
'''
if '"data-product-release": (' not in text:
    if command_marker not in text:
        raise RuntimeError("DKB command marker not found")
    text = text.replace(command_marker, command_entry + command_marker, 1)

example_marker = '''    print(
        "  python tools/dkb.py configuration-comparison-bundle "
'''
example = '''    print(
        "  python tools/dkb.py data-product-release --version 1.0.0 "
        "--commit-sha 0123456789012345678901234567890123456789 "
        "--output-directory ../data-product-release"
    )
'''
if "dkb.py data-product-release --version" not in text:
    if example_marker not in text:
        raise RuntimeError("DKB example marker not found")
    text = text.replace(example_marker, example + example_marker, 1)

PATH.write_text(text, encoding="utf-8")
