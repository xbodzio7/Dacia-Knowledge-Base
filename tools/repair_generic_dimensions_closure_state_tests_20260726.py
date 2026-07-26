#!/usr/bin/env python3
"""Advance historical generic-dimension state tests to the closure milestone."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    ROOT / "tests/test_brochure_generic_dimensions_import_20260726.py": (
        '''        self.assertEqual(state["phase"], "Brochure Generic Dimensions Observation Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Brochure Generic Dimensions Import Closure Review")
        self.assertEqual(state["baseline"]["tests"], 947)''',
        '''        self.assertEqual(state["phase"], "Brochure Generic Dimensions Import Closure Review")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Post-Brochure Priority Selection Review")
        self.assertEqual(state["baseline"]["tests"], 955)''',
    ),
    ROOT / "tests/test_brochure_generic_dimensions_semantic_mapping_review.py": (
        '''        self.assertEqual(state["phase"], "Brochure Generic Dimensions Observation Import")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Brochure Generic Dimensions Import Closure Review")
        self.assertEqual(state["baseline"]["tests"], 947)''',
        '''        self.assertEqual(state["phase"], "Brochure Generic Dimensions Import Closure Review")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Post-Brochure Priority Selection Review")
        self.assertEqual(state["baseline"]["tests"], 955)''',
    ),
}


def main() -> int:
    for path, (old, new) in REPLACEMENTS.items():
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
        elif new not in text:
            raise RuntimeError(f"unexpected historical state contract: {path}")
    print("PASS: generic dimension historical state tests advanced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
