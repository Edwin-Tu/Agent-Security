import re


class InputGuard:
    def __init__(self):
        self.suspicious_patterns = [
            (r"<script[^>]*>", "xss_script"),
            (r"javascript:", "xss_javascript"),
            (r"onerror\s*=", "xss_onerror"),
            (r"onload\s*=", "xss_onload"),
            (r"data:\s*text/html", "xss_data_url"),
            (r"<iframe", "xss_iframe"),
            (r"vbscript:", "xss_vbscript"),
        ]
        self.normalization_rules = []

    def normalize(self, text: str) -> str:
        result = text.strip()
        for rule in self.normalization_rules:
            result = re.sub(rule.get("pattern", ""), rule.get("replacement", ""), result)
        return result

    def check(self, text: str) -> dict:
        if not text:
            return {"blocked": False, "reason": "Empty input."}
        text_lower = text.lower()
        for pattern_str, name in self.suspicious_patterns:
            if re.search(pattern_str, text_lower):
                return {"blocked": True, "reason": f"Suspicious content: {name}", "matched": [name]}
        return {"blocked": False, "reason": "Input passed."}

    def check_suspicious_patterns(self, text: str) -> list[dict]:
        findings = []
        text_lower = text.lower()
        for pattern_str, name in self.suspicious_patterns:
            matches = re.finditer(pattern_str, text_lower)
            for match in matches:
                findings.append({
                    "pattern": name,
                    "matched_text": match.group(),
                    "position": match.start(),
                })
        return findings

    def add_normalization(self, pattern: str, replacement: str = ""):
        self.normalization_rules.append({"pattern": pattern, "replacement": replacement})
