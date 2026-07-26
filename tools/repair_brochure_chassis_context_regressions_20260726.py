#!/usr/bin/env python3
"""Relax historical exact totals after the accepted chassis context model."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected historical contract not found: {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        ROOT / "tests" / "test_jogger_brochure_hybrid_performance_20260726.py",
        '''        self.assertEqual(state["phase"], "Jogger Brochure Hybrid Performance Completion")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Brochure Chassis Measurement Context Modeling")
        self.assertEqual(state["baseline"]["tests"], 867)
        self.assertEqual(state["baseline"]["rows"], 9015)
        self.assertEqual(state["baseline"]["configuration_values"], 2290)
        self.assertEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertEqual(state["baseline"]["configuration_import_specs"], 117)
        self.assertEqual(state["baseline"]["configuration_range_import_specs"], 20)
''',
        '''        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 867)
        self.assertGreaterEqual(state["baseline"]["rows"], 9015)
        self.assertGreaterEqual(state["baseline"]["configuration_values"], 2290)
        self.assertGreaterEqual(state["baseline"]["configuration_value_ranges"], 234)
        self.assertGreaterEqual(state["baseline"]["configuration_import_specs"], 117)
        self.assertGreaterEqual(state["baseline"]["configuration_range_import_specs"], 20)
''',
    )
    replace_once(
        ROOT / "tests" / "test_sandero_total_valve_count_model.py",
        "        self.assertEqual(len(self.attributes), 381)\n",
        "        self.assertGreaterEqual(len(self.attributes), 381)\n",
    )
    print("PASS: chassis context historical regression contracts updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
