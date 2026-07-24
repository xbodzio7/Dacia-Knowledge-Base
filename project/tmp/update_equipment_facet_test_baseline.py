from pathlib import Path

paths = (
    Path("tests/test_jogger_payload_performance_ranges.py"),
    Path("tests/test_jogger_wltp_efficiency_ranges.py"),
)
old = 'self.assertEqual(baseline["tests"], 717)'
new = 'self.assertEqual(baseline["tests"], 719)'
for path in paths:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"expected one baseline assertion in {path}, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
