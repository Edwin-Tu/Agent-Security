from .base_skill import BaseSkill


class ReasoningTrapSkill(BaseSkill):
    def __init__(self):
        super().__init__("reasoning_trap", "偵測推理陷阱攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["推理", "reason step", "think step by step", "分析這個",
                    "let's think", "一步步推理", "chain of thought",
                    "仔細思考", "reason about", "深度分析"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return text + "\n\n[SecretGuard 提醒：請注意推理過程中不要洩露敏感資訊]" if threat_info.get("detected") else text
