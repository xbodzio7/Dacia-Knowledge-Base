#!/usr/bin/env python3
"""Summarize unittest failures from a recovery log."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SEPARATOR = "=" * 70


def summarize(text: str) -> dict[str, object]:
    pattern = re.compile(
        rf"^{re.escape(SEPARATOR)}\n(?P<kind>FAIL|ERROR): (?P<name>.+?)\n"
        rf"-{{70}}\n(?P<body>.*?)(?=^{re.escape(SEPARATOR)}\n|^-{{70}}\nRan )",
        re.MULTILINE | re.DOTALL,
    )
    rows = []
    for match in pattern.finditer(text):
        body = match.group("body").strip()
        locations = []
        for raw, line in re.findall(r'File "([^"]+)", line (\d+)', body):
            marker = "/Dacia-Knowledge-Base/"
            locations.append(
                {
                    "path": raw.split(marker, 1)[-1] if marker in raw else raw,
                    "line": int(line),
                }
            )
        meaningful = [
            line.strip()
            for line in body.splitlines()
            if line.strip().startswith(
                (
                    "AssertionError:",
                    "ReleaseError:",
                    "CompletenessError:",
                    "ComparisonError:",
                    "BundleError:",
                    "ERROR:",
                )
            )
            or ": error:" in line
        ]
        rows.append(
            {
                "kind": match.group("kind"),
                "name": match.group("name"),
                "locations": locations,
                "message": meaningful[-1] if meaningful else body.splitlines()[-1],
            }
        )
    footer = re.search(r"FAILED \((.*?)\)", text)
    return {
        "count": len(rows),
        "failed_summary": footer.group(1) if footer else "",
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = summarize(args.log.read_text(encoding="utf-8", errors="replace"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
