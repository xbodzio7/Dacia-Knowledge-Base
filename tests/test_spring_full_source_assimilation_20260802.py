from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "project" / "source-audit"


class SpringFullSourceAssimilationContract(unittest.TestCase):
    def test_brochure_inventory_covers_all_22_pages(self):
        text = (AUDIT / "spring-brochure-20260219-page-inventory.md").read_text(encoding="utf-8")
        self.assertIn("Pages: 22", text)
        for page in range(1, 23):
            self.assertIn(f"| {page} |", text)

    def test_price_list_inventory_covers_all_6_pages(self):
        text = (AUDIT / "spring-price-my25-stock-20260708-page-inventory.md").read_text(encoding="utf-8")
        self.assertIn("Pages: 6", text)
        for page in range(1, 7):
            self.assertIn(f"| {page} |", text)

    def test_exact_hashes_and_completion_status_are_preserved(self):
        text = (AUDIT / "spring-full-assimilation-intake-20260802.md").read_text(encoding="utf-8")
        self.assertIn("`fully_reviewed`", text)
        self.assertIn("73a4c568ce273bc095f6ecf1cfa4f5f2a92324bb2f0bbc171ba45bb4a4cf3c8d", text)
        self.assertIn("809d24ec3710aac02b3f3a2f33e1872689430a1d6887f387936a5ac3ff343ae0", text)

    def test_charging_cable_conflict_cannot_be_silently_flattened(self):
        conflict = (AUDIT / "spring-source-conflicts-20260802.md").read_text(encoding="utf-8")
        ledger = (AUDIT / "spring-evidence-ledger-20260802.md").read_text(encoding="utf-8")
        self.assertIn("temporal/model-year commercial conflict", conflict)
        self.assertIn("internal source contradiction", conflict)
        self.assertIn("domestic standard, Type 2 optional", ledger)
        self.assertIn("domestic optional 1500, Type 2 standard", ledger)


if __name__ == "__main__":
    unittest.main()
