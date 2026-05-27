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

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


class OllamaClient:

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 60,
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.generate_url = f"{self.ollama_url}/api/generate"

    # ------------------------------------------------------------------
    # 服務狀態
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
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

    # ------------------------------------------------------------------
    # 串流生成 + SecretGuard 監控
    # ------------------------------------------------------------------

    def generate_stream(
        self,
        prompt: str,
        restricted_tokens: Optional[list[str]] = None,
    ) -> dict:
        if not self.is_available():
            return {
                "success": False,
                "blocked": False,
                "output": "",
                "matched_tokens": [],
                "reason": f"Ollama service not available at {self.ollama_url}",
                "error": "Service unavailable",
            }

        from guards.restricted_token_guard import RestrictedTokenGuard
        from runtime.stream_monitor import StreamMonitor

        guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens or [])
        monitor = StreamMonitor(guard)

        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }

        try:
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

            def chunk_generator() -> Iterable[Optional[str]]:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            continue

            monitor_result = monitor.monitor(chunk_generator())

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

    def generate(
        self,
        prompt: str,
        restricted_tokens: Optional[list[str]] = None,
    ) -> dict:
        return self.generate_stream(prompt, restricted_tokens)

    # ------------------------------------------------------------------
    # 純文字生成（無監控，供 AITokenExpander 使用）
    # ------------------------------------------------------------------

    def generate_text(
        self,
        prompt: str,
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
        response = self.generate_text(full_prompt, system_prompt, model)
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


# =====================================================
# 簡易測試
# =====================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OllamaClient Test")
    print("=" * 60)

    client = OllamaClient(
        ollama_url="http://localhost:11434",
        model="mistral",
    )

    print("\n[1] 檢查 Ollama 服務...")
    if client.is_available():
        print("✓ Ollama 服務可用")
    else:
        print("✗ Ollama 服務不可用")
        print("  提示：請確保 Ollama 服務已啟動")
        print("  $ ollama serve")

    print("\n[2] 可用模型：")
    models = client.list_models()
    if models:
        for model in models:
            print(f"  - {model}")
    else:
        print("  （無法取得模型列表）")

    print("\n[3] 測試查詢（無限制）...")
    result = client.generate(
        prompt="What is 2+2?",
        restricted_tokens=[],
    )
    print(f"  Success: {result['success']}")
    print(f"  Blocked: {result['blocked']}")
    print(f"  Output: {result['output'][:100] if result['output'] else '（無輸出）'}...")
    print(f"  Reason: {result['reason']}")

    print("\n[4] 測試查詢（限制 'password'）...")
    result = client.generate(
        prompt="What is a password?",
        restricted_tokens=["password"],
    )
    print(f"  Success: {result['success']}")
    print(f"  Blocked: {result['blocked']}")
    print(f"  Output: {result['output']}")
    print(f"  Matched tokens: {result['matched_tokens']}")
    print(f"  Reason: {result['reason']}")
