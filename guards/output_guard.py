class OutputGuard:
    def __init__(self):
        self.blocked_patterns = [
            "sk-", "-----BEGIN", "AKIA", "ghp_", "gho_",
        ]

    def check(self, text: str) -> dict:
        if not text:
            return {"blocked": False, "reason": "Empty output."}
        text_lower = text.lower()
        for pattern in self.blocked_patterns:
            if pattern.lower() in text_lower:
                return {
                    "blocked": True,
                    "reason": f"Output contains blocked pattern: {pattern}",
                    "matched": [pattern],
                }
        return {"blocked": False, "reason": "Output passed."}

    def add_pattern(self, pattern: str):
        if pattern not in self.blocked_patterns:
            self.blocked_patterns.append(pattern)
