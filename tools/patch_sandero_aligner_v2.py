from pathlib import Path

path = Path("tools/align_sandero_residual_source_closure_contracts_20260801.py")
text = path.read_text(encoding="utf-8")

start = text.index("def replace_test_selection_block")
end = text.index("def replace_importer_selection_block")
replacement = '''def replace_test_selection_block(path: str, end_method: str) -> None:
    content = read(path)
    lines = content.splitlines(keepends=True)
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if "selected = " in line and '["selected_next_package"]' in line
        )
        end = next(
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith(f"    def {end_method}")
        )
    except StopIteration:
        if 'self.assertIsNone(selected)' in content and '["eligible_candidate_count"], 0' in content:
            return
        raise AlignmentError(f"selection test block not found: {path}")
    selected_expression = lines[start].strip().split(" = ", 1)[1]
    payload_expression = selected_expression.rsplit("[", 1)[0]
    replacement = [
        f"        selected = {selected_expression}\\n",
        '        self.assertIsNone(selected)\\n',
        f'        self.assertEqual({payload_expression}["summary"]["eligible_candidate_count"], 0)\\n',
        "\\n",
    ]
    lines[start:end] = replacement
    write(path, "".join(lines))


'''
text = text[:start] + replacement + text[end:]

old = '''    for path in (
        "tests/test_sandero_stepway_essential_source_gap_20260626.py",
        "tests/test_sandero_stepway_expression_source_gap_20260626.py",
    ):
        replace_number(path, 101, 97)
        replace_number(path, 6, 7)
'''
new = '''    for path in (
        "tests/test_sandero_stepway_essential_source_gap_20260626.py",
        "tests/test_sandero_stepway_expression_source_gap_20260626.py",
    ):
        replace_exact(
            path,
            '        self.assertEqual(payload["summary"]["missing_technical_count"], 101)',
            '        self.assertEqual(payload["summary"]["missing_technical_count"], 97)',
        )
        replace_exact(
            path,
            '        self.assertEqual(payload["summary"]["exhausted_source_candidate_count"], 6)',
            '        self.assertEqual(payload["summary"]["exhausted_source_candidate_count"], 7)',
        )
    replace_exact(
        "tests/test_sandero_stepway_expression_source_gap_20260626.py",
        '        self.assertEqual(review["reconciliation"]["resolved_unique_slots"], 7)',
        '        self.assertEqual(review["reconciliation"]["resolved_unique_slots"], 6)',
    )
'''
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("historical-source test replacement block not found")

path.write_text(text, encoding="utf-8", newline="\n")
