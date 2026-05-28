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

    @staticmethod
    def validate_asset(asset: dict) -> tuple[bool, Optional[str]]:
        if "asset_id" not in asset:
            return False, "Missing asset_id"
        if "value" not in asset:
            return False, "Missing value"
        if not isinstance(asset.get("aliases", []), list):
            return False, "aliases must be a list"
        if asset.get("risk_level") not in (None, "low", "medium", "high"):
            return False, "risk_level must be low/medium/high"
        return True, None
