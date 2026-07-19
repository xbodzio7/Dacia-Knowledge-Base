from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "tests/test_jogger_payload_performance_ranges.py",
    ROOT / "tests/test_jogger_wltp_efficiency_ranges.py",
]

for path in FILES:
    text = path.read_text(encoding="utf-8")
    old = 'self.assertEqual(baseline["tests"], 544)'
    if text.count(old) != 1:
        raise RuntimeError(f"unexpected baseline assertion count in {path}")
    path.write_text(text.replace(old, 'self.assertEqual(baseline["tests"], 551)'), encoding="utf-8")

log = ROOT / "project/audits/jogger-ecog120-automatic-finalize.log"
if log.exists():
    log.unlink()

subprocess.run(["python", "tools/dkb.py", "project-state", "--check"], cwd=ROOT, check=True)
subprocess.run(["python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"], cwd=ROOT, check=True)
subprocess.run(["python", "tools/dkb.py", "quality", "--concise", "--database", "/tmp/dkb.sqlite", "--log-file", "/tmp/dkb-quality.log", "--summary-json", "/tmp/dkb-quality.json"], cwd=ROOT, check=True)
