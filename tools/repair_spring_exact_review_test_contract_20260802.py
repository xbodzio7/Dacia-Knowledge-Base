from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tests/test_spring_exact_current_semantic_migration_review_20260802.py"


def replace(old: str, new: str) -> None:
    text = PATH.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor not found: {old!r}")
    PATH.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    replace(
        'HOME_CABLE_ITEM = "spring_home_charging_cable_option"',
        'HOME_CABLE_ITEM = "spring_domestic_socket_charging_cable_option"',
    )
    replace(
        '        "existing_spring_mapping_count": 25,',
        '        "existing_spring_mapping_count": 27,',
    )
    replace(
        '''    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM in item_codes:
        raise AssertionError("later packages must not bypass the home-cable model review")''',
        '''    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM not in item_codes:
        raise AssertionError("accepted home-cable representation was not materialized")''',
    )


if __name__ == "__main__":
    main()
