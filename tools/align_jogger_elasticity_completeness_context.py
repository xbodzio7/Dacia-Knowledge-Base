from __future__ import annotations

import argparse
import json
from pathlib import Path

import existing_configuration_missing_data_analysis as completeness_analysis

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATHS = (
    Path("data/reporting/jogger_ecog120_manual_completeness.json"),
    Path("data/reporting/jogger_ecog120_automatic_completeness.json"),
    Path("data/reporting/jogger_hybrid155_automatic_completeness.json"),
    Path("data/reporting/jogger_tce110_manual_completeness.json"),
)
ANALYSIS_JSON = ROOT / "data/reporting/existing_configuration_missing_data_analysis.json"
ANALYSIS_MD = ROOT / "data/reporting/existing_configuration_missing_data_analysis.md"
ATTRIBUTE = "elasticity_80_120"
GEAR_NUMBER = "4"


def render_scope(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    matches = 0
    for slot in payload["technical_slots"]:
        if slot.get("attribute_code") == ATTRIBUTE:
            slot["gear_number"] = GEAR_NUMBER
            matches += 1
    if matches == 0:
        raise ValueError(f"No {ATTRIBUTE} slot in {path}")
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def expected_analysis() -> tuple[str, str]:
    payload = completeness_analysis.collect(ROOT)
    return (
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        completeness_analysis.render_markdown(payload),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed: list[str] = []
    for relative in SCOPE_PATHS:
        path = ROOT / relative
        expected = render_scope(path)
        current = path.read_text(encoding="utf-8")
        if current != expected:
            changed.append(relative.as_posix())
            if not args.check:
                path.write_text(expected, encoding="utf-8")

    if args.check and changed:
        print("Outdated Jogger completeness scopes:")
        for item in changed:
            print(f"- {item}")
        return 1

    expected_json, expected_md = expected_analysis()
    stale_reports: list[str] = []
    if not ANALYSIS_JSON.is_file() or ANALYSIS_JSON.read_text(encoding="utf-8") != expected_json:
        stale_reports.append(ANALYSIS_JSON.relative_to(ROOT).as_posix())
        if not args.check:
            ANALYSIS_JSON.write_text(expected_json, encoding="utf-8")
    if not ANALYSIS_MD.is_file() or ANALYSIS_MD.read_text(encoding="utf-8") != expected_md:
        stale_reports.append(ANALYSIS_MD.relative_to(ROOT).as_posix())
        if not args.check:
            ANALYSIS_MD.write_text(expected_md, encoding="utf-8")

    if args.check and stale_reports:
        print("Outdated dependent completeness reports:")
        for item in stale_reports:
            print(f"- {item}")
        return 1

    if changed:
        print(f"Aligned {len(changed)} Jogger completeness scopes.")
    else:
        print("Jogger elasticity completeness context already aligned.")
    if stale_reports:
        print(f"Refreshed {len(stale_reports)} dependent completeness reports.")
    else:
        print("Dependent completeness reports already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
