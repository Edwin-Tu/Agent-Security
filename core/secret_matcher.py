import re
import base64


class SecretMatcher:
    def __init__(self):
        self.patterns = {
            "api_key_sk": r"sk-[A-Za-z0-9]{32,}",
            "private_key": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
            "aws_key": r"AKIA[0-9A-Z]{16}",
            "github_token": r"ghp_[A-Za-z0-9]{36}",
            "jwt": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        }

    def match_exact(self, text: str, secrets: list[str]) -> list[dict]:
        text_lower = text.lower()
        matches = []
        for secret in secrets:
            if secret.lower() in text_lower:
                matches.append({"type": "exact", "value": secret})
        return matches

    def match_pattern(self, text: str) -> list[dict]:
        matches = []
        for name, pattern in self.patterns.items():
            found = re.findall(pattern, text)
            for f in found:
                matches.append({"type": "pattern", "name": name, "value": f})
        return matches

    def match_alias(self, text: str, aliases: list[str]) -> list[dict]:
        text_lower = text.lower()
        matches = []
        for alias in aliases:
            if alias.lower() in text_lower:
                matches.append({"type": "alias", "value": alias})
        return matches

    def match_encoded(self, text: str, secrets: list[str]) -> list[dict]:
        matches = []
        for secret in secrets:
            encoded = base64.b64encode(secret.encode()).decode()
            if encoded in text:
                matches.append({"type": "encoded", "method": "base64", "value": secret})
            hex_enc = secret.encode().hex()
            if hex_enc in text:
                matches.append({"type": "encoded", "method": "hex", "value": secret})
        return matches

    def match_all(self, text: str, secrets: list[str], aliases: list[str] = None) -> list[dict]:
        results = []
        results.extend(self.match_exact(text, secrets))
        results.extend(self.match_pattern(text))
        if aliases:
            results.extend(self.match_alias(text, aliases))
        results.extend(self.match_encoded(text, secrets))
        return results
