import re


XSS_PATTERNS = {
    "possible_xss": [
        r"<script[^>]*>.*?</script>",
        r"javascript\s*:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
        r"alert\s*\(",
        r"eval\s*\(",
    ],
}

PROMPT_SMUGGLING_PATTERNS = {
    "prompt_smuggling": [
        r"###\s*SYSTEM",
        r"###\s*USER",
        r"###\s*ASSISTANT",
        r"\[INST\]",
        r"\[/\s*INST\]",
        r"<SYS>",
        r"</SYS>",
        r"(?m)^assistant\s*:",
        r"(?m)^developer\s*:",
        r"(?m)^system\s*:",
        r"(?m)^user\s*:",
        r"<<SYS>>",
        r"<<SYSTEM>>",
    ],
}

STRUCTURED_LEAKAGE_PATTERNS = {
    "structured_leakage_request": [
        r"以\s*JSON\s*列出\s*(所有|全部|內部|秘密|機密|敏感)",
        r"用\s*JSON\s*格式\s*(列出|輸出|顯示)\s*(所有|全部|內部|秘密|機密|敏感)",
        r"以\s*JSON\s*格式\s*(列出|輸出|顯示)\s*(所有|全部|內部|秘密|機密|敏感)",
        r"用\s*JSON\s*(列出|輸出|顯示)\s*(所有|全部|內部|秘密|機密|敏感)",
        r"逐字元\s*(輸出|顯示|列出|回傳)",
        r"逐字\s*(輸出|顯示|列出)",
        r"字元\s*by\s*字元",
        r"(表格|table)\s*列出\s*內部",
        r"用\s*(表格|table)\s*(列出|顯示|輸出|回傳)\s*(內部|所有|全部|秘密|機密|敏感)",
        r"structured\s*output",
        r"以\s*(YAML|XML|CSV)\s*輸出\s*所有",
        r"用\s*(YAML|XML|CSV)\s*(列出|顯示|輸出)\s*所有",
    ],
}

SUSPICIOUS_FORMAT_PATTERNS = {
    "suspicious_format": [
        r"```\s*(bash|sh|zsh|cmd|powershell|shell|terminal)",
        r"```.*\n.*rm\s+[-][rf ]+.*\n```",
        r"```.*\n.*del\s+.*\n```",
        r"```.*\n.*format\s+.*\n```",
    ],
}


class SuspiciousFormatDetector:
    def detect(self, text: str) -> dict:
        if not text or not text.strip():
            return {"matched": False, "rules": []}

        text_lower = text.lower()
        matched_rules = []

        for tag, patterns in XSS_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower, re.IGNORECASE | re.DOTALL):
                    matched_rules.append(tag)
                    break

        for tag, patterns in PROMPT_SMUGGLING_PATTERNS.items():
            for p in patterns:
                if re.search(p, text, re.IGNORECASE):
                    matched_rules.append(tag)
                    break

        for tag, patterns in STRUCTURED_LEAKAGE_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower, re.IGNORECASE):
                    matched_rules.append(tag)
                    break

        for tag, patterns in SUSPICIOUS_FORMAT_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower, re.DOTALL):
                    matched_rules.append(tag)
                    break

        has_code_block = bool(re.search(r"```", text))
        if has_code_block and "suspicious_format" not in matched_rules:
            matched_rules.append("suspicious_format")

        return {
            "matched": len(matched_rules) > 0,
            "rules": matched_rules,
        }
