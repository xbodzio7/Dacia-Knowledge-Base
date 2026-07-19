from __future__ import annotations

import json
from pathlib import Path


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def insert_before(text: str, marker: str, addition: str, label: str) -> str:
    if marker not in text:
        raise RuntimeError(f"missing {label} marker")
    return text.replace(marker, addition + marker, 1)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing {label} text")
    return text.replace(old, new, 1)


def patch_context_wrapper() -> None:
    path = "tools/configuration_comparison_context.py"
    text = read(path)
    if 'dest="html_path"' not in text:
        text = insert_before(
            text,
            '    parser.add_argument(\n        "--csv",',
            '''    parser.add_argument(
        "--html",
        dest="html_path",
        type=Path,
        help="Write a self-contained interactive HTML report.",
    )
''',
            "context parser",
        )
    if "arguments.html_path" not in text:
        text = insert_before(
            text,
            "\n        rows = difference_csv_rows(",
            '''
        if arguments.html_path is not None:
            core.write_atomic(
                arguments.html_path,
                core.render_html(report),
            )
            print(
                "HTML configuration comparison report written to "
                f"{arguments.html_path}"
            )
''',
            "context output",
        )
    if 'dest="html_path"' not in text or "arguments.html_path" not in text:
        raise RuntimeError("context wrapper HTML support incomplete")
    write(path, text)


def patch_unified_cli() -> None:
    path = "tools/dkb.py"
    text = read(path)
    if "[--html FILE]" not in text:
        text = replace_once(
            text,
            '"[--json FILE] [--markdown FILE] [--csv FILE]"',
            '"[--json FILE] [--markdown FILE] [--csv FILE] [--html FILE]"',
            "unified CLI usage",
        )
    if "--html ../configuration-comparison.html" not in text:
        marker = '''    print(
        "  python tools/dkb.py configuration-comparison-item-catalog "
'''
        addition = '''    print(
        "  python tools/dkb.py configuration-comparison "
        "--html ../configuration-comparison.html"
    )
'''
        text = insert_before(text, marker, addition, "unified CLI example")
    write(path, text)


def patch_context_contract() -> None:
    path = "tests/configuration_comparison_context_filter_contract.py"
    text = read(path)
    if 'html_path = root / "comparison.html"' not in text:
        text = replace_once(
            text,
            '            markdown_path = root / "comparison.md"\n            csv_path = root / "differences.csv"',
            '            markdown_path = root / "comparison.md"\n            html_path = root / "comparison.html"\n            csv_path = root / "differences.csv"',
            "context contract path",
        )
    if '                        "--html",\n                        str(html_path),' not in text:
        text = replace_once(
            text,
            '                        "--csv",\n                        str(csv_path),',
            '                        "--html",\n                        str(html_path),\n                        "--csv",\n                        str(csv_path),',
            "context contract arguments",
        )
    if "core.render_html(expected_report)" not in text:
        marker = '''            reader = csv.DictReader(
                csv_path.read_text(encoding="utf-8").splitlines()
            )
'''
        addition = '''            self.assertEqual(
                html_path.read_text(encoding="utf-8"),
                core.render_html(expected_report),
            )
'''
        text = insert_before(text, marker, addition, "context contract assertion")
    write(path, text)


