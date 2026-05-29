from __future__ import annotations

from typing import Optional

from core.restricted_token_guard import RestrictedTokenGuard as CoreRestrictedTokenGuard
from input_normalization.token_expander import TokenExpander


class RestrictedTokenGuard:
    def __init__(
        self,
        rule_path: str = "policies/token_rules.json",
        restricted_tokens: Optional[list[str]] = None,
        protected_assets: Optional[list[dict]] = None,
    ):
        self.rule_path = rule_path
        self.expander = TokenExpander(rule_path=rule_path)
        self.restricted_tokens: list[str] = restricted_tokens or []
        self.protected_assets: list[dict] = protected_assets or []

        if not self.protected_assets and self.restricted_tokens:
            self.protected_assets = self._assets_from_tokens(self.restricted_tokens)

        self.core_guard = CoreRestrictedTokenGuard(self.protected_assets)

    def _assets_from_tokens(self, tokens: list[str]) -> list[dict]:
        expanded = sorted(self.expander.expand(tokens))
        assets = []
        for idx, token in enumerate(expanded):
            assets.append(
                {
                    "asset_id": f"restricted_token_{idx}",
                    "name": token,
                    "type": "exact",
                    "value": token,
                    "aliases": [],
                    "risk_level": "high",
                    "protection_modes": ["exact_match", "case_insensitive_match"],
                    "enabled": True,
                }
            )
        return assets

    def check_text(self, text: str) -> dict:
        return self.core_guard.check_text(text)

    def detect(self, text: str) -> dict:
        result = self.core_guard.check_text(text)
        matched_tokens = [item.get("token", "") for item in result.get("matched_token", []) if item.get("token")]
        return {
            "blocked": result.get("matched", False),
            "matched_tokens": sorted(set(matched_tokens)),
            "reason": result.get("reason", ""),
            "severity": result.get("severity", "low"),
            "matched_token": result.get("matched_token", []),
        }

    def check(self, text: str) -> dict:
        return self.detect(text)

    def mask_text(self, text: str) -> str:
        return self.core_guard.mask_text(text)

    def update_restricted_tokens(self, tokens: list[str]):
        self.restricted_tokens = tokens or []
        self.protected_assets = self._assets_from_tokens(self.restricted_tokens)
        self.core_guard = CoreRestrictedTokenGuard(self.protected_assets)
