#!/usr/bin/env python3
"""Make completed generic-dimension milestones stable across later packages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepairError(RuntimeError):
    """Raised when a known historical contract has drifted unexpectedly."""


def replace_once_or_done(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    elif new not in text:
        raise RepairError(f"unexpected historical contract: {path}")


def main() -> int:
    replace_once_or_done(
        ROOT / "tools/review_brochure_generic_dimensions_import_closure_20260726.py",
        '''def verify_state() -> None:
    state = load_json(ROOT / "project" / "state.json")
    ensure(state.get("phase") == "Brochure Generic Dimensions Import Closure Review", "project phase differs")
    current = state.get("current_package")
    ensure(isinstance(current, dict), "current package is missing")
    ensure(current.get("name") == "Brochure Generic Dimensions Import Closure Review", "current package differs")
    ensure(current.get("status") == "complete", "current package status differs")
    next_package = state.get("next_package")
    ensure(isinstance(next_package, dict), "next state package is missing")
    ensure(next_package.get("name") == "Post-Brochure Priority Selection Review", "next state package differs")
    baseline = state.get("baseline")
    ensure(isinstance(baseline, dict), "state baseline is missing")
    ensure(baseline.get("tests") == 955, "state test baseline differs")
    ensure(baseline.get("rows") == 9688, "state row baseline differs")
    ensure(baseline.get("configuration_values") == 2949, "state value baseline differs")
    ensure(baseline.get("configuration_value_ranges") == 244, "state range baseline differs")
    ensure(baseline.get("attributes") == 385, "state attribute baseline differs")''',
        '''def verify_state() -> None:
    state = load_json(ROOT / "project" / "state.json")
    current = state.get("current_package")
    ensure(isinstance(current, dict), "current package is missing")
    ensure(current.get("status") == "complete", "current package status differs")
    baseline = state.get("baseline")
    ensure(isinstance(baseline, dict), "state baseline is missing")
    ensure(int(baseline.get("tests", 0)) >= 955, "state test baseline predates closure")
    ensure(baseline.get("rows") == 9688, "state row baseline differs")
    ensure(baseline.get("configuration_values") == 2949, "state value baseline differs")
    ensure(baseline.get("configuration_value_ranges") == 244, "state range baseline differs")
    ensure(baseline.get("attributes") == 385, "state attribute baseline differs")''',
    )

    common_old = '''        self.assertEqual(state["phase"], "Brochure Generic Dimensions Import Closure Review")
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(state["next_package"]["name"], "Post-Brochure Priority Selection Review")
        self.assertEqual(state["baseline"]["tests"], 955)'''
    common_new = '''        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 955)'''
    replace_once_or_done(
        ROOT / "tests/test_brochure_generic_dimensions_import_20260726.py",
        common_old,
        common_new,
    )
    replace_once_or_done(
        ROOT / "tests/test_brochure_generic_dimensions_semantic_mapping_review.py",
        common_old,
        common_new,
    )

    replace_once_or_done(
        ROOT / "tests/test_brochure_generic_dimensions_import_closure_review.py",
        '''    def test_project_state_advances_to_priority_selection(self) -> None:
        state = json.loads(
            (ROOT / "project" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            state["phase"],
            "Brochure Generic Dimensions Import Closure Review",
        )
        self.assertEqual(
            state["current_package"]["name"],
            "Brochure Generic Dimensions Import Closure Review",
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["name"],
            "Post-Brochure Priority Selection Review",
        )
        self.assertEqual(state["baseline"]["tests"], 955)''',
        '''    def test_project_state_preserves_closure_baseline(self) -> None:
        state = json.loads(
            (ROOT / "project" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertGreaterEqual(state["baseline"]["tests"], 955)''',
    )
    print("PASS: generic dimension historical state contracts stabilized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
