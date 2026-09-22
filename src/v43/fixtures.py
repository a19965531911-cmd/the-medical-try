"""Read-only fixture loading helpers."""

import json
from pathlib import Path
from typing import Any


def load_fixture(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON list fixture and reject malformed top-level values."""
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError("fixture must contain a JSON list of objects")
    return payload
