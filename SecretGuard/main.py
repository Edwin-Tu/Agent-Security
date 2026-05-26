"""
main.py
=======
SecretGuard 主程式入口。

支援兩種模式：
1. Mock 模式：使用預定義的 mock 輸出測試
2. Ollama 模式：連接真實 Ollama 服務

流程：
  使用者輸入 → 解析 [限制token: xxx] → 擴展限制 token
  → 取得模型輸出 → 即時監控 → 檢查限制詞 → 安全拒答或正常輸出
"""

import sys
import argparse
from pathlib import Path

# 將專案根目錄加入 sys.path
_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from parser.command_parser import parse_user_input
from guards.restricted_token_guard import RestrictedTokenGuard
from runtime.stream_monitor import StreamMonitor
from runtime.ollama_client import OllamaClient


# Mock 測試數據
MOCK_OUTPUTS = {
    "password": "The password is admin123. You can use it to login.",
    "api_key": "Your API key is sk-1234567890abcdef. Keep it secret!",
    "secret": "This is a secret message that should be protected.",
    "normal": "Today is a beautiful day. The weather is nice.",
}


def print_banner() -> None:
    """印出 SecretGuard 標題。"""
    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║          SecretGuard - Runtime Token Guardian             ║")
    print("║     Runtime Guardrail for Local LLMs (Ollama)            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("=" * 60 + "\n")


def interactive_mock_mode() -> None:
    """
    互動式 Mock 模式。
    讓使用者輸入 prompt，模擬模型輸出，測試 SecretGuard。
    """
    print("📋 模式：Mock 測試\n")
    print("說明：")
    print("  1. 輸入格式：[限制token: xxx] 您的問題")
    print("  2. 支援多個 token：[限制token: password, api_key]")
    print("  3. 中英文皆可\n")

    # 使用者輸入
    raw_input = input("請輸入 prompt（含 [限制token: xxx] 前綴）：\n> ")
    if not raw_input.strip():
        print("⚠️  輸入為空，退出。\n")
        return

    # 解析輸入
    parsed = parse_user_input(raw_input)
    restricted_tokens = parsed["restricted_tokens"]
    user_prompt = parsed["user_prompt"]
    has_restriction = parsed["has_restriction"]
    parse_errors = parsed["parse_errors"]

    # 印出解析資訊
    print("\n" + "-" * 60)
    print("📝 解析結果")
    print("-" * 60)
    print(f"問題：{user_prompt}")
    print(f"限制 Token：{restricted_tokens}")
    print(f"有限制：{has_restriction}")

    if parse_errors:
        print(f"⚠️  解析錯誤：")
        for err in parse_errors:
            print(f"  - {err}")

    # 建立防護器
    guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens)
    print(f"已擴展限制詞集合：{guard.restricted_set}")

    # 選擇 mock 輸出
    print("\n" + "-" * 60)
    print("🤖 Mock 模型輸出")
    print("-" * 60)
    print("可用的 mock 輸出：")
    for i, (key, value) in enumerate(MOCK_OUTPUTS.items(), 1):
        print(f"  {i}. {key:12} → {value[:40]}...")

    choice = input("\n選擇輸出（1-4 或直接輸入自訂內容）：").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(MOCK_OUTPUTS):
        mock_output = list(MOCK_OUTPUTS.values())[int(choice) - 1]
        output_type = list(MOCK_OUTPUTS.keys())[int(choice) - 1]
        print(f"✓ 選定：{output_type}")
    else:
        mock_output = choice if choice else MOCK_OUTPUTS["normal"]
        output_type = "custom"

    print(f"模型輸出：{mock_output}")

    # 檢查是否命中限制詞
    result = guard.detect(mock_output)

    print("\n" + "-" * 60)
    print("🔍 防護檢查結果")
    print("-" * 60)
    print(f"被攔截：{result['blocked']}")
    print(f"命中詞彙：{result['matched_tokens']}")
    print(f"原因：{result['reason']}")

    # 根據結果決定輸出
    print("\n" + "-" * 60)
    print("📤 最終輸出")
    print("-" * 60)
    if result["blocked"]:
        print("[SecretGuard] 此內容受到限制，未經授權無法提供。")
        print(f"🚫 已攔截的敏感詞：{', '.join(result['matched_tokens'])}")
    else:
        print(mock_output)
        print("✅ 內容安全，已通過防護檢查")

    print()


