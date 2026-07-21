from __future__ import annotations

import csv
import hashlib
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


class OfficialMy26Sources20260703Tests(unittest.TestCase):
    def test_registered_sources_files_and_relationships(self) -> None:
        expected = {
            "src_pl_sandero_stepway_price_my26_20260703": {
                "file": "PDF/Cenniki/DACIA SANDERO I SANDERO STEPWAY cennik MY26 20260703.pdf",
                "sha256": "5af2dbaf268480ec1e7e6d6e35fd2037b6fba3fb79972026e4f68c08055ba783",
                "models": {"sandero_iii", "sandero_stepway_iii"},
                "versions": {"sandero_iii_expression", "sandero_iii_journey", "sandero_stepway_iii_essential", "sandero_stepway_iii_expression", "sandero_stepway_iii_extreme"},
                "configuration_count": 7,
            },
            "src_pl_duster_price_my26_20260703": {
                "file": "PDF/Cenniki/DACIA DUSTER cennik MY26 20260703.pdf",
                "sha256": "40bb4f3db9019c500fcb4c759f5ad395aa3b35a68bb22aa74f031fefe09727f2",
                "models": {"duster_iii"},
                "versions": {"duster_iii_essential", "duster_iii_expression", "duster_iii_extreme", "duster_iii_journey"},
                "configuration_count": 10,
            },
            "src_pl_jogger_price_my26_20260703": {
                "file": "PDF/Cenniki/DACIA JOGGER cennik MY26 20260703.pdf",
                "sha256": "92606411c4d8c10dd830b0d1c387fe663c4c9618422c5db639c13a23138f4a87",
                "models": {"jogger"},
                "versions": {"jogger_essential", "jogger_expression", "jogger_extreme", "jogger_journey"},
                "configuration_count": 22,
            },
            "src_pl_bigster_price_my26_20260703": {
                "file": "PDF/Cenniki/DACIA BIGSTER cennik MY26 20260703.pdf",
                "sha256": "9528654fb3daf3767a2defbbc80e8a85abceecb11e04bb176aa0b76443be178a",
                "models": {"bigster"},
                "versions": {"bigster_essential", "bigster_expression", "bigster_extreme", "bigster_journey"},
                "configuration_count": 14,
            },
        }

        def rows(name: str) -> list[dict[str, str]]:
            with (REPOSITORY / "data" / "master" / name).open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))

        sources = {row["code"]: row for row in rows("sources.csv")}
        model_rows = rows("source_models.csv")
        version_rows = rows("source_versions.csv")
        configuration_rows = rows("source_configurations.csv")

        for code, contract in expected.items():
            with self.subTest(source=code):
                record = sources[code]
                self.assertEqual(record["document_date"], "2026-07-03")
                self.assertEqual(record["file_path"], contract["file"])
                self.assertEqual(record["sha256"], contract["sha256"])
                self.assertTrue(record["external_reference"].startswith("https://cdn.group.renault.com/"))
                path = REPOSITORY / contract["file"]
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), contract["sha256"])
                self.assertEqual({row["model_code"] for row in model_rows if row["source_code"] == code}, contract["models"])
                self.assertEqual({row["version_code"] for row in version_rows if row["source_code"] == code}, contract["versions"])
                self.assertEqual(len([row for row in configuration_rows if row["source_code"] == code]), contract["configuration_count"])


if __name__ == "__main__":
    unittest.main()
