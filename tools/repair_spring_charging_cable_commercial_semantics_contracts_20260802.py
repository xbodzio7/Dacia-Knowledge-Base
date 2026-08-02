from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"replacement anchor not found in {path}: {old[:80]!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    replace(
        "tools/import_spring_commercial_packages.py",
        'def generated_attributes() -> list[dict[str, str]]:\n    verify_source_contract()\n    return [dict(row) for row in load_attributes_spec()]',
        '''def generated_attributes() -> list[dict[str, str]]:
    verify_source_contract()
    generated = [dict(row) for row in load_attributes_spec()]
    for row in generated:
        if row["commercial_item_code"] == "spring_type2_charging_cable_option":
            row["code"] = "spring_type2_charging_cable_option__type2_charging_cable_supplied"
            row["attribute_code"] = "type2_charging_cable_supplied"
            row["notes"] = "Corrected membership: the brochure item describes a physical Type 2 cable, not the vehicle charging connector."
    return generated''',
    )

    replace(
        "tools/review_spring_charging_cable_commercial_semantics_20260802.py",
        '''    if membership["attribute_code"] != "charging_connector_type":
        raise AssertionError("review package unexpectedly materialized membership correction")''',
        '''    migration_complete = state["current_package"]["package_id"] == "spring_charging_cable_commercial_semantics_migration_001"
    expected_membership = "type2_charging_cable_supplied" if migration_complete else "charging_connector_type"
    if membership["attribute_code"] != expected_membership:
        raise AssertionError("historical Type 2 membership is outside the accepted transition")''',
    )
    replace(
        "tools/review_spring_charging_cable_commercial_semantics_20260802.py",
        '''    if DOMESTIC_ITEM in items:
        raise AssertionError("review package unexpectedly materialized domestic-cable item")
    if any(row["commercial_item_code"] == DOMESTIC_ITEM for row in memberships):
        raise AssertionError("review package unexpectedly materialized domestic membership")
    if any(row["commercial_item_code"] == DOMESTIC_ITEM for row in mappings):
        raise AssertionError("review package unexpectedly materialized domestic mappings")''',
        '''    domestic_memberships = [row for row in memberships if row["commercial_item_code"] == DOMESTIC_ITEM]
    domestic_mappings = [row for row in mappings if row["commercial_item_code"] == DOMESTIC_ITEM]
    if migration_complete:
        if DOMESTIC_ITEM not in items or len(domestic_memberships) != 1 or len(domestic_mappings) != 2:
            raise AssertionError("materialized domestic-cable representation is incomplete")
        if domestic_memberships[0]["attribute_code"] != "domestic_socket_charging_cable":
            raise AssertionError("materialized domestic membership drifted")
        if {row["configuration_code"] for row in domestic_mappings} != {
            "spring_essential_electric70_automatic",
            "spring_extreme_electric100_automatic",
        }:
            raise AssertionError("materialized domestic mapping scope drifted")
    elif DOMESTIC_ITEM in items or domestic_memberships or domestic_mappings:
        raise AssertionError("review package unexpectedly materialized domestic representation")''',
    )

    replace(
        "tools/review_spring_exact_current_semantic_migration_20260802.py",
        'HOME_CABLE_ITEM = "spring_home_charging_cable_option"',
        'HOME_CABLE_ITEM = "spring_domestic_socket_charging_cable_option"',
    )
    replace(
        "tools/review_spring_exact_current_semantic_migration_20260802.py",
        '''    if len(selected) != 25:
        raise RuntimeError(f"expected 25 Spring commercial mappings, found {len(selected)}")''',
        '''    if len(selected) not in {25, 27}:
        raise RuntimeError(f"expected 25 pre-migration or 27 post-migration Spring commercial mappings, found {len(selected)}")
    migration_complete = HOME_CABLE_ITEM in item_index if 'item_index' in locals() else False''',
    )
    # Move migration flag after item_index creation.
    replace(
        "tools/review_spring_exact_current_semantic_migration_20260802.py",
        '''    item_index = {row["code"]: row for row in items}
    membership_index = {''',
        '''    item_index = {row["code"]: row for row in items}
    migration_complete = HOME_CABLE_ITEM in item_index
    membership_index = {''',
    )
    replace(
        "tools/review_spring_exact_current_semantic_migration_20260802.py",
        "    migration_complete = HOME_CABLE_ITEM in item_index if 'item_index' in locals() else False\n",
        "",
    )
    replace(
        "tools/review_spring_exact_current_semantic_migration_20260802.py",
        '''    if membership_index[TYPE2_ITEM]["attribute_code"] != "charging_connector_type":
        raise RuntimeError("Type 2 membership boundary drifted")
    if HOME_CABLE_ITEM in item_index:
        raise RuntimeError("home charging cable unexpectedly already exists")''',
        '''    expected_type2_attribute = "type2_charging_cable_supplied" if migration_complete else "charging_connector_type"
    if membership_index[TYPE2_ITEM]["attribute_code"] != expected_type2_attribute:
        raise RuntimeError("Type 2 membership transition drifted")
    home_rows = [row for row in selected.values() if row["commercial_item_code"] == HOME_CABLE_ITEM]
    if migration_complete:
        if len(home_rows) != 2 or any(row["amount"] != "1500" for row in home_rows):
            raise RuntimeError("domestic charging-cable mappings drifted")
    elif home_rows:
        raise RuntimeError("home charging cable mappings unexpectedly exist")''',
    )

    replace(
        "tests/test_spring_standard_equipment_representation_review_20260802.py",
        '''    if len(memberships) != 1 or memberships[0]["attribute_code"] != "charging_connector_type":
        raise AssertionError("historical blocked Type 2 membership drifted")
    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM in item_codes:
        raise AssertionError("commercial home-cable review has advanced unexpectedly")''',
        '''    item_codes = {row["code"] for row in read_rows(ITEMS)}
    migration_complete = "spring_domestic_socket_charging_cable_option" in item_codes
    expected_attribute = "type2_charging_cable_supplied" if migration_complete else "charging_connector_type"
    if len(memberships) != 1 or memberships[0]["attribute_code"] != expected_attribute:
        raise AssertionError("historical Type 2 membership transition drifted")''',
    )

    replace("tests/test_commercial_items_20260703.py", "self.assertEqual(len(self.items), 39)", "self.assertEqual(len(self.items), 40)")
    replace("tests/test_commercial_items_20260703.py", "self.assertEqual(len(self.members), 93)", "self.assertEqual(len(self.members), 94)")
    replace("tests/test_commercial_items_20260703.py", "self.assertEqual(len(self.mappings), 186)", "self.assertEqual(len(self.mappings), 188)")
    replace(
        "tests/test_commercial_items_20260703.py",
        '                "src_pl_spring_brochure_20260219",\n',
        '                "src_pl_spring_brochure_20260219",\n                "src_pl_spring_commercial_context_20260802",\n',
    )
    replace("tests/test_reviewed_gap_state_materialization_20260802.py", "self.assertEqual(len(rows(MAPPINGS)), 186)", "self.assertEqual(len(rows(MAPPINGS)), 188)")
    replace("tests/test_reviewed_gap_state_materialization_20260802.py", "self.assertEqual(len(rows(path)), 186)", "self.assertEqual(len(rows(path)), 188)")


if __name__ == "__main__":
    main()
