import re


ASSET_NAMES = {
    "flag": [r"flag", r"ctf", r"答案", r"通關碼"],
    "api_key": [r"api[\-\s]*key", r"apikey", r"api[\-\s]*secret", r"api[\-\s]*token", r"api金鑰", r"api密鑰"],
    "password": [r"password", r"passwd", r"pwd", r"passphrase", r"密碼"],
    "token": [r"token", r"auth_token", r"access_token", r"bearer_token", r"refresh_token", r"令牌", r"授權令牌"],
    "private_key": [r"private[\-\s]*key", r"privatekey", r"rsa[\-\s]*key", r"ssh[\-\s]*key", r"私鑰", r"私密金鑰"],
    "system_prompt": [r"system[\-\s]*prompt", r"system[\-\s]*instruction", r"system[\-\s]*message",
                       r"sys[\-\s]*prompt", r"系統提示", r"系統指令"],
    "secret": [r"secret", r"secrets", r"機密"],
    "credential": [r"credential", r"credentials", r"憑證", r"認證資訊"],
}

PARTIAL_DISCLOSURE_PATTERNS = [
    r"(前|頭|第[一二三四五六七八九十\d])\s*\d*\s*個\s*(字元|字|字符|字母|位)",
    r"prefix",
    r"前綴",
    r"(只|僅)\s*(告訴|說|顯示|輸出|給)",
    r"部分\s*(內容|資訊|資料|信息|結果)",
    r"partial",
    r"片段",
]

ENCODED_DISCLOSURE_PATTERNS = [
    r"base64\s*(編碼|encode|輸出|回答|回傳|顯示|列出)",
    r"hex\s*(輸出|回答|回傳|顯示|列出|encode|編碼)",
    r"用\s*(base64|hex)\s*(回答|輸出|回傳|顯示|列出|encode|編碼)",
    r"(encoded|encrypted|obfuscated)\s*(output|format|方式|格式)",
    r"編碼\s*(後|過)?\s*(輸出|回答|回傳|顯示)",
]


class AssetRequestDetector:
    def detect(self, text: str) -> dict:
        if not text or not text.strip():
            return {"matched": False, "rules": [], "detected_assets": []}

        text_lower = text.lower()
        matched_rules = []
        detected_assets = []

        for asset_name, aliases in ASSET_NAMES.items():
            for alias in aliases:
                if re.search(alias, text_lower):
                    if asset_name not in detected_assets:
                        detected_assets.append(asset_name)
                    break

        if detected_assets:
            matched_rules.append("protected_asset_mention")

        for p in PARTIAL_DISCLOSURE_PATTERNS:
            if re.search(p, text_lower):
                matched_rules.append("partial_disclosure")
                break

        for p in ENCODED_DISCLOSURE_PATTERNS:
            if re.search(p, text_lower):
                matched_rules.append("encoded_disclosure")
                break

        return {
            "matched": len(matched_rules) > 0,
            "rules": matched_rules,
            "detected_assets": detected_assets,
        }
