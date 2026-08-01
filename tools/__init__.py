"""One-shot initializer for the temporary Extreme automatic materializer."""
from pathlib import Path

package_dir = Path(__file__).resolve().parent

importer = package_dir / "import_sandero_stepway_extreme_auto_source_gap_20260626.py"
if importer.exists():
    text = importer.read_text(encoding="utf-8")
    old = "sandero_stepway_expression_auto_source_gap_review"
    new = "sandero_stepway_extreme_auto_source_gap_review"
    if old in text:
        importer.write_text(text.replace(old, new), encoding="utf-8")
    elif new not in text:
        raise RuntimeError("Extreme automatic review-path anchor not found")

aligner = package_dir / "align_sandero_stepway_extreme_auto_snapshot_contracts_20260801.py"
if aligner.exists():
    text = aligner.read_text(encoding="utf-8")
    old = '''    text = re.sub(r'("sandero_stepway_iii_expression_ecog120_automatic":)\\s*\\d+', rf'\\g<1> {configuration_counts["sandero_stepway_iii_expression_ecog120_automatic"]}', text)'''
    new = '''    text = re.sub(r'("sandero_stepway_iii_extreme_ecog120_automatic":)\\s*\\d+', rf'\\g<1> {configuration_counts["sandero_stepway_iii_extreme_ecog120_automatic"]}', text)'''
    if old in text:
        aligner.write_text(text.replace(old, new, 1), encoding="utf-8")
    elif new not in text:
        raise RuntimeError("Extreme automatic availability-count anchor not found")

workbook = package_dir.parent / "tests/test_configuration_comparison_workbook.py"
if workbook.exists():
    text = workbook.read_text(encoding="utf-8")
    old_dimension = '            "A1:M337",'
    new_dimension = '            "A1:M338",'
    if old_dimension in text:
        text = text.replace(old_dimension, new_dimension, 1)
    elif new_dimension not in text:
        raise RuntimeError("Extreme automatic workbook dimension anchor not found")

    old_difference_count = 'self.assertEqual(overview["total_difference_count"], 20)'
    new_difference_count = 'self.assertEqual(overview["total_difference_count"], 22)'
    if old_difference_count in text:
        text = text.replace(old_difference_count, new_difference_count, 1)
    elif new_difference_count not in text:
        raise RuntimeError("Extreme automatic workbook difference-count anchor not found")

    workbook.write_text(text, encoding="utf-8")

if importer.exists() and aligner.exists() and workbook.exists():
    Path(__file__).unlink()
