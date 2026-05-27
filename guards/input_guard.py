from core.token_expander import TokenExpander


class InputGuard:
    def __init__(self, rule_path: str = "policies/token_rules.json"):
        self.expander = TokenExpander(rule_path=rule_path)
        self.sanitization_rules: list[str] = []

    def check(self, text: str) -> dict:
        if not text:
            return {"blocked": False, "reason": "Empty input."}
        suspicious = ["<script", "javascript:", "onerror=", "onload=", "data:"]
        text_lower = text.lower()
        for s in suspicious:
            if s in text_lower:
                return {"blocked": True, "reason": f"Suspicious content detected: {s}", "matched": [s]}
        return {"blocked": False, "reason": "Input passed."}

    def sanitize(self, text: str) -> str:
        return text

    def add_rule(self, rule: str):
        self.sanitization_rules.append(rule)
