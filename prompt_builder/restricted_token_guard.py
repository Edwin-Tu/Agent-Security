from typing import Optional
from input_normalization.token_expander import TokenExpander


class RestrictedTokenGuard:
    def __init__(self, rule_path: str = "policies/token_rules.json", restricted_tokens: Optional[list[str]] = None):
        self.restricted_tokens: list[str] = restricted_tokens or []
        self.expander = TokenExpander(rule_path=rule_path)
        self.restricted_set: set[str] = set()
        if self.restricted_tokens:
            self.restricted_set = self.expander.expand(self.restricted_tokens)

    def detect(self, text: str) -> dict:
        if text is None:
            return {"blocked": False, "matched_tokens": [], "reason": "None input."}
        if not self.restricted_set:
            return {"blocked": False, "matched_tokens": [], "reason": "No restricted tokens set."}
        text_lower = text.lower()
        matched = [t for t in sorted(self.restricted_set) if t in text_lower]
        if matched:
            return {"blocked": True, "matched_tokens": matched, "reason": f"Detected: {', '.join(matched)}"}
        return {"blocked": False, "matched_tokens": [], "reason": "Clean."}

    def check(self, text: str) -> dict:
        return self.detect(text)

    def update_restricted_tokens(self, tokens: list[str]):
        self.restricted_tokens = tokens
        self.restricted_set = self.expander.expand(tokens)
