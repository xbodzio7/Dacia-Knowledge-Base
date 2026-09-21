from __future__ import annotations

import csv
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master"


def rows(name: str) -> list[dict[str, str]]:
    with (MASTER / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DocumentarySource20260703MasterCountsTests(unittest.TestCase):
    def test_availability_rows_match_documentary_source_checkpoints(self) -> None:
        source = Counter(
            row["source_code"]
            for row in rows("configuration_attribute_availability.csv")
            if row["source_code"]
            in {
                "src_pl_duster_price_my26_20260703",
                "src_pl_jogger_price_my26_20260703",
                "src_pl_bigster_price_my26_20260703",
            }
        )
        self.assertEqual(
            source,
            Counter(
                {
                    "src_pl_duster_price_my26_20260703": 84,
                    "src_pl_jogger_price_my26_20260703": 90,
                    "src_pl_bigster_price_my26_20260703": 1316,
                }
            ),
        )

    def test_commercial_configuration_rows_match_documentary_audits(self) -> None:
        source = Counter(
            row["source_code"]
            for row in rows("commercial_item_configurations.csv")
            if row["source_code"]
            in {
                "src_pl_duster_price_my26_20260703",
                "src_pl_jogger_price_my26_20260703",
                "src_pl_bigster_price_my26_20260703",
            }
        )
        self.assertEqual(
            source,
            Counter(
                {
                    "src_pl_duster_price_my26_20260703": 29,
                    "src_pl_jogger_price_my26_20260703": 42,
                    "src_pl_bigster_price_my26_20260703": 48,
                }
            ),
        )

    def test_commercial_item_counts_match_documentary_audits(self) -> None:
        source = Counter(
            row["source_code"]
            for row in rows("commercial_items.csv")
            if row["source_code"]
            in {
                "src_pl_jogger_price_my26_20260703",
                "src_pl_bigster_price_my26_20260703",
            }
        )
        self.assertEqual(
            source,
            Counter(
                {
                    "src_pl_jogger_price_my26_20260703": 6,
                    "src_pl_bigster_price_my26_20260703": 7,
                }
            ),
        )


if __name__ == "__main__":
    unittest.main()
