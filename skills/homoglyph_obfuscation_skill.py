from .base_skill import BaseSkill


class HomoglyphObfuscationSkill(BaseSkill):
    def __init__(self):
        super().__init__("homoglyph_obfuscation", "偵測同形字符混淆攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["homoglyph", "相似字符", "unicode lookalike", "混淆字符",
                    "similar looking", "lookalike", "零寬", "zero-width"]
        suspicious_chars = ["ⴲ", "е", "о", "а", "е́", "\\u200b", "\\u200c", "\\u200d"]
        char_detected = any(c in text for c in suspicious_chars)
        text_lower = text.lower()
        keyword_detected = any(p in text_lower for p in patterns)
        if keyword_detected or char_detected:
            return {"detected": True, "pattern": "homoglyph" if char_detected else "keyword", "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到同形字符混淆，已阻擋。" if threat_info.get("detected") else text
