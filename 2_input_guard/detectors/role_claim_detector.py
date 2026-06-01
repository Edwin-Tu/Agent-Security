import re


ROLE_CLAIM_PATTERNS = {
    "owner": [
        r"我\s*是\s*owner",
        r"owner\s*是\s*我",
        r"我\s*是\s*(系統)?管理員",
        r"我\s*是\s*root",
        r"我\s*是\s*superuser",
        r"我\s*是\s*administrator",
        r"我\s*有\s*最高\s*權限",
        r"我\s*有\s*管理員\s*權限",
        r"以\s*owner\s*身份",
        r"以\s*管理員\s*身份",
        r"\bowner\b",
    ],
    "authorized": [
        r"這是\s*授權\s*測試",
        r"開發者\s*允許\s*你",
        r"你\s*可以\s*信任\s*我",
        r"我\s*有\s*授權",
        r"我\s*已\s*獲得\s*授權",
        r"經\s*授權",
        r"authorized\s+(test|access|request)",
        r"trust\s+me",
        r"I['\s]*m\s+(the\s+)?(owner|admin|root|superuser|administrator)",
        r"(owner|admin|administrator)\s+(of|is|:)\s+(this|the|me|my)",
    ],
}


class RoleClaimDetector:
    def detect(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "matched": False,
                "claimed_role": None,
                "requires_authorization_check": False,
                "rules": [],
            }

        text_lower = text.lower()
        claimed_role = None
        matched = False
        matched_rules = []

        for role, patterns in ROLE_CLAIM_PATTERNS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    matched = True
                    matched_rules.append("role_claim")
                    if role == "owner":
                        claimed_role = role
                    elif claimed_role is None:
                        claimed_role = role
                    break

        return {
            "matched": matched,
            "claimed_role": claimed_role,
            "requires_authorization_check": matched,
            "rules": matched_rules,
        }
