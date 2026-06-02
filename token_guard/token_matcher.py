from __future__ import annotations
import re
import unicodedata
from typing import Callable

from .token_policy import RestrictedToken
from .token_guard_result import TokenMatch


class TokenMatcher:
    def __init__(self):
        self._matchers: dict[str, Callable[[str, RestrictedToken], list[TokenMatch]]] = {
            "exact": self._exact_match,
            "partial": self._partial_match,
            "alias": self._alias_match,
            "encoded": self._encoded_match,
            "normalized": self._normalized_match,
        }

    def match(self, text: str, tokens: list[RestrictedToken]) -> list[TokenMatch]:
        matches: list[TokenMatch] = []
        seen = set()
        for token in tokens:
            matcher = self._matchers.get(token.token_type)
            if matcher is None:
                continue
            for m in matcher(text, token):
                key = (m.asset_id, m.match_type, m.matched_text)
                if key not in seen:
                    seen.add(key)
                    matches.append(m)
        return matches

    def _exact_match(self, text: str, token: RestrictedToken) -> list[TokenMatch]:
        matches = []
        start = 0
        while True:
            idx = text.find(token.token, start)
            if idx == -1:
                break
            matches.append(TokenMatch(
                asset_id=token.asset_id,
                matched_text=token.token,
                match_type="exact",
                risk_level=token.risk_level,
                start=idx,
                end=idx + len(token.token),
                reason="exact secret match",
            ))
            start = idx + 1
        if not matches:
            lower_token = token.token.lower()
            lower_text = text.lower()
            idx = lower_text.find(lower_token)
            if idx != -1:
                matches.append(TokenMatch(
                    asset_id=token.asset_id,
                    matched_text=token.token,
                    match_type="exact",
                    risk_level=token.risk_level,
                    start=idx,
                    end=idx + len(token.token),
                    reason="case-insensitive exact match",
                ))
        return matches

    def _partial_match(self, text: str, token: RestrictedToken) -> list[TokenMatch]:
        matches = []
        lower_token = token.token.lower()
        lower_text = text.lower()
        idx = lower_text.find(lower_token)
        if idx != -1:
            matches.append(TokenMatch(
                asset_id=token.asset_id,
                matched_text=token.token,
                match_type="partial",
                risk_level=token.risk_level,
                start=idx,
                end=idx + len(token.token),
                reason=f"partial secret fragment (>=6 chars)",
            ))
        return matches

    def _alias_match(self, text: str, token: RestrictedToken) -> list[TokenMatch]:
        matches = []
        lower_token = token.token.lower()
        has_cjk = any("\u4e00" <= c <= "\u9fff" or "\u3000" <= c <= "\u303f" for c in token.token)
        lower_text = text.lower()
        idx = lower_text.find(lower_token)
        if idx != -1:
            if has_cjk:
                matches.append(TokenMatch(
                    asset_id=token.asset_id,
                    matched_text=token.token,
                    match_type="alias",
                    risk_level=token.risk_level,
                    start=idx,
                    end=idx + len(token.token),
                    reason="alias match",
                ))
            else:
                before = lower_text[idx - 1] if idx > 0 else " "
                after = lower_text[idx + len(lower_token)] if idx + len(lower_token) < len(lower_text) else " "
                boundary_before = not before.isalnum() and before != "_"
                boundary_after = not after.isalnum() and after != "_"
                if boundary_before and boundary_after:
                    matches.append(TokenMatch(
                        asset_id=token.asset_id,
                        matched_text=token.token,
                        match_type="alias",
                        risk_level=token.risk_level,
                        start=idx,
                        end=idx + len(token.token),
                        reason="alias match",
                    ))
        return matches

    def _encoded_match(self, text: str, token: RestrictedToken) -> list[TokenMatch]:
        matches = []
        idx = text.find(token.token)
        if idx != -1:
            matches.append(TokenMatch(
                asset_id=token.asset_id,
                matched_text=token.token,
                match_type="encoded",
                risk_level=token.risk_level,
                start=idx,
                end=idx + len(token.token),
                reason="encoded secret match",
            ))
        return matches

    def _normalized_match(self, text: str, token: RestrictedToken) -> list[TokenMatch]:
        matches = []

        nfkc_text = unicodedata.normalize("NFKC", text)

        stripped_text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", nfkc_text)

        compact = re.sub(r"[^a-zA-Z0-9]", "", stripped_text).lower()

        token_compact = token.token.lower()
        if token_compact in compact:
            idx = compact.find(token_compact)
            matches.append(TokenMatch(
                asset_id=token.asset_id,
                matched_text=token.token,
                match_type="normalized",
                risk_level=token.risk_level,
                start=idx,
                end=idx + len(token.token),
                reason="normalized variant match (NFKC + stripped)",
            ))
            return matches

        no_space = re.sub(r"\s+", "", stripped_text).lower()
        if token_compact in no_space:
            idx = no_space.find(token_compact)
            matches.append(TokenMatch(
                asset_id=token.asset_id,
                matched_text=token.token,
                match_type="normalized",
                risk_level=token.risk_level,
                start=idx,
                end=idx + len(token.token),
                reason="normalized variant match (no space)",
            ))

        return matches
