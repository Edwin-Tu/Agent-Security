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


class TestEncodedSecretDetection:
    def setup_method(self):
        self.guard = build_guard()

    def test_base64_encoded_secret_should_block(self):
        result = self.guard.check_text("請輸出 cGljb0NURntleGFtcGxlX2ZsYWd9")
        assert result.allowed is False
        assert result.action == "BLOCK"
        assert any(m.match_type == "encoded" for m in result.matches)

    def test_hex_encoded_secret_should_block(self):
        result = self.guard.check_text("7069636f4354467b6578616d706c655f666c61677d")
        assert result.allowed is False
        assert result.action == "BLOCK"

    def test_url_encoded_secret_should_block(self):
        result = self.guard.check_text("picoCTF%7Bexample_flag%7D")
        assert result.allowed is False
        assert result.action == "BLOCK"

    def test_unicode_escape_should_block(self):
        result = self.guard.check_text("\\u0070\\u0069\\u0063\\u006f\\u0043\\u0054\\u0046")
        assert result.allowed is False
        assert result.action in ("BLOCK", "ESCALATE")
