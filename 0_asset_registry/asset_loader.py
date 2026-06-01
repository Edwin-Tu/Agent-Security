import json
from pathlib import Path
from typing import Optional


class AssetLoader:
    @staticmethod
    def load_from_json(path: Path) -> list[dict]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assets = data.get("assets") if isinstance(data, dict) else data
        if not isinstance(assets, list):
            return []
        return [a for a in assets if isinstance(a, dict)]

    @staticmethod
    def load_from_directory(directory: Path) -> list[dict]:
        if not directory.exists() or not directory.is_dir():
            return []
        all_assets = []
        for json_file in directory.glob("*.json"):
            assets = AssetLoader.load_from_json(json_file)
            all_assets.extend(assets)
        return all_assets
