#!/usr/bin/env python3
"""Add the canonical boot-capacity slot to imported Bigster reporting scopes."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPECS = (
    ROOT / "data" / "reporting" / "bigster_mildhybridg140_4x2_manual_completeness.json",
    ROOT / "data" / "reporting" / "bigster_mildhybrid140_4x2_manual_completeness.json",
    ROOT / "data" / "reporting" / "bigster_hybrid155_4x2_automatic_completeness.json",
)
SLOT = {"attribute_code": "boot_capacity", "fuel_type_code": ""}


for path in SPECS:
    payload = json.loads(path.read_text(encoding="utf-8"))
    slots = payload.get("technical_slots")
    if not isinstance(slots, list):
        raise RuntimeError(f"technical_slots missing: {path}")
    if SLOT not in slots:
        slots.append(SLOT.copy())
        slots.sort(
            key=lambda item: (
                str(item.get("attribute_code", "")),
                str(item.get("fuel_type_code", "")),
            )
        )
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

print("PASS: Bigster cargo reporting scopes updated")
