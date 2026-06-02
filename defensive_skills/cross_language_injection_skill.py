from .base_skill import BaseSkill


class CrossLanguageInjectionSkill(BaseSkill):
    def __init__(self):
        super().__init__("cross_language_injection", "Detects cross-language injection")

    def detect(self, text: str, context: dict = None) -> dict:
        patterns = ["混合語言", "mix languages", "中英混合", "code-switch",
                    "language mix", "switch language", "夾雜", "混雜"]
        for p in patterns:
            if p in text.lower():
                return {"detected": True, "pattern": p, "risk": "medium"}
        return {"detected": False}

    def defend(self, text: str, threat_info: dict) -> str:
        return "[SecretGuard]\n偵測到跨語言注入嘗試，已阻擋。" if threat_info.get("detected") else text
