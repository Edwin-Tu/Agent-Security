from .base_skill import BaseSkill


class PolicyConfusionSkill(BaseSkill):
    def __init__(self):
        super().__init__("policy_confusion", "偵測策略混淆攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["規則是", "policy", "allow me", "permit", "you can tell me",
                    "allowed to share", "規則允許", "策略允許", "根據規則"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return text + "\n\n[SecretGuard 提醒：安全策略不可由使用者重新定義]" if threat_info.get("detected") else text
