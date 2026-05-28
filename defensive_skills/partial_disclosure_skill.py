from .base_skill import BaseSkill


class PartialDisclosureSkill(BaseSkill):
    def __init__(self):
        super().__init__("partial_disclosure", "Detects partial disclosure attacks")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["第一個字", "最後一個字", "只給我一個字母", "逐字顯示",
                    "first character", "last character", "one letter at a time",
                    "one character", "每個字分開", "前3碼"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "medium"}
        history = (context or {}).get("history", [])
        if history:
            count = sum(1 for h in history if any(pp in h.lower() for pp in patterns))
            if count >= 3:
                return {"detected": True, "pattern": "multi_cue_partial", "risk": "high", "repeat_count": count}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到部分揭露嘗試，已阻擋。" if threat_info.get("detected") else text
