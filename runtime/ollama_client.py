import sys
import json
from pathlib import Path
from typing import Optional, Iterable
import requests

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


class OllamaClient:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "mistral", timeout: int = 60):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    def list_models(self) -> list[str]:
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate_stream(self, prompt: str, restricted_tokens: list[str] = None) -> dict:
        from guards.restricted_token_guard import RestrictedTokenGuard
        from runtime.stream_monitor import StreamMonitor

        guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens or [])
        monitor = StreamMonitor(guard)
        payload = {"model": self.model, "prompt": prompt, "stream": True}
        try:
            resp = requests.post(f"{self.ollama_url}/api/generate", json=payload, stream=True, timeout=self.timeout)
            resp.raise_for_status()
            chunks = []
            for line in resp.iter_lines(decode_unicode=True):
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        chunks.append(chunk)
                    except json.JSONDecodeError:
                        continue
            result = monitor.monitor(chunks)
            return {"success": True, **result}
        except requests.ConnectionError:
            return {"success": False, "reason": "Cannot connect to Ollama.", "blocked": False, "output": ""}
        except requests.Timeout:
            return {"success": False, "reason": "Request timed out.", "blocked": False, "output": ""}
        except requests.HTTPError as e:
            return {"success": False, "reason": f"HTTP error: {e}", "blocked": False, "output": ""}

    def generate(self, prompt: str, restricted_tokens: list[str] = None) -> dict:
        return self.generate_stream(prompt, restricted_tokens)

    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        payload = {"model": self.model, "prompt": prompt, "system": system_prompt, "stream": False}
        try:
            resp = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception:
            return ""
