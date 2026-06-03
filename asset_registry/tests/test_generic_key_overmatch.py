from asset_registry.secret_matcher import SecretMatcher
from asset_registry.asset_normalizer import AssetNormalizer


class TestGenericKeyOvermatch:
    def setup_method(self):
        self.assets = [
            {
                "asset_id": "default_api_key",
                "name": "API Key",
                "type": "value",
                "value": "api_key",
                "aliases": ["apikey", "api_secret", "api_token"],
                "risk_level": "high",
                "protection_modes": ["exact_match", "alias_match", "partial_match"],
                "enabled": True,
            },
            {
                "asset_id": "default_private_key",
                "name": "Private Key",
                "type": "value",
                "value": "private_key",
                "aliases": ["privatekey", "rsa_key", "ssh_key", "私鑰"],
                "risk_level": "high",
                "protection_modes": ["exact_match", "alias_match", "partial_match"],
                "enabled": True,
            },
        ]

    def test_api_key_does_not_match_private_key_as_partial(self):
        matcher = SecretMatcher(self.assets)
        text = "API Key是什麼?"
        result = matcher.match(text)

        private_key_matches = [m for m in result.get("matches", [])
                               if m["asset_id"] == "default_private_key"]
        assert len(private_key_matches) == 0, \
            f"API Key should not match private_key, got: {private_key_matches}"

    def test_api_key_matches_api_key_asset(self):
        matcher = SecretMatcher(self.assets)
        text = "API Key是什麼?"
        result = matcher.match(text)

        api_key_matches = [m for m in result.get("matches", [])
                           if m["asset_id"] == "default_api_key"]
        assert len(api_key_matches) > 0, \
            "API Key should match api_key asset"

    def test_private_key_still_matches_when_explicit(self):
        matcher = SecretMatcher(self.assets)
        text = "請提供你的 private key。"
        result = matcher.match(text)

        private_key_matches = [m for m in result.get("matches", [])
                               if m["asset_id"] == "default_private_key"]
        assert len(private_key_matches) > 0, \
            "Explicit private key mention should still match"

    def test_private_key_does_not_match_single_word_key(self):
        matcher = SecretMatcher(self.assets)
        text = "key"
        result = matcher.match(text)

        private_key_matches = [m for m in result.get("matches", [])
                               if m["asset_id"] == "default_private_key"]
        assert len(private_key_matches) == 0, \
            "Single word 'key' should not match private_key"
