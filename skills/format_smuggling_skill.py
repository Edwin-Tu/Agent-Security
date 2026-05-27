from .base_skill import BaseSkill


class FormatSmugglingSkill(BaseSkill):
    def __init__(self):
        super().__init__("format_smuggling", "Detects format smuggling attacks")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["markdown", "html tag", "code block", "escaped",
                    "```", "<script>", "<iframe>", "svg", "css injection"]
        for p in patterns:
            if p in text.lower():
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return text + "\n\n[SecretGuard 提醒：偵測到格式走私嘗試]" if threat_info.get("detected") else text
