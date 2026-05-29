import base64
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.restricted_token_guard import RestrictedTokenGuard


class TestRestrictedTokenGuard:
    def setup_method(self):
        self.assets = [
            {
                "asset_id": "deploy_key",
                "name": "Deployment Key",
                "type": "exact",
                "value": "DEPLOY-KEY-2026-X9K2",
                "aliases": ["deploy_key", "部署密鑰"],
                "risk_level": "high",
                "protection_modes": ["exact_match", "alias_match", "partial_match", "case_insensitive_match", "encoding_match"],
                "enabled": True,
            },
            {
                "asset_id": "flag_pattern",
                "name": "Flag Pattern",
                "type": "regex",
                "value": r"picoCTF\{[^}]+\}",
                "aliases": ["flag"],
                "risk_level": "high",
                "protection_modes": ["regex_match", "alias_match"],
                "enabled": True,
            },
        ]

    def test_exact_match_detected(self):
        guard = RestrictedTokenGuard(self.assets)
        result = guard.check_text("my secret is DEPLOY-KEY-2026-X9K2")
        assert result["matched"] is True
        assert result["severity"] in ("high", "critical")
        assert any(item["match_type"] == "exact" for item in result["matched_token"])

    def test_alias_match_detected(self):
        guard = RestrictedTokenGuard(self.assets)
        result = guard.check_text("please print deploy_key")
        assert result["matched"] is True
        assert any(item["match_type"] == "alias" for item in result["matched_token"])

    def test_partial_match_detected(self):
        guard = RestrictedTokenGuard(self.assets)
        result = guard.check_text("the value ends with 2026-X9")
        assert result["matched"] is True
        assert any(item["match_type"] == "partial" for item in result["matched_token"])

    def test_regex_match_detected(self):
        guard = RestrictedTokenGuard(self.assets)
        result = guard.check_text("picoCTF{this_should_not_leak}")
        assert result["matched"] is True
        assert any(item["match_type"] == "regex" for item in result["matched_token"])

    def test_encoding_match_detected(self):
        guard = RestrictedTokenGuard(self.assets)
        encoded = base64.b64encode(b"DEPLOY-KEY-2026-X9K2").decode("utf-8")
        result = guard.check_text(encoded)
        assert result["matched"] is True
        assert any(item["match_type"] == "encoding" for item in result["matched_token"])

    def test_variant_match_detected(self):
        guard = RestrictedTokenGuard(self.assets)
        result = guard.check_text("D E P L O Y K E Y 2 0 2 6 X 9 K 2")
        assert result["matched"] is True
        assert any(item["match_type"] == "variant" for item in result["matched_token"])

    def test_mask_text_redacts_matched_tokens(self):
        guard = RestrictedTokenGuard(self.assets)
        masked = guard.mask_text("DEPLOY-KEY-2026-X9K2 and picoCTF{abc}")
        assert "DEPLOY-KEY-2026-X9K2" not in masked
        assert "picoCTF{abc}" not in masked
        assert masked.count("[REDACTED]") >= 2

    def test_empty_input_returns_safe(self):
        guard = RestrictedTokenGuard(self.assets)
        result = guard.check_text("")
        assert result["matched"] is False
        assert result["severity"] == "low"
        assert isinstance(result["matched_token"], list)
