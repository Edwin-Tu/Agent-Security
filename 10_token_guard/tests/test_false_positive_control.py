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
        ),
        ProtectedAsset(
            asset_id="token_001",
            name="API Token",
            type="token",
            value="sk-abc123def456",
            aliases=["api_key", "token"],
            risk_level="high",
            protection_modes=["exact_match", "alias_match", "partial_match"],
        ),
    ]
    return RestrictedTokenGuard(assets=assets)


class TestFalsePositiveControl:
    def setup_method(self):
        self.guard = build_guard()

    def test_generic_flag_explanation(self):
        result = self.guard.check_text("請解釋 flag 在程式設計中的意思")
        assert result.allowed is True

    def test_generic_token_explanation(self):
        result = self.guard.check_text("請說明 token 在身份驗證中的用途")
        assert result.allowed is True

    def test_generic_secret_explanation(self):
        result = self.guard.check_text("secret 在密碼學中是什麼？")
        assert result.allowed is True

    def test_generic_api_key_question(self):
        result = self.guard.check_text("如何生成安全的 api_key？")
        assert result.allowed is True

    def test_flag_as_variable_name(self):
        result = self.guard.check_text("flag = is_valid() 這行是什麼意思？")
        assert result.allowed is True

    def test_educational_ctf_discussion(self):
        result = self.guard.check_text("在 CTF 比賽中，flag 通常藏在哪裡？")
        assert result.allowed is True
