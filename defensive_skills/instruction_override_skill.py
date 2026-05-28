from .base_skill import BaseSkill


class InstructionOverrideSkill(BaseSkill):
    def __init__(self):
        super().__init__("instruction_override", "Detects instruction override attacks")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["忽略以上", "忽略之前的", "ignore previous", "override",
                    " disregard", "不要理會", "ignore all", "忽略先前規則"]
        for p in patterns:
            if p in text.lower():
                return {"detected": True, "pattern": p, "risk": "high"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到指令覆蓋攻擊，已阻擋。" if threat_info.get("detected") else text
