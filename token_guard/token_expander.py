from __future__ import annotations
import base64
import re
import unicodedata

from .token_policy import ProtectedAsset, RestrictedToken


class TokenExpander:
    def __init__(self):
        self._restricted_tokens: list[RestrictedToken] = []

    def expand(self, assets: list[ProtectedAsset]) -> list[RestrictedToken]:
        tokens: list[RestrictedToken] = []
        for asset in assets:
            if not asset.value:
                continue
            modes = asset.protection_modes
            if "exact_match" in modes:
                tokens += self._exact_tokens(asset)
            if "partial_match" in modes:
                tokens += self._partial_tokens(asset)
            if "alias_match" in modes:
                tokens += self._alias_tokens(asset)
            if "encoding_match" in modes:
                tokens += self._encoded_tokens(asset)
            if "normalization_match" in modes:
                tokens += self._normalized_tokens(asset)
        self._restricted_tokens = tokens
        return tokens

    def _exact_tokens(self, asset: ProtectedAsset) -> list[RestrictedToken]:
        return [
            RestrictedToken(asset_id=asset.asset_id, token=asset.value, token_type="exact", risk_level=asset.risk_level, source="asset_value")
        ]

    def _partial_tokens(self, asset: ProtectedAsset) -> list[RestrictedToken]:
        tokens: list[RestrictedToken] = []
        seen: set[str] = set()

        bracket_parts = re.split(r"[{}()\[\]]+", asset.value)
        for bp in bracket_parts:
            bp = bp.strip()
            if len(bp) >= 6 and bp not in seen:
                seen.add(bp)
                tokens.append(RestrictedToken(asset_id=asset.asset_id, token=bp, token_type="partial", risk_level=asset.risk_level, source="generated_variant"))

        parts = re.split(r"[{}\[\]()_\-.\s,;:!?]+", asset.value)
        for part in parts:
            part = part.strip()
            if len(part) >= 6 and part not in seen:
                seen.add(part)
                tokens.append(RestrictedToken(asset_id=asset.asset_id, token=part, token_type="partial", risk_level=asset.risk_level, source="generated_variant"))
        return tokens

    def _alias_tokens(self, asset: ProtectedAsset) -> list[RestrictedToken]:
        return [
            RestrictedToken(asset_id=asset.asset_id, token=alias, token_type="alias", risk_level=asset.risk_level, source="alias")
            for alias in asset.aliases
        ]

    def _encoded_tokens(self, asset: ProtectedAsset) -> list[RestrictedToken]:
        tokens: list[RestrictedToken] = []
        value_bytes = asset.value.encode("utf-8")

        b64 = base64.b64encode(value_bytes).decode("ascii")
        tokens.append(RestrictedToken(asset_id=asset.asset_id, token=b64, token_type="encoded", risk_level=asset.risk_level, source="generated_variant"))

        hex_enc = value_bytes.hex()
        tokens.append(RestrictedToken(asset_id=asset.asset_id, token=hex_enc, token_type="encoded", risk_level=asset.risk_level, source="generated_variant"))

        url_enc = self._url_encode(asset.value)
        if url_enc != asset.value:
            tokens.append(RestrictedToken(asset_id=asset.asset_id, token=url_enc, token_type="encoded", risk_level=asset.risk_level, source="generated_variant"))

        unicode_escape = "".join(f"\\u{ord(c):04x}" for c in asset.value)
        tokens.append(RestrictedToken(asset_id=asset.asset_id, token=unicode_escape, token_type="encoded", risk_level=asset.risk_level, source="generated_variant"))

        return tokens

    def _normalized_tokens(self, asset: ProtectedAsset) -> list[RestrictedToken]:
        tokens: list[RestrictedToken] = []

        nfkc = unicodedata.normalize("NFKC", asset.value)
        no_special = re.sub(r"[^a-zA-Z0-9]", "", nfkc).lower()
        tokens.append(RestrictedToken(asset_id=asset.asset_id, token=no_special, token_type="normalized", risk_level=asset.risk_level, source="generated_variant"))

        return tokens

    @staticmethod
    def _url_encode(text: str) -> str:
        result = []
        for c in text:
            if c.isalnum() or c in "._-~":
                result.append(c)
            else:
                result.append(f"%{ord(c):02X}")
        return "".join(result)

    @property
    def restricted_tokens(self) -> list[RestrictedToken]:
        return self._restricted_tokens
