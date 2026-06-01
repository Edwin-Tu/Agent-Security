import json
from pathlib import Path


class PolicyBuilder:
    def __init__(self, default_path: str = None, role_path: str = None):
        self.default_path = default_path or str(
            Path(__file__).resolve().parent.parent / "policies" / "default_secret_policy.json"
        )
        self.role_path = role_path or str(
            Path(__file__).resolve().parent.parent / "policies" / "role_policy.json"
        )
        self.defaults = self._load_json(self.default_path)
        self.roles = self._load_json(self.role_path)

    def _load_json(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def build(self, assets: list[dict], decision: dict, role: str = "default") -> dict:
        role_config = self.roles.get("roles", {}).get(role, {})
        policy = {
            "action": decision.get("action", "allow"),
            "risk_threshold": decision.get("threshold", "medium"),
            "role": role,
            "restricted_assets": [a.get("name", "unknown") for a in assets],
            "allowed_roles": role_config.get("allowed_roles", []),
            "required_permissions": role_config.get("permissions", []),
            "enable_monitoring": decision.get("action") in ("warn", "restrict", "block", "escalate"),
            "enable_leakage_check": decision.get("action") != "allow",
        }
        return policy

    def reload(self):
        self.defaults = self._load_json(self.default_path)
        self.roles = self._load_json(self.role_path)
