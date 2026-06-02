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


class TestRuntimeExport:
    def setup_method(self):
        self.guard = build_guard()

    def test_export_contains_asset_id(self):
        exported = self.guard.export_for_runtime()
        assert "secret_001" in exported

    def test_export_contains_exact_tokens(self):
        exported = self.guard.export_for_runtime()
        assert "picoCTF{example_flag}" in exported["secret_001"]["exact"]

    def test_export_contains_aliases(self):
        exported = self.guard.export_for_runtime()
        aliases = exported["secret_001"]["aliases"]
        assert "flag" in aliases
        assert "答案" in aliases
        assert "通關碼" in aliases

    def test_export_contains_partial_tokens(self):
        exported = self.guard.export_for_runtime()
        partials = exported["secret_001"]["partial"]
        assert "picoCTF" in partials
        assert "example_flag" in partials

    def test_export_contains_encoded_tokens(self):
        exported = self.guard.export_for_runtime()
        encoded = exported["secret_001"]["encoded"]
        assert len(encoded) > 0

    def test_export_contains_risk_level(self):
        exported = self.guard.export_for_runtime()
        assert exported["secret_001"]["risk_level"] == "critical"

    def test_export_format_is_consumable_by_runtime(self):
        exported = self.guard.export_for_runtime()
        for asset_id, data in exported.items():
            assert "exact" in data
            assert "partial" in data
            assert "aliases" in data
            assert "encoded" in data
            assert "normalized" in data
            assert "risk_level" in data
