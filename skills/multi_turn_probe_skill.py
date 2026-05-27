from .base_skill import BaseSkill


class MultiTurnProbeSkill(BaseSkill):
    def __init__(self):
        super().__init__("multi_turn_probe", "偵測多輪探測攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["循序漸進", "逐步", "step by step probe", "試試看",
                    "先回答", "first tell", "一步一步來", "慢慢來"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high", "multi_turn": True}
        history = (context or {}).get("history", [])
        probe_count = sum(1 for h in history if any(pp in h.lower() for pp in patterns))
        if probe_count >= 2:
            return {"detected": True, "pattern": "accumulated_probe", "risk": "high", "probe_count": probe_count}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到多輪探測攻擊，已阻擋。" if threat_info.get("detected") else text
