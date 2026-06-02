import json
from typing import Generator

import httpx

from llm_gateway.base_provider import BaseLLMProvider, ProviderError

DEFAULT_BASE_URL = "http://127.0.0.1:11434"
CONNECT_TIMEOUT = 5
GENERATE_TIMEOUT = 120


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = DEFAULT_BASE_URL, client: httpx.Client | None = None):
        self.base_url = base_url.rstrip("/")
        self._client_instance = client

    def _get_client(self, timeout: int = CONNECT_TIMEOUT) -> httpx.Client:
        if self._client_instance is not None:
            return self._client_instance
        return httpx.Client(base_url=self.base_url, timeout=httpx.Timeout(timeout, connect=CONNECT_TIMEOUT))

    def list_models(self) -> list[dict]:
        try:
            client = self._get_client()
            resp = client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [{"name": m["name"]} for m in data.get("models", [])]
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            raise ProviderError(str(e))

    def generate(self, model: str, prompt: str, options: dict | None = None) -> str:
        payload: dict = {"model": model, "prompt": prompt, "stream": False}
        if options:
            payload["options"] = options
        try:
            client = self._get_client(timeout=GENERATE_TIMEOUT)
            resp = client.post("/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            raise ProviderError(str(e))

    def stream_generate(self, model: str, prompt: str, options: dict | None = None) -> Generator[str, None, None]:
        payload: dict = {"model": model, "prompt": prompt, "stream": True}
        if options:
            payload["options"] = options
        try:
            client = self._get_client(timeout=GENERATE_TIMEOUT)
            with client.stream("POST", "/api/generate", json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        text = data.get("response", "")
                        if text:
                            yield text
                        if data.get("done"):
                            return
                    except json.JSONDecodeError:
                        continue
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            raise ProviderError(str(e))
