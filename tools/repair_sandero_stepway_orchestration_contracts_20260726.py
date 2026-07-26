#!/usr/bin/env python3
"""Update orchestration snapshots after four Sandero/Stepway chassis slots."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected snapshot not found: {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    context = ROOT / "tests" / "configuration_comparison_context_filter_contract.py"
    replace_once(
        context,
        "        self.assertEqual(len(core.difference_csv_rows(report)), 349)\n",
        "        self.assertEqual(len(core.difference_csv_rows(report)), 365)\n",
    )
    replace_once(
        context,
        '            "fuel_type_code=": 144,\n',
        '            "fuel_type_code=": 160,\n',
    )

    pairs = ROOT / "tests" / "configuration_comparison_pair_summary_contract.py"
    replace_once(
        pairs,
        '            {"122", "124", "126"},\n',
        '            {"126", "128", "130"},\n',
    )
    replace_once(
        pairs,
        "            349,\n",
        "            365,\n",
    )
    print("PASS: Sandero and Stepway orchestration snapshots updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
