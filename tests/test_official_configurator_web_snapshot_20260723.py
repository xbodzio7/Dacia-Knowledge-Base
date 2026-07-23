from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
SOURCE_CODE = "src_pl_dacia_official_configurators_20260723"
SNAPSHOT = REPOSITORY / "project/sources/dacia-pl-configurators-20260723.json"


class OfficialConfiguratorWebSnapshot20260723Tests(unittest.TestCase):
    def rows(self, name: str) -> list[dict[str, str]]:
        with (REPOSITORY / "data/master" / name).open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_snapshot_is_registered_and_hash_verified(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        source = next(row for row in self.rows("sources.csv") if row["code"] == SOURCE_CODE)
        self.assertEqual(source["source_type"], "web_snapshot")
        self.assertEqual(source["publisher"], "Dacia")
        self.assertEqual(source["market"], "PL")
        self.assertEqual(source["document_date"], "2026-07-23")
        self.assertEqual(source["file_path"], SNAPSHOT.relative_to(REPOSITORY).as_posix())
        self.assertEqual(hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(), source["sha256"])
        self.assertEqual(payload["volatility"], "dynamic_web_configurator")
        self.assertEqual(payload["catalog_url"], "https://www.dacia.pl/konfiguruj.html")

    def test_all_active_catalogue_models_have_official_configurator_observation(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        observed = {item["model_code"] for item in payload["observations"]}
        self.assertEqual(observed, {"sandero_iii", "sandero_stepway_iii", "duster_iii", "jogger", "bigster"})
        related = {row["model_code"] for row in self.rows("source_models.csv") if row["source_code"] == SOURCE_CODE}
        self.assertEqual(related, observed)
        for item in payload["observations"]:
            self.assertTrue(item["url"].startswith("https://www.dacia.pl/"))

    def test_snapshot_preserves_dynamic_source_boundaries(self) -> None:
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        boundaries = " ".join(payload["intake_boundaries"])
        self.assertIn("observation date", boundaries)
        self.assertIn("does not prove applicability", boundaries)
        self.assertIn("does not overwrite", boundaries)
        stepway = next(item for item in payload["observations"] if item["model_code"] == "sandero_stepway_iii")
        self.assertEqual(stepway["visible_optional_items"], [{"name": "pakiet MEDIA DISPLAY", "price_pln": 1900}])


if __name__ == "__main__":
    unittest.main()
