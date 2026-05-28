import re
from typing import Optional


class SecretMatcher:
    def __init__(self, assets: Optional[list[dict]] = None):
        self.assets: list[dict] = assets or []

    def set_assets(self, assets: list[dict]):
        self.assets = assets

    def match(self, text: str) -> dict:
        if not text or not self.assets:
            return {"matched": False, "matches": []}

        text_lower = text.lower().strip()
        matches = []

        for asset in self.assets:
            if not asset.get("enabled", True):
                continue
            modes = asset.get("protection_modes", ["exact_match"])
            value = asset.get("value", "")
            aliases = asset.get("aliases", [])

            matched_fragments = []

            for mode in modes:
                fragment = self._try_mode(mode, text, text_lower, value, aliases)
                if fragment:
                    matched_fragments.append(fragment)

            if matched_fragments:
                matches.append({
                    "asset_id": asset["asset_id"],
                    "name": asset.get("name", ""),
                    "risk_level": asset.get("risk_level", "medium"),
                    "matched_fragments": matched_fragments,
                    "allowed_roles": asset.get("allowed_roles", []),
                })

        return {
            "matched": len(matches) > 0,
            "matches": matches,
        }

    def match_pattern(self, text: str) -> list[dict]:
        if not text:
            return []

        patterns = {
            "api_key_sk": r"sk-[A-Za-z0-9]{32,}",
            "private_key": r"-----BEGIN\s+(RSA\s+|EC\s+)?PRIVATE\s+KEY-----",
            "aws_key": r"AKIA[0-9A-Z]{16}",
            "github_token": r"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}",
            "jwt_token": r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        }

        matches = []
        for name, pattern in patterns.items():
            found = re.search(pattern, text)
            if found:
                matches.append({"type": name, "match": found.group()})
        return matches

    def _try_mode(self, mode: str, text: str, text_lower: str,
                  value: str, aliases: list[str]) -> Optional[str]:
        if mode == "exact_match":
            return self.exact_match(text, value)

        if mode == "case_insensitive_match":
            return self.case_insensitive_match(text_lower, value)

        if mode == "alias_match":
            return self.alias_match(text_lower, aliases)

        if mode == "partial_match":
            return self.partial_match(text, value)

        if mode == "encoding_match":
            return self.encoding_match(text, value)

        return None

    @staticmethod
    def exact_match(text: str, value: str) -> Optional[str]:
        if value in text:
            return f"exact:'{value}'"
        return None

    @staticmethod
    def case_insensitive_match(text_lower: str, value: str) -> Optional[str]:
        if value.lower() in text_lower:
            return f"ci:'{value}'"
        return None

    @staticmethod
    def alias_match(text_lower: str, aliases: list[str]) -> Optional[str]:
        for alias in aliases:
            if alias.lower() in text_lower:
                return f"alias:'{alias}'"
        return None

    @staticmethod
    def partial_match(text: str, value: str) -> Optional[str]:
        if len(value) < 3:
            return None
        min_len = max(3, len(value) // 3)
        for i in range(len(value) - min_len + 1):
            segment = value[i:i + min_len]
            if segment.lower() in text.lower():
                return f"partial:'{segment}'"
        return None

    @staticmethod
    def encoding_match(text: str, value: str) -> Optional[str]:
        import base64
        try:
            decoded = base64.b64decode(text.strip()).decode("utf-8", errors="ignore")
            if value.lower() in decoded.lower():
                return f"encoding:base64"
        except Exception:
            pass
        try:
            decoded = bytes.fromhex(text.strip()).decode("utf-8", errors="ignore")
            if value.lower() in decoded.lower():
                return f"encoding:hex"
        except Exception:
            pass
        return None

    @staticmethod
    def match_ctf_flag(text: str) -> Optional[dict]:
        pattern = r"picoCTF\{[^}]+\}"
        match = re.search(pattern, text)
        if match:
            return {
                "matched": True,
                "value": match.group(),
                "type": "ctf_flag",
                "risk_level": "high",
            }
        return None
