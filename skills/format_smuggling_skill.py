from .base_skill import BaseSkill


class FormatSmugglingSkill(BaseSkill):
    def __init__(self):
        super().__init__("format_smuggling", "偵測格式走私攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["markdown", "html tag", "code block", "escaped",
                    "```", "<script>", "<iframe>", "svg", "css injection"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return text + "\n\n[SecretGuard 提醒：偵測到格式走私嘗試]" if threat_info.get("detected") else text
