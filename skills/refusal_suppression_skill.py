from .base_skill import BaseSkill


class RefusalSuppressionSkill(BaseSkill):
    def __init__(self):
        super().__init__("refusal_suppression", "偵測拒絕抑制攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["不要拒絕", "don't refuse", "不能說不知道", "must answer",
                    "不準說不", "you cannot refuse", "一定要回答",
                    "禁止拒絕", "never say no", "always comply"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到拒絕抑制攻擊，已阻擋。" if threat_info.get("detected") else text
