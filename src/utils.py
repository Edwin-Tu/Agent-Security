"""Utility helpers for SecretGuard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(path: str | Path) -> dict[str, Any]:
    """Load a JSON configuration file and return its content."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {file_path}, got {type(payload).__name__}")

    return payload
