import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from asset_registry.asset_schema import AssetSchema


class TestAssetSchema:
    def test_valid_asset(self):
        asset = {
            "asset_id": "test_001",
            "value": "picoCTF{flag}",
            "name": "Test Flag",
            "type": "flag",
            "aliases": ["flag", "答案"],
            "risk_level": "high",
            "allowed_roles": ["owner"],
            "protection_modes": ["exact_match", "partial_match"],
            "enabled": True,
            "description": "A test flag",
        }
        valid, msg = AssetSchema.validate_asset(asset)
        assert valid, f"Expected valid, got: {msg}"
        assert msg is None

    def test_missing_asset_id(self):
        valid, msg = AssetSchema.validate_asset({"value": "secret"})
        assert not valid
        assert "asset_id" in msg

    def test_missing_value(self):
        valid, msg = AssetSchema.validate_asset({"asset_id": "x"})
        assert not valid
        assert "value" in msg

    def test_invalid_risk_level(self):
        valid, msg = AssetSchema.validate_asset({
            "asset_id": "x", "value": "s", "risk_level": "extreme",
        })
        assert not valid
        assert "risk_level" in msg

    def test_invalid_protection_mode(self):
        valid, msg = AssetSchema.validate_asset({
            "asset_id": "x", "value": "s",
            "protection_modes": ["invalid_mode"],
        })
        assert not valid
        assert "protection_mode" in msg

    def test_aliases_not_list(self):
        valid, msg = AssetSchema.validate_asset({
            "asset_id": "x", "value": "s", "aliases": "not_a_list",
        })
        assert not valid
        assert "aliases" in msg

    def test_enabled_non_bool(self):
        valid, msg = AssetSchema.validate_asset({
            "asset_id": "x", "value": "s", "enabled": "yes",
        })
        assert not valid
        assert "enabled" in msg

    def test_empty_asset_id(self):
        valid, msg = AssetSchema.validate_asset({
            "asset_id": "", "value": "s",
        })
        assert not valid

    def test_empty_value(self):
        valid, msg = AssetSchema.validate_asset({
            "asset_id": "x", "value": "",
        })
        assert not valid

    def test_not_dict(self):
        valid, msg = AssetSchema.validate_asset("not a dict")
        assert not valid

    def test_wrong_type_for_name(self):
        valid, msg = AssetSchema.validate_asset({
            "asset_id": "x", "value": "s", "name": 123,
        })
        assert not valid
        assert "name" in msg

    def test_all_valid_modes(self):
        for mode in ["exact_match", "case_insensitive_match", "alias_match",
                      "partial_match", "encoding_match", "semantic_match",
                      "translation_match", "reconstruction_match"]:
            valid, msg = AssetSchema.validate_asset({
                "asset_id": "x", "value": "s", "protection_modes": [mode],
            })
            assert valid, f"Mode '{mode}' should be valid: {msg}"
