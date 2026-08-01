from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATHS = (
    Path("data/reporting/jogger_ecog120_manual_completeness.json"),
    Path("data/reporting/jogger_ecog120_automatic_completeness.json"),
    Path("data/reporting/jogger_hybrid155_automatic_completeness.json"),
    Path("data/reporting/jogger_tce110_manual_completeness.json"),
)
ATTRIBUTE = "elasticity_80_120"
GEAR_NUMBER = "4"


def render(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    matches = 0
    for slot in payload["technical_slots"]:
        if slot.get("attribute_code") == ATTRIBUTE:
            slot["gear_number"] = GEAR_NUMBER
            matches += 1
    if matches == 0:
        raise ValueError(f"No {ATTRIBUTE} slot in {path}")
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed: list[str] = []
    for relative in SCOPE_PATHS:
        path = ROOT / relative
        expected = render(path)
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

    if changed:
        print(f"Aligned {len(changed)} Jogger completeness scopes.")
    else:
        print("Jogger elasticity completeness context already aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
