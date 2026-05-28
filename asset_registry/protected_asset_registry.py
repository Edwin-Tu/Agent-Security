import json
from pathlib import Path
from typing import Optional

from asset_registry.secret_matcher import SecretMatcher

DEFAULT_POLICY_PATH = Path(__file__).resolve().parent.parent / "policies" / "default_secret_policy.json"
USER_POLICY_PATH = Path(__file__).resolve().parent.parent / "policies" / "user_secret_policy.json"
REGISTRY_PATH = Path(__file__).resolve().parent.parent / "policies" / "protected_assets.json"


class ProtectedAssetRegistry:
    def __init__(self):
        self.assets: list[dict] = []
        self.load_registry()
        if not self.assets:
            self.refresh()

    def load_default_assets(self) -> list[dict]:
        return self._load_from(DEFAULT_POLICY_PATH, source="system")

    def load_user_assets(self) -> list[dict]:
        return self._load_from(USER_POLICY_PATH, source="user")

    @staticmethod
    def _load_from(path: Path, source: str) -> list[dict]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assets = data.get("assets") if isinstance(data, dict) else data
        if not isinstance(assets, list):
            return []
        for asset in assets:
            if isinstance(asset, dict):
                asset.setdefault("source", source)
        return assets

    def merge_assets(self) -> list[dict]:
        defaults = self.load_default_assets()
        users = self.load_user_assets()
        seen_ids = {a["asset_id"] for a in defaults if "asset_id" in a}
        merged = list(defaults)
        for u in users:
            if u.get("asset_id") and u["asset_id"] not in seen_ids:
                merged.append(u)
                seen_ids.add(u["asset_id"])
        self.assets = merged
        return self.assets

    def save_registry(self, path: Optional[Path] = None) -> str:
        path = path or REGISTRY_PATH
        payload = {
            "version": "1.0",
            "asset_count": len(self.assets),
            "assets": self.assets,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return str(path)

    def load_registry(self, path: Optional[Path] = None) -> list[dict]:
        path = path or REGISTRY_PATH
        if not path.exists():
            self.assets = []
            return self.assets
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.assets = []
            return self.assets

        if isinstance(data, dict):
            assets = data.get("assets", [])
        elif isinstance(data, list):
            assets = data
        else:
            assets = []

        if not isinstance(assets, list):
            assets = []

        self.assets = [asset for asset in assets if isinstance(asset, dict)]
        return self.assets

    def list_assets(self) -> list[dict]:
        return list(self.assets)

    def get_all(self) -> list[dict]:
        return self.list_assets()

    def get_asset(self, asset_id: str) -> Optional[dict]:
        for a in self.assets:
            if a.get("asset_id") == asset_id:
                return dict(a)
        return None

    def match(self, text: str) -> dict:
        if not self.assets:
            self.load_registry()
        matcher = SecretMatcher(self.assets)
        return matcher.match(text)

    def add_asset(self, asset: dict) -> bool:
        if any(a.get("asset_id") == asset.get("asset_id") for a in self.assets):
            return False
        if "asset_id" not in asset or "value" not in asset:
            return False
        entry = {
            "asset_id": asset["asset_id"],
            "name": asset.get("name", ""),
            "type": asset.get("type", "exact"),
            "value": asset["value"],
            "aliases": asset.get("aliases", []),
            "risk_level": asset.get("risk_level", "medium"),
            "allowed_roles": asset.get("allowed_roles", ["owner"]),
            "protection_modes": asset.get("protection_modes", ["exact_match"]),
            "enabled": asset.get("enabled", True),
            "description": asset.get("description", ""),
            "source": asset.get("source", "user"),
        }
        self.assets.append(entry)
        return True

    def remove_asset(self, asset_id: str) -> bool:
        for i, a in enumerate(self.assets):
            if a.get("asset_id") == asset_id:
                self.assets.pop(i)
                return True
        return False

    def update_asset(self, asset_id: str, updates: dict) -> bool:
        for a in self.assets:
            if a.get("asset_id") == asset_id:
                for key in (
                    "name",
                    "type",
                    "value",
                    "aliases",
                    "risk_level",
                    "allowed_roles",
                    "protection_modes",
                    "enabled",
                    "description",
                    "source",
                ):
                    if key in updates:
                        a[key] = updates[key]
                return True
        return False

    def find_by_keyword(self, keyword: str) -> list[dict]:
        keyword_lower = keyword.lower().strip()
        results = []
        for a in self.assets:
            if not a.get("enabled", True):
                continue
            if keyword_lower in a.get("value", "").lower():
                results.append(a)
                continue
            if keyword_lower in a.get("name", "").lower():
                results.append(a)
                continue
            for alias in a.get("aliases", []):
                if keyword_lower in str(alias).lower():
                    results.append(a)
                    break
        return results

    def refresh(self) -> list[dict]:
        self.merge_assets()
        self.save_registry()
        return self.assets
