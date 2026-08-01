from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one patch anchor in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def patch_importer() -> None:
    path = ROOT / "tools/import_spring_commercial_packages.py"
    replace_once(
        path,
        'DATE = "2026-02-19"\n',
        'DATE = "2026-02-19"\n'
        'CONFIGURATOR_SOURCE_CODE = "src_pl_spring_official_configurator_20260731"\n'
        'CONFIGURATOR_PRICE_DATE = "2026-07-31"\n'
        'REVIEWED_PRICE_OVERRIDES = {\n'
        '    "spring_city_package__spring_extreme_electric100_automatic": (\n'
        '        "1800",\n'
        '        "Exact current Spring Extreme electric 100 package price accepted "\n'
        '        "after registered-source completeness review; no transfer to another "\n'
        '        "grade or powertrain.",\n'
        '    ),\n'
        '    "spring_power_package__spring_extreme_electric100_automatic": (\n'
        '        "3000",\n'
        '        "Exact current Spring Extreme electric 100 package price accepted "\n'
        '        "after registered-source completeness review; no transfer to another "\n'
        '        "grade or powertrain.",\n'
        '    ),\n'
        '}\n',
    )
    replace_once(
        path,
        '}\nEXPECTED_ITEM_IDS = (29, 33)\n',
        '}\nEXPECTED_MAPPING_CODES = {\n'
        '    f"{item_code}__{configuration_code}"\n'
        '    for item_code, configuration_code in EXPECTED_MAPPING_PAGES\n'
        '}\nEXPECTED_ITEM_IDS = (29, 33)\n',
    )
    old_function = '''def generated_configurations() -> list[dict[str, str]]:
    verify_source_contract()
    return [
        {
            "code": row["code"],
            "commercial_item_code": row["commercial_item_code"],
            "configuration_code": row["configuration_code"],
            "availability_status": row["availability_status"],
            "amount": "",
            "currency_code": row["currency_code"],
            "price_date": "",
            "source_code": SOURCE_CODE,
            "notes": f"Source page {row['source_page']}. {row['notes']}",
        }
        for row in load_configurations_spec()
    ]
'''
    new_function = '''def generated_configurations() -> list[dict[str, str]]:
    verify_source_contract()
    generated: list[dict[str, str]] = []
    for row in load_configurations_spec():
        result = {
            "code": row["code"],
            "commercial_item_code": row["commercial_item_code"],
            "configuration_code": row["configuration_code"],
            "availability_status": row["availability_status"],
            "amount": "",
            "currency_code": row["currency_code"],
            "price_date": "",
            "source_code": SOURCE_CODE,
            "notes": f"Source page {row['source_page']}. {row['notes']}",
        }
        override = REVIEWED_PRICE_OVERRIDES.get(row["code"])
        if override is not None:
            amount, notes = override
            result.update(
                {
                    "amount": amount,
                    "price_date": CONFIGURATOR_PRICE_DATE,
                    "source_code": CONFIGURATOR_SOURCE_CODE,
                    "notes": notes,
                }
            )
        generated.append(result)
    return generated
'''
    replace_once(path, old_function, new_function)
    text = path.read_text(encoding="utf-8")
    old_predicate = '''lambda row: row.get("source_code") == SOURCE_CODE
        and row.get("commercial_item_code") in EXPECTED_ITEMS,'''
    count = text.count(old_predicate)
    if count != 2:
        raise RuntimeError(f"expected two Spring mapping predicates, found {count}")
    text = text.replace(
        old_predicate,
        'lambda row: row.get("code") in EXPECTED_MAPPING_CODES,',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def patch_shortlist_fixture_compatibility() -> None:
    path = ROOT / "tools/configuration_shortlist.py"
    replace_once(
        path,
        'def _read_reviewed_gap_report(repository: Path) -> dict[str, Any]:\n'
        '    path = repository / _REVIEWED_GAP_REPORT\n'
        '    try:\n'
        '        payload = json.loads(path.read_text(encoding="utf-8"))\n'
        '    except (OSError, json.JSONDecodeError) as exc:\n',
        'def _read_reviewed_gap_report(repository: Path) -> dict[str, Any] | None:\n'
        '    path = repository / _REVIEWED_GAP_REPORT\n'
        '    try:\n'
        '        payload = json.loads(path.read_text(encoding="utf-8"))\n'
        '    except FileNotFoundError:\n'
        '        return None\n'
        '    except (OSError, json.JSONDecodeError) as exc:\n',
    )
    replace_once(
        path,
        '    payload = _read_reviewed_gap_report(repository)\n'
        '    configurations = catalog.get("configurations")\n',
        '    payload = _read_reviewed_gap_report(repository)\n'
        '    if payload is None:\n'
        '        return\n'
        '    configurations = catalog.get("configurations")\n',
    )


def patch_commercial_contract_test() -> None:
    path = ROOT / "tests/test_commercial_items_20260703.py"
    replace_once(
        path,
        'STOCK_DATE = "2026-07-24"\n',
        'STOCK_DATE = "2026-07-24"\nSPRING_CONFIGURATOR_DATE = "2026-07-31"\n',
    )
    replace_once(
        path,
        '        self.assertEqual({row["price_date"] for row in self.mappings}, {"", DATE, STOCK_DATE})\n',
        '        self.assertEqual(\n'
        '            {row["price_date"] for row in self.mappings},\n'
        '            {"", DATE, STOCK_DATE, SPRING_CONFIGURATOR_DATE},\n'
        '        )\n',
    )


def patch_spring_contract_test() -> None:
    path = ROOT / "tests/test_spring_commercial_packages.py"
    replace_once(
        path,
        '            if row["source_code"] == importer.SOURCE_CODE\n'
        '            and row["commercial_item_code"] in importer.EXPECTED_ITEMS\n',
        '            if row["code"] in importer.EXPECTED_MAPPING_CODES\n',
    )
    text = path.read_text(encoding="utf-8")
    start = text.index('    def test_unpriced_components_are_exposed_without_invented_amounts')
    end = text.index('\n    def test_package_membership_aligns_with_direct_optional_matrix_cells', start)
    replacement = '''    def test_reviewed_prices_and_remaining_unknowns_are_exposed_without_inference(self) -> None:
        components = collect_commercial_components(
            ROOT,
            sorted(importer.SELECTED_CONFIGURATIONS),
            "2026-07-31",
        )
        package_components = {
            code: [row for row in rows if row["code"] in importer.EXPECTED_ITEMS]
            for code, rows in components.items()
        }
        self.assertEqual(
            {code: len(rows) for code, rows in package_components.items()},
            {
                "spring_essential_electric70_automatic": 1,
                "spring_expression_electric70_automatic": 3,
                "spring_extreme_electric100_automatic": 3,
            },
        )
        extreme = {
            row["code"]: row
            for row in package_components["spring_extreme_electric100_automatic"]
        }
        self.assertEqual(extreme["spring_city_package"]["amount"], 1800.0)
        self.assertEqual(extreme["spring_power_package"]["amount"], 3000.0)
        self.assertEqual(
            extreme["spring_type2_charging_cable_option"]["amount"],
            None,
        )
        unknown = [
            row
            for rows in package_components.values()
            for row in rows
            if row["amount"] is None
        ]
        self.assertEqual(
            Counter(row["configuration_code"] for row in unknown),
            Counter(
                {
                    "spring_essential_electric70_automatic": 1,
                    "spring_expression_electric70_automatic": 3,
                    "spring_extreme_electric100_automatic": 1,
                }
            ),
        )
        self.assertTrue(all(row["price_date"] == "" for row in unknown))
        self.assertEqual(
            {extreme[code]["price_date"] for code in ("spring_city_package", "spring_power_package")},
            {"2026-07-31"},
        )
'''
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")


def patch_state_contracts() -> None:
    path = ROOT / "tests/test_registered_source_completeness_reconciliation_20260802.py"
    text = path.read_text(encoding="utf-8")
    start = text.index('    def test_project_state_advances_to_materialization_package')
    end = text.index('\n\n\nif __name__', start)
    replacement = '''    def test_completed_review_remains_preserved_after_materialization(self) -> None:
        state = payload(ROOT / "project/state.json")
        self.assertEqual(
            state["reference_delivery"]["name"],
            "Registered Source Completeness Reconciliation",
        )
        self.assertEqual(state["reference_delivery"]["pull_request"], 448)
        self.assertEqual(
            state["current_package"]["package_id"],
            "reviewed_gap_state_materialization_001",
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["package_id"],
            "spring_commercial_context_resolution_001",
        )
        self.assertEqual(state["baseline"]["tests"], 1788)
'''
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")

    path = ROOT / "tests/test_sandero_residual_source_closure_20260801.py"
    text = path.read_text(encoding="utf-8")
    start = text.index('    def test_completed_closure_remains_preserved_after_follow_up_packages')
    end = text.index('\n\nif __name__', start)
    replacement = '''    def test_completed_closure_remains_preserved_after_follow_up_packages(self):
        state = payload(ROOT / "project/state.json")
        self.assertEqual(
            state["reference_delivery"]["name"],
            "Registered Source Completeness Reconciliation",
        )
        self.assertEqual(state["reference_delivery"]["pull_request"], 448)
        self.assertEqual(
            state["current_package"]["package_id"],
            "reviewed_gap_state_materialization_001",
        )
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertEqual(
            state["next_package"]["package_id"],
            "spring_commercial_context_resolution_001",
        )
        self.assertEqual(state["baseline"]["configuration_values"], 3567)
        self.assertEqual(state["baseline"]["availability_records"], 5906)
'''
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")


def patch_manifest() -> None:
    path = ROOT / "project/state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    manifest = state["current_package"]["manifest_paths"]
    additions = [
        "tests/test_commercial_items_20260703.py",
        "tests/test_registered_source_completeness_reconciliation_20260802.py",
        "tests/test_sandero_residual_source_closure_20260801.py",
        "tests/test_spring_commercial_packages.py",
        "tools/import_spring_commercial_packages.py",
    ]
    for item in additions:
        if item not in manifest:
            manifest.append(item)
    state["current_package"]["manifest_paths"] = sorted(manifest)
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    patch_importer()
    patch_shortlist_fixture_compatibility()
    patch_commercial_contract_test()
    patch_spring_contract_test()
    patch_state_contracts()
    patch_manifest()


if __name__ == "__main__":
    main()
