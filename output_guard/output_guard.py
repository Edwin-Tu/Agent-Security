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
        self.secret_patterns: list[tuple[str, str]] = []
        self.semantic_rules: list[str] = []

    def check(self, text: str) -> dict:
        if not text:
            return {"blocked": False, "reason": "Empty output."}
        for name, pattern in self.blocked_patterns.items():
            if re.search(pattern, text):
                return {"blocked": True, "reason": f"Output contains {name}", "matched": [name]}
        for name, pattern in self.secret_patterns:
            if re.search(pattern, text):
                return {"blocked": True, "reason": f"Secret pattern matched: {name}", "matched": [name]}
        return {"blocked": False, "reason": "Output passed."}

    def check_regex(self, text: str, patterns: dict[str, str]) -> list[dict]:
        findings = []
        for name, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for m in matches:
                findings.append({"pattern": name, "match": m.group(), "position": m.start()})
        return findings

    def check_secrets(self, text: str, secrets: list[str]) -> list[dict]:
        findings = []
        for secret in secrets:
            if secret in text:
                findings.append({"secret": secret, "type": "exact"})
        return findings

    def add_pattern(self, name: str, pattern: str):
        self.blocked_patterns[name] = pattern

    def add_secret_pattern(self, name: str, pattern: str):
        self.secret_patterns.append((name, pattern))

    def add_semantic_rule(self, rule: str):
        self.semantic_rules.append(rule)