def patch_readme() -> None:
    path = "README.md"
    text = read(path)
    text = text.replace(
        "Komenda `configuration-comparison` generuje deterministyczny raport JSON\n"
        "i Markdown dla wszystkich par aktywnych konfiguracji oraz opcjonalny płaski\n"
        "CSV zawierający wyłącznie rzeczywiste różnice.",
        "Komenda `configuration-comparison` generuje deterministyczny raport JSON,\n"
        "Markdown i samodzielny interaktywny HTML dla wszystkich par aktywnych\n"
        "konfiguracji oraz opcjonalny płaski CSV zawierający wyłącznie rzeczywiste różnice.",
        1,
    )
    if "--html ../configuration-comparison.html" not in text:
        text = replace_once(
            text,
            "  --csv ../configuration-comparison-differences.csv\n",
            "  --csv ../configuration-comparison-differences.csv \\\n  --html ../configuration-comparison.html\n",
            "README comparison command",
        )
    text = text.replace(
        "JSON i Markdown pozostają pełnymi formatami: zawierają stany równe,\n"
        "`different` oraz `not_comparable`. CSV jest eksportem użytkowym i pomija\n"
        "wszystkie wyniki inne niż `different`.",
        "JSON, Markdown i HTML pozostają pełnymi formatami: zawierają stany równe,\n"
        "`different` oraz `not_comparable`. HTML zawiera wbudowane style i skrypt\n"
        "filtrowania, działa bez serwera i nie pobiera zewnętrznych zasobów. CSV jest\n"
        "eksportem użytkowym i pomija wszystkie wyniki inne niż `different`.",
        1,
    )
    text = text.replace(
        "* rozwój i uzupełnianie danych,\n",
        "* praktyczne wykorzystanie zamkniętego portfela danych,\n"
        "* interaktywne i eksportowalne porównania konfiguracji,\n",
        1,
    )
    required = (
        "samodzielny interaktywny HTML",
        "--html ../configuration-comparison.html",
        "nie pobiera zewnętrznych zasobów",
        "praktyczne wykorzystanie zamkniętego portfela danych",
    )
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise RuntimeError(f"README markers missing: {missing}")
    write(path, text)


def patch_changelog_and_roadmap() -> None:
    changelog = read("CHANGELOG.md")
    bullet = (
        "* Self-contained interactive HTML configuration comparison reports with "
        "offline filtering, source provenance and evidence-aware states.\n"
    )
    if bullet not in changelog:
        changelog = replace_once(
            changelog,
            "### Added\n\n",
            "### Added\n\n"
            + bullet
            + "* GitHub Actions publication of current Sandero browser reports with a SHA-256 artifact manifest.\n",
            "changelog Added heading",
        )
    write("CHANGELOG.md", changelog)

    roadmap = read("project/ROADMAP.md")
    completed = "- samodzielny interaktywny HTML porównań z filtrowaniem i proweniencją,\n"
    if completed not in roadmap:
        roadmap = replace_once(
            roadmap,
            "- raporty porównawcze konfiguracji i katalog kodów pozycji,\n",
            "- raporty porównawcze konfiguracji i katalog kodów pozycji,\n" + completed,
            "roadmap completed reporting",
        )
    roadmap = roadmap.replace(
        "- stabilne formaty raportów dla użytkowników zewnętrznych.\n",
        "- dalsze stabilne formaty raportów dla użytkowników zewnętrznych.\n",
        1,
    )
    write("project/ROADMAP.md", roadmap)


def patch_state() -> None:
    path = Path("project/state.json")
    state = json.loads(path.read_text(encoding="utf-8"))
    state["updated_on"] = "2026-07-19"
    state["phase"] = "Data Product Utilization"
    state["reference_delivery"] = {
        "name": "Registered Source Reporting Portfolio Completion Review",
        "pull_request": 142,
        "head_sha": "fd1e1a9bbe8b1acd52dc21c8b0818fd252519223",
        "quality_run": 689,
    }
    state["baseline"]["tests"] = 593
    state["current_package"] = {
        "name": "Interactive Configuration Comparison HTML",
        "status": "active",
        "goal": "Publish deterministic browser-ready configuration comparisons with offline filters, source provenance and unchanged evidence semantics.",
    }
    state["next_package"] = {
        "name": "Configuration Discovery and Shortlist Planning Review",
        "status": "planned",
        "goal": "Select the next user-facing workflow for finding and shortlisting configurations from the completed registered-source portfolio.",
    }
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    patch_context_wrapper()
    patch_unified_cli()
    patch_context_contract()
    patch_readme()
    patch_changelog_and_roadmap()
    patch_state()


if __name__ == "__main__":
    main()
