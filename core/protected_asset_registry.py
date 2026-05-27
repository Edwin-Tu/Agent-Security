import json
from pathlib import Path


class ProtectedAssetRegistry:
    def __init__(self, assets_path: str = None, default_path: str = None, user_path: str = None):
        self.assets_path = assets_path or str(Path(__file__).parent.parent / "policies" / "protected_assets.json")
        self.default_path = default_path or str(Path(__file__).parent.parent / "policies" / "default_secret_policy.json")
        self.user_path = user_path or str(Path(__file__).parent.parent / "policies" / "user_secret_policy.json")
        self.assets: list[dict] = []
        self._load_all()

    def _load_all(self):
        self.assets = []
        for path in [self.default_path, self.user_path, self.assets_path]:
            p = Path(path)
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.assets.extend(data)
                elif isinstance(data, dict):
                    self.assets.append(data)

    def register(self, asset: dict):
        self.assets.append(asset)
        self._save_user()

    def _save_user(self):
        user_assets = [a for a in self.assets if a.get("source") == "user"]
        path = Path(self.user_path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(user_assets, f, ensure_ascii=False, indent=2)

    def match(self, text: str) -> list[dict]:
        text_lower = text.lower()
        matches = []
        for asset in self.assets:
            value = asset.get("value", "").lower()
            aliases = [a.lower() for a in asset.get("aliases", [])]
            if value and value in text_lower:
                matches.append({**asset, "matched_by": "exact"})
            for alias in aliases:
                if alias in text_lower:
                    matches.append({**asset, "matched_by": "alias"})
                    break
        return matches

    def get_all(self) -> list[dict]:
        return list(self.assets)

    def get_by_type(self, asset_type: str) -> list[dict]:
        return [a for a in self.assets if a.get("type") == asset_type]

    def get_by_risk(self, level: str) -> list[dict]:
        return [a for a in self.assets if a.get("risk_level") == level]
