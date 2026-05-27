from .base_skill import BaseSkill


class PersonaOverrideSkill(BaseSkill):
    def __init__(self):
        super().__init__("persona_override", "偵測人格覆蓋攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["你現在是", "你將扮演", "act as", "從現在開始你是",
                    "you are now", "你的新角色", "your new role",
                    "化身為", "transform into", "become"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到人格覆蓋攻擊，已阻擋。" if threat_info.get("detected") else text
