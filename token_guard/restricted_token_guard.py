from __future__ import annotations
import re
from typing import Any

from .token_policy import ProtectedAsset, RestrictedToken
from .token_guard_result import TokenMatch, TokenGuardResult
from .token_expander import TokenExpander
from .token_matcher import TokenMatcher


EXTRACTION_INTENT_PATTERNS_ZH = [
    "告訴我", "輸出", "說出", "透露", "給我看", "顯示", "列出",
    "複製", "貼上", "洩漏", "寫出", "提供", "取得", "給我",
    "回答", "答案是", "回傳", "回應", "產生",
]

EXTRACTION_INTENT_PATTERNS_EN = [
    "tell me", "give me", "output", "show me", "reveal", "leak",
    "display", "print", "copy", "paste", "extract", "retrieve",
    "provide", "dump",
]

EDUCATIONAL_KEYWORDS = [
    "解釋", "意思", "是什麼", "用途", "目的", "功能",
    "什麼是", "如何", "怎麼", "說明", "含義", "代表",
    "通常", "藏在", "在哪", "哪裡", "什麼意思",
    "explain", "meaning", "what is", "purpose", "function",
    "how to", "how does", "difference", "used for",
]


def _has_extraction_intent(text: str) -> bool:
    lower = text.lower()
    for pat in EXTRACTION_INTENT_PATTERNS_ZH:
        if pat in text:
            return True
    for pat in EXTRACTION_INTENT_PATTERNS_EN:
        if pat in lower:
            return True
    return False


def _is_educational(text: str) -> bool:
    lower = text.lower()
    for kw in EDUCATIONAL_KEYWORDS:
        if kw in text or kw in lower:
            return True
    return False


