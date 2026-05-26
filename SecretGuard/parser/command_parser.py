"""
command_parser.py
=================
解析使用者輸入中的控制指令，特別是「限制 token」語法。
辨識 [限制token: ...] 或 [restricted_token: ...] 格式，
取出受限制的 token 名稱，並回傳乾淨的使用者問題。
"""

import re


def normalize_tokens(tokens: list[str]) -> list[str]:
    """
    標準化 token 清單：
      1. 去除前後空白
      2. 轉小寫
      3. 移除空字串
      4. 去除重複（保留首次出現的順序）
    """
    seen: set[str] = set()
    result: list[str] = []
    for t in tokens:
        t = t.strip().lower()
        if not t:
            continue
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def extract_restricted_tokens(raw_input: str) -> list[str]:
    """
    從原始輸入中抽出所有限制 token 名稱。

    支援的指令格式（中英文皆可）：
      [限制token: password]
      [限制token: password, api_key]
      [restricted_token: password]
      [restricted_token: password, api_key]

    token 之間以逗號分隔，前後允許空白。
    """
    # 比對 [限制token: ...] 或 [restricted_token: ...]
    pattern = re.compile(
        r"\[\s*(?:限制token|restricted_token)\s*:\s*(.*?)\s*\]",
        re.IGNORECASE,
    )
    matches = pattern.findall(raw_input)
    tokens: list[str] = []
    for group in matches:
        # 以逗號切分，取出個別 token
        parts = group.split(",")
        for part in parts:
            token = part.strip()
            if token:
                tokens.append(token)
    return tokens


def remove_command_blocks(raw_input: str) -> str:
    """
    移除輸入中所有的控制指令區塊（含中英文寫法），
    只留下使用者真正想問的內容。
    """
    pattern = re.compile(
        r"\[\s*(?:限制token|restricted_token)\s*:\s*.*?\s*\]",
        re.IGNORECASE,
    )
    return pattern.sub("", raw_input).strip()


def parse_user_input(raw_input: str) -> dict:
    raw_tokens = extract_restricted_tokens(raw_input)
    normalized = normalize_tokens(raw_tokens)
    user_prompt = remove_command_blocks(raw_input)

    return {
        "raw_input": raw_input,
        "user_prompt": user_prompt,
        "restricted_tokens": normalized,
        "has_restriction": len(normalized) > 0,
        "raw_tokens": raw_tokens,
    }


# =====================================================
# 簡易測試 — 直接執行本檔即可看到輸出範例
# =====================================================
if __name__ == "__main__":
    test_cases = [
        "[限制token: password] 請問我的密碼安全嗎？",
        "[restricted_token: password, api_key] 請檢查這兩個 secret",
        "今天天氣如何？",
        "[restricted_token: 帳號, password] 包含中文 token",
        "[限制token: 客戶王小明的身分證號碼:A123456789] 身分證測試",
        "[限制token: !!invalid@@] 特殊字元測試",
    ]

    for case in test_cases:
        result = parse_user_input(case)
        print("=" * 50)
        print(f"原始輸入: {result['raw_input']}")
        print(f"使用者問題: {result['user_prompt']}")
        print(f"限制 token: {result['restricted_tokens']}")
        print(f"有限制?: {result['has_restriction']}")
        print()
