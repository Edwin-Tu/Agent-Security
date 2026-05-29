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


class TestUnicodeNormalizationDetection:
    def setup_method(self):
        self.guard = build_guard()

    def test_whitespace_injected_secret(self):
        result = self.guard.check_text("p i c o C T F { e x a m p l e _ f l a g }")
        assert result.allowed is False
        assert result.action in ("BLOCK", "ESCALATE")
        assert any(m.match_type == "normalized" for m in result.matches)

    def test_case_obfuscated_secret(self):
        result = self.guard.check_text("PicoCTF{Example_FLAG}")
        assert result.allowed is False
        assert result.action in ("BLOCK", "ESCALATE")

    def test_fullwidth_characters(self):
        result = self.guard.check_text("ｐｉｃｏＣＴＦ｛ｅｘａｍｐｌｅ＿ｆｌａｇ｝")
        assert result.allowed is False

    def test_zero_width_chars_inserted(self):
        text = "p\u200bicoCTF{e\u200bxample_flag}"
        result = self.guard.check_text(text)
        assert result.allowed is False

    def test_separator_inserted_secret(self):
        result = self.guard.check_text("p-i-c-o-C-T-F-{-e-x-a-m-p-l-e-_-f-l-a-g-}")
        assert result.allowed is False

    def test_nfkc_normalized_variant(self):
        result = self.guard.check_text("picoctfexampleflag")
        assert result.allowed is False
