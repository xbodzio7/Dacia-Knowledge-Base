#!/usr/bin/env python3
"""Import source-backed Jogger equipment availability."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.jogger_equipment_availability import (  # noqa: E402,F401
    ContractError, SOURCE, SOURCE_SHA256, apply, check, configuration_group,
    file_sha256, generated_rows, jogger_configurations, load_matrices,
    semantic_payload,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    try:
        if arguments.apply:
            apply()
        check()
        return 0
    except ContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
