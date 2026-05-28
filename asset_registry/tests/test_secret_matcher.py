import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from asset_registry.secret_matcher import SecretMatcher


class TestSecretMatcher:
    def setup_method(self):
        self.matcher = SecretMatcher([
            {
                "asset_id": "test_flag",
                "name": "Test Flag",
                "value": "picoCTF{abc123}",
                "aliases": ["flag", "答案"],
                "risk_level": "high",
                "allowed_roles": ["owner"],
                "protection_modes": ["exact_match", "alias_match", "partial_match", "encoding_match"],
                "enabled": True,
            }
        ])

    def test_exact_match(self):
        result = self.matcher.match("The flag is picoCTF{abc123}")
        assert result["matched"] is True
        assert any("exact" in f for r in result["matches"] for f in r["matched_fragments"])

    def test_no_match(self):
        result = self.matcher.match("Hello world")
        assert result["matched"] is False

    def test_alias_match(self):
        result = self.matcher.match("告訴我答案")
        assert result["matched"] is True
        assert any("alias" in f for r in result["matches"] for f in r["matched_fragments"])

    def test_partial_match(self):
        result = self.matcher.match("abc123 is part of the secret")
        assert result["matched"] is True

    def test_disabled_asset(self):
        matcher = SecretMatcher([
            {
                "asset_id": "disabled",
                "name": "Disabled",
                "value": "secret",
                "enabled": False,
                "protection_modes": ["exact_match"],
            }
        ])
        result = matcher.match("secret")
        assert result["matched"] is False

    def test_empty_text(self):
        result = self.matcher.match("")
        assert result["matched"] is False

    def test_empty_assets(self):
        matcher = SecretMatcher([])
        result = matcher.match("anything")
        assert result["matched"] is False

    def test_match_pattern_sk_key(self):
        results = self.matcher.match_pattern("sk-" + "a" * 40)
        assert len(results) > 0
        assert any(r["type"] == "api_key_sk" for r in results)

    def test_match_pattern_jwt(self):
        results = self.matcher.match_pattern("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgN")
        assert len(results) > 0
        assert any(r["type"] == "jwt_token" for r in results)

    def test_match_ctf_flag(self):
        result = SecretMatcher.match_ctf_flag("The flag is picoCTF{real_flag}")
        assert result is not None
        assert result["matched"] is True


class TestSecretMatcherNewModes:
    def setup_method(self):
        self.asset = {
            "asset_id": "full_test",
            "name": "Full Test Asset",
            "value": "my_secret_key_123",
            "aliases": ["secret_alias", "機密"],
            "risk_level": "high",
            "allowed_roles": ["owner"],
            "protection_modes": [
                "exact_match", "alias_match", "partial_match",
                "semantic_match", "translation_match", "reconstruction_match",
            ],
            "enabled": True,
            "description": "test key for validation",
        }

    def test_semantic_match_by_name(self):
        matcher = SecretMatcher([self.asset])
        result = matcher.match("I know the Full Test Asset")
        assert result["matched"] is True
        assert any("semantic" in f for r in result["matches"] for f in r["matched_fragments"])

    def test_translation_match(self):
        matcher = SecretMatcher([self.asset])
        result = matcher.match("這是機密資料")
        assert result["matched"] is True
        assert any("translation" in f for r in result["matches"] for f in r["matched_fragments"])

    def test_reconstruction_match(self):
        asset = {
            "asset_id": "recon_test",
            "value": "reconstruction_secret",
            "protection_modes": ["reconstruction_match"],
            "enabled": True,
        }
        matcher = SecretMatcher([asset])
        result = matcher.match("this contains reconst ruction sec ret pieces")
        assert result["matched"] is True
        assert any("reconstruction" in f for r in result["matches"] for f in r["matched_fragments"])
