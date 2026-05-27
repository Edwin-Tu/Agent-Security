from typing import Optional
from core.token_expander import TokenExpander


class RestrictedTokenGuard:
    def __init__(
        self,
        rule_path: str = "policies/token_rules.json",
        restricted_tokens: Optional[list[str]] = None,
    ):
        self.restricted_tokens: list[str] = restricted_tokens or []
        self.expander = TokenExpander(rule_path=rule_path)
        self.restricted_set: set[str] = set()
        if self.restricted_tokens:
            self.restricted_set = self.expander.expand(self.restricted_tokens)

    def detect(self, text: str) -> dict:
        if text is None:
            return {"blocked": False, "matched_tokens": [], "reason": "Input text is None."}
        if not self.restricted_set:
            return {"blocked": False, "matched_tokens": [], "reason": "No restricted tokens configured."}
        text_lower = text.lower()
        matched: list[str] = []
        for token in sorted(self.restricted_set):
            if token in text_lower:
                matched.append(token)
        if matched:
            return {
                "blocked": True,
                "matched_tokens": matched,
                "reason": f"Detected restricted token(s): {', '.join(matched)}",
            }
        return {"blocked": False, "matched_tokens": [], "reason": "No restricted tokens detected."}

    def detect_in_stream(self, buffer: str) -> dict:
        return self.detect(buffer)

    def check(self, text: str) -> dict:
        return self.detect(text)

    def update_restricted_tokens(self, restricted_tokens: list[str]) -> None:
        self.restricted_tokens = restricted_tokens
        self.restricted_set = self.expander.expand(restricted_tokens)
