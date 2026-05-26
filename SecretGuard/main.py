"""
main.py
=======
第一階段 mock 測試入口 + AI Token 擴展。

流程：
  使用者輸入 → 解析 [限制token: xxx]
  → 檢查 token 是否已知分類
  → 未知 → 送 Ollama AI 分析 → 自動收錄到 policies → 加入防護
  → 已知 → 直接擴展
  → mock 模型輸出 → 檢查是否命中 → 風險等級評估 → 安全拒答
"""

import json
from pathlib import Path

from parser.command_parser import parse_user_input
from guards.restricted_token_guard import RestrictedTokenGuard
from expansion.token_risk_classifier import TokenRiskClassifier
from guards.risk_level_guard import RiskLevelGuard
from expansion.ai_token_expander import AITokenExpander
from runtime.ollama_client import OllamaClient


def load_known_categories() -> set[str]:
    path = Path("policies/token_rules.json")
    if not path.exists():
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            rules = json.load(f)
        return set(rules.keys()) if isinstance(rules, dict) else set()
    except (json.JSONDecodeError, IOError):
        return set()


def main() -> None:
    print("=== SecretGuard Mock Test ===\n")

    raw_input = input("請輸入 prompt（含 [限制token: xxx] 前綴）：\n> ")

    parsed = parse_user_input(raw_input)
    tokens = parsed["restricted_tokens"]
    raw_tokens = parsed.get("raw_tokens", [])
    user_prompt = parsed["user_prompt"]

    print("\n--- 解析結果 ---")
    print(f"user_prompt:   {user_prompt}")
    print(f"tokens:        {tokens}")

    known = load_known_categories()

    ai_specific_values: list[str] = []
    final_tokens: list[str] = []

    for i, token in enumerate(tokens):
        if token in known:
            final_tokens.append(token)
        else:
            raw = raw_tokens[i] if i < len(raw_tokens) else token
            print(f"\n--- AI Token 擴展: {raw} ---")
            client = OllamaClient()
            expander = AITokenExpander(client, auto_learn=True)
            result = expander.analyze_and_learn(raw)

            if result:
                print(f"  category:        {result.get('category')}")
                print(f"  risk_level:      {result.get('risk_level')}")
                print(f"  expanded_tokens: {result.get('expanded_tokens')}")
                print(f"  specific_values: {result.get('specific_values')}")
                ai_specific_values.extend(result.get("specific_values", []))

                category = result.get("category", "").strip().lower()
                if category and category not in final_tokens:
                    final_tokens.append(category)
            else:
                print("  AI 分析失敗或無法連線至 Ollama，原始 token 照常加入")
                final_tokens.append(token)

    guard = RestrictedTokenGuard(restricted_tokens=final_tokens)
    for val in ai_specific_values:
        normalized = val.strip().lower()
        if normalized:
            guard.restricted_set.add(normalized)

    print(f"\nrestricted_set: {guard.restricted_set}")

    mock_output = "The password is 123456. 身分證號碼是 A123456789。"
    print(f"\n--- Mock 模型輸出 ---")
    print(f"mock_output: {mock_output}")

    result = guard.detect(mock_output)
    print(f"\n--- Detect 結果 ---")
    print(f"blocked:         {result['blocked']}")
    print(f"matched_tokens:  {result['matched_tokens']}")
    print(f"reason:          {result['reason']}")

    if result["matched_tokens"]:
        classifier = TokenRiskClassifier()
        risk_guard = RiskLevelGuard(classifier=classifier, threshold="medium")

        risk_result = risk_guard.check(result["matched_tokens"])
        print(f"\n--- RiskLevelGuard 評估 ---")
        print(f"risk_levels:     {risk_result['risk_levels']}")
        print(f"max_level:       {risk_result['max_level']}")
        print(f"threshold:       {risk_result['threshold']}")
        print(f"blocked:         {risk_result['blocked']}")
        print(f"reason:          {risk_result['reason']}")

        final_blocked = risk_result["blocked"]
    else:
        final_blocked = result["blocked"]

    print(f"\n--- SecretGuard 最終輸出 ---")
    if final_blocked:
        print("[SecretGuard] 此內容受到限制，未經授權無法提供。")
    else:
        print(mock_output)


if __name__ == "__main__":
    main()
