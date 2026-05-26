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

    def generate(
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
