from .base_skill import BaseSkill


class EncodingBypassSkill(BaseSkill):
    def __init__(self):
        super().__init__("encoding_bypass", "Detects encoding bypass attacks")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["base64", "hex encoding", "unicode escape", "url encode",
                    "base64 decode", "hex decode", "percent encoding", "rot13", "morse"]
        for p in patterns:
            if p in text.lower():
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到編碼繞過嘗試，已阻擋。" if threat_info.get("detected") else text
