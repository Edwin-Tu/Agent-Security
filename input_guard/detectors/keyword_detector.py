import re


DIRECT_SECRET_PATTERNS = {
    "direct_secret_request": [
        r"直接\s*輸出\s*(flag|secret|api[-\s]*key|key|token|密碼|機密|秘密)",
        r"告訴\s*我\s*(flag|api[-\s]*key|key|token|密碼|機密|秘密|secret)",
        r"輸出\s*(完整\s*)?(flag|secret|token|key|密碼|機密)",
        r"顯示\s*(flag|secret|token|key|密碼)",
        r"給我\s*(flag|secret|token|key|密碼)",
        r"flag\s*是\s*什麼",
        r"secret\s*是\s*什麼",
        r"什麼\s*是\s*flag",
        r"什麼\s*是\s*secret",
        r"\bflag\b",
        r"\bsecret\b",
        r"\bapi\s*key\b",
    ],
}

INSTRUCTION_OVERRIDE_PATTERNS = {
    "instruction_override": [
        r"忽略\s*(前面|以上|上面)\s*所有\s*(規則|指示|指令|要求|限制)",
        r"忽略\s*(前面|以上|上面|所有|先前的|之前的)\s*(規則|指示|指令|要求|限制)",
        r"不要\s*(遵守|遵循|理會|管|聽)\s*(系統提示|系統指令|規則|限制|上層指示)",
        r"請\s*忽略\s*所有\s*先前的?\s*指[示示]",
        r"####?\s*override",
        r"override\s*:",
        r" disregard\s+(previous|above|all)\s+(instructions|rules)",
        r" ignore\s+(previous|above|all)\s+(instructions|rules)",
    ],
}

SYSTEM_PROMPT_PROBE_PATTERNS = {
    "system_prompt_probe": [
        r"輸出\s*system\s*prompt",
        r"system\s*prompt\s*是\s*什麼",
        r"顯示\s*system\s*prompt",
        r"system\s*prompt\s*的\s*內容",
        r"什麼\s*是\s*system\s*prompt",
        r"印出\s*system\s*prompt",
        r"列出\s*system\s*prompt",
    ],
    "internal_rule_probe": [
        r"列出\s*內部\s*(規則|設定|配置|政策|準則|方針)",
        r"內部\s*(規則|設定|配置|政策)\s*是\s*什麼",
        r"顯示\s*內部\s*(規則|設定|配置|政策)",
        r"什麼\s*是\s*內部\s*(規則|設定|配置|政策)",
        r"defense\s*rules",
        r"security\s*rules",
        r"secret\s*policies?",
        r"內部\s*規則\s*列表",
        r"有哪些\s*(安全|防禦|防守)?\s*(規則|設定|配置)",
        r"安全\s*(規則|設定|配置|政策)",
    ],
}


class KeywordDetector:
    def detect(self, text: str) -> dict:
        if not text or not text.strip():
            return {"matched": False, "rules": []}

        text_lower = text.lower()
        matched_rules = []

        for tag, patterns in DIRECT_SECRET_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    matched_rules.append(tag)
                    break

        for tag, patterns in INSTRUCTION_OVERRIDE_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    matched_rules.append(tag)
                    break

        for tag, patterns in SYSTEM_PROMPT_PROBE_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    matched_rules.append(tag)
                    break

        return {
            "matched": len(matched_rules) > 0,
            "rules": matched_rules,
        }
