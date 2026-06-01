from __future__ import annotations

import json
from pathlib import Path


def load_policy_file(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
