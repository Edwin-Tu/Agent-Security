from .base_skill import BaseSkill


class RolePlaySkill(BaseSkill):
    def __init__(self):
        super().__init__("role_play", "偵測角色扮演繞過攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["假裝你是", "扮演", "想像你是", "pretend you are", "act as if",
                    "you are now", "從現在開始你", "你現在是"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到角色扮演攻擊，已阻擋。" if threat_info.get("detected") else text
