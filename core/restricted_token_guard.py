from __future__ import annotations

import base64
import binascii
import re
from typing import Any


class RestrictedTokenGuard:
    def __init__(self, protected_assets: list[dict] | None):
        self.protected_assets: list[dict] = protected_assets or []
        self.restricted_tokens = self.build_restricted_tokens()

    def build_restricted_tokens(self) -> dict:
        """
        從受保護資產產生禁止 token 清單。
        包含原文、alias、片段、大小寫變體、編碼變體。
        """
        exact_tokens: dict[str, list[dict[str, Any]]] = {}
        partial_tokens: dict[str, list[dict[str, Any]]] = {}
        variant_tokens: dict[str, list[dict[str, Any]]] = {}
        encoded_tokens: dict[str, list[dict[str, Any]]] = {}
        regex_patterns: list[dict[str, Any]] = []

        for asset in self.protected_assets:
            if not isinstance(asset, dict):
                continue
            if not asset.get("enabled", True):
                continue

            value = str(asset.get("value", "")).strip()
            if not value:
                continue

            risk_level = str(asset.get("risk_level", "medium")).lower()
            aliases = [str(a).strip() for a in asset.get("aliases", []) if str(a).strip()]
            modes = set(asset.get("protection_modes") or ["exact_match", "alias_match"])
            asset_type = str(asset.get("type", "exact")).lower()

            meta = {
                "asset_id": asset.get("asset_id", "unknown"),
                "name": asset.get("name", "unknown"),
                "risk_level": risk_level,
            }

            candidates = [value] + aliases

            for token in candidates:
                token_lower = token.lower()
                if not token_lower:
                    continue

                if "exact_match" in modes or token == value:
                    exact_tokens.setdefault(token_lower, []).append({**meta, "match_type": "exact", "token": token})

                if token in aliases and "alias_match" in modes:
                    exact_tokens.setdefault(token_lower, []).append({**meta, "match_type": "alias", "token": token})

                compact = self._compact(token)
                if compact and len(compact) >= 6:
                    variant_tokens.setdefault(compact, []).append({**meta, "match_type": "variant", "token": token})

                if "encoding_match" in modes:
                    b64 = base64.b64encode(token.encode("utf-8")).decode("ascii").lower()
                    hx = token.encode("utf-8").hex().lower()
                    encoded_tokens.setdefault(b64, []).append({**meta, "match_type": "encoding", "token": token})
                    encoded_tokens.setdefault(hx, []).append({**meta, "match_type": "encoding", "token": token})

            if "partial_match" in modes:
                for fragment in self._generate_fragments(value):
                    partial_tokens.setdefault(fragment.lower(), []).append({**meta, "match_type": "partial", "token": fragment})

            if asset_type == "regex" or "regex_match" in modes:
                try:
                    regex_patterns.append({
                        **meta,
                        "match_type": "regex",
                        "token": value,
                        "pattern": re.compile(value, re.IGNORECASE),
                    })
                except re.error:
                    continue

        return {
            "exact_tokens": exact_tokens,
            "partial_tokens": partial_tokens,
            "variant_tokens": variant_tokens,
            "encoded_tokens": encoded_tokens,
            "regex_patterns": regex_patterns,
        }

    def check_text(self, text: str) -> dict:
        """
        檢查文字是否包含禁止 token 或可疑片段。
        回傳 matched / severity / reason / matched_token。
        """
        if text is None:
            return {
                "matched": False,
                "severity": "low",
                "reason": "None input.",
                "matched_token": [],
            }

        raw_text = str(text)
        if not raw_text:
            return {
                "matched": False,
                "severity": "low",
                "reason": "Empty input.",
                "matched_token": [],
            }

        indices = self.restricted_tokens
        lower_text = raw_text.lower()
        compact_text = self._compact(raw_text)

        matches: list[dict] = []
        seen: set[tuple[str, str, str]] = set()

        for token, metas in indices["exact_tokens"].items():
            if token and token in lower_text:
                for m in metas:
                    self._add_match(matches, seen, m)

        for token, metas in indices["partial_tokens"].items():
            if token and token in lower_text:
                for m in metas:
                    self._add_match(matches, seen, m)

        for token, metas in indices["variant_tokens"].items():
            if token and token in compact_text:
                for m in metas:
                    self._add_match(matches, seen, m)

        for item in indices["regex_patterns"]:
            found = item["pattern"].search(raw_text)
            if found:
                matched_item = dict(item)
                matched_item["token"] = found.group(0)
                matched_item.pop("pattern", None)
                self._add_match(matches, seen, matched_item)

        for token, metas in indices["encoded_tokens"].items():
            if token and token in lower_text:
                for m in metas:
                    self._add_match(matches, seen, m)

        decoded_candidates = self._decoded_candidates(raw_text)
        for decoded in decoded_candidates:
            decoded_lower = decoded.lower()
            for token, metas in indices["exact_tokens"].items():
                if token and token in decoded_lower:
                    for m in metas:
                        encoded_match = dict(m)
                        encoded_match["match_type"] = "encoding"
                        self._add_match(matches, seen, encoded_match)

        if not matches:
            return {
                "matched": False,
                "severity": "low",
                "reason": "No restricted token matched.",
                "matched_token": [],
            }

        severity = self._severity_from_matches(matches)
        reason = f"Matched {len(matches)} restricted token(s)."
        return {
            "matched": True,
            "severity": severity,
            "reason": reason,
            "matched_token": matches,
        }

    def mask_text(self, text: str) -> str:
        """
        把敏感 token 替換成 [REDACTED]。
        """
        if text is None:
            return ""

        masked = str(text)
        result = self.check_text(masked)
        if not result["matched"]:
            return masked

        literal_tokens = []
        for item in result["matched_token"]:
            token = str(item.get("token", ""))
            if token:
                literal_tokens.append(token)

        literal_tokens = sorted(set(literal_tokens), key=len, reverse=True)
        for token in literal_tokens:
            masked = re.sub(re.escape(token), "[REDACTED]", masked, flags=re.IGNORECASE)

        for regex_item in self.restricted_tokens["regex_patterns"]:
            masked = regex_item["pattern"].sub("[REDACTED]", masked)

        return masked

    @staticmethod
    def _add_match(matches: list[dict], seen: set[tuple[str, str, str]], item: dict):
        key = (
            str(item.get("asset_id", "")),
            str(item.get("match_type", "")),
            str(item.get("token", "")),
        )
        if key in seen:
            return
        seen.add(key)
        matches.append({
            "asset_id": item.get("asset_id", "unknown"),
            "name": item.get("name", "unknown"),
            "match_type": item.get("match_type", "exact"),
            "token": item.get("token", ""),
            "risk_level": item.get("risk_level", "medium"),
        })

    @staticmethod
    def _generate_fragments(value: str) -> set[str]:
        compact_value = value.strip()
        if len(compact_value) < 6:
            return set()

        min_len = max(3, len(compact_value) // 3)
        max_len = min(12, len(compact_value))
        fragments = set()
        for size in range(min_len, max_len + 1):
            for idx in range(0, len(compact_value) - size + 1):
                frag = compact_value[idx: idx + size].strip()
                if len(frag) >= min_len:
                    fragments.add(frag)
        return fragments

    @staticmethod
    def _compact(text: str) -> str:
        return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", text.lower())

    @staticmethod
    def _decoded_candidates(text: str) -> list[str]:
        candidates = []
        stripped = text.strip()
        if not stripped:
            return candidates

        try:
            decoded = base64.b64decode(stripped, validate=False).decode("utf-8", errors="ignore")
            if decoded:
                candidates.append(decoded)
        except (binascii.Error, ValueError):
            pass

        try:
            decoded = bytes.fromhex(stripped).decode("utf-8", errors="ignore")
            if decoded:
                candidates.append(decoded)
        except ValueError:
            pass

        return candidates

    @staticmethod
    def _severity_from_matches(matches: list[dict]) -> str:
        rank = {
            "low": 0,
            "medium": 1,
            "high": 2,
            "critical": 3,
        }
        inverse = {v: k for k, v in rank.items()}
        highest = 0
        for item in matches:
            level = str(item.get("risk_level", "medium")).lower()
            highest = max(highest, rank.get(level, 1))
        return inverse[highest]
