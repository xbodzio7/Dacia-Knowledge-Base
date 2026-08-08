from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import configuration_shortlist as shortlist_cli  # noqa: E402
from reporting.configuration_shortlist import ShortlistCriteria  # noqa: E402
from reporting.configuration_shortlist_html import collect_browser_catalog  # noqa: E402

MAPPINGS = ROOT / "data/master/commercial_item_configurations.csv"
IMPORT_SPEC = ROOT / "data/imports/reviewed_gap_state_materialization_20260802.csv"
APPLY_SCRIPT = ROOT / "tools/apply_reviewed_gap_state_materialization_20260802.py"
PRICING_JS = ROOT / "tools/reporting/configuration_shortlist_v12_pricing.js"
TARGETS = {
    "spring_city_package__spring_extreme_electric100_automatic": "1800",
    "spring_power_package__spring_extreme_electric100_automatic": "3000",
}
KHaki_TARGET = "spring_colour_lichen_khaki__spring_essential_electric70_automatic"
TYPE2_MAPPING_CODES = {
    "spring_type2_charging_cable_option__spring_essential_electric70_automatic",
    "spring_type2_charging_cable_option__spring_expression_electric70_automatic",
    "spring_type2_charging_cable_option__spring_extreme_electric100_automatic",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_apply_module():
    spec = importlib.util.spec_from_file_location("reviewed_gap_apply", APPLY_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewedGapStateMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = collect_browser_catalog(ROOT, ShortlistCriteria())
        shortlist_cli._apply_reviewed_gap_states(cls.catalog, ROOT)
        cls.by_code = {
            item["configuration_code"]: item
            for item in cls.catalog["configurations"]
        }

    def test_two_exact_current_spring_prices_are_materialized(self) -> None:
        selected = {row["code"]: row for row in rows(MAPPINGS) if row["code"] in TARGETS}
        self.assertEqual(set(selected), set(TARGETS))
        for code, amount in TARGETS.items():
            row = selected[code]
            self.assertEqual(row["amount"], amount)
            self.assertEqual(row["price_date"], "2026-07-31")
            self.assertEqual(row["source_code"], "src_pl_spring_official_configurator_20260731")
            self.assertEqual(row["availability_status"], "optional")
        self.assertEqual(len(rows(MAPPINGS)), 189)

    def test_importer_is_idempotent_and_updates_only_two_rows(self) -> None:
        module = load_apply_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/master").mkdir(parents=True)
            (root / "data/imports").mkdir(parents=True)
            shutil.copy2(MAPPINGS, root / "data/master/commercial_item_configurations.csv")
            shutil.copy2(IMPORT_SPEC, root / "data/imports/reviewed_gap_state_materialization_20260802.csv")
            path = root / "data/master/commercial_item_configurations.csv"
            current = rows(path)
            for row in current:
                if row["code"] in TARGETS:
                    row["amount"] = ""
                    row["price_date"] = ""
                    row["source_code"] = "src_pl_spring_brochure_20260219"
                    row["notes"] = "review fixture"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=module.FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(current)
            self.assertEqual(module.materialize(root), 2)
            self.assertEqual(module.materialize(root), 0)
            self.assertEqual(len(rows(path)), 189)

    def test_all_technical_review_states_are_visible(self) -> None:
        review_states = [
            state
            for configuration in self.catalog["configurations"]
            for state in configuration.get("comparison_values", {}).values()
            if state.get("kind") == "reviewed_gap"
        ]
        self.assertEqual(len(review_states), 22)
        self.assertEqual(
            Counter(state["review_state"] for state in review_states),
            Counter({"source-not-stated": 20, "context-unmodeled": 2}),
        )
        self.assertEqual(
            sum(state["display_value"] == "nie dotyczy — skrzynia automatyczna" for state in review_states),
            2,
        )

    def test_all_commercial_review_states_are_attached(self) -> None:
        reviewed = [
            component
            for configuration in self.catalog["configurations"]
            for component in configuration.get("price_components", [])
            if component.get("review_state")
        ]
        expected = Counter(
            {
                "importable": 2,
                "source-not-stated": 3,
                "source-conflict": 2,
                "context-unmodeled": 18,
            }
        )
        if self.catalog["as_of"] >= "2026-08-02":
            # Advancing the live catalog boundary exposes one additional
            # reviewed commercial component. The existing review ledger
            # classifies it as source-not-stated; a later date alone is not
            # permission to promote it to importable. The three historical
            # Spring Type 2 option mappings remain in master history but are
            # intentionally absent from the current selector because later
            # exact-current canonical evidence says the cable is standard.
            expected["source-not-stated"] += 1
        self.assertEqual(len(reviewed), sum(expected.values()))
        self.assertEqual(
            Counter(item["review_state"] for item in reviewed),
            expected,
        )
        preserved_type2 = {
            row["code"]
            for row in rows(MAPPINGS)
            if row["code"] in TYPE2_MAPPING_CODES
        }
        self.assertEqual(preserved_type2, TYPE2_MAPPING_CODES)
        for configuration_code in (
            "spring_essential_electric70_automatic",
            "spring_expression_electric70_automatic",
            "spring_extreme_electric100_automatic",
        ):
            current_codes = {
                item["code"]
                for item in self.by_code[configuration_code].get("price_components", [])
            }
            self.assertNotIn("spring_type2_charging_cable_option", current_codes)
        extreme = self.by_code["spring_extreme_electric100_automatic"]
        amounts = {item["code"]: item["amount"] for item in extreme["price_components"]}
        self.assertEqual(amounts["spring_city_package"], 1800.0)
        self.assertEqual(amounts["spring_power_package"], 3000.0)
        khaki = next(row for row in rows(MAPPINGS) if row["code"] == KHaki_TARGET)
        self.assertEqual(khaki["availability_status"], "optional")
        self.assertEqual(khaki["amount"], "2300")
        self.assertEqual(khaki["currency_code"], "PLN")
        self.assertEqual(khaki["price_date"], "2026-08-02")
        self.assertEqual(khaki["source_code"], "src_pl_spring_commercial_context_20260802")

    def test_pricing_script_explains_terminal_review_states(self) -> None:
        program = f"""
const pricing = require({json.dumps(str(PRICING_JS))});
const values = [
  pricing.reviewedUnknownPriceStatus({{review_state:'source-conflict'}}),
  pricing.reviewedUnknownPriceStatus({{review_state:'source-not-stated'}}),
  pricing.reviewedUnknownPriceStatus({{review_state:'context-unmodeled', review_reason_code:'model-year-stock-context-not-modeled', candidate_amount_pln:2750, currency_code:'PLN'}}),
  pricing.reviewedUnknownPriceStatus({{review_state:'context-unmodeled', review_reason_code:'stock-selection-and-standalone-price-are-separate-record-contexts', candidate_amount_pln:2200, currency_code:'PLN'}})
];
console.log(JSON.stringify(values));
"""
        completed = subprocess.run(
            ["node", "-e", program], cwd=ROOT, check=True,
            capture_output=True, text=True, encoding="utf-8",
        )
        values = json.loads(completed.stdout)
        self.assertIn("sprzeczne dane źródłowe", values[0])
        self.assertIn("dokładnym źródle", values[1])
        self.assertIn("MY25", values[2])
        self.assertIn("odrębna cena cennikowa", values[3])

    def test_completed_materialization_remains_preserved(self) -> None:
        state = json.loads((ROOT / "project/state.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(state["reference_delivery"]["pull_request"], 449)
        self.assertEqual(state["current_package"]["status"], "complete")
        self.assertTrue(state["current_package"]["package_id"])
        self.assertTrue(state["next_package"]["package_id"])
        self.assertGreaterEqual(state["baseline"]["tests"], 1788)
        self.assertGreaterEqual(state["baseline"]["rows"], 11713)


if __name__ == "__main__":
    unittest.main()
