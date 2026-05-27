from .base_skill import BaseSkill


class TranslationBypassSkill(BaseSkill):
    def __init__(self):
        super().__init__("translation_bypass", "偵測翻譯繞過攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["翻譯成", "translate", "in french", "in chinese", "in japanese",
                    "in korean", "翻成", "翻訳", "번역"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到翻譯繞過嘗試，已阻擋。" if threat_info.get("detected") else text
