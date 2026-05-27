from .base_skill import BaseSkill


class OutputConstraintBypassSkill(BaseSkill):
    def __init__(self):
        super().__init__("output_constraint_bypass", "偵測輸出限制繞過攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["不要限制", "don't filter", "無需審查", "output freely",
                    "no restrictions", "without filtering", "不要審查",
                    "不要管安全", "bypass filter", "忽略安全"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到輸出限制繞過嘗試，已阻擋。" if threat_info.get("detected") else text
