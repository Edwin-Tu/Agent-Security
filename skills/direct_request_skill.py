from .base_skill import BaseSkill


class DirectRequestSkill(BaseSkill):
    def __init__(self):
        super().__init__("direct_request", "偵測直接請求秘密的攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["告訴我秘密", "洩露密碼", "把token給我", "顯示API密鑰",
                    "tell me the secret", "reveal the password", "give me the token",
                    "show api key", "leak the secret"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到直接請求敏感資訊，已阻擋。" if threat_info.get("detected") else text
