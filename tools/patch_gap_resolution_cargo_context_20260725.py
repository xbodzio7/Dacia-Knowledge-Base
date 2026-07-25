#!/usr/bin/env python3
"""Apply the reviewed cargo-context semantic-key repair to gap planning."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "configuration_gap_resolution_plan.py"
TEST = ROOT / "tests" / "test_sandero_stepway_brochure_cargo_20260725.py"


class PatchError(RuntimeError):
    pass


def function_slice(text: str, name: str, next_name: str) -> tuple[int, int, str]:
    start_marker = f"def {name}("
    end_marker = f"def {next_name}("
    start = text.find(start_marker)
    if start < 0:
        raise PatchError(f"function not found: {name}")
    end = text.find(end_marker, start)
    if end < 0:
        raise PatchError(f"following function not found: {next_name}")
    return start, end, text[start:end]


def replace_in_slice(
    text: str,
    name: str,
    next_name: str,
    old: str,
    new: str,
    marker: str,
) -> str:
    start, end, block = function_slice(text, name, next_name)
    if marker in block:
        return text
    if old not in block:
        raise PatchError(f"anchor missing in {name}: {old!r}")
    block = block.replace(old, new, 1)
    return text[:start] + block + text[end:]


def patch_tool() -> None:
    text = TOOL.read_text(encoding="utf-8")
    import_line = (
        "from reporting.cargo_context import context_index, semantic_signature\n"
    )
    if import_line not in text:
        anchor = "from typing import Any, Mapping, Sequence\n"
        if anchor not in text:
            raise PatchError("typing import anchor missing")
        text = text.replace(anchor, anchor + "\n" + import_line, 1)

    text = replace_in_slice(
        text,
        "existing_import_semantics",
        "load_repository_context",
        ") -> set[tuple[str, str, str, str]]:\n"
        "    result: set[tuple[str, str, str, str]] = set()\n",
        ") -> set[tuple[str, str, str, str, str]]:\n"
        "    result: set[tuple[str, str, str, str, str]] = set()\n",
        "tuple[str, str, str, str, str]",
    )
    text = replace_in_slice(
        text,
        "existing_import_semantics",
        "load_repository_context",
        "                observation_date,\n"
        "            )\n",
        "                observation_date,\n"
        "                \"\",\n"
        "            )\n",
        'observation_date,\n                "",',
    )

    context_loader = (
        "    context_path = master / \"configuration_cargo_volume_contexts.csv\"\n"
        "    cargo_contexts = (\n"
        "        context_index(\n"
        "            read_csv(context_path, \"configuration cargo contexts\")\n"
        "        )\n"
        "        if context_path.is_file()\n"
        "        else {}\n"
        "    )\n"
    )
    text = replace_in_slice(
        text,
        "load_repository_context",
        "validate_evidence",
        "    values = read_csv(\n",
        context_loader + "    values = read_csv(\n",
        "configuration cargo contexts",
    )
    text = replace_in_slice(
        text,
        "load_repository_context",
        "validate_evidence",
        "        tuple[str, str, str, str],\n",
        "        tuple[str, str, str, str, str],\n",
        "tuple[str, str, str, str, str],",
    )
    text = replace_in_slice(
        text,
        "load_repository_context",
        "validate_evidence",
        "        key = (\n"
        "            row.get(\"configuration_code\", \"\"),\n",
        "        cargo_context = cargo_contexts.get(row.get(\"code\", \"\"))\n"
        "        key = (\n"
        "            row.get(\"configuration_code\", \"\"),\n",
        "cargo_context = cargo_contexts.get",
    )
    text = replace_in_slice(
        text,
        "load_repository_context",
        "validate_evidence",
        "            row.get(\"observation_date\", \"\"),\n"
        "        )\n",
        "            row.get(\"observation_date\", \"\"),\n"
        "            semantic_signature(cargo_context) if cargo_context else \"\",\n"
        "        )\n",
        "semantic_signature(cargo_context) if cargo_context else",
    )
    text = replace_in_slice(
        text,
        "build_found_candidate",
        "build_expected_plan_spec",
        "        observation_date,\n"
        "    )\n"
        "    existing = context[\"values\"].get(semantic)\n",
        "        observation_date,\n"
        "        \"\",\n"
        "    )\n"
        "    existing = context[\"values\"].get(semantic)\n",
        'observation_date,\n        "",\n    )\n    existing',
    )
    TOOL.write_text(text, encoding="utf-8")


def patch_test() -> None:
    text = TEST.read_text(encoding="utf-8")
    if "import tempfile\n" not in text:
        anchor = "import sys\n"
        if anchor not in text:
            raise PatchError("test import anchor missing")
        text = text.replace(anchor, anchor + "import tempfile\n", 1)

    marker = '"configuration-gap-resolution-plan",'
    if marker not in text:
        anchor = (
            "        self.assertIn(\n"
            "            \"PASS: Sandero and Stepway official brochure cargo "
            "import contract\",\n"
            "            completed.stdout,\n"
            "        )\n"
        )
        if anchor not in text:
            raise PatchError("import-contract assertion anchor missing")
        addition = (
            anchor
            + "        with tempfile.TemporaryDirectory() as directory:\n"
            + "            plan = subprocess.run(\n"
            + "                [\n"
            + "                    sys.executable,\n"
            + "                    \"tools/dkb.py\",\n"
            + "                    \"configuration-gap-resolution-plan\",\n"
            + "                    \"--json\",\n"
            + "                    str(Path(directory) / \"plan.json\"),\n"
            + "                    \"--markdown\",\n"
            + "                    str(Path(directory) / \"plan.md\"),\n"
            + "                ],\n"
            + "                cwd=ROOT,\n"
            + "                text=True,\n"
            + "                capture_output=True,\n"
            + "                check=False,\n"
            + "            )\n"
            + "        self.assertEqual(\n"
            + "            plan.returncode,\n"
            + "            0,\n"
            + "            plan.stdout + plan.stderr,\n"
            + "        )\n"
        )
        text = text.replace(anchor, addition, 1)
    TEST.write_text(text, encoding="utf-8")


def verify() -> None:
    tool = TOOL.read_text(encoding="utf-8")
    test = TEST.read_text(encoding="utf-8")
    required = (
        "from reporting.cargo_context import context_index, semantic_signature",
        "tuple[str, str, str, str, str]",
        "configuration cargo contexts",
        "semantic_signature(cargo_context) if cargo_context else",
    )
    missing = [item for item in required if item not in tool]
    if missing:
        raise PatchError(f"tool markers missing: {missing}")
    if '"configuration-gap-resolution-plan",' not in test:
        raise PatchError("regression command missing from test")


def main() -> int:
    try:
        patch_tool()
        patch_test()
        verify()
    except (OSError, PatchError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print("PASS: gap resolution cargo-context patch applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
