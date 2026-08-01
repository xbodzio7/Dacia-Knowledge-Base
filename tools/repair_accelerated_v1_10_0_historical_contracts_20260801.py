#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES_WITH_NEXT_ASSERTION = (
    "tools/import_sandero_stepway_essential_source_gap_20260626.py",
    "tools/import_sandero_stepway_expression_auto_source_gap_20260626.py",
    "tools/import_sandero_stepway_expression_source_gap_20260626.py",
    "tools/import_sandero_stepway_extreme_source_gap_20260626.py",
)
EXTREME_AUTO = "tools/import_sandero_stepway_extreme_auto_source_gap_20260626.py"


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"replacement marker not found in {path}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    variants = (
        '''    if state["next_package"]["goal"].find(str(selected["source_code"])) < 0:\n        raise ContractError("project state does not reference the selected next source")\n''',
        '''    if str(selected["source_code"]) not in state["next_package"]["goal"]:\n        raise ContractError("project state does not reference the selected next source")\n''',
    )
    for path in FILES_WITH_NEXT_ASSERTION:
        target = ROOT / path
        text = target.read_text(encoding="utf-8")
        for old in variants:
            if old in text:
                target.write_text(text.replace(old, "", 1), encoding="utf-8")
                break
        else:
            if "project state does not reference the selected next source" in text:
                raise RuntimeError(f"unhandled next-package assertion in {path}")

    replace_once(
        EXTREME_AUTO,
        '''    state = json.loads(STATE.read_text(encoding="utf-8"))\n    if (\n        state["current_package"]["package_id"]\n        != "sandero_stepway_extreme_auto_source_gap_005"\n    ):\n        raise ContractError("project state does not identify the completed package")\n    if str(selected["source_code"]) not in state["next_package"]["goal"]:\n        raise ContractError("project state does not reference the selected next source")\n''',
        '''    state = json.loads(STATE.read_text(encoding="utf-8"))\n    if int(state["baseline"]["configuration_values"]) < EXPECTED_VALUE_LAST_ID:\n        raise ContractError("project state baseline predates the completed package")\n''',
    )

    package_path = ROOT / "project/packages/data-products-v1.10.0-accelerated-release-preparation-20260801.md"
    package_text = package_path.read_text(encoding="utf-8")
    marker = "## Historical contract repair"
    if marker not in package_text:
        package_text = package_text.rstrip() + '''\n\n## Historical contract repair\n\nFive completed Sandero Stepway source-gap verifiers now validate their durable data, generated analysis and minimum canonical baseline without requiring `project/state.json` to remain frozen on their former current or next package. This keeps completed package contracts valid while the canonical state advances to release preparation and later milestones.\n'''
        package_path.write_text(package_text, encoding="utf-8")

    state_path = ROOT / "project/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    manifest = state["current_package"]["manifest_paths"]
    for path in (*FILES_WITH_NEXT_ASSERTION, EXTREME_AUTO):
        if path not in manifest:
            manifest.append(path)
    manifest.sort()
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
