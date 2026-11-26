#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"missing repair anchor: {path}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    replace(
        "tools/apply_spring_biel_alpejska_default_colour_migration_20260802.py",
        '    if len(type2) != 3 or len(domestic) != 2:\n        raise AssertionError("completed charging-cable mappings were not preserved")',
        '    if len(type2) != 3 or len(domestic) not in {2, 3}:\n        raise AssertionError("completed charging-cable mappings were not preserved")\n    if len(domestic) == 3 and {row["configuration_code"] for row in domestic} != {\n        "spring_essential_electric70_automatic",\n        "spring_expression_electric70_automatic",\n        "spring_extreme_electric100_automatic",\n    }:\n        raise AssertionError("corrected domestic-cable mapping scope drifted")',
    )
    replace(
        "tools/review_spring_charging_cable_commercial_semantics_20260802.py",
        '        if len(domestic_memberships) != 1 or len(domestic_mappings) != 2:\n            raise AssertionError("materialized domestic-cable representation is incomplete")',
        '        if len(domestic_memberships) != 1 or len(domestic_mappings) not in {2, 3}:\n            raise AssertionError("materialized domestic-cable representation is incomplete")',
    )
    replace(
        "tools/review_spring_charging_cable_commercial_semantics_20260802.py",
        '        if {row["configuration_code"] for row in domestic_mappings} != {\n            "spring_essential_electric70_automatic",\n            "spring_extreme_electric100_automatic",\n        }:\n            raise AssertionError("materialized domestic mapping scope drifted")',
        '        accepted_scopes = {\n            frozenset({\n                "spring_essential_electric70_automatic",\n                "spring_extreme_electric100_automatic",\n            }),\n            frozenset({\n                "spring_essential_electric70_automatic",\n                "spring_expression_electric70_automatic",\n                "spring_extreme_electric100_automatic",\n            }),\n        }\n        if frozenset(row["configuration_code"] for row in domestic_mappings) not in accepted_scopes:\n            raise AssertionError("materialized domestic mapping scope drifted")',
    )
    replace(
        "tests/test_commercial_items_20260703.py",
        '        self.assertEqual(len(self.mappings), 188)',
        '        self.assertEqual(len(self.mappings), 189)',
    )
    replace(
        "tests/test_reviewed_gap_state_materialization_20260802.py",
        '        self.assertEqual(len(rows(MAPPINGS)), 188)',
        '        self.assertEqual(len(rows(MAPPINGS)), 189)',
    )
    replace(
        "tests/test_reviewed_gap_state_materialization_20260802.py",
        '            self.assertEqual(len(rows(path)), 188)',
        '            self.assertEqual(len(rows(path)), 189)',
    )
    old = '''        self.assertEqual(
            {item["configuration_code"] for item in mappings},
            {
                "spring_essential_electric70_automatic",
                "spring_extreme_electric100_automatic",
            },
        )
        self.assertTrue(
            all(
                item["availability_status"] == "optional"
                and item["amount"] == "1500"
                and item["currency_code"] == "PLN"
                and item["price_date"] == "2026-08-02"
                and item["source_code"]
                == "src_pl_spring_commercial_context_20260802"
                for item in mappings
            )
        )'''
    new = '''        by_configuration = {item["configuration_code"]: item for item in mappings}
        self.assertEqual(
            set(by_configuration),
            {
                "spring_essential_electric70_automatic",
                "spring_expression_electric70_automatic",
                "spring_extreme_electric100_automatic",
            },
        )
        for configuration in (
            "spring_essential_electric70_automatic",
            "spring_extreme_electric100_automatic",
        ):
            item = by_configuration[configuration]
            self.assertEqual(item["availability_status"], "optional")
            self.assertEqual(item["amount"], "1500")
            self.assertEqual(item["currency_code"], "PLN")
            self.assertEqual(item["price_date"], "2026-08-02")
            self.assertEqual(item["source_code"], "src_pl_spring_commercial_context_20260802")
        expression = by_configuration["spring_expression_electric70_automatic"]
        self.assertEqual(expression["availability_status"], "optional")
        self.assertEqual(expression["amount"], "1500")
        self.assertEqual(expression["currency_code"], "PLN")
        self.assertEqual(expression["price_date"], "2026-07-08")
        self.assertEqual(expression["source_code"], "src_pl_spring_price_my25_stock_20260708")'''
    replace(
        "tests/test_spring_charging_cable_commercial_semantics_migration_20260802.py",
        old,
        new,
    )


if __name__ == "__main__":
    main()
