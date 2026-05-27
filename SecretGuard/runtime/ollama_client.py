<<<<<<< HEAD
import json
from typing import Optional

import requests


class OllamaClient:

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        timeout: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.generate_url = f"{self.base_url}/api/generate"
=======
"""
ollama_client.py
================
與 Ollama 的集成客戶端。
支援串流輸出，整合 StreamMonitor 進行即時監控和中斷。
"""

import sys
import json
from pathlib import Path
from typing import Optional, Iterable

import requests

# 將專案根目錄加入 sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from guards.restricted_token_guard import RestrictedTokenGuard
from runtime.stream_monitor import StreamMonitor


class OllamaClient:
    """
    Ollama 客戶端。

    使用方式：
        client = OllamaClient(
            ollama_url="http://localhost:11434",
            model="mistral"
        )
        result = client.generate(
            prompt="Tell me a joke",
            restricted_tokens=["password"]
        )
        print(result)
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 60,
    ):
        """
        初始化 Ollama 客戶端。

        參數
        -----
        ollama_url : str
            Ollama 服務的 URL（預設：http://localhost:11434）
        model : str
            使用的模型名稱（預設：mistral）
        timeout : int
            請求超時時間（秒）
        """
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        """
        檢查 Ollama 服務是否可用。

        回傳
        -----
        bool
            若服務可用回傳 True，否則 False
        """
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """
        取得 Ollama 上可用的模型清單。

        回傳
        -----
        list[str]
            模型名稱清單
        """
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except Exception:
            return []

    def generate_stream(
        self,
        prompt: str,
        restricted_tokens: Optional[list[str]] = None,
    ) -> dict:
        """
        與 Ollama 互動，取得串流輸出並進行 SecretGuard 監控。

        參數
        -----
        prompt : str
            使用者的問題
        restricted_tokens : list[str] | None
            限制 token 清單

        回傳
        -----
        dict
            {
                "success": bool,              # 請求是否成功
                "blocked": bool,              # 是否被 SecretGuard 攔截
                "output": str,                # 模型的最終輸出
                "matched_tokens": list[str],  # 命中的限制詞
                "reason": str,                # 狀態說明
                "error": str | None,          # 錯誤訊息（如有）
            }
        """
        # 1. 檢查 Ollama 服務是否可用
        if not self.is_available():
            return {
                "success": False,
                "blocked": False,
                "output": "",
                "matched_tokens": [],
                "reason": f"Ollama service not available at {self.ollama_url}",
                "error": "Service unavailable",
            }

        # 2. 初始化防護器和監控器
        guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens or [])
        monitor = StreamMonitor(guard)

        # 3. 準備請求
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }

        try:
            # 4. 發送請求
            response = requests.post(
                url,
                json=payload,
                stream=True,
                timeout=self.timeout,
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "blocked": False,
                    "output": "",
                    "matched_tokens": [],
                    "reason": f"Ollama returned status {response.status_code}",
                    "error": f"HTTP {response.status_code}",
                }

            # 5. 提取串流 chunk
            def chunk_generator() -> Iterable[Optional[str]]:
                """從回應中逐個提取 token."""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            continue

            # 6. 監控串流
            monitor_result = monitor.monitor(chunk_generator())

            # 7. 回傳結果
            return {
                "success": True,
                "blocked": monitor_result.get("blocked", False),
                "output": monitor_result.get("output", ""),
                "matched_tokens": monitor_result.get("matched_tokens", []),
                "reason": monitor_result.get("reason", ""),
                "error": None,
            }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "blocked": False,
                "output": "",
                "matched_tokens": [],
                "reason": "Connection error - cannot reach Ollama service",
                "error": "Connection error",
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "blocked": False,
                "output": "",
                "matched_tokens": [],
                "reason": "Request timeout",
                "error": "Timeout",
            }
        except Exception as e:
            return {
                "success": False,
                "blocked": False,
                "output": "",
                "matched_tokens": [],
                "reason": f"Error: {str(e)}",
                "error": type(e).__name__,
            }
>>>>>>> 9a0d6291612a66d4ccdc035c43352eb602da7242

    def generate(
        self,
        prompt: str,
<<<<<<< HEAD
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[str]:
        payload: dict = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", None)
        except requests.RequestException:
            return None
        except json.JSONDecodeError:
            return None

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[dict]:
        full_prompt = (
            f"{prompt}\n\n"
            f"回傳純 JSON，不要包含 Markdown 格式、程式碼區塊或任何說明文字。"
        )
        response = self.generate(full_prompt, system_prompt, model)
        if not response:
            return None

        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None
=======
        restricted_tokens: Optional[list[str]] = None,
    ) -> dict:
        """
        同步版本的 generate，整合串流處理。

        參數
        -----
        prompt : str
            使用者的問題
        restricted_tokens : list[str] | None
            限制 token 清單

        回傳
        -----
        dict
            同 generate_stream 的回傳格式
        """
        return self.generate_stream(prompt, restricted_tokens)


# =====================================================
# 簡易測試
# =====================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OllamaClient Test")
    print("=" * 60)

    # 建立客戶端
    client = OllamaClient(
        ollama_url="http://localhost:11434",
        model="mistral",
    )

    # 檢查服務可用性
    print("\n[1] 檢查 Ollama 服務...")
    if client.is_available():
        print("✓ Ollama 服務可用")
    else:
        print("✗ Ollama 服務不可用")
        print("  提示：請確保 Ollama 服務已啟動")
        print("  $ ollama serve")
    print()

    # 列出可用模型
    print("[2] 可用模型：")
    models = client.list_models()
    if models:
        for model in models:
            print(f"  - {model}")
    else:
        print("  （無法取得模型列表）")
    print()

    # 測試查詢（不進行限制）
    print("[3] 測試查詢（無限制）...")
    result = client.generate(
        prompt="What is 2+2?",
        restricted_tokens=[],
    )
    print(f"  Success: {result['success']}")
    print(f"  Blocked: {result['blocked']}")
    print(f"  Output: {result['output'][:100] if result['output'] else '（無輸出）'}...")
    print(f"  Reason: {result['reason']}")
    print()

    # 測試查詢（含限制）
    print("[4] 測試查詢（限制 'password'）...")
    result = client.generate(
        prompt="What is a password?",
        restricted_tokens=["password"],
    )
    print(f"  Success: {result['success']}")
    print(f"  Blocked: {result['blocked']}")
    print(f"  Output: {result['output']}")
    print(f"  Matched tokens: {result['matched_tokens']}")
    print(f"  Reason: {result['reason']}")
>>>>>>> 9a0d6291612a66d4ccdc035c43352eb602da7242
