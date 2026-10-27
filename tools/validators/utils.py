from pathlib import Path


def repository_root() -> Path:
    """Return repository root directory."""
    return Path(__file__).resolve().parents[2]