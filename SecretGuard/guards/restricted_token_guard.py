"""
restricted_token_guard.py
=========================
限制 Token 防護機制。
根據 policies/token_rules.json 將使用者設定的限制 token 擴展成相關詞，
並檢查模型輸出是否命中這些限制詞。
"""

import json
from pathlib import Path
from typing import Optional


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
        """
        初始化防護器。

        參數
        -----
        rule_path : str
            token_rules.json 的路徑。
        restricted_tokens : list[str] | None
            使用者設定的限制 token 清單。
        """
        self.rule_path: str = rule_path
        self.restricted_tokens: list[str] = restricted_tokens or []

        # 讀取規則檔
        self.token_rules: dict = self.load_token_rules(rule_path)

        # 建立完整的限制集合
        self.restricted_set: set[str] = set()
        if self.restricted_tokens:
            self.restricted_set = self.build_restricted_set(self.restricted_tokens)

    # ------------------------------------------------------------------
    # 規則載入
    # ------------------------------------------------------------------

    def load_token_rules(self, rule_path: str) -> dict:
        """
        讀取 token_rules.json，回傳字典。

        JSON 格式範例：
        {
            "password": ["passwd", "pwd", "密碼"],
            "api_key": ["apikey", "api密钥", "key"]
        }

        若檔案不存在或無法解析，回傳空字典。
        """
        path = Path(rule_path)
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            return {}

    # ------------------------------------------------------------------
    # Token 處理
    # ------------------------------------------------------------------

    def normalize_token(self, token: str) -> str:
        """去除前後空白並轉小寫。"""
        return token.strip().lower()

    def expand_tokens(self, restricted_tokens: list[str]) -> list[str]:
        """
        根據 token_rules.json 擴展相關詞。

        例如 restricted_tokens = ["password"]，規則中 "password" -> ["passwd", "pwd"]，
        則回傳 ["password", "passwd", "pwd"]。

        若規則中找不到對應鍵，至少保留原始 token。
        """
        expanded: list[str] = []
        seen: set[str] = set()

        for token in restricted_tokens:
            normalized = self.normalize_token(token)
            if not normalized:
                continue

            # 保留原始 token（尚未加入才加入）
            if normalized not in seen:
                expanded.append(normalized)
                seen.add(normalized)

            # 查詢規則檔，加入相關擴展詞
            related = self.token_rules.get(normalized, [])
            if isinstance(related, list):
                for rel in related:
                    rel_norm = self.normalize_token(str(rel))
                    if rel_norm and rel_norm not in seen:
                        expanded.append(rel_norm)
                        seen.add(rel_norm)

        return expanded

    def build_restricted_set(self, restricted_tokens: list[str]) -> set[str]:
        """
        合併原始 token 與擴展 token，去除重複與空字串。
        """
        expanded = self.expand_tokens(restricted_tokens)
        return {t for t in expanded if t}

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
        """
        重新設定限制 token，並重建 restricted_set。
        """
        self.restricted_tokens = restricted_tokens
        self.restricted_set = self.build_restricted_set(restricted_tokens)


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
