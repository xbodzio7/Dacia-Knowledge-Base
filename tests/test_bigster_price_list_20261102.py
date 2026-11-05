import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CODE = "src_pl_bigster_price_my26_20261102"
EXPECTED = {
    "bigster_essential_mildhybridg140_4x2_manual": 101400,
    "bigster_expression_mildhybridg140_4x2_manual": 110400,
    "bigster_extreme_mildhybridg140_4x2_manual": 118900,
    "bigster_journey_mildhybridg140_4x2_manual": 118500,
    "bigster_expression_mildhybridg140_4x2_automatic": 115600,
    "bigster_extreme_mildhybridg140_4x2_automatic": 124100,
    "bigster_journey_mildhybridg140_4x2_automatic": 123700,
    "bigster_expression_hybrid155_4x2_automatic": 124900,
    "bigster_extreme_hybrid155_4x2_automatic": 133400,
    "bigster_journey_hybrid155_4x2_automatic": 133000,
    "bigster_expression_tribrid150_4x4_automatic": 128900,
    "bigster_extreme_tribrid150_4x4_automatic": 137600,
    "bigster_journey_tribrid150_4x4_automatic": 137200,
}


def _rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class BigsterNovember2026PriceListTests(unittest.TestCase):
    def test_price_source_is_registered_once(self):
        rows = [r for r in _rows(ROOT / "data/master/sources.csv") if r["code"] == SOURCE_CODE]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["document_date"], "2026-11-02")
        self.assertEqual(rows[0]["market"], "PL")
        self.assertEqual(rows[0]["status"], "active")
        self.assertTrue(rows[0]["external_reference"].endswith("/2fe688def9.pdf"))

    def test_source_links_cover_exact_price_matrix(self):
        rows = [r for r in _rows(ROOT / "data/master/source_configurations.csv") if r["source_code"] == SOURCE_CODE]
        # This is a price-only source. Price rows carry the exact source and
        # configuration keys; do not add equipment/technical provenance links.
        self.assertEqual(rows, [])

    def test_catalogue_prices_are_exact_and_unique(self):
        rows = [r for r in _rows(ROOT / "data/master/configuration_prices.csv") if r["source_code"] == SOURCE_CODE]
        self.assertEqual(len(rows), len(EXPECTED))
        self.assertEqual(len({r["code"] for r in rows}), len(EXPECTED))
        self.assertEqual({r["configuration_code"]: int(r["amount"]) for r in rows}, EXPECTED)
        self.assertTrue(all(r["market"] == "PL" for r in rows))
        self.assertTrue(all(r["price_type"] == "catalog_gross" for r in rows))
        self.assertTrue(all(r["currency_code"] == "PLN" for r in rows))
        self.assertTrue(all(r["price_date"] == "2026-11-02" for r in rows))


if __name__ == "__main__":
    unittest.main()
