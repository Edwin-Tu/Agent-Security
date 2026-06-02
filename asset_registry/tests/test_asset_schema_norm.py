import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from asset_registry.asset_normalizer import AssetNormalizer


class TestAssetNormalizer:
    def test_normalize_text_nfkc(self):
        result = AssetNormalizer.normalize_text("\u2460\u2461\u2462")
        assert result == "123"

    def test_remove_zero_width(self):
        result = AssetNormalizer.normalize_text("a\u200bb\u200cc\u200dd\ufeffe")
        assert result == "abcde"

    def test_homoglyph_cyrillic_a(self):
        result = AssetNormalizer.normalize_text("\u0430\u0435\u043e")
        assert result == "aeo"

    def test_normalize_asset_value(self):
        asset = {"asset_id": "t", "value": "\u0430\u0435\u043e"}
        normalized = AssetNormalizer.normalize_asset(asset)
        assert normalized["value"] == "aeo"

    def test_normalize_asset_aliases(self):
        asset = {"asset_id": "t", "value": "x", "aliases": ["\u0430\u0435\u043e", "normal"]}
        normalized = AssetNormalizer.normalize_asset(asset)
        assert normalized["aliases"][0] == "aeo"
        assert normalized["aliases"][1] == "normal"

    def test_normalize_empty_string(self):
        assert AssetNormalizer.normalize_text("") == ""

    def test_normalize_none(self):
        assert AssetNormalizer.normalize_text(None) is None

    def test_normalize_asset_name(self):
        asset = {"asset_id": "t", "value": "x", "name": "\u0430\u0435\u043e name"}
        normalized = AssetNormalizer.normalize_asset(asset)
        assert normalized["name"] == "aeo name"
