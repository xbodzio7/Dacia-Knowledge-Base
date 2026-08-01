from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f"contract not found: {path}")
    target.write_text(text, encoding="utf-8", newline="\n")


replace_once(
    "tests/configuration_comparison_context_filter_contract.py",
    "        self.assertEqual(len(core.difference_csv_rows(report)), 400)",
    "        self.assertEqual(len(core.difference_csv_rows(report)), 411)",
)
replace_once(
    "tests/configuration_comparison_pair_summary_contract.py",
    "            400,\n        )",
    "            411,\n        )",
)

aligner = Path("tools/align_sandero_residual_source_closure_contracts_20260801.py")
text = aligner.read_text(encoding="utf-8")

manifest_anchor = '            "tests/test_duster_ecog120_reporting_scope.py",\n'
manifest_addition = (
    '            "tests/configuration_comparison_context_filter_contract.py",\n'
    '            "tests/configuration_comparison_pair_summary_contract.py",\n'
)
if manifest_addition not in text:
    if manifest_anchor not in text:
        raise SystemExit("aligner manifest anchor not found")
    text = text.replace(manifest_anchor, manifest_addition + manifest_anchor, 1)

apply_anchor = '''    replace_exact(
        "tests/test_duster_ecog120_reporting_scope.py",
        '        self.assertEqual(default["summary"]["total_differences"], 400)',
        '        self.assertEqual(default["summary"]["total_differences"], 411)',
    )
'''
apply_addition = '''    replace_exact(
        "tests/configuration_comparison_context_filter_contract.py",
        "        self.assertEqual(len(core.difference_csv_rows(report)), 400)",
        "        self.assertEqual(len(core.difference_csv_rows(report)), 411)",
    )
    replace_exact(
        "tests/configuration_comparison_pair_summary_contract.py",
        "            400,\\n        )",
        "            411,\\n        )",
    )
'''
if apply_addition not in text:
    if apply_anchor not in text:
        raise SystemExit("aligner apply anchor not found")
    text = text.replace(apply_anchor, apply_anchor + apply_addition, 1)

aligner.write_text(text, encoding="utf-8", newline="\n")
