#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected one anchor in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="")


def main() -> int:
    model = ROOT / "tools/reporting/data_product_release_model.py"
    old = '''    files = sorted(
        path
        for path in source.rglob("*")
        if path.is_file() or path.is_symlink()
    )
'''
    new = '''    files = sorted(
        (
            path
            for path in source.rglob("*")
            if path.is_file() or path.is_symlink()
        ),
        key=lambda path: path.relative_to(source).as_posix(),
    )
'''
    replace_once(model, old, new)

    workflow = ROOT / ".github/workflows/data-product-release-download.yml"
    workflow.write_text(
        '''name: Verified Data Product Release Download

on:
  pull_request:
    paths:
      - .github/workflows/data-product-release-download.yml
      - tools/data_product_release_download.py
      - tools/reporting/data_product_release_download.py
      - tools/reporting/data_product_release_model.py
      - tools/dkb.py
      - tests/test_data_product_release_download.py
      - README.md
      - CHANGELOG.md
      - project/**
  workflow_dispatch:

permissions:
  contents: read

jobs:
  download-and-verify:
    strategy:
      fail-fast: false
      matrix:
        os:
          - ubuntu-latest
          - windows-latest
    runs-on: ${{ matrix.os }}
    steps:
      - name: Check out repository
        uses: actions/checkout@v7
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.13"
      - name: Run downloader regression tests
        run: python -m unittest -q tests.test_data_product_release_download
      - name: Download immutable public v1.0.0
        run: python tools/dkb.py data-product-release-download --version 1.0.0 --output-directory downloaded-release
      - name: Independently verify downloaded assets
        run: python tools/data_product_release.py --verify --version 1.0.0 --commit-sha 653ddacf9dcaeefa356f53e3c00e71666f5c5b3e --output-directory downloaded-release/assets
      - name: Check ready-to-open entry points
        run: python -c "from pathlib import Path; root=Path('downloaded-release/contents'); required=['shortlist/configuration-shortlist.html','comparison-bundle/configuration-comparison-workbook.xlsx','comparison-bundle/comparison-bundle-manifest.json','RELEASE_NOTES.md']; assert all((root / path).is_file() for path in required)"
''',
        encoding="utf-8",
        newline="",
    )

    package = ROOT / "project/packages/verified-data-product-release-download-cli.md"
    anchor = (
        "The focused GitHub Actions workflow also downloads the immutable public "
        "`v1.0.0` on Linux and Windows, independently re-runs "
        "`data-product-release --verify` against commit "
        "`653ddacf9dcaeefa356f53e3c00e71666f5c5b3e`, and checks all four local entry points.\n"
    )
    addition = (
        "\nThe shared deterministic ZIP writer orders files by normalized POSIX "
        "member name, so synthetic and future release manifests keep the same "
        "inventory order on Linux and Windows.\n"
    )
    replace_once(package, anchor, anchor + addition)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