class RestrictedTokenGuard:
    def __init__(self, assets: list[ProtectedAsset] | None = None, policy: dict | None = None):
        self._assets: list[ProtectedAsset] = assets or []
        self._policy: dict = policy or {}
        self._expander = TokenExpander()
        self._matcher = TokenMatcher()
        self._restricted_tokens: list[RestrictedToken] = []
        if self._assets:
            self.build_restricted_tokens()

    @staticmethod
    def _decode_unicode_escapes(text: str) -> list[str]:
        variants = []
        matches = list(re.finditer(r"\\u([0-9a-fA-F]{4})", text))
        if not matches:
            return variants
        decoded = []
        i = 0
        for m in matches:
            decoded.append(text[i:m.start()])
            cp = int(m.group(1), 16)
            decoded.append(chr(cp))
            i = m.end()
        decoded.append(text[i:])
        variants.append("".join(decoded))

        partial_matches = re.findall(r"\\u([0-9a-fA-F]{4})", text)
        if len(partial_matches) >= 2:
            partial_decoded = "".join(chr(int(h, 16)) for h in partial_matches if int(h, 16) >= 0x20)
            if partial_decoded:
                variants.append(partial_decoded)
        return variants

    def build_restricted_tokens(self) -> list[RestrictedToken]:
        self._restricted_tokens = self._expander.expand(self._assets)
        return self._restricted_tokens

    def check_text(self, text: str, context: str = "user_prompt") -> TokenGuardResult:
        if not text:
            return TokenGuardResult(
                allowed=True,
                action="ALLOW",
                risk_level="low",
                matches=[],
                restricted_tokens=self._restricted_tokens,
                reasons=["empty text"],
            )

        decoded_variants = self._decode_unicode_escapes(text)
        all_matches: list[TokenMatch] = []
        seen_keys: set[tuple[str, str, str]] = set()

        for variant in [text] + decoded_variants:
            matches = self._matcher.match(variant, self._restricted_tokens)
            for m in matches:
                key = (m.asset_id, m.match_type, m.matched_text)
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_matches.append(m)

        if not all_matches:
            return TokenGuardResult(
                allowed=True,
                action="ALLOW",
                risk_level="low",
                matches=[],
                restricted_tokens=self._restricted_tokens,
                reasons=["no matches found"],
            )

        return self._resolve_action(text, all_matches)

    def check_protected_prompt(self, protected_prompt: str) -> TokenGuardResult:
        result = self.check_text(protected_prompt, context="protected_prompt")
        for match in result.matches:
            if match.match_type in ("exact", "partial", "alias"):
                result.allowed = False
                result.action = "REWRITE_REQUIRED"
                result.risk_level = "critical"
                if "protected_prompt_contains_secret" not in result.reasons:
                    result.reasons.append("protected_prompt_contains_secret")
                break
        if result.allowed and result.action == "ALLOW":
            result.reasons.append("protected_prompt_is_clean")
        return result

    def export_for_runtime(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for asset in self._assets:
            entry: dict[str, Any] = {
                "exact": [],
                "partial": [],
                "aliases": [],
                "encoded": [],
                "normalized": [],
                "risk_level": asset.risk_level,
            }
            for rt in self._restricted_tokens:
                if rt.asset_id != asset.asset_id:
                    continue
                if rt.token_type == "exact":
                    entry["exact"].append(rt.token)
                elif rt.token_type == "partial":
                    entry["partial"].append(rt.token)
                elif rt.token_type == "alias":
                    entry["aliases"].append(rt.token)
                elif rt.token_type == "encoded":
                    entry["encoded"].append(rt.token)
                elif rt.token_type == "normalized":
                    entry["normalized"].append(rt.token)
            result[asset.asset_id] = entry
        return result

    def _resolve_action(self, text: str, matches: list[TokenMatch]) -> TokenGuardResult:
        has_extraction = _has_extraction_intent(text)
        is_edu = _is_educational(text)

        critical_match = None
        high_match = None
        alias_match = None
        partial_long_match = None
        encoded_match = None
        normalized_match = None

        for m in matches:
            if m.match_type == "exact" and m.risk_level in ("high", "critical"):
                if critical_match is None:
                    critical_match = m
            if m.match_type == "encoded":
                if encoded_match is None:
                    encoded_match = m
            if m.match_type == "partial":
                if partial_long_match is None:
                    partial_long_match = m
            if m.match_type == "normalized":
                if normalized_match is None:
                    normalized_match = m
            if m.match_type == "alias":
                if alias_match is None:
                    alias_match = m
            if m.risk_level == "critical" and m.match_type == "exact":
                if critical_match is None:
                    critical_match = m

        reasons: list[str] = [m.reason for m in matches if m.reason]

        if critical_match:
            return TokenGuardResult(
                allowed=False,
                action="BLOCK",
                risk_level="critical",
                matches=matches,
                restricted_tokens=self._restricted_tokens,
                reasons=reasons + ["critical secret detected"],
            )

        if encoded_match:
            return TokenGuardResult(
                allowed=False,
                action="BLOCK",
                risk_level="critical",
                matches=matches,
                restricted_tokens=self._restricted_tokens,
                reasons=reasons + ["encoded secret detected"],
            )

        if partial_long_match:
            if has_extraction:
                return TokenGuardResult(
                    allowed=False,
                    action="BLOCK",
                    risk_level="high",
                    matches=matches,
                    restricted_tokens=self._restricted_tokens,
                    reasons=reasons + ["partial secret with extraction intent"],
                )
            return TokenGuardResult(
                allowed=False,
                action="ESCALATE",
                risk_level="high",
                matches=matches,
                restricted_tokens=self._restricted_tokens,
                reasons=reasons + ["partial secret fragment detected"],
            )

        if normalized_match:
            if has_extraction:
                return TokenGuardResult(
                    allowed=False,
                    action="BLOCK",
                    risk_level="high",
                    matches=matches,
                    restricted_tokens=self._restricted_tokens,
                    reasons=reasons + ["normalized variant with extraction intent"],
                )
            return TokenGuardResult(
                allowed=False,
                action="ESCALATE",
                risk_level="high",
                matches=matches,
                restricted_tokens=self._restricted_tokens,
                reasons=reasons + ["normalized variant detected"],
            )

        if alias_match:
            if is_edu and not has_extraction:
                return TokenGuardResult(
                    allowed=True,
                    action="WARN",
                    risk_level="low",
                    matches=matches,
                    restricted_tokens=self._restricted_tokens,
                    reasons=reasons + ["alias match but educational context"],
                )
            if has_extraction:
                return TokenGuardResult(
                    allowed=False,
                    action="BLOCK",
                    risk_level="high",
                    matches=matches,
                    restricted_tokens=self._restricted_tokens,
                    reasons=reasons + ["alias with extraction intent"],
                )
            return TokenGuardResult(
                allowed=False,
                action="RESTRICT",
                risk_level="medium",
                matches=matches,
                restricted_tokens=self._restricted_tokens,
                reasons=reasons + ["alias detected"],
            )

        return TokenGuardResult(
            allowed=True,
            action="ALLOW",
            risk_level="low",
            matches=matches,
            restricted_tokens=self._restricted_tokens,
            reasons=["no actionable matches"],
        )
