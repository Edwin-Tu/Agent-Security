from .base_skill import BaseSkill


class StructuredOutputSkill(BaseSkill):
    def __init__(self):
        super().__init__("structured_output", "偵測結構化輸出攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["json格式", "回傳JSON", "output as JSON", "in xml",
                    "json format", "xml format", "as json", "as xml",
                    "以json", "以xml", "struct output"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        if not threat_info.get("detected"):
            return text
        return text + "\n\n[SecretGuard 提醒：請勿以結構化格式輸出敏感資訊]"
