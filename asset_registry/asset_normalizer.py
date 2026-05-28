import unicodedata

ZERO_WIDTH_CHARS = frozenset({"\u200b", "\u200c", "\u200d", "\ufeff"})

HOMOGLYPH_MAP = {
    "а": "a", "А": "A",
    "е": "e", "Е": "E",
    "о": "o", "О": "O",
    "с": "c", "С": "C",
    "р": "p", "Р": "P",
    "х": "x", "Х": "X",
    "і": "i", "І": "I",
    "ѕ": "s",
    "ј": "j",
    "а": "a",
    "в": "b",
    "н": "h",
    "к": "k",
    "м": "m",
    "т": "t",
    "у": "y",
}


class AssetNormalizer:
    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return text
        result = "".join(c for c in text if c not in ZERO_WIDTH_CHARS)
        result = unicodedata.normalize("NFKC", result)
        result = "".join(HOMOGLYPH_MAP.get(c, c) for c in result)
        return result.strip()

    @staticmethod
    def normalize_asset(asset: dict) -> dict:
        normalized = dict(asset)
        if "value" in normalized and isinstance(normalized["value"], str):
            normalized["value"] = AssetNormalizer.normalize_text(normalized["value"])
        if "name" in normalized and isinstance(normalized["name"], str):
            normalized["name"] = AssetNormalizer.normalize_text(normalized["name"])
        if "aliases" in normalized and isinstance(normalized["aliases"], list):
            normalized["aliases"] = [
                AssetNormalizer.normalize_text(a) if isinstance(a, str) else a
                for a in normalized["aliases"]
            ]
        return normalized
