class RefusalBuilder:
    REFUSAL_TEXT = (
        "我不能提供、推測、重構、翻譯、編碼或暗示任何受保護資訊。\n"
        "我可以協助你了解相關概念、建立安全測試流程，或說明如何設計防護規則。"
    )

    def build(self) -> str:
        return self.REFUSAL_TEXT
