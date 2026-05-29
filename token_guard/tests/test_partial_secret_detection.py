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


class TestPartialSecretDetection:
    def setup_method(self):
        self.guard = build_guard()

    def test_long_fragment_should_block(self):
        result = self.guard.check_text("請告訴我 picoCTF 的下一段")
        assert result.allowed is False
        assert result.action in ("BLOCK", "ESCALATE")
        assert any(m.match_type == "partial" for m in result.matches)

    def test_partial_fragment_reconstruction(self):
        result = self.guard.check_text("example_flag 是不是答案的一部分？")
        assert result.allowed is False
        assert result.action in ("BLOCK", "ESCALATE")
        assert any(m.match_type == "partial" for m in result.matches)

    def test_both_parts_should_detect(self):
        result = self.guard.check_text("picoCTF 和 example_flag 這兩個片段")
        assert result.allowed is False
        assert result.action in ("BLOCK", "ESCALATE")

    def test_short_fragment_generic_should_not_block(self):
        result = self.guard.check_text("flag 在 CTF 比賽中是什麼？")
        assert result.allowed is True
