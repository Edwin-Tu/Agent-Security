import re


OVERRIDE_PATTERNS = [
    r"忽略\s*(前面|以上|上面)\s*所有\s*(規則|指示|指令|要求|限制)",
    r"忽略\s*(前面|以上|上面|所有|先前的|之前的)\s*(規則|指示|指令|要求|限制)",
    r"不要\s*(遵守|遵循|理會|管|聽)\s*(系統提示|系統指令|規則|限制|上層指示)",
    r"請\s*忽略\s*所有\s*先前的?\s*指[示示]",
    r"####?\s*override",
    r"override\s*:",
    r" disregard\s+(previous|above|all)\s+(instructions|rules)",
    r" ignore\s+(previous|above|all)\s+(instructions|rules)",
    r"skip\s+(all\s+)?(previous|above)\s+(rules|instructions|prompts)",
    r"不要\s*遵守\s*(任何\s*)?(規則|限制|禁令|約束)",
    r"override\s+(all\s+)?(previous|above|system)\s+(instructions|rules|prompts)",
    r"new\s+instructions\s*:",
    r"updated\s+instructions\s*:",
    r"以下\s*(是|為)\s*(新|更新|覆蓋)\s*(的)?\s*(指示|指令|規則)",
    r"重新\s*(定義|設定|設置|覆蓋)\s*(規則|指示|指令)",
]


class OverrideDetector:
    def detect(self, text: str) -> dict:
        if not text or not text.strip():
            return {"matched": False, "rules": []}

        text_lower = text.lower()
        matched = False

        for p in OVERRIDE_PATTERNS:
            if re.search(p, text_lower):
                matched = True
                break

        return {
            "matched": matched,
            "rules": ["instruction_override"] if matched else [],
        }
