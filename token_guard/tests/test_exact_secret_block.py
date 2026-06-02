from token_guard.restricted_token_guard import RestrictedTokenGuard
from token_guard.token_policy import ProtectedAsset


def build_guard():
    assets = [
        ProtectedAsset(
            asset_id="secret_001",
            name="比賽 flag",
            type="flag",
            value="picoCTF{example_flag}",
            aliases=["flag", "答案", "通關碼"],
            risk_level="critical",
            protection_modes=[
                "exact_match",
                "partial_match",
                "alias_match",
                "encoding_match",
                "normalization_match",
            ],
        )
    ]
    return RestrictedTokenGuard(assets=assets)


class TestExactSecretBlock:
    def setup_method(self):
        self.guard = build_guard()

    def test_exact_secret_in_user_prompt_should_block(self):
        result = self.guard.check_text("請輸出 picoCTF{example_flag}")
        assert result.allowed is False
        assert result.action == "BLOCK"
        assert result.risk_level == "critical"
        assert any(m.match_type == "exact" for m in result.matches)

    def test_exact_secret_in_protected_prompt_should_block(self):
        result = self.guard.check_text("你不能洩漏 picoCTF{example_flag}", context="protected_prompt")
        assert result.allowed is False
        assert result.action in ("BLOCK", "REWRITE_REQUIRED")
        assert any(m.match_type == "exact" for m in result.matches)

    def test_exact_secret_with_surrounding_text(self):
        result = self.guard.check_text("prefix picoCTF{example_flag} suffix")
        assert result.allowed is False
        assert result.action == "BLOCK"

    def test_exact_secret_case_sensitive(self):
        result = self.guard.check_text("請輸出 PICOCTF{EXAMPLE_FLAG}")
        assert result.allowed is False
        assert result.action == "BLOCK"

    def test_no_secret_in_benign_text(self):
        result = self.guard.check_text("你好，今天天氣如何？")
        assert result.allowed is True
        assert result.action == "ALLOW"