def ollama_mode() -> None:
    """
    Ollama 模式。
    連接真實 Ollama 服務並進行防護。
    """
    print("🌐 模式：Ollama 集成\n")

    # 初始化客戶端
    client = OllamaClient(
        ollama_url="http://localhost:11434",
        model="mistral",
    )

    # 檢查服務
    print("正在檢查 Ollama 服務...")
    if not client.is_available():
        print("❌ Ollama 服務不可用")
        print("   請確保 Ollama 已啟動：ollama serve\n")
        return

    print("✓ Ollama 服務可用")

    # 列出模型
    models = client.list_models()
    if models:
        print(f"✓ 可用模型：{', '.join(models)}")
    else:
        print("⚠️  無法取得模型列表")

    # 使用者輸入
    print("\n說明：輸入格式 [限制token: xxx] 您的問題\n")
    raw_input = input("請輸入 prompt：\n> ")
    if not raw_input.strip():
        print("⚠️  輸入為空，退出。\n")
        return

    # 解析輸入
    parsed = parse_user_input(raw_input)
    restricted_tokens = parsed["restricted_tokens"]
    user_prompt = parsed["user_prompt"]

    print(f"\n📝 問題：{user_prompt}")
    print(f"🔒 限制 Token：{restricted_tokens}")
    print("\n⏳ 正在查詢 Ollama...")

    # 調用 Ollama
    result = client.generate(
        prompt=user_prompt,
        restricted_tokens=restricted_tokens,
    )

    print("\n" + "-" * 60)
    if not result["success"]:
        print(f"❌ 錯誤：{result['reason']}")
    elif result["blocked"]:
        print("[SecretGuard] 此內容受到限制，未經授權無法提供。")
        print(f"🚫 已攔截的敏感詞：{', '.join(result['matched_tokens'])}")
    else:
        print(f"✓ 模型回應（已安全檢查）：\n{result['output']}")

    print()


def demo_mode() -> None:
    """
    演示模式。
    展示各種測試場景。
    """
    print("🎬 模式：自動演示\n")

    test_cases = [
        {
            "name": "測試 1：正常內容（無限制）",
            "restricted_tokens": [],
            "output": "Today is a beautiful day.",
        },
        {
            "name": "測試 2：偵測密碼",
            "restricted_tokens": ["password"],
            "output": "The password is admin123.",
        },
        {
            "name": "測試 3：偵測 API Key",
            "restricted_tokens": ["api_key"],
            "output": "Your API key is sk-12345678.",
        },
        {
            "name": "測試 4：多個限制詞",
            "restricted_tokens": ["password", "api_key"],
            "output": "password=admin, api_key=secret",
        },
        {
            "name": "測試 5：中文敏感詞",
            "restricted_tokens": ["password"],
            "output": "我的密碼是 12345",
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['name']}")
        print("-" * 60)

        guard = RestrictedTokenGuard(restricted_tokens=test["restricted_tokens"])
        result = guard.detect(test["output"])

        print(f"限制 Token：{test['restricted_tokens']}")
        print(f"模型輸出：{test['output']}")
        print(f"已擴展詞集：{guard.restricted_set}")
        print(f"結果：{'🚫 被攔截' if result['blocked'] else '✅ 通過'}")
        print(f"詳情：{result['reason']}")

    print("\n" + "=" * 60 + "\n")


def main() -> None:
    """主程式入口。"""
    parser = argparse.ArgumentParser(
        description="SecretGuard - Runtime Token Guardian",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python3 main.py --mock              # 互動式 Mock 模式
  python3 main.py --ollama            # Ollama 模式
  python3 main.py --demo              # 自動演示
  python3 main.py                     # 默認選單
        """,
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="啟動互動式 Mock 模式",
    )
    parser.add_argument(
        "--ollama",
        action="store_true",
        help="啟動 Ollama 集成模式",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="運行自動演示",
    )

    args = parser.parse_args()

    print_banner()

    if args.mock:
        interactive_mock_mode()
    elif args.ollama:
        ollama_mode()
    elif args.demo:
        demo_mode()
    else:
        # 默認選單
        print("📋 選擇模式：\n")
        print("  1. Mock 測試（互動式）")
        print("  2. Ollama 集成")
        print("  3. 自動演示")
        print("  0. 退出\n")

        choice = input("請選擇（0-3）：").strip()

        if choice == "1":
            interactive_mock_mode()
        elif choice == "2":
            ollama_mode()
        elif choice == "3":
            demo_mode()
        elif choice == "0":
            print("退出。\n")
        else:
            print("⚠️  無效選擇\n")


if __name__ == "__main__":
    main()
