from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tests/test_spring_exact_current_semantic_migration_review_20260802.py"


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor not found in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    replace(
        PATH,
        'HOME_CABLE_ITEM = "spring_home_charging_cable_option"',
        'HOME_CABLE_ITEM = "spring_domestic_socket_charging_cable_option"',
    )
    replace(
        PATH,
        '        "existing_spring_mapping_count": 25,',
        '        "existing_spring_mapping_count": 27,',
    )
    replace(
        PATH,
        '''    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM in item_codes:
        raise AssertionError("later packages must not bypass the home-cable model review")''',
        '''    item_codes = {row["code"] for row in read_rows(ITEMS)}
    if HOME_CABLE_ITEM not in item_codes:
        raise AssertionError("accepted home-cable representation was not materialized")''',
    )
    commercial = ROOT / "tests/test_commercial_items_20260703.py"
    replace(
        commercial,
        'self.assertEqual({row["observation_date"] for row in self.items}, {SPRING_DATE, DATE})',
        'self.assertEqual({row["observation_date"] for row in self.items}, {SPRING_DATE, DATE, SPRING_CURRENT_CONTEXT_DATE})',
    )


if __name__ == "__main__":
    main()
