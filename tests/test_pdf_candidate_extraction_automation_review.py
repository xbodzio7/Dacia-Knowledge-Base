"""Discovery gate for the PDF candidate extraction automation review.

The repository keeps orchestration and review contracts outside the historical
counted-test baseline. ``load_tests`` executes the verifier and deliberately
returns an empty suite, so drift fails discovery without changing the 1070-test
baseline.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "tools"
sys.path.insert(0, str(TOOLS))

import review_pdf_candidate_extraction_automation_20260727 as review  # noqa: E402


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del loader, pattern
    review.verify()
    return tests


if __name__ == "__main__":
    review.verify()
