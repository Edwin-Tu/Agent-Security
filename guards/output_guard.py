import re


class OutputGuard:
    def __init__(self):
        self.blocked_patterns = {
            "api_key_sk": r"sk-[A-Za-z0-9]{32,}",
            "private_key": r"-----BEGIN\s+(RSA\s+|EC\s+)?PRIVATE\s+KEY-----",
            "aws_key": r"AKIA[0-9A-Z]{16}",
            "github_token": r"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}",
            "jwt_token": r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        }

    def check(self, text: str) -> dict:
        if not text:
            return {"blocked": False, "reason": "Empty output."}
        for name, pattern in self.blocked_patterns.items():
            if re.search(pattern, text):
                return {"blocked": True, "reason": f"Output contains {name}", "matched": [name]}
        return {"blocked": False, "reason": "Output passed."}

    def add_pattern(self, name: str, pattern: str):
        self.blocked_patterns[name] = pattern
