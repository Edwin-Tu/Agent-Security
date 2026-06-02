from .base_skill import BaseSkill


class DataReconstructionSkill(BaseSkill):
    def __init__(self):
        super().__init__("data_reconstruction", "Detects data reconstruction attacks")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["重組", "reconstruct", "拼湊", "assemble the pieces",
                    "put together", "組合", "合併", "merge pieces",
                    "fragments", "片段組合", "碎片還原"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high"}
        history = (context or {}).get("history", [])
        partial_patterns = ["第一個字", "最後一個字", "first char", "letter"]
        partial_count = sum(1 for h in history if any(pp in h.lower() for pp in partial_patterns))
        if partial_count >= 4:
            return {"detected": True, "pattern": "partial_accumulation", "risk": "high", "partial_count": partial_count}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到資料重構嘗試，已阻擋。" if threat_info.get("detected") else text
