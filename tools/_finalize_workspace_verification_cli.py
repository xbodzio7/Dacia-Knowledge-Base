#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected exactly one anchor in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="")


def main() -> None:
    path = ROOT / "tools/dkb.py"
    command_anchor = '''    "data-product-release-download": (
        "data_product_release_download.py",
        "Download, verify and safely extract one immutable public data-product release.",
        "--version MAJOR.MINOR.PATCH --output-directory DIR",
    ),
'''
    command_addition = command_anchor + '''    "data-product-workspace-verify": (
        "data_product_workspace_verify.py",
        "Verify an extracted data-product workspace fully offline.",
        "--workspace-directory DIR [--json]",
    ),
'''
    replace_once(path, command_anchor, command_addition)

    example_anchor = '''    print(
        "  python tools/dkb.py data-product-release-download --version 1.0.0 "
        "--output-directory ../dkb-data-products-v1.0.0"
    )
'''
    example_addition = example_anchor + '''    print(
        "  python tools/dkb.py data-product-workspace-verify "
        "--workspace-directory ../dkb-data-products-v1.0.0 --json"
    )
'''
    replace_once(path, example_anchor, example_addition)


if __name__ == "__main__":
    main()
