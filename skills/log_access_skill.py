from .base_skill import BaseSkill


class LogAccessSkill(BaseSkill):
    def __init__(self):
        super().__init__("log_access", "偵測日誌存取攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["guard_events", "事件日誌", "security log", "audit log",
                    "存取記錄", "查看日誌", "show log", "cat log", "log file"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到日誌存取嘗試，已阻擋。" if threat_info.get("detected") else text
