from typing import Optional

TRANSLATION_MAP = {
    "flag": ["旗標", "答案", "通關碼", "標誌", "旗帜"],
    "password": ["密碼", "口令", "密码"],
    "token": ["權杖", "令牌", "代幣", "凭证"],
    "private key": ["私鑰", "私钥", "私有密钥"],
    "api key": ["api金鑰", "api密鑰", "api密钥"],
    "secret": ["機密", "秘密", "机密"],
    "system prompt": ["系統提示詞", "系统提示", "系统提示词"],
    "credential": ["憑證", "凭证", "證書"],
}


class TranslationMatcher:
    @staticmethod
    def match(text: str, asset: dict) -> Optional[dict]:
        if not text or not asset:
            return None
        text_lower = text.lower().strip()

        value = asset.get("value", "").lower()
        for eng, translations in TRANSLATION_MAP.items():
            if eng in value or eng in text_lower:
                for t in translations:
                    if t in text_lower:
                        return {
                            "mode": "translation",
                            "matched": t,
                            "source_term": eng,
                            "risk": "medium",
                        }

        name = asset.get("name", "").lower()
        for eng, translations in TRANSLATION_MAP.items():
            for t in translations:
                if t in text_lower and (eng in name or eng in value):
                    return {
                        "mode": "translation",
                        "matched": t,
                        "source_term": eng,
                        "risk": "medium",
                    }

        return None
