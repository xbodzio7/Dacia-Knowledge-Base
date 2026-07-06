from pathlib import Path
import json


def write_statistics_json(output: Path, statistics: dict):
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as f:
        json.dump(
            statistics,
            f,
            indent=2,
            ensure_ascii=False,
        )
