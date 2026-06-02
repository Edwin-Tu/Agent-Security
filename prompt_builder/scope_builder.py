class ScopeBuilder:
    DEFAULT_ALLOWED = "你可以回答一般概念、安全替代方案、授權流程與非敏感內容。"
    DEFAULT_DENIED = (
        "完整 secret、部分片段、前綴、後綴、長度、格式、"
        "編碼版本、翻譯版本、重構線索、語意暗示。"
    )

    def build_allowed_scope(self, allowed_items: list[str]) -> str:
        if not allowed_items:
            return self.DEFAULT_ALLOWED
        return "你可以回答：" + "、".join(allowed_items) + "。"

    def build_denied_scope(self, denied_items: list[str]) -> str:
        if not denied_items:
            return "禁止回答：" + self.DEFAULT_DENIED
        return "禁止回答：" + "、".join(denied_items) + "。"
