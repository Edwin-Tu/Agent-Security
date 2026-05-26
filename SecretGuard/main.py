"""
main.py
=======
第一階段 mock 測試入口。

流程：
  使用者輸入 → 解析 [限制token: xxx] → 擴展限制 token
  → mock 模型輸出 → 檢查是否命中限制詞 → 安全拒答
"""

from parser.command_parser import parse_user_input
from guards.restricted_token_guard import RestrictedTokenGuard


def main() -> None:
    """
    主程式：讓使用者輸入 prompt，解析限制 token，
    用 mock 輸出測試 RestrictedTokenGuard 的偵測功能。
    """
    print("=== SecretGuard Mock Test ===\n")

    # 1. 使用者輸入
    raw_input = input("請輸入 prompt（含 [限制token: xxx] 前綴）：\n> ")

    # 2. 解析輸入
    parsed = parse_user_input(raw_input)
    restricted_tokens = parsed["restricted_tokens"]
    user_prompt = parsed["user_prompt"]
    has_restriction = parsed["has_restriction"]
    parse_errors = parsed["parse_errors"]

    # 3. 印出解析資訊
    print("\n--- 解析結果 ---")
    print(f"user_prompt:      {user_prompt}")
    print(f"restricted_tokens: {restricted_tokens}")
    print(f"has_restriction:  {has_restriction}")

    # 4. 若有錯誤，印出錯誤訊息
    if parse_errors:
        print("parse_errors:")
        for err in parse_errors:
            print(f"  - {err}")

    # 5. 建立防護器
    guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens)
    print(f"expanded set:     {guard.restricted_set}")

    # 6. mock 模型輸出（第一階段不接 Ollama）
    mock_output = "The password is 123456."
    print(f"\n--- Mock 模型輸出 ---")
    print(f"mock_output: {mock_output}")

    # 7. 檢查是否命中限制詞
    result = guard.detect(mock_output)
    print(f"\n--- Detect 結果 ---")
    print(f"blocked:         {result['blocked']}")
    print(f"matched_tokens:  {result['matched_tokens']}")
    print(f"reason:          {result['reason']}")

    # 8. 根據結果決定輸出
    print(f"\n--- SecretGuard 最終輸出 ---")
    if result["blocked"]:
        print("[SecretGuard] 此內容受到限制，未經授權無法提供。")
    else:
        print(mock_output)


if __name__ == "__main__":
    main()
