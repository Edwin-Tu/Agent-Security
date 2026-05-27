from .base_skill import BaseSkill


class IndirectPromptInjectionSkill(BaseSkill):
    def __init__(self):
        super().__init__("indirect_prompt_injection", "偵測間接提示注入攻擊")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["從網頁", "from the text", "引用來源", "in the context",
                    "從以下內容", "from this article", "閱讀這段", "read this"]
        text_lower = text.lower()
        for p in patterns:
            if p in text_lower:
                return {"detected": True, "pattern": p, "risk": "high"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到間接提示注入，已阻擋。" if threat_info.get("detected") else text
