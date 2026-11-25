#!/usr/bin/env python3
"""Reject brittle whole-table assertions in changed tests for shared master CSVs."""
from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED_TABLES = {
    "commercial_items.csv",
    "commercial_item_attributes.csv",
    "commercial_item_configurations.csv",
    "configuration_attribute_values.csv",
    "configuration_attribute_value_ranges.csv",
    "configuration_attribute_availability.csv",
    "configuration_prices.csv",
    "sources.csv",
    "source_models.csv",
    "source_configurations.csv",
    "source_versions.csv",
}


def _attribute_name(node: ast.AST) -> str | None:
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    ):
        return node.attr
    return None


def _master_attributes(tree: ast.Module) -> dict[str, str]:
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if not isinstance(value, ast.Call) or not value.args:
            continue
        if not isinstance(value.func, ast.Name) or value.func.id not in {"read", "rows"}:
            continue
        filename = value.args[0]
        if not isinstance(filename, ast.Constant) or not isinstance(filename.value, str):
            continue
        if Path(filename.value).name not in SHARED_TABLES:
            continue
        for target in targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "cls"
            ):
                found[target.attr] = Path(filename.value).name
    return found


def _comprehension_origin(node: ast.AST, master_attributes: dict[str, str]) -> tuple[bool, set[str]]:
    if not isinstance(node, (ast.SetComp, ast.ListComp, ast.GeneratorExp, ast.DictComp)):
        return False, set()
    sourced = False
    scope_fields: set[str] = set()
    for generator in node.generators:
        sourced = sourced or _attribute_name(generator.iter) in master_attributes
        for condition in generator.ifs:
            for item in ast.walk(condition):
                if not isinstance(item, ast.Subscript):
                    continue
                if not isinstance(item.value, ast.Name):
                    continue
                key = item.slice
                if isinstance(key, ast.Constant) and key.value in {"source_code", "code"}:
                    scope_fields.add(key.value)
    return sourced, scope_fields


def _has_exact_source_scope(scope_fields: set[str], node: ast.AST) -> bool:
    if not scope_fields:
        return False
    for item in ast.walk(node):
        if not isinstance(item, ast.Compare):
            continue
        left = item.left
        if (
            isinstance(left, ast.Subscript)
            and isinstance(left.value, ast.Name)
            and isinstance(left.slice, ast.Constant)
            and left.slice.value in scope_fields
            and any(isinstance(op, (ast.In, ast.Eq)) for op in item.ops)
        ):
            return True
    return False


def inspect_test(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        return [f"{path.relative_to(ROOT)}: cannot parse test: {exc}"]

    master_attributes = _master_attributes(tree)
    if not master_attributes:
        return []

    derived: dict[str, tuple[str, bool]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        sourced, scope_fields = _comprehension_origin(node.value, master_attributes)
        if not sourced:
            continue
        safe = _has_exact_source_scope(scope_fields, node.value)
        for target in targets:
            if isinstance(target, ast.Name):
                derived[target.id] = ("shared master table", safe)

    problems: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "assertEqual" or len(node.args) < 2:
            continue
        left, right = node.args[:2]
        constant_count = (
            isinstance(right, ast.Constant)
            and isinstance(right.value, (int, float))
            and not isinstance(right.value, bool)
        )
        if constant_count and isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id == "len" and left.args:
            attr = _attribute_name(left.args[0])
            if attr in master_attributes:
                problems.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: exact count asserted on the entire shared table {master_attributes[attr]}"
                )
                continue
            if isinstance(left.args[0], ast.Name) and left.args[0].id in derived:
                _, safe = derived[left.args[0].id]
                if not safe:
                    problems.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: exact count asserted on a package-like subset without an exact source-code filter"
                    )

        if isinstance(left, ast.SetComp):
            sourced, scope_fields = _comprehension_origin(left, master_attributes)
            if not sourced or _has_exact_source_scope(scope_fields, left):
                continue
            element = left.elt
            if (
                isinstance(element, ast.Subscript)
                and isinstance(element.slice, ast.Constant)
                and element.slice.value in {"observation_date", "price_date", "document_date"}
            ):
                problems.append(
                    f"{path.relative_to(ROOT)}:{node.lineno}: exact date-set assertion spans the entire shared table; scope it to source/package identities"
                )

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", required=True)
    args = parser.parse_args()
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{args.base_ref}...{args.head_ref}", "--", "tests"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        print(completed.stderr, file=sys.stderr)
        return completed.returncode
    changed_tests = [
        ROOT / name
        for name in completed.stdout.splitlines()
        if name.startswith("tests/test_") and name.endswith(".py")
    ]
    if not changed_tests:
        print("PASS: no changed test modules require shared-master contract review")
        return 0

    problems = [
        problem
        for path in changed_tests
        for problem in inspect_test(path)
    ]
    if problems:
        print("FAIL: shared master-table tests contain brittle whole-table assertions")
        print("\n".join(f"- {problem}" for problem in problems))
        print(
            "Use exact source/package identity filters for package contracts; "
            "derive portfolio-wide inventories from canonical registries."
        )
        return 1

    print(f"PASS: inspected {len(changed_tests)} changed test module(s) for shared-master growth safety")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
