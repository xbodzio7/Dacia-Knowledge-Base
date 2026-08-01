"""One-shot initializer for the temporary package generator."""
from pathlib import Path

package_dir = Path(__file__).resolve().parent
builder = package_dir / "build_sandero_stepway_expression_auto_source_gap_20260801.py"
text = builder.read_text(encoding="utf-8")

old_regex = "r'expected_counts = \\{.*?\\n        \\}'"
new_regex = "r'expected_counts = \\{.*?\\}'"
if old_regex in text:
    text = text.replace(old_regex, new_regex, 1)
elif new_regex not in text:
    raise RuntimeError("context snapshot matcher anchor not found")

old_import = "from tools import existing_configuration_missing_data_analysis as analysis  # noqa: E402"
new_import = (
    old_import
    + "\nfrom tools import import_sandero_stepway_expression_auto_source_gap_20260626 as package  # noqa: E402"
)
if old_import in text and new_import not in text:
    text = text.replace(old_import, new_import, 1)
elif new_import not in text:
    raise RuntimeError("analysis refresh import anchor not found")

old_apply = "    align_spring_contracts(state, range_count)\n    update_manifest()"
new_apply = (
    "    align_spring_contracts(state, range_count)\n"
    "    package.update_analysis_outputs()\n"
    "    update_manifest()"
)
if old_apply in text:
    text = text.replace(old_apply, new_apply, 1)
elif new_apply not in text:
    raise RuntimeError("analysis refresh apply anchor not found")

old_range_patterns = (
    '        "tests/test_configuration_value_ranges.py": '
    "[r'(len\\(rows\\[1:\\]\\), )\\d+', r'(checked, )\\d+', r'(count, )\\d+'],"
)
new_range_patterns = (
    '        "tests/test_configuration_value_ranges.py": '
    "[r'(len\\(rows\\[1:\\]\\), )\\d+', r'(count, )\\d+'],"
)
if old_range_patterns in text:
    text = text.replace(old_range_patterns, new_range_patterns, 1)
elif new_range_patterns not in text:
    raise RuntimeError("range snapshot pattern list not found")

builder.write_text(text, encoding="utf-8")
Path(__file__).unlink()
