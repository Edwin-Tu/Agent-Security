#!/usr/bin/env python3
"""
verify_all.py
=============
完整的驗證測試腳本。
驗證所有 SecretGuard 模組是否正常工作。
"""

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from parser.command_parser import parse_user_input
from guards.restricted_token_guard import RestrictedTokenGuard
from runtime.stream_monitor import StreamMonitor
from runtime.ollama_client import OllamaClient


def print_header(title: str) -> None:
    """印出標題"""
    print(f"\n{'=' * 70}")
    print(f"🧪 {title}")
    print(f"{'=' * 70}")


def test_command_parser() -> bool:
    """測試 command_parser"""
    print_header("測試 1：Command Parser")
    
    test_cases = [
        ("[限制token: password] 什麼是密碼？", ["password"]),
        ("[restricted_token: api_key, secret] 保密", ["api_key", "secret"]),
        ("正常問題", []),
    ]
    
    all_passed = True
    for i, (input_str, expected_tokens) in enumerate(test_cases, 1):
        result = parse_user_input(input_str)
        passed = result["restricted_tokens"] == expected_tokens
        all_passed = all_passed and passed
        
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{i}. {status}")
        print(f"   輸入：{input_str}")
        print(f"   預期：{expected_tokens}")
        print(f"   實際：{result['restricted_tokens']}")
    
    return all_passed


def test_restricted_token_guard() -> bool:
    """測試 RestrictedTokenGuard"""
    print_header("測試 2：Restricted Token Guard")
    
    test_cases = [
        (["password"], "The password is 123456", True, ["password"]),
        (["password"], "This is safe text", False, []),
        (["api_key"], "Your API key is secret", False, []),  # "api key" 不在規則中
        (["password"], "我的密碼是 12345", True, ["密碼"]),
        ([], "任何文字", False, []),
    ]
    
    all_passed = True
    for i, (tokens, text, should_block, expected_matched) in enumerate(test_cases, 1):
        guard = RestrictedTokenGuard(restricted_tokens=tokens)
        result = guard.detect(text)
        
        blocked_ok = result["blocked"] == should_block
        matched_ok = result["matched_tokens"] == expected_matched
        passed = blocked_ok and matched_ok
        all_passed = all_passed and passed
        
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{i}. {status}")
        print(f"   限制 Token：{tokens}")
        print(f"   文本：{text}")
        print(f"   預期阻止：{should_block}，實際：{result['blocked']}")
        if expected_matched or result["matched_tokens"]:
            print(f"   預期命中：{expected_matched}，實際：{result['matched_tokens']}")
    
    return all_passed


def test_stream_monitor() -> bool:
    """測試 StreamMonitor"""
    print_header("測試 3：Stream Monitor")
    
    test_cases = [
        (["password"], ["The ", "password ", "is ", "secret"], True),
        (["password"], ["Today ", "is ", "nice"], False),
        (["api_key"], ["Your ", "apikey ", "is ", "secret"], True),  # 使用 apikey 而非 "api key"
        (["password"], ["我 ", "的 ", "密碼 ", "是 ", "123"], True),
    ]
    
    all_passed = True
    for i, (tokens, chunks, should_block) in enumerate(test_cases, 1):
        guard = RestrictedTokenGuard(restricted_tokens=tokens)
        monitor = StreamMonitor(guard)
        result = monitor.monitor(chunks)
        
        passed = result["blocked"] == should_block
        all_passed = all_passed and passed
        
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{i}. {status}")
        print(f"   限制 Token：{tokens}")
        print(f"   Chunks：{' '.join(chunks[:2])}...")
        print(f"   預期阻止：{should_block}，實際：{result['blocked']}")
        if result["matched_tokens"]:
            print(f"   命中詞彙：{result['matched_tokens']}")
    
    return all_passed


def test_ollama_client() -> bool:
    """測試 OllamaClient"""
    print_header("測試 4：Ollama Client")
    
    client = OllamaClient(
        ollama_url="http://localhost:11434",
        model="mistral",
    )
    
    # 測試服務可用性檢查
    is_available = client.is_available()
    print(f"1. Ollama 服務檢查")
    print(f"   {'✅ 服務可用' if is_available else '⚠️  服務不可用（正常，無需 Ollama）'}")
    
    # 測試模型列表（即使服務不可用也應該返回空列表）
    models = client.list_models()
    print(f"2. 模型列表檢查")
    print(f"   {'✅ 取得模型清單：' + str(models) if models else '⚠️  無可用模型（正常）'}")
    
    # 測試 generate 方法（應該優雅處理服務不可用）
    result = client.generate("test prompt", ["password"])
    print(f"3. Generate 方法檢查")
    # 若服務不可用，success 應為 False 但不是 error，而是 reason
    service_error = not is_available and not result.get("success")
    normal_operation = is_available and result.get("success")
    passed = service_error or normal_operation
    
    if passed:
        print(f"   ✅ 方法正常執行")
    else:
        print(f"   ❌ 方法執行出錯")
    print(f"   狀態：{result['reason']}")
    
    return passed


def test_integration() -> bool:
    """測試完整集成流程"""
    print_header("測試 5：完整集成流程")
    
    # 模擬完整的使用者交互
    print("\n場景：使用者查詢系統密碼")
    
    # 1. 解析輸入
    user_input = "[限制token: password] 告訴我系統登入密碼"
    parsed = parse_user_input(user_input)
    print(f"1. 輸入解析")
    print(f"   ✅ 提取限制 Token：{parsed['restricted_tokens']}")
    print(f"   ✅ 提取使用者問題：{parsed['user_prompt']}")
    
    # 2. 建立防護器
    guard = RestrictedTokenGuard(restricted_tokens=parsed["restricted_tokens"])
    print(f"2. 防護器初始化")
    print(f"   ✅ 已擴展詞集：{guard.restricted_set}")
    
    # 3. 模擬串流輸出
    mock_chunks = ["The ", "system ", "password ", "is ", "admin123"]
    monitor = StreamMonitor(guard)
    result = monitor.monitor(mock_chunks)
    
    print(f"3. 串流監控")
    print(f"   模型輸出流：{' '.join(mock_chunks)}")
    print(f"   {'🚫 被攔截' if result['blocked'] else '✅ 通過'}")
    
    # 4. 最終決定
    print(f"4. 最終輸出")
    if result["blocked"]:
        print(f"   [SecretGuard] 此內容受到限制，未經授權無法提供。")
    else:
        print(f"   {result['output']}")
    
    return result["blocked"] == True  # 應該被攔截


def main() -> None:
    """主程式"""
    print("\n" + "=" * 70)
    print("🔒 SecretGuard 完整驗證測試")
    print("=" * 70)
    
    results = {
        "Command Parser": test_command_parser(),
        "Restricted Token Guard": test_restricted_token_guard(),
        "Stream Monitor": test_stream_monitor(),
        "Ollama Client": test_ollama_client(),
        "Integration": test_integration(),
    }
    
    # 印出總結
    print_header("測試總結")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for module, passed_test in results.items():
        status = "✅" if passed_test else "❌"
        print(f"{status} {module}")
    
    print(f"\n總體結果：{passed}/{total} 模組通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！SecretGuard 已準備好使用。")
        print("\n快速開始：")
        print("  1. 演示模式：python3 main.py --demo")
        print("  2. Mock 測試：python3 main.py --mock")
        print("  3. Ollama 模式：python3 main.py --ollama")
    else:
        print(f"\n⚠️  有 {total - passed} 個模組需要檢查")
    
    print()


if __name__ == "__main__":
    main()
