"""
restricted_token_guard.py
=========================
限制 Token 防護機制。
根據 policies/token_rules.json 將使用者設定的限制 token 擴展成相關詞，
並檢查模型輸出是否命中這些限制詞。
"""

from typing import Optional

from expansion.token_expander import TokenExpander


class RestrictedTokenGuard:
    """
    限制 Token 防護器。

    使用方式：
        guard = RestrictedTokenGuard(restricted_tokens=["password"])
        result = guard.detect("The password is 123456")
        print(result)  # {'blocked': True, ...}
    """

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

    # ------------------------------------------------------------------
    # 偵測方法
    # ------------------------------------------------------------------

    def detect(self, text: str) -> dict:
        """
        檢查文字是否包含任何限制詞。

        若 text 為 None 或空字串，直接回傳未封鎖結果，不會報錯。

        回傳格式：
        {
            "blocked": bool,         # True 表示命中限制詞
            "matched_tokens": list,   # 實際命中的詞
            "reason": str            # 說明文字
        }
        """
        # text 為 None 時不要報錯
        if text is None:
            return {
                "blocked": False,
                "matched_tokens": [],
                "reason": "Input text is None.",
            }

        if not self.restricted_set:
            return {
                "blocked": False,
                "matched_tokens": [],
                "reason": "No restricted tokens configured.",
            }

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

        return {
            "blocked": False,
            "matched_tokens": [],
            "reason": "No restricted tokens detected.",
        }

    def detect_in_stream(self, buffer: str) -> dict:
        """
        串流版本偵測（第一版直接呼叫 detect）。
        未來可擴充為逐步累積緩衝區比對。
        buffer 為 None 時也不會報錯。
        """
        return self.detect(buffer)

    # ------------------------------------------------------------------
    # 更新限制 token
    # ------------------------------------------------------------------

    def update_restricted_tokens(self, restricted_tokens: list[str]) -> None:
        self.restricted_tokens = restricted_tokens
        self.restricted_set = self.expander.expand(restricted_tokens)


# =====================================================
# 簡易測試
# =====================================================
if __name__ == "__main__":
    # 測試案例 1：命中限制詞
    print("=" * 50)
    print("Test 1: 偵測 'password'")
    guard = RestrictedTokenGuard(restricted_tokens=["password"])
    result = guard.detect("The password is 123456")
    print(f"  blocked: {result['blocked']}")
    print(f"  matched: {result['matched_tokens']}")
    print(f"  reason:  {result['reason']}")
    print()

    # 測試案例 2：無限制詞
    print("Test 2: 正常文字")
    result = guard.detect("This is a normal answer.")
    print(f"  blocked: {result['blocked']}")
    print(f"  matched: {result['matched_tokens']}")
    print(f"  reason:  {result['reason']}")
    print()

    # 測試案例 3：空限制清單
    print("Test 3: 空限制清單")
    guard_empty = RestrictedTokenGuard()
    result = guard_empty.detect("The password is 123456")
    print(f"  blocked: {result['blocked']}")
    print(f"  matched: {result['matched_tokens']}")
    print(f"  reason:  {result['reason']}")
    print()

    # 測試案例 4：多個限制詞，部分命中
    print("Test 4: 多個限制詞")
    guard_multi = RestrictedTokenGuard(restricted_tokens=["api_key", "secret"])
    result = guard_multi.detect("This is my secret key.")
    print(f"  blocked: {result['blocked']}")
    print(f"  matched: {result['matched_tokens']}")
    print(f"  reason:  {result['reason']}")
    print()

    # 測試案例 5：text 為 None 不報錯
    print("Test 5: text 為 None")
    result = guard.detect(None)
    print(f"  blocked: {result['blocked']}")
    print(f"  matched: {result['matched_tokens']}")
    print(f"  reason:  {result['reason']}")
