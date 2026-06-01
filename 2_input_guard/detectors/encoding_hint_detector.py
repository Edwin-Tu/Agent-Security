import re


OBFUSCATION_PATTERNS = [
    r"\b\w\s+\w\s+\w\s+\w\b",
    r"\b\w-\w-\w-\w\b",
    r"\b\w_\w_\w_\w\b",
    r"\b\w\.\w\.\w\.\w\b",
]

SPECIFIC_OBFUSCATION = [
    r"\bf\s+l\s+a\s+g\b",
    r"\bf-l-a-g\b",
    r"\bf_l_a_g\b",
    r"\bs\s+e\s+c\s+r\s+e\s+t\b",
    r"\bs-e-c-r-e-t\b",
    r"\bs_e_c_r_e_t\b",
    r"\bk\s+e\s+y\b",
    r"\bk-e-y\b",
    r"\bk_e_y\b",
    r"\bp\s+a\s+s\s+s\b",
    r"\bp-a-s-s\b",
    r"\bp_a_s_s\b",
]

ENCODING_HINT_PATTERNS = [
    r"用\s*(Base64|base64|Hex|hex|Binary|binary| octal|rot13|ROT13)\s*(回答|輸出|回傳|顯示|格式|encode|編碼)",
    r"(請|幫我|麻煩)\s*(用|以)\s*(Base64|base64|Hex|hex|Binary|binary|ROT13|rot13|編碼|encode)\s*(方式|格式)?\s*(回答|輸出|回傳|顯示)",
    r"base64\s*(encode|decode|output|format|回答)",
    r"hex\s*(encode|decode|output|format|回答)",
    r"以\s*(Base64|Hex|Binary|ROT13)\s*(格式|方式)\s*(輸出|回傳|回答)",
    r"請\s*用\s*(Base64|Hex|Binary|ROT13)\s*回答",
]

CROSS_LANGUAGE_PATTERNS = [
    r"用\s*(日本語|日文|英文|English|韓文|한국어|法文|Français|德文|Deutsch|西班牙文|Español)\s*(回答|輸出|回傳|說|解釋)",
    r"用\s*(多種|不同)\s*(語言|語系)\s*(回答|輸出|回傳|說|解釋)",
    r"mixed\s+languages?",
    r"cross\s*[-]?lingu(?:al|istic)",
    r"多語言\s*(回答|輸出|回傳|混合)",
    r"中英\s*(混合|夾雜|交錯)",
]


class EncodingHintDetector:
    def detect(self, text: str) -> dict:
        if not text or not text.strip():
            return {"matched": False, "rules": []}

        text_lower = text.lower()
        matched_rules = []

        for p in SPECIFIC_OBFUSCATION:
            if re.search(p, text_lower):
                matched_rules.append("obfuscation_hint")
                break
        else:
            for p in OBFUSCATION_PATTERNS:
                if re.search(p, text_lower):
                    matched_rules.append("obfuscation_hint")
                    break

        for p in ENCODING_HINT_PATTERNS:
            if re.search(p, text, re.IGNORECASE):
                matched_rules.append("encoding_hint")
                break

        for p in CROSS_LANGUAGE_PATTERNS:
            if re.search(p, text_lower):
                matched_rules.append("cross_language_hint")
                break

        return {
            "matched": len(matched_rules) > 0,
            "rules": matched_rules,
        }
