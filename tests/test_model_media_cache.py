from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

import cache_model_media as media  # noqa: E402


class ModelMediaCacheTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        source = root / media.SOURCE_PATH
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            json.dumps(
                {
                    "captured_on": "2026-07-24",
                    "models": {
                        "sandero_iii": {
                            "model_name": "Sandero",
                            "source_page_url": "https://www.dacia.pl/samochody/sandero.html",
                            "image_url": "https://www.dacia.pl/media/sandero.png",
                            "source_name": "Dacia Polska",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        return root

    def test_offline_first_run_creates_deterministic_local_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.fixture(Path(directory))
            first = media.refresh(repository, offline=True)
            manifest_before = json.loads(
                (repository / media.MANIFEST_PATH).read_text(encoding="utf-8")
            )
            second = media.refresh(repository, offline=True)
            manifest_after = json.loads(
                (repository / media.MANIFEST_PATH).read_text(encoding="utf-8")
            )
            verified = media.verify(repository)
            embedded = media.data_uri(repository, "sandero_iii")
        self.assertEqual(first["statuses"]["sandero_iii"], "placeholder_offline")
        self.assertEqual(second["statuses"]["sandero_iii"], "cached_offline")
        self.assertEqual(
            manifest_before["models"]["sandero_iii"]["sha256"],
            manifest_after["models"]["sandero_iii"]["sha256"],
        )
        self.assertTrue(verified["verified"])
        self.assertTrue(embedded.startswith("data:image/svg+xml;base64,"))


if __name__ == "__main__":
    unittest.main()
