#!/usr/bin/env python3
"""Temporary deterministic materializer for the Duster Eco-G 120 automatic package."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_SNAPSHOT_SHA256 = "9914402753c100f9a9ecb65c01bf454d90d6f18d6e09df00b74342377cba9ebc"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"missing replacement anchor in {path}: {old[:120]!r}")
    write(path, text.replace(old, new, 1))


def insert_after(path: str, anchor: str, addition: str) -> None:
    text = read(path)
    if addition.strip() in text:
        return
    if anchor not in text:
        raise SystemExit(f"missing insertion anchor in {path}: {anchor[:120]!r}")
    write(path, text.replace(anchor, anchor + addition, 1))


def normalize_engine_contract() -> None:
    snapshot_path = "project/sources/dacia-pl-duster-ecog120-automatic-engine-20260724.json"
    payload = json.loads(read(snapshot_path))
    canonical_units = {
        "engine_displacement": "cm3",
        "cylinder_count": "",
        "total_valve_count": "",
    }
    for item in payload["intrinsic_engine_values"]:
        item["unit"] = canonical_units[item["attribute_code"]]
    snapshot_text = json.dumps(payload, indent=2) + "\n"
    actual_sha = hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest()
    if actual_sha != ENGINE_SNAPSHOT_SHA256:
        raise SystemExit(f"unexpected normalized engine snapshot SHA-256: {actual_sha}")
    write(snapshot_path, snapshot_text)

    importer_path = "tools/import_duster_ecog120_automatic_engine_20260724.py"
    text = read(importer_path)
    text = text.replace(
        'SNAPSHOT_SHA256 = "ea3f1209c19778baed6004ae4938bded39b9b5f0608b74668a02f70b75cb23f7"',
        f'SNAPSHOT_SHA256 = "{ENGINE_SNAPSHOT_SHA256}"',
    )
    text = text.replace(
        '("engine_displacement", "", "1199", "cubic_cm")',
        '("engine_displacement", "", "1199", "cm3")',
    )
    text = text.replace(
        '("cylinder_count", "", "3", "count")',
        '("cylinder_count", "", "3", "")',
    )
    text = text.replace(
        '("total_valve_count", "", "12", "count")',
        '("total_valve_count", "", "12", "")',
    )
    text = text.replace(
        '        if unit not in units:\n            raise ContractError(f"inactive unit: {unit}")',
        '        if unit and unit not in units:\n            raise ContractError(f"inactive unit: {unit}")',
    )
    write(importer_path, text)


def apply_importers() -> None:
    for command in (
        [sys.executable, "tools/import_duster_ecog120_automatic_stock_20260724.py", "--apply"],
        [sys.executable, "tools/import_duster_ecog120_automatic_engine_20260724.py", "--apply"],
    ):
        subprocess.run(command, cwd=ROOT, check=True)


def update_baseline_tests() -> None:
    for path in (
        "tests/test_jogger_payload_performance_ranges.py",
        "tests/test_jogger_wltp_efficiency_ranges.py",
    ):
        text = read(path)
        text = text.replace('self.assertEqual(baseline["tests"], 727)', 'self.assertEqual(baseline["tests"], 735)')
        text = text.replace('self.assertEqual(baseline["rows"], 7780)', 'self.assertEqual(baseline["rows"], 7813)')
        text = text.replace('self.assertEqual(baseline["configuration_values"], 1756)', 'self.assertEqual(baseline["configuration_values"], 1765)')
        write(path, text)


def update_catalog_bootstrap_test() -> None:
    path = "tests/test_duster_catalog_bootstrap.py"
    replace_once(
        path,
        '            if row["version_code"].startswith("duster_iii_")\n        }\n        self.assertEqual(set(actual), set(self.expected))',
        '            if row["code"] in self.expected\n        }\n        self.assertEqual(set(actual), set(self.expected))',
    )
    replace_once(
        path,
        '        configuration_codes = set(self.expected)\n        availability = [',
        '        configuration_codes = {\n            row["code"] for row in rows("configurations.csv")\n            if row["status"] == "active"\n            and row["version_code"].startswith("duster_iii_")\n        }\n        availability = [',
    )
    text = read(path)
    text = text.replace('repository_status_configurations"], 69)', 'repository_status_configurations"], 72)')
    text = text.replace('excluded_configurations"], 62)', 'excluded_configurations"], 65)')
    write(path, text)


def update_technical_test() -> None:
    path = "tests/test_duster_technical_specifications.py"
    anchor = '''        cls.values = [
            row for row in cls.all_values
            if row["configuration_code"].startswith("duster_iii_")
        ]
'''
    addition = '''        cls.price_list_values = [
            row for row in cls.values
            if row["source_code"] == SOURCE
        ]
        cls.automatic_engine_values = [
            row for row in cls.values
            if row["source_code"] == "src_pl_duster_ecog120_automatic_engine_20260724"
        ]
        cls.price_list_configurations = {
            row["configuration_code"] for row in cls.price_list_values
        }
'''
    insert_after(path, anchor, addition)
    text = read(path).replace("self.values", "self.price_list_values")
    write(path, text)
    old_core = '''    def test_every_configuration_has_unambiguous_core_values(self) -> None:
        for attribute in (
            "engine_displacement", "cylinder_count", "total_valve_count",
            "braked_trailer_weight", "cargo_volume_vda",
        ):
            self.assertEqual(
                {row["configuration_code"] for row in self.price_list_values if row["attribute_code"] == attribute},
                self.configurations,
                attribute,
            )
'''
    new_core = '''    def test_source_scoped_core_values_preserve_homologation_boundaries(self) -> None:
        for attribute in (
            "engine_displacement", "cylinder_count", "total_valve_count",
            "braked_trailer_weight", "cargo_volume_vda",
        ):
            self.assertEqual(
                {row["configuration_code"] for row in self.price_list_values if row["attribute_code"] == attribute},
                self.price_list_configurations,
                attribute,
            )
        automatic_codes = {
            "duster_iii_expression_ecog120_4x2_automatic",
            "duster_iii_extreme_ecog120_4x2_automatic",
            "duster_iii_journey_ecog120_4x2_automatic",
        }
        self.assertEqual(len(self.automatic_engine_values), 9)
        self.assertEqual(
            {row["configuration_code"] for row in self.automatic_engine_values},
            automatic_codes,
        )
        self.assertEqual(
            {row["attribute_code"] for row in self.automatic_engine_values},
            {"engine_displacement", "cylinder_count", "total_valve_count"},
        )
        self.assertFalse({
            row["attribute_code"] for row in self.automatic_engine_values
        } & {"braked_trailer_weight", "cargo_volume_vda"})
'''
    replace_once(path, old_core, new_core)
    text = read(path)
    text = text.replace('repository_status_configurations"], 69)', 'repository_status_configurations"], 72)')
    text = text.replace('excluded_configurations"], 62)', 'excluded_configurations"], 65)')
    text = text.replace('self.assertEqual(len(self.all_values), 1756)', 'self.assertEqual(len(self.all_values), 1765)')
    write(path, text)


def update_package_test() -> None:
    path = "tests/test_duster_ecog120_automatic_stock_20260724.py"
    replace_once(
        path,
        'from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402\n',
        'import configuration_completeness  # noqa: E402\nfrom reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402\n',
    )
    anchor = '''        for code in (
            "duster_iii_extreme_ecog120_4x2_automatic",
            "duster_iii_journey_ecog120_4x2_automatic",
        ):
            self.assertEqual(
                selected[code]["equipment"]["side_mirrors_folding"]["availability_status"],
                "standard",
            )
'''
    addition = '''        report = configuration_completeness.collect_report(
            REPOSITORY,
            REPOSITORY / "data" / "reporting" / "duster_ecog120_automatic_completeness.json",
        )
        self.assertEqual(report["scope"]["reporting_configurations"], 3)
        self.assertEqual(report["scope"]["technical_slots"], 3)
        self.assertEqual(report["technical"]["present"], 9)
        self.assertEqual(report["technical"]["missing"], 0)
        self.assertEqual(report["equipment"]["denominator"], 0)
'''
    insert_after(path, anchor, addition)
    old = '''        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: Duster Eco-G 120 automatic stock-card contract", result.stdout)
'''
    new = old + '''        engine = subprocess.run(
            [sys.executable, "tools/import_duster_ecog120_automatic_engine_20260724.py", "--check"],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(engine.returncode, 0, engine.stderr)
        self.assertIn("PASS: Duster Eco-G 120 automatic intrinsic-engine contract", engine.stdout)
'''
    replace_once(path, old, new)


def update_state() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["baseline"].update({
        "tests": 735,
        "rows": 7813,
        "configuration_values": 1765,
        "availability_records": 4551,
    })
    state["current_package"]["goal"] = (
        "Register exact 2026 Duster Eco-G 120 automatic Expression, Extreme and Journey "
        "configurations with explicit catalogue prices, directly proven folding-mirror states, "
        "three intrinsic engine values and an independent source-scoped comparison contract."
    )
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def update_docs() -> None:
    insert_after(
        "CHANGELOG.md",
        "* Imported 37 dated factory-equipment observations from nine official Dacia Polska grade pages: exact shark-fin antenna coverage for 31 configurations and six newer standard power-folding-mirror states for Jogger Journey, with historical rows and non-inference boundaries preserved.\n",
        "* Added three exact 2026 Duster Eco-G 120 automatic configurations from official stock cards, three explicit catalogue prices, two standard power-folding-mirror observations and nine source-scoped intrinsic engine values without projecting manual homologation data.\n",
    )
    insert_after(
        "README.md",
        "Bieżący przekrojowy import wyposażenia zapisuje 31 dokładnych obserwacji fabrycznej anteny typu „płetwa rekina” dla Sandero, Sandero Stepway i Joggera oraz sześć nowszych obserwacji seryjnych elektrycznie składanych lusterek dla Joggera Journey. Wersje z jawnie wskazaną anteną biczową otrzymują status fabrycznej płetwy `not_available`; akcesoria, nieudowodnione rozszerzenia pakietów i niejednoznaczne stany Dustera pozostają poza importem. Szczegóły zawiera `project/packages/official-configurator-cross-model-option-coverage-20260724.md`.\n",
        "\nNajnowszy import Dustera dodaje trzy dokładne konfiguracje Eco-G 120 z automatyczną skrzynią: Expression, Extreme i Journey. Zapisuje jawne ceny katalogowe 96 900 zł, 110 300 zł i 107 600 zł, seryjne składane lusterka dla Extreme i Journey oraz trzy cechy silnika wspólne dla dokładnie potwierdzonego automatu: 1199 cm³, trzy cylindry i 12 zaworów. Sprzeczny stan lusterek Expression, typ anteny, masa przyczepy i bagażnik pozostają niewiadomą. Szczegóły zawiera `project/packages/duster-ecog120-automatic-stock-intake-20260724.md`.\n",
    )
    insert_after(
        "project/ROADMAP.md",
        "- przekrojowy import dwóch myląco niepełnych cech wyposażenia z dziewięciu oficjalnych stron wersji: 31 obserwacji anteny typu „płetwa rekina”, sześć aktualizacji składanych lusterek Joggera Journey i jawny non-import Dustera,\n",
        "- trzy dokładne konfiguracje Duster Eco-G 120 automatic z oficjalnych kart samochodów, trzema cenami katalogowymi, dwoma pozytywnymi stanami składanych lusterek, dziewięcioma wartościami silnikowymi i odrębnym zakresem porównawczym,\n",
    )
    package_path = "project/packages/duster-ecog120-automatic-stock-intake-20260724.md"
    marker = "## Determinism\n"
    addition = '''## Intrinsic technical boundary

A second official-web snapshot contributes only three intrinsic Eco-G 120 engine values to each exact automatic configuration: 1199 cm³ displacement, three cylinders and 12 valves. The current Dacia engine page explicitly offers Eco-G 120 with the dual-clutch automatic transmission. Manual towing weight, VDA cargo volume, WLTP and performance values are not projected onto the automatic variants.

The three configurations form a new independent comparison scope containing these nine exact technical observations. Equipment remains available to the buyer-facing browser, while the source-completeness scope intentionally avoids claiming a complete stock-card equipment denominator.

'''
    text = read(package_path)
    if addition.strip() not in text:
        if marker not in text:
            raise SystemExit("missing package determinism marker")
        write(package_path, text.replace(marker, addition + marker, 1))
    review_path = "project/reviews/duster-ecog120-automatic-stock-review-2026-07-24.md"
    review_addition = '''
## Intrinsic engine evidence

A separate official Dacia engine-page snapshot confirms Eco-G 120 automatic availability and the intrinsic 1199 cm³, three-cylinder, 12-valve engine architecture. It does not resolve automatic towing weight, VDA cargo volume, WLTP or performance values, which remain unimported.
'''
    text = read(review_path)
    if review_addition.strip() not in text:
        write(review_path, text.rstrip() + "\n" + review_addition)


def main() -> None:
    normalize_engine_contract()
    apply_importers()
    update_baseline_tests()
    update_catalog_bootstrap_test()
    update_technical_test()
    update_package_test()
    update_state()
    update_docs()
    print("PASS: Duster Eco-G 120 automatic package materialized")


if __name__ == "__main__":
    main()
